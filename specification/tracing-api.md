# Tracing API

Tracing API consist of a few main classes:

- `Tracer` is used for all operations. See [Tracer](#tracer) section.
- `Span` is a mutable object storing information about the current operation
   execution. See [Span](#span) section.
- `SpanData` is an immutable object that is used to report completed spans. See
  [SpanData](#spandata) section.

## Tracer

### Obtaining a tracer

TBD

### Tracer operations

TBD

## Span

Span represents a single operation within a trace. Spans can be nested to form a
trace tree. Often, a trace contains a root span that describes the end-to-end
latency and, optionally, one or more sub-spans for its sub-operations.

### Span creation

TBD

### Span operations

With the exception of the method to retrieve the `Span`'s `SpanContext`, none of
the below may be called after the `Span` is finished.

#### `GetContext`: retrieve the `Span`s `SpanContext`

There should be no parameters.

**Returns** the `SpanContext` for the given `Span`. The returned value may be
used even after the `Span` is finished.

isRecordingEvents

### `SetAttribute`: set the `Span`'s attribute

Required parameters

- The attribute key, which must be a string.
- The attribute value, which must be either a string, a boolean value, or a
  numeric type.

Note that the OpenTelemetry project documents certain ["standard
attributes"](../semantic-conventions.md) that have prescribed semantic meanings.

### `AddEvent`: add an `Event` to `Span`

Required parameters

- One or more key:value pairs, where the keys must be strings and the values may
  be string, booleans or numeric type.

Note that the OpenTelemetry project documents certain ["standard event
keys"](../semantic-conventions.md) which have prescribed semantic meanings.

### `AddLink`: add a `Link` from this `Span` to another

TBD

### `SetStatus`: set the span result status

TBD

#### `UpdateName`: overwrite the operation name

Updates the `Span` name. Upon this update, any sampling behavior based on
`Span` name will depend on the implementation.

Required parameters:

- The new **operation name**, which supersedes whatever was passed in when the
  `Span` was started

#### `End`: finish the `Span`

Optional parameters

There should be no parameters.

### Span lifetime

Span lifetime represents the process of recording the start and the end
timestamps to the Span object:

- The start time is recorded when the Span is created.
- The end time needs to be recorded when the operation is ended.

Start and end time as well as Event's timestamps MUST be recorded at a time of a
calling of corresponding API and MUST not be passed as an argument. In order to
record already completed span - [`SpanData`](#spandata) API HAVE TO be used.

## SpanData

TBD