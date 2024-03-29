# Events API

**Status**: [Experimental](../document-status.md)

<details>
<summary>Table of Contents</summary>

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [Events API](#events-api)
  - [Data model](#data-model)
  - [EventLoggerProvider](#eventloggerprovider)
    - [EventLoggerProvider operations](#eventloggerprovider-operations)
      - [Get an EventLogger](#get-an-eventlogger)
  - [EventLogger](#eventlogger)
    - [EventLogger Operations](#eventlogger-operations)
      - [Emit Event](#emit-event)
  - [Optional and required parameters](#optional-and-required-parameters)
  - [References](#references)

<!-- tocstop -->

</details>

The Event API consists of these main components:

* [EventLoggerProvider](#eventloggerprovider) is the entry point of the API. It provides access to `EventLogger`s.
* [EventLogger](#eventlogger) is the component responsible for emitting events.

## Data model

Wikipedia’s [definition of log file](https://en.wikipedia.org/wiki/Log_file):

>In computing, a log file is a file that records either events that occur in an
>operating system or other software runs.

From OpenTelemetry's perspective LogRecords and Events are both represented
using the same [data model](./data-model.md). An Event is a specialized type
of LogRecord, not a seperate concept.

Events contain all of the features provided by LogRecords, plus one additional
feature. All Events have a `name`.  Events with the same `name` MUST conform to
the same schema for both their `Attributes` and their `Body`.

Unlike the [Logs Bridge API](./bridge-api.md), application developers and
instrumentation authors are encouraged to call this API directly. It is 
appropriate to use the Event API when these properties fit your requirements:

* A consistent schema that can be identified by a name is necessary.
* Analysis by an Observability platform is the intended use case. For
  example: statistics, indexing, machine learning, session replay.
* A semantic convention needs to be defined. We do not define semantic
  conventions for LogRecords that are not Events.

If any of these properties fit your requirements, we recommend using the Event API.
Events are described in more detail in the [semantic conventions](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/general/events.md).

Please note that Events are sent directly to the OTel Log SDK, which currently lacks a
number of advanced features present in popular log frameworks. For example: 
pattern logging, file rotation, network appenders, etc. These features cannot be
used with Events at this time.

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
instances are returned. It is a user error to create `EventLogger`s with different
`attributes` but the same identity.

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
