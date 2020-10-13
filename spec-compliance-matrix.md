# Compliance of Implementations with Specification

The following tables show which features are implemented by each OpenTelemetry
language implementation.

`+` means the feature is supported, `-` means it is not supported, `N/A` means
the feature is not applicable to the particular language, blank cell means the
status of the feature is not known.

## Traces

|Feature                                       |Go |Java|JS |Python|Ruby|Erlang|PHP|Rust|C++|.Net|
|----------------------------------------------|---|----|---|------|----|------|---|----|---|----|
|[TracerProvider](https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/trace/api.md#tracerprovider-operations)|
|Create TracerProvider                         | + | +  | + | +    | +  | +    | + | +  | + | +  |
|Get a Tracer                                  | + | +  | + | +    | +  | +    | + | +  | + | +  |
|Safe for concurrent calls                     | + | +  | + | [-](https://github.com/open-telemetry/opentelemetry-python/issues/392)    | +  | +    | + | +  | + | +  |
|[Tracing Context Utilities](https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/trace/api.md#tracing-context-utilities)|
|Get active Span                               |   |    |   | +    |    |      |   |    |   |    |
|Set active Span                               |   |    |   | +    |    |      |   |    |   |    |
|[Tracer](https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/trace/api.md#tracer-operations)|
|Create a new Span                             | + | +  | + | +    | +  | +    | + | +  | + | +  |
|Get active Span                               | + | +  | + | +    | +  | +    | + | +  | + | +  |
|Mark Span active                              | + | +  | + | +    | +  | +    | + | +  | - | -  |
|Safe for concurrent calls                     | + | +  | + | [-](https://github.com/open-telemetry/opentelemetry-python/issues/1156)    | +  | +    | + | +  | + | +  |
|[SpanReference](https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/trace/api.md#spanreference)|
|Use SpanReference instead of SpanContext      |   |    |   |      |    |      |   |    |   |    |
|IsValid                                       | + | +  | + | +    | +  | +    | + | +  | + | +  |
|IsRemote                                      | - | +  | + | +    | +  | +    | + | +  | + | +  |
|Conforms to the W3C TraceContext spec         | + | +  | + | +    | +  | +    |   | -  | + | +  |
|[Span](https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/trace/api.md#span)|
|Create root span                              | + | +  | + | +    | +  | +    | + | +  | + | +  |
|Create with default parent (active span)      | + | +  | + | +    | +  | +    | + | +  | + | +  |
|Create with parent from Context               | + | +  | + | +    | +  | +    | + | +  | + | +  |
|No explicit parent Span/SpanReference allowed |   | +  |   |      |    |      |   |    |   |    |
|SpanProcessor.OnStart receives parent Context |   |    |   |      |    |      |   |    |   |    |
|UpdateName                                    | + | +  | + | +    | +  | +    | + | +  | - | +  |
|User-defined start timestamp                  | + | +  | + | +    | +  | +    | + | +  | + | +  |
|End                                           | + | +  | + | +    | +  | +    | + | +  | + | +  |
|End with timestamp                            | + | +  | + | +    | +  | +    | + | -  | + | +  |
|IsRecording                                   | + | +  | + | +    | +  | +    | + |    | + | +  |
|IsRecording becomes false after End           |   |    |   |      |    |      |   |    |   |    |
|Set status                                    | + | +  | + | +    | +  | +    | + | +  | + | +  |
|Safe for concurrent calls                     | + | +  | + | [-](https://github.com/open-telemetry/opentelemetry-python/issues/1157)    | +  | +    | + | +  | + | +  |
|[Span attributes](https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/trace/api.md#set-attributes)|
|SetAttribute                                  | + | +  | + | +    | +  | +    | + | +  | + | +  |
|Set order preserved                           | + | -  | + | +    | +  | +    | + | +  | + | +  |
|String type                                   | + | +  | + | +    | +  | +    | + | +  | + | +  |
|Boolean type                                  | + | +  | + | +    | +  | +    | + | +  | + | +  |
|Double floating-point type                    | + | +  | + | +    | +  | +    | - | +  | + | +  |
|Signed int64 type                             | + | +  | + | +    | +  | +    | - | +  | + | +  |
|Array of primitives (homogeneous)             | + | +  | + | +    | +  | -    | + | +  | + | +  |
|`null` values documented as invalid/undefined |   | +  |   |      |    |      |   |    |   |    |
|Unicode support for keys and string values    | + | +  | + | +    | +  | +    | + | +  | + | +  |
|[Span linking](https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/trace/api.md#add-links)|
|AddLink                                       | + | +  | + | +    | +  | +    | + | +  | - | +  |
|Safe for concurrent calls                     | + | +  | + | +    | +  | +    | + | +  | - | +  |
|[Span events](https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/trace/api.md#add-events)|
|AddEvent                                      | + | +  | + | +    | +  | +    | + | +  | - | +  |
|Add order preserved                           | + | +  | + | +    | +  | +    | + | +  | - | +  |
|Safe for concurrent calls                     | + | +  | + | +    | +  | +    | + | +  | - | +  |
|[Span exceptions](https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/trace/api.md#record-exception)|
|RecordException                               | - | +  | + | +    | +  | -    |   | +  | - | +  |
|RecordException with extra parameters         | - | +  | + | [-](https://github.com/open-telemetry/opentelemetry-python/issues/1102)    | -  | -    |   | +  | - | +  |
|[Sampling](https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/trace/sdk.md#sampling)|
|Allow samplers to modify tracestate           |   |    |   | [-](https://github.com/open-telemetry/opentelemetry-python/issues/1220)     |    |      |   |    |   |    |

## Baggage

|Feature                                       |Go|Java|JS |Python|Ruby|Erlang|PHP|Rust|C++|.Net|
|----------------------------------------------|--|----|---|------|----|------|---|----|---|----|
|Basic support                                 |  |    |   |      |    |      |   |    |   |    |
|Use official header name `baggage`            |  |    |   | +    |    |      |   |    |   |    |

## Metrics

|Feature                                       |Go|Java|JS |Python|Ruby|Erlang|PHP|Rust|C++|.Net|
|----------------------------------------------|--|----|---|------|----|------|---|----|---|----|
|TBD|

## Resource

|Feature                                       |Go |Java|JS |Python|Ruby|Erlang|PHP|Rust|C++|.Net|
|----------------------------------------------|---|----|---|------|----|------|---|----|---|----|
|Create from Attributes                        | + | +  | + | +    | +  |      |   |    |   |    |
|Create empty                                  | + | +  | + | +    | +  |      |   |    |   |    |
|Merge                                         | + | +  | + | +    | +  |      |   |    |   |    |
|Retrieve attributes                           | + | +  | + | +    | +  |      |   |    |   |    |

## Context Propagation

|Feature                                       |Go|Java|JS |Python|Ruby|Erlang|PHP|Rust|C++|.Net|
|----------------------------------------------|--|----|---|------|----|------|---|----|---|----|
|Create Context Key                            |  |    | + | +    | +  |      | + |    |   |    |
|Get value from Context                        |  |    | + | +    | +  |      | + |    |   |    |
|Set value for Context                         |  |    | + | +    | +  |      | + |    |   |    |
|Attach Context                                |  |    | + | +    | +  |      | + |    |   |    |
|Detach Context                                |  |    | + | +    | +  |      | + |    |   |    |
|Get current Context                           |  |    | + | +    | +  |      | + |    |   |    |
|Composite Propagator                          |  |    | + | +    | +  |      |   |    |   |    |
|Global Propagator                             |  | +  | + | +    | +  |      |   |    |   |    |
|TraceContext Propagator                       |  | +  | + | +    | +  |      |   |    |   |    |
|B3 Propagator                                 |  | +  | + | +    |    |      |   |    |   |    |
|Jaeger Propagator                             |  | -  | + | [-](https://github.com/open-telemetry/opentelemetry-python/issues/1103)    |    |      |   |    |   |    |
|[TextMapPropagator](https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/context/api-propagators.md#textmap-propagator)|
|Fields                                        |  | +  |   | [-](https://github.com/open-telemetry/opentelemetry-python/issues/1104)   |    |      |   |    |   |    |
|Setter argument                               |  | +  | + | +   |    |      |   |    |   |    |
|Getter argument                               |  | +  | + | +   |    |      |   |    |   |    |
|Getter argument returning Keys                |  | -  |   | [-](https://github.com/open-telemetry/opentelemetry-python/issues/1084)   |    |      |   |    |   |    |

## Error Handling

|Feature                                       |Go|Java|JS |Python|Ruby|Erlang|PHP|Rust|C++|.Net|
|----------------------------------------------|--|----|---|------|----|------|---|----|---|----|
|TBD|

## Environment Variables

|Feature                                       |Go |Java|JS |Python|Ruby|Erlang|PHP|Rust|C++|.Net|
|----------------------------------------------|---|----|---|------|----|------|---|----|---|----|
|OTEL_RESOURCE_ATTRIBUTES                      | + | +  | + | +    | +  | -    | - |    | - | -  |
|OTEL_LOG_LEVEL                                |   | -  | + | [-](https://github.com/open-telemetry/opentelemetry-python/issues/1059)    | +  | -    | - |    | - | -  |
|OTEL_PROPAGATORS                              |   |    |   | +    |    | -    | - |    | - | -  |
|OTEL_BSP_*                                    |   | +  |   | +    | +  | -    | - |    | - | -  |
|OTEL_EXPORTER_OTLP_*                          |   |    |   | [-](https://github.com/open-telemetry/opentelemetry-python/issues/1004)    | +  | -    | - |    | - | -  |
|OTEL_EXPORTER_JAEGER_*                        |   |    |   | [-](https://github.com/open-telemetry/opentelemetry-python/issues/1056)    | +  | -    | - |    | - | -  |
|OTEL_EXPORTER_ZIPKIN_*                        |   |    |   | +    |    | -    | - |    | - | -  |
|OTEL_EXPORTER                                 |   |    |   | [-](https://github.com/open-telemetry/opentelemetry-python/issues/1155)    |    |      |   |    |   |    |

## Exporters

|Feature                                       |Go |Java|JS |Python|Ruby|Erlang|PHP|Rust|C++|.Net|
|----------------------------------------------|---|----|---|------|----|------|---|----|---|----|
|Standard output (logging)                     | + | +  | + | +    | +  | +    | - | +  | + | +  |
|In-memory (mock exporter)                     | + | +  | + | +    | +  | +    | - | -  | - | -  |
|[OTLP](https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/protocol/otlp.md)|
|OTLP/gRPC Exporter                            | + | +  | + | +    |    | +    |   | +  | + | +  |
|OTLP/HTTP binary Protobuf Exporter            | - | -  | + | [-](https://github.com/open-telemetry/opentelemetry-python/issues/1106)    | +  | +    |   |    | + | +  |
|OTLP/HTTP JSON Protobuf Exporter              | - | -  | + | [-](https://github.com/open-telemetry/opentelemetry-python/issues/1003)    |    | -    |   |    |   |    |
|OTLP/HTTP gzip Content-Encoding support       | - | -  | + | [-](https://github.com/open-telemetry/opentelemetry-python/issues/1107)    |    | -    |   |    |   |    |
|Concurrent sending                            | - |    | + | [-](https://github.com/open-telemetry/opentelemetry-python/issues/1108)    |    | -    |   | +  |   |    |
|Honors retryable responses with backoff       | + |    | + | +    | +  | -    |   |    |   |    |
|Honors non-retryable responses                | + |    | - | +    | +  | -    |   |    |   |    |
|Honors throttling response                    | + |    | - | +    | +  | -    |   |    |   |    |
|Multi-destination spec compliance             | - |    |   | [-](https://github.com/open-telemetry/opentelemetry-python/issues/1109)    |    | -    |   |    |   |    |
|[Zipkin](https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/trace/sdk_exporters/zipkin.md)|
|Zipkin V1 JSON                                |   |    |   | [-](https://github.com/open-telemetry/opentelemetry-python/issues/1173)    |    | -    | - | -  |   |    |
|Zipkin V1 Thrift                              |   |    |   | [-](https://github.com/open-telemetry/opentelemetry-python/issues/1174)    |    | -    | - | -  |   |    |
|Zipkin V2 JSON                                | + |    |   | +    |    | -    | + | +  |   |    |
|Zipkin V2 Protobuf                            |   |    |   | [-](https://github.com/open-telemetry/opentelemetry-python/issues/1175)    |    | +    |   | -  |   |    |
|Service name mapping                          | + | +  | + | +    |    | +    | + | +  |   |    |
|SpanKind mapping                              | + | +  | + | +    |    | +    | + | +  |   |    |
|InstrumentationLibrary mapping                |   | +  | - | +    |    | -    | - | -  |   |    |
|Boolean attributes                            | + | +  | + | +    |    | +    | + | +  |   |    |
|Array attributes                              | + | +  | + | [-](https://github.com/open-telemetry/opentelemetry-python/issues/1110)    |    | +    | + | +  |   |    |
|Status mapping                                | + | -  | + | +    |    | +    | + | +  |   |    |
|Event attributes mapping to Annotations       | + |    | + | +    |    | +    | + | +  |   |    |
|Integer microseconds in timestamps            |   |    |   | +    |    |      |   |    |   |    |
|Jaeger|
|TBD|
|OpenCensus|
|TBD|
|Prometheus|
|TBD|
