# Sampling API

## TL;DR

This section tries to summarize all the changes proposed in this RFC:

 1. Move the `Sampler` interface from the API to SDK package. Apply some minor changes to the
 `Sampler` API.
 2. Add capability to record `Attributes` that can be used for sampling decision during the `Span`
 creation time.
 3. Remove `addLink` APIs from the `Span` interface, and allow recording links only during the span
 construction time.

## Motivation

Different users of OpenTelemetry, ranging from library developers, packaged infrastructure binary
developers, application developers, operators, and telemetry system owners, have separate use cases
for OpenTelemetry that have gotten muddled in the design of the original Sampling API. Thus, we need
to clarify what APIs each should be able to depend upon, and how they will configure sampling and
OpenTelemetry according to their needs.

```

                    +----------+           +-----------+
           grpc     |  Library |           |           |
           Django   |  Devs    +---------->| OTel API  |
           Express  |          |   +------>|           |
                    +----------+   |  +--->+-----------+                  +---------+
                                   |  |          ^                        | OTel    |
                                   |  |          |                     +->| Proxy   +---+
                                   |  |          |                     |  |         |   |
                    +----------+   |  |    +-----+-----+------------+  |  +---------+   |
                    |          |   |  |    |           | OTel Wire  |  |                |
           Hbase    |  Infra   |   |  |    |           | Export     |+-+                v
           Envoy    |  Binary  +---+  |    |  OTel     |            |  |           +----v-----+
                    |  Devs    |      |    |  SDK      +------------+  |           |          |
                    +----------+---------->|           |            |  +---------->|  Backend |
                                   +------>|           | Custom     |  +---------->|          |
                                   |  |    |           | Export     |  |           +----------+
                    +----------+   |  |    |           |            |+-+             ^
                    |          +---+  |    +-----------+------------+                |
                    |  App     +------+       ^              ^                       |
                    |  Devs    +              |              |          +------------+-+
                    |          |              |              |          |              |
                    +----------+          +---+----+         +----------+   Telemetry  |
                                          |  SRE   |                    |   Owner      |
                                          |        |                    |              |
                                          +--------+                    +--------------+
                                                                          Lightstep
                                                                          Honeycomb

```

## Explanation

We outline five different use cases (who may be overlapping sets of people), and how they should
interact with OpenTelemetry:

### Library developer

Examples: gRPC, Express, Django developers.

* They must only depend upon the OpenTelemetry API and not upon the SDK.
  * For testing only they may depend on the SDK with InMemoryExporter.
* They are shipping source code that will be linked into others' applications.
* They have no explicit runtime control over the application.
* They know some signal about what traces may be interesting (e.g. unusual control plane requests)
 or uninteresting (e.g. health-checks), but have to write fully generically.

**Solution:**

* For the moment, the OpenTelemetry API will not offer any `SamplingHint` functionality for the last use case.
This is intentional to avoid premature optimizations, and it is based on the fact that changing an API is
backwards incompatible compared to adding a new API.

### Infrastructure package/binary developer

Examples: HBase, Envoy developers.

* They are shipping self-contained binaries that may accept YAML or similar runtime configuration,
 but are not expected to support extensibility/plugins beyond the default OpenTelemetry SDK,
 OpenTelemetry SDKTracer, and OpenTelemetry wire format exporter.
* They may have their own recommendations for sampling rates, but don't run the binaries in
 production, only provide packaged binaries. So their sampling rate configs, and sampling strategies
 need to be a finite "built-in" set from OpenTelemetry's SDK.
* They need to deal with upstream sampling decisions made by services that call them.

**Solution:**

* Allow different sampling strategies by default in OpenTelemetry SDK, all configurable easily via
 YAML or feature flags. See [default samplers](#default-samplers).

### Application developer

These are the folks we've been thinking the most about for OpenTelemetry in general.

* They have full control over the OpenTelemetry implementation or SDK configuration. When using the
 SDK they can configure custom exporters, custom code/samplers, etc.
* They can choose to implement runtime configuration via a variety of means (e.g. baking in feature
 flags, reading YAML files, etc.), or even configure the library in code.
* They make heavy usage of OpenTelemetry for instrumenting application-specific behavior, beyond
 what may be provided by the libraries they use such as gRPC, Django, etc.

**Solution:**

* Allow application developers to link in custom samplers or write their own when using the
 official SDK.
  * These might include dynamic per-field sampling to achieve a target rate
   (e.g. <https://github.com/honeycombio/dynsampler-go>)
* Sampling decisions are made within the start Span operation, after attributes relevant to the
 span have been added to the Span start operation but before a concrete Span object exists (so that
 either a NoOpSpan can be made, or an actual Span instance can be produced depending upon the
 sampler's decision).
* Span.IsRecording() needs to be present to allow costly span attribute/log computation to be
 skipped if the span is a NoOp span.

### Application operator

Often the same people as the application developers, but not necessarily

* They care about adjusting sampling rates and strategies to meet operational needs, debugging,
 and cost.

**Solution:**

* Use config files or feature flags written by the application developers to control the
 application sampling logic.
* Use the config files to configure libraries and infrastructure package behavior.

### Telemetry infrastructure owner

They are the people who provide an implementation for the OpenTelemetry API by using the SDK with
custom `Exporter`s, `Sampler`s, hooks, etc. or by writing a custom implementation, as well as
running the infrastructure for collecting exported traces.

* They care about a variety of things, including efficiency, cost effectiveness, and being able to
 gather spans in a way that makes sense for them.

**Solution:**

* Infrastructure owners receive information attached to the span, after sampling hooks have already
 been run.

## Internal details

In Dapper based systems (or systems without a deferred sampling decision) all exported spans are
stored to the backend, thus some of these systems usually don't scale to a high volume of traces,
or the cost to store all the Spans may be too high. In order to support this use-case and to
ensure the quality of the data we send, OpenTelemetry needs to natively support sampling with some
requirements:

* Send as many complete traces as possible. Sending just a subset of the spans from a trace is
 less useful because in this case the interaction between the spans may be missing.
* Allow application operator to configure the sampling frequency.

For new modern systems that need to collect all the Spans and later may or may not make a deferred
sampling decision, OpenTelemetry needs to natively support a way to configure the library to
collect and export all the Spans. This is possible (even though OpenTelemetry supports sampling) by
setting a default config to always collect all the spans.

### Sampling flags

OpenTelemetry API has two flags/properties:

* `RecordEvents`
  * This property is exposed in the `Span` interface (e.g. `Span.isRecordingEvents()`).
  * If `true` the current `Span` records tracing events (attributes, events, status, etc.),
   otherwise all tracing events are dropped.
  * Users can use this property to determine if expensive trace events can be avoided.
* `SampledFlag`
  * This flag is propagated via the `TraceOptions` to the child Spans (e.g.
   `TraceOptions.isSampled()`). For more details see the W3C definition [here][trace-flags].
  * In Dapper based systems this is equivalent to `Span` being `sampled` and exported.

The flag combination `SampledFlag == false` and `RecordEvents == true` means that the current `Span`
does record tracing events, but most likely the child `Span` will not. This combination is
necessary because:

* Allow users to control recording for individual Spans.
* OpenCensus has this to support z-pages, so we need to keep backwards compatibility.

The flag combination `SampledFlag == true` and `RecordEvents == false` can cause gaps in the
distributed trace, and because of this OpenTelemetry API should NOT allow this combination.

It is safe to assume that users of the API should only access the `RecordEvents` property when
instrumenting code and never access `SampledFlag` unless used in context propagators.

### Sampler interface

The interface for the Sampler class that is available only in the OpenTelemetry SDK:

* `TraceID`
* `SpanID`
* Parent `SpanContext` if any
* `Links`
* Span name
* `SpanKind`
* Initial set of `Attributes` for the `Span` being constructed

It produces an output called `SamplingResult` that includes:

* A `SamplingDecision` enum [`NOT_RECORD`, `RECORD`, `RECORD_AND_PROPAGATE`].
* A set of span Attributes that will also be added to the `Span`.
  * These attributes will be added after the initial set of `Attributes`.
* (under discussion in separate RFC) the SamplingRate float.

### Default Samplers

These are the default samplers implemented in the OpenTelemetry SDK:

* ALWAYS_ON
* ALWAYS_OFF
* ALWAYS_PARENT
  * Trust parent sampling decision (trusting and propagating parent `SampledFlag`).
  * For root Spans (no parent available) returns `NOT_RECORD`.
* Probability
  * Allows users to configure to ignore the parent `SampledFlag`.
  * Allows users to configure if probability applies only for "root spans", "root spans and remote
   parent", or "all spans".
    * Default is to apply only for "root spans and remote parent".
    * Remote parent property should be added to the SpanContext see specs [PR/216][specs-pr-216]
  * Sample with 1/N probability

**Root Span Decision:**

|Sampler|RecordEvents|SampledFlag|
|---|---|---|
|ALWAYS_ON|`True`|`True`|
|ALWAYS_OFF|`False`|`False`|
|ALWAYS_PARENT|`False`|`False`|
|Probability|`Same as SampledFlag`|`Probability`|

**Child Span Decision:**

|Sampler|RecordEvents|SampledFlag|
|---|---|---|
|ALWAYS_ON|`True`|`True`|
|ALWAYS_OFF|`False`|`False`|
|ALWAYS_PARENT|`ParentSampledFlag`|`ParentSampledFlag`|
|Probability|`Same as SampledFlag`|`ParentSampledFlag OR Probability`|

### Links

This RFC proposes that Links will be recorded only during the start `Span` operation, because:

* Link's `SampledFlag` can be used in the sampling decision.
* OpenTracing supports adding references only during the `Span` creation.
* OpenCensus supports adding links at any moment, but this was mostly used to record child Links
which are not supported in OpenTelemetry.
* Allowing links to be recorded after the sampling decision is made will cause samplers to not
work correctly and unexpected behaviors for sampling.

### When does sampling happen

The sampling decision will happen before a real `Span` object is returned to the user, because:

* If child spans are created they need to know the 'SampledFlag'.
* If `SpanContext` is propagated on the wire the 'SampledFlag' needs to be set.
* If user records any tracing event the `Span` object needs to know if the data are kept or not.
 It may be possible to always collect all the events until the sampling decision is made but this is
 an important optimization.

There are two important use-cases to be considered:

* All information that may be used for sampling decisions are available at the moment when the
 logical `Span` operation should start. This is the most common case.
* Some information that may be used for sampling decision are NOT available at the moment when the
 logical `Span` operation should start (e.g. `http.route` may be determine later).

The current [span creation logic][span-creation] facilitates the first use-case very well, but
the second use-case requires users to record the logical `start_time` and collect all the
information necessarily to start the `Span` in custom objects, then when all the properties are
available call the span creation API.

The RFC proposes that we keep the current [span creation logic][span-creation] as it is and we will
address the delayed sampling in a different RFC when that becomes a high priority.

The SDK must call the `Sampler` every time a `Span` is created during the start span operation.

**Alternatives considerations:**

* We considered, to offer a delayed span construction mechanism:
  * For languages where a `Builder` pattern is used to construct a `Span`, to allow users to
    create a `Builder` where the start time of the Span is considered when the `Builder` is created.
  * For languages where no intermediate object is used to construct a `Span`, to allow users maybe
     via a `StartSpanOption` object to start a `Span`. The `StartSpanOption` allows users to set all
     the start `Span` properties.
  * Pros:
    * Would resolve the second use-case posted above.
  * Cons:
    * We could not identify too many real case examples for the second use-case and decided to
      postpone the decision to avoid premature decisions.
* We considered, instead of requiring that sampling decision happens before the `Span` is
 created to add an explicit `MakeSamplingDecision(SamplingHint)` on the `Span`. Attempts to create
 a child `Span`, or to access the `SpanContext` would fail if `MakeSamplingDecision()` had not yet
 been run.
  * Pros:
    * Simplifies the case when all the attributes that may be used for sampling are not available
     when the logical `Span` operation should start.
  * Cons:
    * The most common case would have required an extra API call.
    * Error-prone, users may forget to call the extra API.
    * Unexpected and hard to find errors if user tries to create a child `Span` before calling
     MakeSamplingDecision().
* We considered allowing the sampling decision to be arbitrarily delayed, but guaranteed before
 any child `Span` is created, or `SpanContext` is accessed, or before `Span.end()` finished.
  * Pros:
    * Similar and smaller API that supports both use-cases defined ahead.
  * Cons:
    * If `SamplingHint` needs to also be delayed recorded then an extra API on Span is required
     to set this.
    * Does not allow optimization to not record tracing events, all tracing events MUST be
     recorded before the sampling decision is made.

## Prior art and alternatives

Prior art for Zipkin, and other Dapper based systems: all client-side sampling decisions are made at
head. Thus, we need to retain compatibility with this.

## Open questions

This RFC does not necessarily resolve the question of how to propagate sampling rate values between
different spans and processes. A separate RFC will be opened to cover this case.

## Future possibilities

In the future, we propose that library developers may be able to defer the decision on whether to
recommend the trace be sampled or not sampled until mid-way through execution;

## Related Issues

* [opentelemetry-specification/189](https://github.com/open-telemetry/opentelemetry-specification/issues/189)
* [opentelemetry-specification/187](https://github.com/open-telemetry/opentelemetry-specification/issues/187)
* [opentelemetry-specification/164](https://github.com/open-telemetry/opentelemetry-specification/issues/164)
* [opentelemetry-specification/125](https://github.com/open-telemetry/opentelemetry-specification/issues/125)
* [opentelemetry-specification/87](https://github.com/open-telemetry/opentelemetry-specification/issues/87)
* [opentelemetry-specification/66](https://github.com/open-telemetry/opentelemetry-specification/issues/66)
* [opentelemetry-specification/65](https://github.com/open-telemetry/opentelemetry-specification/issues/65)
* [opentelemetry-specification/53](https://github.com/open-telemetry/opentelemetry-specification/issues/53)
* [opentelemetry-specification/33](https://github.com/open-telemetry/opentelemetry-specification/issues/33)
* [opentelemetry-specification/32](https://github.com/open-telemetry/opentelemetry-specification/issues/32)
* [opentelemetry-specification/31](https://github.com/open-telemetry/opentelemetry-specification/issues/31)

[trace-flags]: https://github.com/w3c/trace-context/blob/main/spec/20-http_request_header_format.md#trace-flags
[specs-pr-216]: https://github.com/open-telemetry/opentelemetry-specification/pull/216
[span-creation]: https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/trace/api.md#span-creation
