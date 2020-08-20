# Common specification concepts

<details>
<summary>
Table of Contents
</summary>

- [Attributes](#attributes)
  - [Attribute and Label Naming](#attribute-and-label-naming)

</details>

## Attributes

Attributes are a list of zero or more key-value pairs. An `Attribute` MUST have the following properties:

- The attribute key, which MUST be a non-`null` and non-empty string.
- The attribute value, which is either:
  - A primitive type: string, boolean, double precision floating point (IEEE 754-1985) or signed 64 bit integer.
  - An array of primitive type values. The array MUST be homogeneous,
    i.e. it MUST NOT contain values of different types. For protocols that do
    not natively support array values such values SHOULD be represented as JSON strings.

Attributes SHOULD preserve the order in which they're set.

Attribute values expressing a numerical value of zero, an empty string, or an
empty array are considered meaningful and MUST be stored and passed on to
processors / exporters. Attribute values of `null` are considered to be not set
and get discarded as if that `Attribute` has never been created.
As an exception to this, if overwriting of values is supported, this results in
removing the attribute.

`null` values within arrays MUST be preserved as-is (i.e., passed on to span
processors / exporters as `null`). If exporters do not support exporting `null`
values, they MAY replace those values by 0, `false`, or empty strings.
This is required for map/dictionary structures represented as two arrays with
indices that are kept in sync (e.g., two attributes `header_keys` and `header_values`,
both containing an array of strings to represent a mapping
`header_keys[i] -> header_values[i]`).

## Attribute and Label Naming

_This section applies to Resource, Span and Log attribute names (also known as
the "attribute keys") and to keys of Metric labels. For brevity within this
section when we use the term "name" without an adjective it is implied to mean
"attribute name or metric label key"._

Every name MUST be a valid Unicode sequence.

_Note: we merely require that the names are represented as Unicode sequences.
This specification does not define how exactly the Unicode sequences are
encoded. The encoding can vary from one programming language to another and from
one wire format to another. Use the idiomatic way to represent Unicode in the
particular programming language or wire format._

Names SHOULD follow these rules:

- Use namespacing to avoid name clashes. Delimit the namespaces using a dot
  character. For example `service.version` denotes the service version where
  `service` is the namespace and `version` is an attribute in that namespace.

- Namespaces can be nested. For example `telemetry.sdk` is a namespace inside
  top-level `telemetry` namespace and `telemetry.sdk.name` is an attribute
  inside `telemetry.sdk` namespace.

- For each multi-word dot-delimited component of the attribute name separate the
  words by underscores (i.e. use snake_case). For example `http.status_code`
  denotes the status code in the http namespace.

- Names SHOULD NOT coincide with namespaces. For example if
  `service.instance.id` is an attribute name then it is no longer valid to have
  an attribute named `service.instance` because `service.instance` is already a
  namespace. Because of this rule be careful when choosing names: every existing
  name prohibits existence of an equally named namespace in the future, and vice
  versa: any existing namespace prohibits existence of an equally named
  attribute or label key in the future.

### Recommendations for OpenTelemetry Authors

- All names that are part of OpenTelemetry semantic conventions SHOULD be part
  of a namespace.

- When coming up with a new semantic convention make sure to check existing
  namespaces for
  [Resources](https://github.com/open-telemetry/opentelemetry-specification/tree/master/specification/resource/semantic_conventions),
  [Spans](https://github.com/open-telemetry/opentelemetry-specification/tree/master/specification/trace/semantic_conventions),
  and
  [Metrics](https://github.com/open-telemetry/opentelemetry-specification/tree/master/specification/metrics/semantic_conventions)
  to see if the new name fits.

- When a new namespace is necessary consider whether it should be a top-level
  namespace (e.g. `service`) or a nested namespace (e.g. `service.instance`).

- Semantic conventions MUST limit names to printable Basic Latin characters
  (more precisely to
  [U+0021 .. U+007E](https://en.wikipedia.org/wiki/Basic_Latin_(Unicode_block)#Table_of_characters)
  subset of Unicode code points). It is recommended to further limit names to
  the following Unicode code points: Latin alphabet, Numeric, Underscore, Dot
  (as namespace delimiter).

### Recommendations for Application Developers

As an application developer when you need to record an attribute or a label
first consult existing semantic conventions for
[Resources](https://github.com/open-telemetry/opentelemetry-specification/tree/master/specification/resource/semantic_conventions),
[Spans](https://github.com/open-telemetry/opentelemetry-specification/tree/master/specification/trace/semantic_conventions),
and
[Metrics](https://github.com/open-telemetry/opentelemetry-specification/tree/master/specification/metrics/semantic_conventions).
If an appropriate name does not exists you will need to come up with a new name.
To do that consider a few options:

- The name is specific to your company and may be possibly used outside the
  company as well. To avoid clashes with names introduced by other companies (in
  a distributed system that uses applications from multiple vendors) it is
  recommended to prefix the new name by your company's reverse domain name, e.g.
  `com.acme.shopname`.

- The name is specific to your application that will be used internally only. If
  you already have an internal company process that helps you to ensure no name
  clashes happen then feel free to follow it. Otherwise it is recommended to
  prefix the attribute name or label key by your application name, provided that
  the application name is reasonably unique within your organization (e.g.
  `myuniquemapapp.longitude` is likely fine). Make sure the application name
  does not clash with an existing semantic convention namespace.

- The name may be generally applicable to applications in the industry. In that
  case consider submitting a proposal to this specification to add a new name to
  the semantic conventions, and if necessary also to add a new namespace.

It is recommended to limit names to printable Basic Latin characters
(more precisely to
[U+0021 .. U+007E](https://en.wikipedia.org/wiki/Basic_Latin_(Unicode_block)#Table_of_characters)
subset of Unicode code points).
