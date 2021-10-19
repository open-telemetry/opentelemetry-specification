# TraceState: Probability Sampling

<!-- toc -->

- [Definitions Used in this Document](#definitions-used-in-this-document)
  * [Sampling](#sampling)
  * [Sampler](#sampler)
  * [Parent-based sampler](#parent-based-sampler)
  * [Probability sampler](#probability-sampler)
  * [Consistent probability sampler](#consistent-probability-sampler)
  * [Always-on sampler](#always-on-sampler)
  * [Always-off sampler](#always-off-sampler)
  * [Non-probability sampler](#non-probability-sampler)
  * [Adjusted count](#adjusted-count)
  * [Unbiased probability sampling](#unbiased-probability-sampling)
  * [Power-of-two random sampling](#power-of-two-random-sampling)

<!-- tocstop -->

**Status**: [Experimental](../document-status.md)

Probability sampling allows OpenTelemetry tracing users to lower their
collection costs with the use of randomized sampling techniques.
OpenTelemetry specifies how to convey and record the results of
probability sampling using the W3C `tracestate` in a way that allows
Span-to-Metrics pipelines to be built that accurately count sampled
spans.

The specification in this document is semantic in nature.  Two
`tracestate` fields, known as "r-value" and "p-value", are defined to
enable the development of interoperable probability Sampler
implementations.  OpenTelemetry is gathering experience with Samplers
based on this specification while the group considers how to add
probability sampling support in the default SDKs, via the specified
built-in Samplers.

## Definitions Used in this Document

### Sampling

Sampling is a family of techniques for collecting and analyzing only a
fraction of a complete data set.  Individual items that are "sampled"
are taken to represent one or more spans when collected and counted.
The representivity of each span is used in a Span-to-Metrics pipeline
to accurately count spans.

Sampling terminology uses "population" to refer to the complete set of
data being sampled from.  In OpenTelemetry tracing, "population"
refers to all spans.

In probability sampling, the representivity of individual sample items
is generally known, whereas OpenTelemetry also recognizes
"non-probability" sampling approaches, in which representivity is not
explicitly quantified.

### Sampler

A Sampler provides configurable logic, used by the SDK, for selecting
which Spans are "recorded" and/or "sampled" in a tracing client
library.  To "record" a span means to build a representation of it in
the client's memory, which makes it eligible for being exported.  To
"sample" a span implies setting the W3C `sampled` flag, recording the
span, and exporting the span when it is finished.

OpenTelemetry supports spans that are "recorded" and not "sampled"
for in-process observability of live spans (e.g., z-pages).

The Sampler interface and the built-in Samplers defined by
OpenTelemetry must be capable of deciding immediately whether to
sample a span, since the child context immediately propagates the
decision.

### Parent-based sampler

A Sampler that makes its decision to sample based on the W3C `sampled`
flag from the context is said to use parent-based sampling.

### Probability sampler

A probability Sampler is a Sampler that knows immediately, for each
of its decisions, the probability that the span had of being selected.

Sampling probability is defined as a number less than or equal to 1
and greater than 0 (i.e., `0 < probability <= 1`).  The case of 0
probability is treated as a special, non-probabilistic case.

### Consistent probability sampler

A consistent probability sampler is a Sampler that supports independent
sampling decisions at each span in a trace while maintaining that 
traces will be complete with probability equal to the minimum sampling 
probability across the trace.  Consistent probability sampling requires that 
for any span in a given trace, if a Sampler with lesser sampling probability 
selects the span for sampling, then the span would also be selected by a
Sampler configured with greater sampling probability.

In OpenTelemetry, consistent probability samplers are limited to
power-of-two probabilities.  OpenTelemetry consistent probability
sampling is defined in terms of "p-value" and "r-value", both
integers, which are propagated via the context to assist in making
consistent sampling decisions.

### Always-on sampler

An always-on sampler is another name for a consistent probability
sampler with probability equal to one.

### Always-off sampler

An always-off Sampler has the effect of disabling a span completely,
effectively excluding it from the population.  This is not defined as
a probability sampler with zero probability, because these spans are
effectively unrepresented.

### Non-probability sampler

A non-probability sampler is a Sampler that makes its decisions not
based on chance, but instead uses arbitrary logic and internal state.

### Adjusted count

Adjusted count is defined as a measure of representivity, the number
of spans in the population that are represented by the individually
sampled span.  Span-to-metrics pipelines can be built by adding the
adjusted count of each sample span to a counter of matching spans.
Likewise, span-to-metrics pipelines can be built by observing the
duration of each sample span in a histogram, the span's adjusted count
number of times each.

The adjusted count 1 means one-to-one sampling.  Adjusted counts
greater than 1 indicate the use of a probability sampler.  Adjusted
counts are unknown when using a non-probability sampler.

Zero adjusted count is defined in a way that supports composition of
probability and non-probability samplers.  In effect, spans that are
"recorded" but not "sampled" have adjusted count of zero.

### Unbiased probability sampling

The statistical term "unbiased" is a requirement applied to the
adjusted count of a span, which states that the expected value of the
sum of adjusted counts across all exported spans MUST equal the true
number of spans in the population.  Statistical bias, a measure of the
difference between an estimate and its true value, of the estimated
span count in the population should equal zero.  Moreover, this
requirement must be true for all subsets of the span population for a 
sampler to be considered an unbiased probability sampler.

Sampling schemes that are not explicitly unbiased should be
categorized as non-probability samplers because they cannot record
unbiased adjusted counts.  Here are example Samplers that do not
qualify as unbiased:

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

As an example, Simple Random Sampling is an unbiased sampling
algorithm.  The algorithm is given a sampling probability `p` in the
interval `(0, 1]` and a source of randomness.  Then for each item:

1. Generate a uniform floating point value `r` in the range `[0, 1)`
2. If `r < p`, select the item with adjusted count `1 / p`.

This algorithm is unbiased because every item in the population
receives equal consideration.

### Power-of-two random sampling

An unbiased sampling scheme can be implemented using a random bit
string as the input.  This scheme is limited to power-of-two sampling
probabilities, as follows.

1. Express the sampling probability as `2**-s`. For example, 25%
   equals `2**-2`
2. Count `r`, the number of consecutive zero bits in the input string
3. If `s <= r`, select the item with adjusted coubnt `2**s`.

This algorithm is the basis of the consistent probability sampling
approach used in OpenTelemetry, defined in greater detail below.

## Probability sampling tracestate fields

The consistent sampling scheme adopted by OpenTelemetry propagates two
values, p-value and r-value, via the context.

1. r-value: this "randomness" value is determined and propagated from the root of the trace to all spans and serves to make sampling decisions consistent
2. p-value: the "parent probability" value can be modified by any span in the trace and informs child parent-based Samplers their adjusted count

Both fields are propagated via the OpenTelemetry `tracestate` under
the `ot` vendor tag using [syntax defined
here](tracestate-handling.md).  Both fields are represented as
unsigned six-bit integers (i.e., in the inclusive interval [0, 63]).

### p-value

The p-value SHOULD be set in the `tracestate` when an unbiased
probability sampler configured with power-of-two probability selected
the parent span for sampling.  p-value SHOULD be set in the
`tracestate` when the W3C `sampled` flag is set in the corresponding
`traceparent`.  Non-probability samplers, having unknown adjusted
count, SHOULD unset p-value when making sampling decisions.

Zero adjusted count is represented by the special p-value 63.
Otherwise, the p-value is set to the negative base-2 logarithm of
sampling probability:

| p-value | Parent Probability |
| -----   | -----------        |
| 0       | 1                  |
| 1       | 1/2                |
| 2       | 1/4                |
| ...     | ...                |
| N       | 2**-N              |
| ...     | ...                |
| 61      | 2**-61             |
| 62      | 2**-62             |
| 63      | 0                  |

### r-value

The r-value SHOULD be set in the `tracestate` by the Sampler at the
root of the trace in order to support consistent probability sampling.
When the value is omitted or not present, child spans in the trace are
not able to participate in consistent probability sampling.

R-value determines which sampling probabilities and will not sample
for spans of a given trace, as follows:

| r-value          | Probability of r-value   | Implied sampling probabilities |
| ---------------- | ------------------------ | ----------------------         |
| 0                | 1/2                      | 1                              |
| 1                | 1/4                      | 1/2 and above                  |
| 2                | 1/8                      | 1/4 and above                  |
| 3                | 1/16                     | 1/8 and above                  |
| ...              | ...                      | ...                            |
| 0 <= r <= 61     | 1/(2**(-r-1))            | 2**(-r) and above              |
| ...              | ...                      | ...                            |
| 59               | 2**-60                   | 2**-59 and above               |
| 60               | 2**-61                   | 2**-60 and above               |
| 61               | 2**-62                   | 2**-61 and above               |
| 62               | 2**-62                   | 2**-62 and above               |

### Probability Sampler behavior



#### Parent-based

#### Consistent probability-based

