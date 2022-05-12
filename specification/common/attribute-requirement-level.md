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
_Note: Consumers of telemetry can detect if telemetry item follows specific semantic convention by checking presence of a `Required` attribute defined by such convention. For example, `db.system` attribute on a span can be used as an indication that span follows database semantics._

- **Conditionally Required**. All instrumentations MUST add the attribute when given condition is satisfied. Semantic convention of a `Conditionally Required` level of an attribute MUST clarify the condition under which the attribute is expected to be populated.
`http.route` is an example of a conditionally required attribute to be populated when instrumented HTTP framework provides route information for the instrumented request. Some low-level HTTP server implementations do not support routing and corresponding instrumentations can't populate the attribute.

- **Recommended**. Instrumentations SHOULD add the attribute by default if it's readily available and can be [efficiently populated](#performance-suggestions). Instrumentation MAY offer a configuration option to disable recommended attributes.

- **Optional**. Instrumentation SHOULD populate the attribute if and only if user configures instrumentation to do so. Instrumentation that doesn't support configuration MUST NOT populate **Optional** attributes.

The requirement level for attribute is defined by semantic conventions depending on attribute availability across instrumented entities, performance, security, and other factors. When defining requirement levels, semantic conventions MUST take into account signal-specific requirements. For example, Metric attributes that may have high cardinality can only be defined with **Optional** level.

Semantic convention that refers to an attribute from another semantic convention MAY modify the requirement level within its own scope. Otherwise, requirement level from referred semantic convention applies.
For example, [Database semantic convention](../trace/semantic_conventions/database.md) references `net.transport` attribute defined in [General attributes](../trace/semantic_conventions/span-general.md) with `Conditionally Required` level on it.

Instrumentations that decide not to populate `Conditionally Required` or `Recommended` attributes due to [performance](#performance-suggestions), security, privacy, or other consideration by default, SHOULD use the **Optional** requirement level on them if the attributes are logically applicable.

## Performance suggestions

Here are several examples of expensive operations to be avoided by default:

- DNS lookup to populate `net.peer.name` if only IP address is available to the instrumentation.
- forcing `http.route` calculation before HTTP framework calculates it
- reading response stream to find `http.response_content_length` when `Content-Length` header is not available
