# Consolidate pre-aggregated and raw metrics APIs

**Status:** `proposed`

## Forward

This propsal was originally split into three semi-related parts. Based on the feedback, they are now combined here into a single proposal. The original proposals were:

    000x-metric-pre-defined-labels
    000x-metric-measure
    000x-eliminate-stats-record

## Overview

Introduce a `Measure` type of metric object that supports a `Record` API.  Like existing `Gauge` and `Cumulative` metrics, the new `Measure` metric supports pre-defined labels.  A new measurement batch API is introduced for recording multiple metric observations simultaneously.

## Motivation

In the current `Metric.GetOrCreateTimeSeries` API for Gauges and Cumulatives, the caller obtains a `TimeSeries` handle for repeatedly recording metrics with certain pre-defined label values set.  This is an important optimization, especially for exporting aggregated metrics.

The use of pre-defined labels improves usability too, for working with metrics in code. Application programs with long-lived objects and associated Metrics can compute predefined label values once (e.g., in a constructor), rather than once per call site.

The current raw statistics API does not support pre-defined labels.  This RFC replaces the raw statistics API by a new, general-purpose type of metric, `MeasureMetric`, generally intended for recording individual measurements the way raw statistics did, with added support for pre-defined labels.

The former raw statistics API supported all-or-none recording for interdependent measurements.  This RFC introduces a `MeasurementBatch` to support recording batches of metric observations.

## Explanation

In the current proposal, Metrics are used for pre-aggregated metric types, whereas Raw statistics are used for uncommon and vendor-specific aggregations.  The optimization and the usability advantages gained with pre-defined labels should be extended to Raw statistics because they are equally important and equally applicable. This is a new requirement.

For example, where the application wants to compute a histogram of some value (e.g., latency), there's good reason to pre-aggregate such information.  In this example, it allows an implementation to effienctly export the histogram of latencies "grouped" into individual results by label value(s).

The new `MeasureMetric` API satisfies the requirements of a single-argument call to record raw statistics, but the raw statistics API had secondary purpose, that of supporting recording multiple observed values simultaneously.  This proposal introduces a `MeasurementBatch` API to record multiple metric observations in a single call.

## Internal details

The type known as `MeasureMetric` is a direct replacement for the raw statistics `Measure` type.  The `MeasureMetric.Record` method records a single observation of the metric.  The `MeasureMetric.GetOrCreateTimeSeries` supports pre-defined labels, just the same as `Gauge` and `Cumulative` metrics.

## Trade-offs and mitigations

This Measure Metric API is conceptually close to the Prometheus [Histogram, Summary, and Untyped metric types](https://prometheus.io/docs/concepts/metric_types/), but there is no way in OpenTelemetry to distinguish these cases at the declaration site, in code.  This topic is covered in 0004-metric-configurable-aggregation.

## Prior art and alternatives

Prometheus supports the notion of vector metrics, which are those which support pre-defined labels.  The vector-metric API supports a variety of methods like `WithLabelValues` to associate labels with a metric handle, similar to `GetOrCreateTimeSeries` in OpenTelemetry.  As in this proposal, Prometheus supports a vector API for all metric types.

## Open questions

Argument ordering has been proposed as the way to pass pre-defined label values in `GetOrCreateTimeseries`.  The argument list must match the parameter list exactly, and if it doesn't we generally find out at runtime or not at all.  This model has more optimization potential, but is easier to misuse, than the alternative.  The alternative approach is to always pass label:value pairs to `GetOrCreateTimeseries`, as opposed to an ordered list of values. 

The same discussion can be had for the `MeasurementBatch` type described here.  It can be declared with an ordered list of metrics, then the `Record` API takes only an ordered list of numbers.  Alternatively, and less prone to misuse, the `MeasurementBatch.Record` API could be declared with a list of metric:number pairs.
