<!--- Hugo front matter used to generate the website version of this page:
linkTitle: Common concepts
aliases: [/docs/reference/specification/common/common]
path_base_for_github_subdir:
  from: tmp/otel/specification/common/_index.md
  to: common/README.md
--->

# Common specification concepts

**Status**: [Stable](../document-status.md), except where otherwise specified

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [AnyValue](#anyvalue)
  * [map](#mapstring-anyvalue)
  * [String representation of non-primitive value types](#string-representation-of-non-primitive-value-types)
    + [Byte Arrays](#byte-arrays)
    + [Empty Values](#empty-values)
    + [Arrays](#arrays)
    + [Maps](#maps)
- [Attribute](#attribute)
  * [Attribute Collections](#attribute-collections)
- [Attribute Limits](#attribute-limits)
  * [Configurable Parameters](#configurable-parameters)
  * [Exempt Entities](#exempt-entities)

<!-- tocstop -->

</details>

## AnyValue

`AnyValue` is either:

- a primitive type: string, boolean, double precision floating point
  (IEEE 754-1985), or signed 64 bit integer,
- a homogeneous array of primitive type values. A homogeneous array MUST NOT
  contain values of different types.
- a byte array.
- an array of `AnyValue`,
- a [`map<string, AnyValue>`](#mapstring-anyvalue),
- an empty value if supported by the language,
  (e.g. `null`, `undefined` in JavaScript/TypeScript, `None` in Python, `nil` in Go/Ruby, not supported in Erlang, etc.)

Arbitrary deep nesting of values for arrays and maps is allowed (essentially
allows to represent an equivalent of a JSON object).

APIs SHOULD be documented in a way to communicate to users that using array and
map values may carry higher performance overhead compared to primitive values.

AnyValues expressing an empty value, a numerical value of zero, an empty string,
or an empty array are considered meaningful and MUST be stored and passed on to
processors / exporters.

While `null` is a valid attribute value, its use within homogeneous arrays
SHOULD generally be avoided unless language constraints make this impossible.
However, if it is impossible to make sure that no `null` values are accepted
(e.g. in languages that do not have appropriate compile-time type checking),
`null` values within arrays MUST be preserved as-is (i.e., passed on to
processors / exporters as `null`). If exporters do not support exporting `null`
values, they MAY replace those values by 0, `false`, or empty strings.
This is required for map/dictionary structures represented as two arrays with
indices that are kept in sync (e.g., two attributes `header_keys` and `header_values`,
both containing an array of strings to represent a mapping
`header_keys[i] -> header_values[i]`).

### map<string, AnyValue>

`map<string, AnyValue>` is a map of string keys to `AnyValue` values.
The keys in the map are unique (duplicate keys are not allowed).

Case sensitivity of keys MUST be preserved.
Keys that differ in casing are treated as distinct keys.

The representation of the map is language-dependent.

The implementation MUST by default enforce that the exported maps contain only
unique keys. The enforcement of uniqueness may be performed
in a variety of ways as it best fits the limitations of the particular
implementation (e.g. by removing duplicates).

The implementation MAY have an option to allow exporting maps with duplicate keys
(e.g. for better performance).
If such option is provided, it MUST be documented that for many receivers,
handling of maps with duplicate keys is unpredictable and it is the users'
responsibility to ensure keys are not duplicate.

Maps are equal when they contain the same key-value pairs,
irrespective of the order in which those elements appear
(unordered collection equality).

### String representation of non-primitive value types

For protocols that do not natively support non-primitive value types,
those values SHOULD be represented as strings following the encoding rules below.

#### Byte Arrays

Byte arrays SHOULD be Base64-encoded. Standalone values appear unquoted; nested values
(within arrays or maps) are quoted as JSON strings.

Example when standalone: `aGVsbG8gd29ybGQ=`

Example when nested in arrays/maps: `"aGVsbG8gd29ybGQ="`

#### Empty Values

Empty values SHOULD be represented as an empty string when standalone,
or as JSON null when nested in arrays or maps.

Example when standalone: empty string (no content)

Example when nested in arrays/maps: `null`

#### Arrays

Arrays SHOULD be represented as JSON arrays.

Examples: `[]`, `[1, "a", true, {"nested": "aGVsbG8gd29ybGQ="}]`

#### Maps

Maps SHOULD be represented as JSON objects.

Examples: `{}`, `{"a": "1", "b": 2, "c": [3, null]}`

## Attribute

<a id="attributes"></a>

An `Attribute` is a key-value pair, which MUST have the following properties:

- The attribute key MUST be a non-`null` and non-empty string.
  - Case sensitivity of keys is preserved. Keys that differ in casing are treated as distinct keys.
- The attribute value MUST be one of types defined in [AnyValue](#anyvalue).

Attributes are equal when their keys and values are equal.

See [Attribute Naming](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/general/naming.md#attributes) for naming guidelines.

See [Requirement Level](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/general/attribute-requirement-level.md) for requirement levels guidelines.

See [this document](attribute-type-mapping.md) to find out how to map values obtained
outside OpenTelemetry into OpenTelemetry attribute values.

### Attribute Collections

[Resources](../resource/sdk.md),
[Instrumentation Scopes](instrumentation-scope.md),
[Metric points](../metrics/data-model.md#metric-points),
[Spans](../trace/api.md#set-attributes), Span
[Events](../trace/api.md#add-events), Span
[Links](../trace/api.md#link) and
[Log Records](../logs/data-model.md),
contain a collection of attributes.

Attribute Collections are top-level collections of key-value pairs used in
OpenTelemetry data models.
Note that they are distinct from [`map<string, AnyValue>`](#mapstring-anyvalue),
which is a type of [`AnyValue`](#anyvalue) used to represent nested data
structures e.g. in attribute values and [log record body](../logs/data-model.md#field-body).

Implementation MUST by default enforce that the exported attribute collections
contain only unique keys. The enforcement of uniqueness may be performed
in a variety of ways as it best fits the limitations of the particular
implementation (e.g. by removing duplicates).

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

Implementations MAY have an option to allow exporting attribute collections
with duplicate keys (e.g. for better performance).
If such option is provided, it MUST be documented that for many receivers,
handling of maps with duplicate keys is unpredictable and it is the users'
responsibility to ensure keys are not duplicate.

Collection of attributes are equal when they contain the same attributes,
irrespective of the order in which those elements appear
(unordered collection equality).

## Attribute Limits

Execution of erroneous code can result in unintended attributes. If there are no
limits placed on attribute collections, they can quickly exhaust available memory,
resulting in crashes that are difficult to recover from safely.

By default an SDK SHOULD apply truncation as per the list of
[configurable parameters](#configurable-parameters) below.

If an SDK provides a way to:

- set an attribute value length limit such that for each
  attribute value:
  - if it is a string, if it exceeds that limit (counting any character in it as
    1), SDKs MUST truncate that value, so that its length is at most equal
    to the limit,
  - if it is a byte array,
    if its length exceeds that limit (counting each byte as 1),
    SDKs MUST truncate that value, so that its length is at most equal to the limit,
  - if it is an array of strings, then apply the limit to
    each value within the array separately,
  - if it is an array of [AnyValue](#anyvalue),
    then apply the limit to each element of the array separately (and recursively),
  - if it is a [map](#mapstring-anyvalue),
    then apply the limit to each value within the map separately (and recursively),
  - otherwise a value MUST NOT be truncated;
- set an attribute count limit such that:
  - if adding an attribute to an attribute collection would result
    in exceeding the limit (counting each attribute in the collection as 1),
    the SDK MUST discard that attribute, so that the total number of attributes in
    an attribute collection is at most equal to the limit;
  - the count limit applies only to top-level attributes, not to nested key-value
    pairs within [maps](#mapstring-anyvalue);
  - otherwise an attribute MUST NOT be discarded.

There MAY be a log emitted to indicate to the user that an attribute was
truncated or discarded. To prevent excessive logging, the log MUST NOT be
emitted more than once per record on which an attribute is set.

If the SDK implements the limits above, it MUST provide a way to change these
limits programmatically. Names of the configuration options SHOULD be the same as
in the list below.

An SDK MAY implement model-specific limits, for example
`SpanAttributeCountLimit` or `LogRecordAttributeCountLimit`. If both a general
and a model-specific limit are implemented, then the SDK MUST first attempt to
use the model-specific limit, if it isn't set, then the SDK MUST attempt to use
the general limit. If neither are defined, then the SDK MUST try to use the
model-specific limit default value, followed by the global limit default value.

Note that the limits apply only to attribute collections.
Therefore, they do not apply to values within other data structures such as
[`LogRecord.Body`](../logs/data-model.md#field-body).

### Configurable Parameters

* `AttributeCountLimit` (Default=128) - Maximum allowed attribute count per record;
* `AttributeValueLengthLimit` (Default=Infinity) - Maximum allowed attribute value length (applies to string values and byte arrays);

### Exempt Entities

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
