# Tracing SDK

<details><summary>Table of Contents</summary>

* [Span Processor](#span-processor)
* [Span Exporter](#span-exporter)

</details>

## Span processor

Span processor is an interface which allows hooks for span start and end method
invocations. The span processors are invoked only when
[`IsRecordingEvents`](api-tracing.md#isrecordingevents) is true. This interface
must be used to implement [span exporter](#span-exporter) to batch and convert
spans.

Span processors can be registered directly on SDK Tracer and they are invoked in
the same order as they were registered.

The following diagram shows `SpanProcessor`'s relationship to other components
in the SDK:

```
  +-----+---------------+   +---------------------+   +-------------------+
  |     |               |   |                     |   |                   |
  |     |               |   | BatchProcessor      |   |    SpanExporter   | 
  |     |               +---> SimpleProcessor     +--->  (JaegerExporter) |
  | SDK | SpanProcessor |   |                     |   |                   |
  |     |               |   +---------------------+   +-------------------+ 
  |     |               |
  |     |               |   +---------------------+
  |     |               |   |                     |
  |     |               +---> ZPagesProcessor     |
  |     |               |   |                     |
  +-----+---------------+   +---------------------+
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
call to shutdown subsequent calls to `onStart` or `onEnd` are not allowed.

Shutdown should not block indefinitely. Language library authors can decide if
they want to make the shutdown timeout to be configurable.

### Built-in span processors

#### Simple processor

The implementation of `SpanProcessor` that passes ended span directly to the
configured `SpanExporter`.

**Configurable parameters:**

* `exporter` - the exporter where the spans are pushed.

#### Batching processor

The implementation of the `SpanProcessor` that batches ended spans and pushes
them to the configured `SpanExporter`.

First the spans are added to a synchronized queue, then exported to the exporter
pipeline in batches. The implementation is responsible for managing the span
queue and sending batches of spans to the exporters. This processor can cause
high contention in a very high traffic service.

**Configurable parameters:**

* `exporter` - the exporter where the spans are pushed.
* `maxQueueSize` - the maximum queue size. After the size is reached spans are
  dropped. The default value is `2048`.
* `scheduledDelayMillis` - the delay interval in milliseconds between two
  consecutive exports. The default value is `5000`.
* `maxExportBatchSize` - the maximum batch size of every export. It must be
  smaller or equal to `maxQueueSize`. The default value is `512`.

## Span Exporter

`Span Exporter` defines the interface that protocol-specific exporters must
implement so that they can be plugged into OpenTelemetry SDK and support sending
of telemetry data.

The goals of the interface are:

* Minimize burden of implementation for protocol-dependent telemetry exporters.
  The protocol exporter is expected to be primarily a simple telemetry data
  encoder and transmitter.
* Allow implementing helpers as composable components that use the same
  chainable `Exporter` interface. SDK authors are encouraged to implement common
  functionality such as queuing, batching, tagging, etc. as helpers. This
  functionality will be applicable regardless of what protocol exporter is used.

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
after which the call must time out with an error result (typically
FailedRetryable).

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

* Success - batch is successfully exported. For protocol exporters this
  typically means that the data is sent over the wire and delivered to the
  destination server.
* FailedNotRetryable - exporting failed. The caller must not retry exporting the
  same batch. The batch must be dropped. This for example can happen when the
  batch contains bad data and cannot be serialized.
* FailedRetryable - cannot export to the destination. The caller should record
  the error and may retry exporting the same batch after some time. This for
  example can happen when the destination is unavailable, there is a network
  error or endpoint does not exist.

#### `Shutdown()`

Shuts down the exporter. Called when SDK is shut down. This is an opportunity
for exporter to do any cleanup required.

`Shutdown` should be called only once for each `Exporter` instance. After the
call to `Shutdown` subsequent calls to `Export` are not allowed and should
return FailedNotRetryable error.

`Shutdown` should not block indefinitely (e.g. if it attempts to flush the data
and the destination is unavailable). Language library authors can decide if they
want to make the shutdown timeout to be configurable.

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
    FailedNotRetryable
    FailedRetryable
)
```

##### Java SpanExporter Interface

```java
public interface SpanExporter {
 public enum ResultCode {
   Success, FailedNotRetryable, FailedRetryable
 }

 ResultCode export(Collection<ExportableSpan> batch);
 void shutdown();
}
```
