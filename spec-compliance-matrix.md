# Compliance of Implementations with Specification

The following tables show which features are implemented by each OpenTelemetry
language implementation.

`+` means the feature is supported, `-` means it is not supported, `N/A` means
the feature is not applicable to the particular language, blank cell means the
status of the feature is not known.

## Traces

| Feature                                                                                          | Optional | Go | Java | JS | Python | Ruby | Erlang | PHP | Rust | C++ | .Net | Swift |
|--------------------------------------------------------------------------------------------------|----------|----|------|----|--------|------|--------|-----|------|-----|------|-------|
| [TracerProvider](specification/trace/api.md#tracerprovider-operations)                           |          |    |      |    |        |      |        |     |      |     |      |       |
| Create TracerProvider                                                                            |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| Get a Tracer                                                                                     |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| Safe for concurrent calls                                                                        |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| Shutdown (SDK only required)                                                                     |          | +  | +    | +  | +      | +    | -      |     | +    | +   | +    | +     |
| ForceFlush (SDK only required)                                                                   |          | [-](https://github.com/open-telemetry/opentelemetry-go/issues/1606)  | +    | -  | -      | +    | -      |     | -    | -   | +    | +     |
| [Trace / Context interaction](specification/trace/api.md#context-interaction)                    |          |    |      |    |        |      |        |     |      |     |      |       |
| Get active Span                                                                                  |          | N/A| +    | +  | +      | +    | +    |     | +    | +   | +    | +     |
| Set active Span                                                                                  |          | N/A| +    | +  | +      | +    | +    |     | +    | +   | +    | +     |
| [Tracer](specification/trace/api.md#tracer-operations)                                           |          |    |      |    |        |      |        |     |      |     |      |       |
| Create a new Span                                                                                |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| Get active Span                                                                                  |          | N/A| +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| Mark Span active                                                                                 |          | N/A| +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| Safe for concurrent calls                                                                        |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| [SpanContext](specification/trace/api.md#spancontext)                                            |          |    |      |    |        |      |        |     |      |     |      |       |
| IsValid                                                                                          |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| IsRemote                                                                                         |          | -  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| Conforms to the W3C TraceContext spec                                                            |          |    | +    | +  | +      | +    | +      |     | +    | +   | +    | +     |
| [Span](specification/trace/api.md#span)                                                          |          |    |      |    |        |      |        |     |      |     |      |       |
| Create root span                                                                                 |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| Create with default parent (active span)                                                         |          | N/A| +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| Create with parent from Context                                                                  |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| No explicit parent Span/SpanContext allowed                                                      |          | +  | +    | +  | +      | +    | +      |     | +    |     | -    | +     |
| SpanProcessor.OnStart receives parent Context                                                    |          | +  | +    | +  | +      | +    | +      |     | +    |     | -    | +     |
| UpdateName                                                                                       |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| User-defined start timestamp                                                                     |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| End                                                                                              |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| End with timestamp                                                                               |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| IsRecording                                                                                      |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| IsRecording becomes false after End                                                              |          | +  | +    | +  | +      | +    | +      |     |      | +   | -    | +     |
| Set status with StatusCode (Unset, Ok, Error)                                                    |          | +  | +    | +  | +      | +    | -      |     | +    |     | +    | +     |
| Safe for concurrent calls                                                                        |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| events collection size limit                                                                     |          | +  | +    | +  | +      | +    | -      |     | +    | +   | -    | +     |
| attribute collection size limit                                                                  |          | +  | +    | +  | +      | +    | -      |     | +    | +   | -    | +     |
| links collection size limit                                                                      |          | +  | +    | +  | +      | +    | -      |     | +    | +   | -    | +     |
| [Span attributes](specification/trace/api.md#set-attributes)                                     |          |    |      |    |        |      |        |     |      |     |      |       |
| SetAttribute                                                                                     |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| Set order preserved                                                                              | X        | +  | -    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| String type                                                                                      |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| Boolean type                                                                                     |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| Double floating-point type                                                                       |          | +  | +    | +  | +      | +    | +      | -   | +    | +   | +    | +     |
| Signed int64 type                                                                                |          | +  | +    | +  | +      | +    | +      | -   | +    | +   | +    | +     |
| Array of primitives (homogeneous)                                                                |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| `null` values documented as invalid/undefined                                                    |          | +  | +    | +  | +      | +    | N/A    |     |      | +   |      | N/A   |
| Unicode support for keys and string values                                                       |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| [Span linking](specification/trace/api.md#specifying-links)                                      |          |    |      |    |        |      |        |     |      |     |      |       |
| Links can be recorded on span creation                                                           |          | +  |      |    |        |      |        |     |      |     |      |       |
| Links order is preserved                                                                         |          | +  |      |    |        |      |        |     |      |     |      |       |
| [Span events](specification/trace/api.md#add-events)                                             |          |    |      |    |        |      |        |     |      | +   |      |       |
| AddEvent                                                                                         |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| Add order preserved                                                                              |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| Safe for concurrent calls                                                                        |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| [Span exceptions](specification/trace/api.md#record-exception)                                   |          |    |      |    |        |      |        |     |      |     |      |       |
| RecordException                                                                                  |          | -  | +    | +  | +      | +    | -      |     | +    | -   | +    | -     |
| RecordException with extra parameters                                                            |          | -  | +    | +  | +      | +    | -      |     | +    | -   | +    | -     |
| [Sampling](specification/trace/sdk.md#sampling)                                                  |          |    |      |    |        |      |        |     |      |     |      |       |
| Allow samplers to modify tracestate                                                              |          | +  | +    |    | +      | +    | +      |     | +    |     | -    | +     |
| ShouldSample gets full parent Context                                                            |          | +  | +    | +  | +      | +    | +      |     |      | +   | -    | +     |
| [New Span ID created also for non-recording Spans](specification/trace/sdk.md#sdk-span-creation) |          | +  | +    |    | +      | +    | +      |     |      |     | -    | +     |
| [IdGenerators](specification/trace/sdk.md#id-generators)                                         |          | +  | +    |    |        | +    |        |     |      |     |      | +     |
| [SpanLimits](specification/trace/sdk.md#span-limits)                                             | X        | +  | +    |    |        | +    |        |     |      |     |      | +     |
| [Built-in `SpanProcessor`s implement `ForceFlush` spec](specification/trace/sdk.md#forceflush-1) |          |    |      |    |        |      |        |     |      |     |      |       |

## Baggage

| Feature                            | Optional | Go | Java | JS | Python | Ruby | Erlang | PHP | Rust | C++ | .Net | Swift |
|------------------------------------|----------|----|------|----|--------|------|--------|-----|------|-----|------|-------|
| Basic support                      |          | +  | +    | +  | +      | +    | +      |     | +    |     | +    | +     |
| Use official header name `baggage` |          | +  | +    | +  | +      | +    | +      |     | +    |     | +    | +     |

## Metrics

|Feature                                       |Optional|Go|Java|JS |Python|Ruby|Erlang|PHP|Rust|C++|.Net|Swift|
|----------------------------------------------|--------|--|----|---|------|----|------|---|----|---|----|-----|
|TBD|

## Resource

| Feature                                                                                                                                     | Optional | Go | Java | JS | Python | Ruby | Erlang | PHP | Rust | C++ | .Net | Swift |
|---------------------------------------------------------------------------------------------------------------------------------------------|----------|----|------|----|--------|------|--------|-----|------|-----|------|-------|
| Create from Attributes                                                                                                                      |          | +  | +    | +  | +      | +    | +      |     | +    | +   | +    | +     |
| Create empty                                                                                                                                |          | +  | +    | +  | +      | +    | +      |     | +    | +   | +    | +     |
| [Merge (v2)](specification/resource/sdk.md#merge)                                                                                           |          | +  | +    |    | +      | +    | +      |     |      | +   | +    |       |
| Retrieve attributes                                                                                                                         |          | +  | +    | +  | +      | +    | +      |     | +    | +   | +    | +     |
| [Default value](specification/resource/semantic_conventions/README.md#semantic-attributes-with-sdk-provided-default-value) for service.name |          | +  | +    |    | +      | +    | +      |     |      | +   | +    |       |

## Context Propagation

| Feature                                                                          | Optional | Go | Java | JS | Python | Ruby | Erlang | PHP | Rust | C++ | .Net | Swift |
|----------------------------------------------------------------------------------|----------|----|------|----|--------|------|--------|-----|------|-----|------|-------|
| Create Context Key                                                               |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| Get value from Context                                                           |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| Set value for Context                                                            |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| Attach Context                                                                   |          | N/A| +    | +  | +      | +    | +      | +   | +    | +   | -    | -     |
| Detach Context                                                                   |          | N/A| +    | +  | +      | +    | +      | +   | +    | +   | -    | -     |
| Get current Context                                                              |          | N/A| +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| Composite Propagator                                                             |          | +  | +    | +  | +      | +    | N/A    |     | +    | +   | +    | +     |
| Global Propagator                                                                |          | +  | +    | +  | +      | +    | +      |     | +    |     | +    | +     |
| TraceContext Propagator                                                          |          | +  | +    | +  | +      | +    | +      |     | +    | +   | +    | +     |
| B3 Propagator                                                                    |          | +  | +    | +  | +      | +    | +      |     | +    | +   | +    | +     |
| Jaeger Propagator                                                                |          | +  | +    | +  | +      |      | +      |     | +    | +   | -    | -     |
| [TextMapPropagator](specification/context/api-propagators.md#textmap-propagator) |          | +  |      |    |        |      |        |     |      |     |      |       |
| Fields                                                                           |          | +  | +    | +  | +      |      | +      |     | +    |     | +    | +     |
| Setter argument                                                                  | X        | N/A| +    | +  | +      | +    | +      |     |      | +   | +    | +     |
| Getter argument                                                                  | X        | N/A| +    | +  | +      | +    | +      |     |      | +   | +    | +     |
| Getter argument returning Keys                                                   | X        | N/A| +    | +  | +      | +    | +      |     |      | +   | -    | +     |

## Environment Variables

Note: Support for environment variables is optional.

|Feature                                       |Go |Java|JS |Python|Ruby|Erlang|PHP|Rust|C++|.Net|Swift|
|----------------------------------------------|---|----|---|------|----|------|---|----|---|----|-----|
|OTEL_RESOURCE_ATTRIBUTES                      | + | +  | + | +    | +  | +    | - | +  | - | +  | -   |
|OTEL_LOG_LEVEL                                | - | -  | + | [-](https://github.com/open-telemetry/opentelemetry-python/issues/1059)    | +  | +    | - |    | - | -  | -   |        |
|OTEL_PROPAGATORS                              | - | +  |   | +    | +  | +    | - |    | - | -  | -   |
|OTEL_BSP_*                                    | - | +  |   | +    | +  | +    | - | +  | - | -  | -   |
|OTEL_EXPORTER_OTLP_*                          | [-](https://github.com/open-telemetry/opentelemetry-go/issues/1085) | +  |   | -    | +  | -    | - |    | - | -  | -   |
|OTEL_EXPORTER_JAEGER_*                        | - | +  |   | +    | +  | -    | - | +  | - | -  | -   |
|OTEL_EXPORTER_ZIPKIN_*                        | - | +  |   | +    |    | -    | - |    | - | -  | -   |
|OTEL_TRACES_EXPORTER                          | - | +  |   | +    | +  | +    |   |    |   |    |     |
|OTEL_METRICS_EXPORTER                         | - | +  |   | +    |    | -    |   |    |   | -  | -   |
|OTEL_SPAN_ATTRIBUTE_COUNT_LIMIT               | - | +  |   | +    | +  | -    |   |    |   |    |     |
|OTEL_SPAN_EVENT_COUNT_LIMIT                   | - | +  |   | +    | +  | -    |   |    |   |    |     |
|OTEL_SPAN_LINK_COUNT_LIMIT                    | - | +  |   | +    | +  | -    |   |    |   |    |     |
|OTEL_TRACES_SAMPLER                           | - | +  |   | +    | +  | +    |   |    |   |    |     |
|OTEL_TRACES_SAMPLER_ARG                       | - | +  |   | +    | +  | +    |   |    |   |    |     |

## Exporters

| Feature                                               | Optional | Go | Java                                                                  | JS | Python                                                                  | Ruby | Erlang | PHP | Rust | C++ | .Net | Swift |
|-------------------------------------------------------|----------|----|-----------------------------------------------------------------------|----|-------------------------------------------------------------------------|------|--------|-----|------|-----|------|-------|
| [Exporter interface](specification/trace/sdk.md#span-exporter)                 |          |    | + |    | +                                                                       |      |        |     |      |     | +    |       |
| [Exporter interface has `ForceFlush`](specification/trace/sdk.md#forceflush-2) |          |    | + |    |                                                                         |      |        |     |      |     |      |       |
| Standard output (logging)                             |          | +  | + | +  | +                                                                       | +    | +      | -   | +    | +   | +    | +     |
| In-memory (mock exporter)                             |          | +  | + | +  | +                                                                       | +    | +      | -   | -    | +   | +    | +     |
| [OTLP](specification/protocol/otlp.md)                |          |    |   |    |                                                                         |      |        |     |      |     |      |       |
| OTLP/gRPC Exporter                                    | *        | +  | + | +  | +                                                                       |      | +      |     | +    | +   | +    | +     |
| OTLP/HTTP binary Protobuf Exporter                    | *        | -  | - | +  | [-](https://github.com/open-telemetry/opentelemetry-python/issues/1106) | +    | +      |     |      |     | -    | -     |
| OTLP/HTTP JSON Protobuf Exporter                      | *        | -  | - | +  | [-](https://github.com/open-telemetry/opentelemetry-python/issues/1003) |      | -      |     |      |     | -    | -     |
| OTLP/HTTP gzip Content-Encoding support               | X        | -  | - | +  | +                                                                       | +    | -      |     |      |     | -    | -     |
| Concurrent sending                                    |          | -  | + | +  | [-](https://github.com/open-telemetry/opentelemetry-python/issues/1108) |      | -      |     | +    |     | -    | -     |
| Honors retryable responses with backoff               | X        | +  |   | +  | +                                                                       | +    | -      |     |      |     | -    | -     |
| Honors non-retryable responses                        | X        | +  |   | -  | +                                                                       | +    | -      |     |      |     | -    | -     |
| Honors throttling response                            | X        | +  |   | -  | +                                                                       | +    | -      |     |      |     | -    | -     |
| Multi-destination spec compliance                     | X        | -  |   |    | [-](https://github.com/open-telemetry/opentelemetry-python/issues/1109) |      | -      |     |      |     | -    | -     |
| [Zipkin](specification/trace/sdk_exporters/zipkin.md) |          |    |   |    |                                                                         |      |        |     |      |     |      |       |
| Zipkin V1 JSON                                        | X        |    | + |    | [-](https://github.com/open-telemetry/opentelemetry-python/issues/1173) |      | -      | -   | -    |     | -    | -     |
| Zipkin V1 Thrift                                      | X        |    | + |    | [-](https://github.com/open-telemetry/opentelemetry-python/issues/1174) |      | -      | -   | -    |     | -    | -     |
| Zipkin V2 JSON                                        | *        | +  | + |    | +                                                                       |      | -      | +   | +    | +   | +    | +     |
| Zipkin V2 Protobuf                                    | *        |    | + |    | +                                                                       |      | +      |     | -    |     | -    | -     |
| Service name mapping                                  |          | +  | + | +  | +                                                                       |      | +      | +   | +    |     | +    | +     |
| SpanKind mapping                                      |          | +  | + | +  | +                                                                       |      | +      | +   | +    |     | +    | +     |
| InstrumentationLibrary mapping                        |          |    | + | -  | +                                                                       |      | -      | -   | +    |     | +    | +     |
| Boolean attributes                                    |          | +  | + | +  | +                                                                       |      | +      | +   | +    |     | +    | +     |
| Array attributes                                      |          | +  | + | +  | [-](https://github.com/open-telemetry/opentelemetry-python/issues/1110) |      | +      | +   | +    |     | +    | +     |
| Status mapping                                        |          | +  | + | +  | +                                                                       |      | +      | +   | +    |     | +    | +     |
| Error Status mapping                                  |          |    | + |    |                                                                         |      |        |     |      |     | +    | -     |
| Event attributes mapping to Annotations               |          | +  | + | +  | +                                                                       |      | +      | +   | +    |     | +    | +     |
| Integer microseconds in timestamps                    |          |    | + |    | +                                                                       |      |        |     |      |     | +    | +     |
| [Jaeger](specification/trace/sdk_exporters/jaeger.md) |          |    |   |    |                                                                         |      |        |     |      |     |      |       |
| Jaeger Thrift over UDP                                | *        |    |   |    | +                                                                       | +    |        |     |      |     | +    | +     |
| Jaeger Protobuf via gRPC                              | *        |    | + |    | [-](https://github.com/open-telemetry/opentelemetry-python/issues/1437) |      |        |     |      |     | -    | -     |
| Jaeger Thrift over HTTP                               | *        |    | + |    | +                                                                       | +    |        |     |      |     | -    | -     |
| Service name mapping                                  |          |    | + |    | +                                                                       | +    |        |     |      |     | +    | +     |
| Resource to Process mapping                           |          |    | + |    | [-](https://github.com/open-telemetry/opentelemetry-python/issues/1436) | +    |        |     |      |     | +    | -     |
| InstrumentationLibrary mapping                        |          |    | + |    | +                                                                       | +    |        |     |      |     | +    | -     |
| Status mapping                                        |          |    | + |    |                                                                         | +    |        |     |      |     | +    | +     |
| Error Status mapping                                  |          |    | + |    |                                                                         | +    |        |     |      |     | +    | -     |
| Events converted to Logs                              |          |    | + |    | +                                                                       | +    |        |     |      |     | +    | +     |
| OpenCensus                                            |          |    |   |    |                                                                         |      |        |     |      |     |      |       |
| TBD                                                   |          |    |   |    |                                                                         |      |        |     |      |     |      |       |
| Prometheus                                            |          |    |   |    |                                                                         |      |        |     |      |     |      |       |
| TBD                                                   |          |    |   |    |                                                                         |      |        |     |      |     |      |       |

`*` For each type of exporter, OTLP, Zipkin, and Jaeger, implementing at least one of the supported formats is required.
Implementing more than one formats is optional.
