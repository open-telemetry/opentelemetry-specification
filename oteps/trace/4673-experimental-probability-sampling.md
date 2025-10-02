# TraceState: Probability Sampling

**Status**: [Deprecated](../../specification/document-status.md)

This document contains the final state of the old, experimental
"tracestate probability sampling" specification. This specification is
recorded as an OTEP so that we can remove it from the OpenTelemetry
specification and still refer to it.

Changes to the document made below, summarized:

- Links to [`sdk.md`][SDK_SPEC]: references were general in nature, as the SDK
  specification was never updated to refer to this document; these
  links were updated to a current permalink to avoid breaking in the
  future.
- Links to [`tracestate-handling.md`][TRACESTATE_HANDLING]:
  these links were updated to a version of the file that was current
  when this file was written, before
  [PR#4162](https://github.com/open-telemetry/opentelemetry-specification/pull/4162)
  added the new specification.
- Remove the table of contents.

[TRACESTATE_HANDLING]: https://github.com/open-telemetry/opentelemetry-specification/blob/ec3779c3d0044503a1ec
[SDK_SPEC]: https://github.com/open-telemetry/opentelemetry-specification/blob/03e4ea2748e18e63d1e00e58e373ca55768fb1b0/specification/trace/tracestate-handling.md

## Overview

Probability sampling allows OpenTelemetry tracing users to lower span
collection costs by the use of randomized sampling techniques.  The
objectives are:

- Compatible with the existing W3C trace context `sampled` flag
- Spans can be accurately counted using a Span-to-metrics pipeline
- Traces tend to be complete, even though spans may make independent sampling decisions.

This document specifies an approach based on an "r-value" and a
"p-value".  At a very high level, r-value is a source of randomness
and p-value encodes the sampling probability.  A context is sampled
when `p <= r`.

Significantly, by including the r-value and p-value in the
OpenTelemetry `tracestate`, these two values automatically propagate
through the context and are recorded on every Span.  This allows Trace
consumers to correctly count spans simply by interpreting the p-value
on a given span.

For efficiency, the supported sampling probabilities are limited to
powers of two.  P-value is derived from sampling probability, which
equals `2**-p`, thus p-value is encoded using an unsigned integer.

For example, a p-value of 3 indicates a sampling probability of 1/8.

Since the W3C trace context does not specify that any of the 128 bits
in a TraceID are true uniform-distributed random bits, the r-value is
introduced as an additional source of randomness.

The recommended method of generating an "r-value" is to count the
number of leading 0s in a string of 62 random bits, however, it is not
required to use this approach.

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

Thus, there are three meaningfully distinct categories of adjusted count:

| Adjusted count is | Interpretation                                                                                                                     |
| --                | --                                                                                                                                 |
| _Unknown_         | The adjusted count is not known, possibly as a result of a non-probability sampler.  Items in this category should not be counted. |
| _Zero_            | The adjusted count is known; the effective count of the item is zero.                                                              |
| _Non-zero_        | The adjusted count is known; the effective count of the item is greater than zero.                                                 |

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
complete subtrace is defined at a span when every descendant span is
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
effectively excluding it from the population.  This is defined as a
non-probability sampler, not a zero-percent probability sampler,
because the spans are effectively unrepresented.

## Consistent Probability sampling

The consistent sampling scheme adopted by OpenTelemetry propagates two
values via the context, termed "p-value" and "r-value".

Both fields are propagated via the OpenTelemetry `tracestate` under
the `ot` vendor tag using the rules for [tracestate
specification][TRACESTATE_HANDLING].  Both fields are represented as
unsigned decimal integers requiring at most 6 bits of information.

This sampling scheme selects items from among a fixed set of 63
distinct probability values. The set of supported probabilities
includes the integer powers of two between 1 and 2**-62.  Zero
probability and probabilities smaller than 2**-62 are treated as a
special case of "ConsistentAlwaysOff" sampler, just as unit
probability (i.e., 100%) describes a special case of
"ConsistentAlwaysOn" sampler.

R-value encodes which among the 63 possibilities will consistently
decide to sample for a given trace.  Specifically, r-value specifies
the smallest probability that will decide to sample a given trace in
terms of the corresponding p-value.  For example, a trace with r-value
0 will sample spans configured for 100% sampling, while r-value 1 will
sample spans configured for 50% or 100% sampling, and so on through
r-value 62, for which a consistent probability sampler will decide
"yes" at every supported probability (i.e., greater than or equal to
2**-62).

P-value encodes the adjusted count for child contexts (i.e., consumers
of `tracestate`) and consumers of sampled spans to record for use in
Span-to-metrics pipelines.  A special p-value of 63 is defined to mean
zero adjusted count, which helps define composition rules for
non-probability samplers.

An invariant will be stated that connects the `sampled` trace flag
found in `traceparent` context to the r-value and p-value found in
`tracestate` context.

### Conformance

Consumers of OpenTelemetry `tracestate` data are expected to validate
the probability sampling fields before interpreting the data.  This
applies to the two samplers specified here as well as consumers of
span data, who are expected to validate `tracestate` before
interpreting span adjusted counts.

Producers of OpenTelemetry `tracestate` containing p-value and r-value
fields are required to meet the behavioral requirements stated for the
`ConsistentProbabilityBased` sampler and to ensure statistically valid
outcomes.  A test suite is included in this specification so that
users and consumers of OpenTelemetry `tracestate` can be assured of
accuracy in Span-to-metrics pipelines.

### Completeness guarantee

This specification defines consistent sampling for power-of-two
sampling probabilities.  When a sampler is configured with a
non-power-of-two sampling probability, the sampler will
probabilistically choose between the nearest powers of two.

When a single consistent probability sampler is used at the root of a
trace and all other spans use a parent-based sampler, the resulting
traces are always complete (ignoring collection errors).  This
property holds even for non-power-of-two sampling probabilities.

When multiple consistent probability samplers are used in the same
trace, in general, trace completeness is ensured at the smallest power
of two greater than or equal to the minimum sampling probability
across the trace.

### Context invariants

The W3C `traceparent` (version 0) contains three fields of
information: the TraceId, the SpanId, and the trace flags.  The
`sampled` trace flag has been defined by W3C to signal an intent to
sample the context.

The [Sampler API][SDK_SPEC#sampler] is responsible for setting the
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
`((p <= r) == sampled) OR (sampled AND (p == 63)) == TRUE`.

The invariant between `sampled`, `p`, and `r` only applies when both
`p` and `r` are present.  When the invariant is violated, the
`sampled` flag takes precedence and `p` is unset from `tracestate` in
order to signal unknown adjusted count.

##### Requirement: Inconsistent p-values are unset

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

##### Requirement: Out-of-range p-values are unset

Consumers SHOULD unset `p` from the `tracestate` if the unsigned
decimal value is greater than 63 before using the `tracestate` to make
a sampling decision or interpret adjusted count.

#### R-value

R-value is set in the `tracestate` by the Sampler at the root of the
trace, in order to support consistent probability sampling.  When the
value is omitted or not present, child spans in the trace are not able
to participate in consistent probability sampling.

R-value determines which sampling probabilities will decide to sample
or not decide to sample for spans of a given trace, as follows:

| r-value          | Implied sampling probabilities |
| ---------------- | ----------------------         |
| 0                | 1                              |
| 1                | 1/2 and above                  |
| 2                | 1/4 and above                  |
| 3                | 1/8 and above                  |
| ...              | ...                            |
| 0 <= r <= 61     | 2**-r and above                |
| ...              | ...                            |
| 59               | 2**-59 and above               |
| 60               | 2**-60 and above               |
| 61               | 2**-61 and above               |
| 62               | 2**-62 and above               |

These probabilities are specified to ensure that conforming Sampler
implementations record spans with correct adjusted counts.  The
recommended method of generating r-values is to count the number of
leading 0s in a string of 62 random bits, however it is not required
to use this approach.

##### Requirement: Out-of-range r-values unset both p and r

Samplers SHOULD unset both `r` and `p` from the `tracestate` if the
unsigned decimal value of `r` is greater than 62 before using the
`tracestate` to make a sampling decision.

##### Requirement: R-value is generated with the correct probabilities

Samplers MUST generate r-values using a randomized scheme that
produces each value with the probabilities equivalent to those
produced by counting the number of leading 0s in a string of 62 random
bits.

#### Examples: Context invariants

##### Example: Probability sampled context

Consider a trace context with the following headers:

```
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
tracestate: ot=r:3;p:2
```

The `traceparent` contents in this example example are repeated from
the [W3C specification](https://www.w3.org/TR/trace-context/#examples-of-http-traceparent-headers))
and have the following base64-encoded field values:

```
base16(version) = 00
base16(trace-id) = 4bf92f3577b34da6a3ce929d0e0e4736
base16(parent-id) = 00f067aa0ba902b7
base16(trace-flags) = 01  // (i.e., sampled)
```

The `tracestate` header contains OpenTelemetry string `r:3;p:2`,
containing decimal-encoded p-value and r-value:

```
base10(r) = 3
base10(p) = 2
```

Here, r-value 3 indicates that a consistent probability sampler
configured with probability 12.5% (i.e., 1-in-8) or greater will
sample the trace.  The p-value 2 indicates that the parent that set
the `sampled` flag was configured to sample at 25% (i.e., 1-in-4).
This trace context is consistent because `p <= r` is true and the
`sampled` flag is set.

##### Example: Probability unsampled

This example has an unsampled context where only the r-value is set.

```
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-00
tracestate: ot=r:3
```

This supports consistent probability sampling in child contexts by
virtue of having an r-value.  P-value is not set, consistent with an
unsampled context.

### Samplers

#### ParentConsistentProbabilityBased sampler

The `ParentConsistentProbabilityBased` sampler is meant as an optional
replacement for the [`ParentBased` Sampler][SDK_SPEC#parentbased]. It is
required to first validate the `tracestate` and then respect the
`sampled` flag in the W3C traceparent.

##### Requirement: ParentConsistentProbabilityBased API

The `ParentConsistentProbabilityBased` Sampler constructor SHOULD take
a single Sampler argument, which is the Sampler to use in case the
`ParentConsistentProbabilityBased` Sampler is called for a root span.

##### Requirement: ParentConsistentProbabilityBased does not modify valid tracestate

The `ParentConsistentProbabilityBased` Sampler MUST NOT modify a
valid `tracestate`.

##### Requirement: ParentConsistentProbabilityBased calls the configured root sampler for root spans

The `ParentConsistentProbabilityBased` Sampler MUST delegate to the
configured root Sampler when there is not a valid parent trace context.

##### Requirement: ParentConsistentProbabilityBased respects the sampled flag for non-root spans

The `ParentConsistentProbabilityBased` Sampler MUST decide to sample
the span according to the value of the `sampled` flag in the W3C
traceparent header.

#### ConsistentProbabilityBased sampler

The `ConsistentProbabilityBased` sampler is meant as an optional
replacement for the [`TraceIdRatioBased`
Sampler][SDK_SPEC#traceidratiobased].  In the case where it is used as a
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

##### Requirement: TraceIdRatioBased API compatibility

The `ConsistentProbabilityBased` Sampler MUST have the same
constructor signature as the built-in `TraceIdRatioBased` sampler in
each OpenTelemetry SDK.

##### Requirement: ConsistentProbabilityBased sampler sets r for root span

The `ConsistentProbabilityBased` Sampler MUST set `r` when it makes a
root sampling decision.

##### Requirement: ConsistentProbabilityBased sampler unsets p when not sampled

The `ConsistentProbabilityBased` Sampler MUST unset `p` from the
`tracestate` when it decides not to sample.

##### Requirement: ConsistentProbabilityBased sampler sets p when sampled

The `ConsistentProbabilityBased` Sampler MUST set `p` when it decides
to sample according to its configured sampling probability.

##### Requirement: ConsistentProbabilityBased sampler records unbiased adjusted counts

The `ConsistentProbabilityBased` Sampler with non-zero probability
MUST set `p` so that the adjusted count interpreted from the
`tracestate` is an unbiased estimate of the number of representative
spans in the population.

##### Requirement: ConsistentProbabilityBased sampler sets r for non-root span

If `r` is not set on the input `tracecontext` and the Span is not a
root span, `ConsistentProbabilityBased` SHOULD set `r` as if it were a
root span and warn the user that a potentially inconsistent trace
is being produced.

##### Requirement: ConsistentProbabilityBased sampler decides not to sample for probabilities less than 2**-62

If the configured sampling probability is in the interval `[0,
2**-62)`, the Sampler MUST decide not to sample.

#### Examples: Consistent probability samplers

##### Example: Setting R-value for a root span

A new root span is sampled by a consistent probability sampler at 25%.
A new r-value should be generated (see the appendix for suitable
methods), in this example r-value 5 is used which happens 1.5625% of
the time and indicates to sample:

```
tracestate: ot=r:5;p:2
```

The span would be sampled because p-value 2 is less than or equal to
r-value 5.  An example `tracestate` where r-value 1 indicates not to
sample at 25%:

```
tracestate: ot=r:1
```

This span would not be sampled because p-value 2 (corresponding with
25% sampling) is greater than r-value 1.

##### Example: Handling inconsistent P-value

When either the consistent probability sampler or the parent-based
consistent probability sampler receives a sampled context but
invalid p-value, for example,

```
tracestate: ot=r:4;p:73
```

the `tracestate` will have its p-value stripped.  The r-value is kept,
and the sampler should act as if the following had been received:

```
tracestate: ot=r:4
```

The consistent probability sampler will make its own (consistent)
decision using the r-value that was received.

The parent-based consistent probability sampler will in this case
follow the `sampled` flag.  If the context is sampled, the resulting
span will have an r-value without a p-value, which indicates unknown
adjusted count.

##### Example: Handling corrupt R-value

A non-root span receives:

```
tracestate: ot=r:100;p:10
```

where the r-value is out of its valid range. The r-value and p-value
are stripped during validation, according to the invariants.  In this
case, the sampler will act as though no `tracestate` were received.

The parent-based consistent probability sampler will sample or not
sample based on the `sampled` flag, in this case.  If the context is
sampled, the recorded span will have an r-value without a p-value,
which indicates unknown adjusted count.

The consistent probability sampler will generate a new r-value and
make a new sampling decision while warning the user of a corrupt and
potentially inconsistent r-value.

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

##### Requirement: Combining multiple sampling decisions using logical `or`

When multiple samplers are combined using composition, the sampling
decision MUST be to sample if at least one of the combined samplers
decides to sample.

##### Requirement: Combine multiple consistent probability samplers using the minimum p-value

When combining Sampler decisions for multiple consistent probability
Samplers and at least one decides to sample, the minimum of the "yes"
decision `p` values MUST be set in the `tracestate`.

##### Requirement: Unset p when multiple consistent probability samplers decide not to sample

When combining Sampler decisions for multiple consistent probability
Samplers and none decides to sample, p-value MUST be unset in the
`tracestate`.

##### Requirement: Use probability sampler p-value when its decision to sample is combined with non-probability samplers

When combining Sampler decisions for a consistent probability Sampler
and a non-probability Sampler, and the probability Sampler decides to
sample, its p-value MUST be set in the `tracestate` regardless of the
non-probability Sampler decision.

##### Requirement: Use p-value 63 when a probability sampler decision not to sample is combined with a non-probability sampler decision to sample

When combining Sampler decisions for a consistent probability Sampler
and a non-probability Sampler, and the probability Sampler decides not
to sample but the non-probability does sample, p-value 63 MUST be set
in the `tracestate`.

#### Examples: Composition

##### Example: Probability and non-probability sampler in a root context

In a new root context, a consistent probability sampler decides not to
set the sampled flag, adds `r:4` indicating that the trace is
consistently sampled at 6.5% (i.e., 1-in-16) and larger probabilities.

The probability sampler decision is composed with a non-probability
sampler that decides to sample the context.  Setting `sampled` when
the probability sampler has not sampled requires setting `p:63`,
indicating zero adjusted count.

The resulting context:

```
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
tracestate: ot=r:4;p:63
```

##### Example: Two consistent probability samplers

Whether a root or non-root, if multiple consistent probability
samplers make a decision to sample a given context, the minimum
p-value is output in the tracestate.

If a root context, the first of the samplers generates `r:15` and its
own p-value `p:10` (i.e., adjusted count 1024).  The second of the two
probability samplers outputs a smaller adjusted count `p:8` (i.e.,
adjusted count 256).

The resulting context takes the smaller p-value:

```
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
tracestate: ot=r:15;p:8
```

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
non-power-of-two sampling probabilities for non-root spans, because
completeness is not guaranteed for non-power-of-two sampling
probabilities.

##### Recommendation: use non-descending power-of-two probabilities

Complete subtraces will be produced when the sequence of sampling
probabilities from the root of a trace to its leaves consists of
non-descending powers of two.  To ensure complete sub-traces are
produced, child samplers SHOULD be configured with a power-of-two
probability greater than or equal to the parent span's sampling
probability.

#### Trace producer: correctness

The use of tracestate to convey adjusted count information rests upon
trust between participants in a trace.  Users are advised not to use a
Span-to-metrics pipeline when the parent sampling decision's
corresponding adjusted count is untrustworthy.

The `ConsistentProbabilityBased` and
`ParentConsistentProbabilityBased` samplers can be used as delegates
of another sampler, for conditioning the choice of sampler on span and
other fixed attributes.  However, for adjusted counts to be
trustworthy, the choice of non-root sampler cannot be conditioned on
the parent's sampled trace flag or the OpenTelemetry tracestate
r-value and p-value, as these decisions would lead to incorrect
adjusted counts.

For example, the built-in [`ParentBased` sampler][SDK_SPEC#parentbased]
supports configuring the delegated-to sampler based on whether the parent
context is remote or non-remote, sampled or unsampled.  If a
`ParentBased` sampler delegates to a `ConsistentProbabilityBased`
sampler only for unsampled contexts, the resulting Span-to-metrics
pipeline will (probably) overcount spans.

##### Recommendation: sampler delegation

For non-root spans, composite samplers SHOULD NOT condition the choice
of delegated-to sampler based on the parent's sampled flag or
OpenTelemetry tracestate.

#### Trace producer: interoperability with `ParentBased` sampler

The OpenTelemetry built-in `ParentBased` sampler is interoperable with
the `ConsistentProbabilityBased` sampler, provided that the
delegated-to sampler does not change the decision that determined its
selection.  For example, it is safe to configure an alternate
`ParentBased` sampler delegate for unsampled spans, provided the
decision does not change to sampled.

Because the `ParentBased` sampler honors the sampled trace flag, and
OpenTelemetry SDKs include the tracestate in the `Span` data, which
means a system can be upgraded to probability sampling by just
replacing `TraceIDRatioBased` samplers with conforming
`ConsistentProbabilityBased` samplers everywhere in the trace.

#### Trace producer: interoperability with `TraceIDRatioBased` sampler

The [`TraceIDRatioBased` specification][SDK_SPEC#traceidratiobased]
includes a RECOMMENDATION against being used for non-root spans
because it does not specify how to make the sampler decision
consistent across the trace.  A `TraceIDRatioBased` sampler at the
root span is interoperable with a `ConsistentParentProbabilityBased`
sampler in terms of completeness, although the resulting spans will
have unknown adjusted count.

When a `TraceIDRatioBased` sampler is configured for a non-root span,
several cases arise where an incorrect OpenTelemetry tracestate can be
generated.  Consider for example a trace with three spans where the
root (R) has a `ConsistentProbabilityBased` sampler, the root's child
(P) has a `TraceIDRatioBased` sampler, and the grand-child (C) has a
`ParentBased` sampler.  Because the `TraceIDRatioBased` sampler change
the intermediate sampled flag without updating the OpenTelemetry
tracestate, we have the following cases:

1. If `TraceIDRatioBased` does not change P's decision, the trace is
   complete and all spans' adjusted counts are correct.
2. If `TraceIDRatioBased` changes P's decision from no to yes, the
   consumer will observe a (definitely) incomplete trace containing P
   and C.  Both spans will have invalid OpenTelemetry tracestate,
   leading to unknown adjusted count in this case.
3. If `TraceIDRatioBased` changes the sampling decision from yes to
   no, the consumer will observe singleton trace with correct adjusted
   count. The consumer cannot determine that R has two unsampled
   descendants.

As these cases demonstrate, users can expect incompleteness and
unknown adjusted count when using `TraceIDRatioBased` samplers for
non-root spans, but this goes against the originally specified
warning.

#### Trace consumer

Trace consumers are expected to apply the simple one-way test for
incompleteness.  When non-root spans are configured with independent
sampling probabilities, traces may be complete in a way that cannot be
detected.  Because of the one-way test, consumers wanting to ensure
complete traces are expected to know the minimum sampling probability
across the system.

Ignoring accidental data loss, a trace will be complete if all its
spans are sampled with consistent probability samplers and the trace's
r-value is larger than the corresponding smallest power of two greater
than or equal to the minimum sampling probability across the trace.

Due to the `ConsistentProbabilityBased` Sampler requirement about
setting `r` when it is unset for a non-root span, trace consumers are
advised to check traces for r-value consistency.  When a single trace
contains more than a single distinct `r` value, it means the trace was
not correctly sampled at the root for probability sampling.  While the
adjusted count of each span is correct in this scenario, it may be
impossible to detect complete traces.

##### Recommendation: Recognize inconsistent r-values

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
- Use a population size of 100,000 spans
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
|-----------|----------------------|-----------------------------------|------------------------|------------------------|----------------------------|
| 1         | 0.900000             | 0, 1                              | 80000                  | 10000                  | 10000                      |
| 2         | 0.600000             | 0, 1                              | 20000                  | 40000                  | 40000                      |
| 3         | 0.330000             | 1, 2                              | 16000                  | 17000                  | 67000                      |
| 4         | 0.130000             | 2, 3                              | 1000                   | 12000                  | 87000                      |
| 5         | 0.100000             | 3, 4                              | 7500                   | 2500                   | 90000                      |
| 6         | 0.050000             | 4, 5                              | 3750                   | 1250                   | 95000                      |
| 7         | 0.017000             | 5, 6                              | 275                    | 1475                   | 98300                      |
| 8         | 0.010000             | 6, 7                              | 437.5                  | 562.5                  | 99000                      |
| 9         | 0.005000             | 7, 8                              | 218.75                 | 281.25                 | 99500                      |
| 10        | 0.002900             | 8, 9                              | 189.375                | 100.625                | 99710                      |
| 11        | 0.001000             | 9, 10                             | 4.6875                 | 95.3125                | 99900                      |
| 12        | 0.000500             | 10, 11                            | 2.34375                | 47.65625               | 99950                      |

The formula for computing Chi-Squared in this case is:

```
ChiSquared = math.Pow(sampled_lowerP - expect_lowerP, 2) / expect_lowerP +
             math.Pow(sampled_upperP - expect_upperP, 2) / expect_upperP +
             math.Pow(100000 - sampled_lowerP - sampled_upperP - expect_unsampled, 2) / expect_unsampled
```

This should be compared with 0.102587, the value of the Chi-Squared
distribution for two degrees of freedom with significance level 5%.
For each probability in the table above, the test is required to
demonstrate a seed that produces exactly one ChiSquared value less
than 0.102587.

##### Requirement: Pass 12 non-power-of-two statistical tests

For the test with 20 trials and 100,000 spans each, the test MUST
demonstrate a random number generator seed such that the ChiSquared
test statistic is below 0.102587 exactly 1 out of 20 times.

#### Test procedure: exact powers of two

In this case there is one degree of freedom for the Chi-Squared test.
The following table summarizes the test parameters.

| Test case | Sampling probability | P-value when sampled | Expect<sub>sampled</sub> | Expect<sub>unsampled</sub> |
|-----------|----------------------|----------------------|--------------------------|----------------------------|
| 13        | 0x1p-01 (0.500000)   | 1                    | 50000                    | 50000                      |
| 14        | 0x1p-04 (0.062500)   | 4                    | 6250                     | 93750                      |
| 15        | 0x1p-07 (0.007812)   | 7                    | 781.25                   | 99218.75                   |

The formula for computing Chi-Squared in this case is:

```
ChiSquared = math.Pow(sampled - expect_sampled, 2) / expect_sampled +
             math.Pow(100000 - sampled - expect_unsampled, 2) / expect_unsampled
```

This should be compared with 0.003932, the value of the Chi-Squared
distribution for one degree of freedom with significance level 5%.
For each probability in the table above, the test is required to
demonstrate a seed that produces exactly one ChiSquared value less
than 0.003932.

##### Requirement: Pass 3 power-of-two statistical tests

For the test with 20 trials and 100,000 spans each, the test MUST
demonstrate a random number generator seed such that the ChiSquared
test statistic is below 0.003932 exactly 1 out of 20 times.

#### Test implementation

The recommended structure for this test uses a table listing the 15
probability values, the expected p-values, whether the ChiSquared
statistic has one or two degrees of freedom, and the index into the
predetermined list of seeds.

```
    for _, test := range []testCase{
        // Non-powers of two
        {0.90000, 1, twoDegrees, 3},
        {0.60000, 1, twoDegrees, 2},
        {0.33000, 2, twoDegrees, 2},
        {0.13000, 3, twoDegrees, 1},
        {0.10000, 4, twoDegrees, 0},
        {0.05000, 5, twoDegrees, 0},
        {0.01700, 6, twoDegrees, 2},
        {0.01000, 7, twoDegrees, 2},
        {0.00500, 8, twoDegrees, 2},
        {0.00290, 9, twoDegrees, 4},
        {0.00100, 10, twoDegrees, 6},
        {0.00050, 11, twoDegrees, 0},

        // Powers of two
        {0x1p-1, 1, oneDegree, 0},
        {0x1p-4, 4, oneDegree, 0},
        {0x1p-7, 7, oneDegree, 1},
    } {
```

Note that seed indexes in the example above have what appears to be
the correct distribution.  The five 0s, two 1s, five 2s, one 3s, and
one 4 demonstrate that it is relatively easy to find examples where
there is exactly one failure.  Probability 0.001, with seed index 6 in
this case, is a reminder that outliers exist.  Further significance
testing of this distribution is not recommended.

## Appendix

### Methods for generating R-values

The method used for generating r-values is not specified, in order to
leave the implementation freedom to optimize.  Typically, when the
TraceId is known to contain at a 62-bit substring of random bits,
R-values can be derived directly from the 62 random bits of TraceId
by:

1. Count the leading zeros
2. Count the leading ones
3. Count the trailing zeros
4. Count the trailing ones.

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

If the TraceId contains unknown or insufficient randomness, another
approach is to generate random bits until the first true or false
value.

```
func nextRValueGenerated() int {
    for r := 0; r < 62; r++ {
        if rand.Bool() == true {
            return r
        }
    }
    return 62
}
```

Any scheme that produces r-values shown in the following table is
considered conforming.

| r-value          | Probability of r-value   |
| ---------------- | ------------------------ |
| 0                | 1/2                      |
| 1                | 1/4                      |
| 2                | 1/8                      |
| 3                | 1/16                     |
| ...              | ...                      |
| 0 <= r <= 61     | 2**-(r+1)                |
| ...              | ...                      |
| 59               | 2**-60                   |
| 60               | 2**-61                   |
| 61               | 2**-62                   |
| 62               | 2**-62                   |
