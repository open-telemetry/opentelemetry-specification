<!--- Hugo front matter used to generate the website version of this page:
linkTitle: SDK
--->

# Metrics SDK

**Status**: [Mixed](../document-status.md)

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [MeterProvider](#meterprovider)
  * [Meter Creation](#meter-creation)
  * [Shutdown](#shutdown)
  * [ForceFlush](#forceflush)
  * [View](#view)
  * [Aggregation](#aggregation)
    + [Drop Aggregation](#drop-aggregation)
    + [Default Aggregation](#default-aggregation)
    + [Sum Aggregation](#sum-aggregation)
    + [Last Value Aggregation](#last-value-aggregation)
    + [Histogram Aggregations](#histogram-aggregations)
      - [Explicit Bucket Histogram Aggregation](#explicit-bucket-histogram-aggregation)
      - [Exponential Bucket Histogram Aggregation](#exponential-bucket-histogram-aggregation)
        * [Handle all normal values](#handle-all-normal-values)
        * [Support a minimum and maximum scale](#support-a-minimum-and-maximum-scale)
        * [Use the maximum scale for single measurements](#use-the-maximum-scale-for-single-measurements)
        * [Maintain the ideal scale](#maintain-the-ideal-scale)
  * [Observations inside asynchronous callbacks](#observations-inside-asynchronous-callbacks)
  * [Resolving duplicate instrument registration conflicts](#resolving-duplicate-instrument-registration-conflicts)
- [Attribute limits](#attribute-limits)
- [Exemplar](#exemplar)
  * [ExemplarFilter](#exemplarfilter)
  * [ExemplarReservoir](#exemplarreservoir)
  * [Exemplar defaults](#exemplar-defaults)
- [MetricReader](#metricreader)
  * [MetricReader operations](#metricreader-operations)
    + [Collect](#collect)
    + [Shutdown](#shutdown-1)
  * [Periodic exporting MetricReader](#periodic-exporting-metricreader)
- [MetricExporter](#metricexporter)
  * [Push Metric Exporter](#push-metric-exporter)
    + [Interface Definition](#interface-definition)
      - [Export(batch)](#exportbatch)
      - [ForceFlush()](#forceflush)
      - [Shutdown()](#shutdown)
  * [Pull Metric Exporter](#pull-metric-exporter)
- [Defaults and configuration](#defaults-and-configuration)
- [Numerical limits handling](#numerical-limits-handling)
- [Compatibility requirements](#compatibility-requirements)
- [Concurrency requirements](#concurrency-requirements)

<!-- tocstop -->

</details>

## MeterProvider

**Status**: [Stable](../document-status.md)

A `MeterProvider` MUST provide a way to allow a [Resource](../resource/sdk.md) to
be specified. If a `Resource` is specified, it SHOULD be associated with all the
metrics produced by any `Meter` from the `MeterProvider`. The [tracing SDK
specification](../trace/sdk.md#additional-span-interfaces) has provided some
suggestions regarding how to implement this efficiently.

### Meter Creation

New `Meter` instances are always created through a `MeterProvider` (see
[API](./api.md#meterprovider)). The `name`, `version` (optional), and
`schema_url` (optional) arguments supplied to the `MeterProvider` MUST be used
to create an [`InstrumentationScope`](../glossary.md#instrumentation-scope)
instance which is stored on the created `Meter`.

Configuration (i.e., [MetricExporters](#metricexporter),
[MetricReaders](#metricreader) and [Views](#view)) MUST be managed solely by the
`MeterProvider` and the SDK MUST provide a way to configure all options that are
implemented by the SDK. This MAY be done at the time of MeterProvider creation
if appropriate.

The `MeterProvider` MAY provide methods to update the configuration. If
configuration is updated (e.g., adding a `MetricReader`), the updated
configuration MUST also apply to all already returned `Meters` (i.e. it MUST NOT
matter whether a `Meter` was obtained from the `MeterProvider` before or after
the configuration change). Note: Implementation-wise, this could mean that
`Meter` instances have a reference to their `MeterProvider` and access
configuration only via this reference.

### Shutdown

This method provides a way for provider to do any cleanup required.

`Shutdown` MUST be called only once for each `MeterProvider` instance. After the
call to `Shutdown`, subsequent attempts to get a `Meter` are not allowed. SDKs
SHOULD return a valid no-op Meter for these calls, if possible.

`Shutdown` SHOULD provide a way to let the caller know whether it succeeded,
failed or timed out.

`Shutdown` SHOULD complete or abort within some timeout. `Shutdown` MAY be
implemented as a blocking API or an asynchronous API which notifies the caller
via a callback or an event. [OpenTelemetry SDK](../overview.md#sdk) authors MAY
decide if they want to make the shutdown timeout configurable.

`Shutdown` MUST be implemented at least by invoking `Shutdown` on all registered
[MetricReader](#metricreader) and [MetricExporter](#metricexporter) instances.

### ForceFlush

This method provides a way for provider to notify the registered
[MetricReader](#metricreader) and [MetricExporter](#metricexporter) instances,
so they can do as much as they could to consume or send the metrics. Note:
unlike [Push Metric Exporter](#push-metric-exporter) which can send data on its
own schedule, [Pull Metric Exporter](#pull-metric-exporter) can only send the
data when it is being asked by the scraper, so `ForceFlush` would not make much
sense.

`ForceFlush` SHOULD provide a way to let the caller know whether it succeeded,
failed or timed out. `ForceFlush` SHOULD return some **ERROR** status if there
is an error condition; and if there is no error condition, it should return some
**NO ERROR** status, language implementations MAY decide how to model **ERROR**
and **NO ERROR**.

`ForceFlush` SHOULD complete or abort within some timeout. `ForceFlush` MAY be
implemented as a blocking API or an asynchronous API which notifies the caller
via a callback or an event. [OpenTelemetry SDK](../overview.md#sdk) authors MAY
decide if they want to make the flush timeout configurable.

`ForceFlush` MUST invoke `ForceFlush` on all registered
[MetricReader](#metricreader) and [Push Metric Exporter](#push-metric-exporter)
instances.

### View

A `View` provides SDK users with the flexibility to customize the metrics that
are output by the SDK. Here are some examples when a `View` might be needed:

* Customize which [Instruments](./api.md#instrument) are to be
  processed/ignored. For example, an [instrumented
  library](../glossary.md#instrumented-library) can provide both temperature and
  humidity, but the application developer might only want temperature.
* Customize the aggregation - if the default aggregation associated with the
  Instrument does not meet the needs of the user. For example, an HTTP client
  library might expose HTTP client request duration as
  [Histogram](./api.md#histogram) by default, but the application developer
  might only want the total count of outgoing requests.
* Customize which attribute(s) are to be reported on metrics. For
  example, an HTTP server library might expose HTTP verb (e.g. GET, POST) and
  HTTP status code (e.g. 200, 301, 404). The application developer might only
  care about HTTP status code (e.g. reporting the total count of HTTP requests
  for each HTTP status code). There could also be extreme scenarios in which the
  application developer does not need any attributes (e.g. just get the total
  count of all incoming requests).

The SDK MUST provide the means to register Views with a `MeterProvider`. Here
are the inputs:

* The Instrument selection criteria (required), which covers:
  * The `type` of the Instrument(s) (optional).
  * The `name` of the Instrument(s). [OpenTelemetry SDK](../overview.md#sdk)
    authors MAY choose to support wildcard characters, with the question mark
    (`?`) matching exactly one character and the asterisk character (`*`)
    matching zero or more characters.  If wildcards are not supported in general,
    OpenTelemetry SDKs MUST specifically recognize the single `*` wildcard
    as matching all instruments.
  * The `name` of the Meter (optional).
  * The `version` of the Meter (optional).
  * The `schema_url` of the Meter (optional).
  * [OpenTelemetry SDK](../overview.md#sdk) authors MAY choose to support more
    criteria. For example, a strong typed language MAY support point type (e.g.
    allow the users to select Instruments based on whether the underlying type
    is integer or double).
  * The criteria SHOULD be treated as additive, which means the Instrument has
    to meet _all_ the provided criteria. For example, if the criteria are
    _instrument name == "Foobar"_ and _instrument type is Histogram_, it will be
    treated as _(instrument name == "Foobar") AND (instrument type is
    Histogram)_.
  * If no criteria is provided, the SDK SHOULD treat it as an error. It is
    recommended that the SDK implementations fail fast. Please refer to [Error
    handling in OpenTelemetry](../error-handling.md) for the general guidance.
* The `name` of the View (optional). If not provided, the Instrument `name`
  MUST be used by default. This will be used as the name of the [metrics
  stream](./data-model.md#events--data-stream--timeseries).
* The configuration for the resulting [metrics
  stream](./data-model.md#events--data-stream--timeseries):
  * The `description`. If not provided, the Instrument `description` MUST be
    used by default.
  * A list of `attribute keys` (optional). If provided, the attributes that are
    not in the list will be ignored. If not provided, all the attribute keys
    will be used by default (TODO: once the Hint API is available, the default
    behavior should respect the Hint if it is available).
  * The `aggregation` (optional) to be used. If not provided, the SDK MUST
    apply a [default aggregation](#default-aggregation) configurable on the
    basis of instrument kind according to the [MetricReader](#metricreader)
    instance.
  * **Status**: [Feature-freeze](../document-status.md) - the
    `exemplar_reservoir` (optional) to use for storing exemplars. This should be
    a factory or callback similar to aggregation which allows different
    reservoirs to be chosen by the aggregation.

In order to avoid conflicts, views which specify a name SHOULD have an
instrument selector that selects at most one instrument. For the registration
mechanism described above, where selection is provided via configuration, the
SDK SHOULD NOT allow Views with a specified name to be declared with instrument
selectors that may select more than one instrument (e.g. wild card instrument
name) in the same Meter. For this and other cases where registering a view will
cause a conflict, SDKs MAY fail fast in accordance with
initialization [error handling principles](../error-handling.md#basic-error-handling-principles).

The SDK SHOULD use the following logic to determine how to process Measurements
made with an Instrument:

* Determine the `MeterProvider` which "owns" the Instrument.
* If the `MeterProvider` has no `View` registered, take the Instrument
    and apply the default Aggregation on the basis of instrument kind
    according to the [MetricReader](#metricreader) instance's
    `aggregation` property.
* If the `MeterProvider` has one or more `View`(s) registered:
  * For each View, if the Instrument could match the instrument selection
    criteria:
    * Try to apply the View configuration. If applying the View results
      in [conflicting metric identities](./data-model.md#opentelemetry-protocol-data-model-producer-recommendations)
      the implementation SHOULD apply the View and emit a warning. If it is not
      possible to apply the View without producing semantic errors (e.g. the
      View sets an asynchronous instrument to use
      the [Explicit bucket histogram aggregation](#explicit-bucket-histogram-aggregation))
      the implementation SHOULD emit a warning and proceed as if the View did
      not exist.
  * If the Instrument could not match with any of the registered `View`(s), the
    SDK SHOULD enable the instrument using the default aggregation and temporality.
    Users can configure match-all Views using [Drop aggregation](#drop-aggregation)
    to disable instruments by default.

Here are some examples:

```python
# Python
'''
+------------------+
| MeterProvider    |
|   Meter A        |
|     Counter X    |
|     Histogram Y  |
|   Meter B        |
|     Gauge Z      |
+------------------+
'''

# metrics from X and Y (reported as Foo and Bar) will be exported
meter_provider
    .add_view("X")
    .add_view("Foo", instrument_name="Y")
    .add_view(
        "Bar",
        instrument_name="Y",
        aggregation=HistogramAggregation(buckets=[5.0, 10.0, 25.0, 50.0, 100.0]))
    .add_metric_reader(PeriodicExportingMetricReader(ConsoleExporter()))
```

```python
# all the metrics will be exported using the default configuration
meter_provider.add_metric_reader(PeriodicExportingMetricReader(ConsoleExporter()))
```

```python
# all the metrics will be exported using the default configuration
meter_provider
    .add_view("*") # a wildcard view that matches everything
    .add_metric_reader(PeriodicExportingMetricReader(ConsoleExporter()))
```

```python
# Counter X will be exported as cumulative sum
meter_provider
    .add_view("X", aggregation=SumAggregation())
    .add_metric_reader(PeriodicExportingMetricReader(ConsoleExporter()))
```

```python
# Counter X will be exported as delta sum
# Histogram Y and Gauge Z will be exported with 2 attributes (a and b)
meter_provider
    .add_view("X", aggregation=SumAggregation())
    .add_view("*", attribute_keys=["a", "b"])
    .add_metric_reader(PeriodicExportingMetricReader(ConsoleExporter()),
              temporality=lambda kind: Delta if kind in [Counter, AsyncCounter, Histogram] else Cumulative)
```

### Aggregation

An `Aggregation`, as configured via the [View](./sdk.md#view),
informs the SDK on the ways and means to compute
[Aggregated Metrics](./data-model.md#opentelemetry-protocol-data-model)
from incoming Instrument [Measurements](./api.md#measurement).

Note: the term _aggregation_ is used instead of _aggregator_. It is recommended
that implementors reserve the "aggregator" term for the future when the SDK
allows custom aggregation implementations.

An `Aggregation` specifies an operation
(i.e. [decomposable aggregate function](https://en.wikipedia.org/wiki/Aggregate_function#Decomposable_aggregate_functions)
like Sum, Histogram, Min, Max, Count)
and optional configuration parameter overrides.
The operation's default configuration parameter values will be used
unless overridden by optional configuration parameter overrides.

Note: Implementors MAY choose the best idiomatic practice for their language to
represent the semantic of an Aggregation and optional configuration parameters.

e.g. The View specifies an Aggregation by string name (i.e. "ExplicitBucketHistogram").

```python
# Use Histogram with custom boundaries
meter_provider
  .add_view(
    "X",
    aggregation="ExplicitBucketHistogram",
    aggregation_params={"Boundaries": [0, 10, 100]}
    )
```

e.g. The View specifies an Aggregation by class/type instance.

```c#
// Use Histogram with custom boundaries
meterProviderBuilder
  .AddView(
    instrumentName: "X",
    aggregation: new ExplicitBucketHistogramAggregation(
      boundaries: new double[] { 0.0, 10.0, 100.0 }
    )
  );
```

TODO: after we release the initial Stable version of Metrics SDK specification,
we will explore how to allow configuring custom
[ExemplarReservoir](#exemplarreservoir)s with the [View](#view) API.

The SDK MUST provide the following `Aggregation` to support the
[Metric Points](./data-model.md#metric-points) in the
[Metrics Data Model](./data-model.md).

- [Drop](./sdk.md#drop-aggregation)
- [Default](./sdk.md#default-aggregation)
- [Sum](./sdk.md#sum-aggregation)
- [Last Value](./sdk.md#last-value-aggregation)
- [Explicit Bucket Histogram](./sdk.md#explicit-bucket-histogram-aggregation)

The SDK MAY provide the following `Aggregation`:

- [Exponential Bucket Histogram Aggregation](./sdk.md#exponential-bucket-histogram-aggregation)

#### Drop Aggregation

The Drop Aggregation informs the SDK to ignore/drop all Instrument Measurements
for this Aggregation.

This Aggregation does not have any configuration parameters.

#### Default Aggregation

The Default Aggregation informs the SDK to use the Instrument Kind
(e.g. at View registration OR at first seen measurement)
to select an aggregation and configuration parameters.

| Instrument Kind | Selected Aggregation                                                                    |
| --- |-----------------------------------------------------------------------------------------|
| [Counter](./api.md#counter) | [Sum Aggregation](./sdk.md#sum-aggregation)                                             |
| [Asynchronous Counter](./api.md#asynchronous-counter) | [Sum Aggregation](./sdk.md#sum-aggregation)                                             |
| [UpDownCounter](./api.md#updowncounter) | [Sum Aggregation](./sdk.md#sum-aggregation)                                             |
| [Asynchronous UpDownCounter](./api.md#asynchronous-updowncounter) | [Sum Aggregation](./sdk.md#sum-aggregation)                                             |
| [Asynchronous Gauge](./api.md#asynchronous-gauge) | [Last Value Aggregation](./sdk.md#last-value-aggregation)                               |
| [Histogram](./api.md#histogram) | [Explicit Bucket Histogram Aggregation](./sdk.md#explicit-bucket-histogram-aggregation) |

This Aggregation does not have any configuration parameters.

#### Sum Aggregation

The Sum Aggregation informs the SDK to collect data for the
[Sum Metric Point](./data-model.md#sums).

The monotonicity of the aggregation is determined by the instrument type:

| Instrument Kind | `SumType` |
| --- | --- |
| [Counter](./api.md#counter) | Monotonic |
| [UpDownCounter](./api.md#updowncounter) | Non-Monotonic |
| [Histogram](./api.md#histogram) | Monotonic |
| [Asynchronous Gauge](./api.md#asynchronous-gauge) | Non-Monotonic |
| [Asynchronous Counter](./api.md#asynchronous-counter) | Monotonic |
| [Asynchronous UpDownCounter](./api.md#asynchronous-updowncounter) | Non-Monotonic |

This Aggregation does not have any configuration parameters.

This Aggregation informs the SDK to collect:

- The arithmetic sum of `Measurement` values.

#### Last Value Aggregation

The Last Value Aggregation informs the SDK to collect data for the
[Gauge Metric Point](./data-model.md#gauge).

This Aggregation does not have any configuration parameters.

This Aggregation informs the SDK to collect:

- The last `Measurement`.
- The timestamp of the last `Measurement`.

#### Histogram Aggregations

All histogram Aggregations inform the SDK to collect:

- Count of `Measurement` values in population.
- Arithmetic sum of `Measurement` values in population. This SHOULD NOT be collected when used with
instruments that record negative measurements (e.g. `UpDownCounter` or `ObservableGauge`).
- Min (optional) `Measurement` value in population.
- Max (optional) `Measurement` value in population.

##### Explicit Bucket Histogram Aggregation

The Explicit Bucket Histogram Aggregation informs the SDK to collect data for
the [Histogram Metric Point](./data-model.md#histogram) using a set of
explicit boundary values for histogram bucketing.

This Aggregation honors the following configuration parameters:

| Key | Value | Default Value | Description |
| --- | --- | --- | --- |
| Boundaries | double\[\] | [ 0, 5, 10, 25, 50, 75, 100, 250, 500, 1000 ] | Array of increasing values representing explicit bucket boundary values.<br><br>The Default Value represents the following buckets:<br>(-&infin;, 0], (0, 5.0], (5.0, 10.0], (10.0, 25.0], (25.0, 50.0], (50.0, 75.0], (75.0, 100.0], (100.0, 250.0], (250.0, 500.0], (500.0, 1000.0], (1000.0, +&infin;) |
| RecordMinMax | true, false | true | Whether to record min and max. |

Explicit buckets are stated in terms of their upper boundary.  Buckets
are exclusive of their lower boundary and inclusive of their upper
bound (except at positive infinity).  A measurement is defined to fall
into the greatest-numbered bucket with boundary that is greater than
or equal to the measurement.

##### Exponential Bucket Histogram Aggregation

The Exponential Histogram Aggregation informs the SDK to collect data
for the [Exponential Histogram Metric
Point](./data-model.md#exponentialhistogram), which uses an exponential
formula to determine bucket boundaries and an integer `scale`
parameter to control resolution.

Scale is not a configurable property of this Aggregation, the
implementation will adjust it as necessary given the data.  This
Aggregation honors the following configuration parameter:

| Key     | Value   | Default Value | Description                                                                                                  |
|---------|---------|---------------|--------------------------------------------------------------------------------------------------------------|
| MaxSize | integer | 160           | Maximum number of buckets in each of the positive and negative ranges, not counting the special zero bucket. |

The default of 160 buckets is selected to establish default support
for a high-resolution histogram able to cover a long-tail latency
distribution from 1ms to 100s with less than 5% relative error.
Because 160 can be factored into `10 * 2**K`, maximum contrast is
relatively simple to derive for scale `K`:

| Scale | Maximum data contrast at 10 * 2**K buckets |
|-------|--------------------------------------------|
| K+2   | 5.657 (2**(10/4))                          |
| K+1   | 32 (2**(10/2))                             |
| K     | 1024 (2**10)                               |
| K-1   | 1048576 (2**20)                            |

The following table shows how the ideal scale for 160 buckets is
calculated as a function of the input range:

| Input range | Contrast | Ideal Scale | Base     | Relative error |
|-------------|----------|-------------|----------|----------------|
| 1ms - 4ms   | 4        | 6           | 1.010889 | 0.542%         |
| 1ms - 20ms  | 20       | 5           | 1.021897 | 1.083%         |
| 1ms - 1s    | 10**3    | 4           | 1.044274 | 2.166%         |
| 1ms - 100s  | 10**5    | 3           | 1.090508 | 4.329%         |
| 1μs - 10s   | 10**7    | 2           | 1.189207 | 8.643%         |

Note that relative error is calculated as half of the bucket width
divided by the bucket midpoint, which is the same in every bucket.
Using the bucket from [1, base), we have `(bucketWidth / 2) /
bucketMidpoint = ((base - 1) / 2) / ((base + 1) / 2) = (base - 1) /
(base + 1)`.

This Aggregation uses the notion of "ideal" scale.  The ideal scale is
either:

1. The maximum supported scale, generally used for single-value histogram Aggregations where scale is not otherwise constrained
2. The largest value of scale such that no more than the maximum number of buckets are needed to represent the full range of input data in either of the positive or negative ranges.

###### Handle all normal values

Implementations are REQUIRED to accept the entire normal range of IEEE
floating point values (i.e., all values except for +Inf, -Inf and NaN
values).

Implementations SHOULD NOT incorporate non-normal values (i.e., +Inf,
-Inf, and NaNs) into the `sum`, `min`, and `max` fields, because these
values do not map into a valid bucket.

Implementations MAY round subnormal values away from zero to the
nearest normal value.

###### Support a minimum and maximum scale

The implementation MUST maintain reasonable minimum and maximum scale
parameters that the automatic scale parameter will not exceed.

###### Use the maximum scale for single measurements

When the histogram contains not more than one value in either of the
positive or negative ranges, the implementation SHOULD use the maximum
scale.

###### Maintain the ideal scale

Implementations SHOULD adjust the histogram scale as necessary to
maintain the best resolution possible, within the constraint of
maximum size (max number of buckets). Best resolution (highest scale)
is achieved when the number of positive or negative range buckets
exceeds half the maximum size, such that increasing scale by one would
not be possible given the size constraint.

### Observations inside asynchronous callbacks

Callback functions MUST be invoked for the specific `MetricReader`
performing collection, such that observations made or produced by
executing callbacks only apply to the intended `MetricReader` during
collection.

The implementation SHOULD disregard the accidental use of APIs
appurtenant to asynchronous instruments outside of registered
callbacks in the context of a single `MetricReader` collection.

The implementation SHOULD use a timeout to prevent indefinite callback
execution.

The implementation MUST complete the execution of all callbacks for a
given instrument before starting a subsequent round of collection.

### Resolving duplicate instrument registration conflicts

As [stated in the API
specification](api.md#instrument-type-conflict-detection),
implementations are REQUIRED to create valid instruments in case of
duplicate instrument registration, and the [data model includes
RECOMMENDATIONS on how to treat the consequent duplicate
conflicting](data-model.md#opentelemetry-protocol-data-model-producer-recommendations)
`Metric` definitions.

The implementation MUST aggregate data from identical Instruments
together in its export pipeline.

The implementation SHOULD assist the user in managing conflicts by
reporting each duplicate-conflicting instrument registration that was
not corrected by a View as follows.  When a potential conflict arises
between two non-identical `Metric` instances having the same `name`:

1. If the potential conflict involves multiple `description`
   properties, setting the `description` through a configured View
   SHOULD avoid the warning.
2. If the potential conflict involves instruments that can be
   distinguished by a supported View selector (e.g., instrument type)
   a View recipe SHOULD be printed advising the user how to avoid the
   warning by renaming one of the conflicting instruments.
3. Otherwise (e.g., use of multiple units), the implementation SHOULD
   pass through the data by reporting both `Metric` objects.

## Attribute limits

**Status**: [Stable](../document-status.md)

Attributes which belong to Metrics are exempt from the
[common rules of attribute limits](../common/README.md#attribute-limits) at this
time. Attribute truncation or deletion could affect identity of metric time
series and the topic requires further analysis.

## Exemplar

**Status**: [Feature-freeze](../document-status.md)

Exemplars are example data points for aggregated data. They provide specific
context to otherwise general aggregations. Exemplars allow correlation between
aggregated metric data and the original API calls where measurements are
recorded. Exemplars work for trace-metric correlation across any metric, not
just those that can also be derived from `Span`s.

An [Exemplar](./data-model.md#exemplars) is a recorded
[Measurement](./api.md#measurement) that exposes the following pieces of
information:

- The `value` of the `Measurement` that was recorded by the API call.
- The `time` the API call was made to record a `Measurement`.
- The set of [Attributes](../common/README.md#attribute) associated with the
  `Measurement` not already included in a metric data point.
- The associated [trace id and span
  id](../trace/api.md#retrieving-the-traceid-and-spanid) of the active [Span
  within Context](../trace/api.md#determining-the-parent-span-from-a-context) of
  the `Measurement` at API call time.

For example, if a user has configured a `View` to preserve the attributes: `X`
and `Y`, but the user records a measurement as follows:

```javascript
const span = tracer.startSpan('makeRequest');
api.context.with(api.trace.setSpan(api.context.active(), span), () => {
  // Record a measurement.
  cache_miss_counter.add(1, {"X": "x-value", "Y": "y-value", "Z": "z-value"});
  ...
  span.end();
})
```

Then an exemplar output in OTLP would consist of:

- The `value` of 1.
- The `time` when the `add` method was called
- The `Attributes` of `{"Z": "z-value"}`, as these are not preserved in the
  resulting metric point.
- The trace/span id for the `makeRequest` span.

While the metric data point for the counter would carry the attributes `X` and
`Y`.

A Metric SDK MUST provide a mechanism to sample `Exemplar`s from measurements
via the `ExemplarFilter` and `ExemplarReservoir` hooks.

`Exemplar` sampling SHOULD be turned off by default. If `Exemplar` sampling is
off, the SDK MUST NOT have overhead related to exemplar sampling.

A Metric SDK MUST allow exemplar sampling to leverage the configuration of
metric aggregation. For example, Exemplar sampling of histograms should be able
to leverage bucket boundaries.

A Metric SDK SHOULD provide extensible hooks for Exemplar sampling, specifically:

- `ExemplarFilter`: filter which measurements can become exemplars.
- `ExemplarReservoir`: storage and sampling of exemplars.

### ExemplarFilter

The `ExemplarFilter` interface MUST provide a method to determine if a
measurement should be sampled.

This interface SHOULD have access to:

- The `value` of the measurement.
- The complete set of `Attributes` of the measurement.
- The [Context](../context/README.md) of the measurement, which covers the
  [Baggage](../baggage/api.md) and the current active
  [Span](../trace/api.md#span).
- A `timestamp` that best represents when the measurement was taken.

See [Defaults and Configuration](#defaults-and-configuration) for built-in
filters.

### ExemplarReservoir

The `ExemplarReservoir` interface MUST provide a method to offer measurements
to the reservoir and another to collect accumulated Exemplars.

The "offer" method SHOULD accept measurements, including:

- The `value` of the measurement.
- The complete set of `Attributes` of the measurement.
- The [Context](../context/README.md) of the measurement, which covers the
  [Baggage](../baggage/api.md) and the current active
  [Span](../trace/api.md#span).
- A `timestamp` that best represents when the measurement was taken.

The "offer" method SHOULD have the ability to pull associated trace and span
information without needing to record full context.  In other words, current
span context and baggage can be inspected at this point.

The "offer" method does not need to store all measurements it is given and
MAY further sample beyond the `ExemplarFilter`.

The "collect" method MUST return accumulated `Exemplar`s. Exemplars are expected
to abide by the `AggregationTemporality` of any metric point they are recorded
with. In other words, Exemplars reported against a metric data point SHOULD have
occurred within the start/stop timestamps of that point.  SDKs are free to
decide whether "collect" should also reset internal storage for delta temporal
aggregation collection, or use a more optimal implementation.

`Exemplar`s MUST retain any attributes available in the measurement that
are not preserved by aggregation or view configuration. Specifically, at a
minimum, joining together attributes on an `Exemplar` with those available
on its associated metric data point should result in the full set of attributes
from the original sample measurement.

The `ExemplarReservoir` SHOULD avoid allocations when sampling exemplars.

### Exemplar defaults

The SDK will come with two types of built-in exemplar reservoirs:

1. SimpleFixedSizeExemplarReservoir
2. AlignedHistogramBucketExemplarReservoir

By default, explicit bucket histogram aggregation with more than 1 bucket will
use `AlignedHistogramBucketExemplarReservoir`. All other aggregations will use
`SimpleFixedSizeExemplarReservoir`.

_SimpleExemplarReservoir_
This Exemplar reservoir MAY take a configuration parameter for the size of the
reservoir pool.  The reservoir will accept measurements using an equivalent of
the [naive reservoir sampling
algorithm](https://en.wikipedia.org/wiki/Reservoir_sampling)

  ```
  bucket = random_integer(0, num_measurements_seen)
  if bucket < num_buckets then
    reservoir[bucket] = measurement
  end
  ```

Additionally, the `num_measurements_seen` count SHOULD be reset at every
collection cycle.

_AlignedHistogramBucketExemplarReservoir_
This Exemplar reservoir MUST take a configuration parameter that is the
configuration of a Histogram.  This implementation MUST keep the last seen
measurement that falls within a histogram bucket.  The reservoir will accept
measurements using the equivalent of the following naive algorithm:

  ```
  bucket = find_histogram_bucket(measurement)
  if bucket < num_buckets then
    reservoir[bucket] = measurement
  end

  def find_histogram_bucket(measurement):
    for boundary, idx in bucket_boundaries do
      if value <= boundary then
        return idx
      end
    end
    return boundaries.length
  ```

## MetricReader

**Status**: [Stable](../document-status.md)

`MetricReader` is an SDK implementation object that provides the
common configurable aspects of the OpenTelemetry Metrics SDK and
determines the following capabilities:

* Collecting metrics from the SDK on demand.
* Handling the [ForceFlush](#forceflush) and [Shutdown](#shutdown) signals from
  the SDK.

To construct a `MetricReader` when setting up an SDK, the caller
SHOULD provide at least the following:

* The `exporter` to use, which is a `MetricExporter` instance.
* The default output `aggregation` (optional), a function of instrument kind.  If not configured, the [default aggregation](#default-aggregation) SHOULD be used.
* The default output `temporality` (optional), a function of instrument kind.  If not configured, the Cumulative temporality SHOULD be used.

The [MetricReader.Collect](#collect) method allows general-purpose
`MetricExporter` instances to explicitly initiate collection, commonly
used with pull-based metrics collection.  A common sub-class of
`MetricReader`, the periodic exporting `MetricReader` SHOULD be provided
to be used typically with push-based metrics collection.

The `MetricReader` MUST ensure that data points are output in the
configured aggregation temporality for each instrument kind.  For
synchronous instruments being output with Cumulative temporality, this
means converting [Delta to Cumulative](supplementary-guidelines.md#synchronous-example-cumulative-aggregation-temporality)
aggregation temporality.  For asynchronous instruments being output
with Delta temporality, this means converting [Cumulative to
Delta](supplementary-guidelines.md#asynchronous-example-delta-temporality) aggregation
temporality.

The SDK MUST support multiple `MetricReader` instances to be registered on the
same `MeterProvider`, and the [MetricReader.Collect](#collect) invocation on one
`MetricReader` instance SHOULD NOT introduce side-effects to other `MetricReader`
instances. For example, if a `MetricReader` instance is receiving metric data
points that have [delta temporality](./data-model.md#temporality), it is expected
that SDK will update the time range - e.g. from (T<sub>n</sub>, T<sub>n+1</sub>]
to (T<sub>n+1</sub>, T<sub>n+2</sub>] - **ONLY** for this particular
`MetricReader` instance.

The SDK MUST NOT allow a `MetricReader` instance to be registered on more than
one `MeterProvider` instance.

```text
+-----------------+            +--------------+
|                 | Metrics... |              |
| In-memory state +------------> MetricReader |
|                 |            |              |
+-----------------+            +--------------+

+-----------------+            +--------------+
|                 | Metrics... |              |
| In-memory state +------------> MetricReader |
|                 |            |              |
+-----------------+            +--------------+
```

The SDK SHOULD provide a way to allow `MetricReader` to respond to
[MeterProvider.ForceFlush](#forceflush) and [MeterProvider.Shutdown](#shutdown).
[OpenTelemetry SDK](../overview.md#sdk) authors MAY decide the language
idiomatic approach, for example, as `OnForceFlush` and `OnShutdown` callback
functions.

### MetricReader operations

#### Collect

Collects the metrics from the SDK. If there are [asynchronous
Instruments](./api.md#asynchronous-instrument-api) involved, their callback
functions will be triggered.

`Collect` SHOULD provide a way to let the caller know whether it succeeded,
failed or timed out. When the `Collect` operation fails or times out on
some of the instruments, the SDK MAY return successfully collected results
and a failed reasons list to the caller.

`Collect` does not have any required parameters, however, [OpenTelemetry
SDK](../overview.md#sdk) authors MAY choose to add parameters (e.g. callback,
filter, timeout). [OpenTelemetry SDK](../overview.md#sdk) authors MAY choose the
return value type, or do not return anything.

Note: it is expected that the `MetricReader.Collect` implementations will be
provided by the SDK, so it is RECOMMENDED to prevent the user from accidentally
overriding it, if possible (e.g. `final` in C++ and Java, `sealed` in C#).

#### Shutdown

This method provides a way for the `MetricReader` to do any cleanup required.

`Shutdown` MUST be called only once for each `MetricReader` instance. After the
call to `Shutdown`, subsequent invocations to `Collect` are not allowed. SDKs
SHOULD return some failure for these calls, if possible.

`Shutdown` SHOULD provide a way to let the caller know whether it succeeded,
failed or timed out.

`Shutdown` SHOULD complete or abort within some timeout. `Shutdown` MAY be
implemented as a blocking API or an asynchronous API which notifies the caller
via a callback or an event. [OpenTelemetry SDK](../overview.md#sdk) authors MAY
decide if they want to make the shutdown timeout configurable.

### Periodic exporting MetricReader

This is an implementation of the `MetricReader` which collects metrics based on
a user-configurable time interval, and passes the metrics to the configured
[Push Metric Exporter](#push-metric-exporter).

Configurable parameters:

* `exportIntervalMillis` - the time interval in milliseconds between two
  consecutive exports. The default value is 60000 (milliseconds).
* `exportTimeoutMillis` - how long the export can run before it is cancelled.
  The default value is 30000 (milliseconds).

One possible implementation of periodic exporting MetricReader is to inherit
from `MetricReader` and start a background task which calls the inherited
`Collect()` method at the requested `exportIntervalMillis`. The reader's
`Collect()` method may still be invoked by other callers. For example,

* A user configures periodic exporting MetricReader with a push exporter and a
  30 second interval.
* At the first 30 second interval, the background task calls `Collect()` which
  passes metrics to the push exporter.
* After 15 seconds, the user decides to flush metrics for just this reader. They
  call `Collect()` which passes metrics to the push exporter.
* After another 15 seconds (at the end of the second 30 second interval),
  the background task calls `Collect()` which passes metrics to the push
  exporter.

## MetricExporter

**Status**: [Stable](../document-status.md)

`MetricExporter` defines the interface that protocol-specific exporters MUST
implement so that they can be plugged into OpenTelemetry SDK and support sending
of telemetry data.

Metric Exporters always have an _associated_ MetricReader.  The
`aggregation` and `temporality` properties used by the
OpenTelemetry Metric SDK are determined when registering Metric
Exporters through their associated MetricReader.  OpenTelemetry
language implementations MAY support automatically configuring the
[MetricReader](#metricreader) to use for an Exporter.

The goal of the interface is to minimize burden of implementation for
protocol-dependent telemetry exporters. The protocol exporter is expected to be
primarily a simple telemetry data encoder and transmitter.

Metric Exporter has access to the [aggregated metrics
data](./data-model.md#timeseries-model).  Metric Exporters SHOULD
report an error condition for data output by the `MetricReader` with
unsupported Aggregation or Aggregation Temporality, as this condition
can be corrected by a change of `MetricReader` configuration.

There could be multiple [Push Metric Exporters](#push-metric-exporter) or [Pull
Metric Exporters](#pull-metric-exporter) or even a mixture of both configured at
the same time on a given `MeterProvider` using one `MetricReader` for each exporter. Different exporters
can run at different schedule, for example:

* Exporter A is a push exporter which sends data every 1 minute.
* Exporter B is a push exporter which sends data every 5 seconds.
* Exporter C is a pull exporter which reacts to a scraper over HTTP.
* Exporter D is a pull exporter which reacts to another scraper over a named
  pipe.

### Push Metric Exporter

Push Metric Exporter sends metric data it receives from a paired
[MetricReader](#metricreader). Here are some examples:

* Sends the data based on a user configured schedule, e.g. every 1 minute.
  This MAY be accomplished by pairing the exporter with a
  [periodic exporting MetricReader](#periodic-exporting-metricreader).
* Sends the data when there is a severe error.

The following diagram shows `Push Metric Exporter`'s relationship to other
components in the SDK:

```text
+-----------------+            +---------------------------------+
|                 | Metrics... |                                 |
| In-memory state +------------> Periodic exporting MetricReader |
|                 |            |                                 |
+-----------------+            |    +-----------------------+    |
                               |    |                       |    |
                               |    | MetricExporter (push) +-------> Another process
                               |    |                       |    |
                               |    +-----------------------+    |
                               |                                 |
                               +---------------------------------+
```

#### Interface Definition

A Push Metric Exporter MUST support the following functions:

##### Export(batch)

Exports a batch of [Metric points](./data-model.md#metric-points). Protocol
exporters that will implement this function are typically expected to serialize
and transmit the data to the destination.

The SDK MUST provide a way for the exporter to get the [Meter](./api.md#meter)
information (e.g. name, version, etc.) associated with each `Metric point`.

`Export` will never be called concurrently for the same exporter instance.
`Export` can be called again only after the current call returns.

`Export` MUST NOT block indefinitely, there MUST be a reasonable upper limit
after which the call must time out with an error result (Failure).

Any retry logic that is required by the exporter is the responsibility of the
exporter. The default SDK SHOULD NOT implement retry logic, as the required
logic is likely to depend heavily on the specific protocol and backend the metrics
are being sent to.

**Parameters:**

`batch` - a batch of `Metric point`s. The exact data type of the batch is
language specific, typically it is some kind of list. The exact type of `Metric
point` is language specific, and is typically optimized for high performance.
Here are some examples:

```text
       +--------+ +--------+     +--------+
Batch: | Metric | | Metric | ... | Metric |
       +---+----+ +--------+     +--------+
           |
           +--> name, unit, description, meter information, ...
           |
           |                  +-------------+ +-------------+     +-------------+
           +--> MetricPoints: | MetricPoint | | MetricPoint | ... | MetricPoint |
                              +-----+-------+ +-------------+     +-------------+
                                    |
                                    +--> timestamps, attributes, value (or buckets), exemplars, ...
```

Refer to the [Metric points](./data-model.md#metric-points) section from the
Metrics Data Model specification for more details.

Note: it is highly recommended that implementors design the `Metric` data type
_based on_ the [Data Model](./data-model.md), rather than directly use the data
types generated from the [proto
files](https://github.com/open-telemetry/opentelemetry-proto/blob/main/opentelemetry/proto/metrics/v1/metrics.proto)
(because the types generated from proto files are not guaranteed to be backward
compatible).

Returns: `ExportResult`

`ExportResult` is one of:

* `Success` - The batch has been successfully exported. For protocol exporters
  this typically means that the data is sent over the wire and delivered to the
  destination server.
* `Failure` - exporting failed. The batch must be dropped. For example, this can
  happen when the batch contains bad data and cannot be serialized.

Note: this result may be returned via an async mechanism or a callback, if that
is idiomatic for the language implementation.

##### ForceFlush()

This is a hint to ensure that the export of any `Metrics` the exporter has
received prior to the call to `ForceFlush` SHOULD be completed as soon as
possible, preferably before returning from this method.

`ForceFlush` SHOULD provide a way to let the caller know whether it succeeded,
failed or timed out.

`ForceFlush` SHOULD only be called in cases where it is absolutely necessary,
such as when using some FaaS providers that may suspend the process after an
invocation, but before the exporter exports the completed metrics.

`ForceFlush` SHOULD complete or abort within some timeout. `ForceFlush` can be
implemented as a blocking API or an asynchronous API which notifies the caller
via a callback or an event. [OpenTelemetry SDK](../overview.md#sdk) authors MAY
decide if they want to make the flush timeout configurable.

##### Shutdown()

Shuts down the exporter. Called when SDK is shut down. This is an opportunity
for exporter to do any cleanup required.

Shutdown SHOULD be called only once for each `MetricExporter` instance. After
the call to `Shutdown` subsequent calls to `Export` are not allowed and should
return a Failure result.

`Shutdown` SHOULD NOT block indefinitely (e.g. if it attempts to flush the data
and the destination is unavailable). [OpenTelemetry SDK](../overview.md#sdk)
authors MAY decide if they want to make the shutdown timeout configurable.

### Pull Metric Exporter

Pull Metric Exporter reacts to the metrics scrapers and reports the data
passively. This pattern has been widely adopted by
[Prometheus](https://prometheus.io/).

Unlike [Push Metric Exporter](#push-metric-exporter) which can send data on its
own schedule, pull exporter can only send the data when it is being asked by the
scraper, and `ForceFlush` would not make sense.

Implementors MAY choose the best idiomatic design for their language. For
example, they could generalize the [Push Metric Exporter
interface](#push-metric-exporter) design and use that for consistency, they
could model the pull exporter as [MetricReader](#metricreader), or they could
design a completely different pull exporter interface. If the pull exporter is
modeled as MetricReader, implementors MAY name the MetricExporter interface as
PushMetricExporter to prevent naming confusion.

The following diagram gives some examples on how `Pull Metric Exporter` can be
modeled to interact with other components in the SDK:

* Model the pull exporter as MetricReader

  ```text
  +-----------------+            +-----------------------------+
  |                 | Metrics... |                             |
  | In-memory state +------------> PrometheusExporter (pull)   +---> Another process (scraper)
  |                 |            | (modeled as a MetricReader) |
  +-----------------+            |                             |
                                 +-----------------------------+
  ```

* Use the same MetricExporter design for both push and pull exporters

  ```text
  +-----------------+            +-----------------------------+
  |                 | Metrics... |                             |
  | In-memory state +------------> Exporting MetricReader      |
  |                 |            |                             |
  +-----------------+            |  +-----------------------+  |
                                 |  |                       |  |
                                 |  | MetricExporter (pull) +------> Another process (scraper)
                                 |  |                       |  |
                                 |  +-----------------------+  |
                                 |                             |
                                 +-----------------------------+
  ```

## Defaults and configuration

The SDK MUST provide configuration according to the [SDK environment
variables](../sdk-environment-variables.md) specification.

## Numerical limits handling

The SDK MUST handle numerical limits in a graceful way according to [Error
handling in OpenTelemetry](../error-handling.md).

If the SDK receives float/double values from [Instruments](./api.md#instrument),
it MUST handle all the possible values. For example, if the language runtime
supports [IEEE 754](https://en.wikipedia.org/wiki/IEEE_754), the SDK needs to
handle NaNs and Infinites.

It is unspecified _how_ the SDK should handle the input limits. The SDK authors
MAY leverage/follow the language runtime behavior for better performance, rather
than perform a check on each value coming from the API.

It is unspecified _how_ the SDK should handle the output limits (e.g. integer
overflow). The SDK authors MAY rely on the language runtime behavior as long as
errors/exceptions are taken care of.

## Compatibility requirements

**Status**: [Stable](../document-status.md)

All the metrics components SHOULD allow new methods to be added to existing
components without introducing breaking changes.

All the metrics SDK methods SHOULD allow optional parameter(s) to be added to
existing methods without introducing breaking changes, if possible.

## Concurrency requirements

**Status**: [Stable](../document-status.md)

For languages which support concurrent execution the Metrics SDKs provide
specific guarantees and safeties.

**MeterProvider** - Meter creation, `ForceFlush` and `Shutdown` are safe to be
called concurrently.

**ExemplarFilter** - all methods are safe to be called concurrently.

**ExemplarReservoir** - all methods are safe to be called concurrently.

**MetricReader** - `Collect` and `Shutdown` are safe to be called concurrently.

**MetricExporter** - `ForceFlush` and `Shutdown` are safe to be called
concurrently.
