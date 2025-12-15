# Multiple Resource in SDK

Allow multiple `Resource` instances per SDK.

## Motivation

OpenTelemetry needs to address two fundamental problems:

- Reporting data against "mutable" or "changing" entities, where currently an
  SDK is allowed a single `Resource`, whose lifetime must match the lifetime of
  the SDK itself.
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
- The SDK will be identified by a single `Resource` provided during SDK startup.
  - ResourceDetection will be expanded, as described in [OTEP 264](0264-resource-and-entities.md).
  - An explicit section about SDK initialization will be created.
- Signal Providers in the SDK will allow "specialization" of the default SDK
  resource. We create new `{Signal}Provider` instances by providing a new
  `Entity` on the existing provider.
  - This will construct a new `Resource` specific to that provider.
  - The new provider will re-use all configuraiton (e.g. export pipeline)
    defined from the base provider.

## Internal details

This proposal splits between an instrumentation facing API, and required
behavior of that API in the SDK.

### API Details

Previously, every `{Signal}Provider` API defined a single
`Get a {Signal}` operation. These will be expanded with a new
`For Entity` operation, which will construct a new `{SignalProvider}`
API component for reporting against a specific `Entity`.

#### For Entity

This API MUST accept the following parameters:

* `entities`: Specifies the `Entity` set to associate with
  emitted telemetry.

Any `entities` provided which conflict with those entities already provided in
the SDK `Resource` represent an *override* of identity. The SDK MUST resolve the
conflict without causing a fatal error.

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

When `For Entity` operation is received by a provider, A new child
`Entity Bound Provider` of the same type MUST be created and returned with the
following restrictions:

- `Entity Bound Provider` MUST be associated with a newly created `Resource`
  which is the result of the incoming `Entity` set merged into the original
  `Provider`'s resource following the existing `Resource` merging algorithm.
  Telemetry created by the parent MUST continue to be associated with the
  original unmodified resource.
- The `Bound Provider` MUST share an export pipeline with its parent. The export
  component (`SpanProcessor`, `MetricReader`, `LogsProcessor`, etc) MUST not be
  `Shutdown` by the `Bound Provider`. This MAY be achieved by wrapping the export
  component in a proxy component which ignores calls to `Shutdown` or translates
  them into `Force Flush`.
- The `Bound Provider` MUST be configured exactly the same as its parent.
  A configuration change on a parent `Provider` MUST be reflected in all of its
  child `Entity Bound Providers`. This MAY be achieved by directly sharing
  the configuration object between `Providers`.
- A `Bound Provider` MUST NOT be directly configurable.
  All configuration comes from its parent.
- If `ForceFlush` or `Shutdown` is called on a `Provider` it MUST also flush all
  of its child `Entity Bound Providers`.
- If `Shutdown` is called on a `Bound Provider` it MUST be treated as a
  `Force Flush`. It MUST NOT shut down its export pipeline.

## Trade-offs and mitigations

The primary trade-offs to make here are around "breaking changes" and subtle
differences in generated telemetry for code leveraging Entity vs. code which
does not. We need give room for consumers of OTLP (vendors, databases, collector)
time to support the new semantics of Entity prior to data showing up which would
not be correctly interpreted without understanding these new semantics. As such,
primarily:

- `Entity`, as defined in OTLP, is an opt-in construct. `Resource` should be
  usable as an identity independent of `Entity`.
- Consumers should now expect SDKs reporting multiple resources in the same
  batch. Theoretically, this SHOULD already be supported due to how OTLP is
  deisgned to allow aggregation / batching of data at any point.

## Prior art and alternatives

OpenCensus previously allowed contextual tags to be specified dynamically and
used everywhere metric measurements were reported. Users were then required to
select which of these were useful to them via the definition of "Views".
OpenTelemetry has aimed for a simpler solution where every metric has an
implicit View definition, and we leverage metric advice to allow sending
attributes than is naturally used when reporting the metric.

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

### What happens when an entity already exists within Resource?

Should we consider this a failure or a feature?

We currently consider this a feature. Upon conflict, the *new* Entity would be
used in the resulting `Resource` reported for a new `{SignalProvider}`.

The SDK needs some form of stable identity for itself, however when reporting
Telemetry, it may be recording data on behalf of some other system.

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

There should be *no* impact on collector components beyond those defined in
[OTEP 4316](https://github.com/open-telemetry/opentelemetry-specification/pull/4316).

### How do we guide developers on when to use `For Entity`?

We will have clear guidance on the `For Entity` methods

## Prototypes

- Java: https://github.com/open-telemetry/opentelemetry-java/compare/main...jsuereth:opentelemetry-java:wip-entity-and-providers
- TypeScript: https://github.com/open-telemetry/opentelemetry-js/pull/5620

## Future possibilities

This proposal brings strong multi-tenant capabilities to the OpenTelemetry SDK.  One possibility
is to improve the interaction between dynamic `Context` and signals, e.g. allowing
some level of interaction `Context` and attributes / entities.

For example, rather than a lexical scope:

```js
const myMeterProvider = globalMeterProvider.forEntity(getCurrentSession())
doSomething(myMeterProvider)
```

We could allow runtime scope:

```js
const ctx = api.context.active();
api.context.with(ctx.setValue(CURRENT_ENTITY_KEY, getCurrentSession()))
doSomething()
```
