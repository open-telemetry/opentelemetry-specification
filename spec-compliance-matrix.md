# Compliance of Implementations with Specification

The following tables show which features are implemented by each OpenTelemetry
language implementation.

`+` means the feature is supported, `-` means it is not supported, `N/A` means
the feature is not applicable to the particular language, blank cell means the
status of the feature is not known.

## Traces

|Feature                                       |Go|Java|JS     |Python|Ruby|Erlang|PHP|Rust|C++|.Net|
|----------------------------------------------|--|----|-------|------|----|------|---|----|---|----|
|[TracerProvider](https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/trace/api.md#tracerprovider-operations)|
|Create TracerProvider                         |  | +  | +     |      | +  |      | + | +  |   |    |
|Get a Tracer                                  |  | +  | +     |      | +  |      | + | +  |   |    |
|Safe for concurrent calls                     |  | +  | +     |      | +  |      | + | +  |   |    |
|[Tracer](https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/trace/api.md#tracer-operations)|
|Create a new Span                             |  | +  | +     |      | +  |      | + | +  |   |    |
|Get active Span                               |  | +  | +     |      | +  |      | + | +  |   |    |
|Mark Span active                              |  | +  | +     |      | +  |      | + | +  |   |    |
|Safe for concurrent calls                     |  | +  | +     |      | +  |      | + | +  |   |    |
|[SpanContext](https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/trace/api.md#spancontext)|
|IsValid                                       |  | +  | -     |      | +  |      | + | +  |   |    |
|IsRemote                                      |  | +  | +     |      | +  |      | + | +  |   |    |
|Conforms to the W3C TraceContext spec         |  | +  | +     |      | +  |      |   | -  |   |    |
|[Span](https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/trace/api.md#span)|
|Create root span                              |  | +  | +     |      | +  |      | + | +  |   |    |
|Create with default parent (active span)      |  | +  | +     |      | +  |      | + | +  |   |    |
|Create with parent from Context               |  | +  | +     |      | +  |      | + | +  |   |    |
|Create with explicit parent Span              |  | +  | +     |      | +  |      | + | -  |   |    |
|Create with explicit parent SpanContext       |  | +  | +     |      | +  |      |   | -  |   |    |
|UpdateName                                    |  | +  | +     |      | +  |      | + | +  |   |    |
|User-defined start timestamp                  |  | +  | +     |      | +  |      | + | +  |   |    |
|End                                           |  | +  | +     |      | +  |      | + | +  |   |    |
|End with timestamp                            |  | +  | +     |      | +  |      | + | -  |   |    |
|IsRecording                                   |  | +  | +     |      | +  |      | + |    |   |    |
|Set status                                    |  | +  | +     |      | +  |      | + | +  |   |    |
|Safe for concurrent calls                     |  | +  | +     |      | +  |      | + | +  |   |    |
|[Span attributes](https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/trace/api.md#set-attributes)|
|SetAttribute                                  |  | +  | +     |      | +  |      | + | +  |   |    |
|Set order preserved                           |  | -  | +     |      | +  |      | + | +  |   |    |
|String type                                   |  | +  | +     |      | +  |      | + | +  |   |    |
|Boolean type                                  |  | +  | +     |      | +  |      | + | +  |   |    |
|Double floating-point type                    |  | +  | +     |      | +  |      | - | +  |   |    |
|Signed int64 type                             |  | +  | +     |      | +  |      | - | +  |   |    |
|Array of primitives (homogeneous)             |  | +  | +     |      | -  |      | + | +  |   |    |
|Unicode support for keys and string values    |  | +  | +     |      | +  |      | + | +  |   |    |
|[Span linking](https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/trace/api.md#add-links)|
|AddLink                                       |  | +  | +     |      | +  |      | + | +  |   |    |
|Safe for concurrent calls                     |  | +  | +     |      | +  |      | + | +  |   |    |
|[Span events](https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/trace/api.md#add-events)|
|AddEvent                                      |  | +  | +     |      | +  |      | + | +  |   |    |
|Add order preserved                           |  | +  | +     |      | +  |      | + | +  |   |    |
|Safe for concurrent calls                     |  | +  | +     |      | +  |      | + | +  |   |    |
|[Span exceptions](https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/trace/api.md#record-exception)|
|RecordException                               |  | +  | +     |      | +  |      |   | +  |   |    |
|RecordException with extra parameters         |  | -  | +     |      | -  |      |   | +  |   |    |

## Metrics

|Feature                                       |Go|Java|Node.js|Python|Ruby|Erlang|PHP|Rust|C++|.Net|
|----------------------------------------------|--|----|-------|------|----|------|---|----|---|----|
|TBD|

## Resource

|Feature                                       |Go|Java|Node.js|Python|Ruby|Erlang|PHP|Rust|C++|.Net|
|----------------------------------------------|--|----|-------|------|----|------|---|----|---|----|
|TBD|

## Context Propagation

|Feature                                       |Go|Java|Node.js|Python|Ruby|Erlang|PHP|Rust|C++|.Net|
|----------------------------------------------|--|----|-------|------|----|------|---|----|---|----|
|TBD|

## Error Handling

|Feature                                       |Go|Java|Node.js|Python|Ruby|Erlang|PHP|Rust|C++|.Net|
|----------------------------------------------|--|----|-------|------|----|------|---|----|---|----|
|TBD|

## Environment Variables

|Feature                                       |Go|Java|Node.js|Python|Ruby|Erlang|PHP|Rust|C++|.Net|
|----------------------------------------------|--|----|-------|------|----|------|---|----|---|----|
|OTEL_RESOURCE_ATTRIBUTES|                     |  |    | +     |      |    |      |   |    |   |    |
|OTEL_LOG_LEVEL|                               |  |    | +     |      |    |      |   |    |   |    |
|OTEL_PROPAGATORS|                             |  |    |       |      |    |      |   |    |   |    |
|OTEL_BSP_*|                                   |  |    |       |      |    |      |   |    |   |    |
|OTEL_EXPORTER_OTLP_*|                         |  |    |       |      |    |      |   |    |   |    |
|OTEL_EXPORTER_JAEGER_*|                       |  |    |       |      |    |      |   |    |   |    |
|OTEL_EXPORTER_ZIPKIN_*|                       |  |    |       |      |    |      |   |    |   |    |

## Exporters

|Feature                                       |Go|Java|JS     |Python|Ruby|Erlang|PHP|Rust|C++|.Net|
|----------------------------------------------|--|----|-------|------|----|------|---|----|---|----|
|Standard output (logging)                     |  | +  | +     |      | +  |      | - | +  |   |    |
|In-memory (mock exporter)                     |  | +  | +     |      | +  |      | - | -  |   |    |
|[OTLP](https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/protocol/otlp.md)|
|OTLP/gRPC Exporter                            |  | +  | +     |      |    |      |   | +  |   |    |
|OTLP/HTTP binary Protobuf Exporter            |  | -  | +     |      |    |      |   |    |   |    |
|OTLP/HTTP JSON Protobuf Exporter              |  | -  | +     |      |    |      |   |    |   |    |
|OTLP/HTTP gzip Content-Encoding support       |  | -  | +     |      |    |      |   |    |   |    |
|Concurrent sending                            |  |    |       |      |    |      |   | +  |   |    |
|Honors retryable responses with backoff       |  |    |       |      |    |      |   |    |   |    |
|Honors non-retryable responses                |  |    |       |      |    |      |   |    |   |    |
|Honors throttling response                    |  |    |       |      |    |      |   |    |   |    |
|Multi-destination spec compliance             |  |    |       |      |    |      |   |    |   |    |
|[Zipkin](https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/trace/sdk_exporters/zipkin.md)|
|Zipkin V1 JSON                                |  |    |       |      |    |      | - | -  |   |    |
|Zipkin V1 Thrift                              |  |    |       |      |    |      | - | -  |   |    |
|Zipkin V2 JSON                                |  |    |       |      |    |      | + | +  |   |    |
|Zipkin V2 Protobuf                            |  |    |       |      |    |      |   | -  |   |    |
|Service name mapping                          |  | +  |       |      |    |      | + | +  |   |    |
|SpanKind mapping                              |  | +  |       |      |    |      | + | +  |   |    |
|InstrumentationLibrary mapping                |  | +  |       |      |    |      | - | -  |   |    |
|Boolean attributes                            |  | +  | +     |      |    |      | + | +  |   |    |
|Array attributes                              |  | +  | +     |      |    |      | + | +  |   |    |
|Status mapping                                |  | -  | +     |      |    |      | + | +  |   |    |
|Event attributes mapping to Annotations       |  |    | +     |      |    |      | + | +  |   |    |
|Fractional microseconds in timestamps         |  | -  | +     |      |    |      | - | -  |   |    |
|Jaeger|
|TBD|
|OpenCensus|
|TBD|
|Prometheus|
|TBD|
