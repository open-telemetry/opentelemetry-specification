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
  * [Rejection Threshold (T)](#rejection-threshold-t)
  * [Random Value (R)](#random-value-r)
  * [Consistent Sampling Decision Approach](#consistent-sampling-decision-approach)
- [Explanation](#explanation)
- [Sampler behavior for initializing and updating T and R values](#sampler-behavior-for-initializing-and-updating-t-and-r-values)
  * [Head samplers](#head-samplers)
  * [Downstream samplers](#downstream-samplers)
- [Algorithms](#algorithms)
  * [Converting floating-point probability to threshold value](#converting-floating-point-probability-to-threshold-value)
  * [Converting integer threshold to a `th`-value](#converting-integer-threshold-to-a-th-value)
  * [Testing randomness vs threshold](#testing-randomness-vs-threshold)
  * [Converting threshold to a sampling probability](#converting-threshold-to-a-sampling-probability)
  * [Converting threshold to an adjusted count (sampling rate)](#converting-threshold-to-an-adjusted-count-sampling-rate)

<!-- tocstop -->

</details>

## Overview

Sampling is an important lever to reduce the costs associated with collecting and processing telemetry data. It enables you to choose a representative set of items from an overall population.

There are two key aspects for sampling of tracing data. The first is that sampling decisions can be made independently for *each* span in a trace. The second is that sampling decisions can be made at multiple points in the telemetry pipeline. For example, the sampling decision for a span at span creation time could have been to **keep** that span, while the downstream sampling decision for the *same* span at a later stage (say in an external process in the data collection pipeline) could be to **drop** it.

For each of the above aspects, if we don't make **consistent** sampling decisions, we will end up with traces that are unusable and do not contain a coherent set of spans, because of the independent sampling decisions. Instead, we want sampling decisions to be made in a **consistent** manner so that we can effectively reason about a trace.

This specification describes a mechanism to achieve such consistent sampling decisions using a mechanism called **Consistent Probability Sampling**. To achieve this, it uses two key building blocks. The first is a common source of randomness (R) that is available to all participants. This can be either a custom value (called `rv`) or taken from the trailing 7 bytes of the TraceID. The second is a concept of a rejection threshold (T). This is derived directly from a participant's sampling rate. This proposal describes how these two values should be propagated and how participants should use them to make sampling decisions.

For more details about this specification, see [OTEP 235](https://github.com/open-telemetry/oteps/blob/main/text/trace/0235-sampling-threshold-in-trace-state.md).

## Definitions

### Sampling Probability

Sampling probability is the likelihood that a span will be *kept*. Each participant can choose a different sampling probability for each span. For example, if the sampling probability is 0.25, around 25% of the spans will be kept.

Sampling probability is valid in the range 2^-56 through 1.  Note that the zero value is not defined and that "never" sampling is not a form of probability sampling.

### Consistent Sampling Decision

A consistent sampling decision means that a positive sampling decision made for a particular span with probability p1 necessarily implies a positive sampling decision for any span belonging to the same trace if it is made with probability p2 >= p1.

### Rejection Threshold (T)

This is a 56-bit value directly derived from the sampling probability. One way to think about this is that this is the number of spans that would be *dropped* out of 2^56 considered spans. This is an alternative to the `p` value in the previous specification. The `p` value is limited to powers of two, while this supports a large range of values.

You can derive the rejection threshold from the sampling probability as follows:

```
Rejection_Threshold = (1 - Sampling_Probability) * 2^56.
```

For example, if the sampling probability is 100% (keep all spans), the rejection threshold is 0.

Similarly, if the sampling probability is 1% (drop 99% of spans), the rejection threshold with 5 digits of precision would be (1-0.01) * 2^56 = 4458562600304640 = 0xfd70a00000000.

We refer to this rejection threshold conceptually as `T`. We represent it using the key `th`. This must be propagated in both the `tracestate` header and in the TraceState attribute of each span.

See [tracestate handling](./tracestate-handling.md#sampling-threshold-value-th) for details about encoding threshold values.

### Random Value (R)

A common random value (that is known or propagated to all participants) is the main ingredient that enables consistent probability sampling. Each participant can compare this value (R) with their rejection threshold (T) to make a consistent sampling decision across an entire trace (or even across a group of traces).

This proposal supports two sources of randomness:

- **A custom source of randomness**: This proposal allows for a *random* (or pseudo-random) 56-bit value. We refer to this as `rv`. This can be generated and propagated through the `tracestate` header and the tracestate attribute in each span.
- **Using TraceID as a source of randomness**: This proposal introduces using the last 56 bits of the `traceid` as the source of randomness. This can be done if the root participant knows that the `traceid` has been generated in a random or pseudo-random manner.

See [tracestate handling](./tracestate-handling.md#sampling-randomness-value-rv) for details about encoding randomness values.

### Consistent Sampling Decision Approach

Given the above building blocks, let's look at how a participant can make consistent sampling decisions. For this, two values MUST be present in the `SpanContext`:

1. The common source of randomness: the 56-bit `R` value.
2. The rejection threshold: the 56-bit `T` value.

If `R` >= `T`, *keep* the span, else *drop* the span.

`T` represents the maximum threshold that was applied in all previous consistent sampling stages. If the current sampling stage applies a greater threshold value than any stage before, it MUST update (increase) the threshold correspondingly.

## Explanation

## Sampler behavior for initializing and updating T and R values

There are two categories of samplers:

- **Head samplers:** Implementations of [`Sampler`](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.29.0/specification/trace/sdk.md#sampler), called by a `Tracer` during span creation.
- **Downstream samplers:** Any component that, given an ended Span, decides whether to *drop* it or *keep* it (by forwarding it to the next component in the pipeline). This category is also known as "collection path samplers" or "sampling processors". Note that *Tail samplers* are a special class of downstream samplers that buffer spans of a trace and make a sampling decision for the trace as a whole using data from any span in the buffered trace.

This section defines the behavior for these two categories of samplers.

### Head samplers

A head sampler is responsible for computing the `rv` and `th` values in a new span's initial [`TraceState`](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.29.0/specification/trace/api.md#tracestate). The main inputs to that computation include the parent span's trace state (if a parent span exists), the new span's trace ID, and possibly the trace flags (to know if the trace ID has been generated in a random manner).

First, a consistent probability `Sampler` may choose its own sampling rate. The higher the chosen sampling rate, the lower the rejection threshold (T). It MAY select any value of T. If a valid `SpanContext` is provided in the call to `ShouldSample` (indicating that the span being created will be a child span), there are two possibilities:

- **The child span chooses a T greater than the parent span's T**: The parent span may be *kept* but it is possible that its child, the current span, may be dropped because of the lower sampling rate. At the same time, in the case where the decision for the child span is to *keep* it, the decision for the parent span would have also been to *keep* (due to our consistent sampling approach) since the parent's sampling rate is greater than the child's sampling rate.
- **The child span chooses a T less than or equal to the parent span's T**:  The parent span might have been *dropped* but it is possible that its child, the current span, may be *kept* because of the higher sampling rate. At the same time, in case where the parent span is *kept*, the child span would be *kept* as well (due to our consistent sampling approach) since the child's sampling rate is greater than the parent's sampling rate.

Note that while both the above cases can result in incomplete traces, they still meet the consistent sampling goals.

For the output TraceState,

- The `th` key MUST be defined with a value corresponding to the sampling probability the sampler used.
- The `rv` value, if present on the input TraceState, MUST be defined and equal to the incoming span context's `rv` value, including the root context.

Trace SDKs are responsible for for synthesizing `rv` values in the OpenTelemetry TraceState root span contexts.

### Downstream samplers

A downstream sampler, in contrast, may output a given ended Span with a *modified* trace state, complying with following rules:

- If the chosen sampling probability is 1, the sampler MUST NOT modify any existing `th`, nor set any `th`.
- Otherwise, the chosen sampling probability is in `(0, 1)`. In this case the sampler MUST output the span with a `th` equal to `max(input th, chosen th)`. In other words, `th` MUST NOT be decreased (as it is not possible to retroactively adjust an earlier stage's sampling probability), and it MUST be increased if a lower sampling probability was used. This case represents the common case where a downstream sampler is reducing span throughput in the system.

## Algorithms

The `th` and `rv` values may be represented and manipulated in a variety of forms depending on the capabilities of the processor and needs of the implementation. As 56-bit values, they are compatible with byte arrays and 64-bit integers, and can also be manipulated with 64-bit floating point with a truly negligible loss of precision.

The following examples are in Golang and Python3. They are intended as examples only for clarity, and not as a suggested implementation.

### Converting floating-point probability to threshold value

Threshold values are encoded with trailing zeros removed, which allows for variable precision.  This can be accompolished by rounding, and there are several practical way to do this with built-in string formatting libraries.

With up to 56 bits of precision available, implementations that use built-in floating point number support will be limited by the precision of the underlying number support.  If the language supports IEEE 754-2008-standard hexadecimal floating point, for example in Golang,

```go
// ProbabilityToThresholdWithPrecision assumes the probability value is in the range
// [0x1p-56, 1] and precision is in the range [1, 14].
func ProbabilityToThresholdWithPrecision(probability float64, precision int) string {
    if probability == 1 {
        // Special case
        return "0"
    }
    // Raise precision by the number of leading 0s or Fs
    _, expF := math.Frexp(probability)
    _, expR := math.Frexp(1 - probability)
    precision = min(14, max(precision+expF/-4, precision+expR/-4))

    // Change the probability to rejection probability, with range [0, 1),
    // translate rejection probability by +1, into range [1, 2).
    // Format the significand of this expression as hexadecimal floating point
    asHex := strconv.FormatFloat(2-probability, 'x', precision, 64)

    // Strip the leading "0x1.", use the requested number of digits.
    // Strip additional trailing zeros.
    digits := asHex[4 : 4+precision]
    return strings.TrimRight(digits, "0")
}
```

To translate directly from floating point probability into a 56-bit unsigned integer representation using `math.Round()` and shift operations, see the [OpenTelemetry Collector-Contrib `pkg/sampling` package][PKGSAMPLING] package demonstrates this form of directly calculating integer thresholds from probabilities.

[PKGSAMPLING]: https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/main/pkg/sampling/README.md

OpenTelemetry SDKs are recommended to use 4 digits of precision by default. The following table shows values computed by the method above for 1-in-N probability sampling, with precision 3, 4, and 5.

<!--- Program at https://go.dev/play/p/7eLM6FkuoA5 (includes function above) generates the table below --->
| 1-in-N  | Input probability  | Threshold (precision 3, 4, 5)      | Actual probability (precision 3, 4, 5)                                       | Exact Adjusted Count (precision 3, 4, 5)                              |
|---------|--------------------|------------------------------------|------------------------------------------------------------------------------|-----------------------------------------------------------------------|
| 1000000 | 1e-06              | ffffef4<br/>ffffef39<br/>ffffef391 | 9.98377799987793e-07<br/>1.00000761449337e-06<br/>9.999930625781417e-07      | 1.0016248358208955e+06<br/>999992.38556461<br/>1.0000069374699865e+06 |
| 100000  | 1e-05              | ffff584<br/>ffff583a<br/>ffff583a5 | 9.998679161071777e-06<br/>1.00000761449337e-05<br/>1.0000003385357559e-05    | 100013.21013412817<br/>99999.238556461<br/>99999.96614643588          |
| 10000   | 0.0001             | fff972<br/>fff9724<br/>fff97247    | 0.00010001659393310547<br/>0.00010000169277191162<br/>0.00010000006295740604 | 9998.340882002383<br/>9999.830725674266<br/>9999.99370426336          |
| 1000    | 0.001              | ffbe7<br/>ffbe77<br/>ffbe76d       | 0.0010004043579101562<br/>0.0009999871253967285<br/>0.000999998301267624     | 999.5958055290753<br/>1000.012874769029<br/>1000.0016987352618        |
| 100     | 0.01               | fd71<br/>fd70a<br/>fd70a4          | 0.0099945068359375<br/>0.010000228881835938<br/>0.009999990463256836         | 100.05496183206107<br/>99.99771123402633<br/>100.00009536752259       |
| 16      | 0.0625             | f<br/>f<br/>f                      | 0.0625<br/>0.0625<br/>0.0625                                                 | 16<br/>16<br/>16                                                      |
| 10      | 0.1                | e66<br/>e666<br/>e6666             | 0.10009765625<br/>0.100006103515625<br/>0.10000038146972656                  | 9.990243902439024<br/>9.99938968568813<br/>9.999961853172863          |
| 8       | 0.125              | e<br/>e<br/>e                      | 0.125<br/>0.125<br/>0.125                                                    | 8<br/>8<br/>8                                                         |
| 5       | 0.2                | ccd<br/>cccd<br/>ccccd             | 0.199951171875<br/>0.1999969482421875<br/>0.19999980926513672                | 5.001221001221001<br/>5.0000762951094835<br/>5.0000047683761295       |
| 4       | 0.25               | c<br/>c<br/>c                      | 0.25<br/>0.25<br/>0.25                                                       | 4<br/>4<br/>4                                                         |
| 3       | 0.3333333333333333 | aab<br/>aaab<br/>aaaab             | 0.333251953125<br/>0.3333282470703125<br/>0.33333301544189453                | 3.0007326007326007<br/>3.00004577706569<br/>3.0000028610256777        |
| 2       | 0.5                | 8<br/>8<br/>8                      | 0.5<br/>0.5<br/>0.5                                                          | 2<br/>2<br/>2                                                         |
| 1       | 1                  | 0<br/>0<br/>0                      | 1<br/>1<br/>1                                                                | 1<br/>1<br/>1                                                         |

### Converting integer threshold to a `th`-value

To convert a 56-bit integer threshold value to the t-value representation, emit it as a hexadecimal value (without a leading '0x'), optionally with trailing zeros omitted:

```py
h = hex(tvalue).rstrip('0')
# remove leading 0x
tv = 'tv='+h[2:]
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
