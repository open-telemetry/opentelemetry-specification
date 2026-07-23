<!--- Hugo front matter used to generate the website version of this page:
linkTitle: Exponential-Histogram Table Lookup
aliases: [/docs/reference/specification/metrics/exponentialhistogramtablelookup]
weight: 2
--->

# Exponential-Histogram Table Lookup

**Status**: [Mixed](../document-status.md)

## Overview

**Status**: [Stable](../document-status.md)

The lookup table algorithm maps IEEE 754 double-precision
floating-point values exactly to bucket indexes without use of the
logarithm function. The algorithm detailed here is documented from two
reference implementations listed in the references section.

The main data structure is a table of exact logarithm significand
values. For a lookup with exponential scale `S`, a lookup table of
`2^S` 52-bit precision logarithm significand values will be
calculated, usually at compile time as this requires special math
support.

A second table of size `2^(S+1)` is calculated. Because the logarithm
function is concave, a linear-approximate lookup in the second table
narrows the search to a single boundary, leaving one comparison.

## Data Structures

Two tables are generated for a chosen maximum table scale `S`, where
`N = 2^S`. Our goal is to exactly subdivide the range `[1, 2)` into N
exact significand boundaries; the same table lookup is applied
regardless of the exponent, which serves to shift the result by
multiples of N.

### Boundaries

The `BOUNDARIES` array consists of `2^S` exact logarithm significand
values and two sentinel values.

```
// Base-2 logarithm significand boundary values
BOUNDARIES = {
  0,                             // Exact power-of-two
  1,                             // Smallest value of the first bucket
  significand_bits(2^(1/N)),     // Smallest value of the second bucket
  significand_bits(2^(2/N)),
  ...                            // 
  significand_bits(2^((N-2)/N)),
  significand_bits(2^((N-1)/N)), // Smallest value of the last bucket
  2^52,                          // Sentinel value
}
```

Each of the non-sentinel values are the 52-bit significand of the
smallest IEEE 754 double whose value is greater than or equal to
`2^(k/N)`. Note:

- `BOUNDARIES[0] = 0`: This captures exact powers of two
- `BOUNDARIES[1] = 1`: This excludes exact powers of two
- The trailing sentinel value simplifies bounds checking.

To compute this table requires a "bignum" library. To express the
necessary `2^(k/N)` calculation for significand bits, compute the
exact power `2^k` and then repeatedly square-root N times.

```
for k in 0..N:
  x = 2^k

  for _ in 0..S:
    x = sqrt(x)

  BOUNDARIES[k+1] = significand(ceiling(x))
```

Note that boundary positions are shifted by one, to account for the
additional sentinel. This will be corrected during lookup.

### Index Table

The `INDEX_TABLE` is a linear-to-exponential bucket mapping with `2N`
entries. An accessory value `SHIFT` determines how many bits are
removed from the 52-bit significand considering `N`, which is `52 -
log2(2*N)`, or simply `51 - S`. The following iterative procedure
fills in the index table.

```
SHIFT = 51 - S
j = 0
for i in 0..2*N:
    x = i << SHIFT
    while x >= BOUNDARIES[j + 1] {
        j += 1;
    }
    INDEX_TABLE[i] = j
```

Each entry maps a linear significand region to the largest bucket
exponential index with boundary less than the true start of the
bucket, including the `+1` offset. Since at most one boundary can fall
within any linear region, this gives the correct index or one less
than the correct index.

## Algorithm

The input is a positive IEEE 754 double-precision value, with the
zero, NaN and Inf cases handled separately. The significand `s` is a
52 bit unsigned integer, and the exponent `e` is the corresponding
unbiased exponent.

```
func MapToIndex(s, e, scale):
    // Step 1: Approximate lookup at built-in table scale S
    linear_idx = s >> SHIFT
    approx = INDEX_TABLE[linear_idx]

    // Step 2: Boundary correction
    bucket = approx
    if s >= BOUNDARIES[approx + 1]:
        bucket = bucket + 1

    // Step 3: Combine with exponent, adjust to scale
    fine_index = (e << S) + bucket - 1
    return fine_index >> (S - scale)
```

Step 1 partitions the 52-bit significand space into `2N` equal regions
and looks up the pre-computed exponential bucket.

Step 2 corrects for the case where an exponential bucket boundary
falls within the linear region.

Step 3 assembles the full index by combining the within-octave bucket
with the exponent. The `-1` corrects the positive offset introduced
above, handling the special case for exact powers of two. The final
right-shift downscales from the table's built-in resolution to the
requested scale.

## Correctness Proof

The logarithm function is concave, steepest at small significand
values.  By dividing the significand range `[1, 2)` into `2N` equal
parts, each region can hold at most one exponential bucket boundary.

TODO:

## Table Size and Scale Selection

The table dimensions are determined by the maximum table scale `S`:

| Table scale S | N = 2^S BOUNDARIES entries (u64) | INDEX_TABLE entries (u16) | Total size |
|---------------|----------------------------------|---------------------------|------------|
| 4             | 16                               | 32                        | ~200B      |
| 6             | 64                               | 128                       | ~800B      |
| 8 (default)   | 256                              | 512                       | ~3 KiB     |
| 10            | 1024                             | 2048                      | ~12 KiB    |

The table supports all scales from 1 to S inclusive.

A table scale of 8, the recommended default, provides 256 sub-buckets
per power-of-two octave with ~0.14% relative error. This covers the
practical range of scales used in observability scenarios.

Implementations control maximum table scale.

## References

- **Dynatrace** — Otmar Ertl's [DynaHist
  library](https://github.com/dynatrace-oss/dynahist)
  ([ExponentialHistogramLargeInclusiveLayout](https://github.com/dynatrace-oss/dynahist/blob/main/src/main/java/com/dynatrace/dynahist/layout/ExponentialHistogramLargeInclusiveLayout.java))
  uses `N` linear buckets with 2 boundary corrections.

- **NewRelic** — Yuke Zhuge's [NrSketch
  library](https://github.com/newrelic-experimental/newrelic-sketch-java)
  ([SubBucketLookupIndexer](https://github.com/newrelic-experimental/newrelic-sketch-java/blob/main/src/main/java/com/newrelic/nrsketch/indexer/SubBucketLookupIndexer.java),
  [algorithm
  description](https://github.com/newrelic-experimental/newrelic-sketch-java/blob/main/Indexer.md))
  uses `2N` linear buckets with 1 boundary correction.
