<!--- Hugo front matter used to generate the website version of this page:
linkTitle: Probability Sampling
--->

# TraceState: Probability Sampling

**Status**: [Experimental](../document-status.md)

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [Overview](#overview)
  * [Definitions](#definitions)
    + [Sampling](#sampling)
    + [Adjusted count](#adjusted-count)
    + [Sampler](#sampler)
    + [Parent-based sampler](#parent-based-sampler)
    + [Probability sampler](#probability-sampler)
    + [Consistent probability sampler](#consistent-probability-sampler)
    + [Trace completeness](#trace-completeness)
    + [Non-probability sampler](#non-probability-sampler)
    + [Always-on consistent probability sampler](#always-on-consistent-probability-sampler)
    + [Always-off sampler](#always-off-sampler)
- [Consistent Probability sampling](#consistent-probability-sampling)
  * [Conformance](#conformance)
  * [Completeness guarantee](#completeness-guarantee)
  * [Context invariants](#context-invariants)
    + [Sampled flag](#sampled-flag)
      - [Requirement: Inconsistent p-values are unset](#requirement-inconsistent-p-values-are-unset)
    + [P-value](#p-value)
      - [Requirement: Out-of-range p-values are unset](#requirement-out-of-range-p-values-are-unset)
    + [R-value](#r-value)
      - [Requirement: Out-of-range r-values unset both p and r](#requirement-out-of-range-r-values-unset-both-p-and-r)
      - [Requirement: R-value is generated with the correct probabilities](#requirement-r-value-is-generated-with-the-correct-probabilities)
    + [Examples: Context invariants](#examples-context-invariants)
      - [Example: Probability sampled context](#example-probability-sampled-context)
      - [Example: Probability unsampled](#example-probability-unsampled)
  * [Samplers](#samplers)
    + [ParentConsistentProbabilityBased sampler](#parentconsistentprobabilitybased-sampler)
      - [Requirement: ParentConsistentProbabilityBased API](#requirement-parentconsistentprobabilitybased-api)
      - [Requirement: ParentConsistentProbabilityBased does not modify valid tracestate](#requirement-parentconsistentprobabilitybased-does-not-modify-valid-tracestate)
      - [Requirement: ParentConsistentProbabilityBased calls the configured root sampler for root spans](#requirement-parentconsistentprobabilitybased-calls-the-configured-root-sampler-for-root-spans)
      - [Requirement: ParentConsistentProbabilityBased respects the sampled flag for non-root spans](#requirement-parentconsistentprobabilitybased-respects-the-sampled-flag-for-non-root-spans)
    + [ConsistentProbabilityBased sampler](#consistentprobabilitybased-sampler)
      - [Requirement: TraceIdRatioBased API compatibility](#requirement-traceidratiobased-api-compatibility)
      - [Requirement: ConsistentProbabilityBased sampler sets r for root span](#requirement-consistentprobabilitybased-sampler-sets-r-for-root-span)
      - [Requirement: ConsistentProbabilityBased sampler unsets p when not sampled](#requirement-consistentprobabilitybased-sampler-unsets-p-when-not-sampled)
      - [Requirement: ConsistentProbabilityBased sampler sets p when sampled](#requirement-consistentprobabilitybased-sampler-sets-p-when-sampled)
      - [Requirement: ConsistentProbabilityBased sampler records unbiased adjusted counts](#requirement-consistentprobabilitybased-sampler-records-unbiased-adjusted-counts)
      - [Requirement: ConsistentProbabilityBased sampler sets r for non-root span](#requirement-consistentprobabilitybased-sampler-sets-r-for-non-root-span)
      - [Requirement: ConsistentProbabilityBased sampler decides not to sample for probabilities less than 2**-62](#requirement-consistentprobabilitybased-sampler-decides-not-to-sample-for-probabilities-less-than-2-62)
    + [Examples: Consistent probability samplers](#examples-consistent-probability-samplers)
      - [Example: Setting R-value for a root span](#example-setting-r-value-for-a-root-span)
      - [Example: Handling inconsistent P-value](#example-handling-inconsistent-p-value)
      - [Example: Handling corrupt R-value](#example-handling-corrupt-r-value)
  * [Composition rules](#composition-rules)
    + [List of requirements](#list-of-requirements)
      - [Requirement: Combining multiple sampling decisions using logical `or`](#requirement-combining-multiple-sampling-decisions-using-logical-or)
      - [Requirement: Combine multiple consistent probability samplers using the minimum p-value](#requirement-combine-multiple-consistent-probability-samplers-using-the-minimum-p-value)
      - [Requirement: Unset p when multiple consistent probability samplers decide not to sample](#requirement-unset-p-when-multiple-consistent-probability-samplers-decide-not-to-sample)
      - [Requirement: Use probability sampler p-value when its decision to sample is combined with non-probability samplers](#requirement-use-probability-sampler-p-value-when-its-decision-to-sample-is-combined-with-non-probability-samplers)
      - [Requirement: Use p-value 63 when a probability sampler decision not to sample is combined with a non-probability sampler decision to sample](#requirement-use-p-value-63-when-a-probability-sampler-decision-not-to-sample-is-combined-with-a-non-probability-sampler-decision-to-sample)
    + [Examples: Composition](#examples-composition)
      - [Example: Probability and non-probability sampler in a root context](#example-probability-and-non-probability-sampler-in-a-root-context)
      - [Example: Two consistent probability samplers](#example-two-consistent-probability-samplers)
  * [Producer and consumer recommendations](#producer-and-consumer-recommendations)
    + [Trace producer: completeness](#trace-producer-completeness)
      - [Recommendation: use non-descending power-of-two probabilities](#recommendation-use-non-descending-power-of-two-probabilities)
    + [Trace producer: correctness](#trace-producer-correctness)
      - [Recommendation: sampler delegation](#recommendation-sampler-delegation)
    + [Trace producer: interoperability with `ParentBased` sampler](#trace-producer-interoperability-with-parentbased-sampler)
    + [Trace producer: interoperability with `TraceIdRatioBased` sampler](#trace-producer-interoperability-with-traceidratiobased-sampler)
    + [Trace consumer](#trace-consumer)
      - [Recommendation: Recognize inconsistent r-values](#recommendation-recognize-inconsistent-r-values)
  * [Appendix: Statistical test requirements](#appendix-statistical-test-requirements)
    + [Test procedure: non-powers of two](#test-procedure-non-powers-of-two)
      - [Requirement: Pass 12 non-power-of-two statistical tests](#requirement-pass-12-non-power-of-two-statistical-tests)
    + [Test procedure: exact powers of two](#test-procedure-exact-powers-of-two)
      - [Requirement: Pass 3 power-of-two statistical tests](#requirement-pass-3-power-of-two-statistical-tests)
    + [Test implementation](#test-implementation)
- [Appendix](#appendix)
  * [Methods for generating R-values](#methods-for-generating-r-values)

<!-- tocstop -->

</details>

## Overview

Probability sampling allows OpenTelemetry tracing users to lower span
collection costs by the use of randomized sampling techniques.  The
objectives are:

- Compatible with the W3C Trace Context Level 1 `sampled` flag
- Compatible with the W3C Trace Context Level 2 `random` flag
- Spans can be accurately counted using a Span-to-metrics pipeline
- Traces tend to be complete, even though Spans make independent sampling decisions.

This document specifies an approach based on an "R-value" and a
"T-value".  At a very high level, R-value is a source of randomness
and T-value encodes the sampling probability in the form of a
"rejection threshold".  A context is sampled when the randomness value
is greater than or equal to the rejection threshold (i.e., `R >= T`).

Ordinarily, R-value is derived from the TraceID; it can be explicitly
set as a field in the TraceState, where T-value is set.

Significantly, by including the T-value and (optionally) R-value in the
OpenTelemetry `tracestate`, these two values automatically propagate
through the context and are recorded with every Span.  This allows Trace
consumers to accurately count spans by interpreting the T-value
encoded within themselves.

T-value and R-value are represented using 56 bits, the number
specified in the W3C Trace Context Level 2 specification.

T-value is encoded using one to 14 hexadecimal digits, expressing the
rejection threshold as an unsigned integer between `0` and
`ffffffffffffff`.  At the boundaries, T-value `0` indicates that
zero spans are being rejected (i.e., 100% sampling), and T-value
`ffffffffffffff` indicates that all except one out of `2**56` spans
are being rejected (i.e., `2**-56` sampling).

When T-value is less than 14 digits, it is zero-padded on the right.
For example, a T-value of `d` encodes a hexadecimal rejection
threshold value `0xd0000000000000`; it can be read as "rejecting 14
(i.e., `0xd`) out of 16 (i.e., `0x10`) spans" and corresponds with
1-in-8 sampling.

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

Thus, there are two meaningfully distinct categories of adjusted count:

| Adjusted count is | Interpretation                                                                                                                     |
|-------------------|------------------------------------------------------------------------------------------------------------------------------------|
| _Unknown_         | The adjusted count is not known, possibly the result of a legacy or non-probability sampler.  Items in this category should not be counted. |
| _Non-zero_        | The adjusted count is known and greater than or equal to one.                                                                      |

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
of its decisions, the probability that the span has of being selected.

Sampling probability is defined as a number less than or equal to 1
and greater than 0 (i.e., `0 < probability <= 1`).  The case of 0
probability is not defined, since no spans are counted.

#### Consistent probability sampler

A consistent probability sampler is a Sampler that supports
independent sampling decisions at each span in a trace while
maintaining that traces will be complete with a certain minimum
probability across the trace.

Consistent probability sampling requires that for any span in a given
trace, if a Sampler with lesser sampling probability selects the span
for sampling, then the span would also be selected by a Sampler
configured with greater sampling probability.

#### Trace completeness

A trace is said to be complete when all of the spans belonging to the
trace are collected.  When at least one span is collected but not all
spans are collected, the trace is considered incomplete.

Trace incompleteness may happen on purpose (e.g., through sampling
configuration), or by accident (e.g., through collection errors).  The
OpenTelemetry trace data model supports a _one-way_ test for
incompleteness: for any non-root span, the trace is definitely
incomplete if the span's parent span was not collected.

Incomplete traces that result from sampling configuration (i.e., on
purpose) are known as partial traces.  An important subset of the
partial traces are those which are also complete subtraces.  A
complete subtrace is defined at span S when every descendent span is
collected.

Since the test for an incompleteness is one-way, it is important to
know which sampling configurations may lead to incomplete traces.
Sampling configurations that lead naturally to complete traces and
complete subtraces are [discussed below](#trace-producer-completeness).

#### Non-probability sampler

A non-probability sampler is a Sampler that makes its decisions not
based on chance, but instead uses arbitrary logic and internal state.
The adjusted count of spans sampled by a non-probability sampler is
unknown.

#### Always-on consistent probability sampler

An always-on sampler is another name for a consistent probability
sampler with probability equal to one.

#### Always-off sampler

An always-off Sampler has the effect of disabling a span completely,
effectively excluding it from the population.  This is not defined as a
probability sampler.

## Consistent Probability sampling

The consistent sampling scheme adopted by OpenTelemetry propagates one
or two values via the context, termed T-value and (optionally)
R-value.  These fields are propagated via the OpenTelemetry
`tracestate` using the `ot` vendor tag, as stated in the rules for
[tracestate handling](tracestate-handling.md).

This sampling scheme selects items from among a fixed set of `2**56`
distinct probability values.  The set of supported probabilities are
expressed in terms of a "rejection threshold", with values between 0
and `(2**56)-1` indicating how many out of `2**56` trace contexts
should be rejected by sampling.

R-value determines which among the `2**56` distinct sampling
probabilities will consistently decide to sample for a given trace.
R-value can be derived from the TraceID, in which case it is defined
by the least-significant 7 bytes (i.e., 56 bits) of the identifier.

Either way, R-value defines the input for the sampling decision, based
on the rejection threshold expressed by T-value.  A trace context is
sampled when `R >= T` (i.e., when the randomness value is greater than
or equal to the rejection threshold).

An invariant will be stated that connects the `sampled` trace flag
found in `traceparent` header to the T-value and (optional) R-value
found in the `tracestate` header.

### Conformance

Consumers of OpenTelemetry `tracestate` data are expected to validate
the probability sampling fields before interpreting the data.  This
applies to the two samplers specified here as well as consumers of
span data, who are expected to validate `tracestate` before
interpreting span adjusted counts.

Producers of OpenTelemetry `tracestate` containing T-value and R-value
fields are required to meet the behavioral requirements stated for the
`ConsistentProbabilityBased` sampler and to ensure statistically valid
outcomes.  A test suite is included in this specification so that
users and consumers of OpenTelemetry `tracestate` can be assured of
accuracy in Span-to-metrics pipelines.

### Context invariants

The W3C Trace Context Level 2 `traceparent` header contains three
fields of information: the TraceID, the SpanID, and the trace flags.
The flags are:

- `sampled` (value `0x1`): signals an intent to sample the context
- `random` (value `0x2`): signals that the least-significant 56 bits of the TraceID are random.

The [Sampler API](sdk.md#sampler) is responsible for setting the
`sampled` and `random` flags and the `tracestate`.

T-value and (optionally) R-value are set in the OpenTelemetry
`tracestate` entry, under the vendor tag `ot`, using the identifiers
`th` and `rv`, respectively.  Both T-value and R-value are encoded
using exclusively hexadecimal digits.

T-value and R-value fields each carry 56-bits of information,
expressing an unsigned value in network byte order.  When T-value is
less than 14 hexadecimal digits, the value is extended with trailing
zeros so that it contains 56 bits.  R-value fields are expressed in
exactly 14 hexadecimal digits.

The R-value field is optional.  When R-value is omitted, an effective
R-value can be calculated from the TraceID, using the trailing 7 bytes
(56 bits) of the identifier in network byte order. Equivalently, the
effective R-value can be calculating using the trailing 14 hexadecimal
digits, specified by OpenTelemetry as the JSON-encoding for TraceID
values.

#### Sampled flag

The invariant between T-value, (effective) R-value, and the Sampled
flag can be stated as `sampled == (R >= T)`.

The invariant between `sampled`, `T`, and `R` only applies when
T-value is present in the `tracestate`.  When the invariant is
violated, the `sampled` flag takes precedence and the T-value is unset
from `tracestate` in order to signal unknown adjusted count.

##### Requirement: Inconsistent T-values are unset

Samplers SHOULD unset T-value (by erasing the `tv` field) when the
invariant between the `sampled` flag, T-value, and (effective) R-value
is violated, before using the `tracestate` to make a sampling decision
or interpret adjusted count.

#### Random flag

The Random flag was introduced in W3C Trace Context Level 2
specification, which also stated which bits of the 128 bit TraceID
would be random when the flag was set.

At the time of this specification:

- No implementations set the Random flag
- All OpenTelemetry trace SDKs generate 128 random bits, except when there is a user-supplied IdGenerator
- Some OpenTelemetry propagation SDK components do not propagate
  unrecognized trace flags.

These points, taken together, means there will be a long delay before
the Random trace flag functions as intended in ther OpenTelemetry
tracing ecosystem.  This is the reason why Head Samplers (inside
tracing SDKs) are required to set the flag and respect its meaning,
while Tail Samplers (inside Collectors) are not recommended to make
use of the flag.

##### Requirement: Head Samplers set required randomness in TraceID

Head Samplers (i.e., trace SDKs) SHOULD by default generate the 56
random bits specified for TraceIDs by the W3C Trace Context Level 2,
and set the Random trace flag, when generating new contexts.

##### Requirement: Tail Samplers assume random TraceIDs

Tail Samplers SHOULD ignore the W3C Trace Context Level 2 Random flag
when interpreting span data.  This is a compromise 

When there is an explicit R-value set, the Sampler will anyway
disregard the Random flag.  However, when there is no explicit R-value
set and the Sampler operates on Span data alone, there is not a local
modification that would be effective and yield consistent sampling.

This recommendation may be revisited after OpenTelemetry SDKs
generally propagate and record Trace Context flags according to the
Trace Context Level 2 specification.  Until such time, Tail Samplers
are encouraged, optionally, to support a "strict" operating mode in
which the Random flag is respected, meaning to treat contexts without
the Random flag and without an explicit R-value as an error condition.

#### T-value

T-value is encoded using the sub-key `th` in the OpenTelemetry
tracestate section, conveying a 56-bit rejection threshold using
between one and 14 hexadecimal digits.  T-value encodings less than 14
digits are padded with trailing zero digits, giving implementations a
choice how much precision they want to use, especially when converting
probability values expressed as percentages, or in decimal form.

Here is an example tracestate value encoding 25% sampling:

```
tracestate: ot=tv:c
```

where `ot` indicates the OpenTelemetry section, `tv` indicates
T-value, and `c` indicates a rejection threshold of 0xc0000000000000
after trailing zeros are removed.

The use of variable precision is significant when expressing
percent-based sampling configuration into an exact T-value.  For
example, a sampling rate of 1/3 translates into a rejection threshold
of 2/3, which can be approximated as a repeating decimal fraction like
`666/1000` or `6666/10000`, can also be expressed as a hexadecimal
fraction like `0xaab/0x1000` or `0xaaab/0x10000`.  Implementations are
recommended to limit precision to 3 or 4 hexadecimal digits, meaning
12 or 16 bits of precision are recommended so that T-values are
reduced to 3 or 4 characters, so that 1/3 sampling may be encoded
as:

```
tracestate: ot=tv:aaab
```

Here is a table of T-value encoding, sampling probability, and
adjusted count as an exact expression and as a floating point value,
for probabilities in the range range between 1 to 1/16.  Rejection
thresholds which cannot be expressed as powers of two are approximate,
as shown.


| T-value | Probability (rational) | Adjusted count (exact)   | Adjusted count (floating point) |
|---------|------------------------|--------------------------|---------------------------------|
| 0       | 1                      | 1                        | 1                               |
| 4       | 3/4                    | 4 / 3                    | 1.33333333333                   |
| 555     | 2/3                    | 1 / (1 - 0x555/0x1000)   | 1.49981691688                   |
| 5555    | 2/3                    | 1 / (1 - 0x5555/0x10000) | 1.499988556                     |
| 8       | 1/2                    | 2                        | 2                               |
| aab     | 1/3                    | 1 / (1 - 0xaab/0x1000)   | 3.00073260073                   |
| aaab    | 1/3                    | 1 / (1 - 0xaaab/0x10000) | 3.00004577707                   |
| c       | 1/4                    | 4                        | 4                               |
| ccd     | 1/5                    | 1 / (1 - 0xccd/0x1000)   | 5.00122100122                   |
| cccd    | 1/5                    | 1 / (1 - 0xcccd/0x10000) | 5.00007629511                   |
| d       | 3/16                   | 1 / (1 - 0xd/0x10)       | 5.33333333333                   |
| e       | 1/8                    | 8                        | 8                               |
| f       | 1/16                   | 16                       | 16                              |

Here is a table covering smaller sampling probabilities, which
generally have leading `f` digits.  Note the use of variable precision
for non-power-of-two values, such as 1/24 which can be successively
approximated using `f` followed by one or more `5` digits.

| T-value        | Probability (rational) | Adjusted count (exact)         | Adjusted count (floating point) |
|----------------|------------------------|--------------------------------|---------------------------------|
| f0f            | 1/17                   | 1/(1 - 0xf0f/0x100)            | 16.9958506224                   |
| f555           | 1/24                   | 1/(1 - 0xf555/0x10000)         | 23.9970706701                   |
| f555555        | 1/24                   | 1/(1 - 0xf555555/0x10000000)   | 23.9999992847                   |
| f8             | 1/32                   | 32                             | 32                              |
| faab           | 1/48                   | 1/(1 - 0xfaab/0x10000)         | 48.0117216117                   |
| faaaaab        | 1/48                   | 1/(1 - 0xfaaaaab/0x10000000)   | 48.000002861                    |
| fc             | 1/64                   | 64                             | 64                              |
| fd27d          | 1/90                   | 1/(1 - 0xfd27d/0x100000)       | 89.9987983864                   |
| fd27d27d       | 1/90                   | 1/(1 - 0xfd27d27d/0x100000000) | 89.9999997066                   |
| fe             | 1/128                  | 128                            | 128                             |
| ff             | 1/256                  | 256                            | 256                             |
| ffff           | 2**-16                 | 2**16                          | 2**16                           |
| ffffff         | 2**-24                 | 2**24                          | 2**24                           |
| ffffffff       | 2**-32                 | 2**32                          | 2**32                           |
| ffffffffff     | 2**-40                 | 2**40                          | 2**40                           |
| ffffffffffff   | 2**-48                 | 2**48                          | 2**48                           |
| ffffffffffffff | 2**-56                 | 2**56                          | 2**56                           |

##### Requirement: Out-of-range T-values are unset

Consumers SHOULD unset T-value from the `tracestate` if the encoded
value encoding is not between one and 14 bytes, all valid hexadecimal
digits, before using the `tracestate` to make a sampling decision or
interpret adjusted count.

#### R-value

R-value is optionally set in the `tracestate` by the Sampler at the
root of the trace, in order to support consistent probability sampling
without the use of TraceID randomness.  R-value is encoded using the
sub-key `rv` in the OpenTelemetry tracestate section, conveying a
56-bit random number using 14 hexadecimal digits.

By making R-value optional in this way, it is possible for
special-purpose instrumentation to achieve consistent probability
sampling across multiple traced contexts.

##### Requirement: Out-of-range R-values unset both T-value and R-value

Samplers SHOULD unset both T-value and R-value from the `tracestate`
if the value of `rv` is not exactly 14 hexadecimal digits, before
using the `tracestate` to make a sampling decision.

##### Requirement: R-value is generated using 56 random bits

Samplers MUST generate R-values using a randomized scheme that
produces each bit using a uniform, independent source of randomness.

#### Examples: Context invariants

##### Example: Probability sampled context

Consider a trace context with the following headers:

```
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-03
tracestate: ot=tv:c
```

The `traceparent` contents in this example example are repeated from
the [W3C specification](https://www.w3.org/TR/trace-context/#examples-of-http-traceparent-headers))
and have the following base64-encoded field values:

```
base16(version) = 00
base16(trace-id) = 4bf92f3577b34da6a3ce929d0e0e4736
base16(parent-id) = 00f067aa0ba902b7
base16(trace-flags) = 03  // (i.e., sampled, random)
```

The `tracestate` header contains OpenTelemetry string `tv:c`,
containing a hex-encoded T-value (`c`).  Because it has no explicit
R-value, the R-value can be derived from the trailing 14 digits of
hexadecimal-encoded TraceID, which is `ce929d0e0e4736` in this example.

```
base16(rv) = ce929d0e0e4736
base10(th) = c0000000000000
```

Here, R-value ce929d0e0e4736 indicates that a consistent probability
sampler configured with probability greater than approximately 19.3%,
the exact probability threshold being expressed as `1 - 0xce929d0e0e4736 / 0x100000000000000`.

Since the T-value is less than or equal to the R-value, in this case
(i.e., `T <= R`), we expect the `sampled` flag to be set.

##### Example: Probability unsampled context

This example has an unsampled context where no tracestate is provided,
with the random flag set.

```
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-02
```

T-value is not set, consistent with an unsampled context.  In this
case, the parent context could have been sampled at less than 19.3%
probability or used the `AlwaysOff` sampler.

##### Example: Probability sampled, explicit R-value context

This example has an sampled context with an explicit R-value and no
random flag set.

```
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
tracestate: ot=tv:8;rv:8d64684bac31e
```

T-value indicates 50% sampling, which is consistent with the explicit
R-value and `sampled` flag being set.

```
base16(rv) = 8d64684bac31e
base10(th) = 80000000000000
```

### Samplers

#### ParentBased sampler extensions

A consistent-probability `ParentBased` sampler is is required to first
validate `tracestate` invariants and then respect the `sampled` flag
in the W3C traceparent.

##### Requirement: ParentBased does not modify valid tracestate

A consistent-probability `ParentBased` Sampler MUST NOT modify a valid `tracestate`.

##### Requirement: ParentBased calls the configured root sampler for root spans

A consistent-probability `ParentBased` Sampler MUST delegate to the
configured root Sampler when there is not a valid parent trace
context.

##### Requirement: ParentBased respects the sampled flag for non-root spans

A consistent-probability `ParentBased` Sampler MUST decide to sample
the span according to the value of the `sampled` flag in the W3C
traceparent header.

#### TraceIdRatioBased sampler extensions

A consistent-probability `TraceIdRatioBased` sampler is required to
produce a valid `tracestate` containing T-value and optional R-value
when it decides to sample a context.  In the case where it is used in
a non-root context, it is required to validate the incoming
`tracestate` and to produce a valid `tracestate` for the outgoing
context.

##### Requirement: TraceIdRatioBased sampler unsets T-value when not sampled

The `TraceIdRatioBased` Sampler MUST unset T-value from the
`tracestate` when it decides not to sample.

##### Requirement: TraceIdRatioBased sampler sets T-value when sampled

The `TraceIdRatioBased` Sampler MUST set T-value when it decides to
sample according to its configured sampling probability.

##### Requirement: TraceIdRatioBased sampler records unbiased adjusted counts

The `TraceIdRatioBased` Sampler MUST set T-value so that the adjusted
count interpreted from the `tracestate` is an unbiased estimate of the
number of representative spans in the population.

##### Requirement: TraceIdRatioBased sampler supports probabilities between 1 and than 2**-56

If the configured sampling probability is not in the interval `[1,
2**-56)`, the Sampler MUST be replaced by an `AlwaysOff` sampler.

### Composition rules

When more than one Sampler participates in the decision to sample a
context, their decisions can be combined using composition rules.  In
all cases, the combined decision to sample is the logical-OR of the
Samplers' decisions (i.e., sample if at least one of the composite
Samplers decides to sample).

To combine T-values from two consistent probability Sampler decisions,
the Sampler with the greater probability takes effect.  The output
T-value becomes the minimum of the two T-values.

To combine a consistent probability Sampler decision with a
non-probability Sampler decision, T-value should be set according to
the probability sampler(s).  If no probability sampler decides to
sample, no T-value should be set.

### Producer and consumer recommendations

#### Trace producer: completeness

As stated in the [completeness guarantee](#completeness-guarantee),
traces will be possibly incomplete when configuring multiple
consistent probability samplers in the same trace.  One way to avoid
producing incomplete traces is to use parent-based samplers except for
root spans.

There is a simple test for trace incompleteness, but it is a one-way
test and does not detect when child spans are uncollected.  One way to
avoid producing incomplete traces is to avoid configuring
TraceIdRatioBased Samplers for non-root spans (i.e., always use
ParentBased Samplers).

##### Recommendation: use non-descending probabilities

Complete subtraces will be produced when the sequence of sampling
probabilities from the root of a trace to its leaves consists of
non-descending.  To ensure complete sub-traces are produced, child
samplers SHOULD be configured with a probability greater than or equal
to the parent span's sampling probability.

#### Trace producer: correctness

The use of tracestate to convey adjusted count information rests upon
trust between participants in a trace.  Users are advised not to use a
Span-to-metrics pipeline when the parent sampling decision's
corresponding adjusted count is untrustworthy.

The `TraceIdRatioBased` and `ParentBased` samplers can be used as
delegates of another sampler, for conditioning the choice of sampler
on span and other fixed attributes.  However, for adjusted counts to
be trustworthy, the choice of non-root sampler cannot be conditioned
on the parent's sampled trace flag or the OpenTelemetry tracestate
R-value or T-value, as these decisions would lead to incorrect
adjusted counts.

For example, the built-in [`ParentBased` sampler](sdk.md#parentbased)
supports configuring the delegated-to sampler based on whether the
parent context is remote or non-remote, sampled or unsampled.  If a
`ParentBased` sampler delegates to a `TraceIdRatioBased` sampler only
for unsampled contexts, the resulting Span-to-metrics pipeline will
(probably) overcount spans.

#### Trace producer: interoperability with legacy `ParentBased` sampler

The legacy built-in `ParentBased` sampler is interoperable with the
consistent-probability `TraceIdRatioBased` sampler, provided that the
delegated-to sampler does not change the decision that determined its
selection.  For example, it is safe to configure an alternate
`ParentBased` sampler delegate for unsampled spans, provided the
decision does not change to sampled.

Because the `ParentBased` sampler honors the sampled trace flag, and
OpenTelemetry SDKs include the tracestate in the `Span` data, a system
can be upgraded to probability sampling by just replacing
`TraceIdRatioBased` samplers with conforming consistent-probability
`TraceIdRatioBased` samplers everywhere in the trace and it is not
necessary to upgrade legacy `ParentBased` samplers.

#### Trace producer: interoperability with legacy `TraceIdRatioBased` sampler

The [`TraceIdRatioBased` specification](sdk.md#traceidratiobased)
includes a RECOMMENDATION against being used for non-root spans
because it does not specify how to make the sampler decision
consistent across the trace.

When a legacy `TraceIdRatioBased` sampler is configured for a non-root
span, cases arise where an incorrect OpenTelemetry tracestate can be
generated.  For example, when a root uses a consistent-probability
`TraceIdRatioBased` sampler but the child uses a legacy
`TraceIdRatioBased` sampler, the grand-child's trace context may carry
the T-value from the root despite being effectively sampled by the
child.

As these cases demonstrate, users can expect incompleteness and
incorrect adjusted count when combining legacy `TraceIdRatioBased`
samplers for non-root spans with consistent-probability
`TraceIdRatioBased` samplers, but this goes against the originally
specified warning.

#### Trace consumer

Trace consumers are expected to apply the simple one-way test for
incompleteness.  When non-root spans are configured with independent
sampling probabilities, traces may be complete in a way that cannot be
detected.  Because of the one-way test, consumers wanting to ensure
complete traces are expected to know the minimum sampling probability
across the system.

Ignoring accidental data loss, a trace will be complete if all its
spans are sampled with consistent probability samplers and the trace's
effective or explicit R-value is greater than or equal to the greatest
rejection threshold across spans in the trace.

##### Recommendation: Recognize inconsistent R-values

When a single trace contains spans with `tracestate` values containing
more than one distinct, explicit value for R-value, the consumer
SHOULD recognize the trace as inconsistently sampled.
