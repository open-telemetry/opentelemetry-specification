# Compliance of Implementations with Specification

The following tables show which features are implemented by each OpenTelemetry
language implementation.

`+` means the feature is supported, `-` means it is not supported, `N/A` means
the feature is not applicable to the particular language, blank cell means the
status of the feature is not known.

For the `Optional` column, `X` means the feature is optional, blank means the
feature is required, and columns marked with `*` mean that for each type of
exporter (OTLP and Zipkin), implementing at least one of the supported
formats is required. Implementing more than one format is optional.

## Traces

| Feature | Optional | Go | Java | JS | Python | Ruby | Erlang | PHP | Rust | C++ | .NET | Swift |
| ------- | -------- | -- | ---- | -- | ------ | ---- | ------ | --- | ---- | --- | ---- | ----- |
| [TracerProvider](specification/trace/api.md#tracerprovider-operations) | Optional | Go | Java | JS | Python | Ruby | Erlang | PHP | Rust | C++ | .NET | Swift |
| Create TracerProvider |  | + | + | + | + | + | + | + | + | + | + | + |
| Get a Tracer |  | + | + | + | + | + | + | + | + | + | + | + |
| Get a Tracer with schema_url |  | + | + | + | + |  |  | + |  | + |  |  |
| Get a Tracer with scope attributes |  | + |  |  | + |  |  | + |  | + |  |  |
| Associate Tracer with InstrumentationScope |  | + |  | + | + | + |  | + |  |  |  |  |
| Safe for concurrent calls |  | + | + | + | + | + | + | + | + | + | + | + |
| Shutdown (SDK only required) |  | + | + | + | + | + | + | + | + | + | + | + |
| ForceFlush (SDK only required) |  | + | + | + | + | + | + | + | + | + | + | + |
| [Trace / Context interaction](specification/trace/api.md#context-interaction) | Optional | Go | Java | JS | Python | Ruby | Erlang | PHP | Rust | C++ | .NET | Swift |
| Get active Span |  | N/A | + | + | + | + | + | + | + | + | + | + |
| Set active Span |  | N/A | + | + | + | + | + | + | + | + | + | + |
| [Tracer](specification/trace/api.md#tracer-operations) | Optional | Go | Java | JS | Python | Ruby | Erlang | PHP | Rust | C++ | .NET | Swift |
| Create a new Span |  | + | + | + | + | + | + | + | + | + | + | + |
| Documentation defines adding attributes at span creation as preferred |  | + |  |  | + | + |  | + |  |  | + |  |
| Get active Span |  | N/A | + | + | + | + | + | + | + | + | + | + |
| Mark Span active |  | N/A | + | + | + | + | + | + | + | + | + | + |
| Safe for concurrent calls |  | + | + | + | + | + | + | + | + | + | + | + |
| [SpanContext](specification/trace/api.md#spancontext) | Optional | Go | Java | JS | Python | Ruby | Erlang | PHP | Rust | C++ | .NET | Swift |
| IsValid |  | + | + | + | + | + | + | + | + | + | + | + |
| IsRemote |  | + | + | + | + | + | + | + | + | + | + | + |
| Conforms to the W3C TraceContext spec |  | + | + | + | + | + | + | + | + | + | + | + |
| [Span](specification/trace/api.md#span) | Optional | Go | Java | JS | Python | Ruby | Erlang | PHP | Rust | C++ | .NET | Swift |
| Create root span |  | + | + | + | + | + | + | + | + | + | + | + |
| Create with default parent (active span) |  | N/A | + | + | + | + | + | + | + | + | + | + |
| Create with parent from Context |  | + | + | + | + | + | + | + | + | + | + | + |
| No explicit parent Span/SpanContext allowed |  | + | + | + | + | + | + | + | + | + | - | + |
| SpanProcessor.OnStart receives parent Context |  | + | + | + | + | + | + | + | + | - | - | + |
| UpdateName |  | + | + | + | + | + | + | + | + | + | + | + |
| User-defined start timestamp |  | + | + | + | + | + | + | + | + | + | + | + |
| End |  | + | + | + | + | + | + | + | + | + | + | + |
| End with timestamp |  | + | + | + | + | + | + | + | + | + | + | + |
| IsRecording |  | + | + | + | + | + | + | + | + | + | + | + |
| IsRecording becomes false after End |  | + | + | + | + | + | + | + | + | + | - | + |
| Set status with StatusCode (Unset, Ok, Error) |  | + | + | + | + | + | + | + | + | + | + | + |
| Safe for concurrent calls |  | + | + | + | + | + | + | + | + | + | + | + |
| events collection size limit |  | + | + | + | + | + | + | + | + | - | - | + |
| attribute collection size limit |  | + | + | + | + | + | + | + | + | - | - | + |
| links collection size limit |  | + | + | + | + | + | + | + | + | - | - | + |
| [SpanProcessor.OnEnding](specification/trace/sdk.md#onending) | X | - | - | - | - | - | - | - | - | - | - | - |
| [Span attributes](specification/trace/api.md#set-attributes) | Optional | Go | Java | JS | Python | Ruby | Erlang | PHP | Rust | C++ | .NET | Swift |
| SetAttribute |  | + | + | + | + | + | + | + | + | + | + | + |
| Set order preserved | X | + | - | + | + | + | + | + | + | + | + | + |
| String type |  | + | + | + | + | + | + | + | + | + | + | + |
| Boolean type |  | + | + | + | + | + | + | + | + | + | + | + |
| Double floating-point type |  | + | + | + | + | + | + | - | + | + | + | + |
| Signed int64 type |  | + | + | + | + | + | + | - | + | + | + | + |
| Array of primitives (homogeneous) |  | + | + | + | + | + | + | + | + | + | + | + |
| `null` values documented as invalid/undefined |  | + | + | + | + | + | N/A | + |  | + |  | N/A |
| Unicode support for keys and string values |  | + | + | + | + | + | + | + | + | + | + | + |
| [Span linking](specification/trace/api.md#specifying-links) | Optional | Go | Java | JS | Python | Ruby | Erlang | PHP | Rust | C++ | .NET | Swift |
| Links can be recorded on span creation |  | + | + | + | + | + | + | + | + | + | + |  |
| Links can be recorded after span creation |  | + |  | + | + |  |  | + |  | + | + |  |
| Links order is preserved |  | + | + | + | + | + | + | + | + | + | + |  |
| [Span events](specification/trace/api.md#add-events) | Optional | Go | Java | JS | Python | Ruby | Erlang | PHP | Rust | C++ | .NET | Swift |
| AddEvent |  | + | + | + | + | + | + | + | + | + | + | + |
| Add order preserved |  | + | + | + | + | + | + | + | + | + | + | + |
| Safe for concurrent calls |  | + | + | + | + | + | + | + | + | + | + | + |
| [Span exceptions](specification/trace/api.md#record-exception) | Optional | Go | Java | JS | Python | Ruby | Erlang | PHP | Rust | C++ | .NET | Swift |
| RecordException |  | + | + | + | + | + | + | + | + | - | + | - |
| RecordException with extra parameters |  | + | + | + | + | + | + | + | + | - | + | - |
| [Sampling](specification/trace/sdk.md#sampling) | Optional | Go | Java | JS | Python | Ruby | Erlang | PHP | Rust | C++ | .NET | Swift |
| Allow samplers to modify tracestate |  | + | + |  | + | + | + | + | + | + | + | + |
| ShouldSample gets full parent Context |  | + | + | + | + | + | + | + | + | + | - | + |
| Sampler: JaegerRemoteSampler |  | + | + | + |  |  |  | - | + |  |  |  |
| [New Span ID created also for non-recording Spans](specification/trace/sdk.md#sdk-span-creation) |  | + | + |  | + | + | + | + | + | + | - | + |
| [IdGenerators](specification/trace/sdk.md#id-generators) |  | + | + | + | + | + | + | + | + | + |  | + |
| [SpanLimits](specification/trace/sdk.md#span-limits) | X | + | + | + | + | + | + | + |  | - |  | + |
| [Built-in `SpanProcessor`s implement `ForceFlush` spec](specification/trace/sdk.md#forceflush-1) |  | + | + | + | + | + | + | + | + | + | + |  |
| [Attribute Limits](specification/common/README.md#attribute-limits) | X | + | + | + | + | + | + | + |  |  |  |  |
| Fetch InstrumentationScope from ReadableSpan |  | + | + | + | + |  |  | + |  |  |  |  |
| [Support W3C Trace Context Level 2 randomness](specification/trace/sdk.md#traceid-randomness) | X | - |  |  |  |  |  |  |  |  |  |  |
| [TraceIdRatioBased sampler implements OpenTelemetry tracestate `th` field](specification/trace/sdk.md#traceidratiobased) | X | - |  |  |  |  |  |  |  |  |  |  |
| [CompositeSampler and built-in ComposableSamplers](specification/trace/sdk.md#compositesampler) | X | - |  |  |  |  |  |  |  |  |  |  |

## Baggage

| Feature | Optional | Go | Java | JS | Python | Ruby | Erlang | PHP | Rust | C++ | .NET | Swift |
| ------- | -------- | -- | ---- | -- | ------ | ---- | ------ | --- | ---- | --- | ---- | ----- |
| Basic support |  | + | + | + | + | + | + | + | + | + | + | + |
| Use official header name `baggage` |  | + | + | + | + | + | + | + | + | + | + | + |

## Metrics

| Feature | Optional | Go | Java | JS | Python | Ruby | Erlang | PHP | Rust | C++ | .NET | Swift |
| ------- | -------- | -- | ---- | -- | ------ | ---- | ------ | --- | ---- | --- | ---- | ----- |
| The API provides a way to set and get a global default `MeterProvider`. | X | + | + | + | + | + | + | + | + | + | - |  |
| It is possible to create any number of `MeterProvider`s. | X | + | + | + | + | + | + | + | + | + | + |  |
| `MeterProvider` provides a way to get a `Meter`. |  | + | + | + | + | + | + | + | + | + | - |  |
| `get_meter` accepts name, `version` and `schema_url`. |  | + | + | + | + |  | + | + | + | + | - |  |
| `get_meter` accepts `attributes`. |  | + |  | - | + |  |  | + | + | + |  |  |
| When an invalid `name` is specified a working `Meter` implementation is returned as a fallback. |  | + | + | + | + | + | + |  | + | + | - |  |
| The fallback `Meter` `name` property keeps its original invalid value. | X | + | - | + | + | + | + |  | + | - | - |  |
| Associate `Meter` with `InstrumentationScope`. |  | + | + | + | + | + | + |  | + | + |  |  |
| `Counter` instrument is supported. |  | + | + | + | + | + | + | + | + | + | + |  |
| `AsynchronousCounter` instrument is supported. |  | + | + | + | + | + | + | + | + | + | + |  |
| `Histogram` instrument is supported. |  | + | + | + | + | + | + | + | + | + | + |  |
| `AsynchronousGauge` instrument is supported. |  | + | + | + | + | + | + | + | + | + | + |  |
| `Gauge` instrument is supported. |  | + | - | + | + | + | - | + | + | - | - |  |
| `UpDownCounter` instrument is supported. |  | + | + | + | + | + | + | + | + | + | + |  |
| `AsynchronousUpDownCounter` instrument is supported. |  | + | + | + | + | + | + | + | + | + | + |  |
| Instruments have `name` |  | + | + | + | + | + | + | + | + | + | + |  |
| Instruments have kind. |  | + | + | + | + | + | + | + | + | + | + |  |
| Instruments have an optional unit of measure. |  | + | + | + | + | + | + | + | + | + | + |  |
| Instruments have an optional description. |  | + | + | + | + | + | + | + | + | + | + |  |
| A valid instrument MUST be created and warning SHOULD be emitted when multiple instruments are registered under the same `Meter` using the same `name`. |  | + | + | + | + | + | + |  |  |  |  |  |
| Duplicate instrument registration name conflicts are resolved by using the first-seen for the stream name. |  |  | + |  |  | - | + |  |  |  |  |  |
| It is possible to register two instruments with same `name` under different `Meter`s. |  | + | + | + | + |  | + |  | + | + | + |  |
| Instrument names conform to the specified syntax. |  | + | + | + | + | + | + |  |  | + |  |  |
| Instrument units conform to the specified syntax. |  | - | + |  | + | + | - |  | + | + | + |  |
| Instrument descriptions conform to the specified syntax. |  | - | + |  | - | + | - |  |  | - | + |  |
| Instrument supports the advisory ExplicitBucketBoundaries parameter. |  | + | + |  |  |  | + |  |  |  |  |  |
| Instrument supports the advisory Attributes parameter. |  | - | + |  |  |  | - |  |  |  |  |  |
| All methods of `MeterProvider` are safe to be called concurrently. |  | + | + | + | - |  | + |  |  | + | + |  |
| All methods of `Meter` are safe to be called concurrently. |  | + | + | + | - |  | + |  |  | + | + |  |
| All methods of any instrument are safe to be called concurrently. |  | + | + | + | - |  | + |  |  | + | + |  |
| `MeterProvider` allows a `Resource` to be specified. |  | + | + | + | + | + |  | + | + | + | + |  |
| A specified `Resource` can be associated with all the produced metrics from any `Meter` from the `MeterProvider`. |  | + | + | + | + | + |  | + | + | + | + |  |
| The supplied `name`, `version` and `schema_url` arguments passed to the `MeterProvider` are used to create an `InstrumentationLibrary` instance stored in the `Meter`. |  | + | - |  | + |  |  |  | + | + | - |  |
| The supplied `name`, `version` and `schema_url` arguments passed to the `MeterProvider` are used to create an `InstrumentationScope` instance stored in the `Meter`. |  | + | + | + | + |  | + | + | + | + |  |  |
| Configuration is managed solely by the `MeterProvider`. |  | + | + | + | + |  | + | + | + | + | + |  |
| The `MeterProvider` provides methods to update the configuration | X | - | - | - | + |  | - |  |  | - | + |  |
| The updated configuration applies to all already returned `Meter`s. | if above | - | - | - | - |  | - |  |  | - | + |  |
| There is a way to register `View`s with a `MeterProvider`. |  | + | + | + | + | + | + | + | + | + | + |  |
| The `View` instrument selection criteria is as specified. |  | + | + | + | + | + | + | + | + | + | + |  |
| The `View` instrument selection criteria supports wildcards. | X | + | + | + | + | + | - |  | + | + | + |  |
| The `View` instrument selection criteria supports the match-all wildcard. |  | + | + | + | + | + | + |  | + | + | + |  |
| The name of the `View` can be specified. |  | - | + | + | + | + | + | + |  | + | + |  |
| The `View` allows configuring the name, description, attributes keys and aggregation of the resulting metric stream. |  | + | + | + | + |  | + | + | + | + | - |  |
| The `View` allows configuring excluded attribute keys of resulting metric stream. |  | + |  | + |  |  |  |  |  |  |  |  |
| The `View` allows configuring the exemplar reservoir of resulting metric stream. | X | + | - | - | - |  | - |  |  |  | - |  |
| The SDK allows more than one `View` to be specified per instrument. | X | + | + | + | + | + | + |  | + | + | + |  |
| The `Drop` aggregation is available. |  | + | + | + | + | + | + |  | + | + | + |  |
| The `Default` aggregation is available. |  | + | + | + | + | + | + |  | + | + | + |  |
| The `Default` aggregation uses the specified aggregation by instrument. |  | + | + | + | + | + | + |  | + | + | + |  |
| The `Sum` aggregation is available. |  | + | + | + | + | + | + | + | + | + | + |  |
| The `LastValue` aggregation is available. |  | + | + | + | + | + | + | + | + | + | + |  |
| The `ExplicitBucketHistogram` aggregation is available. |  | + | + | + | + | + | + | + | + | + | + |  |
| The `ExponentialBucketHistogram` aggregation is available. |  | + |  | + | + | + |  |  |  |  | + |  |
| The metrics Reader implementation supports registering metric Exporters |  | + | + | + | + | + | + | + | + | + | + |  |
| The metrics Reader implementation supports configuring the default aggregation on the basis of instrument kind. |  | + | + | + | + | + | + |  |  | - | - |  |
| The metrics Reader implementation supports configuring the default temporality on the basis of instrument kind. |  | + | + | + | + | + | + |  | + | + |  |  |
| The metrics Exporter has access to the aggregated metrics data (aggregated points, not raw measurements). |  | + | + | + | + | + | + |  | + | + | + |  |
| The metrics Exporter `export` function can not be called concurrently from the same Exporter instance. |  | + | + | + | - | + | + |  |  | + | + |  |
| The metrics Exporter `export` function does not block indefinitely. |  | + | + | + | - | + | + |  |  | + | + |  |
| The metrics Exporter `export` function receives a batch of metrics. |  | + | + | + | + | + | + | + | + | + | + |  |
| The metrics Exporter `export` function returns `Success` or `Failure`. |  | + | + | + | + | + | + | + | + | + | + |  |
| The metrics Exporter provides a `ForceFlush` function. |  | + | + | + | + | + | + | + | + | + | + |  |
| The metrics Exporter `ForceFlush` can inform the caller whether it succeeded, failed or timed out. |  | + | + | + | + | + | + | + |  | + | + |  |
| The metrics Exporter provides a `shutdown` function. |  | + | + | + | + | + | + | + | + | + | + |  |
| The metrics Exporter `shutdown` function do not block indefinitely. |  | + | + | + | - |  | + |  |  | + | + |  |
| The metrics SDK samples `Exemplar`s from measurements. |  | + | + | - | - |  | + |  |  |  | + |  |
| Exemplar sampling can be disabled. |  | + | - | - | - |  | + |  |  |  | + |  |
| The metrics SDK supports SDK-wide exemplar filter configuration |  | + | + | - | - |  | + |  |  |  | + |  |
| The metrics SDK supports `TraceBased` exemplar filter |  | + | + | - | - |  | + |  |  |  | + |  |
| The metrics SDK supports `AlwaysOn` exemplar filter |  | + | + | - | - |  | + |  |  |  | + |  |
| The metrics SDK supports `AlwaysOff` exemplar filter |  | + | + | - | - |  | + |  |  |  | + |  |
| Exemplars retain any attributes available in the measurement that are not preserved by aggregation or view configuration. |  | + | + | - | - |  | + |  |  |  | + |  |
| Exemplars contain the associated trace id and span id of the active span in the Context when the measurement was taken. |  | + | + | - | - |  | + |  |  |  | + |  |
| Exemplars contain the timestamp when the measurement was taken. |  | + | + | - | - |  | + |  |  |  | + |  |
| The metrics SDK provides an `ExemplarReservoir` interface or extension point. |  | + | - | - | - |  | + | + |  |  | - |  |
| An `ExemplarReservoir` has an `offer` method with access to the measurement value, attributes, `Context` and timestamp. |  | + | - | - | - |  | + | + |  |  | - |  |
| The metrics SDK provides a `SimpleFixedSizeExemplarReservoir` that is used by default for all aggregations except `ExplicitBucketHistogram`. |  | + | + | - | - |  | + | + |  |  | - |  |
| The metrics SDK provides an `AlignedHistogramBucketExemplarReservoir` that is used by default for `ExplicitBucketHistogram` aggregation. |  | + | + | - | - |  | + |  |  |  | - |  |
| A metric Producer accepts an optional metric Filter |  | - |  |  |  |  | - |  |  |  |  |  |
| The metric Reader implementation supports registering metric Filter and passing them  its registered metric Producers |  | - |  |  |  |  | - |  |  |  |  |  |
| The metric SDK's metric Producer implementations uses the metric Filter |  | - |  |  |  |  | - |  |  |  |  |  |
| Metric SDK implements [cardinality limit](./specification/metrics/sdk.md#cardinality-limits) |  | + | + | + | - |  |  |  | - | + | + |  |
| Metric SDK supports configuring cardinality limit at MeterReader level |  | - | + | + | - |  |  |  | - | - | - |  |
| Metric SDK supports configuring cardinality limit per metric (using Views) |  | - | + | + | - |  |  |  | - | - | + |  |

## Logs

Features for the [Logging SDK](specification/logs/sdk.md).
Disclaimer: this list of features is still a work in progress, please refer to the specification if in any doubt.

| Feature | Optional | Go | Java | JS | Python | Ruby | Erlang | PHP | Rust | C++ | .NET | Swift |
| ------- | -------- | -- | ---- | -- | ------ | ---- | ------ | --- | ---- | --- | ---- | ----- |
| LoggerProvider.Get Logger |  | + | + | + | + | + |  | + |  | + | - |  |
| LoggerProvider.Get Logger accepts attributes |  | + |  |  | + |  |  | + |  | + |  |  |
| LoggerProvider.Shutdown |  | + | + | + | + | + |  | + |  | + | - |  |
| LoggerProvider.ForceFlush |  | + | + | + | + | + |  | + |  | + | - |  |
| Logger.Emit(LogRecord) |  | + | + | + | + | + |  | + |  | + | - |  |
| LogRecord.Set EventName |  | + |  |  |  |  |  |  | + | + |  |  |
| Logger.Enabled | X | + |  |  |  |  |  | + | + | + |  |  |
| SimpleLogRecordProcessor |  | + | + | + | + | + |  | + |  | + |  |  |
| BatchLogRecordProcessor |  | + | + | + | + | + |  | + |  | + |  |  |
| Can plug custom LogRecordProcessor |  | + | + | + | + | + |  | + |  | + |  |  |
| LogRecordProcessor.Enabled | X | + |  |  |  | + |  |  | + |  |  |  |
| OTLP/gRPC exporter |  | + | + | + | + |  |  | + |  | + | + |  |
| OTLP/HTTP exporter |  | + | + | + | + | + |  | + |  | + | + |  |
| OTLP File exporter |  | - | - |  | - |  |  |  |  | + | - |  |
| Can plug custom LogRecordExporter |  | + | + | + | + | + |  | + |  | + |  |  |
| Trace Context Injection |  | + | + |  | + | + |  | + |  | + | + |  |

## Resource

| Feature | Optional | Go | Java | JS | Python | Ruby | Erlang | PHP | Rust | C++ | .NET | Swift |
| ------- | -------- | -- | ---- | -- | ------ | ---- | ------ | --- | ---- | --- | ---- | ----- |
| Create from Attributes |  | + | + | + | + | + | + | + | + | + | + | + |
| Create empty |  | + | + | + | + | + | + | + | + | + | + | + |
| [Merge (v2)](specification/resource/sdk.md#merge) |  | + | + |  | + | + | + | + | + | + | + |  |
| Retrieve attributes |  | + | + | + | + | + | + | + | + | + | + | + |
| [Default value](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/resource/README.md#semantic-attributes-with-dedicated-environment-variable) for service.name |  | + | + |  | + | + | + | + |  | + | + |  |
| [Resource detector](specification/resource/sdk.md#detecting-resource-information-from-the-environment) interface/mechanism |  | + | + | + | + | + | + | + | + | + | + | + |
| [Resource detectors populate Schema URL](specification/resource/sdk.md#detecting-resource-information-from-the-environment) |  | + | + |  |  |  | - | + |  |  | - |  |

## Context Propagation

| Feature | Optional | Go | Java | JS | Python | Ruby | Erlang | PHP | Rust | C++ | .NET | Swift |
| ------- | -------- | -- | ---- | -- | ------ | ---- | ------ | --- | ---- | --- | ---- | ----- |
| Create Context Key |  | + | + | + | + | + | + | + | + | + | + | + |
| Get value from Context |  | + | + | + | + | + | + | + | + | + | + | + |
| Set value for Context |  | + | + | + | + | + | + | + | + | + | + | + |
| Attach Context |  | N/A | + | + | + | + | + | + | + | + | - | - |
| Detach Context |  | N/A | + | + | + | + | + | + | + | + | - | - |
| Get current Context |  | N/A | + | + | + | + | + | + | + | + | + | + |
| Composite Propagator |  | + | + | + | + | + | + | + | + | + | + | + |
| Global Propagator |  | + | + | + | + | + | + | + | + | + | + | + |
| TraceContext Propagator |  | + | + | + | + | + | + | + | + | + | + | + |
| B3 Propagator |  | + | + | + | + | + | + | + | + | + | + | + |
| Jaeger Propagator |  | + | + | + | + | + | + | + | + | + | - | + |
| OT Propagator |  | + | + | + | + |  |  |  |  |  |  |  |
| OpenCensus Binary Propagator |  | + |  |  |  |  |  |  |  |  |  |  |
| [TextMapPropagator](specification/context/api-propagators.md#textmap-propagator) |  | + | + |  | + | + |  | + |  | + |  |  |
| Fields |  | + | + | + | + | + | + | + | + | + | + | + |
| Setter argument | X | N/A | + | + | + | + | + | + | N/A | + | + | + |
| Getter argument | X | N/A | + | + | + | + | + | + | N/A | + | + | + |
| Getter argument returning Keys | X | N/A | + | + | + | + | + | + | N/A | + | - | + |

## Environment Variables

Note: Support for environment variables is optional.

| Feature | Go | Java | JS | Python | Ruby | Erlang | PHP | Rust | C++ | .NET | Swift |
| ------- | -- | ---- | -- | ------ | ---- | ------ | --- | ---- | --- | ---- | ----- |
| OTEL_SDK_DISABLED | - | + | - | + | + | - | + | - | - | - | - |
| OTEL_RESOURCE_ATTRIBUTES | + | + | + | + | + | + | + | + | + | + | - |
| OTEL_SERVICE_NAME | + | + | + | + | + | + | + |  | + | + |  |
| OTEL_LOG_LEVEL | - | - | + | [-][py1059] | + | - | + |  | - | - | - |
| OTEL_PROPAGATORS | - | + |  | + | + | + | + | - | - | - | - |
| OTEL_BSP_* | + | + | + | + | + | + | + | + | - | + | - |
| OTEL_BLRP_* | + | + |  |  | + |  | + | + | - | + |  |
| OTEL_EXPORTER_OTLP_* | + | + |  | + | + | + | + | + | + | + | - |
| OTEL_EXPORTER_ZIPKIN_* | + | + |  | + | + | - | + | - | - | + | - |
| OTEL_TRACES_EXPORTER | - | + | + | + | + | + | + | - | - | - |  |
| OTEL_METRICS_EXPORTER | - | + |  | + | + | - | + | - | - | - | - |
| OTEL_LOGS_EXPORTER | - | + |  | + | + |  | + |  | - | - |  |
| OTEL_SPAN_ATTRIBUTE_COUNT_LIMIT | + | + | + | + | + | + | + | + | - | + |  |
| OTEL_SPAN_ATTRIBUTE_VALUE_LENGTH_LIMIT | + | + | + | + | + | + | + |  | - | + |  |
| OTEL_SPAN_EVENT_COUNT_LIMIT | + | + | + | + | + | + | + | + | - | + |  |
| OTEL_SPAN_LINK_COUNT_LIMIT | + | + | + | + | + | + | + | + | - | + |  |
| OTEL_EVENT_ATTRIBUTE_COUNT_LIMIT | + | - |  | + | + | + | + |  | - | + |  |
| OTEL_LINK_ATTRIBUTE_COUNT_LIMIT | + | - |  | + | + | + | + |  | - | + |  |
| OTEL_LOGRECORD_ATTRIBUTE_COUNT_LIMIT | + |  |  |  | + |  | + |  | - |  |  |
| OTEL_LOGRECORD_ATTRIBUTE_VALUE_LENGTH_LIMIT | + |  |  |  | + |  | + |  | - |  |  |
| OTEL_TRACES_SAMPLER | + | + | + | + | + | + | + | - | - | - |  |
| OTEL_TRACES_SAMPLER_ARG | + | + | + | + | + | + | + | - | - | - |  |
| OTEL_ATTRIBUTE_VALUE_LENGTH_LIMIT | + | + | + | + | + | - | + |  | - | + |  |
| OTEL_ATTRIBUTE_COUNT_LIMIT | + | + | + | + | + | - | + |  | - | + |  |
| OTEL_METRIC_EXPORT_INTERVAL | + | + |  | + | + |  | + |  | - | + |  |
| OTEL_METRIC_EXPORT_TIMEOUT | + | - |  | + | + |  | + |  | - | + |  |
| OTEL_METRICS_EXEMPLAR_FILTER | + | + |  |  | + |  | + |  | - | + |  |
| OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE | + | + | + | + | + |  | + |  | - | + |  |
| OTEL_EXPORTER_OTLP_METRICS_DEFAULT_HISTOGRAM_AGGREGATION | + | + |  | + | + |  |  |  | - |  |  |
| OTEL_EXPERIMENTAL_CONFIG_FILE | - |  |  |  |  |  | + |  | - |  |  |

## Declarative configuration

See [declarative configuration](./specification/configuration/README.md#declarative-configuration)
for details.
Disclaimer: Declarative configuration is currently in Development status - work in progress.

| Feature | Go | Java | JS | Python | Ruby | Erlang | PHP | Rust | C++ | .NET | Swift |
| ------- | -- | ---- | -- | ------ | ---- | ------ | --- | ---- | --- | ---- | ----- |
| `Parse` a configuration file | + | + | + |  |  |  | + |  | + |  |  |
| The `Parse` operation accepts the configuration YAML file format | + | + | + |  |  |  | + |  | + |  |  |
| The `Parse` operation performs environment variable substitution | + | + |  |  |  |  | + |  | + |  |  |
| The `Parse` operation returns configuration model | + | + | + |  |  |  | + |  | + |  |  |
| The `Parse` operation resolves extension component configuration to `properties` |  | + |  |  |  |  | + |  | + |  |  |
| `Create` SDK components | + | + |  |  |  |  | + |  | + |  |  |
| The `Create` operation accepts configuration model | + | + |  |  |  |  | + |  | + |  |  |
| The `Create` operation returns `TracerProvider` | + | + |  |  |  |  | + |  | + |  |  |
| The `Create` operation returns `MeterProvider` | + | + |  |  |  |  | + |  | + |  |  |
| The `Create` operation returns `LoggerProvider` | + | + |  |  |  |  | + |  | + |  |  |
| The `Create` operation returns `Propagators` |  | + |  |  |  |  | + |  | + |  |  |
| The `Create` operation calls `CreatePlugin` of corresponding `ComponentProvider` when encountering extension components |  | + |  |  |  |  | + |  | + |  |  |
| Register a `ComponentProvider` |  | + |  |  |  |  | + |  | + |  |  |

## Exporters

| Feature | Optional | Go | Java | JS | Python | Ruby | Erlang | PHP | Rust | C++ | .NET | Swift |
| ------- | -------- | -- | ---- | -- | ------ | ---- | ------ | --- | ---- | --- | ---- | ----- |
| [Exporter interface](specification/trace/sdk.md#span-exporter) |  | + | + |  | + | + | + | + | + | + | + |  |
| [Exporter interface has `ForceFlush`](specification/trace/sdk.md#forceflush-2) |  | + | + |  | + | + | + | + | - |  | + |  |
| Standard output (logging) |  | + | + | + | + | + | + | + | + | + | + | + |
| In-memory (mock exporter) |  | + | + | + | + | + | + | + | - | + | + | + |
| **[OTLP](specification/protocol/otlp.md)** | Optional | Go | Java | JS | Python | Ruby | Erlang | PHP | Rust | C++ | .NET | Swift |
| OTLP/gRPC Exporter | * | + | + | + | + |  | + | + | + | + | + | + |
| OTLP/HTTP binary Protobuf Exporter | * | + | + | + | + | + | + | + | + | + | + | - |
| OTLP/HTTP JSON Protobuf Exporter |  | + | - | + | [-][py1003] |  | - | + |  | + | - | - |
| OTLP/HTTP gzip Content-Encoding support | X | + | + | + | + | + | - | + |  | - | - | - |
| Concurrent sending |  | + | + | + | [-][py1108] |  | - | - | + | - | - | - |
| Honors retryable responses with backoff | X | + | - | + | + | + | - | + |  | - | - | - |
| Honors non-retryable responses | X | + | - | - | + | + | - | + |  | - | - | - |
| Honors throttling response | X | + | - | - | + | + | - |  |  | - | - | - |
| Multi-destination spec compliance | X | + | - |  | [-][py1109] |  | - |  |  | - | - | - |
| SchemaURL in ResourceSpans and ScopeSpans |  | + | + |  | + |  | + | + |  |  | - |  |
| SchemaURL in ResourceMetrics and ScopeMetrics |  | + | + |  | + |  | - | + |  |  | - |  |
| SchemaURL in ResourceLogs and ScopeLogs |  | + | + |  | + |  | - | + |  |  | - |  |
| Honors the [user agent spec](specification/protocol/exporter.md#user-agent) |  | + |  |  |  |  |  | + |  |  | + |  |
| [Partial Success](https://github.com/open-telemetry/opentelemetry-proto/blob/main/docs/specification.md#partial-success) messages are handled and logged for OTLP/gRPC | X | + |  |  |  |  |  | + |  |  |  |  |
| [Partial Success](https://github.com/open-telemetry/opentelemetry-proto/blob/main/docs/specification.md#partial-success-1) messages are handled and logged for OTLP/HTTP | X | + |  |  |  |  |  | + |  |  |  |  |
| Metric Exporter configurable temporality preference |  | + | + |  | + |  |  | + |  |  |  |  |
| Metric Exporter configurable default aggregation |  | + | + |  | + |  |  |  |  |  |  |  |
| **[Zipkin](specification/trace/sdk_exporters/zipkin.md)** | Optional | Go | Java | JS | Python | Ruby | Erlang | PHP | Rust | C++ | .NET | Swift |
| Zipkin V1 JSON | X | - | + |  | + | - | - | - | - | - | - | - |
| Zipkin V1 Thrift | X | - | + |  | [-][py1174] | - | - | - | - | - | - | - |
| Zipkin V2 JSON | * | + | + |  | + | + | - | + | + | + | + | + |
| Zipkin V2 Protobuf | * | - | + |  | + | - | + | - | - | - | - | - |
| Service name mapping |  | + | + | + | + | + | + | + | + | + | + | + |
| SpanKind mapping |  | + | + | + | + | + | + | + | + | + | + | + |
| InstrumentationLibrary mapping |  | + | + | - | + | + | - | + | + | + | + | + |
| InstrumentationScope mapping |  |  | + |  |  |  |  |  |  |  |  |  |
| Boolean attributes |  | + | + | + | + | + | + | + | + | + | + | + |
| Array attributes |  | + | + | + | + | + | + | + | + | + | + | + |
| Status mapping |  | + | + | + | + | + | + | + | + | + | + | + |
| Error Status mapping |  | + | + |  | + | + | - | + | + | + | + | - |
| Event attributes mapping to Annotations |  | + | + | + | + | + | + | + | + | + | + | + |
| Integer microseconds in timestamps |  | N/A | + |  | + | + | - | + | + | + | + | + |
| **Prometheus** | Optional | Go | Java | JS | Python | Ruby | Erlang | PHP | Rust | C++ | .NET | Swift |
| [Metadata Deduplication](specification/compatibility/prometheus_and_openmetrics.md#metric-metadata-1) |  | + | + | - | - | - | - | - | + | - | - | - |
| [Name Sanitization](specification/compatibility/prometheus_and_openmetrics.md#metric-metadata-1) |  | + | + | + | + | - | - | - | + | + | + | + |
| [UNIT Metadata](specification/compatibility/prometheus_and_openmetrics.md#metric-metadata-1) | X | - | - | + | + | - | - | - | - | - | + | - |
| [Unit Suffixes](specification/compatibility/prometheus_and_openmetrics.md#metric-metadata-1) | X | + | + | - | + | - | - | - | + | + | + | - |
| [Unit Full Words](specification/compatibility/prometheus_and_openmetrics.md#metric-metadata-1) | X | + | + | - | - | - | - | - | + | - | - | - |
| [HELP Metadata](specification/compatibility/prometheus_and_openmetrics.md#metric-metadata-1) |  | + | + | + | + | - | - | - | + | + | + | + |
| [TYPE Metadata](specification/compatibility/prometheus_and_openmetrics.md#metric-metadata-1) |  | + | + | + | + | - | - | - | + | + | + | + |
| [otel_scope_name and otel_scope_version labels on all Metrics](specification/compatibility/prometheus_and_openmetrics.md#instrumentation-scope-1) |  | + | + | - | - | - | - | - | + | - | - | - |
| [otel_scope_[attribute] labels on all Metrics](specification/compatibility/prometheus_and_openmetrics.md#instrumentation-scope-1) |  | + | - | - | - | - | - | - | - | - | - | - |
| [otel_scope labels can be disabled](specification/compatibility/prometheus_and_openmetrics.md#instrumentation-scope-1) | X | + | - | - | - | - | - | - | + | - | - | - |
| [Gauges become Prometheus Gauges](specification/compatibility/prometheus_and_openmetrics.md#gauges-1) |  | + | + | + | + | - | - | - | + | + | + | - |
| [Cumulative Monotonic Sums become Prometheus Counters](specification/compatibility/prometheus_and_openmetrics.md#sums) |  | + | + | + | + | - | - | - | + | + | + | + |
| [Prometheus Counters have _total suffix by default](specification/compatibility/prometheus_and_openmetrics.md#sums) |  | + | + | + | + | - | - | - | + | - | - | - |
| [Prometheus Counters _total suffixing can be disabled](specification/compatibility/prometheus_and_openmetrics.md#sums) | X | + | - | - | - | - | - | - | - | - | - | - |
| [Cumulative Non-Monotonic Sums become Prometheus Gauges](specification/compatibility/prometheus_and_openmetrics.md#sums) |  | + | + | + | + | - | - | - | + | + | + | - |
| [Delta Non-Monotonic Sums become Cumulative Prometheus Counters](specification/compatibility/prometheus_and_openmetrics.md#sums) | X | - | - | - | - | - | - | - | - | - | - | - |
| [Cumulative Histograms become Prometheus Histograms](specification/compatibility/prometheus_and_openmetrics.md#histograms-1) |  | + | + | + | + | - | - | - | + | + | + | + |
| [Delta Histograms become Cumulative Prometheus Histograms](specification/compatibility/prometheus_and_openmetrics.md#histograms-1) | X | - | - | - | - | - | - | - | - | - | - | - |
| [Attributes Keys are Sanitized](specification/compatibility/prometheus_and_openmetrics.md#metric-attributes) |  | + | + | + | + | - | - | - | + | + | + | + |
| [Colliding sanitized attribute keys are merged](specification/compatibility/prometheus_and_openmetrics.md#metric-attributes) |  | + | + | - | - | - | - | - | + | - | - | - |
| [Exemplars for Histograms and Monotonic sums](specification/compatibility/prometheus_and_openmetrics.md#exemplars-1) | X | + | - | - | - | - | - | - | - | - | - | - |
| [`target_info` metric from Resource](specification/compatibility/prometheus_and_openmetrics.md#resource-attributes-1) | X | + | + | + | + | - | - | - | + | - | - | - |

## OpenCensus Compatibility

Languages not covered by the OpenCensus project, or that did not reach Alpha, are not listed here.

| Feature | Go | Java | JS | Python | C++ | .NET | Erlang |
| ------- | -- | ---- | -- | ------ | --- | ---- | ------ |
| [Trace Bridge](specification/compatibility/opencensus.md#trace-bridge) | + | + | + | + | - | - | - |
| [Metric Bridge](specification/compatibility/opencensus.md#metrics--stats) | + | + | - | - | - | - | - |

## OpenTracing Compatibility

Languages not covered by the OpenTracing project do not need to be listed here, e.g. Erlang.

| Feature | Go | Java | JS | Python | Ruby | PHP | Rust | C++ | .NET | Swift |
| ------- | -- | ---- | -- | ------ | ---- | --- | ---- | --- | ---- | ----- |
| [Create OpenTracing Shim](specification/compatibility/opentracing.md#create-an-opentracing-tracer-shim) |  |  |  |  |  | + |  |  |  |  |
| [Tracer](specification/compatibility/opentracing.md#tracer-shim) |  |  |  |  |  | + |  |  |  |  |
| [Span](specification/compatibility/opentracing.md#span-shim) |  |  |  |  |  | + |  |  |  |  |
| [SpanContext](specification/compatibility/opentracing.md#spancontext-shim) |  |  |  |  |  | + |  |  |  |  |
| [ScopeManager](specification/compatibility/opentracing.md#scopemanager-shim) |  |  |  |  |  | + |  |  |  |  |
| Error mapping for attributes/events |  |  |  |  |  | + |  |  |  |  |
| Migration to OpenTelemetry guide |  |  |  |  |  |  |  |  |  |  |

[py1003]: https://github.com/open-telemetry/opentelemetry-python/issues/1003
[py1059]: https://github.com/open-telemetry/opentelemetry-python/issues/1059
[py1108]: https://github.com/open-telemetry/opentelemetry-python/issues/1108
[py1109]: https://github.com/open-telemetry/opentelemetry-python/issues/1109
[py1174]: https://github.com/open-telemetry/opentelemetry-python/issues/1174
[py1779]: https://github.com/open-telemetry/opentelemetry-python/issues/1779
[php225]: https://github.com/open-telemetry/opentelemetry-php/issues/225
