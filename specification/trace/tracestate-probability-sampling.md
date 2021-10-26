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

Two Samplers are specified that for optional use by OpenTelemetry
tracing SDKs named `ParentConsistentProbabilitityBased` and
`ConsistentProbabilityBased`, meant as optional replacements for the
built-in `ParentBased` and `TraceIdRatioBased` Samplers, respectively.

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

Samplers that conform to this specification have both behavioral and
statistical requirements.  Consumers of OpenTelemetry `tracestate`
data are expected to validate the probability sampling fields before
interpreting the data.

Producers of OpenTelemetry `tracestate` are required to meet the
behavioral requirements and ensure statistically valid outcomes using
tests that are included in this specification, so that users and
consumers of OpenTelemetry `tracestate` can be assured of the accuracy
of their data.

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
a sampling decision.

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

Samplers SHOULD unset `p` from the `tracestate` if the unsigned value is
greater than 63 before using the `tracestate` to make a sampling decision.

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
decision specified for the `ParentBased` sampler for valid contexts.

#### ConsistentProbabilityBased sampler

The `ConsistentProbabilityBased` sampler is meant as an optional
replacement for the [`TraceIdRatioBased`
Sampler](sdk.md#traceidratiobased).  In the case where it is used as a
root sampler, it is required to produce a valid `tracestate`.  In the
case where it is used in a non-root context, it is required to
validate the incoming `tracestate` and to produce a valid `tracestate`
for the outgoing context.

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
to sample to the base-2 logarithm of the unbiased adjusted count.

A test specification for this requirement is given in the appendix.

#### Composition rules

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

### Testing requirements

TODO describe these tests: Overview for hypothesis testing, use of
large N, use of significance levels.  Expectation of a strong general
purpose non-cryptographic random number generator.  Tests are meant to
validate end-to-end sampling logic and span-to-metrics accounting, not
validate the RNG.

Tests are expected to use fixed seeds.  Tests are expected to
demonstrate and document that the statistical tests fail at
approximately at the expected level of statistical significance.
E.g., a 1% significance level test should be repeated and demonstrate
occasional failure, then be saved with the seed that produced the
passing result.  This should be documented.

Tests can be implemented using a another SDK's test, for example.

#### Power of two sampling probability

This MAY use an exact binomial test or it may use a Chi-squared test
with 1 degree of freedom.

Repeat for sampling probabilities: TBD.

#### Arbitrary sampling probability

Chi-squared test with three categories:

1. Unsampled
2. Sampled with lesser probability
3. Sampled with greater/equal probability 

Repeat for sampling probabilities: TBD.

#### Uniform attribute probability

Chi-squared test with arbitrary number of categories.  In either of
the above tests, use a secondary attribute with K categorical values.

Repeat for number of categories: TBD.
