# Extending attributes to support complex values

* [Changes](#changes)
  * [API](#api)
  * [SDK](#sdk)
    * [Signals that support complex attributes](#signals-that-support-complex-attributes)
    * [Signals that don't support complex attributes](#signals-that-dont-support-complex-attributes)
    * [Configuring complex attribute handling](#configuring-complex-attribute-handling)
  * [Semantic conventions](#semantic-conventions)
* [Trade-offs and mitigations](#trade-offs-and-mitigations)
* [Prior art and alternatives](#prior-art-and-alternatives)
* [Open questions](#open-questions)
* [Future possibilities](#future-possibilities)

## Changes

### API

Existing APIs that create or add attributes will be extended to support value with type Any.

It's up to the language to expose an `AnyValue` API for type checking, ergonomics, or performance.
Alternatively, it may use a base object or another standard library type.

Exposing multiple `Attributes` types is NOT RECOMMENDED if conversion between them
is non-trivial in terms of usability or performance.

The SDK is responsible for handling unsupported attribute types depending on the signal.

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
The SDK MUST support reading, validating, and modifying complex attributes within
the processing pipeline.

If `AnyValue` is not defined at the API level, the OTel SDK SHOULD provide it as
a contract for processors and exporters. If the standard library offers a
reasonable substitute, it MAY be used instead.

In either case, the SDK MUST document the contract and SHOULD convert non-primitive
input values to this common type. If conversion is not possible — e.g., when a non-serializable
or unknown object is passed — the SDK SHOULD record string representation of the
provided object.

See the [Configuring complex attribute handling](#configuring-complex-attribute-handling)
section for customization options.

#### Signals that don't support complex attributes

**The OTel SDK SHOULD serialize complex attributes to JSON string if they are added
to metrics, resources, instrumentation scope, or used as identifying attributes on entities.**

The SDK MAY allow customization of this behavior, as described in the [Configuring
complex attribute handling](#allow-recording-structured-attributes) section.

#### Configuring complex attribute handling

The SDK MUST allow customization of how complex attributes are handled on a per-signal
basis via [attribute limits](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/common/README.md#attribute-limits).

Existing attribute value length limits SHOULD be applied to all leaf string nodes
in `AnyValue`. String values SHOULD be truncated to the configured limit.

Leaf nodes of an `AnyValue` attribute SHOULD count toward the attribute count limit.
If the limit is reached, the SDK MUST drop the entire `AnyValue` attribute;
partial exports are not allowed.

A new attribute limit property will be introduced to control whether and how complex
attributes are handled, with the following options:

- **allow**
  - Default for spans, logs, profiles, and descriptive entity attributes.
- **serialize to JSON string**
  - Default for metrics, resources, instrumentation scopes, and identifying entity attributes.
  - The SDK MUST support this option for all signals and SHOULD provide per-signal configuration.
- **drop**
  - SDKs MAY support this option

### Semantic conventions

Semantic conventions will be updated with the following guidance

- Standard attributes SHOULD be used whenever possible. Semantic conventions SHOULD
  assume that backends do not index individual properties of complex attributes,
  that querying or aggregating on such properties is inefficient and complicated,
  and that reporting complex attributes carries higher performance overhead.

- Complex attributes that are likely to be large (when serialized to a string) SHOULD
  be added as *opt-in* attributes. *Large* will be defined based on common backend
  attribute limits, typically around 4–16 KB.

- Complex attributes MUST NOT be used on metrics, resources, or as identifying attributes
  on entities.

## Trade-offs and mitigations

1. Allowing arbitrary objects as attributes is convenient but increases the risk of
   including large, sensitive, mutable, non-serializable, or otherwise problematic
   data in telemetry.

   It is RECOMMENDED to enforce `AnyValue` compatibility at the API level.
   Users and instrumentations SHOULD define custom `AnyValue`-compatible models
   to minimize misuse and reduce performance overhead.

   OTel SDKs MAY provide convenience methods to convert arbitrary objects to `AnyValue`.

   If such convenience is provided, it is RECOMMENDED to limit supported types
   to standard library lists, maps, named tuples, JSON objects, and similar structures.

   If the provided object has a property with an unrecognized type, it is RECOMMENDED
   to fall back to recording a string representation of the original complex object.
   This helps minimize the risk of unintentional use of complex attributes.

2. While it should be possible to record complex data in telemetry, many backends do not
   support it well — or at all — which can result in individual complex attributes
   or entire spans being dropped or rejected.

   In the future, support for complex attributes may be negotiated via OpAMP,
   allowing this behavior to be configured based on backend capabilities without
   requiring user intervention.

   In the meantime, we plan to mitigate this through:

   - Requiring an SDK mode that serializes complex attributes
   - A collector transformation processor that already can drop, flatten, serialize, or
     truncate complex attribute values using OTTL
   - Semantic conventions guidance that discourages their use

## Prior art and alternatives

TODO

## Open questions

TODO

## Future possibilities

We can consider a separate set of attribute limits specifically for complex values,
including a total size limit and ability to estimate `AnyValue` object size.