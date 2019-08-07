# Span processor

Span processor is an interface which allows synchronous hooks for span start and end method invocations.
The span processors are invoked only on sampled spans.

## Interface definition

### OnStart(SpanData)

`OnStart` is called when a span is started and `Span.isRecordingEvents()` is true. 
This method is called synchronously on the execution thread, therefore it should not block or throw an exception.

**Parameters:**

* `SpanData` - a readable span object.

**Returns:** `Void`

### OnEnd(SpanData)

`OnEnd` is called when a span is ended and `Span.isRecordingEvents()` is true.
This method is called synchronously on the execution thread, therefore it should not block or throw an exception.

**Parameters:**

* `SpanData` - a readable span object.

**Returns:** `Void`

### Shutdown()

Shuts down the processor. Called when SDK is shut down. This is an opportunity for processor to do any cleanup required.

`Shutdown` should be called only once for each `Processor` instance. After the call to `Shutdown` subsequent calls to `onStart` or `onEnd` are not allowed.

`Shutdown` should not block indefinitely. Language library authors can decide if they want to make the shutdown timeout to be configurable.

## Built-in span processors

### Simple processor

The implementation of `SpanProcessor` that passes ended span directly to the configured `SpanExporter`.

**Configurable parameters:**

* `exporter` - the exporter where the spans are pushed.

### Batching processor

The implementation of the `SpanProcessor` that batches ended spans and pushes them to the configured `SpanExporter`.

First the spans are added to a synchronized queue, then exported to the exporter pipeline in batches.
When the queue gets half full a preemptive notification is sent to the worker thread to wake up and start a new export cycle.
Thi processor can cause high contention in a very high traffic service.

**Configurable parameters:**

* `exporter` - the exporter where the spans are pushed.
* `maxQueueSize` - the maximum size of the queue. After the size is reached spans are dropped.
* `scheduledDelayMilllis` - the delay interval between two consecutive exports.
* `maxExportBatchSize` - the maximum batch size of every export. It must be smaller or equal to `maxQueueSize`.
