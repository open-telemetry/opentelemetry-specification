# Probability sampling of telemetry events

<!-- toc -->

- [Motivation](#motivation)
- [Examples](#examples)
  * [Span sampling](#span-sampling)
    + [Sample spans to Counter Metric](#sample-spans-to-counter-metric)
    + [Sample spans to Histogram Metric](#sample-spans-to-histogram-metric)
    + [Sample span rate limiting](#sample-span-rate-limiting)
- [Explanation](#explanation)
  * [Model and terminology](#model-and-terminology)
    + [Sampling without replacement](#sampling-without-replacement)
    + [Adjusted sample count](#adjusted-sample-count)
    + [Sampling and variance](#sampling-and-variance)
  * [Conveying the sampling probability](#conveying-the-sampling-probability)
    + [Encoding adjusted count](#encoding-adjusted-count)
    + [Encoding inclusion probability](#encoding-inclusion-probability)
    + [Encoding base-2 logarithm of adjusted count](#encoding-base-2-logarithm-of-adjusted-count)
    + [Multiply the adjusted count into the data](#multiply-the-adjusted-count-into-the-data)
  * [Trace Sampling](#trace-sampling)
    + [Counting child spans using root span adjusted counts](#counting-child-spans-using-root-span-adjusted-counts)
    + [Using parent sampling probability to count all spans](#using-parent-sampling-probability-to-count-all-spans)
    + [Parent sampling for traces](#parent-sampling-for-traces)
      - [`Parent` Sampler](#parent-sampler)
      - [`TraceIDRatio` Sampler](#traceidratio-sampler)
      - [Dapper's "Inflationary" Sampler](#dappers-inflationary-sampler)
- [Proposed `Span` protocol](#proposed-span-protocol)
  * [Span data model changes](#span-data-model-changes)
  * [Proposed `Sampler` composition rules](#proposed-sampler-composition-rules)
    + [Composing two consistent probability samplers](#composing-two-consistent-probability-samplers)
    + [Composing a probability sampler and a non-probability sampler](#composing-a-probability-sampler-and-a-non-probability-sampler)
    + [Composition rules summary](#composition-rules-summary)
  * [Proposed `Sampler` interface changes](#proposed-sampler-interface-changes)
- [Recommended reading](#recommended-reading)
- [Acknowledgements](#acknowledgements)

<!-- tocstop -->

Objective: Specify a foundation for sampling techniques in OpenTelemetry.

## Motivation

Probability sampling allows consumers of sampled telemetry data to
collect a fraction of telemetry events and use them to estimate total
quantities about the population of events, such as the total rate of
events with a particular attribute.

These techniques enable reducing the cost of telemetry collection,
both for producers (i.e., SDKs) and for processors (i.e., Collectors),
without losing the ability to (at least coarsely) monitor the whole
system.

Sampling builds on results from probability theory.  Estimates drawn
from probability samples are *random variables* that are expected to
equal their true value.  When all outcomes are equally likely, meaning
all the potential combinations of items used to compute a sample of
the sampling logic are equally likely, we say the sample is *unbiased*.

Unbiased samples can be used for after-the-fact analysis.  We can
answer questions such as "what fraction of events had property X?"
using the fraction of events in the sample that have property X.

This document outlines how producers and consumers of sample telemetry
data can convey estimates about the total count of telemetry events,
without conveying information about how the sample was computed, using
a quantity known as **adjusted count**.  In common language, a
"one-in-N" sampling scheme emits events with adjusted count equal to
N.  Adjusted count is the expected value of the number of events in
the population represented by an individual sample event.

## Examples

These examples use an attribute named `sampler.adjusted_count` to
convey sampling probability.  Consumers of spans, metrics, and logs
annotated with adjusted counts are able to calculate accurate
statistics about the whole population of events, without knowing
details about the sampling configuration.

The hypothetical `sampler.adjusted_count` attribute is used throughout
these examples to demonstrate this concept, although the proposal
below for OpenTelemetry `Span` messages introduces a dedicated field
with specific interpretation for conveying parent sampling probability.

### Span sampling

Example use-cases for probability sampling of spans generally involve
generating metrics from spans.

#### Sample spans to Counter Metric

In this example, an OpenTelemetry SDK for tracing is configured with a
`SpanProcessor` that counts sample spans as they are processed based
on their adjusted counts.  The SDK could be used to monitor request
rates using Prometheus, for example.

For every complete sample span it receives, the example
`SpanProcessor` will synthesize metric data as though a Counter named
`S_count` corresponding to a span named `S` had been incremented once
per original span.  Using the adjusted count of sampled spans instead,
the value of `S_count` is expected to equal to equal the true number
of spans.

This `SpanProcessor` will for every span it receives add the span's
adjusted count to a corresponding metric Counter instrument.  For
example using the OpenTelemetry Metrics API directly,

```
func (p *spanToMetricsProcessor) OnEnd(span trace.ReadOnlySpan) {
    ctx := context.Background()
    counter := p.meter.NewInt64Counter(span.Name() + "_count")
    counter.Add(
        ctx,
        span.AdjustedCount(),
        span.Attributes()...,
            )
}
```

#### Sample spans to Histogram Metric

For every span it receives, the example processor will synthesize
metric data as though a Histogram instrument named `S_duration` for
span named `S` had been observed once per original span.

The OpenTelemetry Metric data model does not support histogram buckets
with non-integer counts, which forces the use of integer adjusted
counts here (i.e., 1-in-N sampling rates where N is an integer).

Logically speaking, this processor will observe the span's duration
*adjusted count* number of times for every sample span it receives.
This example, therefore, uses a hypothetical `RecordMany()` method to
capture multiple observations of a Histogram measurement at once:

```
    histogram := p.meter.NewFloat64Histogram(
        span.Name() + "_duration",
        metric.WithUnits("ms"),
    )
    histogram.RecordMany(
        ctx,
        span.Duration().Milliseconds(),
        span.AdjustedCount(),
        span.Attributes()...,
    )
```

#### Sample span rate limiting

A collector processor will introduce a slight delay in order to ensure
it has received a complete frame of data, during which time it
maintains a fixed-size buffer of complete input spans.  If the number of spans
received exceeds the size of the buffer before the end of the
interval, begin weighted sampling using the adjusted count of each
span as input weight.

This processor drops spans when the configured rate threshold is
exceeeded, otherwise it passes spans through with unmodifed adjusted
counts.

When the interval expires and the sample frame is considered complete,
the selected sample spans are output with possibly updated adjusted
counts.

## Explanation

Consider a hypothetical telemetry signal in which a stream of
data items is produced containing one or more associated numbers.
Using the OpenTelemetry Metrics data model terminology, we have two
scenarios in which sampling is common.

1. *Counter events:* Each event represents a count, signifying the change in a sum.
2. *Histogram events:* Each event represents an individual variable, signifying membership in a distribution.

A Tracing Span event qualifies as both of these cases simultaneously.
One span can be interpreted as at least one Counter event (e.g., one
request, the number of bytes read) and at least one Histogram event
(e.g., request latency, request size).

In Metrics, [Statsd Counter and Histogram events meet this definition](https://github.com/statsd/statsd/blob/master/docs/metric_types.md#sampling).

In both cases, the goal in sampling is to estimate the count of events
in the whole population, meaning all the events, using only the events
that were selected in the sample.

### Model and terminology

This model is meant to apply in telemetry collection situations where
individual events at an API boundary are sampled for collection.  Once
the process of sampling individual API-level events is understood, we
will learn to apply these techniques for sampling aggregated data.

In sampling, the term *sampling design* refers to how sampling
probability is decided and the term *sample frame* refers to how
events are organized into discrete populations.  The design of a
sampling strategy dictates how the population is framed.

For example, a simple design uses uniform probability, and a simple
framing technique is to collect one sample per distinct span name per
hour.  A different sample framing could collect one sample across all
span names every 10 minutes.

After executing a sampling design over a frame, each item selected in
the sample will have known *inclusion probability*, that determines
how likely the item was to being selected.  Implicitly, all the items
that were not selected for the sample have zero inclusion probability.

Descriptive words that are often used to describe sampling designs:

- *Fixed*: the sampling design is the same from one frame to the next
- *Adaptive*: the sampling design changes from one frame to the next based on the observed data
- *Equal-Probability*: the sampling design uses a single inclusion probability per frame
- *Unequal-Probability*: the sampling design uses multiple inclusion probabilities per frame
- *Reservoir*: the sampling design uses fixed space, has fixed-size output.

Our goal is to support flexibility in choosing sampling designs for
producers of telemetry data, while allowing consumers of sampled
telemetry data to be agnostic to the sampling design used.

#### Sampling without replacement

We are interested in the common case in telemetry collection, where
sampling is performed while processing a stream of events and each
event is considered just once.  Sampling designs of this form are
referred to as *sampling without replacement*.  Unless stated
otherwise, "sampling" in telemetry collection always refers to
sampling without replacement.

After executing a given sampling design over a complete frame of data,
the result is a set of selected sample events, each having known and
non-zero inclusion probability.  There are several other quantities of
interest, after calculating a sample from a sample frame.

- *Sample size*: the number of events with non-zero inclusion probability
- *True population total*: the exact number of events in the frame, which may be unknown
- *Estimated population total*: the estimated number of events in the frame, which is computed from the sample.

The sample size is always known after it is calculated, but the size
may or may not be known ahead of time, depending on the design.
Probabilistic sampling schemes require that the estimated population
total equals the expected value of the true population total.

#### Adjusted sample count

Following the model above, every event defines the notion of an
*adjusted count*.

- *Adjusted count* is zero if the event was not selected for the sample
- *Adjusted count* is the reciprocal of its inclusion probability, otherwise.

The adjusted count of an event represents the expected contribution to
the estimated population total of a sample frame represented by the
individual event.

The use of a reciprocal inclusion probability matches our intuition
for probabilities.  Items selected with "one-out-of-N" probability of
inclusion count for N each, approximately speaking.

This intuition is backed up with statistics.  This equation is known
as the Horvitz-Thompson estimator of the population total, a
general-purpose statistical "estimator" that applies to all *without
replacement* sampling designs.

Assuming sample data is correctly computed, the consumer of sample
data can treat every sample event as though an identical copy of
itself has occurred *adjusted count* times.  Every sample event is
representative for adjusted count many copies of itself.

There is one essential requirement for this to work.  The selection
procedure must be *statistically unbiased*, a term meaning that the
process is required to give equal consideration to all possible
outcomes.

#### Sampling and variance

The use of unbiased sampling outlined above makes it possible to
estimate the population total for arbitrary subsets of the sample, as
every individual sample has been independently assigned an adjusted
count.

There is a natural relationship between statistical bias and variance.
Approximate counting comes with variance, a matter of fact which can
be controlled for by the sample size.  Variance is unavoidable in an
unbiased sample, but variance diminishes with increasing sample size.

Although this makes it sound like small sample sizes are a problem,
due to expected high variance, this is just a limitation of the
technique.  When variance is high, use a larger sample size.

An easy approach for lowering variance is to aggregate sample frames
together across time, which generally increases the size of the
subpopulations being counted.  For example, although the estimates for
the rate of spans by distinct name drawn from a one-minute sample may
have high variance, combining an hour of one-minute sample frames into
an aggregate data set is guaranteed to lower variance (assuming the
numebr of span names stays fixed).  It must, because the data remains
unbiased, so more data results in lower variance.

### Conveying the sampling probability

Some possibilities for encoding the adjusted count or inclusion
probability are discussed below, depending on the circumstances and
the protocol.  Here, the focus is on how to count sampled telemetry
events in general, not a specific kind of event.  As we shall see in
the following section, tracing comes with additional complications.

There are several ways of encoding this adjusted count or inclusion
probability:

- as a dedicated field in an OTLP protobuf message
- as a non-descriptive Attribute in an OTLP Span, Metric, or Log
- without any dedicated field.

#### Encoding adjusted count

We can encode the adjusted count directly as a floating point or
integer number in the range [0, +Inf).  This is a conceptually easy
way to understand sampling because larger numbers mean greater
representivity.

Note that it is possible, given this description, to produce adjusted
counts that are not integers.  Adjusted counts are an approximatation,
and the expected value of an integer can be a fractional count.
Floating-point adjusted counts can be avoided with the use of
integer-reciprocal inclusion probabilities.

#### Encoding inclusion probability

We can encode the inclusion probability directly as a floating point
number in the range [0, 1).  This is typical of the Statsd format,
where each line includes an optional probability.  In this context,
the probability is also commonly referred to as a "sampling rate".  In
this case, smaller numbers mean greater representivity.

#### Encoding base-2 logarithm of adjusted count

We can encode the base-2 logarithm of adjusted count (i.e., negative
base-2 logarithm of inclusion probability).  By using an integer
field, restricting adjusted counts and inclusion probabilities to
powers of two, this allows the use of small non-negative integers to
encode the adjusted count.  In this case, larger numbers mean
exponentially greater representivity.

#### Multiply the adjusted count into the data

When the data itself carries counts, such as for the Metrics Sum and
Histogram points, the adjusted count can be multiplied into the data.

This technique is less desirable because, while it preserves the
expected value of the count or sum, the data loses information about
variance.  This may also lead to rounding errors, when adjusted counts
are not integer valued.

### Trace Sampling

Sampling techniques are always about lowering the cost of data
collection and analysis, but in trace collection and analysis
specifically, approaches can be categorized by whether they reduce
Tracer overhead.  Tracer overhead is reduced by not recording spans
for unsampled traces and requires making the sampling decision at the
time a new span context is created, sometimes before all of its
attributes are known.

Traces are said to be complete when the all spans that were part of
the trace are collected.  When sampling is applied to reduce Tracer
overhead, there is generally an expectation that complete traces will
still be produced.  Sampling techniques that lower Tracer overhead and
produce complete traces are known as *Head trace sampling* techniques.

The decision to produce and collect a sample trace has to be made when
the root span starts, to avoid incomplete traces.  Then, assuming
complete traces can be collected, the adjusted count of the root span
determines an adjusted count for every span in the trace.

#### Counting child spans using root span adjusted counts

The adjusted count of a root span determines the adjusted count of
each of its children based on the following logic:

- The root span is considered representative of `adjusted_count` many
  identical root spans, because it was selected using unbiased sampling
- Context propagation conveys *causation*, the fact the one span produces
  another
- A root span causes each of the child spans in its trace to be produced
- A sampled root span represents `adjusted_count` many traces, representing
  the cause of `adjusted_count` many occurrences per child span in the
  sampled trace.

Using this reasoning, we can define a sample collected from all root
spans in the system, which allows estimating the count of all spans in
the population.  Take a simple probability sample of root spans:

1. In the `Sampler` decision for root spans, use the initial span properties
   to determine the inclusion probability `P`
2. Make a pseudo-random selection with probability `P`, if true return
   `RECORD_AND_SAMPLE` (so that the W3C Trace Context `is-sampled`
   flag is set in all child contexts)
3. Encode a span adjusted count attribute equal to `1/P` on the root span
4. Collect all spans where the W3C Trace Context `is-sampled` flag is set.

After collecting all sampled spans, locate the root span for each.
Apply the root span's adjusted count to every child in the associated
trace.  The sum of adjusted counts on all sampled spans is expected to
equal the population total number of spans.

Now, having stored the sample spans with their adjusted counts, and
assuming the source of randomness is good, we can extrapolate counts
for the population using arbitrary queries over the sampled spans.
Sampled spans can be translated into approximate metrics over the
population of spans, after their adjusted counts are known.

The cost of this analysis, using only the root span's adjusted count,
is that all root spans have to be collected before we can count
non-root spans.  The cost of indexing and looking up the root span
adjusted counts makes this analysis relatively expensive to perform in
real time.

#### Using parent sampling probability to count all spans

If the W3C `is-sampled` flag will be used to determine whether
`RECORD_AND_SAMPLE` is returned in a Sampler, then in order to count
sample spans without first locating the root span requires propagating
information about the parent sampling probability through the
context.  Using the parent sampling probability, instead of the
root, allows individual spans in a trace to control the sampling
probability of their descendents in a sub-trace that use `ParentBased`
sampler.  Such techniques are referred to as *parent sampling*
techniques.

Parent sampling probability may be thought of as the probability
of causing a child span to be a sampled.  Propagators that maintain
this variable MUST obey the rules of conditional probability.  In this
model, the adjusted count of each span depends on the adjusted count
of its parent, not of the root in a trace.  Still, the sum of adjusted
counts of all sampled spans is expected to equal the population total
number of spans.

This applies to other forms of telemetry that happen (i.e., are
caused) within a context carrying parent sampling probability.  For
example, we may record log events and metrics exemplars with adjusted
counts equal to the inverse of the current parent sampling probability
when they are produced.

This technique allows translating spans and logs to metrics without
first locating their root span, a significant performance advantage
compared with first collecting and indexing root spans.

Several parent sampling techniques are discussed in the following
sections and evaluated in terms of their ability to meet all of the
following criteria:

- Reduces Tracer overhead
- Produces complete traces
- Spans are countable.

#### Parent sampling for traces

Details about Sampler implementations that meet
the requirements stated above.

##### `Parent` Sampler

The `Parent` Sampler ensures complete traces, provided all spans are
successfully recorded.  A downside of `Parent` sampling is that it
takes away control over Tracer overhead from non-roots in the trace.
To support real-time span-to-metrics applications, this Sampler
requires propagating the sampling probability or adjusted count of
the context in effect when starting child spans.  This is expanded
upon in [OTEP 168 (WIP)](https://github.com/open-telemetry/oteps/pull/168).

When propagating parent sampling probability, spans recorded by the
`Parent` sampler could encode the adjusted count in the corresponding
`SpanData` using a Span attribute named `sampler.adjusted_count`.

##### `TraceIDRatio` Sampler

The OpenTelemetry tracing specification includes a built-in Sampler
designed for probability sampling using a deterministic sampling
decision based on the TraceID.  This Sampler was not finished before
the OpenTelemetry version 1.0 specification was released; it was left
in place, with [a TODO and the recommendation to use it only for trace
roots](https://github.com/open-telemetry/opentelemetry-specification/issues/1413).
[OTEP 135 proposed a solution](https://github.com/open-telemetry/oteps/pull/135).

The goal of the `TraceIDRatio` Sampler is to coordinate the tracing
decision, but give each service control over Tracer overhead.  Each
service sets its sampling probability independently, and the
coordinated decision ensures that some traces will be complete.
Traces are complete when the TraceID ratio falls below the minimum
Sampler probability across the whole trace.  Techniques have been
developed for [analysis of partial traces that are compatible with
TraceID ratio sampling](https://arxiv.org/pdf/2107.07703.pdf).

The `TraceIDRatio` Sampler has another difficulty with testing for
completeness.  It is impossible to know whether there are missing leaf
spans in a trace without using external information.  One approach,
[lost in the transition from OpenCensus to OpenTelemetry is to count
the number of children of each
span](https://github.com/open-telemetry/opentelemetry-specification/issues/355).

Lacking the number of expected children, we require a way to know the
minimum Sampler probability across traces to ensure they are complete.

To count TraceIDRatio-sampled spans, each span could encode its
adjusted count in the corresponding `SpanData` using a Span attribute
named `sampler.adjusted_count`.

##### Dapper's "Inflationary" Sampler

Google's [Dapper](https://research.google/pubs/pub36356/) tracing
system describes the use of sampling to control the cost of trace
collection at scale.  Dapper's early Sampler algorithm, referred to as
an "inflationary" approach (although not published in the paper), is
reproduced here.

This kind of Sampler allows non-root spans in a trace to raise the
probability of tracing, using a conditional probability formula shown
below.  Traces produced in this way are complete sub-trees, not
necessarily complete.  This technique is successful especially in
systems where a high-throughput service on occasion calls a
low-throughput service.  Low-throughput services are meant to inflate
their sampling probability.

The use of this technique requires propagating the parent inclusion
probability (as discussed for the `Parent` sampler) of the incoming
Context and whether it was sampled, in order to calculate the
probability of starting to sample a new "sub-root" in the trace.

Using standard notation for conditional probability, `P(x)` indicates
the probability of `x` being true, and `P(x|y)` indicates the
probability of `x` being true given that `y` is true.  The axioms of
probability establish that:

```
P(x)=P(x|y)*P(y)+P(x|not y)*P(not y)
```

The variables are:

- **`H`**: The parent inclusion probability of the parent context that
  is in effect, independent of whether the parent context was sampled
- **`I`**: The inflationary sampling probability for the span being
  started.
- **`D`**: The decision probability for whether to start a new sub-root.

This Sampler cannot lower sampling probability, so if the new span is
started with `H >= I` or when the context is already sampled, no new
sampling decisions are made.  If the incoming context is already
sampled, the adjusted count of the new span is `1/H`.

Assuming `H < I` and the incoming context was not sampled, we have the
following probability equations:

```
P(span sampled) = I
P(parent sampled) = H
P(span sampled | parent sampled) = 1
P(span sampled | parent not sampled) = D
```

Using the formula above,

```
I = 1*H + D*(1-H)
```

solve for D:

```
D = (I - H) / (1 - H)
```

Now the Sampler makes a decision with probability `D`.  Whether the
decision is true or false, propagate `I` as the new parent inclusion
probability.  If the decision is true, begin recording a sub-rooted
trace with adjusted count `1/I`.

## Proposed `Span` protocol

Following the proposal for propagating consistent parent sampling
probability developed in [OTEP
168](https://github.com/open-telemetry/oteps/pull/168), this proposal
is limited to adding a field to encode the parent sampling probability.
The OTEP 168 proposal for propagation limits parent sampling
probabilities to powers of two, hence we are able to encode the
corresponding adjusted count using a small non-negative integer.

The OpenTelemetry Span protocol already includes the Span's
`tracestate`, which allows consumers to calculate the adjusted count
of the span by applying the rules specified that proposal to calculate
the parent sampling probability.

The OTEP 168 proposal for propagating parent sampling probability uses 6
bits of information, with 63 ordinary values and a special zero value.
When `tracestate` is empty, the `ot` subkey cannot be found, or the
`p` value cannot be determined, the parent sampling probability is
considered unknown.

| Value | Parent Adjusted Count |
| ----- | ----------------      |
| 0     | 1                     |
| 1     | 2                     |
| 2     | 4                     |
| 3     | 8                     |
| 4     | 16                    |
| ...   | ...                   |
| X     | 2**X                  |
| ...   | ...                   |
| 62    | 2**62                 |
| 63    | 0                     |

Combined with the proposal for propagating parent sampling probability
in OTEP 168, the result is that Sampling can be enabled in an
up-to-date system and all Spans, roots and children alike, will have
known adjusted count.  Consumers of a stream of Span data with the
OTEP 168 `tracestate` value can approximately and accurately count
Spans by their adjusted count.

### Span data model changes

Addition to the Span data model:

```
### Definitions Used in this Document

#### Sampler

A Sampler provides configurable logic, used by the SDK, for selecting
which Spans are "recorded" and/or "sampled" in a tracing client
library.  To "record" a span means to build a representation of it in
the client's memory, which makes it eligible for being exported.  To
"sample" a span implies setting the W3C `sampled` flag and recording
the span for export.

OpenTelemetry supports spans that are "recorded" and not "sampled"
for "live" observability of spans (e.g., z-pages).

The Sampler interface and the built-in Samplers defined by OpenTelemetry 
must be capable of deciding immediately whether to sample the child
context.  The term "sampling" may be used in a more general sense.  
For example, a reservoir sampling scheme limits the rate of sample items 
selected over a period of time, but such a scheme necessarily defers its 
decision making, thus "Sampling" may be applied anywhere on a collection 
path whereas the "Sampler" API is restricted to logic that can immediately
decide to sample a trace in side an OpenTelemetry SDK.

#### Parent-based sampling

A Sampler that makes its decision to sample based on the W3C `sampled`
flag is said to use parent-based sampling.

#### Parent sampling

In a tracing context, Parent sampling refers to the initial decision to
sample a span or a trace, which determines the W3C `sampled` flag of
the child context.  The OpenTelemetry tracing data model currently
supports only parent sampling.

#### Probability sampler

A probability Sampler is a Sampler that knows immediately, for each
of its decisions, the probability that the span had of being selected.

Sampling probability is defined as a number less than or equal to 1
and greater than 0 (i.e., `0 < probability <= 1`).  The case of 0
probability is treated as a special, non-probabilistic case.

#### Consistent probability sampler

A consistent probability sampler is a Sampler that supports independent
sampling decisions at each span in a trace while maintaining that 
traces will be complete with probability equal to the minimum sampling 
probability across the trace.  Consistent probability sampling requires that 
for any span in a given trace, if a Sampler with lesser sampling probability 
selects the span for sampling, then the span would also be selected by a
Sampler configured with greater sampling probability.

In OpenTelemetry, consistent probability samplers are limited to 
power-of-two probabilities.  OpenTelemetry consistent probability sampling 
is defined in terms of a "p-value" and an "r-value", both of which are 
propagated via the context to assist in making consistent sampling decisions.

### Always-on sampler

An always-on sampler is another name for a consistent probability
sampler with probability equal to one.

### Always-off sampler

An always-off Sampler has the effect of disabling a span completely,
effectively excluding it from the population.  This is not defined as
a probability sampler with zero probability, because these spans are
effectively uncountable.

### Non-probability sampler

A non-probability sampler is a Sampler that makes its decisions not 
based on chance, but instead uses arbitrary logic and internal state 
to make its decisions. Because OpenTelemetry specifies the use of 
consistent probability samplers, any sampler other than a parent-based 
sampler that does not meet all the requirements for consistent probability 
sampling is termed a non-probability sampler.

#### Adjusted count

Adjusted count is defined as a measure of representivity, the number
of spans in the population that are represented by the individually
sampled span.  Span-to-metrics pipelines may be built by adding the
adjusted count of each sample span to a counter of matching spans,
observing the duration of each sample span in a histogram adjusted
count many times, and so on.

The adjusted count 1 means an one-to-one sampling was in effect.
Adjusted counts greater than 1 indicate the use of a probability
sampler.  Adjusted counts are unknown when using a non-probability
sampler.

Zero adjusted count is defined in a way to support composition of
probability and non-probability samplers.  In effect, spans that are 
"recorded" but not "sampled" have adjusted count of zero.

#### Unbiased probability sampling

The statistical term "unbiased" is a requirement applied to the
adjusted count of a span, which states that the expected value of the
sum of adjusted counts across all exported spans MUST equal the true
number of spans in the population.  Statistical bias, a measure of the
difference between an estimate and its true value, of the estimated
span count in the population should equal zero.  Moreover, this
requirement must be true for all subsets of the span population for a 
sampler to be considered an unbiased probability sampler.

It is easier to define probability sampling by what it is not.  Here
are several samplers that should be categorized as non-probability
samplers because they cannot record unbiased adjusted counts:

- A traditional form of "leaky-bucket" sampler applies a rate limit to
  the starting of new sampled traces.  When the configured limit is
  not exceeded, all spans pass through with adjusted count 1.  When
  the configured rate limit is exceeded, it is impossible to set
  adjusted count without introducing bias because future arrivals are
  not known.
- A "every-N" sampler records spans on a regular interval, but instead
  of making a probabilistic decision it makes an exact decision 
  (e.g., every 10,000 spans).  This sampler knows the representivity
  of the spans it samples, but the selection process is biased.
- A "at least once per time period" sampler remembers the last time
  each distinct span name exported a span.  When a span occurs after
  more than the specified interval, it samples one (e.g., to ensure
  that receivers know about these spans).  This sampler introduces
  bias because spans that happen between the intervals do not receive
  consideration.
- The "always off" sampler is biased by definition. Since it exports
  no spans, the sum of adjusted count is always zero.
```

### Proposed `Sampler` composition rules

When combining multiple Samplers, the natural outcome is that a span
will be recorded and sampled if any one of the Samplers says to record
or sample the span.  To combine Samplers in a way that preserves
adjusted count requires first classifying Samplers into one of the
following categories:

1. Parent-based (`ParentBased`)
2. Known non-zero probability (`TraceIDRatio`, `AlwaysOn`)
3. Non-probability based (`AlwaysOff`, all other Samplers)

The Parent-based sampler always reduces into one of other two at
runtime, based on whether the parent context includes known parent
probability or not.

Here are the rules for combining Sampler decisions from each of these
categories that may be used to construct composite samplers.

#### Composing two consistent probability samplers

When two consistent probability samplers are used, the Sampler with
the larger probability by definition includes every span the smaller
probability sampler would select.  The result is a consistent sampler
with the minimum p-value.

#### Composing a probability sampler and a non-probability sampler

When a probability sampler is composed with a non-probability sampler,
the effect is to change an unknown probability into a known
probability.  When the probability sampler selects the span, its
adjusted count will be used.  When the probability sampler does not
select a span, zero adjusted count will be used.

The use of zero adjusted count allows recording spans that an unbiased
probability sampler did not select, allowing those spans to be
received at the backend without introducing statistical bias.

#### Composition rules summary

To create a composite Sampler, first express the result of each
Sampler in terms of the p-value and `sampled` flag.  Note that
p-values fall into three categories:

1. Unknown p-value indicates unknown adjusted count
2. Known non-zero p-value (in the range `[0,62]`) indicates known non-zero adjusted count
3. Known zero p-value (`p=63`) indicates known zero adjusted count

While non-probability samplers always return unknown `p` and may set
`sampled=true` or `sampled=false`, a probability sampler is restricted
to returning either `p∈[0,62]` with `sampled=true` or to returning
`p=63` with `sampled=false`.  No individual sampler can return `p=63`
with `sampled=true`, but this condition MAY result from composition of
`p=63` and unknown `p`.

A composite sampler can be computed using the table below, as follows.
Although unknown `p` is never encoded in `tracestate`, for the purpose
of composition we assign unknowns `p=64`, which is 1 beyond the range
of the 6-bit that represent known p-values.  The assignment of `p=64`
simplifies the formulas below .

By following these simple rules, any numher of consistent probability
samplers and non-probability samplers can be combined.  Starting with
`p=64` representing unknown and `sampled=false`, update the composite
p-value to the minimum value of the prior composite p-value and the
individual sampler p-value.

```
p<sub>out</sub> = min(p<sub>in</sub>, p<sub>sampler</sub)
sampled<sub>out</sub> = logicalOR(sampled<sub>in</sub>, sampled<sub>sampler</sub)
```

The composite sampler is always the logical-OR of the individual
samplers.  For p-value, this has two effects:

1. When combining two consistent probability samplers, the
less-selective Sampler's adjusted count is taken.
2. When combining a consistent probability sampler and a
non-probability sampler, this has the effect of changing unknown
adjusted count into known adjusted count.

### Proposed `Sampler` interface changes

The Trace SDK specification of the `SamplingResult` will be extended
with a new field to be returned by all Samplers.

```
- The sampling probability of the span is encoded as the base-2
  logarithm of inverse parent sampling probability, known as "adjusted
  count", which is the effective count of the Span for use in
  Span-to-Metrics pipelines.  The value 64 is used to represent
  unknown adjusted count, and the value 63 is used to represent
  known-zero adjusted count.  For values >=0 and <63, the adjusted
  count of the Span is 2**value, representing power-of-two
  probabilities between 1 and 2**-62.

  The corresonding `SamplerResult` field SHOULD be named
  `log_adjusted_count` because it carries the newly-created 
  span and child context's adjusted count and is expressed as
  the logarithm of adjusted count for spans selected by a 
  probability Sampler. 
```

See [OTEP 168](https://github.com/open-telemetry/oteps/pull/168) for
details on how each of the built-in Samplers is expected to set
`tracestate` for conveying sampling probabilities.

## Recommended reading

[Sampling, 3rd Edition, by Steven
K. Thompson](https://www.wiley.com/en-us/Sampling%2C+3rd+Edition-p-9780470402313).

[A Generalization of Sampling Without Replacement From a Finite Universe](https://www.jstor.org/stable/2280784), JSTOR (1952)

[Performance Is A Shape. Cost Is A Number: Sampling](https://docs.lightstep.com/otel/performance-is-a-shape-cost-is-a-number-sampling), 2020 blog post, Joshua MacDonald

[Priority sampling for estimation of arbitrary subset sums](https://dl.acm.org/doi/abs/10.1145/1314690.1314696)

[Stream sampling for variance-optimal estimation of subset sums](https://arxiv.org/abs/0803.0473).

[Estimation from Partially Sampled Distributed Traces](https://arxiv.org/pdf/2107.07703.pdf), 2021 Dynatrace Research report, Otmar Ertl

## Acknowledgements

Thanks to [Neena Dugar](https://github.com/neena) and [Alex
Kehlenbeck](https://github.com/akehlenbeck) for their help
reconstructing the Dapper Sampler algorithm.
