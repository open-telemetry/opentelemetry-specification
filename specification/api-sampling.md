# Sampling API

Sampling is a mechanism to control the noise and overhead introduced by
OpenTelemetry by reducing the number of samples of traces collected and sent to
the backend.

Sampling may be implemented on different stages of a trace collection.
OpenTelemetry API defines a `Sampler` interface that can be used at
instrumentation points by libraries to check the sampling `Decision` early and
optimize the amount of telemetry that needs to be collected.

All other sampling algorithms may be implemented on SDK layer in exporters, or
even out of process in Agent or Collector.

API defines two interfaces - [`Sampler`](#sampler) and [`Decision`](#decision)
as well as a set of [built-in samplers](#built-in-samplers).

## Sampler

`Sampler` interface allows to create custom samplers which will return a
sampling `Decision` based on information that is typically available just before
the `Span` was created.

### ShouldSample

Returns the sampling Decision for a `Span` to be created.

**Required arguments:**

- `SpanContext` of a parent `Span`. Typically extracted from the wire. Can be
  `null`.
- Boolean that indicates that `SpanContext` was extracted from the wire, i.e.
  parent `Span` is from the different process.
- `TraceId` of the `Span` to be created.
- `SpanId` of the `Span` to be created.
- Name of the `Span` to be created.
- Collection of links that will be associated with the `Span` to be created.
  Typically useful for batch operations.

**Return value:**

Sampling `Decision` whether span should be sampled or not.

### GetDescription

Returns the sampler name or short description with the configuration. This may
be displayed on debug pages or in the logs. Example:
`"ProbabilitySampler{0.000100}"`.

## Decision

`Decision` is an interface with two getters describing the sampling decision.

### IsSampled

Return sampling decision whether span should be sampled or not.

### GetAttributes

Return attributes to be attached to the `Span`. These attributes should be added
to the span only for root span or when sampling decision `IsSampled` changes
from false to true.

Examples of attribute may be algorithm used to make a decision and sampling
priority. Another example may be recording the reason trace was marked as
"important" to sample in. For instance, when traces from specific user session
should be collected, session identifier can be added to attributes.

## Built-in samplers

API MUST provide a way to create the following built-in samplers:

- Always sample. `Sampler` returns `Decision` with `IsSampled=true` and empty
  arguments collection. Description MUST be `AlwaysSampleSampler`.
- Never sample. `Sampler` returns `Decision` with `IsSampled=false` and empty
  arguments collection. Description MUST be `NeverSampleSampler`.
