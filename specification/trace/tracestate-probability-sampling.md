<!--- Hugo front matter used to generate the website version of this page:
linkTitle: Probability Sampling
--->

# TraceState: Probability Sampling

**Status**: [Development](../document-status.md)

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [Overview](#overview)
- [Definitions](#definitions)
  * [Sampling Probability](#sampling-probability)
  * [Consistent Sampling Decision](#consistent-sampling-decision)
  * [Rejection Threshold (`th`)](#rejection-threshold-th)
  * [Randomness Value (`rv`)](#randomness-value-rv)
  * [Consistent Sampling Decision Approach](#consistent-sampling-decision-approach)
- [Sampler behavior for initializing and updating `th` and `rv` values](#sampler-behavior-for-initializing-and-updating-th-and-rv-values)
  * [Head samplers](#head-samplers)
  * [Downstream samplers](#downstream-samplers)
  * [Migration to consistent probability samplers](#migration-to-consistent-probability-samplers)
- [Algorithms](#algorithms)
  * [Converting floating-point probability to threshold value](#converting-floating-point-probability-to-threshold-value)
  * [Converting integer threshold to a `th`-value](#converting-integer-threshold-to-a-th-value)
  * [Testing randomness vs threshold](#testing-randomness-vs-threshold)
  * [Converting threshold to a sampling probability](#converting-threshold-to-a-sampling-probability)
  * [Converting threshold to an adjusted count (sampling rate)](#converting-threshold-to-an-adjusted-count-sampling-rate)

<!-- tocstop -->

</details>

## Overview

Sampling is an important lever to reduce the costs associated with collecting and processing telemetry data.
It enables you to choose a representative set of items from an overall population.

There are two key aspects for sampling of tracing data.
The first is that sampling decisions can be made independently for *each* span in a trace.
The second is that sampling decisions can be made at multiple points in the telemetry pipeline.
For example, the sampling decision for a span at span creation time could have been to **keep** that span, while the downstream sampling decision for the *same* span at a later stage (say in an external process in the data collection pipeline) could be to **drop** it.

For each of the above aspects, if we don't make **consistent** sampling decisions, we will end up with traces that are unusable and do not contain a coherent set of spans, because of the independent sampling decisions.
Instead, we want sampling decisions to be made in a **consistent** manner so that we can effectively reason about a trace.

This specification describes how to achieve consistent sampling decisions using a mechanism called **Consistent Probability Sampling**.
To achieve this, it uses two key building blocks.
The first is a common source of randomness (`rv`) that is available to all participants, which includes a set of tracers and collectors.
This can be either an explicit randomness value (called `rv`) or taken from the trailing 7 bytes of the TraceID.
The second is a concept of a rejection threshold (`th`). This is derived directly from a participant's sampling rate.
This proposal describes how these two values should be propagated and how participants should use them to make sampling decisions.

For more details about this specification, see [OTEP 235](https://github.com/open-telemetry/oteps/blob/main/text/trace/0235-sampling-threshold-in-trace-state.md).

## Definitions

### Sampling Probability

Sampling probability is the likelihood that a span will be *kept*. Each participant can choose a different sampling probability for each span.
For example, if the sampling probability is 0.25, around 25% of the spans will be kept.

In OpenTelemetry, sampling probability is valid in the range 2^-56 through 1.
The value 56 appearing in this expression corresponds with 7 bytes of randomness (i.e., 56 bits) which are specified for W3C Trace Context Level 2 TraceIDs.
Note that the zero value is not defined and that "never" sampling is not a form of probability sampling.

### Consistent Sampling Decision

A consistent sampling decision means that a positive sampling decision made for a particular span with probability p1 necessarily implies a positive sampling decision for any span belonging to the same trace if it is made with probability p2 >= p1.

### Rejection Threshold (`th`)

This is a 56-bit value directly derived from the sampling probability.
One way to think about this is that this is the number of spans that would be *dropped* out of 2^56 considered spans.

You can derive the rejection threshold from the sampling probability as follows:

```
Rejection_Threshold = (1 - Sampling_Probability) * 2^56.
```

For example, if the sampling probability is 100% (keep all spans), the rejection threshold is 0.

Similarly, if the sampling probability is 1% (drop 99% of spans), the rejection threshold with 5 digits of precision would be (1-0.01) * 2^56 ≈ 71337018784743424 = 0xfd70a400000000.

We refer to this rejection threshold as `th`.
We represent it using the OpenTelemetry TraceState key `th`, where the value is propagated and also stored with each span.
In the example above, the `th` key has `fd70a4` as the value, because trailing zeros are removed.

See [tracestate handling](./tracestate-handling.md#sampling-threshold-value-th) for details about encoding threshold values.

### Randomness Value (`rv`)

A common random value (that is known or propagated to all participants) is the main ingredient that enables consistent probability sampling.
Each participant can compare this value (`rv`) with their rejection threshold (`th`) to make a consistent sampling decision across an entire trace (or even across a group of traces).

This proposal supports two sources of randomness:

- **An explicit source of randomness**: OpenTelemetry supports a *random* (or pseudo-random) 56-bit value known as explicit trace randomness. This can be propagated through the OpenTelemetry TraceState `rv` sub-key and is stored in the Span's TraceState field.
- **Using TraceID as a source of randomness**: OpenTelemetry supports using the [least-significant 56 bits of the TraceID as the source of randomness, as specified in W3C Trace Context Level 2][W3CCONTEXTTRACEID]. This can be done if the root Span's Trace SDK knows that the TraceID has been generated in a random or pseudo-random manner.

[W3CCONTEXTTRACEID]: https://www.w3.org/TR/trace-context-2/#randomness-of-trace-id

See [tracestate handling](./tracestate-handling.md#explicit-randomness-value-rv) for details about encoding randomness values.

## Approach and Terminology

### Decision algorithm

Given the above building blocks, let's look at how a participant can make consistent sampling decisions.
For this, two values MUST be present in the `SpanContext`:

1. The common source of randomness: the 56-bit `rv` value.
2. The rejection threshold: the 56-bit `th` value.

If `rv` >= `th`, *keep* the span, else *drop* the span.

### Sampling stages

The two sampling aspects mentioned in the overview are hereby referred to as:

1. Parent/Child sampling. These decisions are made for spans inside an SDK, synchronously, during the life of a trace. These decisions are based on live Contexts.
2. Downstream sampling. These sampling decisions happen for spans on the collection path, after they finish, and may happen at multiple locations in collection pipeline.

We recognize these as two dimensions in which Sampling decisions are
made.  In Parent/Child sampling, there is a progression in the
direction of causality, from parent to child forward in time.  In
Downstream sampling, there is a progression from collector to
collector forward in time.  Considering a finished span at a moment in
time, it will have been sampled once by a Parent/Child sampler and
zero or more times by a Collector.

### Sampling base cases

The CompositeSampler is meant to support combining multiple sampling
rules into one using built-in ComposableSamplers as the base cases.

Within the category of Parent/Child sampling, there are three primary
base cases:

- Root: The Root sampling decision is the first decision in both
  sampling dimensions, made with no prior threshold. The Root sampling
  decision is the only case where it is permitted to modify the
  explicit trace randomness value for a Context.
- Parent-based: When using parent-based sampling at a child, we expect
  the child's decision to match the parent's decision.  The parent and
  child will have matching threshold values.
- Consistent probability: A probability sampler (e.g., TraceIDRatio)
  makes an independent sampling decision.  A consistent probability
  sampling decision ignores the parent's sampling threshold (if any).

Some terms are not about one specific sampler, but about the approach:

- Head: This mode of sampling implies that Root samplers use a
  consistent probability base case and Child samplers are
  parent-based. This term does not reflect on the mode or behavior of
  Downstream samplers. By contrast, "Not Head" sampling means an
  approach that uses unequal probabilities across Parent/Child
  samplers withinin a trace.
- Tail: This mode of sampling implies that Downstream samplers are
  involved the decision. Sometimes this refers to sampling of
  individual spans on the collection path (known as "intermediate"
  sampling), but usually it refers to whole-trace sampling decisions
  made downstream after assembling multiple spans into a single data
  set.  Tail sampling may be combined with Head sampling, of course,
  and may or may not contribute unequal probabilities across spans
  within a trace.

## Sampler behavior for initializing and updating `th` and `rv` values

`th` represents the maximum threshold that was applied in all previous consistent sampling stages.
If the current sampling stage applies a greater threshold value than any stage before, it MUST update (increase) the threshold correspondingly by re-encoding the OpenTelemetry TraceState value.

### Head samplers

See [SDK requirements for trace randomness](./sdk.md#sampling-requirements), which covers potentially inserting explicit trace randomness using the OpenTelemetry TraceState `rv` sub-key.

A head Sampler is responsible for computing the `th` value in a new span's [OpenTelemetry TraceState](./tracestate-handling.md#tracestate-handling). The main inputs to that computation include the parent context's TraceState and the TraceID.

When a span is sampled by in accordance with this specification, the output TraceState SHOULD be set to convey probability sampling:

- The `th` key MUST be defined with a threshold value corresponding to the sampling probability the sampler used.
- If trace randomness was derived from a OpenTelemetry TraceState `rv` sub-key value, the same `rv` value MUST be defined and equal to the incoming OpenTelemetry TraceState `rv` sub-key value.

### Downstream samplers

A downstream sampler, in contrast, may output a given ended Span with a *modified* trace state, complying with following rules:

- If the chosen sampling probability is 1, the sampler MUST NOT modify an existing `th` sub-key value, nor set a `th` sub-key value.
- Otherwise, the chosen sampling probability is in `(0, 1)`. In this case the sampler MUST output the span with a `th` equal to `max(input th, chosen th)`. In other words, `th` MUST NOT be decreased (as it is not possible to retroactively adjust an earlier stage's sampling probability), and it MUST be increased if a lower sampling probability was used. This case represents the common case where a downstream sampler is reducing span throughput in the system.

### Migration to consistent probability samplers

The OpenTelemetry specification for TraceIdRatioBased samplers was not completed until after the SDK specification was declared stable, and the exact behavior of that sampler was left unspecified.
The `th` and `rv` sub-keys defined in the OpenTelemetry TraceState now address this behavior specifically.

As the OpenTelemetry TraceIdRatioBased sampler changes definition, users must consider how to avoid incomplete traces due to inconsistent sampling during the transition between old and new logic.

The original TraceIdRatioBased sampler specification gave a workaround for the underspecified behavior, that it was safe to use for root spans: "It is recommended to use this sampler algorithm only for root spans (in combination with [`ParentBased`](./sdk.md#parentbased)) because different language SDKs or even different versions of the same language SDKs may produce inconsistent results for the same input."

To avoid inconsistency during this transition, users SHOULD follow this guidance until all Trace SDKs in a system have been upgraded to modern Trace randomness requirements based on W3C Trace Context Level 2.
Users can verify that all Trace SDKs have been upgraded when all Spans in their system have the Trace random flag set (in Span flags).
To assist with this migration, the TraceIdRatioBased Sampler issues a warning statement the first time it presumes TraceID randomness for a Context where the Trace random flag is not set.

## Algorithms

The `th` and `rv` values may be represented and manipulated in a variety of forms depending on the capabilities of the processor and needs of the implementation.
As 56-bit values, they are compatible with byte arrays and 64-bit integers, and can also be manipulated with 64-bit floating point with a truly negligible loss of precision.

The following examples are in Python3.
They are intended as examples only for clarity, and not as a suggested implementation.

### Converting floating-point probability to threshold value

Threshold values are encoded with trailing zeros removed, which allows for variable precision.
This can be accomplished by rounding, and there are several practical ways to do this with built-in string formatting libraries.

With up to 56 bits of precision available, implementations that use built-in floating point number support will be limited by the precision of the underlying number support.
One way to encode thresholds uses the IEEE 754-2008-standard hexadecimal floating point representation as a simple solution.

```python
import math

# ProbabilityToThresholdWithPrecision assumes the probability value is in the range
# [2^-56, 1] and precision is in the range [1, 13], which is the maximum for a
# IEEE-754 double-width float value.
def probability_to_threshold_with_precision(probability, precision):
    if probability == 1:
        # Special case
        return "0"

    # Raise precision by the number of leading 'f' digits.
    _, exp = math.frexp(probability)
    # Precision is limited to 12 so that there is at least one digit of precision
    # in the final [:precision] statement below.
    precision = max(1, min(12, precision + exp // -4))

    # Change the probability to 1 + rejection probability = 1 + 1 - probability,
    # i.e., modify the range (0, 1] into the range [1, 2).
    rejection_prob = 2 - probability

    # To ensure rounding correctly below, add an offset equal to half of the
    # final digit of precision in the corresponding representation.
    rejection_prob += math.ldexp(0.5, -4 * precision)

    # The expression above technically can't produce a number >= 2.0 because
    # of the compensation for leading Fs. This gives additional safety for
    # the hex_str[4:][:-3] expression below which blindly drops the exponent.
    if rejection_prob >= 2.0:
        digits = "fffffffffffff"
    else:
        # Use float.hex() to get hexadecimal representation
        hex_str = rejection_prob.hex()

        # The hex representation for values between 1 and 2 looks like '0x1.xxxxxxxp+0'
        # Extract the part after '0x1.' (4 bytes) and before 'p' (3 bytes)
        digits = hex_str[4:][:-3]

    assert len(digits) == 13
    # Remove trailing zeros
    return digits[:precision].rstrip('0')
```

Note the use of `math.frexp(probability)` used to adjust precision using the base-2 exponent of the probability argument.
This makes the configured precision apply to the significant digits of the threshold for probabilities near zero.
Note that there is not a symmetrical adjustment made for values near unit probability, as we do not believe there is a practical use for sampling very precisely near 100%.

To translate directly from floating point probability into a 56-bit unsigned integer representation using `math.Round()` and shift operations, see the [OpenTelemetry Collector-Contrib `pkg/sampling` package][PKGSAMPLING] package.
This package demonstrates how to directly calculate integer thresholds from probabilities.

[PKGSAMPLING]: https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/main/pkg/sampling/README.md

OpenTelemetry SDKs are recommended to use 4 digits of precision by default.
The following table shows values computed by the method above for 1-in-N probability sampling, with precision 3, 4, and 5.

<!--- Program at https://go.dev/play/p/7eLM6FkuoA5 (includes function above) generates the table below --->
| 1-in-N  | Input probability  | Threshold (precision 3, 4, 5)      | Actual probability (precision 3, 4, 5)                                       | Exact Adjusted Count (precision 3, 4, 5)                              |
|---------|--------------------|------------------------------------|------------------------------------------------------------------------------|-----------------------------------------------------------------------|
| 1       | 1                  | 0<br/>0<br/>0                      | 1<br/>1<br/>1                                                                | 1<br/>1<br/>1                                                         |
| 2       | 0.5                | 8<br/>8<br/>8                      | 0.5<br/>0.5<br/>0.5                                                          | 2<br/>2<br/>2                                                         |
| 3       | 0.3333333333333333 | aab<br/>aaab<br/>aaaab             | 0.333251953125<br/>0.3333282470703125<br/>0.33333301544189453                | 3.0007326007326007<br/>3.00004577706569<br/>3.0000028610256777        |
| 4       | 0.25               | c<br/>c<br/>c                      | 0.25<br/>0.25<br/>0.25                                                       | 4<br/>4<br/>4                                                         |
| 5       | 0.2                | ccd<br/>cccd<br/>ccccd             | 0.199951171875<br/>0.1999969482421875<br/>0.19999980926513672                | 5.001221001221001<br/>5.0000762951094835<br/>5.0000047683761295       |
| 8       | 0.125              | e<br/>e<br/>e                      | 0.125<br/>0.125<br/>0.125                                                    | 8<br/>8<br/>8                                                         |
| 10      | 0.1                | e66<br/>e666<br/>e6666             | 0.10009765625<br/>0.100006103515625<br/>0.10000038146972656                  | 9.990243902439024<br/>9.99938968568813<br/>9.999961853172863          |
| 16      | 0.0625             | f<br/>f<br/>f                      | 0.0625<br/>0.0625<br/>0.0625                                                 | 16<br/>16<br/>16                                                      |
| 100     | 0.01               | fd71<br/>fd70a<br/>fd70a4          | 0.0099945068359375<br/>0.010000228881835938<br/>0.009999990463256836         | 100.05496183206107<br/>99.99771123402633<br/>100.00009536752259       |
| 1000    | 0.001              | ffbe7<br/>ffbe77<br/>ffbe76d       | 0.0010004043579101562<br/>0.0009999871253967285<br/>0.000999998301267624     | 999.5958055290753<br/>1000.012874769029<br/>1000.0016987352618        |
| 10000   | 0.0001             | fff972<br/>fff9724<br/>fff97247    | 0.00010001659393310547<br/>0.00010000169277191162<br/>0.00010000006295740604 | 9998.340882002383<br/>9999.830725674266<br/>9999.99370426336          |
| 100000  | 0.00001              | ffff584<br/>ffff583a<br/>ffff583a5 | 9.998679161071777e-06<br/>1.00000761449337e-05<br/>1.0000003385357559e-05    | 100013.21013412817<br/>99999.238556461<br/>99999.96614643588          |
| 1000000 | 0.000001              | ffffef4<br/>ffffef39<br/>ffffef391 | 9.98377799987793e-07<br/>1.00000761449337e-06<br/>9.999930625781417e-07      | 1.0016248358208955e+06<br/>999992.38556461<br/>1.0000069374699865e+06 |

### Converting integer threshold to a `th`-value

To convert a 56-bit integer rejection threshold value to the `th` representation, emit it as a hexadecimal value (without a leading '0x'), optionally with trailing zeros omitted:

```py
if tvalue == 0:
  add_otel_trace_state('th:0')
else:
  h = hex(tvalue).rstrip('0')
  # remove leading 0x
  add_otel_trace_state('th:'+h[2:])
```

### Testing randomness vs threshold

Given randomness and threshold as 64-bit integers, a sample should be taken if randomness is greater than or equal to the threshold.

```
shouldSample = (randomness >= threshold)
```

### Converting threshold to a sampling probability

The sampling probability is a value from 0.0 to 1.0, which can be calculated using floating point by dividing by 2^56:

```py
# embedded _ in numbers for clarity (permitted by Python3)
maxth = 0x100_0000_0000_0000  # 2^56
prob = float(maxth - threshold) / maxth
```

### Converting threshold to an adjusted count (sampling rate)

The adjusted count indicates the approximate quantity of items from the population that this sample represents. It is equal to `1/probability`.

```py
maxth = 0x100_0000_0000_0000  # 2^56
adjCount = maxth / float(maxth - threshold)
```

Adjusted count is not defined for spans that were obtained via non-probabilistic sampling (a sampled span with no `th` value).
