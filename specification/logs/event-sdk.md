# Events SDK

**Status**: [Deprecated](../document-status.md) (was never stabilized),
see the [Logs SDK](./sdk.md) and [Emit Event](./api.md#emit-a-logrecord) in the Logs API for replacement.

<details>
<summary>Table of Contents</summary>

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [Logs API Development](#logs-api-development)
- [Overview](#overview)
- [EventLoggerProvider](#eventloggerprovider)
  * [EventLoggerProvider Creation](#eventloggerprovider-creation)
  * [EventLogger Creation](#eventlogger-creation)
  * [Configuration](#configuration)
  * [ForceFlush](#forceflush)
- [EventLogger](#eventlogger)
  * [Emit Event](#emit-event)

<!-- tocstop -->

</details>

Users of OpenTelemetry need a way for instrumentation interactions with the
OpenTelemetry API to actually produce telemetry. The OpenTelemetry SDK
(henceforth referred to as the SDK) is an implementation of the OpenTelemetry
API that provides users with this functionally.

All implementations of the OpenTelemetry API MUST provide an SDK.

## Logs API Development

> [!NOTE]
> We are currently in the process of defining a new [Logs API](./api.md).

The intent is that Logs SDK will incorporate the current functionality of this existing Events SDK and once it is defined and implemented, the Events SDK usage will be migrated, deprecated, renamed and eventually removed.

No further work is scheduled for the current Event SDK at this time.

## Overview

From OpenTelemetry's perspective LogRecords and Events are both represented
using the same [data model](./event-api.md#event-data-model). Therefore, the default
implementation of an Event SDK MUST generate events using the [Logs Data Model](./data-model.md).

The SDK MUST use the [Logs SDK](./sdk.md) to generate, process and export `LogRecord`s.

## EventLoggerProvider

The `EventLoggerProvider` MUST be implemented as a proxy to an instance of [`LoggerProvider`](./sdk.md#loggerprovider).

All `LogRecord`s produced by any `EventLogger` from the `EventLoggerProvider` SHOULD be associated with the `Resource` from the provided `LoggerProvider`.

### EventLoggerProvider Creation

The SDK SHOULD allow the creation of multiple independent `EventLoggerProvider`s.

### EventLogger Creation

It SHOULD only be possible to create `EventLogger` instances through an `EventLoggerProvider`
(see [Events API](event-api.md)).

The `EventLoggerProvider` MUST implement the [Get an EventLogger API](event-api.md#get-an-eventlogger).

In the case where an invalid `name` (null or empty string) is specified, a
working `EventLogger` MUST be returned as a fallback rather than returning null or
throwing an exception. Its `name` SHOULD keep the original invalid value, and a
message reporting that the specified value is invalid SHOULD be logged.

### Configuration

The `EventLoggerProvider` MUST accept an instance of `LoggerProvider`. Any configuration
related to processing MUST be done by configuring the `LoggerProvider` directly.

### ForceFlush

This method provides a way for the provider to notify the delegate `LoggerProvider`
to force all registered [LogRecordProcessors](sdk.md#logrecordprocessor) to immediately export all
`LogRecords` that have not yet been exported.

## EventLogger

The `EventLogger` MUST be implemented as a proxy to an instance of [`Logger`](./sdk.md#logger).

### Emit Event

Emit a `LogRecord` representing an `Event`.

**Implementation Requirements:**

The implementation MUST use the parameters
to [emit a logRecord](./api.md#emit-a-logrecord) as follows:

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
  set. (NOTE: [emit a logRecord](./api.md#emit-a-logrecord) will
  set `ObservedTimestamp` to the current time when unset.)
* If provided by the user, the `Context` MUST be used to set
  the [Context](./api.md#emit-a-logrecord). If not provided, `Context`
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
