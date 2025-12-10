# Consolidate pre-aggregated and raw metrics APIs

## Foreword

A working group convened on 8/21/2019 to discuss and debate the two metrics RFCs (0003 and 0004) and several surrounding concerns.  This document has been revised with related updates that were agreed upon during this working session.  See the [meeting notes](https://docs.google.com/document/d/1d0afxe3J6bQT-I6UbRXeIYNcTIyBQv4axfjKF4yvAPA/edit#).

## Overview

Introduce a `Measure` kind of metric object that supports a `Record` API method.  Like existing `Gauge` and `Cumulative` metrics, the new `Measure` metric supports pre-defined labels.  A new `RecordBatch` measurement API  is introduced for recording multiple metric observations simultaneously.

## Terminology

This RFC changes how "Measure" is used in the OpenTelemetry metrics specification.  Before, "Measure" was the name of a series of raw measurements.  After, "Measure" is the kind of a metric object used for recording a series raw measurements.

Since this document will be read in the future after the proposal has been written, uses of the word "current" lead to confusion.  For this document, the term "preceding" refers to the state that was current prior to these changes.

The preceding specification used the term `TimeSeries` to describe an instrument bound with a set of pre-defined labels.  In this document, [the term "Handle" is used to describe an instrument with bound labels](0009-metric-handles.md).  In a future OTEP this will be again changed to "Bound instrument".  The term "Handle" is used throughout this document to refer to a bound instrument.

## Motivation

In the preceding `Metric.GetOrCreateTimeSeries` API for Gauges and Cumulatives, the caller obtains a `TimeSeries` handle for repeatedly recording metrics with certain pre-defined label values set.  This enables an important optimization for exporting pre-aggregated metrics, since the implementation is able to compute the aggregate summary "entry" using a pointer or fast table lookup. The efficiency gain requires that the aggregation keys be a subset of the pre-defined labels.

Application programs with long-lived objects and associated Metrics can take advantage of pre-defined labels by computing label values once per object (e.g., in a constructor), rather than once per call site. In this way, the use of pre-defined labels improves the usability of the API as well as makes an important optimization possible to the implementation.

The preceding raw statistics API did not specify support for pre-defined labels.  This RFC replaces the raw statistics API by a new, general-purpose kind of metric, `MeasureMetric`, generally intended for recording individual measurements like the preceding raw statistics API, with explicit support for pre-defined labels.

The preceding raw statistics API supported all-or-none recording for interdependent measurements using a common label set.  This RFC introduces a `RecordBatch` API to support recording batches of measurements in a single API call, where a `Measurement` is now defined as a pair of `MeasureMetric` and `Value` (integer or floating point).

## Explanation

The common use for `MeasureMetric`, like the preceding raw statistics API, is for reporting information about rates and distributions over structured, numerical event data.  Measure metrics are the most general-purpose of metrics.  Informally, the individual metric event has a logical format expressed as one primary key=value (the metric name and a numerical value) and any number of secondary key=values (the labels, resources, and context).

    metric_name=_number_
    pre_defined1=_any_value_
    pre_defined2=_any_value_
    ...
    resource1=_any_value_
    resource2=_any_value_
    ...
    context_tag1=_any_value_
    context_tag2=_any_value_
    ...

Here, "pre_defined" keys are those captured in the metrics handle, "resource" keys are those configured when the SDK was initialized, and "context_tag" keys are those propagated via context.

Events of this form can logically capture a single update to a named metric, whether a cumulative, gauge, or measure kind of metric.  This logical structure defines a _low-level encoding_ of any metric event, across the three kinds of metric.  An SDK could simply encode a stream of these events and the consumer, provided access to the metric definition, should be able to interpret these events according to the semantics prescribed for each kind of metric.

## Metrics API concepts

The `Meter` interface represents the metrics portion of the OpenTelemetry API.

There are three kinds of metric instrument, `CumulativeMetric`, `GaugeMetric`, and `MeasureMetric`.

Metric instruments are constructed through the `Meter` API. Constructing an instrument automatically registers it with the SDK. The common attributes of a metric instrument are:

| Field | Description |
| ----- | ----------- |
| Name | A string. |
| Kind | One of Cumulative, Gauge, or Measure. |
| Recommended Keys | Default aggregation keys. |
| Unit | The unit of measurement being recorded. |
| Description | Information about this metric. |

See the specification for more information on these fields, including formatting and uniqueness requirements.  To define a new metric, use one of the `Meter` API methods (e.g., with names like `NewCumulativeMetric`, `NewGaugeMetric`, or `NewMeasureMetric`).

Metric instrument Handles combine a metric instrument with a set of pre-defined labels.  Handles are obtained by calling a language-specific API method (e.g., `GetHandle`) on the metric instrument with certain label values.  Handles may be used to `Set()`, `Add()`, or `Record()` metrics according to their kind.

## Selecting Metric Kind

By separation of API and implementation in OpenTelemetry, we know that an implementation is free to do _anything_ in response to a metric API call.  By the low-level interpretation defined above, all metric events have the same structural representation, only their logical interpretation varies according to the metric definition.  Therefore, we select metric kinds based on two primary concerns:

1. What should be the default implementation behavior?  Unless configured otherwise, how should the implementation treat this metric variable?
2. How will the program source code read?  Each metric uses a different verb, which helps convey meaning and describe default behavior.  Cumulatives have an `Add()` method.  Gauges have a `Set()` method.  Measures have a `Record()` method.

To guide the user in selecting the right kind of metric for an application, we'll consider the following questions about the primary intent of reporting given data.  We use "of primary interest" here to mean information that is almost certainly useful in understanding system behavior.  Consider these questions:

- Does the measurement represent a quantity of something?  Is it also non-negative?
- Is the sum a matter of primary interest?
- Is the event count a matter of primary interest?
- Is the distribution (p50, p99, etc.) a matter of primary interest?

The specification will be updated with the following guidance.

### Cumulative metric

Likely to be the most common kind of metric, cumulative metric events express the computation of a sum.  Choose this kind of metric when the value is a quantity, the sum is of primary interest, and the event count and distribution are not of primary interest.  To raise (or lower) a cumulative metric, call the `Add()` method.

If the quantity in question is always non-negative, it implies that the sum is monotonic.  This is the common case, `Monotonic(true)`, where cumulative sums only rise, and these metric instruments serve to compute a rate.  For this reason, cumulative metrics have a `Monotonic(false)` option to be declared as allowing negative inputs, the uncommon case.  The SDK should reject negative inputs to monotonic cumulative metrics, but it is not required to.

For cumulative metrics, the default OpenTelemetry implementation exports the sum of event values taken over an interval of time.

### Gauge metric

Gauge metrics express a pre-calculated value that is either `Set()` by explicit instrumentation or observed through a callback.  Generally, this kind of metric should be used when the metric cannot be expressed as a sum or a rate because the measurement interval is arbitrary.  Use this kind of metric when the measurement is a computed value and the sum and event count are not of interest.

Only the gauge kind of metric supports observing the metric via a gauge `Observer` callback (as an option, see `0008-metric-observer.md`).  Semantically, there is an important difference between explicitly setting a gauge and observing it through a callback.  In case of setting the gauge explicitly, the `Set()` call happens inside of an implicit or explicit context.  The implementation is free to associate the explicit `Set()` event with a context, for example.  When observing gauge metrics via a callback, there is no context associated with the event.

As a special case, to support existing metrics infrastructure and the `Observer` pattern, a gauge metric may be declared as a precomputed, monotonic sum using the `Monotonic(true)` option, in which case it is may be used to define a rate.  The initial value is presumed to be zero.  The SDK should reject descending updates to monotonic gauges, but it is not required to.  

For gauge metrics, the default OpenTelemetry implementation exports the last value that was explicitly `Set()`, or if using a callback, the current value from the `Observer`.

### Measure metric

Measure metrics express a distribution of measured values.  This kind of metric should be used when the count or rate of events is meaningful and either:

1. The sum is of interest in addition to the count (rate)
2. Quantile information is of interest.

The key property of a measure metric event is that computing quantiles and/or summarizing a distribution (e.g., via a histogram) may be expensive.  Not only will implementations have various capabilities and algorithms for this task, users may wish to control the quality and cost of aggregating measure metrics.

Like cumulative metrics, non-negative measures are an important case because they support rate calculations.  Measure metrics are described as `Absolute(true)` when the inputs are non-negative.  As an option, measure metrics may be declared as `Absolute(false)` to support positive and negative values.  The SDK should reject negative measurements for Absolute measures, but it is not required to.

### Option to disable metrics by default

Metric instruments are enabled by default, meaning that SDKs will export metric data for this instrument without configuration.  Metric instruments support a `Disabled` option, marking them as verbose sources of information that may be configured on an as-needed basis to control cost (e.g., using a "views" API).

### Kind-specific option summary

The kind-specific optional properties of a metric instrument are:

| Property | Description | Metric kind |
| -------- | ----------- | ----------- |
| Monotonic(true) | Indicates a cumulative that accepts only non-negative values | Cumulative (default) |
| | Indicate a gauge supports ascending value sequences starting at 0 | Gauge |
| Monotonic(false) | Indicates a cumulative that accepts positive and negative values | Cumulative |
| | Indicate a gauge that expresses a monotonic cumulative value | Gauge (default) |
| Absolute(true) | Indicates a measure that accepts non-negative values | Measure (default) |
| Absolute(false) | Indicates a measure that accepts positive and negative values | Measure |

### RecordBatch API

Applications sometimes want to act upon multiple metric instruments in a single API call, either because the values are inter-related to each other, or because it lowers overhead.  RecordBatch logically updates each instrument in the batch using the supplied value.  A single label set applies to the batch.

A single measurement is defined as:

- Instrument: the measure instrument (not a Handle)
- Value: the recorded floating point or integer data

The batch measurement API uses a language-specific method name (e.g., `RecordBatch`).  The entire batch of measurements takes place within a (implicit or explicit) context.

## Prior art and alternatives

Prometheus supports the notion of vector metrics, which are those that support pre-defined labels for a specific set of required keys.  The vector-metric API supports a variety of methods like `WithLabelValues` to associate labels with a metric handle, similar to `GetHandle` in OpenTelemetry.  As in this proposal, Prometheus supports a vector API for all metric types.

## Open questions

### `GetHandle` argument ordering

Argument ordering has been proposed as the way to pass pre-defined label values in `GetHandle`.  The argument list must match the parameter list exactly, and if it doesn't we generally find out at runtime or not at all.  This model has more optimization potential, but is easier to misuse than the alternative.  The alternative approach is to always pass label:value pairs to `GetOrCreateTimeseries`, as opposed to an ordered list of values.

### `RecordBatch` argument ordering

The discussion above can be had for the proposed `RecordBatch` method.  It can be declared with an ordered list of metrics, then the `Record` API takes only an ordered list of numbers.  Alternatively, and less prone to misuse, the `RecordBatch` API has been declared with a list of metric:number pairs.

### Eliminate `GetDefaultHandle()`

Instead of a mechanism to obtain a default handle, some languages may prefer to simply operate on the metric instrument directly in this case.  Should OpenTelemetry eliminate `GetDefaultHandle` and instead specify that cumulative, gauge, and measure metric instruments implement `Add()`, `Set()`, and `Record()` with the same interpretation?

If we eliminate `GetDefaultHandle()`, the SDK may keep a map of metric instrument to default handle on its own.

### `RecordBatch` support for all metrics

In the 8/21 working session, we agreed to limit `RecordBatch` to recording of simultaneous measure metrics, meaning to exclude cumulatives and gauges from batch recording.  There are arguments in favor of supporting batch recording for all metric instruments.

- If atomicity (i.e., the all-or-none property) is the reason for batch reporting, it makes sense to include all the metric instruments in the API
- `RecordBatch` support for cumulatives and gauges will be natural for SDKs that act as forwarders for metric events . The natural implementation for `Add()` and `Set()` methods will be `RecordBatch` with a single event.
- Likewise, it is simple for an SDK that acts as an aggregator (not a forwarder) to redirect `Add()` and `Set()` APIs to the handle-specific `Add()` and `Set()` methods; while the SDK, as the implementation, still may (not must) treat these cumulative and gauge updates as atomic.

Arguments against batch recording for all metric instruments:

- The `Record` in `RecordBatch` suggests it is to be applied to measure metrics.  This is due to measure metrics being the most general-purpose of metric instruments.

## Issues addressed

[Raw vs. other metrics / measurements are unclear](https://github.com/open-telemetry/opentelemetry-specification/issues/83)

[Eliminate Measurement class to save on allocations](https://github.com/open-telemetry/opentelemetry-specification/issues/145)

[Implement three more types of Metric](https://github.com/open-telemetry/opentelemetry-specification/issues/146)
