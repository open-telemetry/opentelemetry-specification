# Add exponential bucketing to histogram protobuf

Add exponential bucketing to histogram protobuf

## Motivation

Currently, the OTEL protobuf [protocol](https://github.com/open-telemetry/opentelemetry-proto/blob/main/opentelemetry/proto/metrics/v1/metrics.proto) only supports explicit bound buckets. Each bucket's bound and count must be explicitly defined. This is inefficient to transport buckets whose bounds have a pattern, such as exponential (ie. log scale) buckets. More importantly, without bucket pattern info, the receiver may not be able to optimize its processing on these buckets. With a protocol that also supports exponential buckets, the bounds can be encoded with just a few parameters, regardless of the number of buckets, and the receiver can optimize processing based on the knowledge that these buckets are exponential.

The explicit bucket type will be kept, as a fallback for arbitrary bucket bounds. For example, Prometheus histograms often come with arbitrary user defined bounds.

Exponential buckets are chosen to be added because they are very good at representing [long tail](https://en.wikipedia.org/wiki/Long_tail) distributions, which are common in the OTEL target application like response time measurement. Exponential buckets (ie. log scale buckets) need far fewer buckets than linear scale buckets to cover the wide range of a long tail distribution. Furthermore, percentiles/quantiles can be computed from exponential buckets with constant relative error across the full range.

## Explanation

Exponential buckets will be added. In general, bucket bounds are in the form of:

```
bound = base ^ exponent
```

where base is a parameter of a bound series, and exponent is an integer. Note that exponent may be positive, negative, or 0. Such bounds are also commonly known as "log scale bounds".

## Internal details

Proposed message type to be added:

```
message ExponentialBuckets {
    double base = 1;
    double zero_count = 2; // Count of values exactly at zero.
    ExponentialBucketCounts positive_value_counts = 3;
    ExponentialBucketCounts negative_value_counts = 4; // Negative values are bucketed with their absolute values
}

// "repeated double bucket_counts" represents an array of N numbers from bucket_counts[0] to bucket_counts[N-1].
// With index i starting at 0, ending at N-1, ExponentialBucketCounts defines N buckets, where
// bucket[i].start_bound = base ^ (i + exponent_offset)
// bucket[i].end_bound = base ^ (i + 1 + exponent_offset)
// bucket[i].count = bucket_counts[i]
message ExponentialBucketCounts {
    sint32 exponent_offset = 1; // offset may be negative.
    repeated double bucket_counts = 2;
}
```

Notes:

* ExponentialBuckets will be added as "oneof" the bucket types in [#272](https://github.com/open-telemetry/opentelemetry-proto/pull/272)
* Per [#257](https://github.com/open-telemetry/opentelemetry-proto/issues/257), only a histogram accepting "double" will be defined.
* Per [#259](https://github.com/open-telemetry/opentelemetry-proto/issues/259), bucket counts type is "double".

## Trade-offs and mitigations

Simplicity is a main design goal. The format targets the most common scenarios. For now, histograms not conforming to ExponentialBuckets may be encoded as explicit buckets. If a histogram type is common enough, a new bucket type may be added in the future.

The followings are restrictions of ExponentialBuckets:

* Buckets for positive and negative values must have the same "base".
* Buckets must cover the full value range. In the future, ExponentialBucketCounts might add an overflow_count and an underflow_count for counts above the highest bucket and below the lowest buckets, respectively. However, overflow or underflow bucket breaks the "pure log scale" property. "Rescale" is preferred when reducing memory cost. See "merge" section below.
* ExponentialBucketCounts is designed for dense buckets. Between the lowest and the highest bucket, most buckets are expected to be non-empty. This is the common case in telemetry applications.
* A "reference" that multiplies onto all bounds is not included. It is always implicitly 1.

## Prior art and alternatives

[#226](https://github.com/open-telemetry/opentelemetry-proto/pull/226) tried to add multiple histogram types at once. This EP reduces the scope to exponential histogram only. And the complexity of the new format is lower because we now decided that histogram types do not share the count fields (see [#259](https://github.com/open-telemetry/opentelemetry-proto/issues/259)).

## Open questions

### Toward universally mergeable histograms

Merging histograms of different types, or even the same type, but with different parameters remains an issue. There are lengthy discussions in [#226](https://github.com/open-telemetry/opentelemetry-proto/pull/226#issuecomment-776526864)

Some merge method may introduce artifacts (information not present in original data). Generally, splitting a bucket introduces artifacts. For example, when using linear interpolation to split a bucket, we are assumming uniform distribution within the bucket. "Uniform distribution" is information not present in original data. Merging buckets on the other hand, does not introduce artifacts. Merging buckets with identical bounds from two histograms is totally artifact free. Merging multiple adjacent buckets in one histogram is also artifact free, but it does reduce the resolution of the histogram. Whether such a merge is "lossy" is arguable. Because of this ambiguity, the term "lossy" is not used in this doc.

For exponential histograms, if base1 = base2 ^ N, where N is an integer, the two histograms can be merged without artifacts. Furthermore, we can introduce a series of bases where

```
base = referenceBase ^ (2 ^ baseScale)
```

Any two histograms using bases from the series can be merged without artifact. This approach is well known and in use in multiple vendors, including [Google internal use](https://github.com/open-telemetry/opentelemetry-proto/pull/226#issuecomment-737496026), [New Relic Distribution Metric](https://docs.newrelic.com/docs/data-apis/understand-data/metric-data/metric-data-type/). It is also described in the [UDDSketch paper](https://arxiv.org/pdf/2004.08604).

Such "2 to 1" binary merge has the following benefits:

* Any 2 histograms in the series can be merged without artifacts. This is a very attractive property.
* A single histogram may be shrunk by 2x using a 2 to 1 merge, at the cost of increasing base to base^2. When facing the choice between "reduced histogram resolution" and "blowing up application memory", shrinking is the obvious choice.

A histogram producer may implement "auto scale" to control memory cost. With a reasonable default config on target relative error and max number of buckets, the producer could operate in an "automagic" fashion. The producer can start with a base at target resolution, and dynamically change the scale if incoming data's range would make the histogram exceed the memory limit. [New Relic](https://docs.newrelic.com/docs/data-apis/understand-data/metric-data/metric-data-type/) and [Google](https://github.com/open-telemetry/opentelemetry-proto/pull/226#issuecomment-737496026) have implemented such logic for internal use. Open source versions from these companies are in plan.

The main disadvantage of scaled exponential histogram is not supporting arbitrary base. The base can only increase by square, or decrease by square root. Unless a user's target relative error is exactly on the series, they have to choose the next smaller base, which costs more space for the target. But in return, you get universally mergeable histograms, which seems like a reasonable trade off. As shown in discussions below, typically, the user has the choice around 1%, 2%, or 4% errors. Since error target is rarely precise science, choosing from the limited menu does not add much burden to the user.

**If we can agree on a "referenceBase", then we have universally mergeable histograms.** In [#226](https://github.com/open-telemetry/opentelemetry-proto/pull/226#issuecomment-777922339), a referenceBase of 2 was proposed. The general form for the series is

```
base = 2 ^ (2 ^ baseScale)
```

where baseScale is an integer.

* When baseScale = 0, base is exactly at referenceBase
* When baseScale > 0, 2^baseScale reference base buckets are merged into one
* When baseScale < 0, a reference base bucket (log2 bucket here) is sub-divided into 2^(-baseScale) subBuckets

In practice, the most interesting range of baseScale is around -4, where percentile relative error is around a few percent. The following table shows bases of interest. Here relative error is computed from "squareRoot(base) - 1". This assumes that percentile calculation returns the log scale mid point of a bucket to minimize relative error.

```
scale   #subBuckets base         relative_error
-3       8          1.090507733  4.43%
-4      16          1.044273782  2.19%
-5      32          1.021897149  1.09%
```

The [comment in #226](https://github.com/open-telemetry/opentelemetry-proto/pull/226#issuecomment-777922339) has more details on why 2 was chosen as the reference base. In summary, "computers like binary numbers". If we are going to choose a reference base, why not make it 2 ("10" in binary)?

### Base10 vs. base2

Alternatively, we may choose a reference base of 10 (decimal). While this may have some "human friendliness", in practice, the benefit is minimal. As shown in the table below, in base10, baseScale of interest is around -6, where a log10 bucket is sub-divided into 64 sub-buckets. We get a bound like 10, 100, or 1000 only every 64 buckets. The "human friendliness" value is minimal.

```
scale   #subBuckets base         relative error
-5       32         1.074607828  3.66%
-6       64         1.036632928  1.82%
-7      128         1.018151722  0.90%
```

Let's further consider the following use cases of histograms to compare base2 and base10:

1. Displaying histogram charts. With a typical base around 1.04 (around 2% relative error), there will be hundreds of buckets for a typical range over 100x. This many points can produce a reasonably smooth curve, regardless of the raw data being base2 or base10.
2. Calculating percentiles or quantiles. This is often used in SLO monitoring. Example SLO: "99% percentile of response time need to be no more than 100ms". To minimize relative error, percentile calculation usually returns log scale mid point of a bucket. So returned percentile values won't be on 10, 100, 1000, etc., even if the histogram is base10.
3. Answering question like "what percentage of values fall below 100". When the threshold is on 10, 100, 1000, etc, base10 histograms do give exact answer. But even in the decimal world, power of 10 numbers is a small population. For thresholds like 200, 500, etc. base10 histograms have no advantage over base2. If an exact answer is required in these cases, a user should create explicit buckets at these bounds, instead of using exponential buckets.

So the "human friendliness" of base10 exponential histograms is largely an illusion. To some extent, the base2 vs. base10 question has been answered long ago: computers convert input from base10 to base2, do processing in base2, then convert final output from base2 to base10. In the histogram case, we take input in "double", which is already in [binary float point format](https://en.wikipedia.org/wiki/Double-precision_floating-point_format). Bucketing these numbers in base10 bounds effectively switches base during processing. It just adds complexity and computational cost.

### Protocol support for universally mergeable histograms

Now the question is if and when we add support for universally mergeable histograms. There are some options:

1. No special support in protocol. Receiver derives baseScale and referenceBase if the base is close enough to a base on a referenceBase series. Implementations will decide how close is "close enough".
2. Allow the protocol to explicitly state baseScale, with referenceBase hardwired at 2.
3. Allow the protocol to explicitly state baseScale and an arbitrary referenceBase.

This proposal is currently written with option 1, with a path to extend to option 2 later:

```
// Current. Option 1
double base = 1;

// Future. Option 2. Changing a single value into a member of a new oneof is safe and binary compatible
oneof base_spec {
   double base = 1;
   sint32 base_scale = 99;  // base = 2 ^ (2^base_scale). base_scale may be negative.
}
```

**Or should we just do option 2 right now?**

## Future possibilities

What are some future changes that this proposal would enable?

* Support universally mergeable histograms
* Additional histogram types may be added
