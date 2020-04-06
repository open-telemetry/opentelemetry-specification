# OpenTelemetry to Zipkin Transformation

This document defines the transformation between OpenTelemetry and Zipkin Spans.
Zipkin's v2 API is defined in the
[zipkin.proto](https://github.com/openzipkin/zipkin-api/blob/master/zipkin.proto)

## Summary

The following table summarizes the major transformations between OpenTelemetry
and Zipkin.

| OpenTelemetry            | Zipkin           | Notes                                                        |
| ------------------------ | ---------------- | ------------------------------------------------------------ |
| Span.TraceID             | Span.TraceID     |                                                              |
| Span.ParentID            | Span.ParentID    |                                                              |
| Span.SpanID              | Span.ID          |                                                              |
| Span.TraceState          | TBD              | TBD                                                          |
| Span.Name                | Span.Name        |                                                              |
| Span.Kind                | Span.Kind        | See [SpanKind](#spankind) for values mapping                |
| Span.StartTime           | Span.Timestamp   | See [Unit of time](#unit-of-time)                            |
| Span.EndTime             | Span.Duration    | Duration is calculated based on StartTime and EndTime. See also [Unit of time](#unit-of-time) |
| Span.Attributes          | Span.Tags        | See [Attributes](#attributes) for data types for the mapping. |
| Span.Events              | Span.Annotations | See [Events](#events) for the mapping format.                |
| Span.Links               | TBD              | TBD                                                          |
| Span.Status              | Add to Span.Tags | See [Status](#status) for tag names to use.                  |
| Span.LocalChildSpanCount | TBD              | TBD                                                          |

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

- Service name
- Local_endpoint
- Remote_endpoint
- debug
- Shared

## Mappings

This section discusses the details of the transformations between OpenTelemetry
and Zipkin.

### SpanKind

The following table lists all the `SpanKind` mappings between OpenTelemetry and
Zipkin.

| OpenTelemetry | Zipkin | Note |
| ------------- | ------ | ---- |
| `SpanKind.CLIENT`|`SpanKind.CLIENT`||
| `SpanKind.SERVER`|`SpanKind.SERVER`||
| `SpanKind.CONSUMER`|`SpanKind.CONSUMER`||
| `SpanKind.PRODUCER`|`SpanKind.PRODUCER` ||
|`SpanKind.INTERNAL`|`null` |must be omitted (set to `null`)|

### Attribute

OpenTelemetry Span `Attribute`(s) MUST be reported as `tags` to Zipkin.
Primitive types MUST be converted to string using en-US culture settings.
Boolean values must use lower case strings `"true"` and `"false"`, except an
attribute named `error`. In case if value of the attribute is `false`, Zipkin
tag needs to be omitted.

Array values MUST be serialized to string like a JSON list as mentioned in
[semantic conventions document](https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/data-semantic-conventions.md#semantic-conventions).

TBD: add examples

### Status

Span `Status` MUST be reported as a key-value pair in `tags` to Zipkin.

The following table defines the OpenTelemetry `Status` to Zipkin `tags` mapping.

| Status|Tag Key| Tag Value |
|--|--|--|
|Code | `ot.status_code` | Name of the code, for example: `OK` |
|Message *(optional)* | `ot.status_description` | `{message}` |

The `ot.status_code` tag value MUST follow the [Standard GRPC Code
Names](https://github.com/grpc/grpc/blob/master/doc/statuscodes.md).

### Events

OpenTelemetry `Event` has an optional `Attribute`(s) which is not supported by
Zipkin. Events MUST be converted to the Annotations with the names which will
include attribute values like this:

```
"my-event-name": { "key1" : "value1", "key2": "value2" }
```

### Unit of Time

Zipkin times like `timestamp`, `duration` and `annotation.timestamp` MUST be
reported in microseconds with decimal accuracy. For example, `duration` of 1234
nanoseconds will be represented as 1.234 microseconds.

## Request Payload

For performance considerations, Zipkin fields that can be absent SHOULD be
omitted from the payload when they are empty in the OpenTelemetry `Span`.

For example, an OpenTelemetry `Span` without any `Event` should not have an
`annotations` field in the Zipkin payload.
