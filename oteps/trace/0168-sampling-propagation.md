# Propagate parent sampling probability

Use the W3C trace context to convey consistent parent sampling probability.

## Motivation

The parent sampling probability is the probability associated with
the start of a trace context that was used to determine whether the
W3C `sampled` flag is set, which determines whether child contexts
will be sampled by a `ParentBased` Sampler.  It is useful to know the
parent sampling probability associated with a context in order to
build span-to-metrics pipelines when the built-in `ParentBased`
Sampler is used.  Further motivation for supporting span-to-metrics
pipelines is presented in [OTEP
170](0170-sampling-probability.md).

A consistent trace sampling decision is one that can be carried out at
any node in a trace, which supports collecting partial traces.
OpenTelemetry specifies a built-in `TraceIDRatioBased` Sampler that
aims to accomplish this goal but was left incomplete (see a
[TODO](../../specification/trace/sdk.md#traceidratiobased)
in the v1.0 Trace specification).

We propose a Sampler option to propagate the necessary information
alongside the [W3C sampled flag](https://www.w3.org/TR/trace-context/#sampled-flag)
using `tracestate` with an `ot` vendor tag, which will require
(separately) [specifying how the OpenTelemetry project uses
`tracestate`
itself](https://github.com/open-telemetry/opentelemetry-specification/pull/1852).

## Explanation

Two pieces of information are needed to convey consistent parent sampling probability:

1. p-value representing the parent sampling probability.
2. r-value representing the "randomness" as the source of consistent sampling decisions.

This proposal uses 6 bits of information to propagate each of these
and does not depend on built-in TraceID randomness, which is not
sufficiently specified for probability sampling at this time.  This
proposal closely follows [research by Otmar
Ertl](https://arxiv.org/pdf/2107.07703.pdf).

### Adjusted count

The concept of adjusted count is introduced in [OTEP
170](./0170-sampling-probability.md).  Briefly, adjusted count is defined
in terms of the sampling probability, where:

| Sampling probability | Adjusted count                     | Notes                                                                                                      |
| --                   | --                                 | --                                                                                                         |
| `probability` != 0   | `adjusted_count` = `1/probability` | For spans selected with non-zero probability, adjusted count is the inverse of their sampling probability. |
| `probability` == 0   | `adjusted_count` = 0               | For spans that were not selected by a probability sampler, adjusted count is zero.                         |

The term is used to convey the representivity of an item that was (or
was not) selected by a probability sampler.  Items that are not
selected by a probability sampler are logically assigned zero adjusted
count, such that if they are recorded for any other reason they do not
introduce bias in the estimated count of the total span population.

### p-value

To limit the cost of this extension and for statistical reasons
documented below, we propose to limit parent sampling probability
to powers of two.  This limits the available parent sampling
probabilities to 1/2, 1/4, 1/8, and so on.  We can compactly encode
these probabilities as small integer values using the base-2 logarithm
of the adjusted count.

Using six bits of information we can convey known sampling rates as
small as 2**-62.  The value 63 is reserved to mean sampling with
probability 0, which conveys an adjusted count of 0 for the associated
context.

When propagated, the "p-value" as it is known will be interpreted as
shown in the following table.  The p-value for known sampling
probabilities is the negative base-2 logarithm of the probability:

| p-value | Parent Probability |
| -----   | -----------      |
| 0       | 1                |
| 1       | 1/2              |
| 2       | 1/4              |
| ...     | ...              |
| N       | 2**-N            |
| ...     | ...              |
| 61      | 2**-61           |
| 62      | 2**-62           |
| 63      | 0                |

[As specified in OTEP 170 for the Trace data
model](0170-sampling-probability.md),
parent sampling probability can be stored in exported Span data to
enable span-to-metrics pipelines to be built.  Because `tracestate` is
already encoded in the OpenTelemetry Span, this proposal is requires
no changes to the Span protocol.  Accepting this proposal means the
p-value can be derived from `tracestate` when the parent sampling
probability is known.

An unknown value for `p` cannot be propagated using `tracestate`
explicitly, simply omitting `p` conveys an unknown parent sampling
probability.

### r-value

With parent sampling probabilities limited to powers of two, the
amount of randomness needed per trace context is limited.  A
consistent sampling decision is accomplished by propagating a specific
random variable known as the r-value.

To develop an intuition for r-values, consider a scenario where every
bit of the `TraceID` is generated by a uniform random bit generator
(i.e., every bit is 0 or 1 with equal probability).  An 128-bit
`TraceID` can therefore be treated as a 128-bit unsigned integer,
which can be mapped into a fraction with range [0, 1) by dividing by
2**128, a form known as the TraceID-ratio.  Now, probability sampling
could be achieved by comparing the TraceID-ratio with the sampling
probability, setting the `sampled` flag when TraceID-ratio is less
than the sampling probability.

It is easy to see that with sampling probability 1, all TraceIDs will
be accepted because TraceID ratios are exclusively less than 1.
Sampling with probability 50% will select TraceID ratios less than
0.5, which maps to all TraceIDs less than 2**127 or, equivalently, all
TraceIDs where the most significant bit is zero.  By the same logic,
sampling with probability 25% means accepting TraceIDs where the most
significant two bits are zero.  In general, with exact probability
`2**-S` is equivalent to selecting TraceIDs with `S` leading zeros in
this example scenario.

The r-value specified here directly describes the number of leading
zeros in a random 62-bit string, specified in a way that does not
require TraceID values to be constructed with random bits in specific
positions or with hard requirements on their uniformity.  In
mathematical terms, the r-value is described by a truncated geometric
distribution, listed below:

| `r` value        | Probability of `r` value | Implied sampling probabilities |
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

Such a random variable `r` can be generated using efficient
instructions on modern computer architectures, for example we may
compute the number of leading zeros using hardware support:

```golang
import (
    "math/rand"
    "math/bits"
)

func nextRValueLeading() int {
    x := uint64(rand.Int63()) // 63 least-significant bits are random
    y := x << 1 | 0x3         // 62 most-significant bits are random
    return bits.LeadingZeros64(y)
}
```

Or we may compute the number of trailing zeros instead, for example
(not using special instructions):

```golang
import (
    "math/rand"
)

func nextRValueTrailing() int {
    x := uint64(rand.Int63())
    for r := 0; r < 62; r++ {
        if x & 0x1 == 0x1 {
            return r
        }
        x = x >> 1
    }
    return 62
}
```

More examples for calculating r-values are shown in
[here](https://gist.github.com/jmacd/79c38c1056035c52f6fff7b7fc071274).
For example, the value 3 means there were three leading zeros and
corresponds with being sampled at probabilities 1-in-1 through 1-in-8
but not at probabilities 1-in-16 and smaller.

### Proposed `tracestate` syntax

The consistent sampling r-value (`r`) and the parent sampling
probability p-value (`p`) will be propagated using two bytes of base16
content for each of the two fields, as follows:

```
tracestate: ot=p:PP;r:RR
```

where `PP` are two bytes of base16 p-value and `RR` are two bytes of
base16 r-value.  These values are omitted when they are unknown.

This proposal should be taken as a recommendation and will be modified
to [match whatever format OpenTelemtry specifies for its
`tracestate`](https://github.com/open-telemetry/opentelemetry-specification/pull/1852).
The choice of base16 encoding is therefore just a recommendation,
chosen because `traceparent` uses base16 encoding.

### Examples

The following `tracestate` value is accompanied by `sampled=true`:

```
tracestate: ot=r:0a;p:03
```

and translates to

```
base16(p-value) = 03 // 1-in-8 parent sampling probability
base16(r-value) = 0a // qualifies for 1-in-1024 or greater probability consistent sampling
```

A `ParentBased` Sampler will include `ot=r:0a;p:03` in the stored
`TraceState` field, allowing consumers to count it as with an adjusted
count of 8 spans.  The `sampled=true` flag remains set.

A `TraceIDRatioBased` Sampler configured with probability 2**-10 or
greater will enable `sampled=true` and convey a new parent sampling
probability via `tracestate: ot=r:0a;p:0a`.

A `TraceIDRatioBased` Sampler configured with probability 2**-11 or
smaller will set `sampled=false` and remove `p` from the tracestate,
setting `tracestate: ot=r:0a`.

## Internal details

The reasoning behind restricting the set of sampling rates is that it:

- Lowers the cost of propagating parent sampling probability
- Limits the number of random bits required
- Avoids floating-point to integer rounding errors
- Makes math involving partial traces tractable.

[An algorithm for making statistical inference from partially-sampled
traces has been published](https://arxiv.org/pdf/2107.07703.pdf) that
explains how to work with a limited number of power-of-2 sampling rates.

### Behavior of the `TraceIDRatioBased` Sampler

The Sampler MUST be configured with a power-of-two probability
expressed as `2**-s` with s being an integer in the range [0, 62]
except for the special case of zero probability (in which case `p=63`
is used).

If the context is a new root, the initial `tracestate` must be created
with randomness value `r`, as described above, in the range [0, 62].
If the context is not a new root, output a new `tracestate` with the
same `r` value as the parent context.

In both cases, set the sampled bit if the outgoing `p` is less than or
equal to the outgoing `r` (i.e., `p <= r`).

When sampled, in both cases, the context's p-value `p` is set to the
value of `s` in the range [0, 62].  If the sampling probability is
zero (the special case where `s` is undefined), use `p=63` the
specified value for zero probability.

If the context is not a new root and the incoming context's r-value
is not set, the implementation SHOULD notify the user of an error
condition and follow the incoming context's `sampled` flag.

### Behavior of the `ParentBased` sampler

The `ParentBased` sampler is unmodified by this proposal.  It honors
the W3C `sampled` flag and copies the incoming `tracestate` keys to
the child context.  If the incoming context has known parent sampling
probability, so does the Span.

The span's parent sampling probability is known when both `p` and `r`
are defined in the `ot` sub-key of `tracestate`.  When `r` or `p` are
not defined, the span's parent sampling probability is unknown.

### Behavior of the `AlwaysOn` Sampler

The `AlwaysOn` Sampler behaves the same as `TraceIDRatioBased` with
100% sampling probability (i.e., `p=1`).

### Behavior of the `AlwaysOff` Sampler

The `AlwaysOff` Sampler behaves the same as `TraceIDRatioBased` with
zero probability (i.e., `p=63`).

## Worked 3-bit example

The behavior of these tables can be verified by hand using a smaller
example.  The following table shows how these equations work where
`r`, `p`, and `s` are limited to 3 bits instead of 6 bits.

Values of `p` are interpreted as follows:

| `p` value | Adjusted count |
| -----     | -----          |
| 0         | 1              |
| 1         | 2              |
| 2         | 4              |
| 3         | 8              |
| 4         | 16             |
| 5         | 32             |
| 6         | 64             |
| 7         | 0              |

Note there are only seven known non-zero values for the adjusted count
(`p`) ranging from 1 to 64. Thus there are seven defined values of `r`
and `s`.  The following table shows `r` and the corresponding
selection probability, along with the calculated adjusted count for
each `s`:

| `r` value | probability of `r` | `s=0` | `s=1` | `s=2` | `s=3` | `s=4` | `s=5` | `s=6` |
| --        | --                 | --    | --    | --    | --    | --    | --    | --    |
| 0         | 1/2                | 1     | 0     | 0     | 0     | 0     | 0     | 0     |
| 1         | 1/4                | 1     | 2     | 0     | 0     | 0     | 0     | 0     |
| 2         | 1/8                | 1     | 2     | 4     | 0     | 0     | 0     | 0     |
| 3         | 1/16               | 1     | 2     | 4     | 8     | 0     | 0     | 0     |
| 4         | 1/32               | 1     | 2     | 4     | 8     | 16    | 0     | 0     |
| 5         | 1/64               | 1     | 2     | 4     | 8     | 16    | 32    | 0     |
| 6         | 1/64               | 1     | 2     | 4     | 8     | 16    | 32    | 64    |

Notice that the sum of `r` probability times adjusted count in each of
the `s=*` columns equals 1.  For example, in the `s=4` column we have
`0*1/2 + 0*1/4 + 0*1/8 + 0*1/16 + 16*1/32 + 16*1/64 + 16*1/64 = 1/2 +
1/4 + 1/4 = 1`.  In the `s=2` column we have `0*1/2 + 0*1/4 + 4*1/8 +
4*1/16 + 4*1/32 + 4*1/64 + 4*1/64 = 1/2 + 1/4 + 1/8 + 1/16 + 1/16 = 1`.
We conclude that when `r` is chosen with the given probabilities,
any choice of `s` produces one expected span.

## Invariant checking

The following table summarizes how the three Sampler cases behave with
respect to the incoming and outgoing values for `p`, `r`, and
`sampled`:

| Sampler                | Incoming `r` | Incoming `p` | Incoming `sampled` | Outgoing `r`               | Outgoing `p`               | Outgoing `sampled`         |
| --                     | --           | --           | --                 | --                         | --                         | --                         |
| Parent                 | unused       | expected     | respected          | checked and passed through | checked and passed through | checked and passed through |
| TraceIDRatio(Non-Root) | used         | unused       | ignored            | checked and passed through | set to `s`                 | set to `p <= r`          |
| TraceIDRatio(Root)     | n/a          | n/a          | n/a                | random variable            | set to `s`                 | set to `p <= r`          |

There are several cases where the resulting span's parent sampling
probability is unknown:

| Sampler                | Unknown condition |
| --                     | --                |
| Parent                 | no incoming `p`   |
| TraceIDRatio(Non-Root) | no incoming `r`   |
| TraceIDRatio(Root)     | none              |

The inputs are recognized as out-of-range as follows:

| Range invariate | Remedy                           |
| --              | --                               |
| `p < 0`         | drop `p` from tracestate         |
| `p > 63`        | drop `p` from tracestate         |
| `r < 0`         | drop `r` and `p` from tracestate |
| `r > 62`        | drop `r` and `p` from tracestate |

There are cases where the combination of `p` and `r` and `sampled` are
inconsistent with each other.  The `sampled` flag is equivalent to the
expression `p <= r`.  When the invariant `sampled <=> p <= r` is
violated, the `ParentBased` sampler MUST correct the propagated values
as discussed below.

The violation is always addressed by honoring the `sampled` flag and
correcting `p` to either 63 (for zero adjusted count) or unset (for
unknown parent sampling probability).

If `sampled` is false and the invariant is violated, drop `p` from the
outgoing context to convey unknown parent sampling probability.

The case where `sampled` is true with `p=63` indicating 0% probability
may by regarded as a special case to allow zero adjusted count
sampling, which permits non-probabilistic sampling to take place in
the presence of probability sampling.  Set `p` to 63.

If `sampled` is true with `p<63` (but `p>r`), drop `p` from the
outgoing context to convey unknown parent sampling probability.

## Prototype

[This proposal has been prototyped in the OTel-Go
SDK.](https://github.com/open-telemetry/opentelemetry-go/pull/2177) No
changes in the OTel-Go Tracing SDK's `Sampler` or `tracestate` APIs
were needed.

## Trade-offs and mitigations

### Naming question

This proposal changes the logic of the `TraceIDRatioBased` sampler,
currently part of the OpenTelemetry specification, in a way that makes
the name no longer meaningful.  The proposed sampler may be named
`ConsistentSampler` and the existing `TraceIDRatioBased` sampler can
be deprecated.

Many SDKs already implement the `TraceIDRatioBased` sampler and it has
been used for probability sampling at trace roots with arbitrary
(i.e., not power-of-two) probabilities.  Because of this, we may keep
the current (under-specified) `TraceIDRatioBased` sampler and rename
it `ProbabilitySampler` to convey that it does behave in a specified
way with respect to the bits of the TraceID.

### Not using TraceID randomness

It would be possible, if TraceID were specified to have at least 62
uniform random bits, to compute the randomness value described above
as the number of leading zeros among those 62 random bits.

However, this would require modifying the W3C traceparent specification,
therefore we do not propose to use bits of the TraceID.

See [W3C
trace context issue 467](https://github.com/w3c/trace-context/issues/467).

### Not using TraceID hashing

It would be possible to make a consistent sampling decision by hashing
the TraceID, but we feel such an approach is not sufficient for making
unbiased sampling decisions.  It is seen as a relatively difficult
task to define and specify a good enough hashing function, much less
to have it implemented in multiple languages.

Hashing is also computationally expensive. This proposal uses extra
data to avoid the computational cost of hashing TraceIDs.

### Restriction to power-of-two

Restricting parent sampling probabilities to powers of two does not limit tail
Samplers from using arbitrary probabilities.  The companion [OTEP
170](0170-sampling-probability.md) has discussed
the use of a `sampler.adjusted_count` attribute that would not be
limited to power-of-two values.  Discussion about how to represent the
effective adjusted count for tail-sampled Spans belongs in [OTEP
170](0170-sampling-probability.md), not this OTEP.

Restricting parent sampling probabilities to powers of two does not limit
Samplers from using arbitrary effective probabilities over a period of
time.  For example, a typical trace sampling rate of 5% (i.e., 1 in
20) can be accomplished by choosing 1/16 sampling 60% of the time and
1/32 sampling 40% of the time:

```
1/16 * 0.6 + 1/32 * 0.4 = 0.05
```

### Propagating `p` when unsampled

Consistent trace sampling requires the `r` value to be propagated even
when the span itself is not sampled.  It is not necessary, however, to
propagate the `p` value when the context is not sampled, since
`ParentBased` samplers will not change the decision.  Although one
use-case was docmented in Google's early Dapper system (known as
"inflationary sampling", see
[OTEP 170](0170-sampling-probability.md#dappers-inflationary-sampler)), the same effect can
be achieved using a consistent sampling decision in this framework.

### Default behavior

In order for consistent trace sampling decisions to be made, the `r`
value MUST be set at the root of the trace.  This behavior could be
opt-in or opt-out.  If opt-in, users would have to enable the setting
of `r` and the setting and propagating of `p` in the tracestate.  If
opt-out, users would have to disable these features to turn them off.
The cost and convenience of Sampling features depend on this choice.

This author's recommendation is that these behaviors be opt-in at
first in order to demonstrate their usefulness.  If it proves
successful, an on-by-default approach could be proposed using a
modified W3C trace context `traceparent`, as this would allow p-values
to be propagated cheaply.

See [W3C issue trace context issue
463](https://github.com/w3c/trace-context/issues/463) which is about
propagating sampling probability in the `traceparent` header, which
makes it cheap enough to have on-by-default.
