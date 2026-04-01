# Metrics observer specification

**Status:** Superceded entirely by [0072-metric-observer](0072-metric-observer.md)

Propose metric `Observer` callbacks for context-free access to current Gauge instrument values on demand.

## Motivation

The current specification describes metric callbacks as an alternate means of generating metrics for the SDK, allowing the application to generate metrics only as often as desired by the monitoring infrastructure.  This proposal limits callback metrics to only support gauge `Observer` callbacks, arguably the only important case.

## Explanation

Gauge metric instruments are typically used to reflect properties that are pre-computed by a system, where the measurement interval is arbitrary.  When selecting a gauge, as opposed to the cumulative or measure kind of metric instrument, there could be significant computational cost in computing the current value.  When this is the case, it is understandable that we are interested in computing them on demand to minimize cost.

Why are gauges different than cumulative and measure instruments?  Measure instruments, by definition, carry information in the individual event, so the callback cannot optimize any better than the SDK can in this case.  Cumulative instruments are more commonly used to record amounts that are readily available, such as the number of bytes read or written, and while this may not always be true, recall the special case of `NonDescending` gauges.

`NonDescending` gauges owe their existence to this case, that we support non-negative cumulative metrics which, being expensive to compute, are recommended for use with `Observer` callbacks.  For example, if it requires a system call or more to compute a non-descending sum, such as the _CPU seconds_ consumed by the process, we should declare a non-descending gauge `Observer` for the instrument, instead of a cumulative.  This allows the cost of the metric to be reduced according to the desired monitoring frequency.

One significant difference between gauges that are explicitly `Set()`, as compared with observer callbacks, is that `Set()` happens inside a context, whereas the observer callback does not.

## Details

Observer callbacks are only supported for gauge metric instruments.  Use the language-specific constructor for an Observer gauge (e.g., `metric.NewFloat64Observer()`).  Observer gauges support the `NonDescending` option.

Callbacks return a map from _label set_ to gauge value. Gauges declared with observer callbacks cannot also be `Set`.

Callbacks should avoid blocking.  The implementation may be required to cancel computation if the callback blocks for too long.

Callbacks must not be called synchronously with application code via any OpenTelemetry API.  Implementations that cannot provide this guarantee should prefer not to implement observer callbacks.

Callbacks may be called synchronously in the SDK on behalf of an exporter.

Callbacks should avoid calling OpenTelemetry APIs, but we recognize this may be impossible to enforce.

## Trade-offs and mitigations

Callbacks are a relatively dangerous programming pattern, which may require care to avoid deadlocks between the application and the API or the SDK.  Implementations may consider preventing deadlocks through runtime callstack introspection, to make these interfaces absolutely safe.
