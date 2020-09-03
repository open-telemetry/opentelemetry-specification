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

### Resource

OpenTelemetry resources MUST be mapped to Jaeger process tags. Multiple resources can exist for a
single process and exporters need to handle this case accordingly.

### InstrumentationLibrary

OpenTelemetry Span's `InstrumentationLibrary` MUST be reported as span `tags` to Jaeger using the following mapping.

| OpenTelemetry | Jaeger |
| ------------- | ------ |
| `InstrumentationLibrary.name`|`otel.instrumentation_library.name`|
| `InstrumentationLibrary.version`|`otel.instrumentation_library.version`|

### Attribute

TBD

### Events

TBD
