# OpenTelemetry to Jaeger Transformation

This document defines the transformation between OpenTelemetry and Jaeger Spans.
Jaeger accepts spans in two formats:

* Thrift `Batch`, defined in [jaeger-idl/.../jaeger.thrift](https://github.com/jaegertracing/jaeger-idl/blob/master/thrift/jaeger.thrift), accepted via UDP or HTTP
* Protobuf `Batch`, defined in [jaeger-idl/.../model.proto](https://github.com/jaegertracing/jaeger-idl/blob/master/proto/api_v2/model.proto), accepted via gRPC

See also: [Jaeger APIs](https://www.jaegertracing.io/docs/latest/apis/).

## Summary

The following table summarizes the major transformations between OpenTelemetry
and Jaeger.

| OpenTelemetry            | Jaeger Thrift    | Jaeger Proto     | Notes |
| ------------------------ | ---------------- | ---------------- | ----- |
| Span.TraceID             | Span.traceIdLow/High | Span.trace_id | See [IDs](#ids)     |
| Span.ParentID            | Span.parentSpanId | as SpanReference | See [Parent ID](#parent-id)     |
| Span.SpanID              | Span.spanId       | Span.span_id     |      |
| Span.Name                | Span.operationName | Span.operation_name |  |
| Span.Kind                | Span.tags["span.kind"] | same | See [SpanKind](#spankind) for values mapping |
| Span.StartTime           | Span.startTime | Span.start_time | See [Unit of time](#unit-of-time) |
| Span.EndTime             | Span.duration | same | Calculated as EndTime - StartTime. See also [Unit of time](#unit-of-time) |
| Span.Attributes          | Span.tags | same | See [Attributes](#attributes) for data types for the mapping.            |
| Span.Events              | Span.logs | same | See [Events](#events) for the mapping format. |
| Span.Links               | Span.references | same | See [Links](#links) |
| Span.Status              | Add to Span.tags | same | See [Status](#status) for tag names to use. |

## Mappings

This section discusses the details of the transformations between OpenTelemetry
and Jaeger.

### Resource

OpenTelemetry resources MUST be mapped to Jaeger's `Span.Process` tags. Multiple resources can exist for a
single process and exporters need to handle this case accordingly.

Critically, Jaeger backend depends on `Span.Process.ServiceName` to identify the service
that produced the spans. That field MUST be populated from the `service.name` attribute
of the [`service` resource](../../resource/semantic_conventions/README.md#service).

### InstrumentationLibrary

OpenTelemetry Span's `InstrumentationLibrary` MUST be reported as span `tags` to Jaeger using the following mapping.

| OpenTelemetry | Jaeger |
| ------------- | ------ |
| `InstrumentationLibrary.name`|`otel.library.name`|
| `InstrumentationLibrary.version`|`otel.library.version`|

### IDs

Trace and span IDs in Jaeger are random sequences of bytes. However, Thrft model
represents IDs using `i64` type, or in case of a 128-bit wide Trace ID as two `i64`
fields `traceIdLow` and `traceIdHigh`. The bytes MUST be converted to/from unsigned
ints using Big Endian byte order, e.g. `[0x10, 0x00, 0x00, 0x00] == 268435456`.
The unsigned ints MUST be converted to `i64` by re-interpreting the existing
64bit value as signed `i64`. For example (in Go):

```go
var (
    id       []byte = []byte{0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00}
    unsigned uint64 = binary.BigEndian.Uint64(id)
    signed   int64  = int64(unsigned)
)
fmt.Println("unsigned:", unsigned)
fmt.Println("  signed:", signed)
// Output:
// unsigned: 18374686479671623680
//   signed: -72057594037927936
```

### Parent ID

Jaeger Thrift format allows capturing parent ID in a top-level Span field.
Jaeger Proto format does not support parent ID field; instead the parent
MUST be recorded as a `SpanReference` of type `CHILD_OF`, e.g.:

```python
    SpanReference(
        ref_type=opentracing.CHILD_OF,
        trace_id=span.context.trace_id,
        span_id=parent_id,
    )
```

### SpanKind

OpenTelemetry `SpanKind` field MUST be encoded as `span.kind` tag in Jaeger span.

| OpenTelemetry | Jaeger |
| ------------- | ------ |
| `SpanKind.CLIENT`|`"client"`|
| `SpanKind.SERVER`|`"server"`|
| `SpanKind.CONSUMER`|`"consumer"`|
| `SpanKind.PRODUCER`|`"producer"` |
| `SpanKind.INTERNAL`| do not add `span.kind` tag |

### Unit of time

In Jaeger Thrift format the timestamps and durations MUST be represented in
microseconds (since epoch for timestamps). If the original value in OpenTelemetry
is expressed in nanoseconds, it MUST be rounded or truncated to microseconds.

In Jaeger Proto format the timestamps and durations MUST be represented
with nanosecond precision using `google.protobuf.Timestamp` and
`google.protobuf.Duration` types.

### Status

Span `Status` MUST be reported as a key-value pair in `tags` to Jaeger, unless it is `UNSET`.
In the latter case it MUST NOT be reported.

The following table defines the OpenTelemetry `Status` to Jaeger `tags` mapping.

| Status|Tag Key| Tag Value |
|--|--|--|
|Code | `otel.status_code` | Name of the code, either `OK` or `ERROR`. MUST NOT be set if the code is `UNSET`. |
|Description | `otel.status_description` | Description of the `Status` if it has a value otherwise not set. |

### Error flag

When Span `Status` is set to `ERROR`, an `error` span tag MUST be added with the
Boolean value of `true`. The added `error` tag MAY override any previous value.

### Attributes

OpenTelemetry Span `Attribute`(s) MUST be reported as `tags` to Jaeger.

Primitive types MUST be represented by the corresponding types of Jaeger tags.

Array values MUST be serialized to string like a JSON list as mentioned in
[semantic conventions](../../overview.md#semantic-conventions).

### Links

OpenTelemetry `Link`(s) MUST be converted to `SpanReference`(s) in Jaeger,
using `FOLLOWS_FROM` reference type. The Link's attributes cannot be represented
in Jaeger explicitly. The exporter MAY additionally convert `Link`(s) to span `Log`(s):

* use Span start time as the timestamp of the Log
* set Log tag `event=link`
* set Log tags `trace_id` and `span_id` from the respective `SpanContext`'s fields
* store `Link`'s attributes as Log tags

### Events

Events MUST be converted to Jaeger Logs. OpenTelemetry Event's `time_unix_nano` and `attributes` fields map directly to Jaeger Log's `timestamp` and `fields` fields. Jaeger Log has no direct equivalent for OpenTelemetry Event's `name` and `dropped_attributes_count` fields but OpenTracing semantic conventions specify some special attribute names [here](https://github.com/opentracing/specification/blob/master/semantic_conventions.md#log-fields-table). OpenTelemetry Event's `name` and `dropped_attributes_count` fields should be added to Jaeger Log's `fields` map as follows:

| OpenTelemetry Event Field | Jaeger Attribute |
| -------------------------- | ----------------- |
| `name`|`event`|
| `dropped_attributes_count`|`otel.event.dropped_attributes_count`|

* `dropped_attributes_count` should only be recorded when it contains a non-zero value.
* If OpenTelemetry Event contains an attributes with the key `event`, it should take precedence over Event's `name` field.
