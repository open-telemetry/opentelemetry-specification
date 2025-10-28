# Extending attributes to support complex values

<!-- toc -->

- [Glossary](#glossary)
- [Why?](#why)
  * [Why do we want complex attributes on spans?](#why-do-we-want-complex-attributes-on-spans)
  * [Why do we want to extend standard attributes?](#why-do-we-want-to-extend-standard-attributes)
  * [Why doesn't this require a major version bump?](#why-doesnt-this-require-a-major-version-bump)
- [How](#how)
  * [API](#api)
  * [SDK](#sdk)
    + [`AnyValue` implementation notes](#anyvalue-implementation-notes)
    + [Attribute limits](#attribute-limits)
  * [Exporters](#exporters)
  * [Semantic conventions](#semantic-conventions)
  * [Proto](#proto)
- [Trade-offs and mitigations](#trade-offs-and-mitigations)
  * [Backends don't support `AnyValue` attributes](#backends-dont-support-anyvalue-attributes)
  * [Arbitrary objects are dangerous](#arbitrary-objects-are-dangerous)
- [Prototypes](#prototypes)
- [Future possibilities](#future-possibilities)
  * [Configurable OTLP exporter behavior (both SDK and Collector)](#configurable-otlp-exporter-behavior-both-sdk-and-collector)
  * [Record pointer to repetitive data](#record-pointer-to-repetitive-data)
- [Backend research](#backend-research)
- [Appendix](#appendix)

<!-- tocstop -->

## Glossary

In the context of this OTEP, we use the following terminology:

- **Simple attributes** are attributes with primitive types or homogeneous arrays of primitives.
  Their types are known in advance and correspond to the top-level  `string_value`,
  `bool`, `int64`, `double`, and `ArrayValue` of those types in the
  [AnyValue proto definition](https://github.com/open-telemetry/opentelemetry-proto/blob/42319f8b5bf330f7c3dd4a097384f9f6d5467450/opentelemetry/proto/common/v1/common.proto#L28-L40).
  These are currently referred to as *standard* attributes in the
  [specification](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.44.0/specification/common/README.md)

- **Complex attributes** include all other values supported by the `AnyValue` proto,
  such as null (empty) value, maps, heterogeneous arrays, and combinations of those with primitives.
  Byte arrays are also considered complex attributes, as they are excluded from
  the current definition of *standard* attributes.

- **AnyValue** represents the type of *any* (simple or complex) attribute value on
  the API, SDK, and [proto level](https://github.com/open-telemetry/opentelemetry-proto/blob/42319f8b5bf330f7c3dd4a097384f9f6d5467450/opentelemetry/proto/common/v1/common.proto#L28-L40).

  It's also known as `any` in the [Log data model](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.44.0/specification/logs/data-model.md#type-any)

This distinction between simple and complex attributes is not intended for the
spec language, but is helpful here because the OTEP proposes including both *simple*
and *complex* attributes in the set of *standard* attributes.

## Why?

### Why do we want complex attributes on spans?

There are a number of reasons why we want to allow complex attributes on spans:

- Emerging semantic conventions have demonstrated the usefulness of
  including complex attributes on spans, such as
  [capturing prompts and completions](https://github.com/open-telemetry/semantic-conventions/pull/2179)
  for Generative AI
  and [capturing request errors](https://graphql.org/learn/response/#request-errors)
  for GraphQL.
- Many users already add complex attributes to spans by JSON-encoding them.
  Supporting complex attributes natively enables future possibilities like
  collector transformations, better attribute truncation, and native
  storage of complex attributes in backends.
- During the span event deprecation process, we found that some people
  use span events to represent complex data on spans.
  Providing support for complex attributes on spans would offer a more natural
  way to store this data.
- During the event stabilization process, it became clear that
  [spans and events are often thought of as being conceptual
  twins](https://opentelemetry.io/blog/2025/opentelemetry-logging-and-you/#how-is-this-different-from-other-signals),
  and that the choice between modeling something as a span or an event should not
  be influenced by whether complex attributes are needed
  (given that logs already support complex attributes).

### Why do we want to extend standard attributes?

Instead of introducing a second set of "extended" attributes that can be used on
spans and events, we propose to extend the standard attributes.

Having multiple attribute sets across the API
[creates ergonomic challenges](https://github.com/open-telemetry/opentelemetry-specification/issues/4201).
While there are some mitigations (as demonstrated in
[opentelemetry-java#7123](https://github.com/open-telemetry/opentelemetry-java/pull/7123) and
[opentelemetry-go#6180](https://github.com/open-telemetry/opentelemetry-go/pull/6180)),
extending the standard attributes provides a more seamless and user-friendly API experience.

### Why doesn't this require a major version bump?

Currently, the SDK specification has a clause that says extending
the set of standard attribute would be
[considered a breaking change](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.44.0/specification/common/README.md#standard-attribute).

We believe that removing this clause and extending standard
attributes can be done gracefully across the OpenTelemetry ecosystem
without requiring a major version bump:

- Language SDKs can implement this without breaking their backwards
  compatibility guarantees (e.g., [Java's](https://github.com/open-telemetry/opentelemetry-java/blob/main/VERSIONING.md)).
- While backends may still need to add support for complex attributes,
  this is the case with the introduction of any new OTLP feature.
  - Bumping the OTLP minor version is already the normal communication mechanism
    for this kind of change.
  - SDKs will be required to only emit complex attributes under that OTLP version
    or later.
  - Stable exporters will be prohibited from emitting complex attributes by default on signals
    other than Logs until at least 6 months after this OTEP is merged.
  - A reasonably straightforward implementation option for backends is to just
    JSON serialize complex attributes and store them as strings.

## How

### API

Existing APIs that create or add attributes will be extended to support
*complex attributes*.

It's RECOMMENDED to expose an `AnyValue` type - the API representing complex or
simple attribute value for type checking, ergonomics, and performance reasons.

Exposing multiple types of attribute sets is NOT RECOMMENDED, such as having "ExtendedAttributes" in addition to "Attributes".

OTel API MUST support setting complex attributes on spans, logs, profiles,
span links, and as descriptive entity attributes.

OTel API MAY support setting complex attributes on metrics, resources,
instrumentation scope, span events, and as identifying entity attributes.

> [!NOTE]
> "MAY" is used here instead of "MUST" to give flexibility to dynamically
> typed language APIs since there are no concrete use cases at this time
> requiring complex attributes in these areas.
>
> Most likely statically typed languages will choose to support
> setting complex attributes uniformly everywhere.
>
> This requirement level could change from "MAY" to "MUST" in the future
> if we uncover use cases for complex attributes in these areas.

API documentation and spec language around complex attributes SHOULD include
language similar to this:

> Simple attributes SHOULD be used whenever possible. Instrumentations SHOULD
> assume that backends do not index individual properties of complex attributes,
> that querying or aggregating on such properties is inefficient and complicated,
> and that reporting complex attributes carries higher performance overhead.

### SDK

OTel SDK MUST support setting complex attributes on spans, logs, profiles,
span links, and as descriptive entity attributes.

OTel SDK MAY support setting complex attributes on metrics, exemplars, resources,
instrumentation scope, span events, and as identifying entity attributes.

> [!NOTE]
> "MAY" is used here instead of "MUST" to give flexibility to dynamically
> typed language SDKs since there are no concrete use cases at this time
> requiring complex attributes in these areas.
>
> Most likely statically typed languages will choose to support
> setting complex attributes uniformly everywhere.
>
> This requirement level could change from "MAY" to "MUST" in the future
> if we uncover use cases for complex attributes in these areas.

The SDK MUST support reading and modifying complex attributes during processing
whenever they are allowed on the API surface.

#### `AnyValue` implementation notes

If the API supports `AnyValue` attributes on metrics, instrumentation scopes,
resources, or identifying entity attributes where attribute equality is extensively
used to identify tracers, meters, loggers, or time series, the `AnyValue`
implementation MUST provide deep equality checks.

For `AnyValue` instances containing one or more lists of key-value pairs:

- the equality of `AnyValue` instances MUST NOT be affected by the ordering of
  the key-value pairs within the list.
- the equality behavior is unspecified if duplicate keys are present.

#### Attribute limits

Complex attribute limits are to be defined separately from this OTEP and apply to all
signals where complex attributes are allowed.

This is tracked in [#4487](https://github.com/open-telemetry/opentelemetry-specification/issues/4487)

### Exporters

OTLP exporter SHOULD pass `AnyValue` attributes to the endpoint.

Exporters for protocols that do not natively support complex values, such as Prometheus,
SHOULD represent complex values as JSON-encoded strings following
[attribute specification](/specification/common/README.md#attribute).

When serializing `AnyValue` objects to JSON, it is RECOMMENDED to sort lists
of key-value pairs lexicographically by key and apply additional settings that
enhance serialization stability.

### Semantic conventions

Semantic conventions will be updated with the following guidance:

- Simple attributes SHOULD be used whenever possible. Semantic conventions SHOULD
  assume that backends do not index individual properties of complex attributes,
  that querying or aggregating on such properties is inefficient and complicated,
  and that reporting complex attributes carries higher performance overhead.

- Complex attributes that are likely to be large (when serialized to a string) SHOULD
  be added as *opt-in* attributes. *Large* will be defined based on common backend
  attribute limits, typically around 4–16 KB.

- Complex attributes MUST NOT be used on metrics, resources, instrumentation scopes,
  or as identifying attributes on entities.

### Proto

OTLP uses `AnyValue` attributes on all signals, so the changes would be limited
to updating comments like [this one](https://github.com/open-telemetry/opentelemetry-proto/blob/be5d58470429d0255ffdd49491f0815a3a63d6ef/opentelemetry/proto/trace/v1/trace.proto#L209-L213)
and adding changelog record.

## Trade-offs and mitigations

### Backends don't support `AnyValue` attributes

While it should be possible to record complex data in telemetry, many backends do not
support it, which can result in individual complex attributes being dropped.

We mitigate this through:

- Introducing new APIs in the experimental parts of the OTel API which will limit
  the impact of unsupported attribute types to early adopters, while giving
  backends time to add support.

- Semantic conventions guidance that limits usage of complex attributes.

- Existing collector transformation processor that can drop, flatten, serialize,
  or truncate complex attributes using OTTL.

### Arbitrary objects are dangerous

Allowing arbitrary objects as attributes is convenient but increases the risk of
including large, sensitive, mutable, non-serializable, or otherwise problematic
data in telemetry.

OTel SDKs that provide convenience to convert arbitrary objects to `AnyValue`
SHOULD limit supported types to primitives, arrays, standard library collections,
named tuples, JSON objects, and similar structures following
[mapping to OTLP AnyValue](/specification/common/attribute-type-mapping.md#converting-to-anyvalue).

Falling back to a string representation of unknown objects is RECOMMENDED to
minimize the risk of unintentional use of complex attributes.

Prior art on AnyValue conversion: [Go](https://github.com/open-telemetry/opentelemetry-go-contrib/blob/72cccd8065dcfd84b69f34d8cb6f349a547fedce/bridges/otelslog/convert.go#L20),
[.NET](https://github.com/open-telemetry/opentelemetry-dotnet/blob/71abd4169b4b6c672343b37c32e3337bc227ed32/src/OpenTelemetry/Logs/ILogger/OpenTelemetryLogger.cs#L134),
[Python](https://github.com/open-telemetry/opentelemetry-python/blob/00329e07fb01d7c3e43bb513fe9be3748745c52e/opentelemetry-api/src/opentelemetry/attributes/__init__.py#L121)

## Prototypes

- [opentelemetry-python#4587](https://github.com/open-telemetry/opentelemetry-python/pull/4587)
- [opentelemetry-go#6809](https://github.com/open-telemetry/opentelemetry-go/pull/6180)

## Future possibilities

### Configurable OTLP exporter behavior (both SDK and Collector)

The OTLP exporter behavior for complex attributes can be made customizable on a per-signal
basis, allowing complex attributes to be:

- passed through (the default),
- serialized to JSON, or
- dropped

This option may be useful as a workaround for applications
whose backend does not handle complex attribute types gracefully.

### Record pointer to repetitive data

Aggregating over structured data introduces performance overhead and additional complexity, such as requiring deep equality checks.

If the data is repetitive, it can be recorded once and assigned a unique identifier. Subsequent telemetry items can then reference this identifier instead of duplicating the data.

This approach reduces performance overhead and the volume of transmitted data and can be implemented incrementally as an optimization. It should not affect the instrumentation API or, more importantly, the user experience, including queries and dashboards.

## Backend research

See [the gist](https://gist.github.com/lmolkova/737ebba190b206a5d60bbc075fea538b)
for additional details.

| Backend                           | Handles complex attributes gracefully? | Comments        |
| --------------------------------- | ----- | ------------------------------ |
| Jaeger (OTLP)                     | :white_check_mark: | serializes to JSON string |
| Prometheus with OTLP remote write | :white_check_mark: | serializes to JSON string |
| Grafana Tempo (OTLP)              | :white_check_mark: | serializes to JSON string, viewable but can't query using this attribute |
| Grafana Loki (OTLP)               | :white_check_mark: | flattens |
| Aspire dashboard (OTLP)           | :white_check_mark: | serializes to JSON string |
| ClickHouse (collector exporter)   | :white_check_mark: | serializes to JSON string, can parse JSON and query |
| Honeycomb (OTLP)                  | :white_check_mark: | flattens if less than 5 layers deep, not array or binary data, JSON string otherwise |
| Logfire (OTLP)                  | :white_check_mark: | stored as JSON, native support for JSON in queries |
| New Relic (OTLP)                  | :white_check_mark: | drops the complex attribute | |
| Splunk (OTLP and HEC exporter)    | :white_check_mark: | flattens for logs (HEC), serializes to JSON string for traces and metrics (OTLP) |

> [!NOTE]
> This list only reflects the behavior at the time of writing and may change in the future.

## Appendix

The [Extend the set of attribute value types #4651](https://github.com/open-telemetry/opentelemetry-specification/pull/4651) PR implements part of this OTEP by requiring that both the OTel API and SDK MUST support complex attributes.
Some languages aim to support complex attributes for all kinds of telemetry.
To maintain consistency across languages, we agreed that all languages should provide the same level of support for complex attributes.
