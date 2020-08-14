# OpenTelemetry to Jaeger Transformation

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

### InstrumentationLibrary

OpenTelemetry Span's `InstrumentationLibrary` MUST be reported as `tags` to Jaeger using the following mapping.
 
| OpenTelemetry | Jaeger |
| ------------- | ------ |
| `InstrumentationLibrary.name`|`otel.instrumentation_library.name`|
| `InstrumentationLibrary.version`|`otel.instrumentation_library.version`|

### Attribute

TBD

### Status

TBD

### Events

TBD
