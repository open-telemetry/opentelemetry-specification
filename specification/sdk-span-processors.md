# Span processor

Span processor is an interface which allows hooks for span start and end method invocations.
The span processors are invoked only when [`IsRecordingEvents`](api-tracing.md#isrecordingevents) is true. This interface can be used to implement [span exporter](sdk-exporter.md) to batch and convert spans.

Span processors can be registered directly on SDK Tracer and they are invoked in the same order as they were registered.

The following diagram shows `SpanProcessor`'s relationship to other components in the SDK:

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

## Interface definition

### OnStart(Span)

`OnStart` is called when a span is started.
This method is called synchronously on the thread that started the span, therefore it should not block or throw exceptions.

**Parameters:**

* `Span` - a readable span object.

**Returns:** `Void`

### OnEnd(Span)

`OnEnd` is called when a span is ended.
This method is called synchronously on the execution thread, therefore it should not block or throw an exception.

**Parameters:**

* `Span` - a readable span object.

**Returns:** `Void`

### Shutdown()

Shuts down the processor. Called when SDK is shut down. This is an opportunity for processor to do any cleanup required.

Shutdown should be called only once for each `Processor` instance. After the call to shutdown subsequent calls to `onStart` or `onEnd` are not allowed.

Shutdown should not block indefinitely. Language library authors can decide if they want to make the shutdown timeout to be configurable.

## Built-in span processors

### Simple processor

The implementation of `SpanProcessor` that passes ended span directly to the configured `SpanExporter`.

**Configurable parameters:**

* `exporter` - the exporter where the spans are pushed.

### Batching processor

The implementation of the `SpanProcessor` that batches ended spans and pushes them to the configured `SpanExporter`.

First the spans are added to a synchronized queue, then exported to the exporter pipeline in batches.
The implementation is responsible for managing the span queue and sending batches of spans to the exporters.
This processor can cause high contention in a very high traffic service.

**Configurable parameters:**

* `exporter` - the exporter where the spans are pushed.
* `maxQueueSize` - the maximum queue size. After the size is reached spans are dropped. The default value is `2048`.
* `scheduledDelayMillis` - the delay interval in milliseconds between two consecutive exports. The default value is `5000`.
* `maxExportBatchSize` - the maximum batch size of every export. It must be smaller or equal to `maxQueueSize`. The default value is `512`.
