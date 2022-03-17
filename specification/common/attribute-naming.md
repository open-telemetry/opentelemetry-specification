# Attribute Naming

**Status**: [Experimental](../document-status.md)

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [Name Pluralization guidelines](#name-pluralization-guidelines)
- [Name Reuse Prohibition](#name-reuse-prohibition)
- [Recommendations for OpenTelemetry Authors](#recommendations-for-opentelemetry-authors)
- [Recommendations for Application Developers](#recommendations-for-application-developers)
- [otel.* Namespace](#otel-namespace)

<!-- tocstop -->

</details>

_This section applies to Resource, Span, Log, and Metric attribute names (also
known as the "attribute keys"). For brevity within this section when we use the
term "name" without an adjective it is implied to mean "attribute name"._

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
  attribute key in the future.

## Name Pluralization guidelines

- When an attribute represents a single entity, the attribute name SHOULD be singular.
  Examples: `host.name`, `db.user`, `container.id`.

- When attribute can represent multiple entities, the attribute name SHOULD be pluralized
  and the value type SHOULD be an array. E.g. `process.command_args` might include multiple
  values: the executable name and command arguments.

- When an attribute represents a measurement,
  [Metric Name Pluralization Guidelines](../metrics/semantic_conventions/README.md#pluralization)
  SHOULD be followed for the attribute name.

## Name Reuse Prohibition

A new attribute MUST NOT be added with the same name as an attribute that
existed in the past but was renamed (with a corresponding schema file).

When introducing a new attribute name check all existing schema files to make
sure the name does not appear as a key of any "rename_attributes" section (keys
denote old attribute names in rename operations).

## Recommendations for OpenTelemetry Authors

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

- Semantic conventions exist for four areas: for Resource, Span, Log, and Metric
  attribute names. In addition, for spans we have two more areas: Event and Link
  attribute names. Identical namespaces or names in all these areas MUST have
  identical meanings. For example the `http.method` span attribute name denotes
  exactly the same concept as the `http.method` metric attribute, has the same
  data type and the same set of possible values (in both cases it records the
  value of the HTTP protocol's request method as a string).

- Semantic conventions MUST limit names to printable Basic Latin characters
  (more precisely to
  [U+0021 .. U+007E](https://en.wikipedia.org/wiki/Basic_Latin_(Unicode_block)#Table_of_characters)
  subset of Unicode code points). It is recommended to further limit names to
  the following Unicode code points: Latin alphabet, Numeric, Underscore, Dot
  (as namespace delimiter).

## Recommendations for Application Developers

As an application developer when you need to record an attribute first consult
existing semantic conventions for
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
  prefix the attribute name by your application name, provided that
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

## otel.* Namespace

Attribute names that start with `otel.` are reserved to be defined by
OpenTelemetry specification. These are typically used to express OpenTelemetry
concepts in formats that don't have a corresponding concept.

For example, the `otel.scope.name` attribute is used to record the
instrumentation scope name, which is an OpenTelemetry concept that is natively
represented in OTLP, but does not have an equivalent in other telemetry formats
and protocols.

Any additions to the `otel.*` namespace MUST be approved as part of
OpenTelemetry specification.
