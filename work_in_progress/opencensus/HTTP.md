# HTTP Trace

This document explains tracing of HTTP requests with OpenCensus.

## Spans

Implementations MUST create a span for outgoing requests at the client and a span for incoming
requests at the server.

Span name is formatted as:

* /$path for outgoing requests.
* /($path|$route) for incoming requests.

If route cannot be determined, path is used to name the the span for outgoing requests.

Port MUST be omitted if it is 80 or 443.

Examples of span names:

* /users
* /messages/[:id]
* /users/25f4c31d

Outgoing requests should be a span kind of CLIENT and
incoming requests should be a span kind of SERVER.

## Propagation

Propagation is how SpanContext is transmitted on the wire in an HTTP request.

Implementations MUST allow users to set their own propagation format and MUST provide an
implementation for [B3](https://github.com/openzipkin/b3-propagation/blob/master/README.md#http-encodings)
and [TraceContext](https://w3c.github.io/trace-context/) at least.

If user doesn't set any propagation methods explicitly, TraceContext is used.

> In a previous version of this spec, we recommended that B3 be the default. For backwards compatibility,
implementations may provide a way for users to "opt in" to the new default explicitly, to
avoid a silent change to defaults that could break existing deployments.

The propagation method SHOULD modify a request object to insert a SpanContext or SHOULD be able
to extract a SpanContext from a request object.

## Status

Implementations MUST set status if HTTP request or response is not successful (e.g. not 2xx). In
redirection case, if the client doesn't have autoredirection support, request should be
considered successful.

Set status code to UNKNOWN (2) if the reason cannot be inferred at the callsite or from the HTTP
status code.

Don't set the status message if the reason can be inferred at the callsite of from the HTTP
status code.

### Mapping from HTTP status codes to Trace status codes

| HTTP code             | Trace status code      |
|-----------------------|------------------------|
| 0...199               | 2 (UNKNOWN)            |
| 200...399             | 0 (OK)                 |
| 400 Bad Request       | 3 (INVALID_ARGUMENT)   |
| 504 Gateway Timeout   | 4 (DEADLINE_EXCEEDED)  |
| 404 Not Found         | 5 (NOT_FOUND)          |
| 403 Forbidden         | 7 (PERMISSION_DENIED)  |
| 401 Unauthorized*     | 16 (UNAUTHENTICATED)   |
| 429 Too Many Requests | 8 (RESOURCE_EXHAUSTED) |
| 501 Not Implemented   | 12 (UNIMPLEMENTED)     |
| 503 Unavailable       | 14 (UNAVAILABLE)       |

Notes: 401 Unauthorized actually means unauthenticated according to RFC 7235, 3.1.

The Status message should be the Reason-Phrase (RFC 2616 6.1.1) from the
response status line (if available).

### Client errors for client HTTP calls

There are a number of client errors when trying to access http endpoint. Here
are examples of mapping those to the OpenCensus status codes.

| Client error                 | Trace status code     |
|------------------------------|-----------------------|
| DNS resolution failed        | 2 (UNKNOWN)           |
| Request cancelled by caller  | 1 (CANCELLED)         |
| URL cannot be parsed         | 3 (INVALID_ARGUMENT)  |
| Request timed out            | 1 (DEADLINE_EXCEEDED) |

## Message events

In the lifetime of an incoming and outgoing request, the following message events SHOULD be created:

* A message event for the request body size if/when determined.
* A message event for the response size if/when determined.

Implementations SHOULD create message event when body size is determined.

```
-> [time], MessageEventTypeSent, UncompressedByteSize, CompressedByteSize
```

Implementations SHOULD create message event when response size is determined.

```
-> [time], MessageEventTypeRecv, UncompressedByteSize, CompressedByteSize
```

## Attributes

Implementations SHOULD set the following attributes on the client and server spans. For a server,
request represents the incoming request. For a client, request represents the outgoing request.

All attributes are optional, but collector should make the best effort to
collect those.

> Work in progress! Please note, that the list below only contains attributes that aren't contained in the [OpenTelemetry main spec](../semantic-conventions.md) (yet):

| Attribute name            | Description                 | Type   |Example value              |
|---------------------------|-----------------------------|--------|---------------------------|
| "http.host"               | Request URL host            | string | `example.com:779`         |
| "http.path"               | Request URL path. If empty - set to `/` | `/users/25f4c31d`  |
| "http.user_agent"         | Request user-agent. Do not inject attribute if user-agent is empty. | string | `HTTPClient/1.2` |               |


Exporters should always export the collected attributes. Exporters should map the collected
attributes to backend's known attributes/labels.

The following table summarizes how OpenCensus attributes maps to the
known attributes/labels on supported tracing backends.

| OpenCensus attribute      | Zipkin             | Jaeger             | Stackdriver Trace label   |
|---------------------------|--------------------|--------------------|---------------------------|
| "http.host"               | "http.host"        | "http.host"        | "/http/host"              |
| "http.method"             | "http.method"      | "http.method"      | "/http/method"            |
| "http.path"               | "http.path"        | "http.path"        | "/http/path"              |
| "http.route"              | "http.route"       | "http.route"       | "/http/route"             |
| "http.user_agent"         | "http.user_agent"  | "http.user_agent"  | "/http/user_agent"        |
| "http.status_code"        | "http.status_code" | "http.status_code" | "/http/status_code"       |
| "http.url"                | "http.url"         | "http.url"         | "/http/url"               |

References:

- [Stackdriver Trace
  label](https://cloud.google.com/trace/docs/reference/v1/rest/v1/projects.traces)
- [Jaeger/Open Tracing](https://github.com/opentracing/specification/blob/master/semantic_conventions.md)
- [Zipkin](https://github.com/openzipkin/zipkin-api/blob/master/thrift/zipkinCore.thrift)

## Test Cases

Test cases for outgoing http calls are in the file
[http-out-test-cases.json](http-out-test-cases.json).

File consists of a set of test cases. Each test case represents outgoing http
call, response it receives and the resulting span properties. It looks like
this:

``` json
{
"name": "Name is populated as a path",
"method": "GET",
"url": "http://{host}:{port}/path/to/resource/",
"headers": {
    "User-Agent": "test-user-agent"
},
"responseCode": 200,
"spanName": "/path/to/resource/",
"spanStatus": "OK",
"spanKind": "Client",
"spanAttributes": {
    "http.path": "/path/to/resource/",
    "http.method": "GET",
    "http.host": "{host}:{port}",
    "http.status_code": "200",
    "http.user_agent": "test-user-agent"
}
}
```

Where `name` is the name of the test case. Properties `method`, `url` and
`headers` collection represents the outgoing call. The field `responseCode`
describes the response status code.

The rest of the properties describe the span details of the resulting span -
it's name, kind, status and attributes.

## Sampling

There are two ways to control the `Sampler` used:
* Controlling the global default `Sampler` via [TraceConfig](https://github.com/census-instrumentation/opencensus-specs/blob/master/trace/TraceConfig.md).
* Pass a specific `Sampler` as an option to the HTTP plugin. Plugins should support setting
a sampler per HTTP request.

Example cases where per-request sampling is useful:

- Having different sampling policy per route
- Having different sampling policy per method
- Filtering out certain paths (e.g. health endpoints) to disable tracing
- Always sampling critical paths
- Sampling based on the custom request header or query parameter

In the following Go example, incoming and outgoing request objects can
dynamically inspected to set a sampler.

For outgoing requests:

```go
type Transport struct {
 	// GetStartOptions allows to set start options per request.
	GetStartOptions func(*http.Request) trace.StartOptions

	// ...
}
```

For incoming requests:

```go
type Handler struct {
 	// GetStartOptions allows to set start options per request.
	GetStartOptions func(*http.Request) trace.StartOptions

	// ...
}
```