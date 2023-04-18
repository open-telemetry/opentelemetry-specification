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

<!-- tocstop -->

</details>

## Overview

Wikipedia’s [definition of log file](https://en.wikipedia.org/wiki/Log_file):

>In computing, a log file is a file that records either events that occur in an
>operating system or other software runs.

From OpenTelemetry's perspective LogRecords and Events are both represented
using the same [data model](./data-model.md).

However, OpenTelemetry does recognize a subtle semantic difference between
LogRecords and Events: Events are LogRecords which have a `name` and `domain`.
Within a particular `domain`, the `name` uniquely defines a particular class or
type of event. Events with the same `domain` / `name` follow the same schema
which assists in analysis in observability platforms. Events are described in
more detail in the [semantic conventions](./semantic_conventions/events.md).

While the logging space has a diverse legacy with many existing logging
libraries in different languages, there is not ubiquitous alignment with
OpenTelemetry events. In some logging libraries, producing records shaped as
OpenTelemetry events is clunky or error-prone.

The Event API offers convenience methods
for [emitting LogRecords](./bridge-api.md#emit-a-logrecord) that conform
to the [semantic conventions for Events](./semantic_conventions/events.md).
Unlike the [Logs Bridge API](./bridge-api.md), application developers and
instrumentation authors are encouraged to call this API directly.

## EventLogger

The `EventLogger` is the entrypoint of the Event API, and is responsible for
emitting `Events` as `LogRecord`s.

### EventLogger Operations

The `EventLogger` MUST provide functions to:

#### Create EventLogger

New `EventLogger` instances are created though a constructor or factory method
on `EventLogger`.

**Parameters:**

* `logger` - the delegate [Logger](./bridge-api.md#logger) used to emit `Events`
  as `LogRecord`s.
* `event_domain` - the domain of emitted events, used to set the `event.domain`
  attribute.

#### Emit Event

Emit a `LogRecord` representing an `Event` to the delegate `Logger`.

This function MAY be named `logEvent`.

**Parameters:**

* `event_name` - the Event name. This argument MUST be recorded as a `LogRecord`
  attribute with the key `event.name`. Care MUST be taken by the implementation
  to not override or delete this attribute while the Event is emitted to
  preserve its identity.
* `logRecord` - the [LogRecord](./data-model.md#log-and-event-record-definition) representing the Event.

**Implementation Requirements:**

The implementation MUST [emit](./bridge-api.md#emit-a-logrecord) the `logRecord` to
the `logger` specified when [creating the EventLogger](#create-eventlogger)
after making the following changes:

* The `event_domain` specified
  when [creating the EventLogger](#create-eventlogger) MUST be set as
  the `event.domain` attribute on the `logRecord`.
* The `event_name` MUST be set as the `event.name` attribute on the `logRecord`.
