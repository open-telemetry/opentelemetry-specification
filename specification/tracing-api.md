# Table of Content
<details>
<summary>
show
</summary>


   * [Tracing API](#tracing-api)
      * [Data types](#data-types)
         * [Time](#time)
            * [Timestamp](#timestamp)
            * [Duration](#duration)
      * [Tracer](#tracer)
         * [Obtaining a tracer](#obtaining-a-tracer)
         * [Tracer operations](#tracer-operations)
            * [GetCurrentSpan](#getcurrentspan)
            * [WithSpan](#withspan)
            * [SpanBuilder](#spanbuilder)
            * [RecordSpanData](#recordspandata)
            * [GetBinaryFormat](#getbinaryformat)
            * [GetHttpTextFormat](#gethttptextformat)
      * [Span](#span)
         * [Span creation](#span-creation)
         * [Span operations](#span-operations)
            * [GetContext](#getcontext)
            * [IsRecordingEvents](#isrecordingevents)
            * [SetAttribute](#setattribute)
            * [AddEvent](#addevent)
            * [AddLink](#addlink)
            * [SetStatus](#setstatus)
            * [UpdateName](#updatename)
            * [End](#end)
         * [Span lifetime](#span-lifetime)
      * [Link](#link)
         * [Link creation](#link-creation)
         * [GetContext](#getcontext-1)
         * [GetAttributes](#getattributes)
      * [SpanData](#spandata)
         * [Constructing SpanData](#constructing-spandata)
         * [Getters](#getters)
            * [GetName](#getname)
            * [GetKind](#getkind)
            * [GetStartTimestamp](#getstarttimestamp)
            * [GetEndTimestamp](#getendtimestamp)
            * [GetContext](#getcontext-2)
            * [GetParentSpanId](#getparentspanid)
            * [GetResource](#getresource)
            * [GetAttributes](#getattributes-1)
            * [GetTimedEvents](#gettimedevents)
            * [GetLinks](#getlinks)
            * [GetStatus](#getstatus)
</details>

# Tracing API

Tracing API consist of a few main classes:

- `Tracer` is used for all operations. See [Tracer](#tracer) section.
- `Span` is a mutable object storing information about the current operation
   execution. See [Span](#span) section.
- `SpanData` is an immutable object that is used to report out-of-band completed
  spans. See [SpanData](#spandata) section.

## Data types
While languages and platforms have different ways of representing data,
this section defines some generic requirements for this API.

### Time
OpenTelemetry can operate on time values up to nanosecond (ns) precision.
The representation of those values is language specific.

#### Timestamp
A timestamp is the time elapsed since the Unix epoch.
* The minimal precision is milliseconds.
* The maximal precision is nanoseconds.

#### Duration
A duration is the elapsed time between two events.
* The minimal precision is milliseconds.
* The maximal precision is nanoseconds.

## Tracer

### Obtaining a tracer

TODO: How tracer can be constructed? https://github.com/open-telemetry/opentelemetry-specification/issues/39

### Tracer operations

#### GetCurrentSpan

returns the current Span from the current context.

There should be no parameter.

Returns the default `Span` that does nothing and has an invalid `SpanContext` if no
`Span` is associated with the current context, otherwise the current `Span` from the context.

#### WithSpan
enters the scope of code where the given `Span` is in the current context.

Required parameters:

- The `Span` to be set to the current context.

Returns an object that defines a scope where the given `Span` will be set to the current context.

The scope is exited and previous state should be restored when the returned object is closed.

#### SpanBuilder
returns a `SpanBuilder` to create and start a new `Span`.

Required parameters:

- Name of the span.

Returns a `SpanBuilder` to create and start a new `Span`.

#### RecordSpanData

records a `SpanData`.

Required parameters:

- `SpanData` to be reported to all exporters.

This API allows to send a pre-populated span object to the exporter.
Sampling and recording decisions as well as other collection optimizations are a
responsibility of a caller.

Note, the `SpanContext` object in the span population with
the values that will allow correlation of telemetry is also a caller responsibility.

This API should be non-blocking.

#### GetBinaryFormat
returns the binary format interface which can serialize/deserialize `Span`s.

There should be no parameter.

Returns the binary format for this implementation. If no implementation is provided
then no-op implementation will be used.

#### GetHttpTextFormat
returns the HTTP text format interface which can inject/extract `Span`s.

There should be no parameter.

Returns the HTTP text format for this implementation. If no implementation is provided
then no-op implementation will be used.

Usually this will be the W3C Trace Context as the HTTP text format. For more details, see
[trace-context](https://github.com/w3c/trace-context).

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

`Span` interface can have alternative implementations. It is expected that
alternative implementations will be implementing vendor-specific logic. However,
implementation MUST NOT allow to directly create a `Span`. Alternative
implementation of `Span` can only be returned from alternative implementation of
`SpanBuilder`, which in turn is only available from the `Tracer`. See [Span
creation](#span-creation).

### Span creation

TODO: SpanBuilder API https://github.com/open-telemetry/opentelemetry-specification/issues/37

### Span operations

With the exception of the method to retrieve the `Span`'s `SpanContext` and
recording status, none of the below may be called after the `Span` is finished.

#### GetContext

Retrieve the `Span`s `SpanContext`

There should be no parameter.

Returns the `SpanContext` for the given `Span`. The returned value may be
used even after the `Span` is finished.

#### IsRecordingEvents

Returns the flag whether this span will be recorded.

There should be no parameter.

Returns true if this `Span` is active and recording information like events with
the `AddEvent` operation and attributes using `SetAttributes`.

#### SetAttribute

Set the `Span`'s attribute.

Required parameters

- The attribute key, which must be a string.
- The attribute value, which must be either a string, a boolean value, or a
  numeric type.

Note that the OpenTelemetry project documents certain ["standard
attributes"](../semantic-conventions.md) that have prescribed semantic meanings.

#### AddEvent

Add an `Event` to `Span`.

Required parameters:

- Name of the event.

Optional parameters:

- One or more key:value pairs, where the keys must be strings and the values may
  be string, booleans or numeric type.

Note that the OpenTelemetry project documents certain ["standard event names and
keys"](../semantic-conventions.md) which have prescribed semantic meanings.

#### AddLink

Adds a link to another `Span` from this `Span`. Linked `Span` can be from the
same or different trace. See [Links description](../terminology.md#links-between-spans).

Required parameters

- `SpanContext` of the `Span` to link to

Optional parameters

- Map of attributes associated with this link. Attributes are key:value pairs
  where hey is a string and value is one of string, boolean and numeric.

API MUST also provide an overload that accepts a [`Link` interface](#link). This
overload allows instrumentation to supply a lazily calculated `Link`.

#### SetStatus

Sets the `Status` to the `Span`. If used, this will override the default `Span`
status. Default is `OK`.

Only the value of the last call will be recorded, and implementations are free
to ignore previous calls.

Required parameters

- New status for the span.

#### UpdateName

Updates the `Span` name. Upon this update, any sampling behavior based on
`Span` name will depend on the implementation.

Required parameters:

- The new **operation name**, which supersedes whatever was passed in when the
  `Span` was started

#### End

Finish the `Span`. This call will take the current timestamp to set as `Span`'s
end time. Implementations MUST ignore all subsequent calls to `End` (there might
be exceptions when Tracer is streaming event and has no mutable state associated
with the `Span`).

Call to `End` of a `Span` MUST not have any effects on child spans. Those may
still be running and can be ended later.

There MUST be no parameter.

This API MUST be non-blocking.

### Span lifetime

Span lifetime represents the process of recording the start and the end
timestamps to the Span object:

- The start time is recorded when the Span is created.
- The end time needs to be recorded when the operation is ended.

Start and end time as well as Event's timestamps MUST be recorded at a time of a
calling of corresponding API and MUST not be passed as an argument. In order to
record already completed span - [`SpanData`](#spandata) API HAVE TO be used.

## Link

`Link` interface represents the [link between
spans](../terminology.md#links-between-spans). Interface only expose two
getters. API also MUST provide a way to create a Link.

### Link creation

API MUST provide a way to create a new `Link`.

Required parameters

- `SpanContext` of the `Span` to link to

Optional parameters

- Map of attributes associated with this link. Attributes are key:value pairs
  where key is a string and value is one of string, boolean and numeric.

### GetContext

Returns the `SpanContext` of a linked span.

### GetAttributes

Returns the immutable collection of attributes associated with this `Link`.
Order of attributes is not significant.

## SpanData

`SpanData` is an immutable and final class. All getters of `SpanData` are thread
safe and can be called any number of times.

`API` MUST provide a way of [constructing `SpanData`](#constructing-spandata)
that can be recorded using `Tracer` method `RecordSpanData`.

### Constructing SpanData

`SpanData` is an immutable object that can be constructed using the following
arguments:

- `SpanContext` identifying this `SpanData`.
- Parent's `SpanId`. All-zeroes `SpanId` or `null` MUST be assumed and
  interchangeable if `SpanData` has no parent.
- `Resource` this SpanData is recorded for. If not specified - `Tracer`'s
  `Resource` will be used instead when the `RecordSpanData` called on the
  `Tracer`.
- Name of this `SpanData`.
- `Kind` of this `SpanData`. `SpanKind.Internal` MUST be assumed as a default.
- Start and End timestamps.
- Set of attributes with the string key and the value, which must be either a
  string, a boolean value, or a numeric type.
- Set of `Events`.
- Set of `Links`.
- `Status` of `SpanData` execution.

All collections passes as an argument MUST be either immutable if language
allows it or copied so the change of the collection will not mutate the
`SpanData`.

### Getters

Getters will be called by exporters in SDK. Implementation MUST not assume that
getters will be called only once or at all. There also MUST be no expectations
on how soon getters will be called after object creation.

#### GetName

Returns the name of this `SpanData`.

#### GetKind

Returns the `SpanKind` of this `SpanData`.

#### GetStartTimestamp

Returns the start timestamp of this `SpanData`.

#### GetEndTimestamp

Returns the end timestamp of this `SpanData`.

#### GetContext

Returns the `SpanContext` associated with this `SpanData`.

#### GetParentSpanId

Returns the `SpanId` of the parent of this `SpanData`.

#### GetResource

Returns the `Resource` associated with this `SpanData`. When `null` is returned
the assumption is that `Resource` will be taken from the `Tracer` that is used
to record this `SpanData`.

#### GetAttributes

Returns the `Attributes` collection associated with this `SpanData`. The order
of attributes in collection is not significant. The typical use of attributes
collection is enumeration so the fast access to the label value by it's key is
not a requirement. This collection MUST be immutable.

#### GetTimedEvents

Return the collection of `Events` with the timestamps associated with this
`SpanData`. The order of events in collection is not guaranteed. This collection
MUST be immutable.

#### GetLinks

Returns the `Links` collection associated with this `SpanData`. The order
of links in collection is not significant. This collection MUST be immutable.

#### GetStatus

Returns the `Status` of this `SpanData`.
