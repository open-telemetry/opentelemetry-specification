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
    * [GetBinaryFormat](#getbinaryformat)
    * [GetHttpTextFormat](#gethttptextformat)
* [SpanContext](#spancontext)
* [Span](#span)
  * [Span creation](#span-creation)
    * [Add Links](#add-links)
  * [Span operations](#span-operations)
    * [Get Context](#get-context)
    * [IsRecording](#isrecording)
    * [Set Attributes](#set-attributes)
    * [Add Events](#add-events)
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
* [SpanKind](#spankind)

</details>

Tracing API consist of a few main classes:

- `Tracer` is used for all operations. See [Tracer](#tracer) section.
- `Span` is a mutable object storing information about the current operation
   execution. See [Span](#span) section.

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

### Obtaining a Tracer

New `Tracer` instances can be created via a `TracerFactory` and its `getTracer`
method. This method expects two string arguments:

- `name` (required): This name must identify the instrumentation library (also
referred to as integration, e.g. `io.opentelemetry.contrib.mongodb`) and *not*
the instrumented library.  
In case an invalid name (null or empty string) is specified, a working
default Tracer implementation as a fallback is returned rather than returning
null or throwing an exception.  
A library, implementing the OpenTelemetry API *may* also ignore this name and
return a default instance for all calls, if it does not support "named"
functionality (e.g. an implementation which is not even observability-related).
A TracerFactory could also return a no-op Tracer here if application owners configure
the SDK to suppress telemetry produced by this library.
- `version` (optional): Specifies the version of the instrumentation library
(e.g. `semver:1.0.0`).

Implementations might require the user to specify configuration properties at
`TracerFactory` creation time, or rely on external configuration, e.g. when using the
provider pattern.

##### Runtimes with multiple deployments/applications

Runtimes that support multiple deployments or applications might need to
provide a different `TracerFactory` instance to each deployment. To support this,
the global `TracerFactory` registry may delegate calls to create new instances of
`TracerFactory` to a separate `Provider` component, and the runtime may include
its own `Provider` implementation which returns a different `TracerFactory` for
each deployment.

`Provider` instances are registered with the API via some language-specific
mechanism, for instance the `ServiceLoader` class in Java.

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
`TraceFlags` and system-specific `TraceState` values.

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

`IsRemote` is a boolean flag which returns true if the SpanContext was propagated 
from a remote parent.

Please review the W3C specification for details on the [Tracestate
field](https://www.w3.org/TR/trace-context/#tracestate-field).

## Span

A `Span` represents a single operation within a trace. Spans can be nested to
form a trace tree. Each trace contains a root span, which typically describes
the end-to-end latency and, optionally, one or more sub-spans for its
sub-operations.

`Span`s encapsulate:

- The operation name
- An immutable [`SpanContext`](#spancontext) that uniquely identifies the
  `Span`
- A parent span in the form of a [`Span`](#span), [`SpanContext`](#spancontext),
  or null
- A start timestamp
- An end timestamp
- An ordered mapping of [`Attribute`s](#set-attributes)
- A list of [`Link`s](#add-links) to other `Span`s
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

Implementations MUST provide a way to create `Span`s via a `Tracer`. By default,
the currently active `Span` is set as the new `Span`'s parent. The `Tracer`
MAY provide other default options for newly created `Span`s.

`Span` creation MUST NOT set the newly created `Span` as the currently
active `Span` by default, but this functionality MAY be offered additionally
as a separate operation.

The API SHOULD require the caller to provide:
- The operation name
- The parent span, and whether the new `Span` should be a root `Span`

The API MUST allow users to provide the following properties, which SHOULD be
empty by default:
- [`SpanKind`](#spankind)
- `Attribute`s - similar API with [Span::SetAttributes](#set-attributes)
- `Link`s - see API definition [here](#add-links)
- `Start timestamp`

Each span has zero or one parent span and zero or more child spans, which
represent causally related operations. A tree of related spans comprises a
trace. A span is said to be a _root span_ if it does not have a parent. Each
trace includes a single root span, which is the shared ancestor of all other
spans in the trace. Implementations MUST provide an option to create a `Span` as
a root span, and MUST generate a new `TraceId` for each root span created.

A `Span` is said to have a _remote parent_ if it is the child of a `Span`
created in another process. Each propagators' deserialization must set 
`IsRemote` to true so `Span` creation knows if the parent is remote.

#### Add Links

During the `Span` creation user MUST have the ability to record links to other `Span`s. Linked
`Span`s can be from the same or a different trace. See [Links
description](overview.md#links-between-spans).

A `Link` is defined by the following properties:
- (Required) `SpanContext` of the `Span` to link to.
- (Optional) One or more `Attribute`.

The `Link` SHOULD be an immutable type.

The Span creation API should provide:
- An API to record a single `Link` where the `Link` properties are passed as
arguments. This MAY be called `AddLink`.
- An API to record a single `Link` whose attributes or attribute values are
lazily constructed, with the intention of avoiding unnecessary work if a link
is unused. If the language supports overloads then this SHOULD be called
`AddLink` otherwise `AddLazyLink` MAY be considered. In some languages, it might
be easier to defer `Link` or attribute creation entirely by providing a wrapping
class or function that returns a `Link` or formatted attributes. When providing
a wrapping class or function it SHOULD be named `LinkFormatter`.

Links SHOULD preserve the order in which they're set.

### Span operations

With the exception of the method to retrieve the `Span`'s `SpanContext` and
recording status, none of the below may be called after the `Span` is finished.

#### Get Context

The Span interface MUST provide:
- An API that returns the `SpanContext` for the given `Span`. The returned value
  may be used even after the `Span` is finished. The returned value MUST be the
  same for the entire Span lifetime. This MAY be called `GetContext`.

#### IsRecording

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
- (Optional) Timestamp for the event.

The `Event` SHOULD be an immutable type.

The Span interface MUST provide:
- An API to record a single `Event` where the `Event` properties are passed as
arguments. This MAY be called `AddEvent`.
- An API to record a single `Event` whose attributes or attribute values are
lazily constructed, with the intention of avoiding unnecessary work if an event
is unused. If the language supports overloads then this SHOULD be called
`AddEvent` otherwise `AddLazyEvent` MAY be considered. In some languages, it
might be easier to defer `Event` or attribute creation entirely by providing a
wrapping class or function that returns an `Event` or formatted attributes. When
providing a wrapping class or function it SHOULD be named `EventFormatter`.

Events SHOULD preserve the order in which they're set. This will typically match
the ordering of the events' timestamps.

Note that the OpenTelemetry project documents certain ["standard event names and
keys"](data-semantic-conventions.md) which have prescribed semantic meanings.

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

It is highly discouraged to update the name of a `Span` after its creation.
`Span` name is often used to group, filter and identify the logical groups of
spans. And often, filtering logic will be implemented before the `Span` creation
for performance reasons. Thus the name update may interfere with this logic.

The method name is called `UpdateName` to differentiate this method from the
regular property setter. It emphasizes that this operation signifies a
major change for a `Span` and may lead to re-calculation of sampling or
filtering decisions made previously depending on the implementation.

Alternatives for the name update may be late `Span` creation, when Span is
started with the explicit timestamp from the past at the moment where the final
`Span` name is known, or reporting a `Span` with the desired name as a child
`Span`.

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

Parameters:
- (Optional) Timestamp to explicitly set the end timestamp

This API MUST be non-blocking.

### Span lifetime

Span lifetime represents the process of recording the start and the end
timestamps to the Span object:

- The start time is recorded when the Span is created.
- The end time needs to be recorded when the operation is ended.

Start and end time as well as Event's timestamps MUST be recorded at a time of a
calling of corresponding API.

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

## SpanKind

Depending on the `Span` position in a `Trace` and application components
boundaries, it can play a different role. This role often defines how `Span`
will be processed and visualized by various backends. So it is important to
record this "hint" whenever possible to the best of the caller's knowledge.

These are the possible SpanKinds:

* `INTERNAL` Default value. Indicates that the span represents an internal
  operation within an application, as opposed to an operations happening at the
  boundaries.
* `SERVER` Indicates that the span covers server-side handling of an RPC or
  other remote request.
* `CLIENT` Indicates that the span describes a request to some remote service.
* `PRODUCER` Indicates that the span describes a producer sending a message to a
  broker. Unlike client and server, there is often no direct critical path
  latency relationship between producer and consumer spans. A `Producer` span ends
  when the message was accepted by the broker while the logical processing of the
  message might span a much longer time.
* `CONSUMER` Indicates that the span describes a consumer receiving a message from
  a broker. As for the `PRODUCER` kind, there is often no direct critical
  path latency relationship between producer and consumer spans.
