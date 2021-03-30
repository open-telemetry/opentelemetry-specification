# Tracing SDK

**Status**: [Stable](../document-status.md)

<details>

<summary>Table of Contents</summary>

* [Tracer Provider](#tracer-provider)
* [Additional Span Interfaces](#additional-span-interfaces)
* [Sampling](#sampling)
* [Span Limits](#span-limits)
* [Id Generator](#id-generators)
* [Span Processor](#span-processor)
* [Span Exporter](#span-exporter)

</details>

## Tracer Provider

### Tracer Creation

New `Tracer` instances are always created through a `TracerProvider` (see
[API](api.md#tracerprovider)). The `name` and `version` arguments
supplied to the `TracerProvider` must be used to create an
[`InstrumentationLibrary`][otep-83] instance which is stored on the created
`Tracer`.

Configuration (i.e., [SpanProcessors](#span-processor), [IdGenerator](#id-generators),
[SpanLimits](#span-limits) and [`Sampler`](#sampling)) MUST be managed solely by
the `TracerProvider` and it MUST provide some way to configure all of them that
are implemented in the SDK, at least when creating or initializing it.

The TracerProvider MAY provide methods to update the configuration. If
configuration is updated (e.g., adding a `SpanProcessor`),
the updated configuration MUST also apply to all already returned `Tracers`
(i.e. it MUST NOT matter whether a `Tracer` was obtained from the
`TracerProvider` before or after the configuration change).
Note: Implementation-wise, this could mean that `Tracer` instances have a
reference to their `TracerProvider` and access configuration only via this
reference.

### Shutdown

This method provides a way for provider to do any cleanup required.

`Shutdown` MUST be called only once for each `TracerProvider` instance. After
the call to `Shutdown`, subsequent attempts to get a `Tracer` are not allowed. SDKs
SHOULD return a valid no-op Tracer for these calls, if possible.

`Shutdown` SHOULD provide a way to let the caller know whether it succeeded,
failed or timed out.

`Shutdown` SHOULD complete or abort within some timeout. `Shutdown` can be
implemented as a blocking API or an asynchronous API which notifies the caller
via a callback or an event. OpenTelemetry client authors can decide if they want to
make the shutdown timeout configurable.

`Shutdown` MUST be implemented at least by invoking `Shutdown` within all internal processors.

### ForceFlush

This method provides a way for provider to immediately export all spans that have not yet been exported for all the internal processors.

`ForceFlush` SHOULD provide a way to let the caller know whether it succeeded,
failed or timed out.

`ForceFlush` SHOULD complete or abort within some timeout. `ForceFlush` can be
implemented as a blocking API or an asynchronous API which notifies the caller
via a callback or an event. OpenTelemetry client authors can decide if they want to
make the flush timeout configurable.

`ForceFlush` MUST invoke `ForceFlush` on all registered `SpanProcessors`.

## Additional Span Interfaces

The [API-level definition for Span's interface](api.md#span-operations)
only defines write-only access to the span.
This is good because instrumentations and applications are not meant to use the data
stored in a span for application logic.
However, the SDK needs to eventually read back the data in some locations.
Thus, the SDK specification defines sets of possible requirements for
`Span`-like parameters:

* **Readable span**: A function receiving this as argument MUST be able to
  access all information that was added to the span,
  as listed [in the API spec](api.md#span-data-members).
  In particular, it MUST also be able to access
  the `InstrumentationLibrary` and `Resource` information (implicitly)
  associated with the span.
  It must also be able to reliably determine whether the Span has ended
  (some languages might implement this by having an end timestamp of `null`,
  others might have an explicit `hasEnded` boolean).

  A function receiving this as argument might not be able to modify the Span.

  Note: Typically this will be implemented with a new interface or
  (immutable) value type.
  In some languages SpanProcessors may have a different readable span type
  than exporters (e.g. a `SpanData` type might contain an immutable snapshot and
  a `ReadableSpan` interface might read information directly from the same
  underlying data structure that the `Span` interface manipulates).

* **Read/write span**: A function receiving this as argument must have access to
  both the full span API as defined in the
  [API-level definition for span's interface](api.md#span-operations) and
  additionally must be able to retrieve all information that was added to the span
  (as with *readable span*).

  It MUST be possible for functions being called with this
  to somehow obtain the same `Span` instance and type
  that the [span creation API](api.md#span-creation) returned (or will return) to the user
  (for example, the `Span` could be one of the parameters passed to such a function,
  or a getter could be provided).

## Sampling

Sampling is a mechanism to control the noise and overhead introduced by
OpenTelemetry by reducing the number of samples of traces collected and sent to
the backend.

Sampling may be implemented on different stages of a trace collection. The
earliest sampling could happen before the trace is actually created, and the
latest sampling could happen on the Collector which is out of process.

The OpenTelemetry API has two properties responsible for the data collection:

* `IsRecording` field of a `Span`. If `false` the current `Span` discards all
  tracing data (attributes, events, status, etc.). Users can use this property
  to determine if collecting expensive trace data can be avoided. [Span
  Processor](#span-processor) MUST receive only those spans which have this
  field set to `true`. However, [Span Exporter](#span-exporter) SHOULD NOT
  receive them unless the `Sampled` flag was also set.
* `Sampled` flag in `TraceFlags` on `SpanContext`. This flag is propagated via
  the `SpanContext` to child Spans. For more details see the [W3C Trace Context
  specification](https://www.w3.org/TR/trace-context/#sampled-flag). This flag indicates that the `Span` has been
  `sampled` and will be exported. [Span Exporters](#span-exporter) MUST
  receive those spans which have `Sampled` flag set to true and they SHOULD NOT receive the ones
  that do not.

The flag combination `SampledFlag == false` and `IsRecording == true`
means that the current `Span` does record information, but most likely the child
`Span` will not.

The flag combination `SampledFlag == true` and `IsRecording == false`
could cause gaps in the distributed trace, and because of this OpenTelemetry API
MUST NOT allow this combination.

<a name="recording-sampled-reaction-table"></a>

The following table summarizes the expected behavior for each combination of
`IsRecording` and `SampledFlag`.

| `IsRecording` | `Sampled` Flag | Span Processor receives Span? | Span Exporter receives Span? |
| ------------- | -------------- | ----------------------------- | ---------------------------- |
| true          | true           | true                          | true                         |
| true          | false          | true                          | false                        |
| false         | true           | Not allowed                   | Not allowed                  |
| false         | false          | false                         | false                        |

The SDK defines the interface [`Sampler`](#sampler) as well as a set of
[built-in samplers](#built-in-samplers) and associates a `Sampler` with each [`TracerProvider`].

### SDK Span creation

When asked to create a Span, the SDK MUST act as if doing the following in order:

1. If there is a valid parent trace ID, use it. Otherwise generate a new trace ID
   (note: this must be done before calling `ShouldSample`, because it expects
   a valid trace ID as input).
2. Query the `Sampler`'s [`ShouldSample`](#shouldsample) method
   (Note that the [built-in `ParentBasedSampler`](#parentbased) can be used to
   use the sampling decision of the parent,
   translating a set SampledFlag to RECORD and an unset one to DROP).
3. Generate a new span ID for the `Span`, independently of the sampling decision.
   This is done so other components (such as logs or exception handling) can rely on
   a unique span ID, even if the `Span` is a non-recording instance.
4. Create a span depending on the decision returned by `ShouldSample`:
   see description of [`ShouldSample`'s](#shouldsample) return value below
   for how to set `IsRecording` and `Sampled` on the Span,
   and the [table above](#recording-sampled-reaction-table) on whether
   to pass the `Span` to `SpanProcessor`s.
   A non-recording span MAY be implemented using the same mechanism as when a
   `Span` is created without an SDK installed or as described in
   [wrapping a SpanContext in a Span](api.md#wrapping-a-spancontext-in-a-span).

### Sampler

`Sampler` interface allows users to create custom samplers which will return a
sampling `SamplingResult` based on information that is typically available just
before the `Span` was created.

#### ShouldSample

Returns the sampling Decision for a `Span` to be created.

**Required arguments:**

* [`Context`](../context/context.md) with parent `Span`.
  The Span's SpanContext may be invalid to indicate a root span.
* `TraceId` of the `Span` to be created.
  If the parent `SpanContext` contains a valid `TraceId`, they MUST always match.
* Name of the `Span` to be created.
* `SpanKind` of the `Span` to be created.
* Initial set of `Attributes` of the `Span` to be created.
* Collection of links that will be associated with the `Span` to be created.
  Typically useful for batch operations, see
  [Links Between Spans](../overview.md#links-between-spans).

**Return value:**

It produces an output called `SamplingResult` which contains:

* A sampling `Decision`. One of the following enum values:
  * `DROP` - `IsRecording() == false`, span will not be recorded and all events and attributes
  will be dropped.
  * `RECORD_ONLY` - `IsRecording() == true`, but `Sampled` flag MUST NOT be set.
  * `RECORD_AND_SAMPLE` - `IsRecording() == true` AND `Sampled` flag MUST be set.
* A set of span Attributes that will also be added to the `Span`. The returned
object must be immutable (multiple calls may return different immutable objects).
* A `Tracestate` that will be associated with the `Span` through the new
  `SpanContext`.
  If the sampler returns an empty `Tracestate` here, the `Tracestate` will be cleared,
  so samplers SHOULD normally return the passed-in `Tracestate` if they do not intend
  to change it.

#### GetDescription

Returns the sampler name or short description with the configuration. This may
be displayed on debug pages or in the logs. Example:
`"TraceIdRatioBased{0.000100}"`.

Description MUST NOT change over time and caller can cache the returned value.

### Built-in samplers

OpenTelemetry supports a number of built-in samplers to choose from.
The default sampler is `ParentBased(root=AlwaysOn)`.

#### AlwaysOn

* Returns `RECORD_AND_SAMPLE` always.
* Description MUST be `AlwaysOnSampler`.

#### AlwaysOff

* Returns `DROP` always.
* Description MUST be `AlwaysOffSampler`.

#### TraceIdRatioBased

* The `TraceIdRatioBased` MUST ignore the parent `SampledFlag`. To respect the
parent `SampledFlag`, the `TraceIdRatioBased` should be used as a delegate of
the `ParentBased` sampler specified below.
* Description MUST return a string of the form `"TraceIdRatioBased{RATIO}"`
  with `RATIO` replaced with the Sampler instance's trace sampling ratio
  represented as a decimal number. The precision of the number SHOULD follow
  implementation language standards and SHOULD be high enough to identify when
  Samplers have different ratios. For example, if a TraceIdRatioBased Sampler
  had a sampling ratio of 1 to every 10,000 spans it COULD return
  `"TraceIdRatioBased{0.000100}"` as its description.

TODO: Add details about how the `TraceIdRatioBased` is implemented as a function
of the `TraceID`. [#1413](https://github.com/open-telemetry/opentelemetry-specification/issues/1413)

##### Requirements for `TraceIdRatioBased` sampler algorithm

* The sampling algorithm MUST be deterministic. A trace identified by a given
  `TraceId` is sampled or not independent of language, time, etc. To achieve this,
  implementations MUST use a deterministic hash of the `TraceId` when computing
  the sampling decision. By ensuring this, running the sampler on any child `Span`
  will produce the same decision.
* A `TraceIdRatioBased` sampler with a given sampling rate MUST also sample all
  traces that any `TraceIdRatioBased` sampler with a lower sampling rate would
  sample. This is important when a backend system may want to run with a higher
  sampling rate than the frontend system, this way all frontend traces will
  still be sampled and extra traces will be sampled on the backend only.
* **WARNING:** Since the exact algorithm is not specified yet (see TODO above),
  there will probably be changes to it in any language SDK once it is, which
  would break code that relies on the algorithm results.
  Only the configuration and creation APIs can be considered stable.
  It is recommended to use this sampler algorithm only for root spans
  (in combination with [`ParentBased`](#parentbased)) because different language
  SDKs or even different versions of the same language SDKs may produce inconsistent
  results for the same input.

#### ParentBased

* This is a composite sampler. `ParentBased` helps distinguished between the
following cases:
  * No parent (root span).
  * Remote parent (`SpanContext.IsRemote() == true`) with `SampledFlag` equals `true`
  * Remote parent (`SpanContext.IsRemote() == true`) with `SampledFlag` equals `false`
  * Local parent (`SpanContext.IsRemote() == false`) with `SampledFlag` equals `true`
  * Local parent (`SpanContext.IsRemote() == false`) with `SampledFlag` equals `false`

Required parameters:

* `root(Sampler)` - Sampler called for spans with no parent (root spans)

Optional parameters:

* `remoteParentSampled(Sampler)` (default: AlwaysOn)
* `remoteParentNotSampled(Sampler)` (default: AlwaysOff)
* `localParentSampled(Sampler)` (default: AlwaysOn)
* `localParentNotSampled(Sampler)` (default: AlwaysOff)

|Parent| parent.isRemote() | parent.IsSampled()| Invoke sampler|
|--|--|--|--|
|absent| n/a | n/a |`root()`|
|present|true|true|`remoteParentSampled()`|
|present|true|false|`remoteParentNotSampled()`|
|present|false|true|`localParentSampled()`|
|present|false|false|`localParentNotSampled()`|

## Span Limits

Erroneous code can add unintended attributes, events, and links to a span. If
these collections are unbounded, they can quickly exhaust available memory,
resulting in crashes that are difficult to recover from safely.

To protect against such errors, SDK Spans MAY discard attributes, links, and
events that would increase the number of elements of each collection beyond
the configured limit.

If the SDK implements the limits above it MUST provide a way to change these
limits, via a configuration to the TracerProvider, by allowing users to
configure individual limits like in the Java example bellow.

The name of the configuration options SHOULD be `AttributeCountLimit`,
`EventCountLimit` and `LinkCountLimit`. The options MAY be bundled in a class,
which then SHOULD be called `SpanLimits`. Implementations MAY provide additional
configuration such as `AttributePerEventCountLimit` and `AttributePerLinkCountLimit`.

```java
public final class SpanLimits {
  SpanLimits(int attributeCountLimit, int linkCountLimit, int eventCountLimit);

  public int getAttributeCountLimit();

  public int getEventCountLimit();

  public int getLinkCountLimit();
}
```

**Configurable parameters:**

* `AttributeCountLimit` (Default=128) - Maximum allowed span attribute count;
* `EventCountLimit` (Default=128) - Maximum allowed span event count;
* `LinkCountLimit` (Default=128) - Maximum allowed span link count;
* `AttributePerEventCountLimit` (Default=128) - Maximum allowed attribute per span event count;
* `AttributePerLinkCountLimit` (Default=128) - Maximum allowed attribute per span link count;

There SHOULD be a log emitted to indicate to the user that an attribute, event,
or link was discarded due to such a limit. To prevent excessive logging, the log
should not be emitted once per span, or per discarded attribute, event, or links.

## Id Generators

The SDK MUST by default randomly generate both the `TraceId` and the `SpanId`.

The SDK MUST provide a mechanism for customizing the way IDs are generated for
both the `TraceId` and the `SpanId`.

The SDK MAY provide this functionality by allowing custom implementations of
an interface like the java example below (name of the interface MAY be
`IdGenerator`, name of the methods MUST be consistent with
[SpanContext](./api.md#retrieving-the-traceid-and-spanid)), which provides
extension points for two methods, one to generate a `SpanId` and one for `TraceId`.

```java
public interface IdGenerator {
  byte[] generateSpanIdBytes();
  byte[] generateTraceIdBytes();
}
```

Additional `IdGenerator` implementing vendor-specific protocols such as AWS
X-Ray trace id generator MUST NOT be maintained or distributed as part of the
Core OpenTelemetry repositories.

## Span processor

Span processor is an interface which allows hooks for span start and end method
invocations. The span processors are invoked only when
[`IsRecording`](api.md#isrecording) is true.

Built-in span processors are responsible for batching and conversion of spans to
exportable representation and passing batches to exporters.

Span processors can be registered directly on SDK `TracerProvider` and they are
invoked in the same order as they were registered.

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
  |     |              |   | Batching Span Processor |   |    SpanExporter   |
  |     |              +---> Simple Span Processor   +--->  (JaegerExporter) |
  |     |              |   |                         |   |                   |
  | SDK | Span.start() |   +-------------------------+   +-------------------+
  |     | Span.end()   |
  |     |              |
  |     |              |
  |     |              |
  |     |              |
  +-----+--------------+
```

### Interface definition

#### OnStart

`OnStart` is called when a span is started. This method is called synchronously
on the thread that started the span, therefore it should not block or throw
exceptions.

**Parameters:**

* `span` - a [read/write span object](#additional-span-interfaces) for the started span.
  It SHOULD be possible to keep a reference to this span object and updates to the span
  SHOULD be reflected in it.
  For example, this is useful for creating a SpanProcessor that periodically
  evaluates/prints information about all active span from a background thread.
* `parentContext` - the parent `Context` of the span that the SDK determined
  (the explicitly passed `Context`, the current `Context` or an empty `Context`
  if that was explicitly requested).

**Returns:** `Void`

#### OnEnd(Span)

`OnEnd` is called after a span is ended (i.e., the end timestamp is already set).
This method MUST be called synchronously within the [`Span.End()` API](api.md#end),
therefore it should not block or throw an exception.

**Parameters:**

* `Span` - a [readable span object](#additional-span-interfaces) for the ended span.
  Note: Even if the passed Span may be technically writable,
  since it's already ended at this point, modifying it is not allowed.

**Returns:** `Void`

#### Shutdown()

Shuts down the processor. Called when SDK is shut down. This is an opportunity
for processor to do any cleanup required.

`Shutdown` SHOULD be called only once for each `SpanProcessor` instance. After
the call to `Shutdown`, subsequent calls to `OnStart`, `OnEnd`, or `ForceFlush`
are not allowed. SDKs SHOULD ignore these calls gracefully, if possible.

`Shutdown` SHOULD provide a way to let the caller know whether it succeeded,
failed or timed out.

`Shutdown` MUST include the effects of `ForceFlush`.

`Shutdown` SHOULD complete or abort within some timeout. `Shutdown` can be
implemented as a blocking API or an asynchronous API which notifies the caller
via a callback or an event. OpenTelemetry client authors can decide if they want to
make the shutdown timeout configurable.

#### ForceFlush()

This is a hint to ensure that any tasks associated with `Spans` for which the
`SpanProcessor` had already received events prior to the call to `ForceFlush` SHOULD
be completed as soon as possible, preferably before returning from this method.

In particular, if any `SpanProcessor` has any associated exporter, it SHOULD
try to call the exporter's `Export` with all spans for which this was not
already done and then invoke `ForceFlush` on it.
The [built-in SpanProcessors](#built-in-span-processors) MUST do so.
If a timeout is specified (see below), the SpanProcessor MUST prioritize honoring the timeout over
finishing all calls. It MAY skip or abort some or all Export or ForceFlush
calls it has made to achieve this goal.

`ForceFlush` SHOULD provide a way to let the caller know whether it succeeded,
failed or timed out.

`ForceFlush` SHOULD only be called in cases where it is absolutely necessary,
such as when using some FaaS providers that may suspend the process after an
invocation, but before the `SpanProcessor` exports the completed spans.

`ForceFlush` SHOULD complete or abort within some timeout. `ForceFlush` can be
implemented as a blocking API or an asynchronous API which notifies the caller
via a callback or an event. OpenTelemetry client authors can decide if they want to
make the flush timeout configurable.

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
* `exportTimeoutMillis` - how long the export can run before it is cancelled.
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

Exports a batch of [readable spans](#additional-span-interfaces).
Protocol exporters that will implement this
function are typically expected to serialize and transmit the data to the
destination.

Export() will never be called concurrently for the same exporter instance.
Export() can be called again only after the current call returns.

Export() MUST NOT block indefinitely, there MUST be a reasonable upper limit
after which the call must time out with an error result (`Failure`).

Any retry logic that is required by the exporter is the responsibility
of the exporter. The default SDK SHOULD NOT implement retry logic, as
the required logic is likely to depend heavily on the specific protocol
and backend the spans are being sent to.

**Parameters:**

batch - a batch of [readable spans](#additional-span-interfaces). The exact data type of the batch is language
specific, typically it is some kind of list,
e.g. for spans in Java it will be typically `Collection<SpanData>`.

**Returns:** ExportResult:

ExportResult is one of:

* `Success` - The batch has been successfully exported.
  For protocol exporters this typically means that the data is sent over
  the wire and delivered to the destination server.
* `Failure` - exporting failed. The batch must be dropped. For example, this
  can happen when the batch contains bad data and cannot be serialized.

Note: this result may be returned via an async mechanism or a callback, if that
is idiomatic for the language implementation.

#### `Shutdown()`

Shuts down the exporter. Called when SDK is shut down. This is an opportunity
for exporter to do any cleanup required.

`Shutdown` should be called only once for each `Exporter` instance. After the
call to `Shutdown` subsequent calls to `Export` are not allowed and should
return a `Failure` result.

`Shutdown` should not block indefinitely (e.g. if it attempts to flush the data
and the destination is unavailable). OpenTelemetry client authors can decide if they
want to make the shutdown timeout configurable.

#### `ForceFlush()`

This is a hint to ensure that the export of any `Spans` the exporter has received prior to the
call to `ForceFlush` SHOULD be completed as soon as possible, preferably before
returning from this method.

`ForceFlush` SHOULD provide a way to let the caller know whether it succeeded,
failed or timed out.

`ForceFlush` SHOULD only be called in cases where it is absolutely necessary,
such as when using some FaaS providers that may suspend the process after an
invocation, but before the exporter exports the completed spans.

`ForceFlush` SHOULD complete or abort within some timeout. `ForceFlush` can be
implemented as a blocking API or an asynchronous API which notifies the caller
via a callback or an event. OpenTelemetry client authors can decide if they want to
make the flush timeout configurable.

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
languages. Examples are for illustration purposes only. OpenTelemetry client authors
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
[otep-83]: https://github.com/open-telemetry/oteps/blob/main/text/0083-component.md
