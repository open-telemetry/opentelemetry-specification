# TraceState: Probability Sampling

<!-- toc -->

- [Approach used in this document](#approach-used-in-this-document)
  * [Objective](#objective)
  * [Definitions](#definitions)
    + [Sampling](#sampling)
    + [Adjusted count](#adjusted-count)
    + [Power-of-two random sampling](#power-of-two-random-sampling)
    + [Sampler](#sampler)
    + [Parent-based sampler](#parent-based-sampler)
    + [Probability sampler](#probability-sampler)
    + [Consistent probability sampler](#consistent-probability-sampler)
    + [Always-on sampler](#always-on-sampler)
    + [Always-off sampler](#always-off-sampler)
    + [Non-probability sampler](#non-probability-sampler)
- [Probability sampling](#probability-sampling)
  * [Conformance](#conformance)
  * [Context invariants](#context-invariants)
    + [Sampled flag](#sampled-flag)
      - [Requirement 1](#requirement-1)
    + [P-value](#p-value)
      - [Requirement 1](#requirement-1-1)
    + [R-value](#r-value)
      - [Requirement 1](#requirement-1-2)
  * [Samplers](#samplers)
    + [ParentConsistentProbabilityBased sampler](#parentconsistentprobabilitybased-sampler)
      - [Requirement 1](#requirement-1-3)
      - [Requirement 2](#requirement-2)
      - [Requirement 3](#requirement-3)
    + [ConsistentProbabilityBased sampler](#consistentprobabilitybased-sampler)
      - [Requirement 1](#requirement-1-4)
      - [Requirement 2](#requirement-2-1)
      - [Requirement 3](#requirement-3-1)
      - [Requirement 4](#requirement-4)
    + [Composition rules](#composition-rules)
      - [Requirement 1](#requirement-1-5)
      - [Requirement 2](#requirement-2-2)
      - [Requirement 3](#requirement-3-2)
      - [Requirement 4](#requirement-4-1)
  * [Testing requirements](#testing-requirements)
    + [Power of two sampling probability](#power-of-two-sampling-probability)
    + [Arbitrary sampling probability](#arbitrary-sampling-probability)
    + [Uniform attribute probability](#uniform-attribute-probability)

<!-- tocstop -->

**Status**: [Experimental](../document-status.md)

Probability sampling allows OpenTelemetry tracing users to lower their
collection costs with the use of randomized sampling techniques.
OpenTelemetry specifies how to convey and record the results of
probability sampling using the W3C `tracestate` in a way that allows
Span-to-Metrics pipelines to be built that accurately count sampled
spans.

## Approach used in this document

### Objective

This document specifies two `tracestate` fields, known as "r-value"
and "p-value" meant to support interoperable Sampler implementations.
Rules are given for creating, validating, interpreting, and mutating
these fields in an OpenTelemetry [context](../context/context.md).

Two Samplers are specified for optional inclusion in OpenTelemetry
tracing SDKs, named `ParentConsistentProbabilitityBased` and
`ConsistentProbabilityBased`.  These are meant as optional
replacements for the built-in `ParentBased` and `TraceIdRatioBased`
Samplers.

### Definitions

#### Sampling

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

#### Adjusted count

Adjusted count is a measure of representivity, the number of spans in
the population that are represented by the individually sampled span.
Span-to-metrics pipelines can be built by adding the adjusted count of
each sample span to a counter of matching spans.

For probability sampling, adjusted count is defined as the reciprocal
(i.e., mathematical inverse) of sampling probability.

For non-probability sampling, adjusted count is unknown.

Zero adjusted count is defined in a way that supports composition of
probability and non-probability sampling.  Zero is assigned as the
adjusted count when a probability sampler does not select a span.

#### Power-of-two random sampling

A simple sampling scheme can be implemented using a random bit string
as the input.  This scheme is limited to power-of-two sampling
probabilities, as follows.

1. Express the sampling probability as `2**-s`. For example, 25%
   equals `2**-2` with `s=2`
2. Count `r`, the number of consecutive zero bits in the input string
3. If `s <= r`, select the item with adjusted count `2**s`.

This algorithm is the basis of the consistent probability sampling
approach used in OpenTelemetry, defined in greater detail below.

#### Sampler

A Sampler provides configurable logic, used by the SDK, for selecting
which Spans are "recorded" and/or "sampled" in a tracing client
library.  To "record" a span means to build a representation of it in
the client's memory, which makes it eligible for being exported.  To
"sample" a span implies setting the W3C `sampled` flag, recording the
span, and exporting the span when it is finished.

OpenTelemetry supports spans that are "recorded" and not "sampled"
for in-process observability of live spans (e.g., z-pages).

The Sampler interface and the built-in Samplers defined by
OpenTelemetry decide immediately whether to sample a span, and the
child context immediately propagates the decision.

#### Parent-based sampler

A Sampler that makes its decision to sample based on the W3C `sampled`
flag from the context is said to use parent-based sampling.

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

#### Always-on sampler

An always-on sampler is another name for a consistent probability
sampler with probability equal to one.

#### Always-off sampler

An always-off Sampler has the effect of disabling a span completely,
effectively excluding it from the population.  This is not defined as
a probability sampler with zero probability, because these spans are
effectively unrepresented.

#### Non-probability sampler

A non-probability sampler is a Sampler that makes its decisions not
based on chance, but instead uses arbitrary logic and internal state.

## Probability sampling

The consistent sampling scheme adopted by OpenTelemetry propagates two
values via the context, termed "p-value" and "r-value":

1. p-value: the "parent probability" value can be set independently by any span in the trace, for its children, and informs child parent-based Samplers of their adjusted count
2. r-value: the "randomness" value is determined and propagated from the root to all spans in the trace and serves to make sampling decisions consistent

Both fields are propagated via the OpenTelemetry `tracestate` under
the `ot` vendor tag using the rules for [tracestate
handling](tracestate-handling.md).  Both fields are represented as
unsigned integers requiring at most 6 bits of information.  An
invariant will be stated that connects the `sampled` trace flag found
in `traceparent` context to the r-value and p-value found in
`tracestate` context.

### Conformance

Consumers of OpenTelemetry `tracestate` data are expected to validate
the probability sampling fields before interpreting the data.  This
applies to the two samplers specified here as well as consumers of
span data, who are expected to validate `tracestate` before
interpreting span adjusted counts.

Producers of OpenTelemetry `tracestate` containing p-value and r-value
fields are required to meet the behavioral requirements stated for the
ConsistentProbabilityBased sampler, to ensure statistically valid
outcomes, using a test suite included in this specification, so that
users and consumers of OpenTelemetry `tracestate` can be assured of
accurate span counts in a span-to-metrics pipeline.

### Context invariants

The W3C `traceparent` (version 0) contains three fields of
information: the TraceId, the SpanId, and the trace flags.  The
`sampled` trace flag has been defined by W3C to signal an intent to
sample the context.

The [Sampler API](sdk.md#sampler) is responsible for setting the
`sampled` flag and the `tracestate`. 

P-value and r-value are set in the OpenTelemetry `tracestate`, under
the vendor tag `ot`, using the identifiers `p` and `r`.  P-value is an
unsigned integer valid in the inclusive range `[0, 63]` (i.e., there
are 64 valid values).  R-value is an unsigned integer valid in the
inclusive range `[0, 62]` (i.e., there are 63 valid values).  P-value
and r-value are independent settings, each can be meaningfully set
without the other present.

#### Sampled flag

Probability sampling uses additional information to enable consistent
decision making and to record the adjusted count of sampled spans.
When both values are defined and in the specified range, the invariant
between r-value and p-value and the `sampled` trace flag states that
`sampled` is equivalent to the expression `p <= r || p == 63`.

The invariant between `sampled`, `p`, and `r` only applies when both
`p` and `r` are present.  When the invariant is violated, the
`sampled` flag takes precedence and `p` is unset from `tracestate` in
order to signal unknown adjusted count.

##### Requirement 1

Samplers SHOULD unset `p` when the invariant between the `sampled`,
`p`, and `r` values is violated before using the `tracestate` to make
a sampling decision or interpret adjusted count.

#### P-value

Zero adjusted count is represented by the special p-value 63,
otherwise the p-value is set to the negative base-2 logarithm of
sampling probability:

| p-value | Parent Probability | Adjusted count |
| -----   | -----------        | --             |
| 0       | 1                  | 1              |
| 1       | 1/2                | 2              |
| 2       | 1/4                | 4              |
| ...     | ...                | ...            |
| N       | 2**-N              | 2**N           |
| ...     | ...                | ...            |
| 61      | 2**-61             | 2**61          |
| 62      | 2**-62             | 2**62          |
| 63      | 0                  | 0              |

##### Requirement 1

Consumers SHOULD unset `p` from the `tracestate` if the unsigned value
is greater than 63 before using the `tracestate` to make a sampling
decision or interpret adjusted count.

#### R-value

R-value is set in the `tracestate` by the Sampler at the root of the
trace, in order to support consistent probability sampling.  When the
value is omitted or not present, child spans in the trace are not able
to participate in consistent probability sampling.

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

##### Requirement 1

Samplers SHOULD unset both `r` and `p` from the `tracestate` if the
unsigned value is of `r` is greater than 62 before using the
`tracestate` to make a sampling decision.

### Samplers

#### ParentConsistentProbabilityBased sampler

The `ParentConsistentProbabilityBased` sampler is meant as an optional
replacement for the [`ParentBased` Sampler](sdk.md#parentbased). It is
required to first validate the `tracestate` and then behave as the
`ParentBased` sampler would.

##### Requirement 1

The `ParentConsistentProbabilityBased` Sampler MUST have the same
constructor signature as the built-in `ParentBased` sampler in each
OpenTelemetry SDK.

##### Requirement 2

The `ParentConsistentProbabilityBased` Sampler MUST NOT modify a
valid `tracestate`.

##### Requirement 3

The `ParentConsistentProbabilityBased` Sampler MUST make the same
decision specified for the `ParentBased` sampler when the context is
valid.

#### ConsistentProbabilityBased sampler

The `ConsistentProbabilityBased` sampler is meant as an optional
replacement for the [`TraceIdRatioBased`
Sampler](sdk.md#traceidratiobased).  In the case where it is used as a
root sampler, the `ConsistentProbabilityBased` sampler is required to
produce a valid `tracestate`.  In the case where it is used in a
non-root context, it is required to validate the incoming `tracestate`
and to produce a valid `tracestate` for the outgoing context.

The `ConsistentProbabilityBased` sampler is required to support
probabilities that are not exact powers of two.  To do so,
implementations are required to select between the nearest powers of
two probabilistically.  For example, 5% sampling can be achieved by
selecting 1/16 sampling 60% of the time and 1/32 sampling 40% of the
time.

##### Requirement 1

The `ConsistentProbabilityBased` Sampler MUST have the same
constructor signature as the built-in `TraceIdRatioBased` sampler in
each OpenTelemetry SDK.

##### Requirement 2

The `ConsistentProbabilityBased` Sampler MUST set `r` when it makes a
root sampling decision.

##### Requirement 3

The `ConsistentProbabilityBased` Sampler MUST unset `p` from the
`tracestate` when it decides not to sample.

##### Requirement 4

The `ConsistentProbabilityBased` Sampler MUST set `p` when it decides
to sample.

##### Requirement 5

When it decides to sample, the `ConsistentProbabilityBased` Sampler
MUST set `p` to the negative base-2 logarithm of a power-of-two
sampling probability.

##### Requirement 6

The `ConsistentProbabilityBased` Sampler MUST set `p` so that the
adjusted count interpreted from the `tracestate` is an unbiased
estimate of the number of representative spans in the population.

A test specification for this requirement is given in the appendix.

##### Requirement 7

If `r` is not set on the input `tracecontext` and the Span is not a
root span, `ConsistentProbabilityBased` SHOULD set `r` as if it were a
root span.

##### Requirement 8

If the configured sampling probability is less than `2**-62`, the
Sampler should round down to zero probability and make the same
sampling decision as the builtin `AlwaysOff` sampler would.

### Composition rules

When more than one Sampler participates in the decision to sample a
context, their decisions can be combined using composition rules.  In
all cases, the combined decision to sample is the logical-OR of the
Samplers' decisions (i.e., sample if at least one of the composite
Samplers decides to sample).

To combine p-values from two consistent probability Sampler decisions,
the Sampler with the greater probability takes effect.  The output
p-value becomes the minimum of the two values for `p`.

To combine a consistent probability Sampler decision with a
non-probability Sampler decision, p-value 63 is used to signify zero
adjusted count.  If the probability Sampler decides to sample, its
p-value takes effect.  If the probability Sampler decides not to
sample when the non-probability sample does sample, p-value 63 takes
effect signifying zero adjusted count.

#### List of requirements

##### Requirement 1

When combining Sampler decisions for multiple consistent probability
Samplers and at least one decides to sample, the minimum of the "yes"
decision `p` values MUST be set in the `tracestate`.

##### Requirement 2

When combining Sampler decisions for multiple consistent probability
Samplers and none decides to sample, p-value MUST be unset in the
`tracestate`.

##### Requirement 3

When combining Sampler decisions for a consistent probability Sampler
and a non-probability Sampler, and the probability Sampler decides to
sample, its p-value MUST be set in the `tracestate` regardless of the
non-probability Sampler decision.

##### Requirement 4

When combining Sampler decisions for a consistent probability Sampler
and a non-probability Sampler, and the probability Sampler decides not
to sample but the non-probability does sample, p-value 63 MUST be set
in the `tracestate`.

### Consumer-only requirements

#### Trace consumers

Due to the `ConsistentProbabilityBased` Sampler requirement about
setting `r` when it is unset for a non-root span, trace consumers are
advised to check traces for r-value consistency.

When a single trace contains more than a single distinct `r` value, it
means the trace was not correctly sampled at the root for probability
sampling.  While the adjusted count of each span is correct in this
scenario, it may be impossible to detect complete traces.

##### Requirement 1

When a single trace contains spans with `tracestate` values containing
more than one distinct value for `r`, the consumer SHOULD recognize
the trace as inconsistently sampled.

### Appendix: Statistical test requirements

This section specifies a test that can be implemented to ensure basic
conformance with the requirement that sampling decisions are unbiased.

The goal of this test specification is to be simple to implement and
not require advanced statistical skills or libraries to be successful.

This test is not meant to evaluate the performance of a random number
generator.  This test assumes the underlying RNG is of good quality
and checks that the sampler produces the expected proportionality with
a high degree of statistical confidence.

One of the challenges of this kind of test is that probabilistic tests
are expected to occasionally produce exceptional results.  To make
this a strict test for random behavior, we take the following approach:

- Generate a pre-determined list of 20 random seeds
- Use fixed values for significance level (5%) and trials (20)
- Use a population size of one million spans
- For each trial, simulate the population and compute ChiSquared 
  test statistic
- Locate the first seed value in the ordered list such that the
  Chi-Squared significance test fails exactly once out of 20 trials

To create this test, perform the above sequence using the seed values
from the predetermined list, in order, until a seed value is found
with exactly one failure.  This is expected to happen fairly often and
is required to happen once among the 20 available seeds.  After
calculating the index of the first seed with exactly one ChiSquared
failure, record it in the test.  For continuous integration testing,
it is only necessary to re-run the test using the predetermined seed
index.

As specified, the Chi-Squared test has either one or two degrees of
freedom, depending on whether the sampling probability is an exact
power of two or not.

#### Test procedure: non-powers of two

In this case there are two degrees of freedom for the Chi-Squared test.
The following table summarizes the test parameters.

| Test case | Sampling probability | Lower, Upper p-value when sampled | Expect<sub>lower</sub> | Expect<sub>upper</sub> | Expect<sub>unsampled</sub> |
| ---       | ---                  | ---                               | ---                    | ---                    | ---                        |
| 0         | 0.900000             | 0, 1                              | 100000                 | 800000                 | 100000                     |
| 1         | 0.600000             | 0, 1                              | 400000                 | 200000                 | 400000                     |
| 2         | 0.330000             | 1, 2                              | 170000                 | 160000                 | 670000                     |
| 3         | 0.130000             | 2, 3                              | 120000                 | 10000                  | 870000                     |
| 4         | 0.100000             | 3, 4                              | 25000                  | 75000                  | 900000                     |
| 5         | 0.050000             | 4, 5                              | 12500                  | 37500                  | 950000                     |
| 6         | 0.017000             | 5, 6                              | 14250                  | 2750                   | 983000                     |
| 7         | 0.010000             | 6, 7                              | 5625                   | 4375                   | 990000                     |
| 8         | 0.005000             | 7, 8                              | 2812.5                 | 2187.5                 | 995000                     |
| 9         | 0.002900             | 8, 9                              | 1006.25                | 1893.75                | 997100                     |
| 10        | 0.001000             | 9, 10                             | 953.125                | 46.875                 | 999000                     |
| 11        | 0.000500             | 10, 11                            | 476.5625               | 23.4375                | 999500                     |
| 12        | 0.000260             | 11, 12                            | 228.28125              | 31.71875               | 999740                     |
| 13        | 0.000230             | 12, 13                            | 14.140625              | 215.859375             | 999770                     |
| 14        | 0.000100             | 13, 14                            | 22.0703125             | 77.9296875             | 999900                     |

The formula for computing Chi-Squared in this case is:

```
ChiSquared = math.Pow(sampled<sub>lower</sub> - expect<sub>lower</sub>, 2) / expect<sub>lower</sub> +
             math.Pow(sampled<sub>upper</sub> - expect<sub>upper</sub>, 2) / expect<sub>upper</sub> +
             math.Pow(1000000 - sampled<sub>lower</sub> - sampled<sub>upper</sub> - expect<sub>unsampled</sub>, 2) / expect<sub>unsampled</sub>

```

This should be compared with 0.102587, the value of the Chi-Squared
distribution for two degrees of freedom with significance level 5%.
For each probability in the table above, the test is required to
demonstrate a seed that produces exactly one ChiSquared value less
than 0.102587.

##### Requirement 1

For the test with 20 trials and 1 million spans each, the test MUST
demonstrate a random number generator seed such that the ChiSquared
test statistic is below 0.102587 exactly 1 out of 20 times.

#### Test procedure: exact powers of two

In this case there is one degree of freedom for the Chi-Squared test.
The following table summarizes the test parameters.

| Test case | Sampling probability | P-value when sampled | Expect<sub>sampled</sub> | Expect<sub>unsampled</sub> |
| ---       | ---                  | ---                  | ---                      | ---                        |
| 15        | 0x1p-01 (0.500000)   | 1                    | 500000                   | 500000                     |
| 16        | 0x1p-04 (0.062500)   | 4                    | 62500                    | 937500                     |
| 17        | 0x1p-07 (0.007812)   | 7                    | 7812.5                   | 992187.5                   |
| 18        | 0x1p-10 (0.000977)   | 10                   | 976.5625                 | 999023.4375                |
| 19        | 0x1p-13 (0.000122)   | 13                   | 122.0703125              | 999877.9297                |

The formula for computing Chi-Squared in this case is:

```
ChiSquared = math.Pow(sampled - expect<sub>sampled</sub>, 2) / expect<sub>sampled</sub> +
             math.Pow(1000000 - sampled - expect<sub>unsampled</sub>, 2) / expect<sub>unsampled</sub>
```

This should be compared with 0.003932, the value of the Chi-Squared
distribution for one degree of freedom with significance level 5%.
For each probability in the table above, the test is required to
demonstrate a seed that produces exactly one ChiSquared value less
than 0.003932.

##### Requirement 1

For the teset with 20 trials and 1 million spans each, the test MUST
demonstrate a random number generator seed such that the ChiSquared
test statistic is below 0.003932 exactly 1 out of 20 times.

