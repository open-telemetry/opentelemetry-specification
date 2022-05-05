# Attribute Requirement Level

**Status**: [Experimental](../document-status.md)

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [Performance suggestions](#performance-suggestions)

<!-- tocstop -->

</details>

_This section applies to Log, and Metric, Resource, and Span describes requirement levels for attributes._

Following attribute requirement levels are specified:

- **Required**. All instrumentations MUST populate the attribute. Semantic convention defining required attribute expects that an absolute majority instrumentation libraries and applications are able to efficiently retrieve and populate it, can ensure cardinality, security, and other requirements specific to signal defined by the convention. `http.method` is an example of a required attribute.

- **Conditional**. All instrumentations SHOULD add the attribute when instrumented entity supports corresponding feature and the attribute value can be [efficiently retrieved and populated](#performance-suggestions). Semantic convention assigning `Conditional` level on an attribute, SHOULD clarify when attribute is expected to be populated.
`http.route` is an example of a conditional attribute: is widely supported by HTTP web frameworks, but some low-level HTTP server implementations do not support it.
_Note: For producers of telemetry `Required` and `Conditional` levels are semantically the same (under the assumption that `Required` attributes are always available). However, consumers may use this distinction to identify conventions or validate telemetry._
< TODO need a better name, took 'conditional' from schema definition>

- **Recommended**. Instrumentations SHOULD add the attribute by default if it's readily available and can be [efficiently populated](#performance-suggestions). Instrumentation MAY allow explicit configuration to disable recommended attributes.

- **Opt-in**. Instrumentations SHOULD NOT add the attribute by default. Instrumentation SHOULD populate the attribute if and only if user configures instrumentation to do so. Instrumentation that doesn't support configuration MUST NOT populate **Opt-in** attributes.

The requirement level for attribute is defined by semantic conventions depending on attribute availability across instrumented entities, performance, security, and other factors. When defining requirement levels, semantic conventions MUST take into account signal-specific requirements. For example, Metric attributes that may have high cardinality can only be defined with **Opt-in** level.

Semantic convention that refers to an attribute from another (e.g. general) semantic convention MAY modify the requirement level within its own scope. Otherwise, requirement level from referred semantic convention applies.

Instrumentations that decide not to populate `Conditional` or `Recommended` attributes due to performance, security, privacy, or other consideration by default, SHOULD use the **Opt-in** requirement level on them if the attributes are logically applicable.

## Performance suggestions

In some cases instrumented entities do not have `Conditional` or `Recommended` attribute value readily available and retrieval can be expensive. Instrumentations SHOULD NOT perform expensive resource-consuming operation to obtain attribute values. Corresponding attributes SHOULD NOT be populated by default.

Here are several examples of expensive operations:

- DNS lookup to populate `net.peer.name` if only IP address is available to the instrumentation.
- forcing `http.route` calculation before HTTP framework calculates it
- reading response stream to find `http.response_content_length` when `Content-Length` header is not available
