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
with OpAmp (where a stable idenitity for the SDK is desired), and in desinging a Metrics SDK, where
changes in Resource mean a dynamic and divergent storage strategy, without a priori knowledge of whether these resource mutations are
relevant to the metric or not.

Additionally, today when reporting data from one "process" about mulitple resources, the only recourse available is to instantiate
multiple SDKs and define different resources in each SDK.  This absolute separation can be highly problematic with the notion of
"built-in" instrumentation, where libraries (e.g. gRPC) come with an out-of-the-box OpenTelemetry support and it's unclear how
to ensure this instrumentation is use correctly in the presence of multiple SDKs. 

## Explanation

We proposes these new fundamental concepts in OpenTelemetry:

- `Resource` *remains immutable*
  - Building on [OTEP 264`](0264-resource-and-entities.md), identifying attirbutes
    are clearly outlined in Resource going forward, addressing unclear real world usage of Resource attributes ([e,g, identifying attributes in OpAMP](https://github.com/open-telemetry/opamp-spec/blob/main/specification.md#agentdescriptionidentifying_attributes)).
  - SDK will be given an explicit initialization stage where `Resource` is not in a complete state, addressing OpenTelemetry JS concerns around async resource detection.
- `InstrumentationScope` is enhanced with `Entity` similar to `Resource`.
  - When using `Get a Meter` or `Get a Tracer` operations in OpenTelemetry, we can already optionally specific a set of `Attributes`. Now
    we can specify a full `Entity`.
  - When an `Entity` X exists on `InstrumentationScope`, this now means "observing X in the context of the current `Resource`". For example,
    on a Mobile device. An immutable `Resource` that idnetifies the device would be constructed. "Session" now becomes an Entity
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

### SDK Details

TODO:

- EntityDetector definition
- ResourceInitializer SDK component
- Implications on MeterProvider.

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
proposes making resource fully mutable, which comes with its won set of tradeoffs.

## Open questions

Allowing a multi-tenant agency in the OpenTelemetry SDK has a set of known issues we must resolve.

### How do we Garbage collecting "stale" scopes

As seen in [Issue #3062](https://github.com/open-telemetry/opentelemetry-specification/issues/3062),
systems observing multiple tenants need to ensure that tenant which are only observed briefly do not
continue to consume resources (particularly memory) for long periods of time. There needs to be
some level of control (either direct or implicit) in allowing new "Scope with Entity" to be created.

### What happens when an entity exists within Resource and InstrumentationScope?

TODO

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

## Prototypes

**In Progress**

## Future possibilities

This proposal brings strong multi-tenant capabilities to the OpenTelemetry SDK.  One possibility
is to improve the interaction between dynamic `Context` and `IntrumentationScope`, e.g. allowing
some level of interaction between `InstrumentationScope`'s entity set and `Context`.
