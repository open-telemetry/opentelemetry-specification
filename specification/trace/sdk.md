<!--- Hugo front matter used to generate the website version of this page:
linkTitle: SDK
--->

# Tracing SDK

**Status**: [Stable](../document-status.md), except where otherwise specified

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [Tracer Provider](#tracer-provider)
  * [Tracer Creation](#tracer-creation)
  * [Configuration](#configuration)
    + [TracerConfigurator](#tracerconfigurator)
  * [Shutdown](#shutdown)
  * [ForceFlush](#forceflush)
- [Tracer](#tracer)
  * [TracerConfig](#tracerconfig)
  * [Enabled](#enabled)
- [Additional Span Interfaces](#additional-span-interfaces)
- [Sampling](#sampling)
  * [Recording Sampled reaction table](#recording-sampled-reaction-table)
  * [SDK Span creation](#sdk-span-creation)
    + [Span flags](#span-flags)
  * [Sampler](#sampler)
    + [ShouldSample](#shouldsample)
    + [GetDescription](#getdescription)
  * [Built-in samplers](#built-in-samplers)
    + [AlwaysOn](#alwayson)
    + [AlwaysOff](#alwaysoff)
    + [TraceIdRatioBased](#traceidratiobased)
      - [`TraceIdRatioBased` sampler configuration](#traceidratiobased-sampler-configuration)
      - [`TraceIdRatioBased` sampler algorithm](#traceidratiobased-sampler-algorithm)
      - [`TraceIdRatioBased` sampler description](#traceidratiobased-sampler-description)
      - [`TraceIdRatioBased` sampler compatibility warning](#traceidratiobased-sampler-compatibility-warning)
    + [ParentBased](#parentbased)
    + [JaegerRemoteSampler](#jaegerremotesampler)
    + [CompositeSampler](#compositesampler)
      - [ComposableSampler](#composablesampler)
        * [GetSamplingIntent](#getsamplingintent)
      - [Built-in ComposableSamplers](#built-in-composablesamplers)
        * [ComposableAlwaysOn](#composablealwayson)
        * [ComposableAlwaysOff](#composablealwaysoff)
        * [ComposableTraceIDRatioBased](#composabletraceidratiobased)
        * [ComposableParentThreshold](#composableparentthreshold)
        * [ComposableRuleBased](#composablerulebased)
        * [ComposableAnnotating](#composableannotating)
  * [Sampling Requirements](#sampling-requirements)
    + [TraceID randomness](#traceid-randomness)
    + [Random trace flag](#random-trace-flag)
    + [Explicit randomness](#explicit-randomness)
      - [Do not overwrite explicit randomness](#do-not-overwrite-explicit-randomness)
      - [Root samplers set explicit randomness for non-random TraceIDs](#root-samplers-set-explicit-randomness-for-non-random-traceids)
    + [Presumption of TraceID randomness](#presumption-of-traceid-randomness)
    + [IdGenerator randomness](#idgenerator-randomness)
- [Span Limits](#span-limits)
- [Id Generators](#id-generators)
  * [IdGenerator randomness](#idgenerator-randomness-1)
- [Span processor](#span-processor)
  * [Interface definition](#interface-definition)
    + [OnStart](#onstart)
    + [OnEnding](#onending)
    + [OnEnd(Span)](#onendspan)
    + [Shutdown()](#shutdown)
    + [ForceFlush()](#forceflush)
  * [Built-in span processors](#built-in-span-processors)
    + [Simple processor](#simple-processor)
    + [Batching processor](#batching-processor)
- [Span Exporter](#span-exporter)
  * [Interface Definition](#interface-definition)
    + [`Export(batch)`](#exportbatch)
    + [`Shutdown()`](#shutdown)
    + [`ForceFlush()`](#forceflush)
  * [Further Language Specialization](#further-language-specialization)
    + [Examples](#examples)
      - [Go SpanExporter Interface](#go-spanexporter-interface)
      - [Java SpanExporter Interface](#java-spanexporter-interface)

<!-- tocstop -->

</details>

## Tracer Provider

### Tracer Creation

It SHOULD only be possible to create `Tracer` instances through a `TracerProvider`
(see [API](./api.md#tracerprovider)).

The `TracerProvider` MUST implement the [Get a Tracer API](api.md#get-a-tracer).

The input provided by the user MUST be used to create
an [`InstrumentationScope`](../common/instrumentation-scope.md) instance which
is stored on the created `Tracer`.

**Status**: [Development](../document-status.md) - The `TracerProvider` MUST
compute the relevant [TracerConfig](#tracerconfig) using the
configured [TracerConfigurator](#tracerconfigurator), and create
a `Tracer` whose behavior conforms to that `TracerConfig`.

### Configuration

Configuration (
i.e., [SpanProcessors](#span-processor), [IdGenerator](#id-generators), [SpanLimits](#span-limits), [`Sampler`](#sampling),
and (**Development**) [TracerConfigurator](#tracerconfigurator)) MUST be
owned by the `TracerProvider`. The configuration MAY be applied at the time
of `TracerProvider` creation if appropriate.

The TracerProvider MAY provide methods to update the configuration. If
configuration is updated (e.g., adding a `SpanProcessor`),
the updated configuration MUST also apply to all already returned `Tracers`
(i.e. it MUST NOT matter whether a `Tracer` was obtained from the
`TracerProvider` before or after the configuration change).
Note: Implementation-wise, this could mean that `Tracer` instances have a
reference to their `TracerProvider` and access configuration only via this
reference.

#### TracerConfigurator

**Status**: [Development](../document-status.md)

A `TracerConfigurator` is a function which computes
the [TracerConfig](#tracerconfig) for a [Tracer](#tracer).

The function MUST accept the following parameter:

* `tracer_scope`:
  The [`InstrumentationScope`](../common/instrumentation-scope.md) of
  the `Tracer`.

The function MUST return the relevant `TracerConfig`, or some signal indicating
that the [default TracerConfig](#tracerconfig) should be used. This signal MAY
be nil, null, empty, or an instance of the default `TracerConfig` depending on
what is idiomatic in the language.

This function is called when a `Tracer` is first created, and for each
outstanding `Tracer` when a `TracerProvider`'s `TracerConfigurator` is
updated (if updating is supported). Therefore, it is important that it returns
quickly.

`TracerConfigurator` is modeled as a function to maximize flexibility.
However, implementations MAY provide shorthand or helper functions to
accommodate common use cases:

* Select one or more Tracers by name, with exact match or pattern matching.
* Disable one or more specific Tracers.
* Disable all Tracers, and selectively enable one or more specific Tracers.

### Shutdown

This method provides a way for provider to do any cleanup required.

`Shutdown` MUST be called only once for each `TracerProvider` instance. After
the call to `Shutdown`, subsequent attempts to get a `Tracer` are not allowed. SDKs
SHOULD return a valid no-op Tracer for these calls, if possible.

`Shutdown` SHOULD provide a way to let the caller know whether it succeeded,
failed or timed out.

`Shutdown` SHOULD complete or abort within some timeout. `Shutdown` can be
implemented as a blocking API or an asynchronous API which notifies the caller
via a callback or an event. OpenTelemetry client authors can decide if they want to
make the shutdown timeout configurable.

`Shutdown` MUST be implemented at least by invoking `Shutdown` within all internal processors.

### ForceFlush

This method provides a way for provider to immediately export all spans that have not yet been exported for all the internal processors.

`ForceFlush` SHOULD provide a way to let the caller know whether it succeeded,
failed or timed out.

`ForceFlush` SHOULD complete or abort within some timeout. `ForceFlush` can be
implemented as a blocking API or an asynchronous API which notifies the caller
via a callback or an event. OpenTelemetry client authors can decide if they want to
make the flush timeout configurable.

`ForceFlush` MUST invoke `ForceFlush` on all registered `SpanProcessors`.

## Tracer

**Status**: [Development](../document-status.md) - `Tracer` MUST behave
according to the [TracerConfig](#tracerconfig) computed
during [Tracer creation](#tracer-creation). If the `TracerProvider` supports
updating the [TracerConfigurator](#tracerconfigurator), then upon update
the `Tracer` MUST be updated to behave according to the new `TracerConfig`.

### TracerConfig

**Status**: [Development](../document-status.md)

A `TracerConfig` defines various configurable aspects of a `Tracer`'s behavior.
It consists of the following parameters:

* `disabled`: A boolean indication of whether the Tracer is enabled.

  If not explicitly set, the `disabled` parameter SHOULD default to `false` (
  i.e. `Tracer`s are enabled by default).

  If a `Tracer` is disabled, it MUST behave equivalently
  to a [No-op Tracer](./api.md#behavior-of-the-api-in-the-absence-of-an-installed-sdk).

  The value of `disabled` MUST be used to resolve whether a `Tracer`
  is [Enabled](./api.md#enabled). If `disabled` is `true`, `Enabled`
  returns `false`. If `disabled` is `false`, `Enabled` returns `true`. It is not
  necessary for implementations to ensure that changes to `disabled` are
  immediately visible to callers of `Enabled`.

### Enabled

**Status**: [Development](../document-status.md)

`Enabled` MUST return `false` when either:

- there are no registered [`SpanProcessors`](#span-processor),
- `Tracer` is disabled ([`TracerConfig.disabled`](#tracerconfig) is `true`).

Otherwise, it SHOULD return `true`.
It MAY return `false` to support additional optimizations and features.

## Additional Span Interfaces

The [API-level definition for Span's interface](api.md#span-operations)
only defines write-only access to the span.
This is good because instrumentations and applications are not meant to use the data
stored in a span for application logic.
However, the SDK needs to eventually read back the data in some locations.
Thus, the SDK specification defines sets of possible requirements for
`Span`-like parameters:

* **Readable span**: A function receiving this as argument MUST be able to
  access all information that was added to the span, as listed
  in the API spec for [Span](api.md#span). Note: Below, a few particular properties
  are called out for clarity, but for the complete list of required properties,
  the [Span API spec](api.md#span) is authoritative.

  A function receiving this as argument MUST be able to access
  the `InstrumentationScope` [since 1.10.0] and `Resource` information
  (implicitly) associated with the span. For backwards compatibility
  it MUST also be able to access the `InstrumentationLibrary`
  [deprecated since 1.10.0] having the same name and version values as the
  `InstrumentationScope`.

  A function receiving this as argument MUST be able to reliably determine
  whether the Span has ended
  (some languages might implement this by having an end timestamp of `null`,
  others might have an explicit `hasEnded` boolean).

  Counts for attributes, events and links dropped due to collection limits MUST be
  available for exporters to report as described in the [exporters](../common/mapping-to-non-otlp.md#dropped-attributes-count)
  specification.

  As an exception to the authoritative set of span properties defined in the API spec,
  implementations MAY choose not to expose (and store) the full parent [Context](../context/README.md)
  of the Span but they MUST expose at least the full parent [SpanContext](api.md#spancontext).

  A function receiving this as argument might not be able to modify the Span.

  Note: Typically this will be implemented with a new interface or
  (immutable) value type.
  In some languages SpanProcessors may have a different readable span type
  than exporters (e.g. a `SpanData` type might contain an immutable snapshot and
  a `ReadableSpan` interface might read information directly from the same
  underlying data structure that the `Span` interface manipulates).

* **Read/write span**: A function receiving this as argument must have access to
  both the full span API as defined in the
  [API-level definition for span's interface](api.md#span-operations) and
  additionally must be able to retrieve all information that was added to the span
  (as with *readable span*).

  It MUST be possible for functions being called with this
  to somehow obtain the same `Span` instance and type
  that the [span creation API](api.md#span-creation) returned (or will return) to the user
  (for example, the `Span` could be one of the parameters passed to such a function,
  or a getter could be provided).

## Sampling

Sampling is a mechanism to control the noise and overhead introduced by
OpenTelemetry by reducing the number of samples of traces collected and sent to
the backend.

Sampling may be implemented on different stages of a trace collection. The
earliest sampling could happen before the trace is actually created, and the
latest sampling could happen on the Collector, which is out of process.

The OpenTelemetry API has two properties responsible for the data collection:

* `IsRecording` field of a `Span`. If `false`, the current `Span` discards all
  tracing data (attributes, events, status, etc.). Users can use this property
  to determine if collecting expensive trace data can be avoided. [Span
  Processor](#span-processor) MUST receive only those spans which have this
  field set to `true`. However, [Span Exporter](#span-exporter) SHOULD NOT
  receive them unless the `Sampled` flag was also set.
* `Sampled` flag in `TraceFlags` on `SpanContext`. This flag is propagated via
  the `SpanContext` to child Spans. For more details see the [W3C Trace Context
  specification][W3CCONTEXTSAMPLEDFLAG]. This flag indicates that the `Span` has been
  `sampled` and will be exported. [Span Exporters](#span-exporter) MUST
  receive those spans which have `Sampled` flag set to true and they SHOULD NOT receive the ones
  that do not.

The flag combination `SampledFlag == false` and `IsRecording == true`
means that the current `Span` does record information, but most likely the child
`Span` will not.

The flag combination `SampledFlag == true` and `IsRecording == false`
could cause gaps in the distributed trace, and because of this the OpenTelemetry SDK
MUST NOT allow this combination.

### Recording Sampled reaction table

The following table summarizes the expected behavior for each combination of
`IsRecording` and `SampledFlag`.

| `IsRecording` | `Sampled` Flag | Span Processor receives Span? | Span Exporter receives Span? |
| ------------- | -------------- | ----------------------------- | ---------------------------- |
| true          | true           | true                          | true                         |
| true          | false          | true                          | false                        |
| false         | true           | Not allowed                   | Not allowed                  |
| false         | false          | false                         | false                        |

The SDK defines the interface [`Sampler`](#sampler) as well as a set of
[built-in samplers](#built-in-samplers) and associates a `Sampler` with each [`TracerProvider`].

### SDK Span creation

When asked to create a Span, the SDK MUST act as if doing the following in order:

1. If there is a valid parent trace ID, use it. Otherwise generate a new trace ID
   (note: this must be done before calling `ShouldSample`, because it expects
   a valid trace ID as input).
2. Query the `Sampler`'s [`ShouldSample`](#shouldsample) method.
3. Generate a new span ID for the `Span`, independently of the sampling decision.
   This is done so other components (such as logs or exception handling) can rely on
   a unique span ID, even if the `Span` is a non-recording instance.
4. Create a span depending on the decision returned by `ShouldSample`:
   see description of [`ShouldSample`'s](#shouldsample) return value below
   for how to set `IsRecording` and `Sampled` on the Span,
   and the [table above](#recording-sampled-reaction-table) on whether
   to pass the `Span` to `SpanProcessor`s.
   A non-recording span MAY be implemented using the same mechanism as when a
   `Span` is created without an SDK installed or as described in
   [wrapping a SpanContext in a Span](api.md#wrapping-a-spancontext-in-a-span).

#### Span flags

The OTLP representation for Span and Span Link includes a 32-bit field declared as Span Flags.

Bits 0-7 (8 least significant bits) of the Span Flags field are reserved for the 8 bits of Trace Context flags,
specified in the [W3C Trace Context Level 2][W3CCONTEXTMAIN] Candidate Recommendation.
[See the list of recognized flags](./api.md#spancontext).

### Sampler

`Sampler` interface allows users to create custom samplers which will return a
sampling `SamplingResult` based on information that is typically available just
before the `Span` was created.

#### ShouldSample

Returns the sampling Decision for a `Span` to be created.

**Required arguments:**

* [`Context`](../context/README.md) with parent `Span`.
  The Span's SpanContext may be invalid to indicate a root span.
* `TraceId` of the `Span` to be created.
  If the parent `SpanContext` contains a valid `TraceId`, they MUST always match.
* Name of the `Span` to be created.
* `SpanKind` of the `Span` to be created.
* Initial set of `Attributes` of the `Span` to be created.
* Collection of links that will be associated with the `Span` to be created.
  Typically useful for batch operations, see
  [Links Between Spans](../overview.md#links-between-spans).

Note: Implementations may "bundle" all or several arguments together in a single
object.

**Return value:**

It produces an output called `SamplingResult` which contains:

* A sampling `Decision`. One of the following enum values:
  * `DROP` - `IsRecording` will be `false`, the `Span` will not be recorded and all events and attributes
  will be dropped.
  * `RECORD_ONLY` - `IsRecording` will be `true`, but the `Sampled` flag MUST NOT be set.
  * `RECORD_AND_SAMPLE` - `IsRecording` will be `true` and the `Sampled` flag MUST be set.
* A set of span Attributes that will also be added to the `Span`. The returned
object must be immutable (multiple calls may return different immutable objects).
* A `Tracestate` that will be associated with the `Span` through the new
  `SpanContext`.
  If the sampler returns an empty `Tracestate` here, the `Tracestate` will be cleared,
  so samplers SHOULD normally return the passed-in `Tracestate` if they do not intend
  to change it.

#### GetDescription

Returns the sampler name or short description with the configuration. This may
be displayed on debug pages or in the logs. Example:
`"TraceIdRatioBased{0.000100}"`.

Description MAY change over time, for example, if the sampler supports dynamic
configuration or otherwise adjusts its parameters.
Callers SHOULD NOT cache the returned value.

### Built-in samplers

OpenTelemetry supports a number of built-in samplers to choose from.
The default sampler is `ParentBased(root=AlwaysOn)`.

#### AlwaysOn

* Returns `RECORD_AND_SAMPLE` always.
* Description MUST be `AlwaysOnSampler`.

#### AlwaysOff

* Returns `DROP` always.
* Description MUST be `AlwaysOffSampler`.

#### TraceIdRatioBased

**Status**: [Development](../document-status.md)

The `TraceIdRatioBased` sampler implements simple, ratio-based probability sampling using randomness features specified in the [W3C Trace Context Level 2][W3CCONTEXTMAIN] Candidate Recommendation.
OpenTelemetry follows W3C Trace Context Level 2, which specifies 56 bits of randomness,
[specifying how to make consistent probability sampling decisions using 56 bits of randomness][CONSISTENTSAMPLING].

The `TraceIdRatioBased` sampler MUST ignore the parent `SampledFlag`.
For respecting the parent `SampledFlag`, see the `ParentBased` sampler specified below.

Note that the "ratio-based" part of this Sampler's name implies that
it makes a probability decision directly from the TraceID, even though
it was not originally specified in an exact way.  In the present
specification, the Sampler decision is more nuanced: only a portion of
the identifier is used, after checking whether the OpenTelemetry
TraceState field contains an explicit randomness value.

[W3CCONTEXTMAIN]: https://www.w3.org/TR/trace-context-2/

##### `TraceIdRatioBased` sampler configuration

The `TraceIdRatioBased` sampler is typically configured using a 32-bit or 64-bit floating point number to express the sampling ratio.
The minimum valid sampling ratio is `2^-56`, and the maximum valid sampling ratio is 1.0.
From an input sampling ratio, a rejection threshold value is calculated; see [consistent-probability sampler requirements][CONSISTENTSAMPLING] for details on converting sampling ratios into thresholds with variable precision.

[CONSISTENTSAMPLING]: ./tracestate-probability-sampling.md

##### `TraceIdRatioBased` sampler algorithm

Given a Sampler configured with a sampling threshold `T` and Context with randomness value `R` (typically, the 7 rightmost bytes of the trace ID), when `ShouldSample()` is called, it uses the expression `R >= T` to decide whether to return `RECORD_AND_SAMPLE` or `DROP`.

* If randomness value (R) is greater or equal to the rejection threshold (T), meaning when (R >= T), return `RECORD_AND_SAMPLE`, otherwise, return `DROP`.
* When (R >= T), the OpenTelemetry TraceState SHOULD be modified to include the key-value `th:T` for rejection threshold value (T), as specified for the [OpenTelemetry TraceState `th` sub-key][TRACESTATEHANDLING].

[TRACESTATEHANDLING]: ./tracestate-handling.md#sampling-threshold-value-th

##### `TraceIdRatioBased` sampler description

The `TraceIdRatioBased` GetDescription MUST return a string of the form `"TraceIdRatioBased{RATIO}"`
with `RATIO` replaced with the Sampler instance's trace sampling ratio
represented as a decimal number. The precision of the number SHOULD follow
implementation language standards and SHOULD be high enough to identify when
Samplers have different ratios. For example, if a TraceIdRatioBased Sampler
had a sampling ratio of 1 to every 10,000 spans it could return
`"TraceIdRatioBased{0.000100}"` as its description.

##### `TraceIdRatioBased` sampler compatibility warning

This specification has been revised from the original
`TraceIdRatioBased` Sampler definition.  The present definition for
`TraceIdRatioBased` uses a new definition for trace randomness, where
unless an explicit randomness value is set in the OpenTelemetry
TraceState `rv` sub-key, Samplers are meant to presume that TraceIDs
contain the necessary 56 bits of randomness.

When a TraceIdRatioBased Sampler makes a decision for a non-root Span
based on TraceID randomness, there is a possibility that the TraceID
was in fact generated by an older SDK, unaware of this specification.
The Trace random flag lets us disambiguate these two cases.  This flag
propagates information to let TraceIdRatioBased Samplers confirm that
TraceIDs are random, however this requires W3C Trace Context Level 2
to be supported by every Trace SDK that has handled the context.

When a TraceIdRatioBased Sampler makes a decision for a non-root Span
using TraceID randomness, but the Trace random flag was not set, the
SDK SHOULD issue a warning statement in its log with a compatibility
warning.  As an example of this compatibility warning:

```
WARNING: The TraceIdRatioBased sampler is presuming TraceIDs are random
and expects the Trace random flag to be set in confirmation.  Please
upgrade your caller(s) to use W3C Trace Context Level 2.
```

#### ParentBased

* This is a sampler decorator. `ParentBased` helps distinguish between the
following cases:
  * No parent (root span).
  * Remote parent (`SpanContext.IsRemote() == true`) with `SampledFlag` set
  * Remote parent (`SpanContext.IsRemote() == true`) with `SampledFlag` not set
  * Local parent (`SpanContext.IsRemote() == false`) with `SampledFlag` set
  * Local parent (`SpanContext.IsRemote() == false`) with `SampledFlag` not set

Required parameters:

* `root(Sampler)` - Sampler called for spans with no parent (root spans)

Optional parameters:

* `remoteParentSampled(Sampler)` (default: AlwaysOn)
* `remoteParentNotSampled(Sampler)` (default: AlwaysOff)
* `localParentSampled(Sampler)` (default: AlwaysOn)
* `localParentNotSampled(Sampler)` (default: AlwaysOff)

|Parent| parent.isRemote() | parent.IsSampled()| Invoke sampler|
|--|--|--|--|
|absent| n/a | n/a |`root()`|
|present|true|true|`remoteParentSampled()`|
|present|true|false|`remoteParentNotSampled()`|
|present|false|true|`localParentSampled()`|
|present|false|false|`localParentNotSampled()`|

#### JaegerRemoteSampler

[Jaeger remote sampler][jaeger-remote-sampling] allows remotely controlling the sampling configuration for the SDKs. The sampling configuration is periodically loaded from the backend (see [Remote Sampling API][jaeger-remote-sampling-api]), where it can be managed by operators via configuration files or even automatically calculated (see [Adaptive Sampling][jaeger-adaptive-sampling]). The sampling configuration retrieved by the remote sampler can instruct it to  use either a single sampling method for the whole service (e.g., `TraceIdRatioBased`), or different methods for different endpoints (span names), for example, sample `/product` endpoint at 10%, `/admin` endpoint at 100%, and never sample `/metrics` endpoint.

The full Protobuf definition can be found at [jaegertracing/jaeger-idl/api_v2/sampling.proto](https://github.com/jaegertracing/jaeger-idl/blob/main/proto/api_v2/sampling.proto).

The following configuration properties should be available when creating the sampler:

* endpoint - address of a service that implements the [Remote Sampling API][jaeger-remote-sampling-api], such as Jaeger Collector or OpenTelemetry Collector.
* polling interval - polling interval for getting configuration from remote
* initial sampler - initial sampler that is used before the first configuration is fetched

[jaeger-remote-sampling]: https://www.jaegertracing.io/docs/1.41/architecture/sampling/#remote-sampling
[jaeger-remote-sampling-api]: https://www.jaegertracing.io/docs/1.41/architecture/apis/#remote-sampling-configuration-stable
[jaeger-adaptive-sampling]: https://www.jaegertracing.io/docs/1.41/architecture/sampling/#adaptive-sampling

#### CompositeSampler

**Status**: [Development](../document-status.md)

CompositeSampler is a decorator that implements the standard `Sampler` interface but uses a composition of samplers to make its decisions.

The CompositeSampler takes a ComposableSampler as input and delegates the sampling decision to that interface.  See [Probability Sampling in TraceState](./tracestate-probability-sampling.md) for more details.

##### ComposableSampler

ComposableSampler is a specialized interface that extends the standard Sampler functionality. It introduces a composable approach to sampling by defining a new method called `GetSamplingIntent`, which allows multiple samplers to work together in making a sampling decision.

###### GetSamplingIntent

Returns a SamplingIntent structure that indicates the sampler's preference for sampling a Span, without actually making the final decision.

**Required arguments:**

* All of the original Sampler API parameters are included
* Parent context, threshold, incoming trace state, and trace flag
  information MAY be precomputed so that ComposableSamplers do not
  repeatedly probe the Context for this information.

Note: ComposableSamplers MUST NOT modify the parameters passed to
delegate GetSamplingIntent methods, as they are considered read-only
state.

**Return value:**

The method returns a `SamplingIntent` structure with the following elements:

* `threshold` - The sampling threshold value. A lower threshold increases the likelihood of sampling.
* `threshold_reliable` - A boolean indicating if the threshold can be reliably used for
   [Span-to-Metrics estimation](./tracestate-probability-sampling.md#sampling-related-terms).
* `attributes_provider` - An optional provider of attributes to be added to the span if it is sampled.
* `trace_state_provider` - An optional provider of a modified TraceState.

Note that `trace_state_provider` may be a significant source of
complexity.  ComposableSamplers MUST NOT modify the OpenTelemetry
TraceState (i.e., the `ot` sub-key of TraceState).  The calling
CompositeSampler SHOULD update the threshold of the outgoing
TraceState (unless `!threshold_reliable`) and that the explicit
randomness values MUST not be modified.

##### Built-in ComposableSamplers

###### ComposableAlwaysOn

* Always returns a `SamplingIntent` with threshold set to sample all spans (threshold = 0)
* Sets `threshold_reliable` to `true`
* Does not add any attributes

###### ComposableAlwaysOff

* Always returns a `SamplingIntent` with no threshold, indicating all spans should be dropped
* Sets `threshold_reliable` to `false`
* Does not add any attributes

###### ComposableTraceIDRatioBased

* Returns a `SamplingIntent` with threshold determined by the configured sampling ratio
* Sets `threshold_reliable` to `true`
* Does not add any attributes

**Required parameters:**

* `ratio` - A value between `2^-56` and 1.0 (inclusive) representing the desired probability of sampling.

A ratio value of 0 is considered non-probabilistic. For the zero case
a `ComposableAlwaysOff` instance SHOULD be returned instead.

###### ComposableParentThreshold

* For spans without a parent context, delegate to the root sampler
* For spans with a parent context, returns a `SamplingIntent` that propagates the parent's sampling decision
* Returns the parent's threshold if available; otherwise, if the parent's *sampled* flag is set, returns threshold=0; otherwise, if the parent's *sampled* flag is not set, no threshold is returned.
* Sets `threshold_reliable` to match the parent's reliability, which is true if the parent had a threshold.
* Does not add any attributes

**Required parameters:**

* `root` - A delegate for sampling spans without a parent context.

###### ComposableRuleBased

* Evaluates a series of rules based on predicates and returns the `SamplingIntent` from the first matching sampler
* If no rules match, returns a non-sampling intent

**Required parameters:**

* `rules` - A list of (Predicate, ComposableSampler) pairs, where Predicate is a function that evaluates whether a rule applies

###### ComposableAnnotating

* Delegates the sampling decision to another sampler but adds attributes to sampled spans
* Returns a `SamplingIntent` that combines the delegate's threshold with additional attributes

**Required parameters:**

* `attributes` - Attributes to add to sampled spans
* `delegate` - The underlying sampler that makes the actual sampling decision

**Example configuration:**

An example of creating a composite sampler configuration:

```
// Create a rule-based sampler for root spans
rootSampler = ComposableRuleBased([
  (isHealthCheck, ComposableAlwaysOff),
  (isCheckout, ComposableAlwaysOn),
  (isAnything, ComposableTraceIDRatio(0.1))
])

// Create a parent-based sampler for child spans
finalSampler = ComposableParentThreshold(rootSampler)
```

This example creates a configuration where:

- Health check endpoints are never sampled
- Checkout endpoints are always sampled
- Other root spans are sampled at 10%
- Child spans follow their parent's sampling decision

### Sampling Requirements

**Status**: [Development](../document-status.md)

The [W3C Trace Context Level 2][W3CCONTEXTMAIN] Candidate Recommendation includes [a Random trace flag][W3CCONTEXTRANDOMFLAG] for indicating that the TraceID contains 56 random bits, specified for statistical purposes.
This flag indicates that [the least-significant ("rightmost") 7 bytes or 56 bits of the TraceID are random][W3CCONTEXTTRACEID].

Note the Random flag does not propagate through [Trace Context Level 1][W3CCONTEXTLEVEL1] implementations, which do not recognize the flag.
When this flag is 1, it is considered meaningful.  When this flag is 0, it may be due to a non-random TraceID or because a Trace Context Level 1 propagator was used.
To enable sampling in this and other situations where TraceIDs lack sufficient randomness,
OpenTelemetry defines an optional [explicit randomness value][OTELRVALUE] encoded in the [W3C TraceState field][W3CCONTEXTTRACESTATE].

This specification recommends the use of either TraceID randomness or explicit randomness,
which ensures that samplers always have sufficient randomness when using W3C Trace Context propagation.

[W3CCONTEXTMAIN]: https://www.w3.org/TR/trace-context-2/
[W3CCONTEXTLEVEL1]: https://www.w3.org/TR/trace-context/
[W3CCONTEXTTRACEID]: https://www.w3.org/TR/trace-context-2/#randomness-of-trace-id
[W3CCONTEXTTRACESTATE]: https://www.w3.org/TR/trace-context-2/#tracestate-header
[W3CCONTEXTSAMPLEDFLAG]: https://www.w3.org/TR/trace-context-2/#sampled-flag
[W3CCONTEXTRANDOMFLAG]: https://www.w3.org/TR/trace-context-2/#random-trace-id-flag
[OTELRVALUE]: ./tracestate-handling.md#explicit-randomness-value-rv

#### TraceID randomness

For root span contexts, the SDK SHOULD implement the TraceID randomness requirements of the [W3C Trace Context Level 2][W3CCONTEXTTRACEID] Candidate Recommendation when generating TraceID values.

#### Random trace flag

For root span contexts, the SDK SHOULD set the `Random` flag in the trace flags when it generates TraceIDs that meet the [W3C Trace Context Level 2 randomness requirements][W3CCONTEXTTRACEID].

#### Explicit randomness

Explicit randomness is a mechanism that enables API users and
SDK authors to control trace randomness.  The following recommendation
applies to Trace SDKs that have disregarded the recommendation on
TraceID randomness, above.  It has two parts.

##### Do not overwrite explicit randomness

API users control the initial TraceState of a root span, so they can
provide explicit randomness for a trace by defining the [`rv`
sub-key of the OpenTelemetry TraceState][OTELRVALUE].  SDKs and Samplers
MUST NOT overwrite explicit randomness in an OpenTelemetry TraceState
value.

##### Root samplers set explicit randomness for non-random TraceIDs

When the SDK has generated a TraceID that does not meet the [W3C Trace
Context Level 2 randomness requirements][W3CCONTEXTTRACEID], indicated
by an unset trace random flag, and when the the [`rv` sub-key of the
OpenTelemetry TraceState][OTELRVALUE] is not already set, the Root
sampler has the opportunity to insert an explicit randomness value.

Root Samplers MAY insert an explicit randomness value into the
OpenTelemetry TraceState value in cases where an explicit
randomness value is not already set.

For example, here's a W3C Trace Context with non-random identifiers and an
explicit randomness value:

```
traceparent: 00-ffffffffffffffffffffffffffffffff-ffffffffffffffff-00
tracestate: ot=rv:7479cfb506891d
```

#### Presumption of TraceID randomness

For all span contexts, OpenTelemetry samplers SHOULD presume that TraceIDs meet the W3C Trace Context Level 2 randomness requirements, unless an explicit randomness value is present in the [`rv` sub-key of the OpenTelemetry TraceState][OTELRVALUE].

#### IdGenerator randomness

If the SDK uses an `IdGenerator` extension point, the SDK SHOULD allow the extension to determine whether the Random flag is set when new IDs are generated.

## Span Limits

Span attributes MUST adhere to the [common rules of attribute limits](../common/README.md#attribute-limits).

SDK Spans MAY also discard links and events that would increase the number of
elements of each collection beyond the configured limit.

If the SDK implements the limits above it MUST provide a way to change these
limits, via a configuration to the TracerProvider, by allowing users to
configure individual limits like in the Java example bellow.

The name of the configuration options SHOULD be `EventCountLimit` and `LinkCountLimit`. The options MAY be bundled in a class,
which then SHOULD be called `SpanLimits`. Implementations MAY provide additional
configuration such as `AttributePerEventCountLimit` and `AttributePerLinkCountLimit`.

```java
public final class SpanLimits {
  SpanLimits(int attributeCountLimit, int linkCountLimit, int eventCountLimit);

  public int getAttributeCountLimit();

  public int getAttributeCountPerEventLimit();

  public int getAttributeCountPerLinkLimit();

  public int getEventCountLimit();

  public int getLinkCountLimit();
}
```

**Configurable parameters:**

* [all common options applicable to attributes](../common/README.md#configurable-parameters)
* `EventCountLimit` (Default=128) - Maximum allowed span event count;
* `LinkCountLimit` (Default=128) - Maximum allowed span link count;
* `AttributePerEventCountLimit` (Default=128) - Maximum allowed attribute per span event count;
* `AttributePerLinkCountLimit` (Default=128) - Maximum allowed attribute per span link count;

There SHOULD be a message printed in the SDK's log to indicate to the user
that an attribute, event, or link was discarded due to such a limit.
To prevent excessive logging, the message MUST be printed at most once per
span (i.e., not per discarded attribute, event, or link).

## Id Generators

The SDK MUST by default randomly generate both the `TraceId` and the `SpanId`.

The SDK MUST provide a mechanism for customizing the way IDs are generated for
both the `TraceId` and the `SpanId`.

The SDK MAY provide this functionality by allowing custom implementations of
an interface like the java example below (name of the interface MAY be
`IdGenerator`, name of the methods MUST be consistent with
[SpanContext](./api.md#retrieving-the-traceid-and-spanid)), which provides
extension points for two methods, one to generate a `SpanId` and one for `TraceId`.

```java
public interface IdGenerator {
  byte[] generateSpanIdBytes();
  byte[] generateTraceIdBytes();
}
```

Additional `IdGenerator` implementing vendor-specific protocols such as AWS
X-Ray trace id generator MUST NOT be maintained or distributed as part of the
Core OpenTelemetry repositories.

### IdGenerator randomness

**Status**: [Development](../document-status.md)

Custom implementations of the `IdGenerator` SHOULD identify themselves
appropriately when all generated TraceID values meet the [W3C Trace
Context Level 2 randomness requirements][W3CCONTEXTTRACEID], so that
the Trace `random` flag will be set in the associated Trace contexts.
This is presumed to be a static property of the `IdGenerator`
implementation which can be inferred using language features, for
example by extending a marker interface.

## Span processor

Span processor is an interface which allows hooks for span start and end method
invocations. The span processors are invoked only when
[`IsRecording`](api.md#isrecording) is true.

Built-in span processors are responsible for batching and conversion of spans to
exportable representation and passing batches to exporters.

Span processors can be registered directly on SDK `TracerProvider` and they are
invoked in the same order as they were registered.

Each processor registered on `TracerProvider` is a start of pipeline that consist
of span processor and optional exporter. SDK MUST allow to end each pipeline with
individual exporter.

SDK MUST allow users to implement and configure custom processors.

The following diagram shows `SpanProcessor`'s relationship to other components
in the SDK:

```
  +-----+--------------+   +-------------------------+   +----------------+
  |     |              |   |                         |   |                |
  |     |              |   | Batching Span Processor |   |  SpanExporter  |
  |     |              +---> Simple Span Processor   +---> (OTLPExporter) |
  |     |              |   |                         |   |                |
  | SDK | Span.start() |   +-------------------------+   +----------------+
  |     | Span.end()   |
  |     |              |
  |     |              |
  |     |              |
  |     |              |
  +-----+--------------+
```

### Interface definition

The `SpanProcessor` interface MUST declare the following methods:

* [OnStart](#onstart)
* [OnEnd](#onendspan)
* [Shutdown](#shutdown-1)
* [ForceFlush](#forceflush-1)

The `SpanProcessor` interface SHOULD declare the following methods:

* [OnEnding](#onending) method.

#### OnStart

`OnStart` is called when a span is started. This method is called synchronously
on the thread that started the span, therefore it should not block or throw
exceptions. If multiple `SpanProcessors` are registered, their `OnStart` callbacks
are invoked in the order they have been registered.

**Parameters:**

* `span` - a [read/write span object](#additional-span-interfaces) for the started span.
  It SHOULD be possible to keep a reference to this span object and updates to the span
  SHOULD be reflected in it.
  For example, this is useful for creating a SpanProcessor that periodically
  evaluates/prints information about all active span from a background thread.
* `parentContext` - the parent `Context` of the span that the SDK determined
  (the explicitly passed `Context`, the current `Context` or an empty `Context`
  if that was explicitly requested).

**Returns:** `Void`

#### OnEnding

**Status**: [Development](../document-status.md)

`OnEnding` is called during the span `End()` operation.
The end timestamp MUST have been computed (the `OnEnding` method duration is not included
in the span duration).
The Span object MUST still be mutable (i.e., `SetAttribute`, `AddLink`, `AddEvent` can be called) while `OnEnding` is called.
This method MUST be called synchronously within the [`Span.End()` API](api.md#end),
therefore it should not block or throw an exception.
If multiple `SpanProcessors` are registered, their `OnEnding` callbacks
are invoked in the order they have been registered.
The SDK MUST guarantee that the span can no longer be modified by any other thread
before invoking `OnEnding` of the first `SpanProcessor`. From that point on, modifications
are only allowed synchronously from within the invoked `OnEnding` callbacks.  All registered SpanProcessor `OnEnding` callbacks are executed before any SpanProcessor's `OnEnd` callback is invoked.

**Parameters:**

* `span` - a [read/write span object](#additional-span-interfaces) for the span which is about to be ended.

**Returns:** `Void`

#### OnEnd(Span)

`OnEnd` is called after a span is ended (i.e., the end timestamp is already set).
This method MUST be called synchronously within the [`Span.End()` API](api.md#end),
therefore it should not block or throw an exception.

**Parameters:**

* `Span` - a [readable span object](#additional-span-interfaces) for the ended span.
  Note: Even if the passed Span may be technically writable,
  since it's already ended at this point, modifying it is not allowed.

**Returns:** `Void`

#### Shutdown()

Shuts down the processor. Called when SDK is shut down. This is an opportunity
for processor to do any cleanup required.

`Shutdown` SHOULD be called only once for each `SpanProcessor` instance. After
the call to `Shutdown`, subsequent calls to `OnStart`, `OnEnd`, or `ForceFlush`
are not allowed. SDKs SHOULD ignore these calls gracefully, if possible.

`Shutdown` SHOULD provide a way to let the caller know whether it succeeded,
failed or timed out.

`Shutdown` MUST include the effects of `ForceFlush`.

`Shutdown` SHOULD complete or abort within some timeout. `Shutdown` can be
implemented as a blocking API or an asynchronous API which notifies the caller
via a callback or an event. OpenTelemetry client authors can decide if they want to
make the shutdown timeout configurable.

#### ForceFlush()

This is a hint to ensure that any tasks associated with `Spans` for which the
`SpanProcessor` had already received events prior to the call to `ForceFlush` SHOULD
be completed as soon as possible, preferably before returning from this method.

In particular, if any `SpanProcessor` has any associated exporter, it SHOULD
try to call the exporter's `Export` with all spans for which this was not
already done and then invoke `ForceFlush` on it.
The [built-in SpanProcessors](#built-in-span-processors) MUST do so.
If a timeout is specified (see below), the SpanProcessor MUST prioritize honoring the timeout over
finishing all calls. It MAY skip or abort some or all Export or ForceFlush
calls it has made to achieve this goal.

`ForceFlush` SHOULD provide a way to let the caller know whether it succeeded,
failed or timed out.

`ForceFlush` SHOULD only be called in cases where it is absolutely necessary,
such as when using some FaaS providers that may suspend the process after an
invocation, but before the `SpanProcessor` exports the completed spans.

`ForceFlush` SHOULD complete or abort within some timeout. `ForceFlush` can be
implemented as a blocking API or an asynchronous API which notifies the caller
via a callback or an event. OpenTelemetry client authors can decide if they want to
make the flush timeout configurable.

### Built-in span processors

The standard OpenTelemetry SDK MUST implement both simple and batch processors,
as described below. Other common processing scenarios should be first considered
for implementation out-of-process in [OpenTelemetry Collector](../overview.md#collector).

#### Simple processor

This is an implementation of `SpanProcessor` which passes finished spans
and passes the export-friendly span data representation to the configured
`SpanExporter`, as soon as they are finished.

The processor MUST synchronize calls to `Span Exporter`'s `Export`
to make sure that they are not invoked concurrently.

**Configurable parameters:**

* `exporter` - the exporter where the spans are pushed.

#### Batching processor

This is an implementation of the `SpanProcessor` which create batches of finished
spans and passes the export-friendly span data representations to the
configured `SpanExporter`.

The processor MUST synchronize calls to `Span Exporter`'s `Export`
to make sure that they are not invoked concurrently.

The processor SHOULD export a batch when any of the following happens AND the
previous export call has returned:

- `scheduledDelayMillis` after the processor is constructed OR the first span
  is received by the span processor.
- `scheduledDelayMillis` after the previous export timer ends, OR the previous
  export completes, OR the first span is added to the queue after the previous
  export timer ends or previous batch completes.
- The queue contains `maxExportBatchSize` or more spans.
- `ForceFlush` is called.

If the queue is empty when an export is triggered, the processor MAY export
an empty batch OR skip the export and consider it to be completed immediately.

**Configurable parameters:**

* `exporter` - the exporter where the spans are pushed.
* `maxQueueSize` - the maximum queue size. After the size is reached spans are
  dropped. The default value is `2048`.
* `scheduledDelayMillis` - the maximum delay interval in milliseconds between two
  consecutive exports. The default value is `5000`.
* `exportTimeoutMillis` - how long the export can run before it is cancelled.
  The default value is `30000`.
* `maxExportBatchSize` - the maximum batch size of every export. It must be
  smaller or equal to `maxQueueSize`. If the queue reaches `maxExportBatchSize`
  a batch will be exported even if `scheduledDelayMillis` milliseconds have not
  elapsed. The default value is `512`.

## Span Exporter

`Span Exporter` defines the interface that protocol-specific exporters must
implement so that they can be plugged into OpenTelemetry SDK and support sending
of telemetry data.

The goal of the interface is to minimize burden of implementation for
protocol-dependent telemetry exporters. The protocol exporter is expected to be
primarily a simple telemetry data encoder and transmitter.

Each implementation MUST document the concurrency characteristics the SDK
requires of the exporter.

### Interface Definition

The exporter MUST support three functions: **Export**, **Shutdown**, and **ForceFlush**.
In strongly typed languages typically there will be one separate `Exporter`
interface per signal (`SpanExporter`, ...).

#### `Export(batch)`

Exports a batch of [readable spans](#additional-span-interfaces).
Protocol exporters that will implement this
function are typically expected to serialize and transmit the data to the
destination.

Export() should not be be called concurrently with other `Export` calls for the
same exporter instance.

Depending on the implementation the result of the export may be returned to the
Processor not in the return value of the call to Export() but in a language
specific way for signaling completion of an asynchronous task. This means that
while an instance of an exporter should never have its Export() called
concurrently it does not mean that the task of exporting can not be done
concurrently. How this is done is outside the scope of this specification.

Export() MUST NOT block indefinitely, there MUST be a reasonable upper limit
after which the call must time out with an error result (`Failure`).

Concurrent requests and retry logic is the responsibility of the exporter. The
default SDK's Span Processors SHOULD NOT implement retry logic, as the required
logic is likely to depend heavily on the specific protocol and backend the spans
are being sent to. For example, the [OpenTelemetry Protocol (OTLP)
specification](../protocol/otlp.md)
defines logic for both sending concurrent requests and retrying requests.

**Parameters:**

batch - a batch of [readable spans](#additional-span-interfaces). The exact data type of the batch is language
specific, typically it is some kind of list,
e.g. for spans in Java it will be typically `Collection<SpanData>`.

**Returns:** ExportResult:

The return of Export() is implementation specific. In what is idiomatic for the
language the Exporter must send an `ExportResult` to the Processor.
`ExportResult` has values of either `Success` or `Failure`:

* `Success` - The batch has been successfully exported.
  For protocol exporters this typically means that the data is sent over
  the wire and delivered to the destination server.
* `Failure` - exporting failed. The batch must be dropped. For example, this
  can happen when the batch contains bad data and cannot be serialized.

For example, in Java the return of Export() would be a Future which when
completed returns the `ExportResult` object. While in Erlang the Exporter sends
a message to the Processor with the `ExportResult` for a particular batch of
spans.

#### `Shutdown()`

Shuts down the exporter. Called when SDK is shut down. This is an opportunity
for exporter to do any cleanup required.

`Shutdown` should be called only once for each `Exporter` instance. After the
call to `Shutdown` subsequent calls to `Export` are not allowed and should
return a `Failure` result.

`Shutdown` should not block indefinitely (e.g. if it attempts to flush the data
and the destination is unavailable). OpenTelemetry client authors can decide if they
want to make the shutdown timeout configurable.

#### `ForceFlush()`

This is a hint to ensure that the export of any `Spans` the exporter has received prior to the
call to `ForceFlush` SHOULD be completed as soon as possible, preferably before
returning from this method.

`ForceFlush` SHOULD provide a way to let the caller know whether it succeeded,
failed or timed out.

`ForceFlush` SHOULD only be called in cases where it is absolutely necessary,
such as when using some FaaS providers that may suspend the process after an
invocation, but before the exporter exports the completed spans.

`ForceFlush` SHOULD complete or abort within some timeout. `ForceFlush` can be
implemented as a blocking API or an asynchronous API which notifies the caller
via a callback or an event. OpenTelemetry client authors can decide if they want to
make the flush timeout configurable.

### Further Language Specialization

Based on the generic interface definition laid out above library authors must
define the exact interface for the particular language.

Authors are encouraged to use efficient data structures on the interface
boundary that are well suited for fast serialization to wire formats by protocol
exporters and minimize the pressure on memory managers. The latter typically
requires understanding of how to optimize the rapidly-generated, short-lived
telemetry data structures to make life easier for the memory manager of the
specific language. General recommendation is to minimize the number of
allocations and use allocation arenas where possible, thus avoiding explosion of
allocation/deallocation/collection operations in the presence of high rate of
telemetry data generation.

#### Examples

These are examples on what the `Exporter` interface can look like in specific
languages. Examples are for illustration purposes only. OpenTelemetry client authors
are free to deviate from these provided that their design remain true to the
spirit of `Exporter` concept.

##### Go SpanExporter Interface

```go
type SpanExporter interface {
    Export(batch []ExportableSpan) ExportResult
    Shutdown()
}

type ExportResult struct {
    Code         ExportResultCode
    WrappedError error
}

type ExportResultCode int

const (
    Success ExportResultCode = iota
    Failure
)
```

##### Java SpanExporter Interface

```java
public interface SpanExporter {
 public enum ResultCode {
   Success, Failure
 }

 ResultCode export(Collection<ExportableSpan> batch);
 void shutdown();
}
```
