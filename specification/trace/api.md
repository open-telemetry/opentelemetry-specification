# Tracing API

**Status**: [Stable, Feature-freeze](../document-status.md)

<details>
<summary>
Table of Contents
</summary>

* [Data types](#data-types)
  * [Time](#time)
    * [Timestamp](#timestamp)
    * [Duration](#duration)
* [TracerProvider](#tracerprovider)
  * [TracerProvider operations](#tracerprovider-operations)
* [Context Interaction](#context-interaction)
* [Tracer](#tracer)
  * [Tracer operations](#tracer-operations)
* [SpanContext](#spancontext)
  * [Retrieving the TraceId and SpanId](#retrieving-the-traceid-and-spanid)
  * [IsValid](#isvalid)
  * [IsRemote](#isremote)
* [Span](#span)
  * [Span creation](#span-creation)
    * [Determining the Parent Span from a Context](#determining-the-parent-span-from-a-context)
    * [Specifying Links](#specifying-links)
  * [Span operations](#span-operations)
    * [Get Context](#get-context)
    * [IsRecording](#isrecording)
    * [Set Attributes](#set-attributes)
    * [Add Events](#add-events)
    * [Set Status](#set-status)
    * [UpdateName](#updatename)
    * [End](#end)
    * [Record Exception](#record-exception)
  * [Span lifetime](#span-lifetime)
  * [Wrapping a SpanContext in a Span](#wrapping-a-spancontext-in-a-span)
* [SpanKind](#spankind)
* [Concurrency](#concurrency)
* [Included Propagators](#included-propagators)

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

The `TracerProvider` MUST provide the following functions:

- Get a `Tracer`

#### Get a Tracer

This API MUST accept the following parameters:

- `name` (required): This name must identify the [instrumentation library](../overview.md#instrumentation-libraries)
  (e.g. `io.opentelemetry.contrib.mongodb`).
  If an application or library has built-in OpenTelemetry instrumentation, both
  [Instrumented library](../glossary.md#instrumented-library) and
  [Instrumentation library](../glossary.md#instrumentation-library) may refer to the same library.
  In that scenario, the `name` denotes a module name or component name within that library
  or application.
  In case an invalid name (null or empty string) is specified, a working
  default Tracer implementation as a fallback is returned rather than returning
  null or throwing an exception.
  A library, implementing the OpenTelemetry API *may* also ignore this name and
  return a default instance for all calls, if it does not support "named"
  functionality (e.g. an implementation which is not even observability-related).
  A TracerProvider could also return a no-op Tracer here if application owners configure
  the SDK to suppress telemetry produced by this library.
- `version` (optional): Specifies the version of the instrumentation library (e.g. `1.0.0`).

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

## Context Interaction

This section defines all operations within the Tracing API that interact with the
[`Context`](../context/context.md).

The API MUST provide the following functionality to interact with a `Context`
instance:

- Extract the `Span` from a `Context` instance
- Insert the `Span` to a `Context` instance

The functionality listed above is necessary because API users SHOULD NOT have
access to the [Context Key](../context/context.md#create-a-key) used by the Tracing API implementation.

If the language has support for implicitly propagated `Context` (see
[here](../context/context.md#optional-global-operations)), the API SHOULD also provide
the following functionality:

- Get the currently active span from the implicit context. This is equivalent to getting the implicit context, then extracting the `Span` from the context.
- Set the currently active span to the implicit context. This is equivalent to getting the implicit context, then inserting the `Span` to the context.

All the above functionalities operate solely on the context API, and they MAY be
exposed as either static methods on the trace module, or as static methods on a class
inside the trace module. This functionality SHOULD be fully implemented in the API when possible.

## Tracer

The tracer is responsible for creating `Span`s.

Note that `Tracers` should usually *not* be responsible for configuration.
This should be the responsibility of the `TracerProvider` instead.

### Tracer operations

The `Tracer` MUST provide functions to:

- [Create a new `Span`](#span-creation) (see the section on `Span`)

## SpanContext

A `SpanContext` represents the portion of a `Span` which must be serialized and
propagated along side of a distributed context. `SpanContext`s are immutable.

The OpenTelemetry `SpanContext` representation conforms to the [W3C TraceContext
specification](https://www.w3.org/TR/trace-context/). It contains two
identifiers - a `TraceId` and a `SpanId` - along with a set of common
`TraceFlags` and system-specific `TraceState` values.

`TraceId` A valid trace identifier is a 16-byte array with at least one
non-zero byte.

`SpanId` A valid span identifier is an 8-byte array with at least one non-zero
byte.

`TraceFlags` contain details about the trace. Unlike TraceState values,
TraceFlags are present in all traces. The current version of the specification
only supports a single flag called [sampled](https://www.w3.org/TR/trace-context/#sampled-flag).

`TraceState` carries vendor-specific trace identification data, represented as a list
of key-value pairs. TraceState allows multiple tracing
systems to participate in the same trace. It is fully described in the [W3C Trace Context
specification](https://www.w3.org/TR/trace-context/#tracestate-header).

The API MUST implement methods to create a `SpanContext`. These methods SHOULD be the only way to
create a `SpanContext`. This functionality MUST be fully implemented in the API, and SHOULD NOT be
overridable.

### Retrieving the TraceId and SpanId

The API MUST allow retrieving the `TraceId` and `SpanId` in the following forms:

* Hex - returns the lowercase [hex encoded](https://tools.ietf.org/html/rfc4648#section-8)
`TraceId` (result MUST be a 32-hex-character lowercase string) or `SpanId`
(result MUST be a 16-hex-character lowercase string).
* Binary - returns the binary representation of the `TraceId` (result MUST be a
16-byte array) or `SpanId` (result MUST be an 8-byte array).

The API SHOULD NOT expose details about how they are internally stored.

### IsValid

An API called `IsValid`, that returns a boolean value, which is `true` if the SpanContext has a
non-zero TraceID and a non-zero SpanID, MUST be provided.

### IsRemote

An API called `IsRemote`, that returns a boolean value, which is `true` if the SpanContext was
propagated from a remote parent, MUST be provided.
When extracting a `SpanContext` through the [Propagators API](../context/api-propagators.md#propagators-api),
`IsRemote` MUST return true, whereas for the SpanContext of any child spans it MUST return false.

### TraceState

`TraceState` is a part of [`SpanContext`](./api.md#spancontext), represented by an immutable list of string key/value pairs and
formally defined by the [W3C Trace Context specification](https://www.w3.org/TR/trace-context/#tracestate-header).
Tracing API MUST provide at least the following operations on `TraceState`:

* Get value for a given key
* Add a new key/value pair
* Update an existing value for a given key
* Delete a key/value pair

These operations MUST follow the rules described in the [W3C Trace Context specification](https://www.w3.org/TR/trace-context/#mutating-the-tracestate-field).
All mutating operations MUST return a new `TraceState` with the modifications applied.
`TraceState` MUST at all times be valid according to rules specified in [W3C Trace Context specification](https://www.w3.org/TR/trace-context/#tracestate-header-field-values).
Every mutating operations MUST validate input parameters.
If invalid value is passed the operation MUST NOT return `TraceState` containing invalid data
and MUST follow the [general error handling guidelines](../error-handling.md).

Please note, since `SpanContext` is immutable, it is not possible to update `SpanContext` with a new `TraceState`.
Such changes then make sense only right before
[`SpanContext` propagation](../context/api-propagators.md)
or [telemetry data exporting](sdk.md#span-exporter).
In both cases, `Propagators` and `SpanExporters` may create a modified `TraceState` copy before serializing it to the wire.

## Span

A `Span` represents a single operation within a trace. Spans can be nested to
form a trace tree. Each trace contains a root span, which typically describes
the entire operation and, optionally, one or more sub-spans for its sub-operations.

<a name="span-data-members"></a>
`Span`s encapsulate:

- The span name
- An immutable [`SpanContext`](#spancontext) that uniquely identifies the
  `Span`
- A parent span in the form of a [`Span`](#span), [`SpanContext`](#spancontext),
  or null
- A [`SpanKind`](#spankind)
- A start timestamp
- An end timestamp
- [`Attributes`](../common/common.md#attributes)
- A list of [`Link`s](#specifying-links) to other `Span`s
- A list of timestamped [`Event`s](#add-events)
- A [`Status`](#set-status).

The _span name_ concisely identifies the work represented by the Span,
for example, an RPC method name, a function name,
or the name of a subtask or stage within a larger computation.
The span name SHOULD be the most general string that identifies a
(statistically) interesting _class of Spans_,
rather than individual Span instances while still being human-readable.
That is, "get_user" is a reasonable name, while "get_user/314159",
where "314159" is a user ID, is not a good name due to its high cardinality.
Generality SHOULD be prioritized over human-readability.

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
change its name, set its `Attribute`s, add `Event`s, and set the `Status`. These
MUST NOT be changed after the `Span`'s end time has been set.

`Span`s are not meant to be used to propagate information within a process. To
prevent misuse, implementations SHOULD NOT provide access to a `Span`'s
attributes besides its `SpanContext`.

Vendors may implement the `Span` interface to effect vendor-specific logic.
However, alternative implementations MUST NOT allow callers to create `Span`s
directly. All `Span`s MUST be created via a `Tracer`.

### Span Creation

There MUST NOT be any API for creating a `Span` other than with a [`Tracer`](#tracer).

In languages with implicit `Context` propagation, `Span` creation MUST NOT
set the newly created `Span` as the active `Span` in the
[current `Context`](#context-interaction) by default, but this functionality
MAY be offered additionally as a separate operation.

The API MUST accept the following parameters:

- The span name. This is a required parameter.
- The parent `Context` or an indication that the new `Span` should be a root `Span`.
  The API MAY also have an option for implicitly using
  the current Context as parent as a default behavior.
  This API MUST NOT accept a `Span` or `SpanContext` as parent, only a full `Context`.

  The semantic parent of the Span MUST be determined according to the rules
  described in [Determining the Parent Span from a Context](#determining-the-parent-span-from-a-context).
- [`SpanKind`](#spankind), default to `SpanKind.Internal` if not specified.
- [`Attributes`](../common/common.md#attributes). Additionally,
  these attributes may be used to make a sampling decision as noted in [sampling
  description](sdk.md#sampling). An empty collection will be assumed if
  not specified.

  Whenever possible, users SHOULD set any already known attributes at span creation
  instead of calling `SetAttribute` later.

- `Link`s - an ordered sequence of Links, see API definition [here](#specifying-links).
- `Start timestamp`, default to current time. This argument SHOULD only be set
  when span creation time has already passed. If API is called at a moment of
  a Span logical start, API user MUST NOT explicitly set this argument.

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

Any span that is created MUST also be ended.
This is the responsibility of the user.
API implementations MAY leak memory or other resources
(including, for example, CPU time for periodic work that iterates all spans)
if the user forgot to end the span.

#### Determining the Parent Span from a Context

When a new `Span` is created from a `Context`, the `Context` may contain a `Span`
representing the currently active instance, and will be used as parent.
If there is no `Span` in the `Context`, the newly created `Span` will be a root span.

A `SpanContext` cannot be set as active in a `Context` directly, but by
[wrapping it into a Span](#wrapping-a-spancontext-in-a-span).
For example, a `Propagator` performing context extraction may need this.

#### Specifying links

During the `Span` creation user MUST have the ability to record links to other
`Span`s. Linked `Span`s can be from the same or a different trace. See [Links
description](../overview.md#links-between-spans). `Link`s cannot be added after
Span creation.

A `Link` is structurally defined by the following properties:

- `SpanContext` of the `Span` to link to.
- Zero or more [`Attributes`](../common/common.md#attributes) further describing
  the link.

The Span creation API MUST provide:

- An API to record a single `Link` where the `Link` properties are passed as
  arguments. This MAY be called `AddLink`. This API takes the `SpanContext` of
  the `Span` to link to and optional `Attributes`, either as individual
  parameters or as an immutable object encapsulating them, whichever is most
  appropriate for the language. Implementations MAY ignore links with an
  [invalid](#isvalid) `SpanContext`.

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

After a `Span` is ended, it usually becomes non-recording and thus
`IsRecording` SHOULD consequently return false for ended Spans.
Note: Streaming implementations, where it is not known if a span is ended,
are one expected case where `IsRecording` cannot change after ending a Span.

`IsRecording` SHOULD NOT take any parameters.

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

A `Span` MUST have the ability to set [`Attributes`](../common/common.md#attributes) associated with it.

The Span interface MUST provide:

- An API to set a single `Attribute` where the attribute properties are passed
  as arguments. This MAY be called `SetAttribute`. To avoid extra allocations some
  implementations may offer a separate API for each of the possible value types.

Setting an attribute with the same key as an existing attribute SHOULD overwrite
the existing attribute's value.

Note that the OpenTelemetry project documents certain ["standard
attributes"](semantic_conventions/README.md) that have prescribed semantic meanings.

Note that [Samplers](sdk.md#sampler) can only consider information already
present during span creation. Any changes done later, including new or changed
attributes, cannot change their decisions.

#### Add Events

A `Span` MUST have the ability to add events. Events have a time associated
with the moment when they are added to the `Span`.

An `Event` is structurally defined by the following properties:

- Name of the event.
- A timestamp for the event. Either the time at which the event was
  added or a custom timestamp provided by the user.
- Zero or more [`Attributes`](../common/common.md#attributes) further describing
  the event.

The Span interface MUST provide:

- An API to record a single `Event` where the `Event` properties are passed as
  arguments. This MAY be called `AddEvent`.
  This API takes the name of the event, optional `Attributes` and an optional
  `Timestamp` which can be used to specify the time at which the event occurred,
  either as individual parameters or as an immutable object encapsulating them,
  whichever is most appropriate for the language. If no custom timestamp is
  provided by the user, the implementation automatically sets the time at which
  this API is called on the event.

Events SHOULD preserve the order in which they are recorded.
This will typically match the ordering of the events' timestamps,
but events may be recorded out-of-order using custom timestamps.

Consumers should be aware that an event's timestamp might be before the start or
after the end of the span if custom timestamps were provided by the user for the
event or when starting or ending the span.
The specification does not require any normalization if provided timestamps are
out of range.

Note that the OpenTelemetry project documents certain ["standard event names and
keys"](semantic_conventions/README.md) which have prescribed semantic meanings.

Note that [`RecordException`](#record-exception) is a specialized variant of
`AddEvent` for recording exception events.

#### Set Status

Sets the `Status` of the `Span`. If used, this will override the default `Span`
status, which is `Unset`.

`Status` is structurally defined by the following properties:

- `StatusCode`, one of the values listed below.
- Optional `Description` that provides a descriptive message of the `Status`.
  `Description` MUST only be used with the `Error` `StatusCode` value.
  An empty `Description` is equivalent with a not present one.

`StatusCode` is one of the following values:

- `Unset`
  - The default status.
- `Ok`
  - The operation has been validated by an Application developer or Operator to
    have completed successfully.
- `Error`
  - The operation contains an error.

The Span interface MUST provide:

- An API to set the `Status`. This SHOULD be called `SetStatus`. This API takes
  the `StatusCode`, and an optional `Description`, either as individual
  parameters or as an immutable object encapsulating them, whichever is most
  appropriate for the language. `Description` MUST be IGNORED for `StatusCode`
  `Ok` & `Unset` values.

The status code SHOULD remain unset, except for the following circumstances:

When the status is set to `ERROR` by Instrumentation Libraries, the status codes
SHOULD be documented and predictable. The status code should only be set to `ERROR`
according to the rules defined within the semantic conventions. For operations
not covered by the semantic conventions, Instrumentation Libraries SHOULD
publish their own conventions, including status codes.

Generally, Instrumentation Libraries SHOULD NOT set the status code to `Ok`,
unless explicitly configured to do so. Instrumention libraries SHOULD leave the
status code as `Unset` unless there is an error, as described above.

Application developers and Operators may set the status code to `Ok`.

Analysis tools SHOULD respond to an `Ok` status by suppressing any errors they
would otherwise generate. For example, to suppress noisy errors such as 404s.

Only the value of the last call will be recorded, and implementations are free
to ignore previous calls.

#### UpdateName

Updates the `Span` name. Upon this update, any sampling behavior based on `Span`
name will depend on the implementation.

Note that [Samplers](sdk.md#sampler) can only consider information already
present during span creation. Any changes done later, including updated span
name, cannot change their decisions.

Alternatives for the name update may be late `Span` creation, when Span is
started with the explicit timestamp from the past at the moment where the final
`Span` name is known, or reporting a `Span` with the desired name as a child
`Span`.

Required parameters:

- The new **span name**, which supersedes whatever was passed in when the
  `Span` was started

#### End

Signals that the operation described by this span has
now (or at the time optionally specified) ended.

Implementations SHOULD ignore all subsequent calls to `End` and any other Span methods,
i.e. the Span becomes non-recording by being ended
(there might be exceptions when Tracer is streaming events
and has no mutable state associated with the `Span`).

Language SIGs MAY provide methods other than `End` in the API that also end the
span to support language-specific features like `with` statements in Python.
However, all API implementations of such methods MUST internally call the `End`
method and be documented to do so.

`End` MUST NOT have any effects on child spans.
Those may still be running and can be ended later.

`End` MUST NOT inactivate the `Span` in any `Context` it is active in.
It MUST still be possible to use an ended span as parent via a Context it is
contained in. Also, any mechanisms for putting the Span into a Context MUST
still work after the Span was ended.

Parameters:

- (Optional) Timestamp to explicitly set the end timestamp.
  If omitted, this MUST be treated equivalent to passing the current time.

This API MUST be non-blocking.

#### Record Exception

To facilitate recording an exception languages SHOULD provide a
`RecordException` method if the language uses exceptions.
This is a specialized variant of [`AddEvent`](#add-events),
so for anything not specified here, the same requirements as for `AddEvent` apply.

The signature of the method is to be determined by each language
and can be overloaded as appropriate.
The method MUST record an exception as an `Event` with the conventions outlined in
the [exception semantic conventions](semantic_conventions/exceptions.md) document.
The minimum required argument SHOULD be no more than only an exception object.

If `RecordException` is provided, the method MUST accept an optional parameter
to provide any additional event attributes
(this SHOULD be done in the same way as for the `AddEvent` method).
If attributes with the same name would be generated by the method already,
the additional attributes take precedence.

Note: `RecordException` may be seen as a variant of `AddEvent` with
additional exception-specific parameters and all other parameters being optional
(because they have defaults from the exception semantic convention).

### Span lifetime

Span lifetime represents the process of recording the start and the end
timestamps to the Span object:

- The start time is recorded when the Span is created.
- The end time needs to be recorded when the operation is ended.

Start and end time as well as Event's timestamps MUST be recorded at a time of a
calling of corresponding API.

### Wrapping a SpanContext in a Span

The API MUST provide an operation for wrapping a `SpanContext` with an object
implementing the `Span` interface. This is done in order to expose a `SpanContext`
as a `Span` in operations such as in-process `Span` propagation.

If a new type is required for supporting this operation, it SHOULD NOT be exposed
publicly if possible (e.g. by only exposing a function that returns something
with the Span interface type). If a new type is required to be publicly exposed,
it SHOULD be named `NonRecordingSpan`.

The behavior is defined as follows:

- `GetContext()` MUST return the wrapped `SpanContext`.
- `IsRecording` MUST return `false` to signal that events, attributes and other elements
  are not being recorded, i.e. they are being dropped.

The remaining functionality of `Span` MUST be defined as no-op operations.
Note: This includes `End`, so as an exception from the general rule,
it is not required (or even helpful) to end such a Span.

This functionality MUST be fully implemented in the API, and SHOULD NOT be overridable.

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

In order for `SpanKind` to be meaningful, callers SHOULD arrange that
a single Span does not serve more than one purpose.  For example, a
server-side span SHOULD NOT be used directly as the parent of another
remote span.  As a simple guideline, instrumentation should create a
new Span prior to extracting and serializing the SpanContext for a
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

## Concurrency

For languages which support concurrent execution the Tracing APIs provide
specific guarantees and safeties. Not all of API functions are safe to
be called concurrently.

**TracerProvider** - all methods are safe to be called concurrently.

**Tracer** - all methods are safe to be called concurrently.

**Span** - All methods of Span are safe to be called concurrently.

**Event** - Events are immutable and safe to be used concurrently.

**Link** - Links are immutable and safe to be used concurrently.

## Included Propagators

The API layer or an extension package MUST include the following `Propagator`s:

* A `TextMapPropagator` implementing the [W3C TraceContext Specification](https://www.w3.org/TR/trace-context/).

See [Propagators Distribution](../context/api-propagators.md#propagators-distribution)
for how propagators are to be distributed.

## Behavior of the API in the absence of an installed SDK

In general, in the absence of an installed SDK, the Trace API is a "no-op" API.
This means that operations on a Tracer, or on Spans, should have no side effects and do nothing. However, there
is one important exception to this general rule, and that is related to propagation of a `SpanContext`:
The API MUST create a [non-recording Span](#wrapping-a-spancontext-in-a-span) with the `SpanContext`
that is in the `Span` in the parent `Context` (whether explicitly given or implicit current) or,
if the parent is a non-recording Span (which it usually always is if no SDK is present),
it MAY return the parent Span back from the creation method.
If the parent `Context` contains no `Span`, an empty non-recording Span MUST be returned instead
(i.e., having a `SpanContext` with all-zero Span and Trace IDs, empty Tracestate, and unsampled TraceFlags).
This means that a `SpanContext` that has been provided by a configured `Propagator`
will be propagated through to any child span and ultimately also `Inject`,
but that no new `SpanContext`s will be created.
