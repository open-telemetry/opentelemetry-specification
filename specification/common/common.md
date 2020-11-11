# Common specification concepts

<details>
<summary>
Table of Contents
</summary>

- [Attributes](#attributes)
  - [Attribute and Label Naming](#attribute-and-label-naming)
    - [Name Pluralization Guidelines](#name-pluralization-guidelines)
    - [Recommendations for OpenTelemetry Authors](#recommendations-for-opentelemetry-authors)
    - [Recommendations for Application Developers](#recommendations-for-application-developers)

</details>

## Attributes

Attributes are a list of zero or more key-value pairs. An `Attribute` MUST have the following properties:

- The attribute key, which MUST be a non-`null` and non-empty string.
- The attribute value, which is either:
  - A primitive type: string, boolean, double precision floating point (IEEE 754-1985) or signed 64 bit integer.
  - An array of primitive type values. The array MUST be homogeneous,
    i.e. it MUST NOT contain values of different types. For protocols that do
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
  Note: the fact that an entity is located within another entity is typically
  not a sufficient reason for forming nested namespaces. The purpose of a
  namespace is to avoid name clashes, not to indicate entity hierarchies. This
  purpose should primarily drive the decision about forming nested namespaces.

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
  
### Name Pluralization guidelines

- When an attribute represents a single entity, the attribute name SHOULD be singular.
  Examples: `host.name`, `db.user`, `container.id`.

- When attribute can represent multiple entities, the attribute name SHOULD be pluralized
  and the value type SHOULD be an array. E.g. `process.command_args` might include multiple
  values: the executable name and command arguments.

- When an attribute represents a measurement,
  [Metric Name Pluralization Guidelines](../metrics/semantic_conventions/README.md#pluralization)
  SHOULD be followed for the attribute name.

### Recommendations for OpenTelemetry Authors

- All names that are part of OpenTelemetry semantic conventions SHOULD be part
  of a namespace.

- When coming up with a new semantic convention make sure to check existing
  namespaces for
  [Resources](../resource/semantic_conventions/README.md),
  [Spans](../trace/semantic_conventions/README.md),
  and
  [Metrics](../metrics/semantic_conventions/README.md)
  to see if the new name fits.

- When a new namespace is necessary consider whether it should be a top-level
  namespace (e.g. `service`) or a nested namespace (e.g. `service.instance`).

- Semantic conventions exist for four areas: for Resource, Span and Log
  attribute names as well as Metric label keys. In addition, for spans we have
  two more areas: Event and Link attribute names. Identical namespaces or names
  in all these areas MUST have identical meanings. For example the `http.method`
  span attribute name denotes exactly the same concept as the `http.method`
  metric label, has the same data type and the same set of possible values (in
  both cases it records the value of the HTTP protocol's request method as a
  string).

- Semantic conventions MUST limit names to printable Basic Latin characters
  (more precisely to
  [U+0021 .. U+007E](https://en.wikipedia.org/wiki/Basic_Latin_(Unicode_block)#Table_of_characters)
  subset of Unicode code points). It is recommended to further limit names to
  the following Unicode code points: Latin alphabet, Numeric, Underscore, Dot
  (as namespace delimiter).

### Recommendations for Application Developers

As an application developer when you need to record an attribute or a label
first consult existing semantic conventions for
[Resources](../resource/semantic_conventions/README.md),
[Spans](../trace/semantic_conventions/README.md),
and
[Metrics](../metrics/semantic_conventions/README.md).
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
