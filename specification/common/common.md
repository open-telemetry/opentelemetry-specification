# Common specification concepts

**Status**: [Stable, Feature-freeze](../document-status.md)

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [Attribute](#attribute)
  * [Attribute Limits](#attribute-limits)
    + [Exempt Entities](#exempt-entities)

<!-- tocstop -->

</details>

## Attribute

<a id="attributes"></a>

An `Attribute` is a key-value pair, which MUST have the following properties:

- The attribute key MUST be a non-`null` and non-empty string.
- The attribute value is either:
  - A primitive type: string, boolean, double precision floating point (IEEE 754-1985) or signed 64 bit integer.
  - An array of primitive type values. The array MUST be homogeneous,
    i.e., it MUST NOT contain values of different types. For protocols that do
    not natively support array values such values SHOULD be represented as JSON strings.

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
