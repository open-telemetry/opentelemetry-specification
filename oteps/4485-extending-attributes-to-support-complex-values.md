# Extending attributes to support complex values

* [Glossary](#glossary)
* [Why?](#why)
  * [Why do we want complex attributes on spans?](#why-do-we-want-complex-attributes-on-spans)
  * [Why do we want to extend standard attributes?](#why-do-we-want-to-extend-standard-attributes)
  * [Why isn't it a breaking change?](#why-isnt-it-a-breaking-change)
* [How](#how)
  * [API](#api)
  * [SDK](#sdk)
    * [Attribute limits](#attribute-limits)
  * [Semantic conventions](#semantic-conventions)
* [Trade-offs and mitigations](#trade-offs-and-mitigations)
  * [Backends don't support `AnyValue` attributes](#backends-dont-support-anyvalue-attributes)
  * [Arbitrary objects are dangerous](#arbitrary-objects-are-dangerous)
* [Future possibilities](#future-possibilities)
  * [Configurable SDK behavior](#configurable-sdk-behavior)
  * [Additional size limits](#additional-size-limits)

## Glossary

In the context of this OTEP, we use the following terminology:

- **Simple attributes** are attributes with primitive types or homogeneous arrays of primitives.
  Their types are known in advance and correspond to the top-level  `string_value`,
  `bool`, `int64`, `double`, and `ArrayValue` of those types in the
  [AnyValue proto definition](https://github.com/open-telemetry/opentelemetry-proto/blob/42319f8b5bf330f7c3dd4a097384f9f6d5467450/opentelemetry/proto/common/v1/common.proto#L28-L40).
  These are currently referred to as *standard* attributes in the
  [specification](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.44.0/specification/common/README.md)

- **Complex attributes** include all other values supported by the `AnyValue` proto,
  such as maps, heterogeneous arrays, and combinations of those with primitives.
  Byte arrays are also considered complex attributes, as they are excluded from
  the current definition of *standard* attributes.

This distinction is not intended for the spec language, but is helpful here
because the OTEP proposes including both *simple* and *complex* attributes
in the set of *standard* attributes.

## Why?

### Why do we want complex attributes on spans?

There are a number of reasons why we want to allow complex attributes on spans:

- Emerging semantic conventions, such as Generative AI,
  demonstrate the usefulness of including complex attributes on spans.
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
  twins.](https://opentelemetry.io/blog/2025/opentelemetry-logging-and-you/#how-is-this-different-from-other-signals),
  and the choice between modeling something as a span or an event should not
  be influenced by whether complex attributes are needed.

### Why do we want to extend standard attributes?

Instead of introducing a second set of "extended" attributes that can be used on
spans and events, we propose to extend the standard attributes.

Having multiple attribute sets across the API
[creates ergonomic challenges](https://github.com/open-telemetry/opentelemetry-specification/issues/4201).
While there are some mitigations (as demonstrated in
[opentelemetry-java#7123](https://github.com/open-telemetry/opentelemetry-java/pull/7123) and
[opentelemetry-go#6180](https://github.com/open-telemetry/opentelemetry-go/pull/6180)),
extending the standard attributes provides a more seamless and user-friendly API experience.

### Why isn't it a breaking change?

Currently, the SDK specification states that extending the set of standard
attribute types to the full set of attribute types supported by OTLP would be
[considered a breaking change](/specification/common/README.md#standard-attribute).

We propose revisiting this and allowing extending the set of standard attribute
types to the full set of attribute types supported by OTLP, without treating it as
a breaking change, for the following reasons:

- Language SDKs can implement this without breaking their backwards
  compatibility guarantees (e.g., [Java's](https://github.com/open-telemetry/opentelemetry-java/blob/main/VERSIONING.md)).
- The OpenTelemetry Collector already supports transforming data to complex attributes
  via OTTL across all signals, so backends are not free from an obligation to handle
  complex attributes gracefully (even if that just means dropping them currently).
- While backends may still need to add support for complex attributes,
  this is the case with the introduction of any new OTLP feature.
  Bumping the OTLP minor version is already the normal communication mechanism
  for this kind of change.
  A reasonably straightforward implementation option for backends is to just
  JSON serialize complex attributes and store them as strings.

## How

### API

Existing APIs that create or add attributes will be extended to support value
with type `AnyValue`.

It's RECOMMENDED to expose an `AnyValue` API for type checking, ergonomics,
and performance.

Exposing multiple `Attributes` types is NOT RECOMMENDED.

> [!NOTE]
>
> While OTel metrics are designed for aggregation, future SDK implementations
> may choose to record measurements as individual events. This would make complex
> values acceptable in metrics.
>
> Ultimately, it’s up to the backend to decide whether to support complex
> values for a given signal or serialize/drop it otherwise.

### SDK

**The OTel SDK MUST support complex attributes on all telemetry signals.**

It includes spans, logs, and profiles where complex attributes have known use-cases as
well as metrics, resources, instrumentation scope, and entities where complex attributes
usage is currently discouraged and expected to be accidental.

Any future OTel signals SHOULD support complex attributes unless there is a
reason not to, which MUST be documented in the specification.

The OTel SDK SHOULD pass both simple and complex attributes to the processing
pipeline as `AnyValue`.
The SDK MUST support reading and modifying complex attributes during processing.

#### Attribute limits

The SDK SHOULD apply [attribute limits](/specification/common/README.md#attribute-limits)
to complex attributes.

**Attribute value length limit** SHOULD be applied to all leaf string nodes in
`AnyValue` which SHOULD be truncated to the configured limit.

Leaf nodes of an `AnyValue` attribute SHOULD count toward the **attribute count limit**.
If the limit is reached, the SDK MUST drop the entire `AnyValue` attribute;
partial exports are not allowed.

### Semantic conventions

Semantic conventions will be updated with the following guidance

- Simple attributes SHOULD be used whenever possible. Semantic conventions SHOULD
  assume that backends do not index individual properties of complex attributes,
  that querying or aggregating on such properties is inefficient and complicated,
  and that reporting complex attributes carries higher performance overhead.

- Complex attributes that are likely to be large (when serialized to a string) SHOULD
  be added as *opt-in* attributes. *Large* will be defined based on common backend
  attribute limits, typically around 4–16 KB.

- Complex attributes MUST NOT be used on metrics, resources, instrumentation scopes,
  or as identifying attributes on entities.

## Trade-offs and mitigations

### Backends don't support `AnyValue` attributes

While it should be possible to record complex data in telemetry, many backends do not
support it well - or at all - which can result in individual complex attributes
being dropped or rejected.

We mitigate this through:

- Introducing new APIs in the experimental parts of the OTel API which limits
  the impact of unsupported attribute types to early adopters, while giving
  backends time to add support.

- Semantic conventions guidance that limits usage of complex attributes.

- Existing collector transformation processor that can drop, flatten, serialize,
  or truncate complex attributes using OTTL.

### Arbitrary objects are dangerous

Allowing arbitrary objects as attributes is convenient but increases the risk of
including large, sensitive, mutable, non-serializable, or otherwise problematic
data in telemetry.

It is RECOMMENDED to enforce `AnyValue` compatibility at the API level.
Users and instrumentations SHOULD define custom `AnyValue`-compatible models
to minimize misuse and reduce performance overhead.

OTel SDKs MAY provide convenience methods to convert arbitrary objects to `AnyValue`.
If such convenience is provided, it is RECOMMENDED to limit supported types
to primitives, arrays, standard library collections, named tuples, JSON objects, and
similar structures following [mapping to OTLP AnyValue](/specification/common/attribute-type-mapping.md#mapping-arbitrary-data-to-otlp-anyvalue).
Falling back to a string representation of unknown objects is RECOMMENDED to
minimize the risk of unintentional use of complex attributes.

## Future possibilities

### Configurable SDK behavior

The SDK behavior for complex attributes can be made customizable on a per-signal
basis, allowing it to either **serialize complex values to JSON strings** or
**drop** the corresponding attribute.

This option may be useful as a workaround for applications that don’t use a
collector and whose backend does not handle complex attribute types gracefully.

### Additional size limits

We can consider a separate set of attribute limits specifically for complex values,
including a total size limit and ability to estimate `AnyValue` object size.
