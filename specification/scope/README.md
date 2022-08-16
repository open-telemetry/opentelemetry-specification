# Scope Semantic Conventions

**Status**: [Experimental](../document-status.md)

This document defines standard attributes for the [instrumentation scope](../glossary.md#instrumentation-scope).

<!-- semconv scope -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `short_name` | string | The short name for the instrumentation scope, which should generally be less than 15 characters, and generally consist of a single word. It is not required to be globally unique, but should be unique enough to make it very unlikely to collide with other short names.  An example use is as the [namespace](https://github.com/OpenObservability/OpenMetrics/blob/main/specification/OpenMetrics.md#metric-naming-and-namespaces) (prefix) for OpenMetrics metric names. It is recommended for the short_name to be related to the name of the scope. | `mylibrary`; `otelmacaron` | Recommended |
<!-- endsemconv -->
