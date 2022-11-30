# Events API Interface

**Status**: [Experimental](../document-status.md)

<details>
<summary>Table of Contents</summary>

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [EventLogger](#eventlogger)
  * [EventLogger Operations](#eventlogger-operations)
    + [Create EventLogger](#create-eventlogger)
    + [Emit Event](#emit-event)

<!-- tocstop -->

</details>

The Event API offers convenience methods
for [emitting LogRecords](./api.md#emit-logrecord) that conform
to the [semantic conventions for Events](./semantic_conventions/events.md).

## EventLogger

The `EventLogger` is the entrypoint of the Event API, and is responsible for
emitting `Events` as `LogRecords`.

### EventLogger Operations

The `EventLogger` MUST provide functions to:

#### Create EventLogger

New `EventLogger` instances are created though a constructor or factory method
on `EventLogger`.

**Parameters:**

* `logger` - the delegate [Logger](./api.md#logger) used to emit `Events`
  as `LogRecords`.
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
* `logRecord` - the [LogRecord](./api.md#logrecord) representing the Event.

**Implementation Requirements:**

The implementation MUST [emit](./api.md#emit-logrecord) the `logRecord` to
the `logger` specified when [creating the EventLogger](#create-eventlogger)
after making the following changes:

* The `event_domain` specified
  when [creating the EventLogger](#create-eventlogger) MUST be set as
  the `event.domain` attribute on the `logRecord`.
* The `event_name` MUST be set as the `event.name` attribute on the `logRecord`.
