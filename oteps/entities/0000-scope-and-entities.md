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

TODO

## Trade-offs and mitigations

TODO

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

## Prototypes

**In Progress**

## Future possibilities

This proposal brings strong multi-tenant capabilities to the OpenTelemetry SDK.  One possibility
is to improve the interaction between dynamic `Context` and `IntrumentationScope`, e.g. allowing
some level of interaction between `InstrumentationScope`'s entity set and `Context`.
