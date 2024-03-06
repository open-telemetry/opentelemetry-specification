# Events SDK

**Status**: [Experimental](../document-status.md)

<details>
<summary>Table of Contents</summary>

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [Overview](#overview)
- [EventLoggerProvider](#eventloggerprovider)
- [EventLogger](#eventlogger)
  * [Emit Event](#emit-event)
- [Additional Interfaces](#additional-interfaces)

<!-- tocstop -->

</details>

Users of OpenTelemetry need a way for instrumentation interactions with the
OpenTelemetry API to actually produce telemetry. The OpenTelemetry SDK
(henceforth referred to as the SDK) is an implementation of the OpenTelemetry
API that provides users with this functionally.

All implementations of the OpenTelemetry API MUST provide an SDK.

## Overview

From OpenTelemetry's perspective LogRecords and Events are both represented
using the same [data model](./event-api.md#data-model). Therefore, the default
implementation of an Event SDK MUST generate events using the [Logs Data Model](./data-model.md).

The SDK MAY be implemented on top of the [Logs Bridge API](./bridge-api.md).

## EventLoggerProvider

TODO

## EventLogger

TODO

### Emit Event

Emit a `LogRecord` representing an `Event`.

**Implementation Requirements:**

The implementation MUST use the parameters
to [emit a logRecord](./bridge-api.md#emit-a-logrecord) as follows:

* The `Name` MUST be used to set
  the `event.name` [Attribute](./data-model.md#field-attributes). If
  the `Attributes` provided by the user contain an `event.name` attribute the
  value provided in the `Name` takes precedence.
* If provided by the user, the `Payload` MUST be used to set
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

## Additional Interfaces

TODO
