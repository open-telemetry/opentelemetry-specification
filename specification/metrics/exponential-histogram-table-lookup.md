<!--- Hugo front matter used to generate the website version of this page:
linkTitle: Exponential-Histogram Table Lookup
aliases: [/docs/reference/specification/metrics/exponentialhistogramtablelookup]
weight: 2
--->

# Exponential-Histogram Table Lookup

**Status**: [Development](../document-status.md)

This document provides non-normative implementation guidance for
[ExponentialHistogram](./data-model.md#exponentialhistogram) and its
[SDK aggregation](./sdk.md#base2-exponential-bucket-histogram-aggregation).
It adds no requirements to those specifications and does not require
implementations to use table lookup.

## Overview

The lookup table algorithm maps positive normal IEEE 754
double-precision floating-point values exactly to bucket indexes at
supported scales, without evaluating a logarithm during lookup.
For bucket selection, positive subnormal inputs are clamped to the
smallest positive normal value, `0x1p-1022`, as permitted by the
[SDK specification](./sdk.md#handle-all-normal-values).
Related table lookup methods are listed in the [references](#references).

The *fraction field* is the 52 explicitly stored significand bits of a
binary64 value. In this document, `s` is the unsigned integer encoded by
those bits, with `0 <= s < 2^52`. For positive normal values, the
significand is `1 + s / 2^52`; its leading `1` is implicit.

The algorithm uses precomputed integer thresholds for exponential
bucket boundaries within one power-of-two interval. A second table
maps equally spaced fraction-field regions to positions in the
boundary table. One comparison then determines the bucket.

## Data Structures

Two tables are generated for a chosen maximum table scale `S`, where
`1 <= S <= 51` and `N = 2^S`. The upper bound keeps `SHIFT = 51 - S`
non-negative; practical limits are discussed under
[scale selection](#table-size-and-scale-selection).

For a normalized significand in `[1, 2)`, the mathematical boundaries
are `2^(k/N)`. The same tables apply at every exponent `e`, which
contributes `e * N` to the bucket index. In the formulas and pseudocode
below, `^` denotes exponentiation, not bitwise exclusive OR.

### Boundaries

The `BOUNDARIES` array has `N + 2` entries: `N` integer thresholds,
one leading sentinel, and one trailing sentinel.
Each threshold is the smallest fraction-field value belonging to the
next bucket under upper-inclusive bucket semantics.

```
BOUNDARIES[0] = 0
BOUNDARIES[1] = 1
for k where 1 <= k < N:
    BOUNDARIES[k+1] = ceiling(2^(52 + k/N)) - 2^52
BOUNDARIES[N+1] = 2^52
```

Here `ceiling` denotes integer ceiling applied to the exact real value.
For `1 <= k < N`, `2^(k/N)` is irrational and therefore not
representable as a binary64 value. Rounding it upward gives the first
representable value strictly above the mathematical boundary. Subtracting
`2^52` removes the implicit leading bit.

The boundary at `k = 0` is exactly representable. `BOUNDARIES[1] = 1`
leaves fraction-field value zero in the preceding bucket, so exact
powers of two receive the upper-inclusive adjustment. The trailing
sentinel exceeds every possible 52-bit fraction-field value and covers
the highest possible correction access, `BOUNDARIES[N+1]`.

The thresholds can be computed using integer arithmetic. For
`1 <= k < N`, the full significand, including the implicit leading bit,
is

```
B[k] = ceiling(2^(52 + k/N))
     = ceiling((2^(52*N + k))^(1/N)).
```

Because `N = 2^S`, apply a ceiling integer square root `S` times to
the exact integer `2^(52*N + k)`. The result is the least integer
greater than or equal to `2^(52 + k/N)`. Removing its leading bit
produces the fraction-field threshold. `integer_sqrt` below returns
the integer part of the square root:

```
for k where 1 <= k < N:
    x = 2^(52*N + k)

    repeat S times:
        root = integer_sqrt(x)
        x = root if root * root == x else root + 1

    BOUNDARIES[k+1] = x - 2^52
```

For the supported table scales, `2^52 < x < 2^53`, so subtraction is
equivalent to masking off the leading bit in the example generators.
Repeated ceiling square roots give the exact integer ceiling: for a
non-negative integer `m`, `m^2 >= ceiling(y)` holds exactly when
`m^2 >= y`. Thus rounding upward after each square root does not
change the final integer result.

Complete table generators using [Go] and [Python] support table scales
1 through 16 and produce the same output for a given scale. For example:

```sh
go run ./examples/exponential-histogram-table-lookup/main.go --scale 8
python ./examples/exponential-histogram-table-lookup/main.py --scale 8
```

The Go generator's regression tests can be run from the repository root:

```sh
go test ./examples/exponential-histogram-table-lookup/main.go ./examples/exponential-histogram-table-lookup/main_test.go
```

[Go]: ../../examples/exponential-histogram-table-lookup/main.go
[Python]: ../../examples/exponential-histogram-table-lookup/main.py

### Index Table

The `INDEX_TABLE` has `2N` entries. Let `SHIFT = 51 - S` and
`W = 2^SHIFT`. Entry `i` represents the fraction-field interval
`[i * W, (i + 1) * W)` and contains the largest `j` such that
`BOUNDARIES[j] <= i * W`. Equivalently,
`BOUNDARIES[j] <= i * W < BOUNDARIES[j+1]`.

```
SHIFT = 51 - S
j = 0
for i where 0 <= i < 2*N:
    x = i << SHIFT
    while x >= BOUNDARIES[j + 1]:
        j = j + 1
    INDEX_TABLE[i] = j
```

An entry is a boundary-table position, not the final signed bucket
index. It is exact at the start of the region. For other fraction-field
values in the region, it is either the correct position or one less;
the [proof below](#correctness-proof) shows why one comparison suffices.

## Algorithm

The input is a positive, finite IEEE 754 double-precision value outside
the [zero bucket](./data-model.md#zero-count-and-zero-threshold).
Other inputs are handled separately.

This variant clamps positive subnormal inputs to `0x1p-1022` before
decomposition. Here `e` is the unbiased exponent of the clamped value,
so `value = (1 + s / 2^52) * 2^e`.
`Float64bits` returns the unsigned 64-bit IEEE 754 representation.
`signed_integer` converts a value to a signed integer.
Exponent and bucket-index calculations use signed
integers wide enough for all intermediate results, and the final
right shift is arithmetic (rounding toward negative infinity).

The lookup supports `1 <= scale <= S`. For other scales, the caller
selects another mapping or handles the error as described under
[scale selection](#table-size-and-scale-selection).

```
func MapToIndex(value, scale):
    if scale < 1 or scale > S:
        return error("scale outside table range")

    value = max(value, 0x1p-1022)
    bits = Float64bits(value)
    s = bits & (2^52 - 1)
    e = signed_integer(bits >> 52) - 1023

    // Step 1: Approximate lookup at built-in table scale S
    linear_idx = s >> SHIFT
    approx = INDEX_TABLE[linear_idx]

    // Step 2: Boundary correction
    bucket = approx
    if s >= BOUNDARIES[approx + 1]:
        bucket = bucket + 1

    // Step 3: Combine with exponent, adjust to scale
    fine_index = e * 2^S + signed_integer(bucket) - 1
    return fine_index >> (S - scale)
```

For bucket selection, this implementation treats positive subnormal
inputs as the smallest positive normal value, `0x1p-1022`, and maps them
to the bucket containing that value. For positive scales, `0x1p-1022`
is that bucket's inclusive upper boundary, and its index is
`(-1022 * 2^scale) - 1`.

Step 1 identifies the fraction-field region and looks up the
boundary-table position at its start.

Step 2 advances that position if the input reaches the next threshold
within the region.

Step 3 converts the boundary-table position to a bucket index using
`bucket - 1` and adds the exponent contribution. In particular, `s = 0`
gives `bucket = 0` and index `e * N - 1`. The final right shift
downscales from `S` to the requested scale.

## Correctness Proof

Adjacent mathematical boundaries in `[1, 2]` are separated by at least
`2^(1/N) - 1`. Since

```
2^(1/N) - 1 = exp(ln(2) / N) - 1 > ln(2) / N > 1 / (2N),
```

their separation in fraction-field units is greater than the integer
region width `W = 2^52 / (2N)`. Rounding both boundaries upward to
integers leaves a separation of at least `W`. Consequently, a
half-open region `[i * W, (i + 1) * W)` contains at most one of these
thresholds.

The adjusted threshold at `s = 1` lies in the first region when
`W > 1`; the next threshold is greater than `W` and lies outside that
region. When `W = 1`, each region contains only one integer value.
Thus the power-of-two adjustment also permits at most one threshold
per region.

The index-table lookup starts at the exact position for the region's
first value. At most one increment is needed to reach the position
for any other value in that region. The thresholds put each
representable value on the correct side of its mathematical boundary,
including exact powers of two. Adding `e * N` therefore gives the
exact bucket index at scale `S` after subtracting the table-position
offset of one.

Finally, [perfect subsetting](./data-model.md#exponential-scale) makes
floor division by `2^(S - scale)` the exact downscaling operation. The
arithmetic right shift implements that division, including for negative
indexes. For subnormal inputs, this reasoning applies to the clamped
value rather than the original input.

## Table Size and Scale Selection

Table dimensions depend on the compiled-in table scale `S`. These
sizes include the sentinels and assume 64-bit boundary entries,
excluding alignment and container overhead:

| Table scale `S` | `BOUNDARIES` entries | `INDEX_TABLE` entries | Index entry width | Total size |
|-----------------|---------------------|-----------------------|-------------------|------------|
| 4               | 18                  | 32                    | 16 bits           | 208 B      |
| 6               | 66                  | 128                   | 16 bits           | 784 B      |
| 8               | 258                 | 512                   | 16 bits           | 3088 B     |
| 10              | 1026                | 2048                  | 16 bits           | 12304 B    |
| 16              | 65538               | 131072                | 32 bits           | 1048592 B  |

`INDEX_TABLE` entries range from `0` through `N`, inclusive, because
of the leading sentinel. Unsigned 16-bit entries suffice only through
`S = 15`; scale 16 requires at least 17 bits. The Go generator uses
32-bit entries for all supported scales; consumers can use narrower
entries when the values fit.

For example, `S = 8` provides 256 buckets per power-of-two interval
with about 3 KiB of table storage using 16-bit index entries. At scale
8, the histogram's [relative error](./sdk.md#base2-exponential-bucket-histogram-aggregation)
is about 0.14%; this is distinct from bucket-mapping error.

The table supports positive scales through `S`. This implementation
choice is separate from the SDK aggregation's
[`MaxScale`](./sdk.md#base2-exponential-bucket-histogram-aggregation),
whose default is 20. For supported scales above `S`, an implementation
can use the [logarithm method](./data-model.md#all-scales-use-the-logarithm-function);
the exactness claim for table lookup does not extend to that method.
For zero and negative scales, direct
[exponent mapping](./data-model.md#scale-zero-extract-the-exponent)
avoids the table.

An alternative is a lookup-only mapper that reports unsupported scales
during initialization. We recommend documenting the supported range and
handling incompatible configuration through the existing
[error-handling rules](../error-handling.md#basic-error-handling-principles),
rather than silently replacing the requested scale with `S` or failing
during measurement recording. Selecting a table size does not change
the SDK's `MaxScale` requirements.

We recommend selecting scale limits that account for table-entry and
bucket-index widths, shift counts, and the numeric limits of every
intermediate calculation, including table generation and validation.
Arbitrary precision does not imply an unbounded exponent range. For
example, a Go [`math/big.Float`](https://pkg.go.dev/math/big#Float)
reference calculation that forms
`2^index` before taking square roots overflows at the largest bucket
index for scale 21. Limiting that calculation to scale 20 avoids this
particular overflow.

The integer table generator above has different constraints: its
largest initial integer occupies `53 * 2^S` bits. At `S = 20`, that is
6.625 MiB for one integer alone, before temporary storage and the cost
of computing the remaining boundaries. The example generators limit
`S` to 16; this is not a universal bignum or histogram scale limit.
We recommend validating generation limits before allocating tables
and reporting unsupported scales explicitly.

## References

- **Dynatrace** — [DynaHist
  library](https://github.com/dynatrace-oss/dynahist)
  ([ExponentialHistogramLargeInclusiveLayout](https://github.com/dynatrace-oss/dynahist/blob/main/src/main/java/com/dynatrace/dynahist/layout/ExponentialHistogramLargeInclusiveLayout.java))
  uses `N` linear buckets with 2 boundary corrections.

- **NewRelic** — [NrSketch
  library](https://github.com/newrelic-experimental/newrelic-sketch-java)
  ([SubBucketLookupIndexer](https://github.com/newrelic-experimental/newrelic-sketch-java/blob/main/src/main/java/com/newrelic/nrsketch/indexer/SubBucketLookupIndexer.java),
  [algorithm
  description](https://github.com/newrelic-experimental/newrelic-sketch-java/blob/main/Indexer.md))
  uses `2N` linear buckets with 1 boundary correction.
