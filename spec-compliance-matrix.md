# Compliance of Implementations with Specification

The following tables show which features are implemented by each OpenTelemetry
language implementation.

`+` means the feature is supported, `-` means it is not supported, `N/A` means
the feature is not applicable to the particular language, blank cell means the
status of the feature is not known.

For the `Optional` column, `X` means the feature is optional, blank means the
feature is required, and columns marked with `*` mean that for each type of
exporter (OTLP, Zipkin, and Jaeger), implementing at least one of the supported
formats is required. Implementing more than one format is optional.

## Traces

| Feature                                                                                          | Optional | Go  | Java | JS  | Python | Ruby | Erlang | PHP | Rust | C++ | .NET | Swift |
|--------------------------------------------------------------------------------------------------|----------|-----|------|-----|--------|------|--------|-----|------|-----|------|-------|
| [TracerProvider](specification/trace/api.md#tracerprovider-operations)                           |          |     |      |     |        |      |        |     |      |     |      |       |
| Create TracerProvider                                                                            |          | +   | +    | +   | +      | +    | +      | +   | +    | +   | +    | +     |
| Get a Tracer                                                                                     |          | +   | +    | +   | +      | +    | +      | +   | +    | +   | +    | +     |
| Get a Tracer with schema_url                                                                     |          | +   | +    |     |        |      |        |     |      | +   |      |       |
| Safe for concurrent calls                                                                        |          | +   | +    | +   | +      | +    | +      | +   | +    | +   | +    | +     |
| Shutdown (SDK only required)                                                                     |          | +   | +    | +   | +      | +    | +      | +   | +    | +   | +    | +     |
| ForceFlush (SDK only required)                                                                   |          | +   | +    | -   | +      | +    | +      | +   | +    | +   | +    | +     |
| [Trace / Context interaction](specification/trace/api.md#context-interaction)                    |          |     |      |     |        |      |        |     |      |     |      |       |
| Get active Span                                                                                  |          | N/A | +    | +   | +      | +    | +      | +   | +    | +   | +    | +     |
| Set active Span                                                                                  |          | N/A | +    | +   | +      | +    | +      | +   | +    | +   | +    | +     |
| [Tracer](specification/trace/api.md#tracer-operations)                                           |          |     |      |     |        |      |        |     |      |     |      |       |
| Create a new Span                                                                                |          | +   | +    | +   | +      | +    | +      | +   | +    | +   | +    | +     |
| Get active Span                                                                                  |          | N/A | +    | +   | +      | +    | +      | +   | +    | +   | +    | +     |
| Mark Span active                                                                                 |          | N/A | +    | +   | +      | +    | +      | +   | +    | +   | +    | +     |
| Safe for concurrent calls                                                                        |          | +   | +    | +   | +      | +    | +      | +   | +    | +   | +    | +     |
| [SpanContext](specification/trace/api.md#spancontext)                                            |          |     |      |     |        |      |        |     |      |     |      |       |
| IsValid                                                                                          |          | +   | +    | +   | +      | +    | +      | +   | +    | +   | +    | +     |
| IsRemote                                                                                         |          | +   | +    | +   | +      | +    | +      | +   | +    | +   | +    | +     |
| Conforms to the W3C TraceContext spec                                                            |          | +   | +    | +   | +      | +    | +      | +   | +    | +   | +    | +     |
| [Span](specification/trace/api.md#span)                                                          |          |     |      |     |        |      |        |     |      |     |      |       |
| Create root span                                                                                 |          | +   | +    | +   | +      | +    | +      | +   | +    | +   | +    | +     |
| Create with default parent (active span)                                                         |          | N/A | +    | +   | +      | +    | +      | +   | +    | +   | +    | +     |
| Create with parent from Context                                                                  |          | +   | +    | +   | +      | +    | +      | +   | +    | +   | +    | +     |
| No explicit parent Span/SpanContext allowed                                                      |          | +   | +    | +   | +      | +    | +      |     | +    | +   | -    | +     |
| SpanProcessor.OnStart receives parent Context                                                    |          | +   | +    | +   | +      | +    | +      | +   | +    | -   | -    | +     |
| UpdateName                                                                                       |          | +   | +    | +   | +      | +    | +      | +   | +    | +   | +    | +     |
| User-defined start timestamp                                                                     |          | +   | +    | +   | +      | +    | +      | +   | +    | +   | +    | +     |
| End                                                                                              |          | +   | +    | +   | +      | +    | +      | +   | +    | +   | +    | +     |
| End with timestamp                                                                               |          | +   | +    | +   | +      | +    | +      | +   | +    | +   | +    | +     |
| IsRecording                                                                                      |          | +   | +    | +   | +      | +    | +      | +   | +    | +   | +    | +     |
| IsRecording becomes false after End                                                              |          | +   | +    | +   | +      | +    | +      | +   | +    | +   | -    | +     |
| Set status with StatusCode (Unset, Ok, Error)                                                    |          | +   | +    | +   | +      | +    | +      | +   | +    | +   | +    | +     |
| Safe for concurrent calls                                                                        |          | +   | +    | +   | +      | +    | +      | +   | +    | +   | +    | +     |
| events collection size limit                                                                     |          | +   | +    | +   | +      | +    | +      | +   | +    | -   | -    | +     |
| attribute collection size limit                                                                  |          | +   | +    | +   | +      | +    | +      | +   | +    | -   | -    | +     |
| links collection size limit                                                                      |          | +   | +    | +   | +      | +    | +      | +   | +    | -   | -    | +     |
| [Span attributes](specification/trace/api.md#set-attributes)                                     |          |     |      |     |        |      |        |     |      |     |      |       |
| SetAttribute                                                                                     |          | +   | +    | +   | +      | +    | +      | +   | +    | +   | +    | +     |
| Set order preserved                                                                              | X        | +   | -    | +   | +      | +    | +      | +   | +    | +   | +    | +     |
| String type                                                                                      |          | +   | +    | +   | +      | +    | +      | +   | +    | +   | +    | +     |
| Boolean type                                                                                     |          | +   | +    | +   | +      | +    | +      | +   | +    | +   | +    | +     |
| Double floating-point type                                                                       |          | +   | +    | +   | +      | +    | +      | -   | +    | +   | +    | +     |
| Signed int64 type                                                                                |          | +   | +    | +   | +      | +    | +      | -   | +    | +   | +    | +     |
| Array of primitives (homogeneous)                                                                |          | +   | +    | +   | +      | +    | +      | +   | +    | +   | +    | +     |
| `null` values documented as invalid/undefined                                                    |          | +   | +    | +   | +      | +    | N/A    | +   |      | +   |      | N/A   |
| Unicode support for keys and string values                                                       |          | +   | +    | +   | +      | +    | +      | +   | +    | +   | +    | +     |
| [Span linking](specification/trace/api.md#specifying-links)                                      |          |     |      |     |        |      |        |     |      |     |      |       |
| Links can be recorded on span creation                                                           |          | +   | +    |     |        | +    | +      | +   | +    | +   | +    |       |
| Links order is preserved                                                                         |          | +   | +    |     |        | +    | +      | +   | +    | +   | +    |       |
| [Span events](specification/trace/api.md#add-events)                                             |          |     |      |     |        |      |        |     |      |     |      |       |
| AddEvent                                                                                         |          | +   | +    | +   | +      | +    | +      | +   | +    | +   | +    | +     |
| Add order preserved                                                                              |          | +   | +    | +   | +      | +    | +      | +   | +    | +   | +    | +     |
| Safe for concurrent calls                                                                        |          | +   | +    | +   | +      | +    | +      | +   | +    | +   | +    | +     |
| [Span exceptions](specification/trace/api.md#record-exception)                                   |          |     |      |     |        |      |        |     |      |     |      |       |
| RecordException                                                                                  |          | -   | +    | +   | +      | +    | +      | +   | +    | -   | +    | -     |
| RecordException with extra parameters                                                            |          | -   | +    | +   | +      | +    | +      | +   | +    | -   | +    | -     |
| [Sampling](specification/trace/sdk.md#sampling)                                                  |          |     |      |     |        |      |        |     |      |     |      |       |
| Allow samplers to modify tracestate                                                              |          | +   | +    |     | +      | +    | +      | +   | +    | +   | -    | +     |
| ShouldSample gets full parent Context                                                            |          | +   | +    | +   | +      | +    | +      | +   | +    | +   | -    | +     |
| [New Span ID created also for non-recording Spans](specification/trace/sdk.md#sdk-span-creation) |          | +   | +    |     | +      | +    | +      | +   | +    | +   | -    | +     |
| [IdGenerators](specification/trace/sdk.md#id-generators)                                         |          | +   | +    |     | +      | +    | +      | +   | +    | +   |      | +     |
| [SpanLimits](specification/trace/sdk.md#span-limits)                                             | X        | +   | +    |     | +      | +    | +      | +   |      | -   |      | +     |
| [Built-in `SpanProcessor`s implement `ForceFlush` spec](specification/trace/sdk.md#forceflush-1) |          |     | +    |     | +      | +    | +      | +   | +    | +   |      |       |
| [Attribute Limits](specification/common/common.md#attribute-limits)                              | X        |     | +    |     |        |      | +      | +   |      |     |      |       |

## Baggage

| Feature                            | Optional | Go | Java | JS | Python | Ruby | Erlang | PHP | Rust | C++ | .NET | Swift |
|------------------------------------|----------|----|------|----|--------|------|--------|-----|------|-----|------|-------|
| Basic support                      |          | +  | +    | +  | +      | +    | +      | +   | +    |  +  | +    | +     |
| Use official header name `baggage` |          | +  | +    | +  | +      | +    | +      | +   | +    |  +  | +    | +     |

## Metrics

**Status**: [Experimental](./specification/document-status.md)

Disclaimer: this list of features is still a work in progress, please refer to the specification if in any doubt.

| Feature                                                                                                                                                                      | Optional | Go | Java | JS | Python | Ruby | Erlang | PHP | Rust | C++ | .NET | Swift |
|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|----|------|----|--------|------|--------|-----|------|-----|------|-------|
| The API provides a way to set and get a global default `MeterProvider`.                                                                                                      | X        | +  |  +   |    |    +   |      |        |     |      |     |   -  |       |
| It is possible to create any number of `MeterProvider`s.                                                                                                                     | X        | +  |  +   |    |    +   |      |        |     |      |     |   +  |       |
| `MeterProvider` provides a way to get a `Meter`.                                                                                                                             |          | +  |  +   |    |    +   |      |        |     |      |     |   -  |       |
| `get_meter` accepts name, `version` and `schema_url`.                                                                                                                        |          | +  |  +   |    |    +   |      |        |     |      |     |   -  |       |
| When an invalid `name` is specified a working `Meter` implementation is returned as a fallback.                                                                              |          | +  |  +   |    |    -   |      |        |     |      |     |   -  |       |
| The fallback `Meter` `name` property keeps its original invalid value.                                                                                                       | X        | -  |  -   |    |    -   |      |        |     |      |     |   -  |       |
| The meter provides functions to create a new `Counter`.                                                                                                                      |          | +  |  +   |    |    +   |      |        |     |      |     |   +  |       |
| The meter provides functions to create a new `AsynchronousCounter`.                                                                                                          |          | +  |  +   |    |    +   |      |        |     |      |     |   +  |       |
| The meter provides functions to create a new `Histogram`.                                                                                                                    |          | +  |  +   |    |    +   |      |        |     |      |     |   +  |       |
| The meter provides functions to create a new `AsynchronousGauge`.                                                                                                            |          | +  |  +   |    |    +   |      |        |     |      |     |   +  |       |
| The meter provides functions to create a new `UpDownCounter`.                                                                                                                |          | +  |  +   |    |    +   |      |        |     |      |     |   -  |       |
| The meter provides functions to create a new `AsynchronousUpDownCounter`.                                                                                                    |          | +  |  +   |    |    +   |      |        |     |      |     |   -  |       |
| Instruments have `name`                                                                                                                                                      |          | +  |  +   |    |    +   |      |        |     |      |     |   +  |       |
| Instruments have kind.                                                                                                                                                       |          | +  |      |    |    +   |      |        |     |      |     |   +  |       |
| Instruments have an optional unit of measure.                                                                                                                                |          | +  |  +   |    |    +   |      |        |     |      |     |   +  |       |
| Instruments have an optional description.                                                                                                                                    |          | +  |  +   |    |    +   |      |        |     |      |     |   +  |       |
| An error is returned when multiple instruments are registered under the same `Meter` using the same `name`.                                                                  |          | +  |      |    |    -   |      |        |     |      |     |   +  |       |
| It is possible to register two instruments with same `name` under different `Meter`s.                                                                                        |          | +  |  +   |    |    +   |      |        |     |      |     |   +  |       |
| Instrument names conform to the specified syntax.                                                                                                                            |          | -  |  -   |    |    -   |      |        |     |      |     |   +  |       |
| Instrument units conform to the specified syntax.                                                                                                                            |          | -  |  -   |    |    -   |      |        |     |      |     |   +  |       |
| Instrument descriptions conform to the specified syntax.                                                                                                                     |          | -  |  -   |    |    -   |      |        |     |      |     |   +  |       |
| `create_counter` returns a `Counter`.                                                                                                                                        |          | +  |  +   |    |    +   |      |        |     |      |     |   +  |       |
| The API for `Counter` accepts the name, unit and description of the instrument.                                                                                              |          | +  |  +   |    |    +   |      |        |     |      |     |   +  |       |
| `Counter` has an `add` method.                                                                                                                                               |          | +  |  +   |    |    +   |      |        |     |      |     |   +  |       |
| The `add` method returns no (or dummy) value.                                                                                                                                |  X       | +  |  +   |    |    +   |      |        |     |      |     |   +  |       |
| The `add` method accepts optional attributes.                                                                                                                                |          | +  |  +   |    |    +   |      |        |     |      |     |   +  |       |
| The `add` method accepts the increment amount.                                                                                                                               |          | +  |  +   |    |    +   |      |        |     |      |     |   +  |       |
| The `add` method of `Counter` accepts only positive amounts.                                                                                                                 |          | +  |  +   |    |    -   |      |        |     |      |     |   -  |       |
| `create_asynchronous_counter` creates an `AsynchronousCounter`.                                                                                                              |          | +  |  +   |    |    +   |      |        |     |      |     |   +  |       |
| The API for `AsynchronousCounter` accepts the name, unit and description of the instrument.                                                                                  |          | +  |  +   |    |    +   |      |        |     |      |     |   +  |       |
| The API for `AsynchronousCounter` accepts a callback.                                                                                                                        |          | +  |  +   |    |    +   |      |        |     |      |     |   +  |       |
| `create_up_down_counter` returns an `UpDownCounter`.                                                                                                                         |          | +  |      |    |    +   |      |        |     |      |     |   -  |       |
| The API for `UpDownCounter` accepts the name, unit and description of the instrument.                                                                                        |          | +  |      |    |    +   |      |        |     |      |     |   -  |       |
| `UpDownCounter` has an `add` method.                                                                                                                                         |          | +  |      |    |    +   |      |        |     |      |     |   -  |       |
| The `add` method returns no (or dummy) value.                                                                                                                                |  X       | +  |      |    |    +   |      |        |     |      |     |   -  |       |
| The `add` method accepts optional attributes.                                                                                                                                |          | +  |      |    |    +   |      |        |     |      |     |   -  |       |
| The `add` method accepts the increment amount.                                                                                                                               |          | +  |      |    |    +   |      |        |     |      |     |   -  |       |
| `create_asynchronous_up_down_counter` creates an `AsynchronousUpDownCounter`.                                                                                                |          | +  |      |    |    +   |      |        |     |      |     |   -  |       |
| The API for `AsynchronousUpDownCounter` accepts the name, unit and description of the instrument.                                                                            |          | +  |      |    |    +   |      |        |     |      |     |   -  |       |
| The API for `AsynchronousUpDownCounter` accepts a callback.                                                                                                                  |          | +  |  +   |    |    +   |      |        |     |      |     |   -  |       |
| `create_histogram` returns a `Histogram`.                                                                                                                                    |          | +  |      |    |    +   |      |        |     |      |     |   +  |       |
| The API for `Histogram` accepts the name, unit and description of the instrument.                                                                                            |          | +  |      |    |    +   |      |        |     |      |     |   +  |       |
| `Histogram` has a `record` method.                                                                                                                                           |          | +  |      |    |    +   |      |        |     |      |     |   +  |       |
| The `record` method return no (or dummy) value.                                                                                                                              |  X       | +  |      |    |    +   |      |        |     |      |     |   +  |       |
| The `record` method accepts optional attributes.                                                                                                                             |          | +  |      |    |    +   |      |        |     |      |     |   +  |       |
| The `record` method accepts a value.                                                                                                                                         |          | +  |      |    |    +   |      |        |     |      |     |   +  |       |
| The `record` method of `Histogram` accepts only positive amounts.                                                                                                            |          | -  |      |    |    -   |      |        |     |      |     |   +  |       |
| `create_asynchronous_gauge` creates an `Asynchronous Gauge`.                                                                                                                 |          | +  |      |    |    +   |      |        |     |      |     |   +  |       |
| The API for `AsynchronousGauge` accepts the name, unit and description of the instrument.                                                                                    |          | +  |      |    |    +   |      |        |     |      |     |   +  |       |
| The API for `AsynchronousGauge` accepts a callback.                                                                                                                          |          | +  |      |    |    +   |      |        |     |      |     |   +  |       |
| The callback function of an `Asynchronous` instrument does not block indefinitely.                                                                                           |          | -  |  -   |    |    -   |      |        |     |      |     |   ?  |       |
| The callback function reports `Measurement`s.                                                                                                                                |          | +  |  +   |    |    +   |      |        |     |      |     |   +  |       |
| There is a way to pass state to the callback.                                                                                                                                | X        | +  |  +   |    |    -   |      |        |     |      |     |   +  |       |
| All methods of `MeterProvider` are safe to be called concurrently.                                                                                                           |          | +  |  +   |    |    -   |      |        |     |      |     |   +  |       |
| All methods of `Meter` are safe to be called concurrently.                                                                                                                   |          | +  |  +   |    |    -   |      |        |     |      |     |   +  |       |
| All methods of any instrument are safe to be called concurrently.                                                                                                            |          | +  |  +   |    |    -   |      |        |     |      |     |   +  |       |
| `MeterProvider` allows a `Resource` to be specified.                                                                                                                         |          | +  |  +   |    |    +   |      |        |     |      |     |   +  |       |
| A specified `Resource` can be associated with all the produced metrics from any `Meter` from the `MeterProvider`.                                                            |          | +  |  +   |    |    +   |      |        |     |      |     |   +  |       |
| The supplied `name`, `version` and `schema_url` arguments passed to the `MeterProvider` are used to create an `InstrumentationLibrary` instance stored in the `Meter`.       |          | +  |  +   |    |    +   |      |        |     |      |     |   -  |       |
| Configuration is managed solely by the `MeterProvider`.                                                                                                                      |          | +  |  +   |    |    +   |      |        |     |      |     |   +  |       |
| The `MeterProvider` provides methods to update the configuration                                                                                                             | X        | -  |  -   |    |    +   |      |        |     |      |     |   +  |       |
| The updated configuration applies to all already returned `Meter`s.                                                                                                          | if above | -  |  -   |    |    -   |      |        |     |      |     |   +  |       |
| There is a way to register `View`s with a `MeterProvider`.                                                                                                                   |          | -  |  +   |    |    +   |      |        |     |      |     |   +  |       |
| The `View` instrument selection criteria is as specified.                                                                                                                    |          |    |  +   |    |    -   |      |        |     |      |     |   +  |       |
| The name of the `View` can be specified.                                                                                                                                     |          |    |  +   |    |    -   |      |        |     |      |     |   +  |       |
| The `View` allows configuring the name description, attributes keys and aggregation of the resulting metric stream.                                                          |          |    |  ?   |    |    -   |      |        |     |      |     |   -  |       |
| The `View` allows configuring the exemplar reservoir of resulting metric stream.                                                                                             | X        |    |  ?   |    |    -   |      |        |     |      |     |   -  |       |
| The SDK allows more than one `View` to be specified per instrument.                                                                                                          | X        |    |  ?   |    |    -   |      |        |     |      |     |   +  |       |
| The `Drop` aggregation is available.                                                                                                                                         |          | +  |  +   |    |    -   |      |        |     |      |     |   +  |       |
| The `Drop` aggregation drops all measurements and does not produce a metric stream.                                                                                          |          | +  |  +   |    |    -   |      |        |     |      |     |   +  |       |
| The `Default` aggregation is available.                                                                                                                                      |          | +  |  +   |    |    -   |      |        |     |      |     |   +  |       |
| The `Default` aggregation uses the specified aggregation by instrument.                                                                                                      |          | +  |  +   |    |    -   |      |        |     |      |     |   +  |       |
| The `Sum` aggregation is available.                                                                                                                                          |          | +  |  +   |    |    +   |      |        |     |      |     |   +  |       |
| The `Sum` aggregation performs as specified.                                                                                                                                 |          | +  |  +   |    |    +   |      |        |     |      |     |   +  |       |
| The `LastValue` aggregation is available.                                                                                                                                    |          | +  |  +   |    |    +   |      |        |     |      |     |   +  |       |
| The `LastValue` aggregation performs as specified.                                                                                                                           |          | +  |  +   |    |    +   |      |        |     |      |     |   +  |       |
| The `Histogram` aggregation is available.                                                                                                                                    |          | +  |  +   |    |    -   |      |        |     |      |     |   +  |       |
| The `Histogram` aggregation performs as specified.                                                                                                                           |          | +  |  +   |    |    -   |      |        |     |      |     |   +  |       |
| The explicit bucket `Histogram` aggregation is available.                                                                                                                    |          | -  |  +   |    |    +   |      |        |     |      |     |   +  |       |
| The explicit bucket `Histogram` aggregation performs as specified.                                                                                                           |          | -  |  +   |    |    -   |      |        |     |      |     |   +  |       |
| The metrics exporter has access to the aggregated metrics data (aggregated points, not raw measurements).                                                                    |          | +  |  -   |    |    -   |      |        |     |      |     |   +  |       |
| The metrics exporter `export` function can not be called concurrently from the same exporter instance.                                                                       |          | +  |  -   |    |    -   |      |        |     |      |     |   +  |       |
| The metrics exporter `export` function does not block indefinitely.                                                                                                          |          | +  |  -   |    |    -   |      |        |     |      |     |   +  |       |
| The metrics exporter `export` function receives a batch of metrics.                                                                                                          |          | +  |  +   |    |    -   |      |        |     |      |     |   +  |       |
| The metrics exporter `export` function returns `Success` or `Failure`.                                                                                                       |          | +  |  +   |    |    -   |      |        |     |      |     |   +  |       |
| The metrics exporter provides a `ForceFlush` function.                                                                                                                       |          | -  |  -   |    |    -   |      |        |     |      |     |   +  |       |
| The metrics exporter `ForceFlush` can inform the caller whether it succeeded, failed or timed out.                                                                           |          |    |      |    |    -   |      |        |     |      |     |   +  |       |
| The metrics exporter provides a `shutdown` function.                                                                                                                         |          | +  |  +   |    |    -   |      |        |     |      |     |   +  |       |
| The metrics exporter `shutdown` function do not block indefinitely.                                                                                                          |          | +  |  -   |    |    -   |      |        |     |      |     |   +  |       |
| The metrics SDK samples `Exemplar`s from measurements.                                                                                                                       |          |    |      |    |    -   |      |        |     |      |     |   -  |       |
| Exemplar sampling can be disabled.                                                                                                                                           |          |    |      |    |    -   |      |        |     |      |     |   -  |       |
| The metrics SDK samples measurements in the context of a sampled trace by default.                                                                                           |          |    |      |    |    -   |      |        |     |      |     |   -  |       |
| Exemplars retain any attributes available in the measurement that are not preserved by aggregation or view configuration.                                                    |          |    |      |    |    -   |      |        |     |      |     |   -  |       |
| Exemplars contain the associated trace id and span id of the active span in the Context when the measurement was taken.                                                      |          |    |      |    |    -   |      |        |     |      |     |   -  |       |
| Exemplars contain the timestamp when the measurement was taken.                                                                                                              |          |    |      |    |    -   |      |        |     |      |     |   -  |       |
| The metrics SDK provides an `ExemplarReservoir` interface or extension point.                                                                                                | X        |    |      |    |    -   |      |        |     |      |     |   -  |       |
| An `ExemplarReservoir` has an `offer` method with access to the measurement value, attributes, `Context` and timestamp.                                                      | X        |    |      |    |    -   |      |        |     |      |     |   -  |       |
| The metrics SDK provides a `SimpleFixedSizeExemplarReservoir` that is used by default for all aggregations except `ExplicitBucketHistogram`.                                 |          |    |      |    |    -   |      |        |     |      |     |   -  |       |
| The metrics SDK provides an `AlignedHistogramBucketExemplarReservoir` that is used by default for `ExplicitBucketHistogram` aggregation.                                     |          |    |      |    |    -   |      |        |     |      |     |   -  |       |
| The metrics SDK provides an `ExemplarFilter` interface or extension point.                                                                                                   | X        |    |      |    |    -   |      |        |     |      |     |   -  |       |
| An `ExemplarFilter` has access to the measurement value, attributes, `Context` and timestamp.                                                                                | X        |    |      |    |    -   |      |        |     |      |     |   -  |       |

## Resource

| Feature                                                                                                                                     | Optional | Go | Java | JS | Python | Ruby | Erlang | PHP | Rust | C++ | .NET | Swift |
|---------------------------------------------------------------------------------------------------------------------------------------------|----------|----|------|----|--------|------|--------|-----|------|-----|------|-------|
| Create from Attributes                                                                                                                      |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| Create empty                                                                                                                                |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| [Merge (v2)](specification/resource/sdk.md#merge)                                                                                           |          | +  | +    |    | +      | +    | +      | +   | +    | +   | +    |       |
| Retrieve attributes                                                                                                                         |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| [Default value](specification/resource/semantic_conventions/README.md#semantic-attributes-with-sdk-provided-default-value) for service.name |          | +  | +    |    | +      | +    | +      |     |      | +   | +    |       |
| [Resource detector](specification/resource/sdk.md#detecting-resource-information-from-the-environment) interface/mechanism                  |          | +  | +    | +  | +      | +    | +      | [-][php225]   | +    | +   | +    | +     |
| [Resource detectors populate Schema URL](specification/resource/sdk.md#detecting-resource-information-from-the-environment)                 |          | +  |      |    |        |      | -      |     |      |     | -    |       |

## Context Propagation

| Feature                                                                          | Optional | Go | Java | JS | Python | Ruby | Erlang | PHP | Rust | C++ | .NET | Swift |
|----------------------------------------------------------------------------------|----------|----|------|----|--------|------|--------|-----|------|-----|------|-------|
| Create Context Key                                                               |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| Get value from Context                                                           |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| Set value for Context                                                            |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| Attach Context                                                                   |          | N/A| +    | +  | +      | +    | +      | +   | +    | +   | -    | -     |
| Detach Context                                                                   |          | N/A| +    | +  | +      | +    | +      | +   | +    | +   | -    | -     |
| Get current Context                                                              |          | N/A| +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| Composite Propagator                                                             |          | +  | +    | +  | +      | +    | +      |     | +    | +   | +    | +     |
| Global Propagator                                                                |          | +  | +    | +  | +      | +    | +      |     | +    | +   | +    | +     |
| TraceContext Propagator                                                          |          | +  | +    | +  | +      | +    | +      |     | +    | +   | +    | +     |
| B3 Propagator                                                                    |          | +  | +    | +  | +      | +    | +      |     | +    | +   | +    | +     |
| Jaeger Propagator                                                                |          | +  | +    | +  | +      | +    | +      |     | +    | +   | -    | -     |
| [TextMapPropagator](specification/context/api-propagators.md#textmap-propagator) |          | +  |      |    |        |      |        |     |      |     |      |       |
| Fields                                                                           |          | +  | +    | +  | +      | +    | +      |     | +    | +   | +    | +     |
| Setter argument                                                                  | X        | N/A| +    | +  | +      | +    | +      |     | N/A  | +   | +    | +     |
| Getter argument                                                                  | X        | N/A| +    | +  | +      | +    | +      |     | N/A  | +   | +    | +     |
| Getter argument returning Keys                                                   | X        | N/A| +    | +  | +      | +    | +      |     | N/A  | +   | -    | +     |

## Environment Variables

Note: Support for environment variables is optional.

|Feature                                       |Go |Java|JS |Python|Ruby|Erlang|PHP|Rust|C++|.NET|Swift|
|----------------------------------------------|---|----|---|------|----|------|---|----|---|----|-----|
|OTEL_RESOURCE_ATTRIBUTES                      | + | +  | + | +    | +  | +    | - | +  | + | +  | -   |
|OTEL_SERVICE_NAME                             | + |    |   |      |    | +    |   |    |   | +  |     |
|OTEL_LOG_LEVEL                                | - | -  | + | [-][py1059] | +  | - | -  |    | - | -  | -   |
|OTEL_PROPAGATORS                              | - | +  |   | +    | +  | +    | - | -  | - | -  | -   |
|OTEL_BSP_*                                    | - | +  |   | +    | +  | +    | - | +  | - | -  | -   |
|OTEL_EXPORTER_OTLP_*                          | + | +  |   | +    | +  | +    | - | +  | + | +  | -   |
|OTEL_EXPORTER_JAEGER_*                        | + |    |   |      |    | -    | - |    | - | +  | -   |
|OTEL_EXPORTER_ZIPKIN_*                        | - |    |   |      |    | -    | - | -  | - | +  | -   |
|OTEL_TRACES_EXPORTER                          | - | +  |   | +    | +  | +    |   | -  | - | -  |     |
|OTEL_METRICS_EXPORTER                         | - | +  |   | +    | -  | -    |   | -  | - | -  | -   |
|OTEL_LOGS_EXPORTER                            |   |    |   |      |    |      |   |    |   | -  |     |
|OTEL_SPAN_ATTRIBUTE_COUNT_LIMIT               | - | +  |   | +    | +  | +    |   | +  | - | -  |     |
|OTEL_SPAN_ATTRIBUTE_VALUE_LENGTH_LIMIT        |   |    |   |      |    | +    |   |    |   | -  |     |
|OTEL_SPAN_EVENT_COUNT_LIMIT                   | - | +  |   | +    | +  | +    |   | +  | - | -  |     |
|OTEL_SPAN_LINK_COUNT_LIMIT                    | - | +  |   | +    | +  | +    |   | +  | - | -  |     |
|OTEL_EVENT_ATTRIBUTE_COUNT_LIMIT              |   |    |   |      |    | +    |   |    |   | -  |     |
|OTEL_LINK_ATTRIBUTE_COUNT_LIMIT               |   |    |   |      |    | +    |   |    |   | -  |     |
|OTEL_TRACES_SAMPLER                           | - | +  |   | +    | +  | +    |   | -  | - | -  |     |
|OTEL_TRACES_SAMPLER_ARG                       | - | +  |   | +    | +  | +    |   | -  | - | -  |     |
|OTEL_ATTRIBUTE_VALUE_LENGTH_LIMIT             |   |    |   |      |    | -    |   |    |   | -  |     |
|OTEL_ATTRIBUTE_COUNT_LIMIT                    |   |    |   |      |    | -    |   |    |   | -  |     |
|OTEL_METRICS_EXEMPLAR_FILTER                  |   |    |   |      |    |      |   |    |   | -  |     |

## Exporters

| Feature                                                                        | Optional | Go | Java | JS | Python   | Ruby | Erlang | PHP | Rust | C++ | .NET | Swift |
|--------------------------------------------------------------------------------|----------|----|------|----|----------|------|--------|-----|------|-----|------|-------|
| [Exporter interface](specification/trace/sdk.md#span-exporter)                 |          |    | + |    | +           |      | +      | +   | +    | +   | +    |       |
| [Exporter interface has `ForceFlush`](specification/trace/sdk.md#forceflush-2) |          |    | + |    | [-][py1779] | +    | +      | +   | -    |     |      |       |
| Standard output (logging)                                                      |          | +  | + | +  | +           | +    | +      | -   | +    | +   | +    | +     |
| In-memory (mock exporter)                                                      |          | +  | + | +  | +           | +    | +      | +   | -    | +   | +    | +     |
| [OTLP](specification/protocol/otlp.md)                                         |          |    |   |    |             |      |        |     |      |     |      |       |
| OTLP/gRPC Exporter                                                             | *        | +  | + | +  | +           |      | +      | +   | +    | +   | +    | +     |
| OTLP/HTTP binary Protobuf Exporter                                             | *        | +  | + | +  | +           | +    | +      |     | +    | +   | +    | -     |
| OTLP/HTTP JSON Protobuf Exporter                                               |          | +  | - | +  | [-][py1003] |      | -      |     |      | +   | -    | -     |
| OTLP/HTTP gzip Content-Encoding support                                        | X        | +  | + | +  | +           | +    | -      |     |      | -   | -    | -     |
| Concurrent sending                                                             |          | -  | + | +  | [-][py1108] |      | -      |     | +    | -   | -    | -     |
| Honors retryable responses with backoff                                        | X        | +  |   | +  | +           | +    | -      |     |      | -   | -    | -     |
| Honors non-retryable responses                                                 | X        | +  |   | -  | +           | +    | -      |     |      | -   | -    | -     |
| Honors throttling response                                                     | X        | +  |   | -  | +           | +    | -      |     |      | -   | -    | -     |
| Multi-destination spec compliance                                              | X        | +  |   |    | [-][py1109] |      | -      |     |      | -   | -    | -     |
| SchemaURL in ResourceSpans and InstrumentationLibrarySpans                     |          | +  |   |    |             |      | +      |     |      |     | -    |       |
| SchemaURL in ResourceMetrics and InstrumentationLibraryMetrics                 |          |    |   |    |             |      | -      |     |      |     | -    |       |
| SchemaURL in ResourceLogs and InstrumentationLibraryLogs                       |          |    |   |    |             |      | -      |     |      |     | -    |       |
| [Zipkin](specification/trace/sdk_exporters/zipkin.md)                          |          |    |   |    |             |      |        |     |      |     |      |       |
| Zipkin V1 JSON                                                                 | X        | -  | + |    | +           | -    | -      | -   | -    | -   | -    | -     |
| Zipkin V1 Thrift                                                               | X        | -  | + |    | [-][py1174] | -    | -      | -   | -    | -   | -    | -     |
| Zipkin V2 JSON                                                                 | *        | +  | + |    | +           | +    | -      | +   | +    | +   | +    | +     |
| Zipkin V2 Protobuf                                                             | *        | -  | + |    | +           | -    | +      | -   | -    | -   | -    | -     |
| Service name mapping                                                           |          | +  | + | +  | +           | +    | +      | +   | +    | +   | +    | +     |
| SpanKind mapping                                                               |          | +  | + | +  | +           | +    | +      | +   | +    | +   | +    | +     |
| InstrumentationLibrary mapping                                                 |          | +  | + | -  | +           | +    | -      | +   | +    | +   | +    | +     |
| Boolean attributes                                                             |          | +  | + | +  | +           | +    | +      | +   | +    | +   | +    | +     |
| Array attributes                                                               |          | +  | + | +  | +           | +    | +      | +   | +    | +   | +    | +     |
| Status mapping                                                                 |          | +  | + | +  | +           | +    | +      | +   | +    | +   | +    | +     |
| Error Status mapping                                                           |          | +  | + |    |             | +    | -      | +   | +    | +   | +    | -     |
| Event attributes mapping to Annotations                                        |          | +  | + | +  | +           | +    | +      | +   | +    | +   | +    | +     |
| Integer microseconds in timestamps                                             |          | N/A| + |    | +           | +    | -      | +   | +    | +   | +    | +     |
| [Jaeger](specification/trace/sdk_exporters/jaeger.md)                          |          |    |   |    |             |      |        |     |      |     |      |       |
| Jaeger Thrift over UDP                                                         | *        | +  |   |    | +           | +    | -      |     | +    | +   | +    | +     |
| Jaeger Protobuf via gRPC                                                       | *        | -  | + |    | [-][py1437] | -    | -      |     |      | -   | -    | -     |
| Jaeger Thrift over HTTP                                                        | *        | +  | + |    | +           | +    | -      |     | +    | +   | +    | -     |
| Service name mapping                                                           |          | +  | + |    | +           | +    | -      |     |      | +   | +    | +     |
| Resource to Process mapping                                                    |          | +  | + |    | +           | +    | -      |     | +    | -   | +    | -     |
| InstrumentationLibrary mapping                                                 |          | +  | + |    | +           | +    | -      |     | +    | -   | +    | -     |
| Status mapping                                                                 |          | +  | + |    | +           | +    | -      |     | +    | +   | +    | +     |
| Error Status mapping                                                           |          | +  | + |    | +           | +    | -      |     | +    | +   | +    | -     |
| Events converted to Logs                                                       |          | +  | + |    | +           | +    | -      |     | +    | -   | +    | +     |
| OpenCensus                                                                     |          |    |   |    |             |      |        |     |      |     |      |       |
| TBD                                                                            |          |    |   |    |             |      |        |     |      |     |      |       |
| Prometheus                                                                     |          |    |   |    |             |      |        |     |      |     |      |       |
| TBD                                                                            |          |    |   |    |             |      |        |     |      |     |      |       |

## OpenTracing Compatibility

Languages not covered by the OpenTracing project do not need to be listed here, e.g. Erlang.

| Feature                                                                                                 |Go |Java|JS |Python|Ruby|PHP|Rust|C++|.NET|Swift|
|---------------------------------------------------------------------------------------------------------|---|----|---|------|----|---|----|---|----|-----|
| [Create OpenTracing Shim](specification/compatibility/opentracing.md#create-an-opentracing-tracer-shim) |   |    |   |      |    |   |    |   |    |     |
| [Tracer](specification/compatibility/opentracing.md#tracer-shim)                                        |   |    |   |      |    |   |    |   |    |     |
| [Span](specification/compatibility/opentracing.md#span-shim)                                            |   |    |   |      |    |   |    |   |    |     |
| [SpanContext](specification/compatibility/opentracing.md#spancontext-shim)                              |   |    |   |      |    |   |    |   |    |     |
| [ScopeManager](specification/compatibility/opentracing.md#scopemanager-shim)                            |   |    |   |      |    |   |    |   |    |     |
| Error mapping for attributes/events                                                                     |   |    |   |      |    |   |    |   |    |     |
| Migration to OpenTelemetry guide                                                                        |   |    |   |      |    |   |    |   |    |     |

[py1003]: https://github.com/open-telemetry/opentelemetry-python/issues/1003
[py1059]: https://github.com/open-telemetry/opentelemetry-python/issues/1059
[py1108]: https://github.com/open-telemetry/opentelemetry-python/issues/1108
[py1109]: https://github.com/open-telemetry/opentelemetry-python/issues/1109
[py1174]: https://github.com/open-telemetry/opentelemetry-python/issues/1174
[py1437]: https://github.com/open-telemetry/opentelemetry-python/issues/1437
[py1779]: https://github.com/open-telemetry/opentelemetry-python/issues/1779
[php225]: https://github.com/open-telemetry/opentelemetry-php/issues/225
