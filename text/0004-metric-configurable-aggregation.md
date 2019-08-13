# Let Metrics support configrable, recommended aggregations

**Status:** `proposed`

Let the user configure recommended Metric aggregations (SUM, COUNT, MIN, MAX, LAST_VALUE, HISTOGRAM, SUMMARY).

## Motivation

In the current API proposal, Metric types like Gauge and Cumulative are mapped into specific aggregations: Gauge:LAST_VALUE and Cumulative:SUM.  Depending on RFC 0003-measure-metric-type, which creates a new MeasureMetric type, this proposal introduces the ability to configure alternative, potentially multiple aggregations for Metrics.  This allows the MeasureMetric type to support HISTOGRAM and SUMMARY aggregations, as an alternative to raw statistics.

## Explanation

This proposal completes the elimination of Raw statistics by recognizing that aggregations should be independent of metric type.  This recognizes that _sometimes_ we have a cumulative but want to compute a histogram of increment values, and _sometimes_ we have a measure that has multiple interesting aggregations.

Following this change, we should think of the _Metric type_ as:

1. Indicating something about what kind of numbers are being recorded (i.e., the input domain, e.g., restricted to values >= 0?)
   1. For Gauges: Something pre-computed where rate or count is not relevant
   1. For Cumulatives: Something where rate or count is relevant
   1. For Measures: Something where individual values are relevant
1. Indicating something about the default interpretation, based on the action verb (Set, Inc, Record, etc.)
   1. For Gauges: the action is Set()
   1. For Cumulatives: the action is Inc()
   1. For Measures: the action is Record()
1. Unless the programmer declares otherwise, suggesting a default aggregation
   1. For Gauges: LAST_VALUE is interesting, SUM is likely not interesting
   1. For Cumulatives: SUM is interesting, LAST_VALUE is likely not interesting
   1. For Measures: all aggregations apply, default is MIN, MAX, SUM, COUNT.

## Internal details

Metric constructors should take an optional list of aggregations, to override the default behavior.  When constructed with an explicit list of aggregations, the implementation may use this as a hint about which aggregations should be exported by default.  However, the implementation is not bound by these recommendations in any way and is free to control which aggregations that are applied.

The standard defined aggregations are broken into two groups, those which are "decomposable" (i.e., inexpensive) and those which are not.

The decomposable aggregations are simple to define:

1. SUM: The sum of observed values.
1. COUNT: The number of observations.
1. MIN: The smallest value.
1. MAX: The largest value.
1. LAST_VALUE: The latest value.

The non-decomposable aggregations do not have standard definitions, they are purely advisory.  The intention behind these are:

1. HISTOGRAM: The intended output is a distribution summary, specifically summarizing counts into non-overlapping ranges.
1. SUMMARY: This is a more generic way to request information about a distribution, perhaps represented in some vendor-specific way / not a histogram.

## Example

To declare a MeasureMetric,

```
   myMetric := metric.NewMeasureMetric(
		   "ex.com/mymetric",
	           metric.WithAggregations(metric.SUM, metric.COUNT),
		   metric.WithLabelKeys(aKey, bKey))
)
```

Here, we have declared a Measure-type metric with recommended SUM and COUNT aggregations (allowing to compute the average) with `aKey` and `bKey` as recommended aggregation dimensions.  While the SDK has full control over which aggregations are actually performed, the programmer has specified a good default behavior for the implementation to use.

## Trade-offs and mitigations

This avoids requiring programmers to use the `view` API, which is an SDK API, not a user-facing instrumentation API. Letting the application programmer recommend aggregations directly gives the implementation more information about the raw statistics. Letting programmers declare their intent has few downsides, since there is a well-defined default behavior.

## Prior art and alternatives

Existing systems generally declare separate Metric types according to the desired aggregation.  Raw statistics were invented to overcome this, and the present proposal brings back the ability to specify an Aggregation at the point where a Metric is defined.

## Open questions

There are questions about the value of the MIN and MAX aggregations.  While they are simple to compute, they are difficult to use in practice.

There are questions about the interpretation of HISTOGRAM and SUMMARY. The point of Raw statistics was that we shouldn't specify these aggregations because they are expensive and many implementations are possible.  This is still true. What is the value in specifying HISTOGRAM as opposed to SUMMARY?  How is SUMMARY different from MIN/MAX/COUNT/SUM, does it imply implementation-defined quantiles?
