<!--- Hugo front matter used to generate the website version of this page:
linkTitle: API
weight: 1
--->

# Tracing API

**Status**: [Stable](../document-status.md), except where otherwise specified

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [Data types](#data-types)
  * [Time](#time)
    + [Timestamp](#timestamp)
    + [Duration](#duration)
- [TracerProvider](#tracerprovider)
  * [TracerProvider operations](#tracerprovider-operations)
    + [Get a Tracer](#get-a-tracer)
- [Context Interaction](#context-interaction)
- [Tracer](#tracer)
  * [Tracer operations](#tracer-operations)
    + [Enabled](#enabled)
- [SpanContext](#spancontext)
  * [Retrieving the TraceId and SpanId](#retrieving-the-traceid-and-spanid)
  * [IsValid](#isvalid)
  * [IsRemote](#isremote)
  * [TraceState](#tracestate)
- [Span](#span)
  * [Span Creation](#span-creation)
    + [Determining the Parent Span from a Context](#determining-the-parent-span-from-a-context)
    + [Specifying links](#specifying-links)
  * [Span operations](#span-operations)
    + [Get Context](#get-context)
    + [IsRecording](#isrecording)
    + [Set Attributes](#set-attributes)
    + [Add Events](#add-events)
    + [Add Link](#add-link)
    + [Set Status](#set-status)
    + [UpdateName](#updatename)
    + [End](#end)
    + [Record Exception](#record-exception)
  * [Span lifetime](#span-lifetime)
  * [Wrapping a SpanContext in a Span](#wrapping-a-spancontext-in-a-span)
- [SpanKind](#spankind)
- [Link](#link)
- [Concurrency requirements](#concurrency-requirements)
- [Included Propagators](#included-propagators)
- [Behavior of the API in the absence of an installed SDK](#behavior-of-the-api-in-the-absence-of-an-installed-sdk)

<!-- tocstop -->

</details>

The Tracing API consists of these main components:

- [`TracerProvider`](#tracerprovider) is the entry point of the API.
  It provides access to `Tracer`s.
- [`Tracer`](#tracer) is responsible for creating `Span`s.
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
or because it's easier with dependency injection frameworks.
Thus, implementations of `TracerProvider` SHOULD allow creating an arbitrary
number of `TracerProvider` instances.

### TracerProvider operations

The `TracerProvider` MUST provide the following functions:

- Get a `Tracer`

#### Get a Tracer

This API MUST accept the following parameters:

- `name` (required): This name SHOULD uniquely identify the
  [instrumentation scope](../common/instrumentation-scope.md), such as the
  [instrumentation library](../glossary.md#instrumentation-library) (e.g.
  `io.opentelemetry.contrib.mongodb`), package, module or class name. If an
  application or library has built-in OpenTelemetry instrumentation, both
  [Instrumented library](../glossary.md#instrumented-library) and
  [Instrumentation library](../glossary.md#instrumentation-library) may refer to
  the same library. In that scenario, the `name` denotes a module name or
  component name within that library or application. In case an invalid name
  (null or empty string) is specified, a working Tracer implementation MUST be
  returned as a fallback rather than returning null or throwing an exception,
  its `name` property SHOULD be set to an **empty** string, and a message
  reporting that the specified value is invalid SHOULD be logged. A library,
  implementing the OpenTelemetry API *may* also ignore this name and return a
  default instance for all calls, if it does not support "named" functionality
  (e.g. an implementation which is not even observability-related). A
  TracerProvider could also return a no-op Tracer here if application owners
  configure the SDK to suppress telemetry produced by this library.
- `version` (optional): Specifies the version of the instrumentation scope if the scope
  has a version (e.g. a library version). Example value: `1.0.0`.
- [since 1.4.0] `schema_url` (optional): Specifies the Schema URL that should be
  recorded in the emitted telemetry.
- [since 1.13.0] `attributes` (optional): Specifies the instrumentation scope attributes
  to associate with emitted telemetry.

The term *identical* applied to Tracers describes instances where all parameters
are equal. The term *distinct* applied to Tracers describes instances where at
least one parameter has a different value.

Implementations MUST NOT require users to repeatedly obtain a `Tracer` again
with the same identity to pick up configuration changes. This can be
achieved either by allowing to work with an outdated configuration or by
ensuring that new configuration applies also to previously returned `Tracer`s.

Note: This could, for example, be implemented by storing any mutable
configuration in the `TracerProvider` and having `Tracer` implementation objects
have a reference to the `TracerProvider` from which they were obtained. If
configuration must be stored per-tracer (such as disabling a certain tracer),
the tracer could, for example, do a look-up with its identity in a map
in the `TracerProvider`, or the `TracerProvider` could maintain a registry of
all returned `Tracer`s and actively update their configuration if it changes.

## Context Interaction

This section defines all operations within the Tracing API that interact with the
[`Context`](../context/README.md).

The API MUST provide the following functionality to interact with a `Context`
instance:

- Extract the `Span` from a `Context` instance
- Combine the `Span` with a `Context` instance, creating a new `Context` instance

The functionality listed above is necessary because API users SHOULD NOT have
access to the [Context Key](../context/README.md#create-a-key) used by the Tracing API implementation.

If the language has support for implicitly propagated `Context` (see
[here](../context/README.md#optional-global-operations)), the API SHOULD also provide
the following functionality:

- Get the currently active span from the implicit context. This is equivalent to getting the implicit context, then extracting the `Span` from the context.
- Set the currently active span into a new context, and make that the implicit context. This is equivalent to combining the current implicit context's values with the `Span` to create a new context, which is then made the current implicit context.

All the above functionalities operate solely on the context API, and they MAY be
exposed as either static methods on the trace module, or as static methods on a class
inside the trace module. This functionality SHOULD be fully implemented in the API when possible.

## Tracer

The tracer is responsible for creating `Span`s.

Note that `Tracer`s should usually *not* be responsible for configuration.
This should be the responsibility of the `TracerProvider` instead.

### Tracer operations

The `Tracer` MUST provide functions to:

- [Create a new `Span`](#span-creation) (see the section on `Span`)

The `Tracer` SHOULD provide functions to:

- [Report if `Tracer` is `Enabled`](#enabled)

#### Enabled

**Status**: [Development](../document-status.md)

To help users avoid performing computationally expensive operations when
creating `Span`s, a `Tracer` SHOULD provide this `Enabled` API.

There are currently no required parameters for this API. Parameters can be
added in the future, therefore, the API MUST be structured in a way for
parameters to be added.

This API MUST return a language idiomatic boolean type. A returned value of
`true` means the `Tracer` is enabled for the provided arguments, and a returned
value of `false` means the `Tracer` is disabled for the provided arguments.

The returned value is not always static, it can change over time. The API
SHOULD be documented that instrumentation authors needs to call this API each
time they [create a new `Span`](#span-creation) to ensure they have the most
up-to-date response.

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

`TraceFlags` contain details about the trace.
Unlike TraceState values, TraceFlags are present in all traces.
The current version of the specification supports two flags:

- [Sampled](https://www.w3.org/TR/trace-context-2/#sampled-flag)
- [Random](https://www.w3.org/TR/trace-context-2/#random-trace-id-flag)

`TraceState` carries tracing-system-specific trace identification data, represented as a list of key-value pairs.
TraceState allows multiple tracing systems to participate in the same trace.
It is fully described in the [W3C Trace Context specification](https://www.w3.org/TR/trace-context-2/#tracestate-header).
For specific OpenTelemetry values in `TraceState`, see the [TraceState Handling](tracestate-handling.md) document.

`IsRemote`, a boolean indicating whether the SpanContext was received from somewhere
else or locally generated, see [IsRemote](#isremote).

The API MUST implement methods to create a `SpanContext`. These methods SHOULD be the only way to
create a `SpanContext`. This functionality MUST be fully implemented in the API, and SHOULD NOT be
overridable.

### Retrieving the TraceId and SpanId

The API MUST allow retrieving the `TraceId` and `SpanId` in the following forms:

* Hex - returns the lowercase [hex encoded](https://datatracker.ietf.org/doc/html/rfc4648#section-8)
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
When extracting a `SpanContext` through the [Propagators API](../context/api-propagators.md),
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
In both cases, `Propagator`s and `SpanExporter`s may create a modified `TraceState` copy before serializing it to the wire.

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
- [`Attributes`](../common/README.md#attribute)
- A list of [`Link`s](#link) to other `Span`s
- A list of timestamped [`Event`s](#add-events)
- A [`Status`](#set-status).

The *span name* concisely identifies the work represented by the Span,
for example, an RPC method name, a function name,
or the name of a subtask or stage within a larger computation.
The span name SHOULD be the most general string that identifies a
(statistically) interesting *class of Spans*,
rather than individual Span instances while still being human-readable.
That is, "get_user" is a reasonable name, while "get_user/314159",
where "314159" is a user ID, is not a good name due to its high cardinality.
Generality SHOULD be prioritized over human-readability.

For example, here are potential span names for an endpoint that gets a
hypothetical account information:

| Span Name | Guidance |
| --------- | -------- |
| `get` | Too general |
| `get_account/42` | Too specific |
| `get_account` | Good, and account_id=42 would make a nice Span attribute |
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
- [`Attributes`](../common/README.md#attribute). Additionally,
  these attributes may be used to make a sampling decision as noted in [sampling
  description](sdk.md#sampling). An empty collection will be assumed if
  not specified.

  The API documentation MUST state that adding attributes at span creation is preferred
  to calling `SetAttribute` later, as samplers can only consider information
  already present during span creation.

- `Link`s - an ordered sequence of Links, see [API definition](#link).
- `Start timestamp`, default to current time. This argument SHOULD only be set
  when span creation time has already passed. If API is called at a moment of
  a Span logical start, API user MUST NOT explicitly set this argument.

Each span has zero or one parent span and zero or more child spans, which
represent causally related operations. A tree of related spans comprises a
trace. A span is said to be a *root span* if it does not have a parent. Each
trace includes a single root span, which is the shared ancestor of all other
spans in the trace. Implementations MUST provide an option to create a `Span` as
a root span, and MUST generate a new `TraceId` for each root span created.
For a Span with a parent, the `TraceId` MUST be the same as the parent.
Also, the child span MUST inherit all `TraceState` values of its parent by default.

A `Span` is said to have a *remote parent* if it is the child of a `Span`
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

During `Span` creation, a user MUST have the ability to record links to other `Span`s.
Linked `Span`s can be from the same or a different trace -- see [links](#link).
`Link`s added at `Span` creation may be considered by [Samplers](sdk.md#sampler)
to make a sampling decision.

### Span operations

With the exception of the function to retrieve the `Span`'s `SpanContext` and
`IsRecording`, none of the below may be called after the `Span` is
finished.

#### Get Context

The Span interface MUST provide:

- An API that returns the `SpanContext` for the given `Span`. The returned value
  may be used even after the `Span` is finished. The returned value MUST be the
  same for the entire Span lifetime. This MAY be called `GetContext`.

#### IsRecording

A `Span` is recording (`IsRecording` returns `true`) when the data provided to
it via functions like `SetAttributes`, `AddEvent`, `SetStatus` is captured in
some form (e.g. in memory). When a `Span` is not recording (`IsRecording` returns
`false`), all this data is discarded right away. Further attempts to set or add
data will not record, making the span effectively a no-op.

This flag may be `true` despite the entire trace not being sampled. This
allows information about the individual Span to be recorded and processed without
sending it to the backend. An example of this scenario may be recording and
processing of all incoming requests for the processing and building of
SLA/SLO latency charts while sending only a subset - sampled spans - to the
backend. See also the [sampling section of SDK design](sdk.md#sampling).

After a `Span` is ended, it SHOULD become non-recording and `IsRecording`
SHOULD always return `false`. The one known exception to this is
streaming implementations of the API that do not keep local state and cannot
change the value of `IsRecording` after ending the span.

`IsRecording` SHOULD NOT take any parameters.

This flag SHOULD be used to avoid expensive computations of a Span attributes or
events in case when a Span is definitely not recorded. Note that any child
span's recording is determined independently from the value of this flag
(typically based on the `sampled` flag of a `TraceFlags` on
[SpanContext](#spancontext)).

Users of the API should only access the `IsRecording` property when
instrumenting code and never access `SampledFlag` unless used in context
propagators.

#### Set Attributes

A `Span` MUST have the ability to set [`Attributes`](../common/README.md#attribute) associated with it.

The Span interface MUST provide:

- An API to set a single `Attribute` where the attribute properties are passed
  as arguments. This MAY be called `SetAttribute`. To avoid extra allocations some
  implementations may offer a separate API for each of the possible value types.

The Span interface MAY provide:

- An API to set multiple `Attributes` at once, where the `Attributes` are passed in a
  single method call.

Setting an attribute with the same key as an existing attribute SHOULD overwrite
the existing attribute's value.

Note that the OpenTelemetry project documents certain ["standard
attributes"](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/README.md) that have prescribed semantic meanings.

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
- Zero or more [`Attributes`](../common/README.md#attribute) further describing
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
keys"](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/README.md) which have prescribed semantic meanings.

Note that [`RecordException`](#record-exception) is a specialized variant of
`AddEvent` for recording exception events.

#### Add Link

A `Span` MUST have the ability to add `Link`s associated with it after its creation - see [Links](#link).
`Link`s added after `Span` creation may not be considered by [Samplers](sdk.md#sampler).

#### Set Status

Sets the `Status` of the `Span`. If used, this will override the default `Span`
status, which is `Unset`.

`Status` is structurally defined by the following properties:

- `StatusCode`, one of the values listed below.
- Optional `Description` that provides a descriptive message of the `Status`.
  `Description` MUST only be used with the `Error` `StatusCode` value.
  An empty `Description` is equivalent with a not present one.

Note: The [OTLP protocol definition](https://github.com/open-telemetry/opentelemetry-proto/blob/724e427879e3d2bae2edc0218fff06e37b9eb46e/opentelemetry/proto/trace/v1/trace.proto#L264)
refers to the `Description` property as `message`.

`StatusCode` is one of the following values:

- `Unset`
  - The default status.
- `Ok`
  - The operation has been validated by an Application developer or Operator to
    have completed successfully.
- `Error`
  - The operation contains an error.

These values form a total order: `Ok > Error > Unset`.
This means that setting `Status` with `StatusCode=Ok` will override any prior or future attempts to set
span `Status` with `StatusCode=Error` or `StatusCode=Unset`. See below for more specific rules.

The Span interface MUST provide:

- An API to set the `Status`. This SHOULD be called `SetStatus`. This API takes
  the `StatusCode`, and an optional `Description`, either as individual
  parameters or as an immutable object encapsulating them, whichever is most
  appropriate for the language. `Description` MUST be IGNORED for `StatusCode`
  `Ok` & `Unset` values.

The status code SHOULD remain unset, except for the following circumstances:

An attempt to set value `Unset` SHOULD be ignored.

When the status is set to `Error` by Instrumentation Libraries, the `Description`
SHOULD be documented and predictable. The status code should only be set to `Error`
according to the rules defined within the semantic conventions. For operations
not covered by the semantic conventions, Instrumentation Libraries SHOULD
publish their own conventions, including possible values of `Description`
and what they mean.

Generally, Instrumentation Libraries SHOULD NOT set the status code to `Ok`,
unless explicitly configured to do so. Instrumentation Libraries SHOULD leave the
status code as `Unset` unless there is an error, as described above.

Application developers and Operators may set the status code to `Ok`.

When span status is set to `Ok` it SHOULD be considered final and any further
attempts to change it SHOULD be ignored.

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

Expect this operation to be called in the "hot path" of production
applications. It needs to be designed to complete fast, if not immediately.
This operation itself MUST NOT perform blocking I/O on the calling thread.
Any locking used needs be minimized and SHOULD be removed entirely if
possible. Some downstream SpanProcessors and subsequent SpanExporters called
from this operation may be used for testing, proof-of-concept ideas, or
debugging and may not be designed for production use themselves. They are not
in the scope of this requirement and recommendation.

#### Record Exception

To facilitate recording an exception languages SHOULD provide a
`RecordException` method if the language uses exceptions.
This is a specialized variant of [`AddEvent`](#add-events),
so for anything not specified here, the same requirements as for `AddEvent` apply.

The signature of the method is to be determined by each language
and can be overloaded as appropriate.
The method MUST record an exception as an `Event` with the conventions outlined in
the [exceptions](exceptions.md) document.
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

- `GetContext` MUST return the wrapped `SpanContext`.
- `IsRecording` MUST return `false` to signal that events, attributes and other elements
  are not being recorded, i.e. they are being dropped.

The remaining functionality of `Span` MUST be defined as no-op operations.
Note: This includes `End`, so as an exception from the general rule,
it is not required (or even helpful) to end such a Span.

This functionality MUST be fully implemented in the API, and SHOULD NOT be overridable.

## SpanKind

`SpanKind` clarifies the relationship between Spans that are correlated via
parent/child relationships or span links. `SpanKind` describes two independent
properties that benefit tracing systems during analysis:

1. Whether a span represents an outgoing call to a remote service (`CLIENT` and
   `PRODUCER` spans) or a processing of an incoming request initiated externally (`SERVER`
   and `CONSUMER` spans).
2. Whether a Span represents a request/response operation (`CLIENT` and `SERVER`
   spans) or a deferred execution (`PRODUCER` and `CONSUMER` spans).

In order for `SpanKind` to be meaningful, callers SHOULD arrange that
a single Span does not serve more than one purpose.  For example, a
server-side span SHOULD NOT be used to describe outgoing remote procedure call.
As a simple guideline, instrumentation should create a
new Span prior to injecting the `SpanContext` for a remote outgoing call.

Note: A `CLIENT` span may have a child that is also a `CLIENT` span, or a
`PRODUCER` span might have a local child that is a `CLIENT` span,
depending on how the various components that are providing the functionality
are built and instrumented.

[Semantic conventions](../overview.md#semantic-conventions) for
specific technologies should document kind for each span they define.

For instance, [Database Client Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/db/database-spans/)
recommend using `CLIENT` span kind to describes database calls.
If the database client communicates to the server over HTTP, the HTTP
instrumentation (when enabled) creates nested `CLIENT` spans to track individual
HTTP calls performed in the scope of logical database `CLIENT` operation.

These are the possible `SpanKind`s:

* `SERVER` indicates that the span covers server-side handling of a remote
  request while the client awaits a response.
* `CLIENT` indicates that the span describes a request to a remote service where
  the client awaits a response.
  When the context of a `CLIENT` span is propagated, `CLIENT` span usually
  becomes a parent of a remote `SERVER` span.
* `PRODUCER` indicates that the span describes the initiation or scheduling
  of a local or remote operation. This initiating span often ends before the
  correlated `CONSUMER` span, possibly even before the `CONSUMER` span starts.

  In messaging scenarios with batching, tracing individual messages requires
  a new `PRODUCER` span per message to be created.
* `CONSUMER` indicates that the span represents the processing of an operation
  initiated by a producer, where the producer does not wait for the outcome.
* `INTERNAL` Default value. Indicates that the span represents an
  internal operation within an application, as opposed to an
  operations with remote parents or children.

To summarize the interpretation of these kinds:

| `SpanKind` | Call direction | Communication style |
|------------|----------------|---------------------|
| `CLIENT`   |   outgoing     |   request/response  |
| `SERVER`   |   incoming     |   request/response  |
| `PRODUCER` |   outgoing     |  deferred execution |
| `CONSUMER` |   incoming     |  deferred execution |
| `INTERNAL` |                |                     |

## Link

A user MUST have the ability to record links to other `SpanContext`s.
Linked `SpanContext`s can be from the same or a different trace -- see [Links
between spans](../overview.md#links-between-spans).

A `Link` is structurally defined by the following properties:

- `SpanContext` of the `Span` to link to.
- Zero or more [`Attributes`](../common/README.md#attribute) further describing
  the link.

The API MUST provide:

- An API to record a single `Link` where the `Link` properties are passed as
  arguments. This MAY be called `AddLink`. This API takes the `SpanContext` of
  the `Span` to link to and optional `Attributes`, either as individual
  parameters or as an immutable object encapsulating them, whichever is most
  appropriate for the language. Implementations SHOULD record links containing
  `SpanContext` with empty `TraceId` or `SpanId` (all zeros) as long as either the attribute set
  or `TraceState` is non-empty.

The Span interface MAY provide:

- An API to add multiple `Link`s at once, where the `Link`s are passed in a
  single method call.

Span SHOULD preserve the order in which `Link`s are set.

The API documentation MUST state that adding links at span creation is preferred
to calling `AddLink` later, for contexts that are available during span creation,
because head sampling decisions can only consider information present during span creation.

## Concurrency requirements

For languages which support concurrent execution the Tracing APIs provide
specific guarantees and safeties. Not all of API functions are safe to
be called concurrently.

**TracerProvider** - all methods MUST be safe to be called concurrently.

**Tracer** - all methods MUST be safe to be called concurrently.

**Span** - all methods MUST be safe to be called concurrently.

**Event** - Events are immutable and MUST be safe to be called concurrently.

**Link** - Links are immutable and MUST be safe to be called concurrently.

## Included Propagators

See [Propagators Distribution](../context/api-propagators.md#propagators-distribution)
for how propagators are to be distributed.

## Behavior of the API in the absence of an installed SDK

In general, in the absence of an installed SDK, the Trace API is a "no-op" API.
This means that operations on a Tracer, or on Spans, should have no side effects
and do nothing. However, there is one important exception to this general rule,
and that is related to propagation of a `SpanContext`: The API MUST return a
non-recording `Span` with the `SpanContext` in the parent `Context` (whether explicitly given or implicit current).
If the `Span` in the parent `Context` is already non-recording, it SHOULD be returned directly
without instantiating a new `Span`.
If the parent `Context` contains no `Span`, an empty non-recording Span MUST be
returned instead (i.e., having a `SpanContext` with all-zero Span and Trace IDs,
empty Tracestate, and unsampled TraceFlags).  This means that a `SpanContext`
that has been provided by a configured `Propagator` will be propagated through
to any child span and ultimately also `Inject`, but that no new `SpanContext`s
will be created.
