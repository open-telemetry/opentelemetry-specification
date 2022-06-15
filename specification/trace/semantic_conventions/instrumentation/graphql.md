# Semantic conventions for GraphQL Server

**Status**: [Experimental](../../../document-status.md)

This document defines semantic conventions to apply when instrumenting the GraphQL implementation. They map GraphQL
operations to attributes on a Span.

The **span name** MUST be of the format `<graphql.operation.type> <graphql.operation.name>` provided that
`graphql.operation.type` and `graphql.operation.name` are available. If `graphql.operation.name` is not available, the
span SHOULD be named `<graphql.operation.type>`. When `<graphql.operation.type>` is not available, `GraphQL Operation`
MAY be used as span name.

<!-- semconv graphql -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `graphql.operation.name` | string | The name of the operation being executed. | `findBookById` | Recommended |
| `graphql.operation.type` | string | The type of the operation being executed. | `query`; `mutation`; `subscription` | Recommended |
| `graphql.document` | string | The GraphQL document being executed. [1] | `query findBookById { bookById(id: ?) { name } }` | Recommended |

**[1]:** The value may be sanitized to exclude sensitive information.

`graphql.operation.type` MUST be one of the following:

| Value  | Description |
|---|---|
| `query` | GraphQL query |
| `mutation` | GraphQL mutation |
| `subscription` | GraphQL subscription |
<!-- endsemconv -->
