# Metrics SDK

**Status**: [Feature-freeze](../document-status.md)

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
    + [Histogram Aggregation](#histogram-aggregation)
    + [Explicit Bucket Histogram Aggregation](#explicit-bucket-histogram-aggregation)
- [Attribute limits](#attribute-limits)
- [Exemplar](#exemplar)
  * [ExemplarFilter](#exemplarfilter)
  * [ExemplarReservoir](#exemplarreservoir)
  * [Exemplar defaults](#exemplar-defaults)
- [MetricReader](#metricreader)
  * [MetricReader operations](#metricreader-operations)
    + [Collect](#collect)
  * [Shutdown](#shutdown-1)
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

A `MeterProvider` MUST provide a way to allow a [Resource](../resource/sdk.md) to
be specified. If a `Resource` is specified, it SHOULD be associated with all the
metrics produced by any `Meter` from the `MeterProvider`. The [tracing SDK
specification](../trace/sdk.md#additional-span-interfaces) has provided some
suggestions regarding how to implement this efficiently.

### Meter Creation

New `Meter` instances are always created through a `MeterProvider` (see
[API](./api.md#meterprovider)). The `name`, `version` (optional), and
`schema_url` (optional) arguments supplied to the `MeterProvider` MUST be used
to create an
[`InstrumentationLibrary`](https://github.com/open-telemetry/oteps/blob/main/text/0083-component.md)
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
* Customize which attribute(s) are to be reported as metrics dimension(s). For
  example, an HTTP server library might expose HTTP verb (e.g. GET, POST) and
  HTTP status code (e.g. 200, 301, 404). The application developer might only
  care about HTTP status code (e.g. reporting the total count of HTTP requests
  for each HTTP status code). There could also be extreme scenarios in which the
  application developer does not need any dimension (e.g. just get the total
  count of all incoming requests).
* Add additional dimension(s) from the [Context](../context/context.md). For
  example, a [Baggage](../baggage/api.md) value might be available indicating
  whether an HTTP request is coming from a bot/crawler or not. The application
  developer might want this to be converted to a dimension for HTTP server
  metrics (e.g. the request/second from bots vs. real users).

The SDK MUST provide the means to register Views with a `MeterProvider`. Here
are the inputs:

* The Instrument selection criteria (required), which covers:
  * The `type` of the Instrument(s) (optional).
  * The `name` of the Instrument(s), with wildcard support (optional).
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
  * If _none_ the optional criteria is provided, the SDK SHOULD treat it as an
    error. It is recommended that the SDK implementations fail fast. Please
    refer to [Error handling in OpenTelemetry](../error-handling.md) for the
    general guidance.
* The `name` of the View (optional). If not provided, the Instrument `name`
  MUST be used by default. This will be used as the name of the [metrics
  stream](./datamodel.md#events--data-stream--timeseries).
* The configuration for the resulting [metrics
  stream](./datamodel.md#events--data-stream--timeseries):
  * The `description`. If not provided, the Instrument `description` MUST be
    used by default.
  * A list of `attribute keys` (optional). If provided, the attributes that are
    not in the list will be ignored. If not provided, all the attribute keys
    will be used by default (TODO: once the Hint API is available, the default
    behavior should respect the Hint if it is available).
  * The `extra dimensions` which come from Baggage/Context (optional). If not
    provided, no extra dimension will be used. Please note that this only
    applies to [synchronous Instruments](./api.md#synchronous-instrument).
  * The `aggregation` (optional) to be used. If not provided, the SDK MUST
    apply a [default aggregation](#default-aggregation). If the aggregation
    outputs metric points that use aggregation temporality (e.g. Histogram,
    Sum), the SDK SHOULD handle the aggregation temporality based on the
    temporality of each [MetricReader](#metricreader) instance.
  * The `exemplar_reservoir` (optional) to use for storing exemplars.
    This should be a factory or callback similar to aggregation which allows
    different reservoirs to be chosen by the aggregation.

The SDK SHOULD use the following logic to determine how to process Measurements
made with an Instrument:

* Determine the `MeterProvider` which "owns" the Instrument.
* If the `MeterProvider` has no `View` registered, take the Instrument and apply
    the default configuration.
* If the `MeterProvider` has one or more `View`(s) registered:
  * For each View, if the Instrument could match the instrument selection
    criteria:
    * Try to apply the View configuration. If there is an error (e.g. the View
      asks for extra dimensions from the Baggage, but the Instrument is
      [asynchronous](./api.md#asynchronous-instrument) which doesn't have
      Context) or a conflict (e.g. the View requires to export the metrics using
      a certain name, but the name is already used by another View), provide a
      way to let the user know (e.g. expose [self-diagnostics
      logs](../error-handling.md#self-diagnostics)).
  * If the Instrument could not match with any of the registered `View`(s), the
    SDK SHOULD provide a default behavior. The SDK SHOULD also provide a way for
    the user to turn off the default behavior via MeterProvider (which means the
    Instrument will be ignored when there is no match). Individual
    implementations can decide what the default behavior is, and how to turn the
    default behavior off.
* END.

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
    .add_view("X", aggregation=SumAggregation(CUMULATIVE))
    .add_metric_reader(PeriodicExportingMetricReader(ConsoleExporter()))
```

```python
# Counter X will be exported as delta sum
# Histogram Y and Gauge Z will be exported with 2 dimensions (a and b)
meter_provider
    .add_view("X", aggregation=SumAggregation(DELTA))
    .add_view("*", attribute_keys=["a", "b"])
    .add_metric_reader(PeriodicExportingMetricReader(ConsoleExporter()))
```

### Aggregation

An `Aggregation`, as configured via the [View](./sdk.md#view),
informs the SDK on the ways and means to compute
[Aggregated Metrics](./datamodel.md#opentelemetry-protocol-data-model)
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
[Metric Points](./datamodel.md#metric-points) in the
[Metrics Data Model](./datamodel.md).

- [Drop](./sdk.md#drop-aggregation)
- [Default](./sdk.md#default-aggregation)
- [Sum](./sdk.md#sum-aggregation)
- [Last Value](./sdk.md#last-value-aggregation)
- [Histogram](./sdk.md#histogram-aggregation)
- [Explicit Bucket Histogram](./sdk.md#explicit-bucket-histogram-aggregation)

#### Drop Aggregation

The Drop Aggregation informs the SDK to ignore/drop all Instrument Measurements
for this Aggregation.

This Aggregation does not have any configuration parameters.

#### Default Aggregation

The Default Aggregation informs the SDK to use the Instrument Kind
(e.g. at View registration OR at first seen measurement)
to select an aggregation and configuration parameters.

| Instrument Kind | Selected Aggregation |
| --- | --- |
| [Counter](./api.md#counter) | [Sum Aggregation](./sdk.md#sum-aggregation) |
| [Asynchronous Counter](./api.md#asynchronous-counter) | [Sum Aggregation](./sdk.md#sum-aggregation) |
| [UpDownCounter](./api.md#updowncounter) | [Sum Aggregation](./sdk.md#sum-aggregation) |
| [Asynchrounous UpDownCounter](./api.md#asynchronous-updowncounter) | [Sum Aggregation](./sdk.md#sum-aggregation) |
| [Asynchronous Gauge](./api.md#asynchronous-gauge) | [Last Value Aggregation](./sdk.md#last-value-aggregation) |
| [Histogram](./api.md#histogram) | [Histogram Aggregation](./sdk.md#histogram-aggregation) |

This Aggregation does not have any configuration parameters.

#### Sum Aggregation

The Sum Aggregation informs the SDK to collect data for the
[Sum Metric Point](./datamodel.md#sums).

The monotonicity of the aggregation is determined by the instrument type:

| Instrument Kind | `SumType` |
| --- | --- |
| [Counter](./api.md#counter) | Monotonic |
| [UpDownCounter](./api.md#updowncounter) | Non-Monotonic |
| [Histogram](./api.md#histogram) | Monotonic |
| [Asynchronous Gauge](./api.md#asynchronous-gauge) | Non-Monotonic |
| [Asynchronous Counter](./api.md#asynchronous-counter) | Monotonic |
| [Asynchrounous UpDownCounter](./api.md#asynchronous-updowncounter) | Non-Monotonic |

This Aggregation does not have any configuration parameters.

This Aggregation informs the SDK to collect:

- The arithmetic sum of `Measurement` values.

#### Last Value Aggregation

The Last Value Aggregation informs the SDK to collect data for the
[Gauge Metric Point](./datamodel.md#gauge).

This Aggregation does not have any configuration parameters.

This Aggregation informs the SDK to collect:

- The last `Measurement`.
- The timestamp of the last `Measurement`.

#### Histogram Aggregation

The Histogram Aggregation informs the SDK to select the best Histogram
Aggregation available. i.e. [Explicit Bucket Histogram
Aggregation](./sdk.md#explicit-bucket-histogram-aggregation).

This Aggregation does not have any configuration parameters.

#### Explicit Bucket Histogram Aggregation

The Explicit Bucket Histogram Aggregation informs the SDK to collect data for
the [Histogram Metric Point](./datamodel.md#histogram) using a set of
explicit boundary values for histogram bucketing.

This Aggregation honors the following configuration parameters:

| Key | Value | Default Value | Description |
| --- | --- | --- | --- |
| Boundaries | double\[\] | [ 0, 5, 10, 25, 50, 75, 100, 250, 500, 1000 ] | Array of increasing values representing explicit bucket boundary values.<br><br>The Default Value represents the following buckets:<br>(-&infin;, 0], (0, 5.0], (5.0, 10.0], (10.0, 25.0], (25.0, 50.0], (50.0, 75.0], (75.0, 100.0], (100.0, 250.0], (250.0, 500.0], (500.0, 1000.0], (1000.0, +&infin;) |
| RecordMinMax | true, false | true | Whether to record min and max. |

Note: This aggregation should not fill out `sum` when used with instruments that
record negative measurements, e.g. `UpDownCounter` or `ObservableGauge`.

This Aggregation informs the SDK to collect:

- Count of `Measurement` values falling within explicit bucket boundaries.
- Arithmetic sum of `Measurement` values in population.
- Min (optional) `Measurement` value in population.
- Max (optional) `Measurement` value in population.

## Attribute limits

Attributes which belong to Metrics are exempt from the
[common rules of attribute limits](../common/common.md#attribute-limits) at this
time. Attribute truncation or deletion could affect identitity of metric time
series and it requires further analysis.

## Exemplar

An [Exemplar](./datamodel.md#exemplars) is a recorded
[Measurement](./api.md#measurement) that exposes the following pieces of
information:

- The `value` that was recorded.
- The `time` the `Measurement` was seen.
- The set of [Attributes](../common/common.md#attributes) associated with the
  `Measurement` not already included in a metric data point.
- The associated [trace id and span
  id](../trace/api.md#retrieving-the-traceid-and-spanid) of the active [Span
  within Context](../trace/api.md#determining-the-parent-span-from-a-context) of
  the `Measurement`.

A Metric SDK MUST provide a mechanism to sample `Exemplar`s from measurements.

A Metric SDK MUST allow `Exemplar` sampling to be disabled.  In this instance
the SDK SHOULD not have overhead related to exemplar sampling.

A Metric SDK MUST sample `Exemplar`s only from measurements within the context
of a sampled trace BY DEFAULT.

A Metric SDK MUST allow exemplar sampling to leverage the configuration of a
metric aggregation. For example, Exemplar sampling of histograms should be able
to leverage bucket boundaries.

A Metric SDK SHOULD provide extensible hooks for Exemplar sampling, specifically:

- `ExemplarFilter`: filter which measurements can become exemplars
- `ExemplarReservoir`: determine how to store exemplars.

### ExemplarFilter

The `ExemplarFilter` interface MUST provide a method to determine if a
measurement should be sampled.

This interface SHOULD have access to:

- The `value` of the measurement.
- The complete set of `Attributes` of the measurement.
- The [Context](../context/context.md) of the measurement, which covers the
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
- The [Context](../context/context.md) of the measurement, which covers the
  [Baggage](../baggage/api.md) and the current active
  [Span](../trace/api.md#span).
- A `timestamp` that best represents when the measurement was taken.

The "offer" method SHOULD have the ability to pull associated trace and span
information without needing to record full context.  In other words, current
span context and baggage can be inspected at this point.

The "offer" method does not need to store all measurements it is given and
MAY further sample beyond the `ExemplarFilter`.

The "collect" method MUST return accumulated `Exemplar`s.

`Exemplar`s MUST retain the any attributes available in the measurement that
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

*SimpleExemplarReservoir*
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

*AlignedHistogramBucketExemplarReservoir*
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

`MetricReader` is an interface which provides the following capabilities:

* Collecting metrics from the SDK.
* Handling the [ForceFlush](#forceflush) and [Shutdown](#shutdown) signals from
  the SDK.

The SDK MUST support multiple `MetricReader` instances to be registered on the
same `MeterProvider`, and the [MetricReader.Collect](#collect) invocation on one
`MetricReader` instance SHOULD NOT introduce side-effects to other `MetricReader`
instances. For example, if a `MetricReader` instance is receiving metric data
points that have [delta temporality](./datamodel.md#temporality), it is expected
that SDK will update the time range - e.g. from (T<sub>n</sub>, T<sub>n+1</sub>]
to (T<sub>n+1</sub>, T<sub>n+2</sub>] - **ONLY** for this particular
`MetricReader` instance.

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

The SDK SHOULD provide a way to allow the preferred [Aggregation
Temporality](./datamodel.md#temporality) to be specified for a `MetricReader`
instance during the setup (e.g. initialization, registration, etc.) time. If the
preferred temporality is explicitly specified then the SDK SHOULD respect that,
otherwise use Cumulative.

[OpenTelemetry SDK](../overview.md#sdk)
authors MAY choose the best idiomatic design for their language:

* Whether to treat the temporality settings as recommendation or enforcement.
  For example, if the temporality is set to Delta, would the SDK want to perform
  Cumulative->Delta conversion for an [Asynchronous
  Counter](./api.md#asynchronous-counter), or downgrade it to a
  [Gauge](./datamodel.md#gauge), or keep consuming it as Cumulative due to the
  consideration of [memory
  efficiency](./supplementary-guidelines.md#memory-management)?
* Refer to the [supplementary
  guidelines](./supplementary-guidelines.md#aggregation-temporality), which have
  more context and suggestions.

### MetricReader operations

#### Collect

Collects the metrics from the SDK. If there are [asynchronous
Instruments](./api.md#asynchronous-instrument) involved, their callback
functions will be triggered.

`Collect` SHOULD provide a way to let the caller know whether it succeeded,
failed or timed out.

`Collect` does not have any required parameters, however, [OpenTelemetry
SDK](../overview.md#sdk) authors MAY choose to add parameters (e.g. callback,
filter, timeout). [OpenTelemetry SDK](../overview.md#sdk) authors MAY choose the
return value type, or do not return anything.

Note: it is expected that the `MetricReader.Collect` implementations will be
provided by the SDK, so it is RECOMMENDED to prevent the user from accidentally
overriding it, if possible (e.g. `final` in C++ and Java, `sealed` in C#).

### Shutdown

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

* `exporter` - the push exporter where the metrics are sent to.
* `exportIntervalMillis` - the time interval in milliseconds between two
  consecutive exports. The default value is 60000 (milliseconds).
* `exportTimeoutMillis` - how long the export can run before it is cancelled.
  The default value is 30000 (milliseconds).

## MetricExporter

`MetricExporter` defines the interface that protocol-specific exporters MUST
implement so that they can be plugged into OpenTelemetry SDK and support sending
of telemetry data.

The goal of the interface is to minimize burden of implementation for
protocol-dependent telemetry exporters. The protocol exporter is expected to be
primarily a simple telemetry data encoder and transmitter.

Metric Exporter has access to the [aggregated metrics
data](./datamodel.md#timeseries-model).

There could be multiple [Push Metric Exporters](#push-metric-exporter) or [Pull
Metric Exporters](#pull-metric-exporter) or even a mixture of both configured on
a given `MeterProvider`. Different exporters can run at different schedule, for
example:

* Exporter A is a push exporter which sends data every 1 minute.
* Exporter B is a push exporter which sends data every 5 seconds.
* Exporter C is a pull exporter which reacts to a scraper over HTTP.
* Exporter D is a pull exporter which reacts to another scraper over a named
  pipe.

`MetricExporter` SHOULD provide a way to allow `MetricReader` to retrieve its
preferred temporality.

### Push Metric Exporter

Push Metric Exporter sends the data on its own schedule. Here are some examples:

* Sends the data based on a user configured schedule, e.g. every 1 minute.
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

Exports a batch of [Metric points](./datamodel.md#metric-points). Protocol
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
                                    +--> timestamps, dimensions, value (or buckets), exemplars, ...
```

Refer to the [Metric points](./datamodel.md#metric-points) section from the
Metrics Data Model specification for more details.

Note: it is highly recommended that implementors design the `Metric` data type
_based on_ the [Data Model](./datamodel.md), rather than directly use the data
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
design a completely different pull exporter interface.

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

All the metrics components SHOULD allow new methods to be added to existing
components without introducing breaking changes.

All the metrics SDK methods SHOULD allow optional parameter(s) to be added to
existing methods without introducing breaking changes, if possible.

## Concurrency requirements

For languages which support concurrent execution the Metrics SDKs provide
specific guarantees and safeties.

**MeterProvider** - Meter creation, `ForceFlush` and `Shutdown` are safe to be
called concurrently.

**ExemplarFilter** - all methods are safe to be called concurrently.

**ExemplarReservoir** - all methods are safe to be called concurrently.

**MetricReader** - `Collect` and `Shutdown` are safe to be called concurrently.

**MetricExporter** - `ForceFlush` and `Shutdown` are safe to be called
concurrently.
