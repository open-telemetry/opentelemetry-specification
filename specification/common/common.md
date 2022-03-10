# Common specification concepts

**Status**: [Stable, Feature-freeze](../document-status.md)

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [Attribute](#attribute)
  * [Attribute Limits](#attribute-limits)
    + [Exempt Entities](#exempt-entities)
- [Attribute Collections](#attribute-collections)

<!-- tocstop -->

</details>

## Attribute

<a id="attributes"></a>

An `Attribute` is a key-value pair, which MUST have the following properties:

- The attribute key MUST be a non-`null` and non-empty string.
- The attribute value is either:
  - A primitive type: string, boolean, double precision floating point (IEEE 754-1985) or signed 64 bit integer.
  - An array of primitive type values. The array MUST be homogeneous,
    i.e., it MUST NOT contain values of different types.

For protocols that do not natively support non-string values, non-string values SHOULD be represented as JSON-encoded strings.  For example, the expression `int64(100)` will be encoded as `100`, `float64(1.5)` will be encoded as `1.5`, and an empty array of any type will be encoded as `[]`.

Attribute values expressing a numerical value of zero, an empty string, or an
empty array are considered meaningful and MUST be stored and passed on to
processors / exporters.

Attribute values of `null` are not valid and attempting to set a `null` value is
undefined behavior.

`null` values SHOULD NOT be allowed in arrays. However, if it is impossible to
make sure that no `null` values are accepted
(e.g. in languages that do not have appropriate compile-time type checking),
`null` values within arrays MUST be preserved as-is (i.e., passed on to span
processors / exporters as `null`). If exporters do not support exporting `null`
values, they MAY replace those values by 0, `false`, or empty strings.
This is required for map/dictionary structures represented as two arrays with
indices that are kept in sync (e.g., two attributes `header_keys` and `header_values`,
both containing an array of strings to represent a mapping
`header_keys[i] -> header_values[i]`).

See [Attribute Naming](attribute-naming.md) for naming guidelines.

### Attribute Limits

Execution of erroneous code can result in unintended attributes. If there are no
limits placed on attributes, they can quickly exhaust available memory, resulting
in crashes that are difficult to recover from safely.

By default an SDK SHOULD apply truncation as per the list of
[configurable parameters](#attribute-limits-configuration) below.

If an SDK provides a way to:

- set an attribute value length limit such that for each
  attribute value:
  - if it is a string, if it exceeds that limit (counting any character in it as
    1), SDKs MUST truncate that value, so that its length is at most equal
    to the limit,
  - if it is an array of strings, then apply the above rule to each of the
    values separately,
  - otherwise a value MUST NOT be truncated;
- set a limit of unique attribute keys such that:
  - for each unique attribute key, addition of which would result in exceeding
    the limit, SDK MUST discard that key/value pair.

There MAY be a log emitted to indicate to the user that an attribute was
truncated or discarded. To prevent excessive logging, the log MUST NOT be
emitted more than once per record on which an attribute is set.

If the SDK implements the limits above, it MUST provide a way to change these
limits programmatically. Names of the configuration options SHOULD be the same as
in the list below.

An SDK MAY implement model-specific limits, for example
`SpanAttributeCountLimit`. If both a general and a model-specific limit are
implemented, then the SDK MUST first attempt to use the model-specific limit, if
it isn't set, then the SDK MUST attempt to use the general limit. If neither are
defined, then the SDK MUST try to use the model-specific limit default value,
followed by the global limit default value.

<a name="attribute-limits-configuration"></a>
**Configurable parameters:**

* `AttributeCountLimit` (Default=128) - Maximum allowed attribute count per record;
* `AttributeValueLengthLimit` (Default=Infinity) - Maximum allowed attribute value length;

#### Exempt Entities

Resource attributes SHOULD be exempt from the limits described above as resources
are not susceptible to the scenarios (auto-instrumentation) that result in
excessive attributes count or size. Resources are also sent only once per batch
instead of per span so it is relatively cheaper to have more/larger attributes
on them. Resources are also immutable by design and they are generally passed
down to TracerProvider along with limits. This makes it awkward to implement
attribute limits for Resources.

Attributes, which belong to Metrics, are exempt from the limits described above
at this time, as discussed in
[Metrics Attribute Limits](../metrics/sdk.md#attribute-limits).

## Attribute Collections

[Resources](../resource/sdk.md), Metrics
[data points](../metrics/datamodel.md#metric-points),
[Spans](../trace/api.md#set-attributes), Span
[Events](../trace/api.md#add-events), Span
[Links](../trace/api.md#specifying-links) and
[Log Records](../logs/data-model.md) may contain a collection of attributes. The
keys in each such collection are unique, i.e. there MUST NOT exist more than one
key-value pair with the same key. The enforcement of uniqueness may be performed
in a variety of ways as it best fits the limitations of the particular
implementation.

Normally for the telemetry generated using OpenTelemetry SDKs the attribute
key-value pairs are set via an API that either accepts a single key-value pair
or a collection of key-value pairs. Setting an attribute with the same key as an
existing attribute SHOULD overwrite the existing attribute's value. See for
example Span's [SetAttribute](../trace/api.md#set-attributes) API.

A typical implementation of [SetAttribute](../trace/api.md#set-attributes) API
will enforce the uniqueness by overwriting any existing attribute values pending
to be exported, so that when the Span is eventually exported the exporters see
only unique attributes. The OTLP format in particular requires that exported
Resources, Spans, Metric data points and Log Records contain only unique
attributes.

Some other implementations may use a streaming approach where every
[SetAttribute](../trace/api.md#set-attributes) API call immediately results in
that individual attribute value being exported using a streaming wire protocol.
In such cases the enforcement of uniqueness will likely be the responsibility of
the recipient of this data.
