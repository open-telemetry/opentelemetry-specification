# Events SDK

**Status**: [Development](../document-status.md)

<details>
<summary>Table of Contents</summary>

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [Events SDK](#events-sdk)
  - [Overview](#overview)
  - [EventLoggerProvider](#eventloggerprovider)
    - [EventLoggerProvider Creation](#eventloggerprovider-creation)
    - [EventLogger Creation](#eventlogger-creation)
    - [Configuration](#configuration)
      - [EventLoggerConfigurator](#eventloggerconfigurator)
    - [Shutdown](#shutdown)
    - [ForceFlush](#forceflush)
  - [EventLogger](#eventlogger)
    - [EventLoggerConfig](#eventloggerconfig)
    - [Emit Event](#emit-event)
  - [EventProcessor](#eventprocessor)
    - [EventProcessor operations](#eventprocessor-operations)
      - [OnEmit](#onemit)
      - [ShutDown](#shutdown-1)
      - [ForceFlush](#forceflush-1)
    - [Built-in processors](#built-in-processors)
      - [Log bridge processor](#log-bridge-processor)
      - [Span event processor](#span-event-processor)
      - [Event processors for language-specific logging libraries](#event-processors-for-language-specific-logging-libraries)

<!-- tocstop -->

</details>

Users of OpenTelemetry need a way for instrumentation interactions with the
OpenTelemetry API to actually produce telemetry. The OpenTelemetry SDK
(henceforth referred to as the SDK) is an implementation of the OpenTelemetry
API that provides users with this functionally.

All implementations of the OpenTelemetry API MUST provide an SDK.

## Overview

From OpenTelemetry's perspective LogRecords and Events are both represented
using the same [data model](./event-api.md#event-data-model). Therefore, the default
implementation of an Event SDK MUST generate events using the [Logs Data Model](./data-model.md).

The SDK MUST use the [Logs SDK](./sdk.md) to generate, process and export `LogRecord`s.

## EventLoggerProvider

A `EventLoggerProvider` MUST provide a way to allow a [Resource](../resource/sdk.md)
to be specified. If a `Resource` is specified, it SHOULD be associated with all
the `LogRecord`s produced by any `EventLogger` from the `EventLoggerProvider`.

### EventLoggerProvider Creation

The SDK SHOULD allow the creation of multiple independent `EventLoggerProvider`s.

### EventLogger Creation

It SHOULD only be possible to create `EventLogger` instances through a `EventLoggerProvider`
(see [Event API](event-api.md)).

The `EventLoggerProvider` MUST implement the [Get an EventLogger API](event-api.md#get-an-eventlogger).

The input provided by the user MUST be used to create
an [`InstrumentationScope`](../glossary.md#instrumentation-scope) instance which
is stored on the created `EventLogger`.

In the case where an invalid `name` (null or empty string) is specified, a
working `EventLogger` MUST be returned as a fallback rather than returning null or
throwing an exception, its `name` SHOULD keep the original invalid value, and a
message reporting that the specified value is invalid SHOULD be logged.

### Configuration

Configuration (
i.e. [EventProcessors](#eventprocessor) and [EventLoggerConfigurator](#eventloggerconfigurator))
MUST be owned by the `EventLoggerProvider`. The configuration MAY be applied at the
time of `EventLoggerProvider` creation if appropriate.

The `EventLoggerProvider` MAY provide methods to update the configuration. If
configuration is updated (e.g., adding an `EventProcessor`), the updated
configuration MUST also apply to all already returned `EventLogger`s (i.e. it MUST
NOT matter whether an `EventLogger` was obtained from the `EventLoggerProvider` before or
after the configuration change). Note: Implementation-wise, this could mean
that `EventLogger` instances have a reference to their `EventLoggerProvider` and access
configuration only via this reference.

#### EventLoggerConfigurator

An `EventLoggerConfigurator` is a function which computes
the [EventLoggerConfig](#eventloggerconfig) for an [EventLogger](#eventlogger).

The function MUST accept the following parameter:

* `event_logger_scope`:
  The [`InstrumentationScope`](../glossary.md#instrumentation-scope) of
  the `EventLogger`.

The function MUST return the relevant `EventLoggerConfig`, or some signal indicating
that the [default EventLoggerConfig](#eventloggerconfig) should be used. This signal MAY
be nil, null, empty, or an instance of the default `EventLoggerConfig` depending on
what is idiomatic in the language.

This function is called when an `EventLogger` is first created, and for each
outstanding `EventLogger` when an `EventLoggerProvider`'s `EventLoggerConfigurator` is
updated (if updating is supported). Therefore, it is important that it returns
quickly.

`EventLoggerConfigurator` is modeled as a function to maximize flexibility.
However, implementations MAY provide shorthand or helper functions to
accommodate common use cases:

* Select one or more event loggers by name, with exact match or pattern matching.
* Disable one or more specific event loggers.
* Disable all event loggers, and selectively enable one or more specific event loggers.

### Shutdown

This method provides a way for provider to do any cleanup required.

`Shutdown` MUST be called only once for each `EventLoggerProvider` instance. After
the call to `Shutdown`, subsequent attempts to get an `EventLogger` are not allowed.
SDKs SHOULD return a valid no-op `EventLogger` for these calls, if possible.

`Shutdown` SHOULD provide a way to let the caller know whether it succeeded,
failed or timed out.

`Shutdown` SHOULD complete or abort within some timeout. `Shutdown` MAY be
implemented as a blocking API or an asynchronous API which notifies the caller
via a callback or an event. [OpenTelemetry SDK](../overview.md#sdk) authors MAY
decide if they want to make the shutdown timeout configurable.

`Shutdown` MUST be implemented by invoking `Shutdown` on all
registered [EventProcessors](#eventprocessor).

### ForceFlush

This method provides a way for provider to notify the
registered [EventProcessors](#eventprocessor) to immediately export all
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
registered [EventProcessors](#eventprocessor).

## EventLogger

### EventLoggerConfig

A `EventLoggerConfig` defines various configurable aspects of an `EventLogger`'s behavior.
It consists of the following parameters:

* `disabled`: A boolean indication of whether the logger is enabled.

  If not explicitly set, the `disabled` parameter SHOULD default to `false` (
  i.e. `EventLogger`s are enabled by default).

  If an `EventLogger` is disabled, it MUST behave equivalently
  to [No-op EventLogger](./noop.md#eventlogger).

  The value of `disabled` MUST be used to resolve whether a `Logger`
  is [Enabled](./bridge-api.md#enabled). If `disabled` is `true`, `Enabled`
  returns `false`. If `disabled` is `false`, `Enabled` returns `true`. It is not
  necessary for implementations to ensure that changes to `disabled` are
  immediately visible to callers of `Enabled`. I.e. atomic, volatile,
  synchronized, or equivalent memory semantics to avoid stale reads are
  discouraged to prioritize performance over immediate consistency.

### Emit Event

Emit a `LogRecord` representing an `Event`.

**Implementation Requirements:**

The implementation MUST use the parameters
to [emit a logRecord](./bridge-api.md#emit-a-logrecord) as follows:

* The `Name` MUST be used to set
  the `event.name` [Attribute](./data-model.md#field-attributes). If
  the `Attributes` provided by the user contain an `event.name` attribute the
  value provided in the `Name` takes precedence.
* If provided by the user, the `Body` MUST be used to set
  the [Body](./data-model.md#field-body). If not provided, `Body` MUST not be
  set.
* If provided by the user, the `Timestamp` MUST be used to set
  the [Timestamp](./data-model.md#field-timestamp). If not provided, `Timestamp`
  MUST be set to the current time when [emit](#emit-event) was called.
* The [Observed Timestamp](./data-model.md#field-observedtimestamp) MUST not be
  set. (NOTE: [emit a logRecord](./bridge-api.md#emit-a-logrecord) will
  set `ObservedTimestamp` to the current time when unset.)
* If provided by the user, the `Context` MUST be used to set
  the [Context](./bridge-api.md#emit-a-logrecord). If not provided, `Context`
  MUST be set to the current Context.
* If provided by the user, the `SeverityNumber` MUST be used to set
  the [Severity Number](./data-model.md#field-severitynumber) when emitting the
  logRecord. If not provided, `SeverityNumber` MUST be set
  to `SEVERITY_NUMBER_INFO=9`.
* The [Severity Text](./data-model.md#field-severitytext) MUST not be set.
* If provided by the user, the `Attributes` MUST be used to set
  the [Attributes](./data-model.md#field-attributes). The user
  provided `Attributes` MUST not take over the `event.name`
  attribute previously discussed.

## EventProcessor

`EventProcessor` is an interface which allows hooks for `LogRecord`
emitting from the `EventLogger`.

Built-in processors are responsible for passing `LogRecord`s to various
logging pipelines.

`EventProcessors` can be registered directly on SDK `EventLoggerProvider` and
they are invoked in the same order as they were registered.

The SDK MUST allow users to implement and configure custom processors and
decorate built-in processors for advanced scenarios such as enriching with
attributes.

The following diagram shows `EventProcessor`'s relationship to other
components in the SDK:

```
  +-----+--------------------+   +--------------------+
  |     |                    |   |                    |
  |     |                    |   | LogBridgeProcessor |
  |     |                    +---> SpanEventProcessor |
  |     |                    |   |                    |
  | SDK | EventLogger.emit() |   +--------------------+
  |     |                    |
  |     |                    |
  |     |                    |
  |     |                    |
  |     |                    |
  +-----+--------------------+
```

### EventProcessor operations

#### OnEmit

`OnEmit` is called when a `LogRecord` is [emitted](event-api.md#emit-event). This
method is called synchronously on the thread that emitted the `LogRecord`,
therefore it SHOULD NOT block or throw exceptions.

**Parameters:**

* `logRecord` - a [ReadWriteLogRecord](#readwritelogrecord) for the
  emitted `LogRecord`.
* `context` - the resolved `Context` (the explicitly passed `Context` or the
  current `Context`)

**Returns:** `Void`

An `EventProcessor` may freely modify `logRecord` for the duration of
the `OnEmit` call. If `logRecord` is needed after `OnEmit` returns (i.e. for
asynchronous processing) only reads are permitted.

#### ShutDown

Shuts down the processor. Called when the SDK is shut down. This is an
opportunity for the processor to do any cleanup required.

`Shutdown` SHOULD be called only once for each `EventProcessor` instance.
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
the `EventProcessor` had already received events prior to the call
to `ForceFlush` SHOULD be completed as soon as possible, preferably before
returning from this method.

`ForceFlush` SHOULD provide a way to let the caller know whether it succeeded,
failed or timed out.

`ForceFlush` SHOULD only be called in cases where it is absolutely necessary,
such as when using some FaaS providers that may suspend the process after an
invocation, but before the `EventProcessor` exports the
emitted `LogRecord`s.

`ForceFlush` SHOULD complete or abort within some timeout. `ForceFlush` can be
implemented as a blocking API or an asynchronous API which notifies the caller
via a callback or an event. OpenTelemetry SDK authors can decide if they want to
make the flush timeout configurable.

### Built-in processors

The standard OpenTelemetry SDK MUST implement both the log bridge processor
and span event processor as described below.

#### Log bridge processor

This is an implementation of `EventProcessor` which
passes the `ReadWriteLogRecord` representation to the
configured Log SDK.

**Configurable parameters:**

* `loggingProvider` - the `LoggingProvider` to use when emitting `LogRecord`s.
  TODO need new Logging Provider SDK method

#### Span event processor

This is an implementation of the `EventProcessor` which adds the
`LogRecord` to the current span as a `SpanEvent`.
If there's no current span, this is a no-op.
If the `LogRecord` has a body, it MUST be json-serialized to a `SpanEvent`
attribute named `event.body`.

**Configurable parameters:**

* `tracerProvider` - the `TracerProvider` to use when emitting `SpanEvent`s.

#### Event processors for language-specific logging libraries

These are additional implementations of `EventProcessor` which
emit the `LogRecord` to language-specific logging libraries.

When using 3rd party loggers, it's the end users responsibility to configure
that logging library to call the log bridge API if they want logs to be exported
to OpenTelemetry.

You should not install this processor and the log bridge processor at the same
time since it can lead to duplicate logs being emitted to log exporters.

The SDK MAY guard against this by not allowing both to be installed at the same time.
