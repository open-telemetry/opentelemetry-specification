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
* [SpanContext](#spancontext)
* [Span](#span)
  * [Span creation](#span-creation)
    * [Determining the Parent Span from a Context](#determining-the-parent-span-from-a-context)
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

The Tracing API consist of these main classes:

- [`TracerProvider`](#tracerprovider) is the entry point of the API.
  It provides access to `Tracer`s.
- [`Tracer`](#tracer) is the class responsible for creating `Span`s.
- [`Span`](#span) is the API to trace an operation.

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

## TracerProvider

`Tracer`s can be accessed with a `TracerProvider`.

In implementations of the API, the `TracerProvider` is expected to be the
stateful object that holds any configuration.

Normally, the `TracerProvider` is expected to be accessed from a central place.
Thus, the API SHOULD provide a way to set/register and access
a global default `TracerProvider`.

Notwithstanding any global `TracerProvider`, some applications may want to or
have to use multiple `TracerProvider` instances,
e.g. to have different configuration (like `SpanProcessor`s) for each
(and consequently for the `Tracer`s obtained from them),
or because its easier with dependency injection frameworks.
Thus, implementations of `TracerProvider` SHOULD allow creating an arbitrary
number of `TracerProvider` instances.

### TracerProvider operations

The `TracerProvider` MUST provide functions to:

- Get a `Tracer`

That API MUST accept the following parameters:

- `name` (required): This name must identify the [instrumentation library](../overview.md#instrumentation-libraries)
  (e.g. `io.opentelemetry.contrib.mongodb`) and *not* the instrumented library.
  In case an invalid name (null or empty string) is specified, a working
  default Tracer implementation as a fallback is returned rather than returning
  null or throwing an exception.
  A library, implementing the OpenTelemetry API *may* also ignore this name and
  return a default instance for all calls, if it does not support "named"
  functionality (e.g. an implementation which is not even observability-related).
  A TracerProvider could also return a no-op Tracer here if application owners configure
  the SDK to suppress telemetry produced by this library.
- `version` (optional): Specifies the [version](../resource/semantic_conventions#version-attributes) of the instrumentation library
  (e.g. `semver:1.0.0`).

It is unspecified whether or under which conditions the same or different
`Tracer` instances are returned from this functions.

Implementations MUST NOT require users to repeatedly obtain a `Tracer` again
with the same name+version to pick up configuration changes.
This can be achieved either by allowing to work with an outdated configuration or
by ensuring that new configuration applies also to previously returned `Tracer`s.

Note: This could, for example, be implemented by storing any mutable
configuration in the `TracerProvider` and having `Tracer` implementation objects
have a reference to the `TracerProvider` from which they were obtained.
If configuration must be stored per-tracer (such as disabling a certain tracer),
the tracer could, for example, do a look-up with its name+version in a map in
the `TracerProvider`, or the `TracerProvider` could maintain a registry of all
returned `Tracer`s and actively update their configuration if it changes.

## Tracer

The tracer is responsible for creating `Span`s.

Note that `Tracers` should usually *not* be responsible for configuration.
This should be the responsibility of the `TracerProvider` instead.

### Tracer operations

The `Tracer` MUST provide functions to:

- [Create a new `Span`](#span-creation) (see the section on `Span`)

The `Tracer` SHOULD provide methods to:

- Get the currently active `Span`
- Mark a given `Span` as active

The `Tracer` MUST delegate to the [`Context`](../context/context.md) to perform
these tasks, i.e. the above methods MUST do the same as a single equivalent
method of the Context management system.
In particular, this implies that the active span MUST not depend on the `Tracer`
that it is queried from/was set to, as long as the tracers were obtained from
the same `TracerProvider`.

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
When creating children from remote spans, their IsRemote flag MUST be set to false.

Please review the W3C specification for details on the [Tracestate
field](https://www.w3.org/TR/trace-context/#tracestate-field).

## Span

A `Span` represents a single operation within a trace. Spans can be nested to
form a trace tree. Each trace contains a root span, which typically describes
the entire operation and, optionally, one or more sub-spans for its sub-operations.

`Span`s encapsulate:

- The span name
- An immutable [`SpanContext`](#spancontext) that uniquely identifies the
  `Span`
- A parent span in the form of a [`Span`](#span), [`SpanContext`](#spancontext),
  or null
- A [`SpanKind`](#spankind)
- A start timestamp
- An end timestamp
- [`Attribute`s](#set-attributes), a collection of key-value pairs
- A list of [`Link`s](#add-links) to other `Span`s
- A list of timestamped [`Event`s](#add-events)
- A [`Status`](#set-status).

The _span name_ is a human-readable string which concisely identifies the work
represented by the Span, for example, an RPC method name, a function name,
or the name of a subtask or stage within a larger computation. The span name
should be the most general string that identifies a (statistically) interesting
_class of Spans_, rather than individual Span instances. That is, "get_user" is
a reasonable name, while "get_user/314159", where "314159" is a user ID, is not
a good name due to its high cardinality.

For example, here are potential span names for an endpoint that gets a
hypothetical account information:

| Span Name         | Guidance     |
| ----------------- | ------------ |
| `get`             | Too general  |
| `get_account/42`  | Too specific |
| `get_account`     | Good, and account_id=42 would make a nice Span attribute |
| `get_account/{accountId}` | Also good (using the "HTTP route") |

The `Span`'s start and end timestamps reflect the elapsed real time of the
operation.

For example, if a span represents a request-response cycle (e.g. HTTP or an RPC),
the span should have a start time that corresponds to the start time of the
first sub-operation, and an end time of when the final sub-operation is complete.
This includes:

- receiving the data from the request
- parsing of the data (e.g. from a binary or json format)
- any middleware or additional processing logic
- business logic
- construction of the response
- sending of the response

Child spans (or in some cases events) may be created to represent
sub-operations which require more detailed observability. Child spans should
measure the timing of the respective sub-operation, and may add additional
attributes.

A `Span`'s start time SHOULD be set to the current time on [span
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

There MUST NOT be any API for creating a `Span` other than with a [`Tracer`](#tracer).

When creating a new `Span`, the `Tracer` MUST allow the caller to specify the
new `Span`'s parent in the form of a `Span` or `SpanContext`. The `Tracer`
SHOULD create each new `Span` as a child of its active `Span`, unless an
explicit parent is provided or the option to create a span without a parent is
selected.

`Span` creation MUST NOT set the newly created `Span` as the currently
active `Span` by default, but this functionality MAY be offered additionally
as a separate operation.

The API MUST accept the following parameters:

- The span name. This is a required parameter.
- The parent `Span` or a `Context` containing a parent `Span` or `SpanContext`,
  and whether the new `Span` should be a root `Span`. API MAY also have an
  option for implicit parenting from the current context as a default behavior.
  See [Determining the Parent Span from a Context](#determining-the-parent-span-from-a-context)
  for guidance on `Span` parenting from explicit and implicit `Context`s.
- [`SpanKind`](#spankind), default to `SpanKind.Internal` if not specified.
- `Attribute`s - A collection of key-value pairs, with the same semantics as
  the ones settable with [Span::SetAttributes](#set-attributes). Additionally,
  these attributes may be used to make a sampling decision as noted in [sampling
  description](sdk.md#sampling). An empty collection will be assumed if
  not specified.

  Whenever possible, users SHOULD set any already known attributes at span creation
  instead of calling `SetAttribute` later.

- `Link`s - see API definition [here](#add-links). Empty list will be assumed if
  not specified.
- `Start timestamp`, default to current time. This argument SHOULD only be set
  when span creation time has already passed. If API is called at a moment of
  a Span logical start, API user MUST not explicitly set this argument.

Each span has zero or one parent span and zero or more child spans, which
represent causally related operations. A tree of related spans comprises a
trace. A span is said to be a _root span_ if it does not have a parent. Each
trace includes a single root span, which is the shared ancestor of all other
spans in the trace. Implementations MUST provide an option to create a `Span` as
a root span, and MUST generate a new `TraceId` for each root span created.
For a Span with a parent, the `TraceId` MUST be the same as the parent.
Also, the child span MUST inherit all `TraceState` values of its parent by default.

A `Span` is said to have a _remote parent_ if it is the child of a `Span`
created in another process. Each propagators' deserialization must set
`IsRemote` to true on a parent `SpanContext` so `Span` creation knows if the
parent is remote.

#### Determining the Parent Span from a Context

When a new `Span` is created from a `Context`, the `Context` may contain:

- A current `Span`
- An extracted `SpanContext`
- A current `Span` and an extracted `SpanContext`
- Neither a current `Span` nor an extracted `Span` context

The parent should be selected in the following order of precedence:

- Use the current `Span`, if available.
- Use the extracted `SpanContext`, if available.
- There is no parent. Create a root `Span`.

#### Add Links

During the `Span` creation user MUST have the ability to record links to other `Span`s. Linked
`Span`s can be from the same or a different trace. See [Links
description](../overview.md#links-between-spans).

A `Link` is defined by the following properties:

- (Required) `SpanContext` of the `Span` to link to.
- (Optional) One or more `Attribute`s with the same restrictions as defined for
  [Span Attributes](#set-attributes).

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

With the exception of the function to retrieve the `Span`'s `SpanContext` and
recording status, none of the below may be called after the `Span` is finished.

#### Get Context

The Span interface MUST provide:

- An API that returns the `SpanContext` for the given `Span`. The returned value
  may be used even after the `Span` is finished. The returned value MUST be the
  same for the entire Span lifetime. This MAY be called `GetContext`.

#### IsRecording

Returns true if this `Span` is recording information like events with the
`AddEvent` operation, attributes using `SetAttributes`, status with `SetStatus`,
etc.

There should be no parameter.

This flag SHOULD be used to avoid expensive computations of a Span attributes or
events in case when a Span is definitely not recorded. Note that any child
span's recording is determined independently from the value of this flag
(typically based on the `sampled` flag of a `TraceFlag` on
[SpanContext](#spancontext)).

This flag may be `true` despite the entire trace being sampled out. This
allows to record and process information about the individual Span without
sending it to the backend. An example of this scenario may be recording and
processing of all incoming requests for the processing and building of
SLA/SLO latency charts while sending only a subset - sampled spans - to the
backend. See also the [sampling section of SDK design](sdk.md#sampling).

Users of the API should only access the `IsRecording` property when
instrumenting code and never access `SampledFlag` unless used in context
propagators.

#### Set Attributes

A `Span` MUST have the ability to set attributes associated with it.

An `Attribute` is defined by the following properties:

- (Required) The attribute key, which MUST be a non-`null` and non-empty string.
- (Required) The attribute value, which is either:
  - A primitive type: string, boolean or numeric.
  - An array of primitive type values. The array MUST be homogeneous,
    i.e. it MUST NOT contain values of different types.

The Span interface MUST provide:

- An API to set a single `Attribute` where the attribute properties are passed
  as arguments. This MAY be called `SetAttribute`. To avoid extra allocations some
  implementations may offer a separate API for each of the possible value types.

Attributes SHOULD preserve the order in which they're set. Setting an attribute
with the same key as an existing attribute SHOULD overwrite the existing
attribute's value.

Attribute values expressing a numerical value of zero or an empty string are
considered meaningful and MUST be stored and passed on to span processors / exporters.
Attribute values of `null` are considered to be not set and get discarded as if
that `SetAttribute` call had never been made.
As an exception to this, if overwriting of values is supported, this results in
clearing the previous value and dropping the attribute key from the set of attributes.

`null` values within arrays MUST be preserved as-is (i.e., passed on to span
processors / exporters as `null`). If exporters do not support exporting `null`
values, they MAY replace those values by 0, `false`, or empty strings.
This is required for map/dictionary structures represented as two arrays with
indices that are kept in sync (e.g., two attributes `header_keys` and `header_values`,
both containing an array of strings to represent a mapping
`header_keys[i] -> header_values[i]`).

Note that the OpenTelemetry project documents certain ["standard
attributes"](semantic_conventions/README.md) that have prescribed semantic meanings.

#### Add Events

A `Span` MUST have the ability to add events. Events have a time associated
with the moment when they are added to the `Span`.

An `Event` is defined by the following properties:

- (Required) Name of the event.
- (Optional) One or more `Attribute`s with the same restrictions as defined for
  [Span Attributes](#set-attributes).
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
keys"](semantic_conventions/README.md) which have prescribed semantic meanings.

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

The function name is called `UpdateName` to differentiate this function from the
regular property setter. It emphasizes that this operation signifies a major
change for a `Span` and may lead to re-calculation of sampling or filtering
decisions made previously depending on the implementation.

Alternatives for the name update may be late `Span` creation, when Span is
started with the explicit timestamp from the past at the moment where the final
`Span` name is known, or reporting a `Span` with the desired name as a child
`Span`.

Required parameters:

- The new **span name**, which supersedes whatever was passed in when the
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
- `Unknown`
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
- `Internal`
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
Languages should follow their usual conventions on whether to return `null` or an empty string here if no description was given.

### GetIsOk

Returns true if the canonical code of this `Status` is `Ok`, otherwise false.

## SpanKind

`SpanKind` describes the relationship between the Span, its parents,
and its children in a Trace.  `SpanKind` describes two independent
properties that benefit tracing systems during analysis.

The first property described by `SpanKind` reflects whether the Span
is a remote child or parent.  Spans with a remote parent are
interesting because they are sources of external load.  Spans with a
remote child are interesting because they reflect a non-local system
dependency.

The second property described by `SpanKind` reflects whether a child
Span represents a synchronous call.  When a child span is synchronous,
the parent is expected to wait for it to complete under ordinary
circumstances.  It can be useful for tracing systems to know this
property, since synchronous Spans may contribute to the overall trace
latency. Asynchronous scenarios can be remote or local.

In order for `SpanKind` to be meaningful, callers should arrange that
a single Span does not serve more than one purpose.  For example, a
server-side span should not be used directly as the parent of another
remote span.  As a simple guideline, instrumentation should create a
new Span prior to extracting and serializing the span context for a
remote call.

These are the possible SpanKinds:

* `SERVER` Indicates that the span covers server-side handling of a
  synchronous RPC or other remote request.  This span is the child of
  a remote `CLIENT` span that was expected to wait for a response.
* `CLIENT` Indicates that the span describes a synchronous request to
  some remote service.  This span is the parent of a remote `SERVER`
  span and waits for its response.
* `PRODUCER` Indicates that the span describes the parent of an
  asynchronous request.  This parent span is expected to end before
  the corresponding child `CONSUMER` span, possibly even before the
  child span starts. In messaging scenarios with batching, tracing
  individual messages requires a new `PRODUCER` span per message to
  be created.
* `CONSUMER` Indicates that the span describes the child of an
  asynchronous `PRODUCER` request.
* `INTERNAL` Default value. Indicates that the span represents an
  internal operation within an application, as opposed to an
  operations with remote parents or children.

To summarize the interpretation of these kinds:

| `SpanKind` | Synchronous | Asynchronous | Remote Incoming | Remote Outgoing |
|--|--|--|--|--|
| `CLIENT` | yes | | | yes |
| `SERVER` | yes | | yes | |
| `PRODUCER` | | yes | | maybe |
| `CONSUMER` | | yes | maybe | |
| `INTERNAL` | | | | |
