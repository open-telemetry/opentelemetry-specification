# Semantic conventions for GraphQL Server

**Status**: [Experimental](../../../document-status.md)

This document defines semantic conventions to apply when instrumenting the GraphQL Server. They map GraphQL queries to
attributes on a Span.

<!-- semconv graphql -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `graphql.operation.name` | string | The name of the operation being executed. | `findBookById` | No |
| `graphql.operation.type` | string | The type of the operation being executed. | `QUERY`; `MUTATION`; `SUBSCRIPTION` | No |
| `graphql.query` | string | The GraphQL query being executed. [1] | `query findBookById { bookById(id: ?) { name } }` | No |

**[1]:** The value may be sanitized to exclude sensitive information.
<!-- endsemconv -->
