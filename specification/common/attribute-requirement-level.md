# Attribute Requirement Level

**Status**: [Experimental](../document-status.md)

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [Performance considerations](#performance-considerations)

<!-- tocstop -->

</details>

_This section applies to Resource, Span, Log, and Metric and describes requirement levels for attributes._

Following attribute requirement levels are specified:

- **Required**. All instrumentations MUST populate the attribute. Semantic convention defining required attribute expects that an absolute majority instrumentation libraries and applications are able to efficiently retrieve and populate it, can ensure cardinality, security, and other requirements specific to signal defined by the convention. `http.method` is an example of required attribute.

- **Conditional**. All instrumentations MUST add the attribute when instrumented entity supports corresponding feature and the attribute value can be efficiently retrieved and populated (see [Performance Considerations](#performance-considerations)).
For example, `http.route` is widely supported by HTTP web frameworks, but some low-level HTTP server implementations do not support it.
_Note: For producers of telemetry `Required` and `Conditional` levels are semantically the same (under the assumption that `Required` attributes are always available). However, consumers may use this distinction to identify conventions or validate telemetry._
< TODO need a better name, took 'conditional' from schema definition>

- **Recommended**. Instrumentations SHOULD add the attribute by default if it's readily available and can be efficiently populated. Instrumentation MAY allow explicit configuration to disable recommended attributes.

- **Opt-in**. Instrumentations SHOULD NOT add the attribute by default. Instrumentation SHOULD populate the attribute if and only if user configures instrumentation to do so. Instrumentation that doesn't support configuration MUST NOT populate **Opt-in** attributes.

The requirement level for attribute is defined by semantic conventions depending on attribute availability across instrumented entities, performance, security, and other factors. When defining requirement levels, semantic conventions MUST take into account signal-specific requirements. For example, Metric attributes that may have high cardinality can only be defined with **Opt-in** level.

Semantic convention that refers to attribute from another (e.g. general) semantic convention defaults to initial requirement level and MAY modify the requirement level in scope of a child convention.

Instrumentation that cannot populate attribute according to defined requirement level due to performance, security, privacy, or other consideration, MUST use **Opt-in** requirement level on it.

## Performance considerations

In some cases instrumented entities do not have attribute value readily available and retrieval can be expensive. For example, `net.peer.name` may require DNS lookup if only IP address is available to the instrumentation.

Instrumentations MUST NOT perform expensive resource-consuming operation to obtain attribute values. Corresponding attributes MUST NOT be populated by default.

Basic local operations such as string formatting, escaping or arithmetic operations are allowed.
