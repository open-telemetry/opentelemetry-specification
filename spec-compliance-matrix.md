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

| Feature                                                                                          | Optional | Go | Java | JS | Python | Ruby | Erlang | PHP | Rust | C++ | .NET | Swift |
|--------------------------------------------------------------------------------------------------|----------|----|------|----|--------|------|--------|-----|------|-----|------|-------|
| [TracerProvider](specification/trace/api.md#tracerprovider-operations)                           |          |    |      |    |        |      |        |     |      |     |      |       |
| Create TracerProvider                                                                            |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| Get a Tracer                                                                                     |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| Get a Tracer with schema_url                                                                     |          | +  |      |    |        |      |        |     |      | +   |      |       |
| Safe for concurrent calls                                                                        |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| Shutdown (SDK only required)                                                                     |          | +  | +    | +  | +      | +    | -      |     | +    | +   | +    | +     |
| ForceFlush (SDK only required)                                                                   |          | +  | +    | -  | +      | +    | -      |     | +    | +   | +    | +     |
| [Trace / Context interaction](specification/trace/api.md#context-interaction)                    |          |    |      |    |        |      |        |     |      |     |      |       |
| Get active Span                                                                                  |          | N/A| +    | +  | +      | +    | +      |     | +    | +   | +    | +     |
| Set active Span                                                                                  |          | N/A| +    | +  | +      | +    | +      |     | +    | +   | +    | +     |
| [Tracer](specification/trace/api.md#tracer-operations)                                           |          |    |      |    |        |      |        |     |      |     |      |       |
| Create a new Span                                                                                |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| Get active Span                                                                                  |          | N/A| +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| Mark Span active                                                                                 |          | N/A| +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| Safe for concurrent calls                                                                        |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| [SpanContext](specification/trace/api.md#spancontext)                                            |          |    |      |    |        |      |        |     |      |     |      |       |
| IsValid                                                                                          |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| IsRemote                                                                                         |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| Conforms to the W3C TraceContext spec                                                            |          | +  | +    | +  | +      | +    | +      |     | +    | +   | +    | +     |
| [Span](specification/trace/api.md#span)                                                          |          |    |      |    |        |      |        |     |      |     |      |       |
| Create root span                                                                                 |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| Create with default parent (active span)                                                         |          | N/A| +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| Create with parent from Context                                                                  |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| No explicit parent Span/SpanContext allowed                                                      |          | +  | +    | +  | +      | +    | +      |     | +    | +   | -    | +     |
| SpanProcessor.OnStart receives parent Context                                                    |          | +  | +    | +  | +      | +    | +      |     | +    | -   | -    | +     |
| UpdateName                                                                                       |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| User-defined start timestamp                                                                     |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| End                                                                                              |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| End with timestamp                                                                               |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| IsRecording                                                                                      |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| IsRecording becomes false after End                                                              |          | +  | +    | +  | +      | +    | +      |     | +    | +   | -    | +     |
| Set status with StatusCode (Unset, Ok, Error)                                                    |          | +  | +    | +  | +      | +    | -      |     | +    | +   | +    | +     |
| Safe for concurrent calls                                                                        |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| events collection size limit                                                                     |          | +  | +    | +  | +      | +    | -      |     | +    | -   | -    | +     |
| attribute collection size limit                                                                  |          | +  | +    | +  | +      | +    | -      |     | +    | -   | -    | +     |
| links collection size limit                                                                      |          | +  | +    | +  | +      | +    | -      |     | +    | -   | -    | +     |
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
| Links can be recorded on span creation                                                           |          | +  |      |    |        | +    |        |     | +    | +   |      |       |
| Links order is preserved                                                                         |          | +  |      |    |        | +    |        |     | +    | +   |      |       |
| [Span events](specification/trace/api.md#add-events)                                             |          |    |      |    |        |      |        |     |      |     |      |       |
| AddEvent                                                                                         |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| Add order preserved                                                                              |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| Safe for concurrent calls                                                                        |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| [Span exceptions](specification/trace/api.md#record-exception)                                   |          |    |      |    |        |      |        |     |      |     |      |       |
| RecordException                                                                                  |          | -  | +    | +  | +      | +    | -      |     | +    | -   | +    | -     |
| RecordException with extra parameters                                                            |          | -  | +    | +  | +      | +    | -      |     | +    | -   | +    | -     |
| [Sampling](specification/trace/sdk.md#sampling)                                                  |          |    |      |    |        |      |        |     |      |     |      |       |
| Allow samplers to modify tracestate                                                              |          | +  | +    |    | +      | +    | +      |     | +    | +   | -    | +     |
| ShouldSample gets full parent Context                                                            |          | +  | +    | +  | +      | +    | +      |     | +    | +   | -    | +     |
| [New Span ID created also for non-recording Spans](specification/trace/sdk.md#sdk-span-creation) |          | +  | +    |    | +      | +    | +      |     | +    | +   | -    | +     |
| [IdGenerators](specification/trace/sdk.md#id-generators)                                         |          | +  | +    |    | +      | +    |        |     | +    | +   |      | +     |
| [SpanLimits](specification/trace/sdk.md#span-limits)                                             | X        | +  | +    |    | +      | +    |        |     |      | -   |      | +     |
| [Built-in `SpanProcessor`s implement `ForceFlush` spec](specification/trace/sdk.md#forceflush-1) |          |    |      |    | +      | +    |        |     | +    | +   |      |       |
| [Attribute Limits](specification/common/common.md#attribute-limits)                              | X        |    |      |    |        |      |        |     |      |     |      |       |

## Baggage

| Feature                            | Optional | Go | Java | JS | Python | Ruby | Erlang | PHP | Rust | C++ | .NET | Swift |
|------------------------------------|----------|----|------|----|--------|------|--------|-----|------|-----|------|-------|
| Basic support                      |          | +  | +    | +  | +      | +    | +      |     | +    |  +  | +    | +     |
| Use official header name `baggage` |          | +  | +    | +  | +      | +    | +      |     | +    |  +  | +    | +     |

## Metrics

| Feature                                                                                                                                                                           | Optional | Go | Java | JS | Python | Ruby | Erlang | PHP | Rust | C++ | .NET | Swift |
|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|----|------|----|--------|------|--------|-----|------|-----|------|-------|
| The API provides a way to set and get a global default MeterProvider                                                                                                              |          |    |      |    |        |      |        |     |      |     |      |       |
| It is possible to create any number of MeterProviders                                                                                                                             |          |    |      |    |        |      |        |     |      |     |      |       |
| MeterProvider provides a way to get Meter                                                                                                                                                   |          |    |      |    |        |      |        |     |      |     |      |       |
| When an invalid name is specified a working meter implementation is returned as a fallback.                                                                                       |          |    |      |    |        |      |        |     |      |     |      |       |
| The fallback meter name property keeps its original invalid value                                                                                                                 |          |    |      |    |        |      |        |     |      |     |      |       |
| The fallback meter name property keeps its original invalid value                                                                                                                 |          |    |      |    |        |      |        |     |      |     |      |       |
| The API provides a way to set and get a global default MeterProvider                                                                                                         |          |    |      |    |        |      |        |     |      |     |      |       |
| It is possible to create any number of MeterProviders                                                                                                                             |          |    |      |    |        |      |        |     |      |     |      |       |
| `get_meter` accepts name, version and schema_url                                                                                                                                  |          |    |      |    |        |      |        |     |      |     |      |       |
| The fallback meter name property keeps its original invalid value.                                                                                                                |          |    |      |    |        |      |        |     |      |     |      |       |
| New configuration applies to previously returned meters.                                                                                                                          |          |    |      |    |        |      |        |     |      |     |      |       |
| The meter provides functions to create a new Counter                                                                                                                              |          |    |      |    |        |      |        |     |      |     |      |       |
| The meter provides functions to create a new AsynchronousCounter                                                                                                                  |          |    |      |    |        |      |        |     |      |     |      |       |
| The meter provides functions to create a new Histogram                                                                                                                            |          |    |      |    |        |      |        |     |      |     |      |       |
| The meter provides functions to create a new Asynchronous Gauge                                                                                                                   |          |    |      |    |        |      |        |     |      |     |      |       |
| The meter provides functions to create a new UpDownCounter                                                                                                                        |          |    |      |    |        |      |        |     |      |     |      |       |
| The meter provides functions to create a new Asynchronous UpDownCounter                                                                                                                                     |          |    |      |    |        |      |        |     |      |     |      |       |
| The instrument has name.                                                                                                                                                          |          |    |      |    |        |      |        |     |      |     |      |       |
| The instrument has kind.                                                                                                                                                          |          |    |      |    |        |      |        |     |      |     |      |       |
| The instrument has an optional unit of measure.                                                                                                                                   |          |    |      |    |        |      |        |     |      |     |      |       |
| The instrument has an optional description.                                                                                                                                       |          |    |      |    |        |      |        |     |      |     |      |       |
| The meter returns an error when multiple instruments are registered under the same Meter using the same name.                                                                     |          |    |      |    |        |      |        |     |      |     |      |       |
| It is possible to register two instruments with same name under different Meters.                                                                                             |          |    |      |    |        |      |        |     |      |     |      |       |
| Instrument names conform to the specified syntax.                                                                                                                                 |          |    |      |    |        |      |        |     |      |     |      |       |
| Instrument units conform to the specified syntax.                                                                                                                                 |          |    |      |    |        |      |        |     |      |     |      |       |
| Instrument descriptions conform to the specified syntax.                                                                                                                          |          |    |      |    |        |      |        |     |      |     |      |       |
| `create_counter` returns a `Counter` object.                                                                                                                                   |          |    |      |    |        |      |        |     |      |     |      |       |
| The API for creating a counter accepts the name of the instrument.                                                                                                                |          |    |      |    |        |      |        |     |      |     |      |       |
| The API for creating a counter accepts the unit of the instrument.                                                                                                                |          |    |      |    |        |      |        |     |      |     |      |       |
| The API for creating a counter accepts the description of the instrument.                                                                                                         |          |    |      |    |        |      |        |     |      |     |      |       |
| The counter has an add method.                                                                                                                                                    |          |    |      |    |        |      |        |     |      |     |      |       |
| The add method returns `null` (this can vary depending on the language).                                                                                                                                                      |          |    |      |    |        |      |        |     |      |     |      |       |
| The add method accepts optional attributes.                                                                                                                                       |          |    |      |    |        |      |        |     |      |     |      |       |
| The add method accepts the increment amount.                                                                                                                                      |          |    |      |    |        |      |        |     |      |     |      |       |
| The add method accepts only positive amounts.                                                                                                                                     |          |    |      |    |        |      |        |     |      |     |      |       |
| `create_asynchronous_counter` returns an `AsynchronousCounter` object.                                                                                                                      |          |    |      |    |        |      |        |     |      |     |      |       |
| The API ObservableCounter is an abstract class.                                                                                                                                   |          |    |      |    |        |      |        |     |      |     |      |       |
| The API for creating an asynchronous counter accepts the name of the instrument.                                                                                                   |          |    |      |    |        |      |        |     |      |     |      |       |
| The API for creating a asynchronous counter accepts the unit of the instrument.                                                                                                   |          |    |      |    |        |      |        |     |      |     |      |       |
| The API for creating a asynchronous counter accepts the description of the instrument.                                                                                            |          |    |      |    |        |      |        |     |      |     |      |       |
| The API for creating a asynchronous counter accepts a callback.                                                                                                                   |          |    |      |    |        |      |        |     |      |     |      |       |
| The asynchronous counter has an add method.                                                                                                                                       |          |    |      |    |        |      |        |     |      |     |      |       |
| The add method returns None.                                                                                                                                                      |          |    |      |    |        |      |        |     |      |     |      |       |
| The add method accepts optional attributes.                                                                                                                                       |          |    |      |    |        |      |        |     |      |     |      |       |
| The add method accepts the increment amount.                                                                                                                                      |          |    |      |    |        |      |        |     |      |     |      |       |
| The add method accepts only positive amounts.                                                                                                                                     |          |    |      |    |        |      |        |     |      |     |      |       |
| The callback function of an Asynchronous Instrument has a timeout.                                                                                                                                              |          |    |      |    |        |      |        |     |      |     |      |       |
| The callback function reports measurements.                                                                                                                                       |          |    |      |    |        |      |        |     |      |     |      |       |
| There is a way to pass state to the callback.                                                                                                                                     |          |    |      |    |        |      |        |     |      |     |      |       |
| All methods of MeterProvider are safe to be called concurrently.                                                                                                                  |          |    |      |    |        |      |        |     |      |     |      |       |
| all methods of Meter are safe to be called concurrently.                                                                                                                          |          |    |      |    |        |      |        |     |      |     |      |       |
| All methods of Instrument are safe to be called concurrently.                                                                                                                     |          |    |      |    |        |      |        |     |      |     |      |       |
| Test MeterProvider allows a Resource to be specified.                                                                                                                             |          |    |      |    |        |      |        |     |      |     |      |       |
| A specified Resource can be associated with all The produced metrics from any Meter from the MeterProvider.                                                                       |          |    |      |    |        |      |        |     |      |     |      |       |
| The supplied name, version and schema_url arguments passed to the MeterProvider are used to create an InstrumentationLibrary instance stored in the Meter.                        |          |    |      |    |        |      |        |     |      |     |      |       |
| configuration can be managed by The MeterProvider.                                                                                                                                |          |    |      |    |        |      |        |     |      |     |      |       |
| The MeterProvider provides methods to update the configuration                                                                                                                    |          |    |      |    |        |      |        |     |      |     |      |       |
| The updated configuration applies to all already returned Meters.                                                                                                                 |          |    |      |    |        |      |        |     |      |     |      |       |
| There is a way to register Views with a MeterProvider                                                                                                                             |          |    |      |    |        |      |        |     |      |     |      |       |
| The view instrument selection criteria is as specified.                                                                                                                           |          |    |      |    |        |      |        |     |      |     |      |       |
| The name of the View can be specified.                                                                                                                                            |          |    |      |    |        |      |        |     |      |     |      |       |
| The configuration for the metrics stream is as specified.                                                                                                                         |          |    |      |    |        |      |        |     |      |     |      |       |
| The specified logic is used to process Measurements made by an instrument.                                                                                                        |          |    |      |    |        |      |        |     |      |     |      |       |
| The None aggregation is available.                                                                                                                                                |          |    |      |    |        |      |        |     |      |     |      |       |
| The None aggregation drops all measurements.                                                                                                                                      |          |    |      |    |        |      |        |     |      |     |      |       |
| The Default aggregation is available.                                                                                                                                             |          |    |      |    |        |      |        |     |      |     |      |       |
| The Default aggregation uses the specified aggregation.                                                                                                                           |          |    |      |    |        |      |        |     |      |     |      |       |
| The Sum aggregation is available.                                                                                                                                                 |          |    |      |    |        |      |        |     |      |     |      |       |
| The Sum aggregation performs as specified.                                                                                                                                        |          |    |      |    |        |      |        |     |      |     |      |       |
| The Last Value aggregation is available.                                                                                                                                          |          |    |      |    |        |      |        |     |      |     |      |       |
| The Last Value aggregation performs as specified.                                                                                                                                 |          |    |      |    |        |      |        |     |      |     |      |       |
| The Histogram aggregation is available.                                                                                                                                           |          |    |      |    |        |      |        |     |      |     |      |       |
| The Histogram aggregation performs as specified.                                                                                                                                  |          |    |      |    |        |      |        |     |      |     |      |       |
| The Explicit Bucket Histogram aggregation is available.                                                                                                                           |          |    |      |    |        |      |        |     |      |     |      |       |
| The Explicit Bucket Histogram aggregation performs as specified.                                                                                                                  |          |    |      |    |        |      |        |     |      |     |      |       |
| A MeasurementProcessor allows hooks when a Measurement is recorded by an instrument.                                                                                              |          |    |      |    |        |      |        |     |      |     |      |       |
| A MeasurementProcessor has access to The Measurement, Instrument and Resource.                                                                                                    |          |    |      |    |        |      |        |     |      |     |      |       |
| If a Measurement is reported by a synchronous Instrument, Then a MeasurementProcessor has access to the Baggage, Context and Span associated with the Measurement.                |          |    |      |    |        |      |        |     |      |     |      |       |
| The metric SDK provides a mechanism to sample Exemplars from measurements.                                                                                                        |          |    |      |    |        |      |        |     |      |     |      |       |
| The SDK allows an exemplar to be disabled.                                                                                                                                        |          |    |      |    |        |      |        |     |      |     |      |       |
| A disabled exemplar does not cause any overhead.                                                                                                                                  |          |    |      |    |        |      |        |     |      |     |      |       |
| By default The SDK only samples exemplars from the context of a sampled trace                                                                                                     |          |    |      |    |        |      |        |     |      |     |      |       |
| Exemplar sampling can leverage the configuration of a metric aggregator.                                                                                                          |          |    |      |    |        |      |        |     |      |     |      |       |
| The SDK provides extensible Exemplar sampling hooks.                                                                                                                              |          |    |      |    |        |      |        |     |      |     |      |       |
| The SDK provides an ExemplarFilter sampling hook.                                                                                                                                 |          |    |      |    |        |      |        |     |      |     |      |       |
| The SDK provides an ExemplarReservoir sampling hook.                                                                                                                              |          |    |      |    |        |      |        |     |      |     |      |       |
| The Exemplarfilter provides a method to determine if a measurement should be sampled.                                                                                             |          |    |      |    |        |      |        |     |      |     |      |       |
| The interface has access to the value of the measurement, the complete set of attributes of the measurement, the context of the measurement and the timestamp of the measurement. |          |    |      |    |        |      |        |     |      |     |      |       |
| The ExemplarReservoir interface provides a method to offer measurements to the reservoir and another to collect accumulated Exemplars.                                            |          |    |      |    |        |      |        |     |      |     |      |       |
| The offer method accepts measurements including value, Attributes, Context and timestamp.                                                                                         |          |    |      |    |        |      |        |     |      |     |      |       |
| The offer method has the ability to pull associated trace and span information without needing to record full context.                                                            |          |    |      |    |        |      |        |     |      |     |      |       |
| The offer method does not need to store all measurements it is given and can further sample beyond the ExemplarFilter.                                                            |          |    |      |    |        |      |        |     |      |     |      |       |
| The collect method returns accumulated Exemplars.                                                                                                                                 |          |    |      |    |        |      |        |     |      |     |      |       |
| Exemplars retain any attributes available in The measurement that are not preserved by aggregation or view configuration.                                                         |          |    |      |    |        |      |        |     |      |     |      |       |
| Joining togeTher attributes on an Exemplar with those available on its associated metric data point result in the full set of attributes from the original sample measurement.    |          |    |      |    |        |      |        |     |      |     |      |       |
| The ExemplarReservoir avoids allocations when sampling exemplars.                                                                                                                 |          |    |      |    |        |      |        |     |      |     |      |       |
| The SDK includes a SimpleFixedSizeExemplarReservoir.                                                                                                                              |          |    |      |    |        |      |        |     |      |     |      |       |
| The SDK includes an AlignedHistogramBucketExemplarReservoir.                                                                                                                      |          |    |      |    |        |      |        |     |      |     |      |       |
| By default fixed sized histogram aggregators use AlignedHistogramBucketExemplarReservoir.                                                                                         |          |    |      |    |        |      |        |     |      |     |      |       |
| All other aggregators use SimpleFixedSizeExemplarReservoir.                                                                                                                       |          |    |      |    |        |      |        |     |      |     |      |       |
| The SimpleFixedSizeExemplarReservoir takes a configuration parameter for the size of the reservoir pool.                                                                          |          |    |      |    |        |      |        |     |      |     |      |       |
| The reservoir will accept measurements using an equivalent of the naive reservoir sampling algorithm.                                                                             |          |    |      |    |        |      |        |     |      |     |      |       |
| The AlignedHistogramBucketExemplarReservoir takes a configuration parameter that is the configuration of an Histogram.                                                            |          |    |      |    |        |      |        |     |      |     |      |       |
| The implementation keeps the last seen measurement that falls within an Histogram bucket.                                                                                         |          |    |      |    |        |      |        |     |      |     |      |       |
| The reservoir will accept measurements by using the equivalent of the specified naive algorithm.                                                                                  |          |    |      |    |        |      |        |     |      |     |      |       |
| The metric exporter has access to the pre aggregated metrics data                                                                                                                 |          |    |      |    |        |      |        |     |      |     |      |       |
| The SDK provides a Push and a Pull Metric Exporter.                                                                                                                               |          |    |      |    |        |      |        |     |      |     |      |       |
| The Push exporter provides an export function.                                                                                                                                    |          |    |      |    |        |      |        |     |      |     |      |       |
| The Push exporter export function can not be called concurrently from the same exporter instance.                                                                                 |          |    |      |    |        |      |        |     |      |     |      |       |
| The Push exporter export function does not block indefinitely.                                                                                                                    |          |    |      |    |        |      |        |     |      |     |      |       |
| The Push exporter export function receives a batch of metrics.                                                                                                                    |          |    |      |    |        |      |        |     |      |     |      |       |
| The Push exporter export function returns Success or Failure.                                                                                                                     |          |    |      |    |        |      |        |     |      |     |      |       |
| The Push exporter provides a ForceFlush function.                                                                                                                                 |          |    |      |    |        |      |        |     |      |     |      |       |
| The Push exporter ForceFlush can inform the caller wether it succeeded, failed or timed out.                                                                                      |          |    |      |    |        |      |        |     |      |     |      |       |
| The Push exporter provides a ForceFlush function.                                                                                                                                 |          |    |      |    |        |      |        |     |      |     |      |       |
| The Push exporter provides a shutdown function.                                                                                                                                   |          |    |      |    |        |      |        |     |      |     |      |       |
| The Push exporter shutdown function return Failure after being called once.                                                                                                       |          |    |      |    |        |      |        |     |      |     |      |       |
| The Push exporter shutdown function do not block indefinitely.                                                                                                                    |          |    |      |    |        |      |        |     |      |     |      |       |
| The SDK provides OTEL_METRICS_EXEMPLAR_FILTER.                                                                                                                                    |          |    |      |    |        |      |        |     |      |     |      |       |
| The default value for OTEL_METRICS_EXEMPLAR_FILTER is WITH_SAMPLED_TRACE.                                                                                                         |          |    |      |    |        |      |        |     |      |     |      |       |
| The value of NONE for OTEL_METRICS_EXEMPLAR_FILTER causes no measurements to be eligble for exemplar sampling.                                                                    |          |    |      |    |        |      |        |     |      |     |      |       |
| The value of ALL for OTEL_METRICS_EXEMPLAR_FILTER causes all measurements to be eligble for exemplar sampling.                                                                    |          |    |      |    |        |      |        |     |      |     |      |       |
| The value of WITH_SAMPLED_TRACE for OTEL_METRICS_EXEMPLAR_FILTER causes only measurements s with a sampled parent span in context to be eligble for exemplar sampling.            |          |    |      |    |        |      |        |     |      |     |      |       |

## Resource

| Feature                                                                                                                                     | Optional | Go | Java | JS | Python | Ruby | Erlang | PHP | Rust | C++ | .NET | Swift |
|---------------------------------------------------------------------------------------------------------------------------------------------|----------|----|------|----|--------|------|--------|-----|------|-----|------|-------|
| Create from Attributes                                                                                                                      |          | +  | +    | +  | +      | +    | +      |     | +    | +   | +    | +     |
| Create empty                                                                                                                                |          | +  | +    | +  | +      | +    | +      |     | +    | +   | +    | +     |
| [Merge (v2)](specification/resource/sdk.md#merge)                                                                                           |          | +  | +    |    | +      | +    | +      |     | +    | +   | +    |       |
| Retrieve attributes                                                                                                                         |          | +  | +    | +  | +      | +    | +      |     | +    | +   | +    | +     |
| [Default value](specification/resource/semantic_conventions/README.md#semantic-attributes-with-sdk-provided-default-value) for service.name |          | +  | +    |    | +      | +    | +      |     |      | +   | +    |       |
| [Resource detector](specification/resource/sdk.md#detecting-resource-information-from-the-environment) interface/mechanism                  |          | +  | +    | +  | +      | +    | +      | [-][php225]   | +    | +   | +    | +     |
| [Resource detectors populate Schema URL](specification/resource/sdk.md#detecting-resource-information-from-the-environment)                 |          | +  |      |    |        |      |        |     |      |     |      |       |

## Context Propagation

| Feature                                                                          | Optional | Go | Java | JS | Python | Ruby | Erlang | PHP | Rust | C++ | .NET | Swift |
|----------------------------------------------------------------------------------|----------|----|------|----|--------|------|--------|-----|------|-----|------|-------|
| Create Context Key                                                               |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| Get value from Context                                                           |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| Set value for Context                                                            |          | +  | +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| Attach Context                                                                   |          | N/A| +    | +  | +      | +    | +      | +   | +    | +   | -    | -     |
| Detach Context                                                                   |          | N/A| +    | +  | +      | +    | +      | +   | +    | +   | -    | -     |
| Get current Context                                                              |          | N/A| +    | +  | +      | +    | +      | +   | +    | +   | +    | +     |
| Composite Propagator                                                             |          | +  | +    | +  | +      | +    | N/A    |     | +    | +   | +    | +     |
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
|OTEL_SERVICE_NAME                             | + |    |   |      |    |      |   |    |   |    |     |
|OTEL_LOG_LEVEL                                | - | -  | + | [-][py1059] | +  | + | -  |    | - | -  | -   |
|OTEL_PROPAGATORS                              | - | +  |   | +    | +  | +    | - | -  | - | -  | -   |
|OTEL_BSP_*                                    | - | +  |   | +    | +  | +    | - | +  | - | -  | -   |
|OTEL_EXPORTER_OTLP_*                          | + | +  |   | +    | +  | -    | - | +  | + | -  | -   |
|OTEL_EXPORTER_JAEGER_*                        | + |    |   |      |    | -    | - |    | - | +  | -   |
|OTEL_EXPORTER_ZIPKIN_*                        | - |    |   |      |    | -    | - | -  | - | -  | -   |
|OTEL_TRACES_EXPORTER                          | - | +  |   | +    | +  | +    |   | -  | - |    |     |
|OTEL_METRICS_EXPORTER                         | - | +  |   | +    | -  | -    |   | -  | - | -  | -   |
|OTEL_SPAN_ATTRIBUTE_COUNT_LIMIT               | - | +  |   | +    | +  | -    |   | +  | - |    |     |
|OTEL_SPAN_ATTRIBUTE_VALUE_LENGTH_LIMIT        |   |    |   |      |    |      |   |    |   |    |     |
|OTEL_SPAN_EVENT_COUNT_LIMIT                   | - | +  |   | +    | +  | -    |   | +  | - |    |     |
|OTEL_SPAN_LINK_COUNT_LIMIT                    | - | +  |   | +    | +  | -    |   | +  | - |    |     |
|OTEL_EVENT_ATTRIBUTE_COUNT_LIMIT              |   |    |   |      |    |      |   |    |   |    |     |
|OTEL_LINK_ATTRIBUTE_COUNT_LIMIT               |   |    |   |      |    |      |   |    |   |    |     |
|OTEL_TRACES_SAMPLER                           | - | +  |   | +    | +  | +    |   | -  | - |    |     |
|OTEL_TRACES_SAMPLER_ARG                       | - | +  |   | +    | +  | +    |   | -  | - |    |     |
|OTEL_ATTRIBUTE_VALUE_LENGTH_LIMIT             |   |    |   |      |    |      |   |    |   |    |     |
|OTEL_ATTRIBUTE_COUNT_LIMIT                    |   |    |   |      |    |      |   |    |   |    |     |

## Exporters

| Feature                                                                        | Optional | Go | Java | JS | Python   | Ruby | Erlang | PHP | Rust | C++ | .NET | Swift |
|--------------------------------------------------------------------------------|----------|----|------|----|----------|------|--------|-----|------|-----|------|-------|
| [Exporter interface](specification/trace/sdk.md#span-exporter)                 |          |    | + |    | +           |      |        |     | +    | +   | +    |       |
| [Exporter interface has `ForceFlush`](specification/trace/sdk.md#forceflush-2) |          |    | + |    | [-][py1779] | +    |        |     | -    |     |      |       |
| Standard output (logging)                                                      |          | +  | + | +  | +           | +    | +      | -   | +    | +   | +    | +     |
| In-memory (mock exporter)                                                      |          | +  | + | +  | +           | +    | +      | -   | -    | +   | +    | +     |
| [OTLP](specification/protocol/otlp.md)                                         |          |    |   |    |             |      |        |     |      |     |      |       |
| OTLP/gRPC Exporter                                                             | *        | +  | + | +  | +           |      | +      |     | +    | +   | +    | +     |
| OTLP/HTTP binary Protobuf Exporter                                             | *        | +  | + | +  | +           | +    | +      |     | +    | +   | +    | -     |
| OTLP/HTTP JSON Protobuf Exporter                                               |          | +  | - | +  | [-][py1003] |      | -      |     |      | +   | -    | -     |
| OTLP/HTTP gzip Content-Encoding support                                        | X        | +  | + | +  | +           | +    | -      |     |      | -   | -    | -     |
| Concurrent sending                                                             |          | -  | + | +  | [-][py1108] |      | -      |     | +    | -   | -    | -     |
| Honors retryable responses with backoff                                        | X        | +  |   | +  | +           | +    | -      |     |      | -   | -    | -     |
| Honors non-retryable responses                                                 | X        | +  |   | -  | +           | +    | -      |     |      | -   | -    | -     |
| Honors throttling response                                                     | X        | +  |   | -  | +           | +    | -      |     |      | -   | -    | -     |
| Multi-destination spec compliance                                              | X        | +  |   |    | [-][py1109] |      | -      |     |      | -   | -    | -     |
| SchemaURL in ResourceSpans and InstrumentationLibrarySpans                     |          | +  |   |    |             |      |        |     |      |     |      |       |
| SchemaURL in ResourceMetrics and InstrumentationLibraryMetrics                 |          |    |   |    |             |      |        |     |      |     |      |       |
| SchemaURL in ResourceLogs and InstrumentationLibraryLogs                       |          |    |   |    |             |      |        |     |      |     |      |       |
| [Zipkin](specification/trace/sdk_exporters/zipkin.md)                          |          |    |   |    |             |      |        |     |      |     |      |       |
| Zipkin V1 JSON                                                                 | X        | -  | + |    | +           | -    | -      | -   | -    | -   | -    | -     |
| Zipkin V1 Thrift                                                               | X        | -  | + |    | [-][py1174] | -    | -      | -   | -    | -   | -    | -     |
| Zipkin V2 JSON                                                                 | *        | +  | + |    | +           | +    | -      | +   | +    | +   | +    | +     |
| Zipkin V2 Protobuf                                                             | *        | -  | + |    | +           | -    | +      |     | -    | -   | -    | -     |
| Service name mapping                                                           |          | +  | + | +  | +           | +    | +      | +   | +    | +   | +    | +     |
| SpanKind mapping                                                               |          | +  | + | +  | +           | +    | +      | +   | +    | +   | +    | +     |
| InstrumentationLibrary mapping                                                 |          | +  | + | -  | +           | +    | -      | -   | +    | +   | +    | +     |
| Boolean attributes                                                             |          | +  | + | +  | +           | +    | +      | +   | +    | +   | +    | +     |
| Array attributes                                                               |          | +  | + | +  | +           | +    | +      | +   | +    | +   | +    | +     |
| Status mapping                                                                 |          | +  | + | +  | +           | +    | +      | +   | +    | +   | +    | +     |
| Error Status mapping                                                           |          | +  | + |    |             | +    |        |     | +    | +   | +    | -     |
| Event attributes mapping to Annotations                                        |          | +  | + | +  | +           | +    | +      | +   | +    | +   | +    | +     |
| Integer microseconds in timestamps                                             |          | N/A| + |    | +           | +    |        |     | +    | +   | +    | +     |
| [Jaeger](specification/trace/sdk_exporters/jaeger.md)                          |          |    |   |    |             |      |        |     |      |     |      |       |
| Jaeger Thrift over UDP                                                         | *        | +  |   |    | +           | +    |        |     | +    | +   | +    | +     |
| Jaeger Protobuf via gRPC                                                       | *        | -  | + |    | [-][py1437] | -    |        |     |      | -   | -    | -     |
| Jaeger Thrift over HTTP                                                        | *        | +  | + |    | +           | +    |        |     | +    | +   | -    | -     |
| Service name mapping                                                           |          | +  | + |    | +           | +    |        |     |      | +   | +    | +     |
| Resource to Process mapping                                                    |          | +  | + |    | +           | +    |        |     | +    | -   | +    | -     |
| InstrumentationLibrary mapping                                                 |          | +  | + |    | +           | +    |        |     | +    | -   | +    | -     |
| Status mapping                                                                 |          | +  | + |    | +           | +    |        |     | +    | +   | +    | +     |
| Error Status mapping                                                           |          | +  | + |    | +           | +    |        |     | +    | +   | +    | -     |
| Events converted to Logs                                                       |          | +  | + |    | +           | +    |        |     | +    | -   | +    | +     |
| OpenCensus                                                                     |          |    |   |    |             |      |        |     |      |     |      |       |
| TBD                                                                            |          |    |   |    |             |      |        |     |      |     |      |       |
| Prometheus                                                                     |          |    |   |    |             |      |        |     |      |     |      |       |
| TBD                                                                            |          |    |   |    |             |      |        |     |      |     |      |       |

[py1003]: https://github.com/open-telemetry/opentelemetry-python/issues/1003
[py1059]: https://github.com/open-telemetry/opentelemetry-python/issues/1059
[py1108]: https://github.com/open-telemetry/opentelemetry-python/issues/1108
[py1109]: https://github.com/open-telemetry/opentelemetry-python/issues/1109
[py1174]: https://github.com/open-telemetry/opentelemetry-python/issues/1174
[py1437]: https://github.com/open-telemetry/opentelemetry-python/issues/1437
[py1779]: https://github.com/open-telemetry/opentelemetry-python/issues/1779
[php225]: https://github.com/open-telemetry/opentelemetry-php/issues/225
