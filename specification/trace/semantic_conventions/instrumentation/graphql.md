# Semantic conventions for GraphQL Server

**Status**: [Experimental](../../../document-status.md)

This document defines semantic conventions to apply when instrumenting the GraphQL Server. They map GraphQL operations
to attributes on a Span.

**Span kind:** MUST always be `INTERNAL`.

The **span name** MUST be of the format `<graphql.operation.type> <graphql.operation.name>` provided that
`graphql.operation.type` and `graphql.operation.name` are available. If `graphql.operation.name` is not available, the
span SHOULD be named `<graphql.operation.type>`. When `<graphql.operation.type>` is not available, `GraphQL Operation`
MAY be used as span name.

<!-- semconv graphql -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `graphql.operation.name` | string | The name of the operation being executed. | `findBookById` | No |
| `graphql.operation.type` | string | The type of the operation being executed. | `QUERY`; `MUTATION`; `SUBSCRIPTION` | No |
| `graphql.operation.body` | string | The GraphQL query being executed. [1] | `query findBookById { bookById(id: ?) { name } }` | No |

**[1]:** The value may be sanitized to exclude sensitive information.
<!-- endsemconv -->
