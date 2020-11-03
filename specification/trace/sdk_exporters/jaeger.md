# OpenTelemetry to Jaeger Transformation

**Status**: [Feature-freeze](../../document-status.md).

This document defines the transformation between OpenTelemetry and Jaeger Spans.
Jaeger's v2 API is defined in the
[jaeger model.proto](https://github.com/jaegertracing/jaeger-idl/blob/master/proto/api_v2/model.proto)

## Summary

The following table summarizes the major transformations between OpenTelemetry
and Jaeger.

TBD

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

### Attribute

TBD

### Status

TBD

### Events

Events MUST be converted to Jaeger Logs. OpenTelemetry Event's `time_unix_nano` and `attributes` fields map directly to Jaeger Log's `timestamp` and `fields` fields. Jaeger Log has no direct equivalent for OpenTelemetry Event's `name` and `dropped_attributes_count` fields but OpenTracing semantic conventions specify some special attribute names [here](https://github.com/opentracing/specification/blob/master/semantic_conventions.md#log-fields-table). OpenTelemetry Event's `name` and `dropped_attributes_count` fields should be added to Jaeger Log's `fields` map as follows:

| OpenTelemetry Event Field | Jaeger Attribute |
| -------------------------- | ----------------- |
| `name`|`event`|
| `dropped_attributes_count`|`otel.event.dropped_attributes_count`|

* `dropped_attributes_count` should only be recorded when it contains a non-zero value.
* If OpenTelemetry Event contains an attributes with the key `event`, it should take precedence over Event's `name` field.
