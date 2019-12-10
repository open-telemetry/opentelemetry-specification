
# OpenTelemetry to Zipkin Transformation

This document defines the transformation between OpenTelemetry and Zipkin Spans.
Zipkin's v2 API is defined in the
[zipkin2-api.yaml](https://github.com/openzipkin/zipkin-api/blob/master/zipkin2-api.yaml)

## Summary

The following table summarizes the major transformations between OpenTelemetry
and Zipkin.

|OpenTelemetry|Zipkin
|--|--|--|
|`span.kind=INTERNAL`|`span.kind=SERVER`
|`span.attributes` | `span.tags`
|`span.status.code` | tag as `ot.status_code: OK`
|`span.status.message` | optional tag as `ot.status_description: {msg}`
|`span.events` | `span.annotations`, skip on event attributes

## Mappings

This section discusses the details of the transformations between OpenTelemetry
and Zipkin.

### SpanKind

Zipkin doesn't support OpenTelemetry's `SpanKind.INTERNAL`.
`SpanKind.INTERNAL` type MUST be reported to Zipkin as `SERVER`.

The following table lists all the `SpanKind` mappings between OpenTelemetry and
Zipkin.

|OpenTelemetry|Zipkin
|--|--|
`SpanKind.CLIENT`|`SpanKind.CLIENT`
`SpanKind.SERVER`|`SpanKind.SERVER`
`SpanKind.CONSUMER`|`SpanKind.CONSUMER`
`SpanKind.PRODUCER`|`SpanKind.PRODUCER`
`SpanKind.INTERNAL`|`SpanKind.SERVER`

### Attribute

OpenTelemetry Span `Attribute`(s) MUST be reported as `tags` to Zipkin.

### Status

Span `Status` SHOULD be reported as a key-value pair in `tags` to Zipkin.

The following table defines the OpenTelemetry `Status` to Zipkin `tags` mapping.

Status|Tag Key| Tag Value
|--|--|--|
|Code | `ot.status_code` | Name of the code, for example: `OK`
|Message *(optional)* | `ot.status_description` | `{message}`

The `ot.status_code` tag value MUST follow the [Standard GRPC Code
Names](https://github.com/grpc/grpc/blob/master/doc/statuscodes.md).

### Event

OpenTelemetry `Event` has an optional `Attribute`(s) which is not supported by
Zipkin.
These `Event` attributes are may be left out from the final Zipkin payload.

## Unit of Time

Zipkin times like `timestamp`, `duration` and `event.timestamp` MUST be reported
in microseconds with decimal accuracy.

## Request Payload

For performance considerations, Zipkin fields that can be absent SHOULD be
omitted from the payload when they are empty in the OpenTelemetry `Span`.

For example, an OpenTelemetry `Span` without any `Event` should not have an
`annotations` field in the Zipkin payload.
