# Logs SDK

**Status**: [Stable](../document-status.md), except where otherwise specified

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [LoggerProvider](#loggerprovider)
  * [LoggerProvider Creation](#loggerprovider-creation)
  * [Logger Creation](#logger-creation)
  * [Configuration](#configuration)
    + [LoggerConfigurator](#loggerconfigurator)
  * [Shutdown](#shutdown)
  * [ForceFlush](#forceflush)
- [Logger](#logger)
  * [LoggerConfig](#loggerconfig)
- [Additional LogRecord interfaces](#additional-logrecord-interfaces)
  * [ReadableLogRecord](#readablelogrecord)
  * [ReadWriteLogRecord](#readwritelogrecord)
- [LogRecord Limits](#logrecord-limits)
- [LogRecordProcessor](#logrecordprocessor)
  * [LogRecordProcessor operations](#logrecordprocessor-operations)
    + [OnEmit](#onemit)
    + [ShutDown](#shutdown)
    + [ForceFlush](#forceflush-1)
  * [Built-in processors](#built-in-processors)
    + [Simple processor](#simple-processor)
    + [Batching processor](#batching-processor)
- [LogRecordExporter](#logrecordexporter)
  * [LogRecordExporter operations](#logrecordexporter-operations)
    + [Export](#export)
    + [ForceFlush](#forceflush-2)
    + [Shutdown](#shutdown-1)

<!-- tocstop -->

</details>

Users of OpenTelemetry need a way for instrumentation interactions with the
OpenTelemetry API to actually produce telemetry. The OpenTelemetry Logging SDK
(henceforth referred to as the SDK) is an implementation of the OpenTelemetry
API that provides users with this functionally.

All language implementations of OpenTelemetry MUST provide an SDK.

## LoggerProvider

A `LoggerProvider` MUST provide a way to allow a [Resource](../resource/sdk.md)
to be specified. If a `Resource` is specified, it SHOULD be associated with all
the `LogRecord`s produced by any `Logger` from the `LoggerProvider`.

### LoggerProvider Creation

The SDK SHOULD allow the creation of multiple independent `LoggerProviders`s.

### Logger Creation

It SHOULD only be possible to create `Logger` instances through a `LoggerProvider`
(see [Bridge API](bridge-api.md)).

The `LoggerProvider` MUST implement the [Get a Logger API](bridge-api.md#get-a-logger).

The input provided by the user MUST be used to create
an [`InstrumentationScope`](../glossary.md#instrumentation-scope) instance which
is stored on the created `Logger`.

In the case where an invalid `name` (null or empty string) is specified, a
working `Logger` MUST be returned as a fallback rather than returning null or
throwing an exception, its `name` SHOULD keep the original invalid value, and a
message reporting that the specified value is invalid SHOULD be logged.

**Status**: [Experimental](../document-status.md) - The `LoggerProvider` MUST
compute the relevant [LoggerConfig](#loggerconfig) using the
configured [LoggerConfigurator](#loggerconfigurator), and create
a `Logger` whose behavior conforms to that `LoggerConfig`.

### Configuration

Configuration (
i.e. [LogRecordProcessors](#logrecordprocessor) and (**experimental**) [LoggerConfigurator](#loggerconfigurator))
MUST be owned by the `LoggerProvider`. The configuration MAY be applied at the
time of `LoggerProvider` creation if appropriate.

The `LoggerProvider` MAY provide methods to update the configuration. If
configuration is updated (e.g., adding a `LogRecordProcessor`), the updated
configuration MUST also apply to all already returned `Logger`s (i.e. it MUST
NOT matter whether a `Logger` was obtained from the `LoggerProvider` before or
after the configuration change). Note: Implementation-wise, this could mean
that `Logger` instances have a reference to their `LoggerProvider` and access
configuration only via this reference.

#### LoggerConfigurator

**Status**: [Experimental](../document-status.md)

A `LoggerConfigurator` is a function which computes
the [LoggerConfig](#loggerconfig) for a [Logger](#logger).

The function MUST accept the following parameter:

* `logger_scope`:
  The [`InstrumentationScope`](../glossary.md#instrumentation-scope) of
  the `Logger`.

The function MUST return the relevant `LoggerConfig`, or some signal indicating
that the [default LoggerConfig](#loggerconfig) should be used. This signal MAY
be nil, null, empty, or an instance of the default `LoggerConfig` depending on
what is idiomatic in the language.

This function is called when a `Logger` is first created, and for each
outstanding `Logger` when a `LoggerProvider`'s `LoggerConfigurator` is
updated (if updating is supported). Therefore, it is important that it returns
quickly.

`LoggerConfigurator` is modeled as a function to maximize flexibility.
However, implementations MAY provide shorthand or helper functions to
accommodate common use cases:

* Select one or more loggers by name, with exact match or pattern matching.
* Disable one or more specific loggers.
* Disable all loggers, and selectively enable one or more specific loggers.

### Shutdown

This method provides a way for provider to do any cleanup required.

`Shutdown` MUST be called only once for each `LoggerProvider` instance. After
the call to `Shutdown`, subsequent attempts to get a `Logger` are not allowed.
SDKs SHOULD return a valid no-op `Logger` for these calls, if possible.

`Shutdown` SHOULD provide a way to let the caller know whether it succeeded,
failed or timed out.

`Shutdown` SHOULD complete or abort within some timeout. `Shutdown` MAY be
implemented as a blocking API or an asynchronous API which notifies the caller
via a callback or an event. [OpenTelemetry SDK](../overview.md#sdk) authors MAY
decide if they want to make the shutdown timeout configurable.

`Shutdown` MUST be implemented by invoking `Shutdown` on all
registered [LogRecordProcessors](#logrecordprocessor).

### ForceFlush

This method provides a way for provider to notify the
registered [LogRecordProcessors](#logrecordprocessor) to immediately export all
`ReadableLogRecords` that have not yet been exported.

`ForceFlush` SHOULD provide a way to let the caller know whether it succeeded,
failed or timed out. `ForceFlush` SHOULD return some **ERROR** status if there
is an error condition; and if there is no error condition, it SHOULD return
some **NO ERROR** status, language implementations MAY decide how to model
**ERROR** and **NO ERROR**.

`ForceFlush` SHOULD complete or abort within some timeout. `ForceFlush` MAY be
implemented as a blocking API or an asynchronous API which notifies the caller
via a callback or an event. [OpenTelemetry SDK](../overview.md#sdk) authors MAY
decide if they want to make the flush timeout configurable.

`ForceFlush` MUST invoke `ForceFlush` on all
registered [LogRecordProcessors](#logrecordprocessor).

## Logger

**Status**: [Experimental](../document-status.md) - `Logger` MUST behave
according to the [LoggerConfig](#loggerconfig) computed
during [logger creation](#logger-creation). If the `LoggerProvider` supports
updating the [LoggerConfigurator](#loggerconfigurator), then upon update
the `Logger` MUST be updated to behave according to the new `LoggerConfig`.

### LoggerConfig

**Status**: [Experimental](../document-status.md)

A `LoggerConfig` defines various configurable aspects of a `Logger`'s behavior.
It consists of the following parameters:

* `disabled`: A boolean indication of whether the logger is enabled.

  If not explicitly set, the `disabled` parameter SHOULD default to `false` (
  i.e. `Logger`s are enabled by default).

  If a `Logger` is disabled, it MUST behave equivalently
  to [No-op Logger](./noop.md#logger).

## Additional LogRecord interfaces

In this document we refer to `ReadableLogRecord` and `ReadWriteLogRecord`, defined as follows.

### ReadableLogRecord

A function receiving this as an argument MUST be able to access all the
information added to the [LogRecord](data-model.md#log-and-event-record-definition). It MUST also be able to
access the [Instrumentation Scope](./data-model.md#field-instrumentationscope)
and [Resource](./data-model.md#field-resource) information (implicitly)
associated with the `LogRecord`.

The [trace context fields](./data-model.md#trace-context-fields) MUST be populated from
the resolved `Context` (either the explicitly passed `Context` or the
current `Context`) when [emitted](./bridge-api.md#emit-a-logrecord).

Counts for attributes due to collection limits MUST be available for exporters
to report as described in
the [transformation to non-OTLP formats](../common/mapping-to-non-otlp.md#dropped-attributes-count)
specification.

Note: Typically this will be implemented with a new interface or (immutable)
value type. The SDK may also use a single type to represent both `ReadableLogRecord`
and `ReadWriteLogRecord`.

### ReadWriteLogRecord

ReadWriteLogRecord is a superset of [ReadableLogRecord](#readablelogrecord).

A function receiving this as an argument MUST additionally be able to modify
the following information added to the [LogRecord](data-model.md#log-and-event-record-definition):

* [`Timestamp`](./data-model.md#field-timestamp)
* [`ObservedTimestamp`](./data-model.md#field-observedtimestamp)
* [`SeverityText`](./data-model.md#field-severitytext)
* [`SeverityNumber`](./data-model.md#field-severitynumber)
* [`Body`](./data-model.md#field-body)
* [`Attributes`](./data-model.md#field-attributes) (addition, modification, removal)
* [`TraceId`](./data-model.md#field-traceid)
* [`SpanId`](./data-model.md#field-spanid)
* [`TraceFlags`](./data-model.md#field-traceflags)

## LogRecord Limits

`LogRecord` attributes MUST adhere to
the [common rules of attribute limits](../common/README.md#attribute-limits).

If the SDK implements attribute limits it MUST provide a way to change these
limits, via a configuration to the `LoggerProvider`, by allowing users to
configure individual limits like in the Java example below.

The options MAY be bundled in a class, which then SHOULD be called
`LogRecordLimits`.

```java
public interface LogRecordLimits {
  public int getAttributeCountLimit();

  public int getAttributeValueLengthLimit();
}
```

**Configurable parameters:**

* [all common options applicable to attributes](../common/README.md#configurable-parameters)

There SHOULD be a message printed in the SDK's log to indicate to the user
that an attribute was discarded due to such a limit.
To prevent excessive logging, the message MUST be printed at most once per
`LogRecord` (i.e., not per discarded attribute).

## LogRecordProcessor

`LogRecordProcessor` is an interface which allows hooks for `LogRecord`
emitting.

Built-in processors are responsible for batching and conversion of `LogRecord`s
to exportable representation and passing batches to exporters.

`LogRecordProcessors` can be registered directly on SDK `LoggerProvider` and
they are invoked in the same order as they were registered.

Each processor registered on `LoggerProvider` is part of a pipeline that
consists of a processor and optional [exporter](#logrecordexporter). The SDK
MUST allow each pipeline to end with an individual exporter.

The SDK MUST allow users to implement and configure custom processors and
decorate built-in processors for advanced scenarios such as enriching with
attributes.

The SDK SHOULD allow users to set up independent log processing pipelines.

The following diagram shows `LogRecordProcessor`'s relationship to other
components in the SDK:

```
  +-----+------------------------+   +------------------------------+   +-------------------------+
  |     |                        |   |                              |   |                         |
  |     |                        |   | Batching LogRecordProcessor  |   |    LogRecordExporter    |
  |     |                        +---> Simple LogRecordProcessor    +--->     (OtlpExporter)      |
  |     |                        |   |                              |   |                         |
  | SDK | Logger.emit(LogRecord) |   +------------------------------+   +-------------------------+
  |     |                        |
  |     |                        |
  |     |                        |
  |     |                        |
  |     |                        |
  +-----+------------------------+
```

### LogRecordProcessor operations

#### OnEmit

`OnEmit` is called when a `LogRecord` is [emitted](bridge-api.md#emit-a-logrecord). This
method is called synchronously on the thread that emitted the `LogRecord`,
therefore it SHOULD NOT block or throw exceptions.

**Parameters:**

* `logRecord` - a [ReadWriteLogRecord](#readwritelogrecord) for the
  emitted `LogRecord`. It is `logRecord` MAY be passed as a 
* `context` - the resolved `Context` (the explicitly passed `Context` or the
  current `Context`)

**Returns:** `Void`

A `LogRecordProcessor` may freely modify `logRecord` for the duration of
the `OnEmit` call. If `logRecord` is needed after `OnEmit` returns (i.e. for
asynchronous processing) only reads are permitted.

It is implementation specific whether `logRecord` modification are
also applied to the subsequent registered processors.
For instance, `logRecord` may be passed by value or by reference.
If `logRecord` modifications are applied the to subsequent registered processors,
then [ReadWriteLogRecord](#readwritelogrecord) SHOULD offer
a way to make a copy so that the user can set up independent log processing
pipelines.

#### ShutDown

Shuts down the processor. Called when the SDK is shut down. This is an
opportunity for the processor to do any cleanup required.

`Shutdown` SHOULD be called only once for each `LogRecordProcessor` instance.
After the call to `Shutdown`, subsequent calls to `OnEmit` are not allowed. SDKs
SHOULD ignore these calls gracefully, if possible.

`Shutdown` SHOULD provide a way to let the caller know whether it succeeded,
failed or timed out.

`Shutdown` MUST include the effects of `ForceFlush`.

`Shutdown` SHOULD complete or abort within some timeout. `Shutdown` can be
implemented as a blocking API or an asynchronous API which notifies the caller
via a callback or an event. OpenTelemetry SDK authors can decide if they want
to make the shutdown timeout configurable.

#### ForceFlush

This is a hint to ensure that any tasks associated with `LogRecord`s for which
the `LogRecordProcessor` had already received events prior to the call
to `ForceFlush` SHOULD be completed as soon as possible, preferably before
returning from this method.

In particular, if any `LogRecordProcessor` has any associated exporter, it
SHOULD try to call the exporter's `Export` with all `LogRecord`s for which this
was not already done and then invoke `ForceFlush` on it.
The [built-in LogRecordProcessors](#built-in-processors) MUST do so. If a
timeout is specified (see below), the `LogRecordProcessor` MUST prioritize
honoring the timeout over
finishing all calls. It MAY skip or abort some or all Export or ForceFlush calls
it has made to achieve this goal.

`ForceFlush` SHOULD provide a way to let the caller know whether it succeeded,
failed or timed out.

`ForceFlush` SHOULD only be called in cases where it is absolutely necessary,
such as when using some FaaS providers that may suspend the process after an
invocation, but before the `LogRecordProcessor` exports the
emitted `LogRecord`s.

`ForceFlush` SHOULD complete or abort within some timeout. `ForceFlush` can be
implemented as a blocking API or an asynchronous API which notifies the caller
via a callback or an event. OpenTelemetry SDK authors can decide if they want to
make the flush timeout configurable.

### Built-in processors

The standard OpenTelemetry SDK MUST implement both simple and batch processors,
as described below. Other common processing scenarios SHOULD be first considered
for implementation out-of-process
in [OpenTelemetry Collector](../overview.md#collector).

#### Simple processor

This is an implementation of `LogRecordProcessor` which passes finished logs and
passes the export-friendly `ReadableLogRecord` representation to the
configured [LogRecordExporter](#logrecordexporter), as soon as they are
finished.

**Configurable parameters:**

* `exporter` - the exporter where the `LogRecord`s are pushed.

#### Batching processor

This is an implementation of the `LogRecordProcessor` which create batches
of `LogRecord`s and passes the export-friendly `ReadableLogRecord`
representations to the configured `LogRecordExporter`.

**Configurable parameters:**

* `exporter` - the exporter where the `LogRecord`s are pushed.
* `maxQueueSize` - the maximum queue size. After the size is reached logs are
  dropped. The default value is `2048`.
* `scheduledDelayMillis` - the delay interval in milliseconds between two
  consecutive exports. The default value is `1000`.
* `exportTimeoutMillis` - how long the export can run before it is cancelled.
  The default value is `30000`.
* `maxExportBatchSize` - the maximum batch size of every export. It must be
  smaller or equal to `maxQueueSize`. The default value is `512`.

## LogRecordExporter

`LogRecordExporter` defines the interface that protocol-specific exporters must
implement so that they can be plugged into OpenTelemetry SDK and support sending
of telemetry data.

The goal of the interface is to minimize burden of implementation for
protocol-dependent telemetry exporters. The protocol exporter is expected to be
primarily a simple telemetry data encoder and transmitter.

### LogRecordExporter operations

A `LogRecordExporter` MUST support the following functions:

#### Export

Exports a batch of [ReadableLogRecords](#readablelogrecord). Protocol exporters
that will implement this function are typically expected to serialize and
transmit the data to the destination.

`Export` will never be called concurrently for the same exporter instance.
Depending on the implementation the result of the export may be returned to the
Processor not in the return value of the call to `Export` but in a language
specific way for signaling completion of an asynchronous task. This means that
while an instance of an exporter will never have it `Export` called concurrently
it does not mean that the task of exporting can not be done concurrently. How
this is done is outside the scope of this specification. Each implementation
MUST document the concurrency characteristics the SDK requires of the exporter.

`Export` MUST NOT block indefinitely, there MUST be a reasonable upper limit
after which the call must time out with an error result (`Failure`).

Concurrent requests and retry logic is the responsibility of the exporter. The
default SDK's `LogRecordProcessors` SHOULD NOT implement retry logic, as the
required logic is likely to depend heavily on the specific protocol and backend
the logs are being sent to. For example,
the [OpenTelemetry Protocol (OTLP) specification](../protocol/otlp.md) defines
logic for both sending concurrent requests and retrying requests.

**Parameters:**

* `batch` - a batch of [ReadableLogRecords](#readablelogrecord). The exact data type
of the batch is language specific, typically it is some kind of list, e.g. for
logs in Java it will be typically `Collection<LogRecordData>`.

**Returns:** `ExportResult`

The return of `Export` is implementation specific. In what is idiomatic for the
language the Exporter must send an `ExportResult` to the
Processor. `ExportResult` has values of either `Success` or `Failure`:

* `Success` - The batch has been successfully exported. For protocol exporters
  this typically means that the data is sent over the wire and delivered to the
  destination server.
* `Failure` - exporting failed. The batch must be dropped. For example, this can
  happen when the batch contains bad data and cannot be serialized.

For example, in Java the return of `Export` would be a Future which when
completed returns the `ExportResult` object. While in Erlang the exporter sends
a message to the processor with the `ExportResult` for a particular batch.

#### ForceFlush

This is a hint to ensure that the export of any `ReadableLogRecords` the
exporter has received prior to the call to `ForceFlush` SHOULD be completed as
soon as possible, preferably before returning from this method.

`ForceFlush` SHOULD provide a way to let the caller know whether it succeeded,
failed or timed out.

`ForceFlush` SHOULD only be called in cases where it is absolutely necessary,
such as when using some FaaS providers that may suspend the process after an
invocation, but before the exporter exports the `ReadlableLogRecords`.

`ForceFlush` SHOULD complete or abort within some timeout. `ForceFlush` can be
implemented as a blocking API or an asynchronous API which notifies the caller
via a callback or an event. [OpenTelemetry SDK](../overview.md#sdk) authors MAY
decide if they want to make the flush timeout configurable.

#### Shutdown

Shuts down the exporter. Called when SDK is shut down. This is an opportunity
for exporter to do any cleanup required.

Shutdown SHOULD be called only once for each `LogRecordExporter` instance. After
the call to `Shutdown` subsequent calls to `Export` are not allowed and SHOULD
return a Failure result.

`Shutdown` SHOULD NOT block indefinitely (e.g. if it attempts to flush the data
and the destination is unavailable). [OpenTelemetry SDK](../overview.md#sdk)
authors MAY decide if they want to make the shutdown timeout configurable.

- [OTEP0150 Logging Library SDK Prototype Specification](https://github.com/open-telemetry/oteps/blob/main/text/logs/0150-logging-library-sdk.md)
