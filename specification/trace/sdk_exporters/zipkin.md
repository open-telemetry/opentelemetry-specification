# OpenTelemetry to Zipkin Transformation

**Status**: [Stable](../../document-status.md)

This document defines the transformation between OpenTelemetry and Zipkin Spans.
Zipkin's v2 API is defined in the
[zipkin.proto](https://github.com/openzipkin/zipkin-api/blob/master/zipkin.proto)

## Summary

The following table summarizes the major transformations between OpenTelemetry
and Zipkin.

| OpenTelemetry            | Zipkin           | Notes                                                                                         |
| ------------------------ | ---------------- | --------------------------------------------------------------------------------------------- |
| Span.TraceID             | Span.TraceID     |                                                                                               |
| Span.ParentID            | Span.ParentID    |                                                                                               |
| Span.SpanID              | Span.ID          |                                                                                               |
| Span.TraceState          | TBD              | TBD                                                                                           |
| Span.Name                | Span.Name        |                                                                                               |
| Span.Kind                | Span.Kind        | See [SpanKind](#spankind) for values mapping                                                  |
| Span.StartTime           | Span.Timestamp   | See [Unit of time](#unit-of-time)                                                             |
| Span.EndTime             | Span.Duration    | Duration is calculated based on StartTime and EndTime. See also [Unit of time](#unit-of-time) |
| Span.Attributes          | Span.Tags        | See [Attributes](../../common/common.md#attributes) for data types for the mapping.            |
| Span.Events              | Span.Annotations | See [Events](#events) for the mapping format.                                                 |
| Span.Links               | TBD              | TBD                                                                                           |
| Span.Status              | Add to Span.Tags | See [Status](#status) for tag names to use.                                                   |
| Span.LocalChildSpanCount | TBD              | TBD                                                                                           |

TBD : This is work in progress document and it is currently doesn't specify
mapping for these fields:

OpenTelemetry fields:

- Resource attributes
- Tracestate
- Links
- LocalChildSpanCount
- dropped attributes count
- dropped events count
- dropped links count

Zipkin fields:

- Local_endpoint
- debug
- Shared

## Mappings

This section discusses the details of the transformations between OpenTelemetry
and Zipkin.

### Service name

Zipkin service name MUST be set to the value of the
[resource attribute](../../resource/semantic_conventions/README.md):
`service.name`. If no `service.name` is contained in a Span's Resource, it MUST be populated from the
[default](../../resource/sdk.md#sdk-provided-resource-attributes) `Resource`.
In Zipkin it is important that the service name is consistent
for all spans in a local root. Otherwise service graph and aggregations would
not work properly. OpenTelemetry doesn't provide this consistency guarantee.
Exporter may chose to override the value for service name based on a local root
span to improve Zipkin user experience.

*Note*, the attribute `service.namespace` MUST NOT be used for the Zipkin
service name and should be sent as a Zipkin tag.

### SpanKind

The following table lists all the `SpanKind` mappings between OpenTelemetry and
Zipkin.

| OpenTelemetry | Zipkin | Note |
| ------------- | ------ | ---- |
| `SpanKind.CLIENT`|`SpanKind.CLIENT`||
| `SpanKind.SERVER`|`SpanKind.SERVER`||
| `SpanKind.CONSUMER`|`SpanKind.CONSUMER`||
| `SpanKind.PRODUCER`|`SpanKind.PRODUCER` ||
| `SpanKind.INTERNAL`|`null` |must be omitted (set to `null`)|

### InstrumentationLibrary

OpenTelemetry Span's `InstrumentationLibrary` MUST be reported as `tags` to Zipkin using the following mapping.

| OpenTelemetry | Zipkin
| ------------- | ------ |
| `InstrumentationLibrary.name`|`otel.library.name`|
| `InstrumentationLibrary.version`|`otel.library.version`|

### Remote endpoint

#### OTLP -> Zipkin

If Zipkin `SpanKind` resolves to either `SpanKind.CLIENT` or `SpanKind.PRODUCER`
then the service SHOULD specify remote endpoint otherwise Zipkin won't treat the
Span as a dependency. `peer.service` is the preferred attribute but is not
always available. The following table lists the possible attributes for
`remoteEndpoint` by preferred ranking:

|Rank|Attribute Name|Reason|
|---|---|---|
|1|peer.service|[OpenTelemetry adopted attribute for remote service.](../semantic_conventions/span-general.md#general-remote-service-attributes)|
|2|net.peer.name|[OpenTelemetry adopted attribute for remote hostname, or similar.](../semantic_conventions/span-general.md#general-network-connection-attributes)|
|3|net.peer.ip & net.peer.port|[OpenTelemetry adopted attribute for remote address of the peer.](../semantic_conventions/span-general.md#general-network-connection-attributes)|
|4|peer.hostname|Remote hostname defined in OpenTracing specification.|
|5|peer.address|Remote address defined in OpenTracing specification.|
|6|http.host|Commonly used HTTP host header attribute for Http Spans.|
|7|db.name|Commonly used database name attribute for DB Spans.|

* Ranking should control the selection order. For example, `net.peer.name` (Rank
  2) should be selected before `http.host` (Rank 6).
* `net.peer.ip` can be used by itself as `remoteEndpoint` but should be combined
  with `net.peer.port` if it is also present.

#### Zipkin -> OTLP

When mapping from Zipkin to OTLP set `peer.service` tag from `remoteEndpoint`
unless there is a `peer.service` tag defined explicitly.

### Attribute

OpenTelemetry Span `Attribute`(s) MUST be reported as `tags` to
Zipkin.

Some attributes defined in [semantic
convention](../semantic_conventions/README.md)
document maps to the strongly-typed fields of Zipkin spans.

Primitive types MUST be converted to string using en-US culture settings.
Boolean values MUST use lower case strings `"true"` and `"false"`.

Array values MUST be serialized to string like a JSON list as mentioned in
[semantic conventions](../../overview.md#semantic-conventions).

TBD: add examples

### Status

Span `Status` MUST be reported as a key-value pair in `tags` to Zipkin, unless it is `UNSET`.
In the latter case it MUST NOT be reported.

The following table defines the OpenTelemetry `Status` to Zipkin `tags` mapping.

| Status|Tag Key| Tag Value |
|--|--|--|
|Code | `otel.status_code` | Name of the code, either `OK` or `ERROR`. MUST NOT be set if the code is `UNSET`. |
|Description| `error` | Description of the `Status`. MUST be set if the code is `ERROR`, use an empty string if Description has no value. MUST NOT be set for `OK` and `UNSET` codes. |

Note: The `error` tag should only be set if `Status` is `Error`. If a boolean
version (`{"error":false}` or `{"error":"false"}`) is present, it SHOULD be
removed. Zipkin will treat any span with `error` sent as failed.

### Events

OpenTelemetry `Event` has an optional `Attribute`(s) which is not supported by
Zipkin. Events MUST be converted to the Annotations with the names which will
include attribute values like this:

```
"my-event-name": { "key1" : "value1", "key2": "value2" }
```

### Unit of Time

Zipkin times like `timestamp`, `duration` and `annotation.timestamp` MUST be
reported in microseconds as whole numbers. For example, `duration`
of 1234 nanoseconds will be represented as 1 microsecond.

## Request Payload

For performance considerations, Zipkin fields that can be absent SHOULD be
omitted from the payload when they are empty in the OpenTelemetry `Span`.

For example, an OpenTelemetry `Span` without any `Event` should not have an
`annotations` field in the Zipkin payload.

## Considerations for Legacy (v1) Format

Zipkin's v2 [json](https://github.com/openzipkin/zipkin-api/blob/master/zipkin2-api.yaml) format was defined in 2017, followed up by a [protobuf](https://github.com/openzipkin/zipkin-api/blob/master/zipkin.proto) format in 2018.

Frameworks made before then use a more complex v1 [Thrift](https://github.com/openzipkin/zipkin-api/blob/master/thrift/zipkinCore.thrift) or [json](https://github.com/openzipkin/zipkin-api/blob/master/zipkin-api.yaml) format that notably differs in so far as it uses terminology such as Binary Annotation, and repeats endpoint information on each attribute.

Consider using [V1SpanConverter.java](https://github.com/openzipkin/zipkin/blob/master/zipkin/src/main/java/zipkin2/v1/V1SpanConverter.java) as a reference implementation for converting v1 model to OpenTelemetry.

The span timestamp and duration were late additions to the V1 format. As in the code link above, it is possible to heuristically derive them from annotations.
