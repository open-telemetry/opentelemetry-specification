# Semantic conventions for Elasticsearch

**Status**: [Experimental](../../../document-status.md)

This document defines semantic conventions to apply when instrumenting requests to Elasticsearch. They map Elasticsearch
requests to attributes on a Span. It also describes the configuration options that may be proivded as part of the
instrumentation.

## Span Name

The **span name** SHOULD be of the format `<db.elasticsearch.method> <db.elasticsearch.url *with placeholders*>`.

The elasticsearch url is modified with placeholders in order to reduce the cardinality of the span name. When the url
contains a document id, it SHOULD be replaced by the identifier `{id}`. When the url contains a target data stream or
index, it SHOULD be replaced by `{target}`.
For example, a request to `/test-index/_doc/123` should have the span name `GET /{target}/_doc/{id}`. 
When there is no target or document id, the span name will contain the exact url, as in `POST /_search`.


## `db.statement` span attribute value and configuration options

### `db_statement` configuration option

The `db.statement` attribute MUST correspond to the request `body`, with sanitization. The implementation MUST have an
option to control how the `db.statement` is set in the span attribute, called `db_statement`.

The instrumentation MUST provide the following options for the `db_statement` configuration:
- `omit`: Do not include anything in the `db.statement` span attribute
- `sanitize`: Replace values at specific keys with `?`
- `raw`: Include the request `body` as-is

`sanitize` is the default. When the `sanitize` option is set, the values at the following keys are replaced by `?`:
- `password`
- `passwd`
- `pwd`
- `secret`
- `*key`
- `*token*`
- `*session*`
- `*credit*`
- `*card*`
- `*auth*`
- `set-cookie`

For example, given the request 
```ruby
client.index(
  index: 'users',
  id: '1',
  body: { name: 'Emily', password: 'top_secret' }
)
```

the `db.statement` span attribute would be set to the following, for each `db_statement` option:
- `omit`: `{ db.statement: '' }`
- `sanitize`: `{ db.statement: "{\"name\":\"Emily\",\"password\":\"?\"}" }`
- `raw`: `{ db.statement: "{\"name\":\"Emily\",\"password\":\"top_secret\"}" }`

### `sanitize_field_names` configuration option

The instrumentation MAY have an option `sanitize_field_names` that accepts a list of wildcard patterns to match 
keys against. The list provided by the user is concatenated to the default list. For example:

```ruby
config = { sanitize_field_names: ['abc*', '*xyz'] }
```

would result in `'abc*'`, `'*xyz'` being added to the list of sanitized keys mentioned above.

## Span attributes

<!-- semconv elasticsearch -->
| Attribute                  | Type | Description                                                                                          | Examples                                     | Requirement Level      |
|----------------------------|---|------------------------------------------------------------------------------------------------------|----------------------------------------------|------------------------|
| `db.elasticsearch.doc_id`  | string | The document that the request targets, specified in the path.                                        | `'123'`                                      | Conditionally Required |
| `db.elasticsearch.params`  | string | The query params of the request, as a json string.                                                   | `'"{\"q\":\"test\"}", "{\"refresh\":true}"'` | Conditionally Required |
| `db.elasticsearch.target`  | string | The name of the data stream or index that is targeted.                                               | `'users'`                                    | Conditionally Required |
| `db.elasticsearch.url`     | string | The url of the request, including the target and exact document id. | `'/test-index/_doc/123'`                     | Required |
| `db.elasticsearch.method`* | string | The HTTP method of the request. | `'GET'`                                       | Required |


*`db.elasticsearch.method` MUST be one of the following:

| Value    | Description         |
|----------|---------------------|
| `GET`    | HTTP GET request    |
| `POST`   | HTTP POST request   |
| `PUT`    | HTTP PUT request    |
| `DELETE` | HTTP DELETE request |
<!-- endsemconv -->
