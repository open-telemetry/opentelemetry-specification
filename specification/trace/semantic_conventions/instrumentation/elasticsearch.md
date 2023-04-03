# Semantic conventions for Elasticsearch

**Status**: [Experimental](../../../document-status.md)

This document defines semantic conventions to apply when instrumenting requests to Elasticsearch. They map Elasticsearch
requests to attributes on a Span. It also describes the configuration options that may be proivded as part of the
instrumentation.

### Span Name

The **span name** SHOULD be of the format `<db.elasticsearch.method> <db.elasticsearch.url *with placeholders*>`.

The elasticsearch url is modified with placeholders in order to reduce the cardinality of the span name. When the url
contains a document id, it SHOULD be replaced by the identifier `{id}`. When the url contains a target data stream or
index, it SHOULD be replaced by `{target}`.
For example, a request to `/test-index/_doc/123` should have the span name `GET /{target}/_doc/{id}`. 
When there is no target or document id, the span name will contain the exact url, as in `POST /_search`.

### Span attributes

<!-- semconv elasticsearch -->
| Attribute                 | Type | Description                                                         | Examples                                                | Requirement Level      |
|---------------------------|---|---------------------------------------------------------------------|---------------------------------------------------------|------------------------|
| `db.elasticsearch.doc_id` | string | The document that the request targets, specified in the path.       | `'123'`                                                 | Conditionally Required |
| `db.elasticsearch.params` | string | The query params of the request, as a json string.                  | `'"{\"q\":\"test\"}", "{\"refresh\":true}"'`            | Conditionally Required |
| `db.elasticsearch.target` | string | The name of the data stream or index that is targeted.              | `'users'`                                               | Conditionally Required |
| `db.elasticsearch.url`    | string | The exact url of the request, including the target and document id. | `'/test-index/_doc/123'`                                | Required               |
| `db.elasticsearch.method` | string | The HTTP method of the request.                                     | `'GET'`                                                 | Required               |
| `db.statement`            | string | The request body, as a json string. [1]                             | `"{\"name\":\"TestUser\",\"password\":\"top_secret\"}"` | Conditionally Required |

**[1]:** The value may be sanitized to exclude sensitive information.
<!-- endsemconv -->
