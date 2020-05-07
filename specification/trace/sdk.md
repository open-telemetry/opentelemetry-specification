# Tracing SDK

<details>

<summary>Table of Contents</summary>

* [Sampling](#sampling)
* [Tracer Creation](#tracer-creation)
* [Span Processor](#span-processor)
* [Span Exporter](#span-exporter)

</details>

## Sampling

Sampling is a mechanism to control the noise and overhead introduced by
OpenTelemetry by reducing the number of samples of traces collected and sent to
the backend.

Sampling may be implemented on different stages of a trace collection.
OpenTelemetry API defines a `Sampler` interface that can be used at
instrumentation points by libraries to check the `SamplingResult` early and
optimize the amount of telemetry that needs to be collected.

All other sampling algorithms may be implemented on SDK layer in exporters, or
even out of process in Agent or Collector.

The OpenTelemetry API has two properties responsible for the data collection:

* `IsRecording` field of a `Span`. If `true` the current `Span` records
  tracing events (attributes, events, status, etc.), otherwise all tracing
  events are dropped. Users can use this property to determine if expensive
  trace events can be avoided. [Span Processors](#span-processor) will receive
  all spans with this flag set. However, [Span Exporter](#span-exporter) will
  not receive them unless the `Sampled` flag was set.
* `Sampled` flag in `TraceFlags` on `SpanContext`. This flag is propagated via
  the `SpanContext` to child Spans. For more details see the [W3C Trace Context
  specification][trace-flags]. This flag indicates that the `Span` has been
  `sampled` and will be exported. [Span Processor](#span-processor) and [Span
  Exporter](#span-exporter) will receive spans with the `Sampled` flag set for
  processing.

The flag combination `SampledFlag == false` and `IsRecording == true`
means that the current `Span` does record information, but most likely the child
`Span` will not.

The flag combination `SampledFlag == true` and `IsRecording == false`
could cause gaps in the distributed trace, and because of this OpenTelemetry API
MUST NOT allow this combination.

The SDK defines the two interfaces [`Sampler`](#sampler) and
[`Decision`](#decision) as well as a set of [built-in
samplers](#built-in-samplers).

### Sampler

`Sampler` interface allows to create custom samplers which will return a
sampling `SamplingResult` based on information that is typically available just
before the `Span` was created.

#### ShouldSample

Returns the sampling Decision for a `Span` to be created.

**Required arguments:**

* `SpanContext` of a parent `Span`. Typically extracted from the wire. Can be
  `null`.
* `TraceId` of the `Span` to be created. It can be different from the `TraceId`
  in the `SpanContext`. Typically in situations when the `Span` to be created
  starts a new Trace.
* `SpanId` of the `Span` to be created.
* Name of the `Span` to be created.
* `SpanKind`
* Initial set of `Attributes` for the `Span` being constructed
* Collection of links that will be associated with the `Span` to be created.
  Typically useful for batch operations, see
  [Links Between Spans](../overview.md#links-between-spans).

**Return value:**

It produces an output called `SamplingResult` which contains:

* A sampling `Decision`. One of the following enum values:
  * `NOT_RECORD` - `IsRecording() == false`, span will not be recorded and all events and attributes
  will be dropped.
  * `RECORD` - `IsRecording() == true`, but `Sampled` flag MUST NOT be set.
  * `RECORD_AND_SAMPLED` - `IsRecording() == true` AND `Sampled` flag` MUST be set.
* A set of span Attributes that will also be added to the `Span`.
  * The list of attributes returned by `SamplingResult` MUST be immutable.
  Caller may call this method any number of times and can safely cache the
  returned value.

#### GetDescription

Returns the sampler name or short description with the configuration. This may
be displayed on debug pages or in the logs. Example:
`"ProbabilitySampler{0.000100}"`.

Description MUST NOT change over time and caller can cache the returned value.

### Built-in samplers

These are the default samplers implemented in the OpenTelemetry SDK:

* ALWAYS_ON
  * This will be used as a default.
  * Description MUST be `AlwaysOnSampler`.
* ALWAYS_OFF
  * Description MUST be `AlwaysOffSampler`.
* ALWAYS_PARENT
  * `Returns RECORD_AND_SAMPLED` if `SampledFlag` is set to true on parent
  SpanContext and `NOT_RECORD` otherwise.
  * Description MUST be `AlwaysParentSampler`.
* Probability
  * The default behavior should be to trust the parent `SampledFlag`. However
  there should be configuration to change this.
  * The default behavior is to apply the sampling probability only for Spans
  that are root spans (no parent) and Spans with remote parent. However there
  should be configuration to change this to "root spans only", or "all spans".
  * Description MUST be `ProbabilitySampler{0.000100}`.

#### Probability Sampler algorithm

TODO: Add details about how the probability sampler is implemented as a function
of the `TraceID`.

## Tracer Creation

New `Tracer` instances are always created through a `TracerProvider` (see
[API](api.md#obtaining-a-tracer)).  The `name` and `version` arguments
supplied to the `TracerProvider` must be used to create a
[`Resource`](../resource/sdk.md) instance which is stored on the created `Tracer`.

All configuration objects (SDK specific) and extension points (span processors,
propagators) must be provided to the `TracerProvider`. `Tracer` instances must
not duplicate this data (unless for read-only access) to avoid that different
`Tracer` instances of a `TracerProvider` have different versions of these data.

The readable representations of all `Span` instances created by a `Tracer` must
provide a `getLibraryResource` method that returns this `Resource` information
held by the `Tracer`.

## Span processor

Span processor is an interface which allows hooks for span start and end method
invocations. The span processors are invoked only when
[`IsRecording`](api.md#isrecording) is true.

Built-in span processors are responsible for batching and conversion of spans to
exportable representation and passing batches to exporters.

Span processors can be registered directly on SDK `TracerProvider` and they are
invoked in the same order as they were registered.

All `Tracer` instances created by a `TracerProvider` share the same span processors.
Changes to this collection reflect in all `Tracer` instances.
Implementation-wise, this could mean that `Tracer` instances have a reference to
their `TracerProvider` and can access span processor objects only via this
reference.

Manipulation of the span processors collection must only happen on `TracerProvider`
instances. This means methods like `addSpanProcessor` must be implemented on
`TracerProvider`.

Each processor registered on `TracerProvider` is a start of pipeline that consist
of span processor and optional exporter. SDK MUST allow to end each pipeline with
individual exporter.

SDK MUST allow users to implement and configure custom processors and decorate
built-in processors for advanced scenarios such as tagging or filtering.

The following diagram shows `SpanProcessor`'s relationship to other components
in the SDK:

```
  +-----+--------------+   +-------------------------+   +-------------------+
  |     |              |   |                         |   |                   |
  |     |              |   | BatchExporterProcessor  |   |    SpanExporter   |
  |     |              +---> SimpleExporterProcessor +--->  (JaegerExporter) |
  |     |              |   |                         |   |                   |
  | SDK | Span.start() |   +-------------------------+   +-------------------+
  |     | Span.end()   |
  |     |              |   +---------------------+
  |     |              |   |                     |
  |     |              +---> ZPagesProcessor     |
  |     |              |   |                     |
  +-----+--------------+   +---------------------+
```

### Interface definition

#### OnStart(Span)

`OnStart` is called when a span is started. This method is called synchronously
on the thread that started the span, therefore it should not block or throw
exceptions.

**Parameters:**

* `Span` - a readable span object.

**Returns:** `Void`

#### OnEnd(Span)

`OnEnd` is called when a span is ended. This method is called synchronously on
the execution thread, therefore it should not block or throw an exception.

**Parameters:**

* `Span` - a readable span object.

**Returns:** `Void`

#### Shutdown()

Shuts down the processor. Called when SDK is shut down. This is an opportunity
for processor to do any cleanup required.

Shutdown should be called only once for each `Processor` instance. After the
call to shutdown subsequent calls to `onStart`, `onEnd`, or `forceFlush` are not allowed.

Shutdown should not block indefinitely. Language library authors can decide if
they want to make the shutdown timeout configurable.

#### ForceFlush()

Export all ended spans to the configured `Exporter` that have not yet been exported.

`ForceFlush` should only be called in cases where it is absolutely necessary, such as when using some FaaS providers that may suspend the process after an invocation, but before the `Processor` exports the completed spans.

`ForceFlush` should not block indefinitely. Language library authors can decide if they want to make the flush timeout configurable.

### Built-in span processors

The standard OpenTelemetry SDK MUST implement both simple and batch processors,
as described below. Other common processing scenarios should be first considered
for implementation out-of-process in [OpenTelemetry Collector](../overview.md#collector)

#### Simple processor

This is an implementation of `SpanProcessor` which passes finished spans
and passes the export-friendly span data representation to the configured
`SpanExporter`, as soon as they are finished.

**Configurable parameters:**

* `exporter` - the exporter where the spans are pushed.

#### Batching processor

This is an implementation of the `SpanProcessor` which create batches of finished
spans and passes the export-friendly span data representations to the
configured `SpanExporter`.

**Configurable parameters:**

* `exporter` - the exporter where the spans are pushed.
* `maxQueueSize` - the maximum queue size. After the size is reached spans are
  dropped. The default value is `2048`.
* `scheduledDelayMillis` - the delay interval in milliseconds between two
  consecutive exports. The default value is `5000`.
* `exporterTimeoutMillis` - how long the export can run before it is cancelled.
  The default value is `30000`.
* `maxExportBatchSize` - the maximum batch size of every export. It must be
  smaller or equal to `maxQueueSize`. The default value is `512`.

## Span Exporter

`Span Exporter` defines the interface that protocol-specific exporters must
implement so that they can be plugged into OpenTelemetry SDK and support sending
of telemetry data.

The goal of the interface is to minimize burden of implementation for
protocol-dependent telemetry exporters. The protocol exporter is expected to be
primarily a simple telemetry data encoder and transmitter.

### Interface Definition

The exporter must support two functions: **Export** and **Shutdown**. In
strongly typed languages typically there will be 2 separate `Exporter`
interfaces, one that accepts spans (SpanExporter) and one that accepts metrics
(MetricsExporter).

#### `Export(batch)`

Exports a batch of telemetry data. Protocol exporters that will implement this
function are typically expected to serialize and transmit the data to the
destination.

Export() will never be called concurrently for the same exporter instance.
Export() can be called again only after the current call returns.

Export() must not block indefinitely, there must be a reasonable upper limit
after which the call must time out with an error result (`Failure`).

Any retry logic that is required by the exporter is the responsibility
of the exporter. The default SDK SHOULD NOT implement retry logic, as
the required logic is likely to depend heavily on the specific protocol
and backend the spans are being sent to.

**Parameters:**

batch - a batch of telemetry data. The exact data type of the batch is language
specific, typically it is a list of telemetry items, e.g. for spans in Java it
will be typically `Collection<ExportableSpan>`.

Note that the data type for a span for illustration purposes here is written as
an imaginary type ExportableSpan (similarly for metrics it would be e.g.
ExportableMetrics). The actual data type must be specified by language library
authors, it should be able to represent the span data that can be read by the
exporter.

**Returns:** ExportResult:

ExportResult is one of:

* `Success` - The batch has been successfully exported.
  For protocol exporters this typically means that the data is sent over
  the wire and delivered to the destination server.
* `Failure` - exporting failed. The batch must be dropped. For example, this
  can happen when the batch contains bad data and cannot be serialized.

#### `Shutdown()`

Shuts down the exporter. Called when SDK is shut down. This is an opportunity
for exporter to do any cleanup required.

`Shutdown` should be called only once for each `Exporter` instance. After the
call to `Shutdown` subsequent calls to `Export` are not allowed and should
return a `Failure` result.

`Shutdown` should not block indefinitely (e.g. if it attempts to flush the data
and the destination is unavailable). Language library authors can decide if they
want to make the shutdown timeout configurable.

### Further Language Specialization

Based on the generic interface definition laid out above library authors must
define the exact interface for the particular language.

Authors are encouraged to use efficient data structures on the interface
boundary that are well suited for fast serialization to wire formats by protocol
exporters and minimize the pressure on memory managers. The latter typically
requires understanding of how to optimize the rapidly-generated, short-lived
telemetry data structures to make life easier for the memory manager of the
specific language. General recommendation is to minimize the number of
allocations and use allocation arenas where possible, thus avoiding explosion of
allocation/deallocation/collection operations in the presence of high rate of
telemetry data generation.

#### Examples

These are examples on what the `Exporter` interface can look like in specific
languages. Examples are for illustration purposes only. Language library authors
are free to deviate from these provided that their design remain true to the
spirit of `Exporter` concept.

##### Go SpanExporter Interface

```go
type SpanExporter interface {
    Export(batch []ExportableSpan) ExportResult
    Shutdown()
}

type ExportResult struct {
    Code         ExportResultCode
    WrappedError error
}

type ExportResultCode int

const (
    Success ExportResultCode = iota
    Failure
)
```

##### Java SpanExporter Interface

```java
public interface SpanExporter {
 public enum ResultCode {
   Success, Failure
 }

 ResultCode export(Collection<ExportableSpan> batch);
 void shutdown();
}
```

[trace-flags]: https://www.w3.org/TR/trace-context/#trace-flags
