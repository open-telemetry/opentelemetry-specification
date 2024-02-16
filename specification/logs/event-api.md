# Events API Interface

**Status**: [Experimental](../document-status.md)

<details>
<summary>Table of Contents</summary>

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [Overview](#overview)
- [EventLogger](#eventlogger)
  * [EventLogger Operations](#eventlogger-operations)
    + [Create EventLogger](#create-eventlogger)
    + [Emit Event](#emit-event)
- [Optional and required parameters](#optional-and-required-parameters)

<!-- tocstop -->

</details>

## Overview

Wikipedia’s [definition of log file](https://en.wikipedia.org/wiki/Log_file):

>In computing, a log file is a file that records either events that occur in an
>operating system or other software runs.

From OpenTelemetry's perspective LogRecords and Events are both represented
using the same [data model](./data-model.md).

However, OpenTelemetry does recognize a subtle semantic difference between
LogRecords and Events: Events are LogRecords which have a `name` which uniquely
defines a particular class or type of event. All events with the same `name`
have `Payloads` that conform to the same schema, which assists in analysis in
observability platforms. Events are described in more detail in
the [semantic conventions](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/general/events.md).

While the logging space has a diverse legacy with many existing logging
libraries in different languages, there is not ubiquitous alignment with
OpenTelemetry events. In some logging libraries, producing records shaped as
OpenTelemetry events is clunky or error-prone.

The Event API offers convenience methods
for [emitting LogRecords](./bridge-api.md#emit-a-logrecord) that conform
to the [semantic conventions for Events](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/general/events.md).
Unlike the [Logs Bridge API](./bridge-api.md), application developers and
instrumentation authors are encouraged to call this API directly.

The Event API consists of these main components:

* [EventLoggerProvider](#eventloggerprovider) is the entry point of the API. It provides access to `EventLogger`s.
* [EventLogger](#eventlogger) is the component responsible for emitting events.

## EventLoggerProvider

`EventLogger`s can be accessed with a `EventLoggerProvider`.

Normally, the `EventLoggerProvider` is expected to be accessed from a central place.
Thus, the API SHOULD provide a way to set/register and access a global default
`EventLoggerProvider`.

### EventLoggerProvider operations

The `EventLoggerProvider` MUST provide the following functions:

* Get an `EventLogger`

#### Get an EventLogger

This API MUST accept the following parameters:

* `name`: This name uniquely identifies the [instrumentation scope](../glossary.md#instrumentation-scope),
  such as the [instrumentation library](../glossary.md#instrumentation-library)
  (e.g. `io.opentelemetry.contrib.mongodb`), package, module or class name.
  If an application or library has built-in OpenTelemetry instrumentation, both
  [Instrumented library](../glossary.md#instrumented-library) and
  [Instrumentation library](../glossary.md#instrumentation-library) may refer to
  the same library. In that scenario, the `name` denotes a module name or component
  name within that library or application.

* `version` (optional): Specifies the version of the instrumentation scope if
  the scope has a version (e.g. a library version). Example value: 1.0.0.

* `schema_url` (optional): Specifies the Schema URL that should be recorded in
  the emitted telemetry.

* `attributes` (optional): Specifies the instrumentation scope attributes to
  associate with emitted telemetry. This API MUST be structured to accept a
  variable number of attributes, including none.

`EventLogger`s are identified by `name`, `version`, and `schema_url` fields.  When more
than one `EventLogger` of the same `name`, `version`, and `schema_url` is created, it
is unspecified whether or under which conditions the same or different `EventLogger`
instances are returned. It is a user error to create EventLoggers with different
`attributes` but the same identity.

The term *identical* applied to `EventLogger`s describes instances where all
identifying fields are equal. The term *distinct* applied to `EventLogger`s describes
instances where at least one identifying field has a different value.

The effect of associating a Schema URL with a `EventLogger` MUST be that the telemetry
emitted using the `EventLogger` will be associated with the Schema URL, provided that
the emitted data format is capable of representing such association.

## EventLogger

The `EventLogger` is the entrypoint of the Event API, and is responsible for
emitting `Events` as `LogRecord`s.

### EventLogger Operations

The `EventLogger` MUST provide functions to:

#### Emit Event

The effect of calling this API is to emit an `Event` to the processing pipeline.

**Parameters:**

* The `Name` of the Event, as described
  in [event.name semantic conventions](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/general/events.md).
* The (`AnyValue`) (optional) `Payload` of the Event.
* The `Timestamp` (optional) of the Event.
* The [Context](../context/README.md) (optional) associated with the Event.
* The `SeverityNumber` (optional) of the Event.
* The `Attributes` (optional) of the Event. Event `Attributes` provide
  additional details about the Event which are not part of the
  well-defined `Payload`.

**Implementation Requirements:**

The implementation MUST use the parameters
to [emit a logRecord](./bridge-api.md#emit-a-logrecord) using the `EventLogger`
specified when [creating the EventLogger](#create-eventlogger) as follows:

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

## Optional and required parameters

The operations defined include various parameters, some of which are marked
optional. Parameters not marked optional are required.

For each optional parameter, the API MUST be structured to accept it, but MUST
NOT obligate a user to provide it.

For each required parameter, the API MUST be structured to obligate a user to
provide it.
