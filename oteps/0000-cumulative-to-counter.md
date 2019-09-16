# Rename "Cumulative" to "Counter" in the metrics API

**Status:** `proposed`

Prefer the name "Counter" as opposed to "Cumulative".

## Motivation

Informally speaking, it seems that OpenTelemetry community members would prefer to call Cumulative metric instruments "Counters".  During conversation (e.g., in the 8/21 working session), this has become clear.

Counter is a noun, like the other kinds Gauge and Measure.  Cumulative is an adjective, so while "Cumulative instrument" makes sense, it describes a "Counter".

## Explanation

This will eliminate the cognitive cost of mapping "cumulative" to "counter" when speaking about these APIs.

This is the term used for a cumulative metric instrument, for example, in [Statsd](https://github.com/statsd/statsd/blob/master/docs/metric_types.md) and [Prometheus](https://prometheus.io/docs/concepts/metric_types/#counter).  

However, we have identified important sub-cases of Counter that are treated as follows.  Counters have an option:

- True-cumulative Counter: By default, `Add()` arguments must be >= 0.
- Bi-directional Counter: As an option, `Add()` arguments must be +/-0.

Gauges are sometimes used to monitoring non-descending quantities (e.g., cpu usage), as an option:

- Bi-directional Gauge: By default, `Set()` arguments may by +/- 0.
- Uni-directional Gauge: As an option, `Set()` arguments must change by >= 0.

Uni-directional Gauge instruments are typically used in metric `Observer` callbacks where the observed value is cumulative.

## Trade-offs and mitigations

Other ways to describe the distinction between true-cumulative and bi-directional Counters are:

- Additive (vs. Cumulative)
- GaugeDelta (vs. Gauge)

It is possible that reducing all of these cases into the broad term "Counter" creates more confusion than it addresses.

## Internal details

Simply replace every "Cumulative" with "Counter", then edit for grammar. 

## Prior art and alternatives

In a survey of existing metrics libraries, Counter is far more common.
