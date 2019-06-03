# Tracing API

Tracing API consist of a few main classes:

- `Tracer` is used for all operations. See [Tracer](#tracer) section.
- `Span` is a mutable object storing information about the current operation
   execution. See [Span](#span) section.
- `SpanData` is an immutable object that is used to report out-of-band completed
  spans. See [SpanData](#spandata) section.

## Tracer

### Obtaining a tracer

TODO: How tracer can be constructed? https://github.com/open-telemetry/opentelemetry-specification/issues/39

### Tracer operations

TODO: Tracing operations. https://github.com/open-telemetry/opentelemetry-specification/issues/38

## Span

Span represents a single operation within a trace. Spans can be nested to form a
trace tree. Often, a trace contains a root span that describes the end-to-end
latency and, optionally, one or more sub-spans for its sub-operations.

Once Span [is created](#span-creation) - Span operations can be used to add
additional properties to it like attributes, links, events, name and resulting
status. Span cannot be used to retrieve these properties. This prevents the
mis-use of spans as an in-process information propagation mechanism.

The only two getters on span returns `SpanContext` and the flag on whether span
will be recorded.

### Span creation

TODO: SpanBuilder API https://github.com/open-telemetry/opentelemetry-specification/issues/37

### Span operations

With the exception of the method to retrieve the `Span`'s `SpanContext` and
recording status, none of the below may be called after the `Span` is finished.

#### `GetContext`: retrieve the `Span`s `SpanContext`

There should be no parameters.

**Returns** the `SpanContext` for the given `Span`. The returned value may be
used even after the `Span` is finished.

#### `IsRecordingEvents`: returns the flag whether this span will be recorded

There should be no parameters.

Returns true if this `Span` is active and recording information like events with
the `AddEvent` operation and attributes using `SetAttributes`.

### `SetAttribute`: set the `Span`'s attribute

Required parameters

- The attribute key, which must be a string.
- The attribute value, which must be either a string, a boolean value, or a
  numeric type.

Note that the OpenTelemetry project documents certain ["standard
attributes"](../semantic-conventions.md) that have prescribed semantic meanings.

### `AddEvent`: add an `Event` to `Span`

Required parameters:

- Name of the event.

Optional parameters:

- One or more key:value pairs, where the keys must be strings and the values may
  be string, booleans or numeric type.

Note that the OpenTelemetry project documents certain ["standard event names and
keys"](../semantic-conventions.md) which have prescribed semantic meanings.

### `AddLink`: add a `Link` from this `Span` to another

Adds a link to another `Span` from this `Span`. Linked `Span` can be from the
same or different trace. See [Links description](../terminology.md#links-between-spans).

Required parameters

- `SpanContext` of the `Span` to link to

Optional parameters

- Map of attributes associated with this link. Attributes are key:value pairs
  where hey is a string and value is one of string, boolean and numeric.

### `SetStatus`: set the span result status

Sets the `Status` to the `Span`. If used, this will override the default `Span`
status. Default is `OK`.

Only the value of the last call will be recorded, and implementations are free
to ignore previous calls.

Required parameters

- New status for the span.

#### `UpdateName`: overwrite the operation name

Updates the `Span` name. Upon this update, any sampling behavior based on
`Span` name will depend on the implementation.

Required parameters:

- The new **operation name**, which supersedes whatever was passed in when the
  `Span` was started

#### `End`: finish the `Span`

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

TODO: SpanData operations https://github.com/open-telemetry/opentelemetry-specification/issues/35
