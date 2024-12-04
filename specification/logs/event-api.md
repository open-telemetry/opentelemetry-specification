# Events API

**Status**: [Deprecated](../document-status.md) (was never stabilized),
see [Emit Event](./api.md#emit-an-event) in the Logs API for replacement.

<details>
<summary>Table of Contents</summary>

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [Event Data model](#event-data-model)
- [Event API use cases](#event-api-use-cases)
- [EventLoggerProvider](#eventloggerprovider)
  * [EventLoggerProvider operations](#eventloggerprovider-operations)
    + [Get an EventLogger](#get-an-eventlogger)
- [EventLogger](#eventlogger)
  * [EventLogger Operations](#eventlogger-operations)
    + [Emit Event](#emit-event)
- [Optional and required parameters](#optional-and-required-parameters)
- [References](#references)

<!-- tocstop -->

</details>

The Event API consists of these main components:

* [EventLoggerProvider](#eventloggerprovider) is the entry point of the API. It
  provides access to `EventLogger`s.
* [EventLogger](#eventlogger) is the component responsible for emitting events.

## Event Data model

Wikipedia’s [definition of log file](https://en.wikipedia.org/wiki/Log_file):

>In computing, a log file is a file that records either events that occur in an
>operating system or other software runs.

From OpenTelemetry's perspective LogRecords and Events are both represented
using the same [data model](./data-model.md). An Event is a specialized type
of LogRecord, not a separate concept.

Events are OpenTelemetry's standardized semantic formatting for LogRecords.
Beyond the structure provided by the LogRecord data model, it is helpful for
logs to have a common format within that structure. When OpenTelemetry
instrumentation emits logs, those logs SHOULD be formatted as Events. All
semantic conventions defined for logs MUST be formatted as Events.

The Event format is as follows. All Events have a
[`event.name` attribute](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/general/events.md),
and all Events with the same `event.name` MUST conform to the same schema for
both their `Attributes` and their `Body`.

## Event API use cases

The Events API was designed to allow shared libraries to emit high quality
logs without needing to depend on a third party logger. Unlike the
[Logs API](./api.md), instrumentation authors and application
developers are encouraged to call this API directly. It is appropriate to
use the Event API when these properties fit your requirements:

* Logging from a shared library that must run in many applications.
* A semantic convention needs to be defined. We do not define semantic
  conventions for LogRecords that are not Events.
* Analysis by an observability platform is the intended use case. For
  example: statistics, indexing, machine learning, session replay.
* Normalizing logging and having a consistent schema across a large
  application is helpful.

If any of these properties fit your requirements, we recommend using the Event API.
Events are described in more detail in the [semantic conventions](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/general/events.md).

Please note that the OpenTelemetry Log SDK currently lacks a number of advanced
features present in popular logging libraries. For example: pattern logging, file
rotation, network appenders, etc. These features cannot be used with the
OpenTelemetry Event SDK at this time.

If a logging library is capable of creating logs which correctly map
to the Event data model, logging in this manner is also an acceptable way to
create Events.

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

* `name`: Specifies the name of the [instrumentation scope](../glossary.md#instrumentation-scope),
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

The term *identical* applied to `EventLogger`s describes instances where all
parameters are equal. The term *distinct* applied to `EventLogger`s describes
instances where at least one parameter has a different value.

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
* The (`AnyValue`) (optional) `Body` of the Event.
* The `Timestamp` (optional) of the Event.
* The [Context](../context/README.md) (optional) associated with the Event.
* The `SeverityNumber` (optional) of the Event.
* The `Attributes` (optional) of the Event. Event `Attributes` provide
  additional details about the Event which are not part of the
  well-defined event `Body`.

## Optional and required parameters

The operations defined include various parameters, some of which are marked
optional. Parameters not marked optional are required.

For each optional parameter, the API MUST be structured to accept it, but MUST
NOT obligate a user to provide it.

For each required parameter, the API MUST be structured to obligate a user to
provide it.

## References

- [OTEP0202 Introducing Events and Logs API](https://github.com/open-telemetry/oteps/blob/main/text/0202-events-and-logs-api.md)
