# Tracing API

<details>
<summary>
Table of Contents
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
  * [Span operations](#span-operations)
    * [Get Context](#get-context)
    * [IsRecordingEvents](#isrecordingevents)
    * [Set Attributes](#set-attributes)
    * [Add Events](#add-events)
    * [Add Links](#add-links)
    * [Set Status](#set-status)
    * [UpdateName](#updatename)
    * [End](#end)
  * [Span lifetime](#span-lifetime)
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
    * [GetContext](#getcontext)
    * [GetParentSpanId](#getparentspanid)
    * [GetResource](#getresource)
    * [GetAttributes](#getattributes)
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

The OpenTelemetry library achieves in-process context propagation of `Span`s by
way of the `Tracer`.

The `Tracer` is responsible for tracking the currently active `Span`, and
exposes methods for creating and activating new `Span`s. The `Tracer` is
configured with `Propagator`s which support transferring span context across
process boundaries.

`Tracer`s are generally expected to be used as singletons. Implementations
SHOULD provide a single global default `Tracer`.

Some applications may require multiple `Tracer` instances, e.g. to create
`Span`s on behalf of other applications. Implementations MAY provide a global
registry of `Tracer`s for such applications.

### Obtaining a tracer

`Tracer` object construction and registration will vary by implementation.
`Tracer`s may be explicitly created and registered from user code, or resolved
from linked dependencies using the provider pattern.

Implementations might require the user to specify configuration properties at
`Tracer` creation time, or rely on external configuration, e.g. when using the
provider pattern.

##### Runtimes with multiple deployments/applications

Runtimes that support multiple deployments or applications might need to
provide a different `Tracer` instance to each deployment. To support this,

the global `Tracer` registry may delegate calls to create new `Tracer`s to a
separate `Provider` component, and the runtime may include its own `Provider`
implementation which returns a different `Tracer` for each deployment.

`Provider`s are registered with the API via some language-specific mechanism,
for instance the `ServiceLoader` class in Java.

### Tracer operations

The `Tracer` MUST provide methods to:

- Get the currently active `Span`
- Create a new `Span`
- Make a given `Span` as active

The `Tracer` SHOULD allow end users to configure other tracing components that
control how `Span`s are passed across process boundaries, including the binary
and text format `Propagator`s used to serialize `Span`s created by the
`Tracer`.

When getting the current span, the `Tracer` MUST return a placeholder `Span`
with an invalid `SpanContext` if there is no currently active `Span`.

When creating a new `Span`, the `Tracer` MUST allow the caller to specify the
new `Span`'s parent in the form of a `Span` or `SpanContext`. The `Tracer`
SHOULD create each new `Span` as a child of its active `Span` unless an
explicit parent is provided or the option to create a span without a parent is
selected, or the current active `Span` is invalid.

The `Tracer` MUST provide a way to update its active `Span`, and MAY provide
convenience methods to manage a `Span`'s lifetime and the scope in which a
`Span` is active. When an active `Span` is made inactive, the previously-active
`Span` SHOULD be made active. A `Span` maybe finished (i.e. have a non-null end
time) but stil active. A `Span` may be active on one thread after it has been
made inactive on another.

The `Tracer` MUST support recording `Span`s that were created _out of band_,
i.e.  not by the tracer itself. For this reason, implementations MUST NOT
require that a `Span`'s start and end timestamps match the wall time when it is
created, made active, or finished.

The implementation MUST provide no-op binary and text `Propagator`s, which the
`Tracer` SHOULD use by default if other propagators are not configured. SDKs
SHOULD use the W3C HTTP Trace Context as the default text format. For more
details, see [trace-context](https://github.com/w3c/trace-context).

## SpanContext

A `SpanContext` represents the portion of a `Span` which must be serialized and
propagated along side of a distributed context. `SpanContext`s are immutable.
`SpanContext` MUST be a final (sealed) class.

The OpenTelemetry `SpanContext` representation conforms to the [w3c TraceContext
specification](https://www.w3.org/TR/trace-context/). It contains two
identifiers - a `TraceId` and a `SpanId` - along with a set of common
`TraceFlags` and system-specific `TraceState` values. `SpanContext` is
represented as an interface, in order to be serializable into a wider variety of
trace context wire formats. 

`TraceId` A valid trace identifier is a 16-byte array with at least one
non-zero byte.

`SpanId` A valid span identifier is an 8-byte array with at least one non-zero
byte.

`TraceFlags` contain details about the trace. Unlike Tracestate values,
TraceFlags are present in all traces. Currently, the only `TraceFlags` is a
boolean `sampled`
[flag](https://www.w3.org/TR/trace-context/#trace-flags).

`Tracestate` carries system-specific configuration data, represented as a list
of key-value pairs. TraceState allows multiple tracing systems to participate in
the same trace. 

`IsValid` is a boolean flag which returns true if the SpanContext has a non-zero
TraceID and a non-zero SpanID.

Please review the W3C specification for details on the [Tracestate
field](https://www.w3.org/TR/trace-context/#tracestate-field).

## Span

A `Span` represents a single operation within a trace. Spans can be nested to
form a trace tree. Each trace contains a root span, which typically describes
the end-to-end latency and, optionally, one or more sub-spans for its
sub-operations.

`Span`s encapsulate:

- The operation name
- An immutable [`SpanContext`](#SpanContext) that uniquely identifies the
  `Span`
- A parent span in the form of a [`Span`](#Span), [`SpanContext`](#SpanContext),
  or null
- A start timestamp
- An end timestamp
- An ordered mapping of [`Attribute`s](#Set-Attributes)
- A list of [`Link`s](#add-Links) to other `Span`s
- A list of timestamped [`Event`s](#add-events)
- A [`Status`](#set-status).

The `Span`'s start and end timestamps reflect the elapsed real time of the
operation. A `Span`'s start time SHOULD be set to the current time on [span
creation](#span-creation). After the `Span` is created, it SHOULD be possible to
change the its name, set its `Attribute`s, and add `Link`s and `Event`s. These
MUST NOT be changed after the `Span`'s end time has been set.

`Span`s are not meant to be used to propagate information within a process. To
prevent misuse, implementations SHOULD NOT provide access to a `Span`'s
attributes besides its `SpanContext`.

Vendors may implement the `Span` interface to effect vendor-specific logic.
However, alternative implementations MUST NOT allow callers to create `Span`s
directly. All `Span`s MUST be created via a `Tracer`.

### Span Creation

Implementations MUST provide a way to create `Span`s via a `Tracer`, which is
responsible for tracking the currently active `Span` and MAY provide default
options for newly created `Span`s.

The API SHOULD require the caller to provide:
- The operation name
- The parent span, and whether the new `Span` should be a root `Span`.

The API MUST allow users to provide the following properties, which SHOULD be
empty by default:
- `Attribute`s
- `Link`s
- `Event`s

Each span has zero or one parent span and zero or more child spans, which
represent causally related operations. A tree of related spans comprises a
trace. A span is said to be a _root span_ if it does not have a parent. Each
trace includes a single root span, which is the shared ancestor of all other
spans in the trace. Implementations MUST provide an option to create a `Span` as
a root span, and MUST generate a new `TraceId` for each root span created.

A `Span` is said to have a _remote parent_ if it is the child of a `Span`
created in another process. Since the `SpanContext` is the only component of a
`Span` that is propagated between processes, a `Span`'s parent SHOULD be a
`SpanContext` if it is remote. Otherwise, it may be a `Span` or `SpanContext`.


### Span operations

With the exception of the method to retrieve the `Span`'s `SpanContext` and
recording status, none of the below may be called after the `Span` is finished.

#### Get Context

The Span interface MUST provide:
- An API that returns the `SpanContext` for the given `Span`. The returned value
  may be used even after the `Span` is finished. The returned value MUST be the
  same for the entire Span lifetime. This MAY be called `GetContext`.

#### IsRecordingEvents

Returns the flag whether this span will be recorded.

There should be no parameter.

Returns true if this `Span` is active and recording information like events with
the `AddEvent` operation and attributes using `SetAttributes`.

#### Set Attributes

A `Span` MUST have the ability to set attributes associated with it.

An `Attribute` is defined by the following properties:
- (Required) The attribute key, which must be a string.
- (Required) The attribute value, which must be either a string, a boolean
value, or a numeric type.

The Span interface MUST provide:
- An API to set a single `Attribute` where the attribute properties are passed
as arguments. This MAY be called `SetAttribute`. To avoid extra allocations some
implementations may offer a separate API for each of the possible value types.

Attributes SHOULD preserve the order in which they're set. Setting an attribute
with the same key as an existing attribute SHOULD overwrite the existing
attribute's value.

Note that the OpenTelemetry project documents certain ["standard
attributes"](data-semantic-conventions.md) that have prescribed semantic meanings.

#### Add Events

A `Span` MUST have the ability to add events. Events have a time associated
with the moment when they are added to the `Span`.

An `Event` is defined by the following properties:
- (Required) Name of the event.
- (Optional) One or more `Attribute`.

The `Event` SHOULD be an immutable type.

The Span interface MUST provide:
- An API to record a single `Event` where the `Event` properties are passed as
arguments. This MAY be called `AddEvent`.
- An API to record a single lazily initialized `Event`. This can be implemented
by providing an `Event` interface or a concrete `Event` definition and an
`EventFormatter`. If the language supports overloads then this SHOULD be called
`AddEvent` otherwise `AddLazyEvent` may be considered.

Events SHOULD preserve the order in which they're set. This will typically match
the ordering of the events' timestamps.

Note that the OpenTelemetry project documents certain ["standard event names and
keys"](data-semantic-conventions.md) which have prescribed semantic meanings.

#### Add Links

A `Span` MUST have the ability to record links to other `Span`s. Linked `Span`s
can be from the same or a different trace. See [Links
description](overview.md#links-between-spans).

A `Link` is defined by the following properties:
- (Required) `SpanContext` of the `Span` to link to.
- (Optional) One or more `Attribute`.

The `Link` SHOULD be an immutable type.

The Span interface MUST provide:
- An API to record a single `Link` where the `Link` properties are passed as
arguments. This MAY be called `AddLink`.
- An API to record a single lazily initialized `Link`. This can be implemented
by providing a `Link` interface or a concrete `Link` definition and a
`LinkFormatter`. If the language supports overloads then this MAY be called
`AddLink` otherwise `AddLazyLink` MAY be consider.

Links SHOULD preserve the order in which they're set.

#### Set Status

Sets the [`Status`](#status) of the `Span`. If used, this will override the
default `Span` status, which is `OK`.

Only the value of the last call will be recorded, and implementations are free
to ignore previous calls.

The Span interface MUST provide:
- An API to set the `Status` where the new status is the only argument. This
SHOULD be called `SetStatus`.

#### UpdateName

Updates the `Span` name. Upon this update, any sampling behavior based on `Span`
name will depend on the implementation.

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

## Status

`Status` interface represents the status of a finished `Span`. It's composed of
a canonical code in conjunction with an optional descriptive message.

### StatusCanonicalCode

`StatusCanonicalCode` represents the canonical set of status codes of a finished
`Span`, following the [Standard GRPC
codes](https://github.com/grpc/grpc/blob/master/doc/statuscodes.md):

- `Ok`
  - The operation completed successfully.
- `Cancelled`
  - The operation was cancelled (typically by the caller).
- `UnknownError`
  - An unknown error.
- `InvalidArgument`
  - Client specified an invalid argument. Note that this differs from
  `FailedPrecondition`. `InvalidArgument` indicates arguments that are problematic
  regardless of the state of the system.
- `DeadlineExceeded`
  - Deadline expired before operation could complete. For operations that change the
  state of the system, this error may be returned even if the operation has
  completed successfully.
- `NotFound`
  - Some requested entity (e.g., file or directory) was not found.
- `AlreadyExists`
  - Some entity that we attempted to create (e.g., file or directory) already exists.
- `PermissionDenied`
  - The caller does not have permission to execute the specified operation.
  `PermissionDenied` must not be used if the caller cannot be identified (use
  `Unauthenticated1` instead for those errors).
- `ResourceExhausted`
  - Some resource has been exhausted, perhaps a per-user quota, or perhaps the
  entire file system is out of space.
- `FailedPrecondition`
  - Operation was rejected because the system is not in a state required for the
  operation's execution.
- `Aborted`
  - The operation was aborted, typically due to a concurrency issue like sequencer
  check failures, transaction aborts, etc.
- `OutOfRange`
  - Operation was attempted past the valid range. E.g., seeking or reading past end
  of file. Unlike `InvalidArgument`, this error indicates a problem that may be
  fixed if the system state changes.
- `Unimplemented`
  - Operation is not implemented or not supported/enabled in this service.
- `InternalError`
  - Internal errors. Means some invariants expected by underlying system has been
  broken.
- `Unavailable`
  - The service is currently unavailable. This is a most likely a transient
  condition and may be corrected by retrying with a backoff.
- `DataLoss`
  - Unrecoverable data loss or corruption.
- `Unauthenticated`
  - The request does not have valid authentication credentials for the operation.

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

Returns the `Links` collection associated with this `SpanData`. The order of
links in collection is not significant. This collection MUST be immutable.

#### GetStatus

Returns the `Status` of this `SpanData`.
