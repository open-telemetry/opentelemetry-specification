# OTLP: JSON Encoding for OTLP/HTTP

This is a proposal to add HTTP Transport extension supporting JSON serialization for
[OTLP](0035-opentelemetry-protocol.md) (OpenTelemetry Protocol).

## Table of Contents

* [Motivation](#motivation)
* [OTLP/HTTP+JSON Protocol Details](#otlphttpjson-protocol-details)
  * [JSON Mapping](#json-mapping)
  * [Request](#request)
  * [Response](#response)
    * [Success](#success)
    * [Failures](#failures)
    * [Throttling](#throttling)
    * [All Other Responses](#all-other-responses)
  * [Connection](#connection)
  * [Parallel Connections](#parallel-connections)

## Motivation

Protobuf is a relatively big dependency, which some clients are not willing to take. For example, WebJS, iOS/Android (in some scenarios, the size of the installation package is limited, do not want to introduce protobuf dependencies). Plain JSON is a smaller dependency and is built in the standard libraries of many programming languages.

## OTLP/HTTP+JSON Protocol Details

OTLP/HTTP+JSON will be consistent with the [OTLP/HTTP](0099-otlp-http.md) specification except that the payload will use JSON instead of protobuf.

### JSON Mapping

Use proto3 standard defined [JSON Mapping](https://protobuf.dev/programming-guides/proto3/#json) for mapping between protobuf and JSON. `trace_id`  and `span_id` is base64 encoded in OTLP/HTTP+JSON, not hex.

### Request

Telemetry data is sent via HTTP POST request.

The default URL path for requests that carry trace data is `/v1/traces` (for
example the full URL when connecting to "example.com" server will be
`https://example.com/v1/traces`). The request body is a JSON-encoded
[`ExportTraceServiceRequest`](https://github.com/open-telemetry/opentelemetry-proto/blob/e6c3c4a74d57f870a0d781bada02cb2b2c497d14/opentelemetry/proto/collector/trace/v1/trace_service.proto#L38)
message.

The default URL path for requests that carry metric data is `/v1/metrics` and the
request body is a JSON-encoded
[`ExportMetricsServiceRequest`](https://github.com/open-telemetry/opentelemetry-proto/blob/e6c3c4a74d57f870a0d781bada02cb2b2c497d14/opentelemetry/proto/collector/metrics/v1/metrics_service.proto#L35)
message.

The client MUST set "Content-Type: application/json" request header. The
client MAY gzip the content and in that case SHOULD include "Content-Encoding:
gzip" request header. The client MAY include "Accept-Encoding: gzip" request
header if it can receive gzip-encoded responses.

Non-default URL paths for requests MAY be configured on the client and server
sides.

### Response

#### Success

On success the server MUST respond with `HTTP 200 OK`. Response body MUST be
JSON-encoded
[`ExportTraceServiceResponse`](https://github.com/open-telemetry/opentelemetry-proto/blob/e6c3c4a74d57f870a0d781bada02cb2b2c497d14/opentelemetry/proto/collector/trace/v1/trace_service.proto#L47)
message for traces and
[`ExportMetricsServiceResponse`](https://github.com/open-telemetry/opentelemetry-proto/blob/e6c3c4a74d57f870a0d781bada02cb2b2c497d14/opentelemetry/proto/collector/metrics/v1/metrics_service.proto#L44)
message for metrics.

The server MUST set "Content-Type: application/json" response header. If
the request header "Accept-Encoding: gzip" is present in the request the server
MAY gzip-encode the response and set "Content-Encoding: gzip" response header.

The server SHOULD respond with success no sooner than after successfully
decoding and validating the request.

#### Failures

If the processing of the request fails the server MUST respond with appropriate
`HTTP 4xx` or `HTTP 5xx` status code. See sections below for more details about
specific failure cases and HTTP status codes that should be used.

Response body for all `HTTP 4xx` and `HTTP 5xx` responses MUST be a
JSON-encoded
[Status](https://pkg.go.dev/google.golang.org/genproto/googleapis/rpc/status#Status)
message that describes the problem.

This specification does not use `Status.code` field and the server MAY omit
`Status.code` field. The clients are not expected to alter their behavior based
on `Status.code` field but MAY record it for troubleshooting purposes.

The `Status.message` field SHOULD contain a developer-facing error message as
defined in `Status` message schema.

The server MAY include `Status.details` field with additional details. Read
below about what this field can contain in each specific failure case.

#### Bad Data

If the processing of the request fails because the request contains data that
cannot be decoded or is otherwise invalid and such failure is permanent then the
server MUST respond with `HTTP 400 Bad Request`. The `Status.details` field in
the response SHOULD contain a
[BadRequest](https://github.com/googleapis/googleapis/blob/d14bf59a446c14ef16e9931ebfc8e63ab549bf07/google/rpc/error_details.proto#L166)
that describes the bad data.

The client MUST NOT retry the request when it receives `HTTP 400 Bad Request`
response.

#### Throttling

If the server receives more requests than the client is allowed or the server is
overloaded the server SHOULD respond with `HTTP 429 Too Many Requests` or
`HTTP 503 Service Unavailable` and MAY include
["Retry-After"](https://datatracker.ietf.org/doc/html/rfc7231#section-7.1.3) header with a
recommended time interval in seconds to wait before retrying.

The client SHOULD honour the waiting interval specified in "Retry-After" header
if it is present. If the client receives `HTTP 429` or `HTTP 503` response and
"Retry-After" header is not present in the response then the client SHOULD
implement an exponential backoff strategy between retries.

#### All Other Responses

All other HTTP responses that are not explicitly listed in this document should
be treated according to HTTP specification.

If the server disconnects without returning a response the client SHOULD retry
and send the same request. The client SHOULD implement an exponential backoff
strategy between retries to avoid overwhelming the server.

### Connection

If the client is unable to connect to the server the client SHOULD retry the
connection using exponential backoff strategy between retries. The interval
between retries must have a random jitter.

The client SHOULD keep the connection alive between requests.

Server implementations MAY handle OTLP/gRPC, OTLP/HTTP requests and OTLP/HTTP+JSON on the same
port and multiplex the connections to the corresponding transport handler based
on "Content-Type" request header.

### Parallel Connections

To achieve higher total throughput the client MAY send requests using several
parallel HTTP connections. In that case the maximum number of parallel
connections SHOULD be configurable.
