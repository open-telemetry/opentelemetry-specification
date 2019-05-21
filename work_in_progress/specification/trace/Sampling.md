# Sampling

This document is about the sampling bit, sampling decision, samplers and how and when
OpenCensus samples traces. A sampled trace is one that gets exported via the configured
exporters.

## Sampling Bit (propagated via TraceOptions)

The Sampling bit is always set only at the start of a Span, using a `Sampler`

### What kind of samplers does OpenCensus support?
* `AlwaysSample` - sampler that makes a "yes" decision every time.
* `NeverSample` - sampler that makes a "no" decision every time.
* `Probability` - sampler that tries to uniformly sample traces with a given probability. When 
applied to a child `Span` of a **sampled** parent `Span`, the child `Span` keeps the sampling
decision.
* `RateLimiting` - sampler that tries to sample with a rate per time window (0.1 traces/second). 
When applied to a child `Span` of a **sampled** parent `Span`, the child `Span` keeps the sampling 
decision. For implementation details see [this](#ratelimiting-sampler-implementation-details)

### How can users control the Sampler that is used for sampling?
There are 2 ways to control the `Sampler` used when the library samples:
* Controlling the global default `Sampler` via [TraceConfig](https://github.com/census-instrumentation/opencensus-specs/blob/master/trace/TraceConfig.md).
* Pass a specific `Sampler` when starting the [Span](https://github.com/census-instrumentation/opencensus-specs/blob/master/trace/Span.md)
(a.k.a. "span-scoped").
  * For example `AlwaysSample` and `NeverSample` can be used to implement request-specific 
  decisions such as those based on http paths.

### When does OpenCensus sample traces?
The OpenCensus library samples based on the following rules:
1. If the span is a root `Span`, then a `Sampler` will be used to make the sampling decision:
   * If a "span-scoped" `Sampler` is provided, use it to determine the sampling decision.
   * Else use the global default `Sampler` to determine the sampling decision.
2. If the span is a child of a remote `Span` the sampling decision will be:
   * If a "span-scoped" `Sampler` is provided, use it to determine the sampling decision.
   * Else use the global default `Sampler` to determine the sampling decision.
3. If the span is a child of a local `Span` the sampling decision will be:
   * If a "span-scoped" `Sampler` is provided, use it to determine the sampling decision.
   * Else keep the sampling decision from the parent.

### RateLimiting sampler implementation details
The problem we are trying to solve is:
1. Getting QPS based sampling.
2. Providing real sampling probabilities.
3. Minimal overhead.

Idea is to store the time that we last made a QPS based sampling decision in an atomic. Then we can
use the elapsed time Z since the coin flip to weight our current coin flip. We choose our
probability function P(Z) such that we get the desired sample QPS. We want P(Z) to be very
cheap to compute.

Let X be the desired QPS. Let Z be the elapsed time since the last sampling decision in seconds.
```
P(Z) = min(Z * X, 1)
```

To see that this is approximately correct, consider the case where we have perfectly distributed
time intervals. Specifically, let X = 1 and Z = 1/N. Then we would have N coin flips per second,
each with probability 1/N, for an expectation of 1 sample per second.

This will under-sample: consider the case where X = 1 and Z alternates between 0.5 and 1.5. It is
possible to get about 1 QPS by always sampling, but this algorithm only gets 0.75 QPS.
