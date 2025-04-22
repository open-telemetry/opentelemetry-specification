# Extending attributes to support complex values

* [Why?](#why)
  * [Why do we want complex attributes on spans?](#why-do-we-want-complex-attributes-on-spans)
  * [Why do we want to extend standard attributes?](#why-do-we-want-to-extend-standard-attributes)
  * [Why isn't it a breaking change?](#why-isnt-it-a-breaking-change)
* [How](#how)
  * [API](#api)
  * [SDK](#sdk)
    * [Signals that support complex attributes](#signals-that-support-complex-attributes)
    * [Signals that don't support complex attributes](#signals-that-dont-support-complex-attributes)
    * [Handling complex attributes](#handling-complex-attributes)
  * [Semantic conventions](#semantic-conventions)
* [Trade-offs and mitigations](#trade-offs-and-mitigations)
* [Prior art and alternatives](#prior-art-and-alternatives)
* [Open questions](#open-questions)
* [Future possibilities](#future-possibilities)

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
[considered a breaking change](../specification/common/README.md#standard-attribute).

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

Existing APIs that create or add attributes will be extended to support value with type `AnyValue`.

It's up to the language to expose an `AnyValue` API for type checking, ergonomics, or performance.
Alternatively, it may use a base object or another standard library type.

Exposing multiple `Attributes` types is NOT RECOMMENDED if conversion between them
is non-trivial in terms of usability or performance.

The SDK is responsible for handling attribute types depending on the signal.

> [!NOTE]
>
> While OTel metrics are designed for aggregation, future SDK implementations
> may choose to record measurements as individual events. This would make complex
> values acceptable in metrics.
>
> Ultimately, it’s up to the SDK implementation to decide whether to support complex
> values for a given signal. Guidance for OTel-hosted SDKs is provided in the next section.
>
> The API, however, is less opinionated. It should not offer conveniences for recording
> complex attributes on metrics (resources, etc), but it does not have to make it impossible.

### SDK

#### Signals that support complex attributes

**The OTel SDK MUST support complex attributes on spans, logs, profiles, and descriptive
entity attributes.**

Any future OTel signals SHOULD support complex attributes unless there is a
reason not to, which MUST be documented in the specification.

By default, the OTel SDK SHOULD pass complex attributes to the processing pipeline.
The SDK MUST support reading and modifying complex attributes during processing.

If `AnyValue` is not defined at the API level, the OTel SDK SHOULD provide it as
a contract for processors and exporters. The SDK MUST document the contract and
SHOULD convert non-primitive input values to this common type. If conversion is
not possible - e.g., when a non-serializable or unknown object is passed - the SDK
SHOULD record string representation of the provided object.

See the [Configuring complex attribute handling](#configuring-complex-attribute-handling)
section for customization options.

#### Signals that don't support complex attributes

**The OTel SDK SHOULD serialize complex attributes to JSON string if they are added
to metrics, resources, instrumentation scope, or used as identifying attributes on entities.**

The SDK MAY allow customizing this behavior, see [Configuring
complex attribute handling](#allow-recording-structured-attributes) section.

> [!Note]
>
> Complex attributes are not intended to be used on metrics and other
> signals in this category. Their usage is discouraged and expected to be accidental.
>
> JSON serialization overhead is limited to specific applications and is used as a
> fallback (better than dropping).

#### Handling complex attributes

The SDK SHOULD allow per-signal configuration of [attribute limits](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/common/README.md#attribute-limits).

**Attribute value length limit** SHOULD be applied to all leaf string nodes in `AnyValue`.
String values SHOULD be truncated to the configured limit.

Leaf nodes of an `AnyValue` attribute SHOULD count toward the **attribute count limit**.
If the limit is reached, the SDK MUST drop the entire `AnyValue` attribute;
partial exports are not allowed.

A **new attribute limit** property will be introduced to control how and if complex
attributes are handled, with the following options:

- **pass as is**
  - Default for spans, logs, profiles, and descriptive entity attributes.
  - The SDK MAY support this option for all signals.

- **serialize to JSON string**
  - Default for metrics, resources, instrumentation scopes, and identifying entity attributes.
  - The SDK MUST support this option for all signals and SHOULD provide per-signal configuration.

- **drop**
  - The SDK MAY support this option

### Semantic conventions

Semantic conventions will be updated with the following guidance

- Standard attributes SHOULD be used whenever possible. Semantic conventions SHOULD
  assume that backends do not index individual properties of complex attributes,
  that querying or aggregating on such properties is inefficient and complicated,
  and that reporting complex attributes carries higher performance overhead.

- Complex attributes that are likely to be large (when serialized to a string) SHOULD
  be added as *opt-in* attributes. *Large* will be defined based on common backend
  attribute limits, typically around 4–16 KB.

- Complex attributes MUST NOT be used on metrics, resources, instrumentation scopes,
  or as identifying attributes on entities.

## Trade-offs and mitigations

1. Allowing arbitrary objects as attributes is convenient but increases the risk of
   including large, sensitive, mutable, non-serializable, or otherwise problematic
   data in telemetry.

   It is RECOMMENDED to enforce `AnyValue` compatibility at the API level.
   Users and instrumentations SHOULD define custom `AnyValue`-compatible models
   to minimize misuse and reduce performance overhead.

   OTel SDKs MAY provide convenience methods to convert arbitrary objects to `AnyValue`.
   If such convenience is provided, it is RECOMMENDED to limit supported types
   to primitives, arrays, standard library collections, named tuples, JSON objects, and
   similar structures.

   If the object has any property with an unrecognized type, it is RECOMMENDED
   to fall back to recording a string representation of the whole object to minimize
   the risk of unintentional use of complex attributes.

2. While it should be possible to record complex data in telemetry, many backends do not
   support it well - or at all - which can result in individual complex attributes
   or entire spans being dropped or rejected.

   In the future, support for complex attributes may be negotiated via OpAMP,
   allowing this behavior to be configured based on backend capabilities without
   requiring user intervention.

   In the meantime, we plan to mitigate this through:

   - Requiring an SDK mode that serializes complex attributes to JSON
   - A collector transformation processor that already can drop, flatten, serialize, or
     truncate complex attributes using OTTL
   - Semantic conventions guidance that discourages their use

## Prior art and alternatives

TODO

## Open questions

TODO

## Future possibilities

We can consider a separate set of attribute limits specifically for complex values,
including a total size limit and ability to estimate `AnyValue` object size.