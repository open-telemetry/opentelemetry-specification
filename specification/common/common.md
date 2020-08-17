# Common specification concepts

<details>
<summary>
Table of Contents
</summary>

- [Attributes](#attributes)
  - [Attribute Naming](#attribute-naming)
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

### Attribute Naming

Attribute name (also known as the "attribute key") MUST be a valid Unicode
sequence.

Attribute names SHOULD follow these rules:

- Use namespacing to avoid name clashes. Delimit the namespaces using a dot
  character. For example `service.version` denotes the service version where
  `service` is the namespace and `version` is an attribute in that namespace.

- Namespaces can be nested. For example `telemetry.sdk` is a namespace inside
  top-level `telemetry` namespace and `telemetry.sdk.name` is an attribute
  inside `telemetry.sdk` namespace.

- For each multi-word dot-delimited component of the attribute name separate the
  words by underscores (i.e. use snake_case). For example `http.status_code`
  denotes the status code in the http namespace.

- Attribute names SHOULD NOT coincide with namespaces. For example if
  `service.instance.id` is an attribute name then it is no longer valid to have
  an attribute named `service.instance` because `service.instance` is already a
  namespace. Because of this rule be careful when choosing attribute names:
  every existing attribute name prohibits existence of an equally named
  namespace in the future, and vice versa: any existing namespace prohibits
  existence of an equally named attribute in the future.

#### Recommendations for OpenTelemetry Authors

- All attribute names that are part of OpenTelemetry semantic conventions
  SHOULD be part of a namespace. 

- When coming up with a new convention make sure to check existing namespaces
  for
  [Resources](https://github.com/open-telemetry/opentelemetry-specification/tree/master/specification/resource/semantic_conventions),
  [Spans](https://github.com/open-telemetry/opentelemetry-specification/tree/master/specification/trace/semantic_conventions),
  and
  [Metrics](https://github.com/open-telemetry/opentelemetry-specification/tree/master/specification/metrics/semantic_conventions)
  to see if the new attributes fits.

- When a new namespace is necessary consider whether it should be a top-level
  namespace (e.g. `service`) or a nested namespace (e.g. `service.instance`).

- Semantic conventions MUST limit attribute names to printable Basic Latin
  characters (more precisely to
  [U+0021 .. U+007E](https://en.wikipedia.org/wiki/Basic_Latin_(Unicode_block)#Table_of_characters)
  subset of Unicode code points). It is recommended to further limit attribute
  names to the following Unicode code points: Latin alphabet, Numeric,
  Underscore, Dot (as namespace delimiter).

#### Recommendations for Application Developers

As an application developer when you need to record an attribute first consult
existing semantic conventions for
[Resources](https://github.com/open-telemetry/opentelemetry-specification/tree/master/specification/resource/semantic_conventions),
[Spans](https://github.com/open-telemetry/opentelemetry-specification/tree/master/specification/trace/semantic_conventions),
and
[Metrics](https://github.com/open-telemetry/opentelemetry-specification/tree/master/specification/metrics/semantic_conventions).
If appropriate attribute name does not exists you will need to come up with a
new name. To do that consider a few options:

- The attribute is specific to your company and may be possibly used outside the
  company as well. To avoid name clashes with attributes introduced by other
  companies (in a distributed system that uses applications from multiple
  vendors) it is recommended to prefix the attribute name by your company's
  reverse domain name, e.g. `com.acme.shopname`.

- The attribute is specific to your application that will be used internally
  only. If you already have an internal company process that helps you to ensure
  no name clashes happen then feel free to follow it. Otherwise it is
  recommended to prefix the attribute name by your application name, provided
  that the application name is reasonably unique within your organization (e.g.
  `myuniquemapapp.longitude` is likely fine). Make sure the application name
  does not clash with an existing semantic convention namespace.

- The attribute may be generally applicable to applications in the industry. In
  that case consider submitting a proposal to this specification to add a new
  attribute to the semantic conventions, if necessary also to add a new
  namespace for the attribute.

It is recommended to limit attribute names to printable Basic Latin characters
(more precisely to
[U+0021 .. U+007E](https://en.wikipedia.org/wiki/Basic_Latin_(Unicode_block)#Table_of_characters)
subset of Unicode code points).

