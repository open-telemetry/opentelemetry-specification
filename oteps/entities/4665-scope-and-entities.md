# Scope and Entities

Define the relationship between `InstrumentationScope` and `Entity`.

## Motivation

OpenTelemetry needs to address two fundamental problems:

- Reporting data against "mutable" or "changing" entities, where `Resource`
  is currently defined as an "immutable" identity in the data model.
- Providing true multi-tenant capabilities, where, e.g. metrics about one tenant
  will be implicitly separated from metrics about another tenant.

The first problem is well outlined in (not accepted) [OTEP 4316](https://github.com/open-telemetry/opentelemetry-specification/pull/4316).
Fundamentally, while we need an immutable identity, the reality is that `Resource`
in today's OpenTelemetry usage is not strong enough to support key use cases. For example,
OpenTelemetry JS, in the node.js environment, cannot guarantee that all identifying
attributes for Resource are discovered prior to SDK startup, leading to an "eventual identity" situation
that must be addressed in the Specification. Additionally, our Client/Browser SIG has been
trying to model the notion of "User Session" which has a much shorter lifespan than the SDK itself, so
requiring a single identity that is both immutable and matches the SDK lifetime prevents any good mechanism of reporting user session.

However, [OTEP 4316](https://github.com/open-telemetry/opentelemetry-specification/pull/4316) explores
relaxing the immutability restriction vs. providing a new mechanism. During prototyping,
initially this seemed to be easily accomplished, but ran into major complications both in interactions
with OpAmp (where a stable identity for the SDK is desired), and in designing a Metrics SDK, where
changes in Resource mean a dynamic and divergent storage strategy, without a priori knowledge of whether these resource mutations are
relevant to the metric or not.

Additionally, today when reporting data from one "process" about multiple resources, the only recourse available is to instantiate
multiple SDKs and define different resources in each SDK.  This absolute separation can be highly problematic with the notion of
"built-in" instrumentation, where libraries (e.g. gRPC) come with an out-of-the-box OpenTelemetry support and it's unclear how
to ensure this instrumentation is use correctly in the presence of multiple SDKs.

## Explanation

We proposes these new fundamental concepts in OpenTelemetry:

- `Resource` *remains immutable*
  - Building on [OTEP 264](0264-resource-and-entities.md), identifying attributes
    are clearly outlined in Resource going forward, addressing unclear real world usage of Resource attributes ([e,g, identifying attributes in OpAMP](https://github.com/open-telemetry/opamp-spec/blob/main/specification.md#agentdescriptionidentifying_attributes)).
  - SDK will be given an explicit initialization stage where `Resource` is not in a complete state, addressing OpenTelemetry JS concerns around async resource detection.
- `InstrumentationScope` is enhanced with `Entity` similar to `Resource`.
  - When using `Get a Meter` or `Get a Tracer` operations in OpenTelemetry, we could already optionally specify a set of `Attribute`s. Now
    we can specify a full `Entity`.
  - When an `Entity` X exists on `InstrumentationScope`, this now means "observing X in the context of the current `Resource`". For example,
    on a Mobile device, an immutable `Resource` that identifies the device would be constructed. "Session" now becomes an Entity
    attached to the `InstrumentationScope`, meaning events, spans and metrics generated are against the "sesion in the context of the device".

## Internal details

TODO - introduction.

### API Details

Previously, every `Get A {signal reporter}` operation must accept the following
instrumentation scope parameters:

* `name`: Specifies the name of the [instrumentation scope](../../specification/common/instrumentation-scope.md).

* `version` (optional): Specifies the version of the instrumentation scope if
  the scope has a version (e.g. a library version). Example value: 1.0.0.

* `schema_url` (optional): Specifies the Schema URL that should be recorded in
  the emitted telemetry.

* `attributes` (optional): Specifies the instrumentation scope attributes to
  associate with emitted telemetry. This API MUST be structured to accept a
  variable number of attributes, including none.


Going forward, these operations (`Get a Logger`, `Get a Meter`, `Get a Tracer`)
will be updated to include an additional optional parameter:

* `entities` (optional): Specifies the `Entity` set to associate with 
  emitted telemetry.

Any `attributes` provided which conflict with those attributes in the provided
`entities` consitutes an error and MUST be reported by the SDK.  The SDK
MAY resolve the discrepency without causing a fatal error. In this case,
the entity data model SHOULD take precedence over the `attributes` provided.

The set of `Entity` provided to these operations MUST only include one `Entity`
per `type`.

#### Entity

An `Entity` is a collection of the following values:

- `type`: A string describing the class of the Entity.
- `id`: An attribute collection that identifies an instance of the Entity.
- (optional) `description`: An attribute collection that describes the instance
  of the Entity.
- (optional) `schema_url`: Specifies the Schema URL that should be recorded for
  this Entity.

An `Entity` is uniquely identified by the combination of its `type` and `id`.

`schema_url` defines version of the schema used to describe an `Entity`. If
two entities exist with the same identity and different `schema_url`s, they
MUST be considered in conflict with each other.

### SDK Details

The SDK is updated to, explicitly, include three new components:

- `ResourceInitializer`: A formalized component that is responsible for
  determining the `Resource` an SDK will use.
- `ResourceListener`: A formalized component for notifying the rest of the
  SDK that resource initialization has completed.
- `Resource Detector`: A formalized component that is responsible for
  detecting `entity`s on the initial `Resource`.

Additionally the following key changes are made to the SDK:

- All `{Tracer/Meter/Logger}Provider` components are updated to use the
  `ResourceInitializer` instead of directly accepting a `Resource`.
  - This MAY be done via the `ResourceListener` component defined.
  - This MAY be done via delaying SDK initializtion until a `Resource`
    is available on `ResourceInitializer`
  - The default SDK constructors MUST use (or recommend) `ResourceInitializer`.
- `MeterProvider` MUST treat entity found on InstrumentationScope as identifying,
  an aggregate reported events separately by scope. Note: this is the case in
  the specification today, however many implementations do not yet respect
  InstrumentationScope loose

#### ResourceListener

The `ResourceListener` MUST provide the following operations in the SDK:

* `On Resource Initialize`

##### On ResourceInitialize

`On ResourceInitialize` MUST accept the following parameters:

* `Resource`: represents the entire set of resources after initialize.
* `status`: represents the status of resource initialization.

This operation MUST only be called once per ResourceInitializer.

#### ResourceInitializer

The `ResourceInitializer` MUST provide the following operations in the SDK:

* `On Change`
* (optional) `GetResource`

ResourceInitializer has two states:

- *DETECTING*: The provider is waiting for ResourceDetectors to complete.
- *INITIALIZED*: A complete resource is available and ResourceListeners will
  be notified of the final resource.

##### ResourceInitializer creation

Creation of a ResourceInitializer MUST accept the following parameters:

* `detectors`: a list of ResourceDetectors.
* (optional) `initialization_timeout`: A timeout for when to abandon slow
  ResourceDetectors and consider a resource initialized.

ResourceInitializer MUST allow initial resource detection during its creation. This
initialization SHOULD not block other SDK providers from initializing (e.g.
MeterProvider, TracerProvider).

A ResourceInitializer MAY allow customizable concurrency behavior, e.g. using a
separate thread for ResourceListener events.

Internally, the entities discovered via resource detection MUST be merged in
the order provided to create the initial resource.

During resource detection, ResourceInitializer MUST NOT fire any ResourceListener
events.

Upon completion of the resource detection phase, ResourceInitializer MUST fire
an `On ResourceInitialize` event to all ResourceListeners.

Any calls to `GetResource` operation, if provided, SHOULD block until
resource detection is completed.

Upon failure for resource detection to complete within a timeout, a resource
SHOULD be constructed with available completed detection, `GetResource`
operations MUST be unblocked and `On ResourceInitialize` event MUST be fired
to all ResourceListeners. This call MUST provide a failure status.

##### On Change

`On Change` registers a `ResourceListener` to be called when a Resource has
been detected or detection has failed.

If the `EntityProvider` is already initialized, then it MUST call
`On ResourceInitialize` immediately with the current resource held by the
`ResourceInitializer`.

##### Get Resource

`Get Resource` MUST return a reference to the current resource held by the
ResourceInitializer.

This operation MAY block when ResourceInitializer is in a DETECTING,
but MUST NOT block indefinitely.

#### ResourceDetector

A `ResourceDetector` concept is updated.

ResourceDetector MUST provide the following operations:

- `Detect entities`

##### Detect Entities operation

The Detect Entities Operation SHOULD allow asynchronous or long-running
exeuction, e.g. issuing an HTTP request to a local service for identity, reading
from disk, etc.

The Detect Entities Operation SHOULD return a status to indicate completion or
failure.

The Detect Entities Operation MUST have a mechanism to report detected `Entity`
to the ResourceInitializer. This MUST include the following:

- The `type` of the Entity.
- (optional) The `schema_url` of the Entity.
- The `id` of the Entity (as a set of attributes).
- (optional) The `description` of the Entity (as a set of attributes).

The Detect Entities operation MAY be asynchronous.

### Protocol Details

The OpenTelemetry Protocol (OTLP) will be modified such that
`InstrumentationScope` will support carrying `Entity` objects. There are two
ways this could be done:

- A new `entity_refs` field on `InstrumentationScope` similar to what was
  done for resource. This would avoid breaking implementations which make use
  of additional attributes in `InstrumentationScope`, as this field would still
  contain all new attributes for the scope.
- A new `entities` field on `InstrumentationScope` which would contain the
  entire set of entities and all values. Optional attributes would be stored
  separately to `entities`, and consumers of OTLP would need to know about
  both fields.

## Trade-offs and mitigations

The primary trade-offs to make here are around "breaking changes" and subtle
differences in generated telemetry for code leveraging Entity vs. code which
does not. We need give room for consumers of OTLP (vendors, databases, collector)
time to support the new semantics of Entity prior to data showing up which would
not be correctly interpreted without understanding these new semantics. As such,
primarily:

- Understanding that two `InstrumentationScope`s are different because of the
  `Entity` data within them.
- Appropriately aggregating or finding data about an `Entity`. If that entity
  is now reported in `InstrumentationScope`, then older systems may no longer
  be able to interact with it.

## Prior art and alternatives

OpenCensus previously allowed contextual tags to be specified dynamically and used everywhere metric 
measurements were reported. Users were then required to select which of these were useful to them via
the definition of "Views". OpenTelemetry has aimed for a simpler solution where every
metric has an implicit View definition, and we leverage metric advice to allow sending attributes
than is naturally used when reporting the metric.

As called out in the description, [OTEP 4316](https://github.com/open-telemetry/opentelemetry-specification/pull/4316)
proposes making resource fully mutable, which comes with its own set of tradeoffs.

Today, Semantic Conventions already defines `Entity` and uses it to group and
report `Resource` attributes cohesively. Additionally, Semantic convention only
models "entity associations", that is requiring a signal (e.g. a metric, event
or span) to be attached to an entity. For example, the `system.cpu.time` metric
is expected to be associated with a `host` entity. This association makes no
assumption about whether that is through `Resource` or some other mechanism,
and can therefore be extended to support `InstrumentationScope` based entities.

## Open questions

Adding entity in InstrumentationScope has a lot of implications that must be
resolved.

### What are the SDK safeguards against high-cardinality Entities?

As seen in [Issue #3062](https://github.com/open-telemetry/opentelemetry-specification/issues/3062),
systems observing multiple tenants need to ensure that tenants which are only observed briefly do not
continue to consume resources (particularly memory) for long periods of time. There needs to be
some level of control (either direct or implicit) in allowing new "Scope with Entity" to be created.

### What happens when an entity exists within Resource and InstrumentationScope?

Should we consider this a failure or a feature?

For simplicity in modeling, we plan to prototype where this is *disallowed*
until proven we need this, in which case we need crisp language about
what this models exactly.

For now, only ONE entity of a given type will be allowed across both
`Resource` and `InstrumentationScope` within the SDK.

### How to represent Entity in InstrumentationScope?

Should we do the same thing as `Resource` or something more direct?

Due to mitigations and concerns around compatibility, we recommend sticking to
the same compatibility decision as `Resource` for `InstrumentationScope`.

### Are descriptive attributes allowed to change for Resource?

Its not clear how resource immutability is kept or what is meant by immutable.
Will the resource emitted on the first export be the same as the one emitted for
the entire lifetime of the process? Are descriptive attributes on entities
attached to resource still allowed to change? What about attaching new entities
to that resource?

For now:

- The set of entities reported on Resource becomes locked.
  All identifying attributes are also locked.
- Whether we want to allow descriptive attributes to change - this can be
  determined or evolve over time. Until the ecosystem around OTLP is leveraging
  the "identity" attributes of Entity for Resource, we should not allow
  mutation of descriptive attributes.

### What is the expected impact on Collector components?

How should standard Collector processors (like the attributes processor,
resource processor, or filter processor) be updated to interact with Entities
within the InstrumentationScope?

### How do we guide developers on when to use InstrumenationScope vs. Resource?

The distinction between an immutable Resource entity and a "mutable" Scope
entity is subtle. The Resource begins to take on the identity of the SDK itself
while Scope allows "refinement" of that identity, within some bound.

## Prototypes

TODO: **In Progress**

## Future possibilities

This proposal brings strong multi-tenant capabilities to the OpenTelemetry SDK.  One possibility
is to improve the interaction between dynamic `Context` and `IntrumentationScope`, e.g. allowing
some level of interaction between `InstrumentationScope`'s entity set and `Context`.
