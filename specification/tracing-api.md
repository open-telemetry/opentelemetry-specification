# Tracing API

<details>
<summary>
Table of Content
</summary>

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
* [SpanContext](#spancontext)
* [Span](#span)
  * [Span creation](#span-creation)
    * [StartSpan](#startspan)
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
* [Status](#status)
  * [StatusCanonicalCode](#statuscanonicalcode)
  * [Status creation](#status-creation)
  * [GetCanonicalCode](#getcanonicalcode)
  * [GetDescription](#getdescription)
  * [GetIsOk](#getisok)
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

A tracer SHOULD be obtained from a global registry, for example `OpenTelemetry.getTracer()`.

The registration to the registry depends on the language. In some languages the tracer is explicitly 
created and registered from user code and other languages the tracer implementation is resolved
from linked dependencies using provider pattern.

The tracer object construction depends on the implementation. Various implementations might require
to specify different configuration properties at creation time. In languages where provider pattern
is used the configuration is provided externally.

#### Tracer provider

Tracer provider is an internal class used by the global registry (`OpenTelemetry`) to get a tracer instance.
The global registry delegates calls to the provider every time a tracer instance is requested.
This is necessary for use-cases when a single instrumentation code runs for multiple deployments.

The tracer provider is registered to API usually via language-specific mechanism, for instance `ServiceLoader` in Java.

##### Runtime with multiple deployments/applications

Application runtimes which support multiple deployments/applications might need to provide a different
tracer instance to each deployment. In this case the runtime provides its own implementation of provider
which returns a different tracer for each deployment.

### Tracer operations

#### GetCurrentSpan

Returns the current Span from the current context.

There should be no parameter.

Returns the default `Span` that does nothing and has an invalid `SpanContext` if no
`Span` is associated with the current context, otherwise the current `Span` from the context.

#### WithSpan
Enters the scope of code where the given `Span` is in the current context.

Required parameters:

- The `Span` to be set to the current context.

Returns an object that defines a scope where the given `Span` will be set to the current context.

The scope is exited and previous state should be restored when the returned object is closed.

#### SpanBuilder
Returns a `SpanBuilder` to create and start a new `Span`
if a `Builder` pattern for [Span creation](#span-creation) is used.

Required parameters:

- Name of the span.

Returns a `SpanBuilder` to create and start a new `Span`.

#### RecordSpanData

Records a `SpanData`.

Required parameters:

- `SpanData` to be reported to all exporters.

This API allows to send a pre-populated span object to the exporter.
Sampling and recording decisions as well as other collection optimizations are a
responsibility of a caller.

Note, the `SpanContext` object in the span population with
the values that will allow correlation of telemetry is also a caller responsibility.

This API should be non-blocking.

#### GetBinaryFormat
Returns the binary format interface which can serialize/deserialize `Span`s.

There should be no parameter.

Returns the binary format for this implementation. If no implementation is provided
then no-op implementation will be used.

#### GetHttpTextFormat
Returns the HTTP text format interface which can inject/extract `Span`s.

There should be no parameter.

Returns the HTTP text format for this implementation. If no implementation is provided
then no-op implementation will be used.

Usually this will be the W3C Trace Context as the HTTP text format. For more details, see
[trace-context](https://github.com/w3c/trace-context).

## SpanContext
A `SpanContext` represents the portion of a `Span` which must be serialized and propagated along side of a distributed context. `SpanContext`s are immutable. `SpanContext` MUST be a final (sealed) class.

The OpenTelemetry `SpanContext` representation conforms to the [w3c TraceContext specification](https://www.w3.org/TR/trace-context/). It contains two identifiers - a `TraceId` and a `SpanId` - along with a set of common `TraceOptions` and system-specific `TraceState` values. `SpanContext` is represented as an interface, in order to be serializable into a wider variety of trace context wire formats. 

`TraceId` A valid trace identifier is a 16-byte array with at least one non-zero byte.

`SpanId` A valid span identifier is an 8-byte array with at least one non-zero byte.

`TraceOptions` contain details about the trace. Unlike Tracestate values, TraceOptions are present in all traces. Currently, the only TraceOption is a boolean `recorded` [flag](https://www.w3.org/TR/trace-context/#recorded-flag-00000001).

`Tracestate` carries system-specific configuration data, represented as a list of key-value pairs. TraceState allows multiple tracing systems to participate in the same trace. 

`IsValid` is a boolean flag which returns true if the SpanContext has a non-zero TraceID and a non-zero SpanID.

Please review the W3C specification for details on the [Tracestate field](https://www.w3.org/TR/trace-context/#tracestate-field).

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

API MUST provide a way to create a new `Span`. Each language implementation should
follow its own convention on `Span` creation, for example `Builder` in Java,
`Options` in Go, etc. `Span` creation method MUST be defined on `Tracer`.

Required parameters:

- Name of the span.

Optional parameters (or corresponding setters on `Builder` if using a `Builder` pattern):

- Parent `Span`. If not set, the value of [Tracer.getCurrentSpan](#getcurrentspan)
  at `StartSpan` time will be used as parent. MUST be used to create a `Span`
  when manual Context propagation is used OR when creating a root `Span` with
  a parent with an invalid `SpanContext`.
- Parent `SpanContext`. If not set, the value of [Tracer.getCurrentSpan](#getcurrentspan)
  at `StartSpan` time will be used as parent. MUST be used to create a `Span`
  when the parent is in a different process.
- The option to become a root `Span` for a new trace.
  If not set, the value of [Tracer.getCurrentSpan](#getcurrentspan) at `StartSpan`
  time will be used as parent.

- **Note**: The three parameters above (parent `Span`, parent `SpanContext` and `root`) are
  mutually exclusive. Based on language implementation, if multiple parameters are specified
  or corresponding `Setter`s are called multiple times, only the last specified value will be used.
  For example:
    1. `builder.setParent(parentSpan).setNoParent().startSpan()` will generate a new root span
    and `parentSpan` will be ignored;
    2. `tracer.StartSpan(options.WithNoParent(), options.WithParentContext(parentCtx))`
    will generate a new child span with remote parent `parentCtx`, and `WithNoParent` will be ignored.
  
  In languages that need to take all the three parameters at the same time when creating a `Span`,
  parent `Span` should take precedence, then remote parent `SpanContext`, and `root` comes last.
  For example:
    3. `tracer.start_span(name='span', parent_span=span1, parent_span_context=ctx, root=true)`
    will generate a new child span with parent `span1`, while `parent_span_context` and `root`
    will be ignored. 

- `Sampler` to the newly created `Span`. If not set, the implementation should provide a
  default sampler used by Tracer.
- Collection of `Link`s that will be associated with the newly created Span
- The override value for [a flag indicating whether events should be recorded](#isrecordingevents)
  for the newly created `Span`. If not set, the implementation will provide a default.
- `SpanKind` for the newly created `Span`. If not set, the implementation will
  provide a default value `INTERNAL`.

#### StartSpan

Starts a new `Span`.

If called multiple times with `Builder` pattern, the same `Span` will be returned.

There should be no parameter if using a `Builder` pattern. Otherwise, `StartSpan`
should accept all the optional parameters described in [Span creation](#span-creation).

Returns the newly created `Span`.

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

## Status

`Status` interface represents the status of a finished `Span`. It's composed of
a canonical code in conjuction with an optional descriptive message.

### StatusCanonicalCode

`StatusCanonicalCode` represents the canonical set of status codes of a finished `Span`, following the [Standard GRPC codes](https://github.com/grpc/grpc/blob/master/doc/statuscodes.md).

#### Ok

The operation completed successfully.

#### Cancelled

The operation was cancelled (typically by the caller).

#### UnknownError

An unknown error.

#### InvalidArgument

Client specified an invalid argument. Note that this differs from `FailedPrecondition`.
`InvalidArgument` indicates arguments that are problematic regardless of the state of the
system.

#### DeadlineExceeded

Deadline expired before operation could complete. For operations that change the state
of the system, this error may be returned even if the operation has completed successfully.

#### NotFound

Some requested entity (e.g., file or directory) was not found.

#### AlreadyExists

Some entity that we attempted to create (e.g., file or directory) already exists.

#### PermissionDenied

The caller does not have permission to execute the specified operation.
`PermissionDenied` must not be used if the caller cannot be
identified (use `Unauthenticated1` instead for those errors).

#### ResourceExhausted

Some resource has been exhausted, perhaps a per-user quota, or perhaps
the entire file system is out of space.

#### FailedPrecondition

Operation was rejected because the system is not in a state required for the operation's
execution.

#### Aborted

The operation was aborted, typically due to a concurrency issue like sequencer check
failures, transaction aborts, etc.

#### OutOfRange

Operation was attempted past the valid range. E.g., seeking or reading past end of file.
Unlike `InvalidArgument`, this error indicates a problem that may be fixed if the system
state changes.

#### Unimplemented

Operation is not implemented or not supported/enabled in this service.

#### InternalError

Internal errors. Means some invariants expected by underlying system has been broken.

#### Unavailable

The service is currently unavailable. This is a most likely a transient condition
and may be corrected by retrying with a backoff.

#### DataLoss

Unrecoverable data loss or corruption.

#### Unauthenticated

The request does not have valid authentication credentials for the operation.

### Status creation

API MUST provide a way to create a new `Status`.

Required parameters

- `StatusCanonicalCode` of this `Status`.

Optional parameters

- Description of this `Status`.

### GetCanonicalCode

Returns the `StatusCanonicalCode` of this `Status`.

### GetDescription

Returns the description of this `Status`.

### GetIsOk

Returns false if this `Status` represents an error, else returns true.

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
