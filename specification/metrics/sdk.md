# Metrics SDK

**Status**: [Experimental](../document-status.md)

**Owner:**

* [Reiley Yang](https://github.com/reyang)

**Domain Experts:**

* [Bogdan Drutu](https://github.com/bogdandrutu)
* [Josh Suereth](https://github.com/jsuereth)
* [Joshua MacDonald](https://github.com/jmacd)

Note: this specification is subject to major changes. To avoid thrusting
language client maintainers, we don't recommend OpenTelemetry clients to start
the implementation unless explicitly communicated via
[OTEP](https://github.com/open-telemetry/oteps#opentelemetry-enhancement-proposal-otep).

<details>
<summary>
Table of Contents
</summary>

* [MeterProvider](#meterprovider)
* [MeasurementProcessor](#measurementprocessor)
* [MetricProcessor](#metricprocessor)
* [MetricExporter](#metricexporter)
  * [Push Metric Exporter](#push-metric-exporter)
  * [Pull Metric Exporter](#pull-metric-exporter)

</details>

## MeterProvider

TODO:

* Allow multiple pipelines (processors, exporters).
* Configure "Views".
* Configure timing (related to [issue
  1432](https://github.com/open-telemetry/opentelemetry-specification/issues/1432)).

## MeasurementProcessor

`MeasurementProcessor` is an interface which allows hooks when a
[Measurement](./api.md#measurement) is recorded by an
[Instrument](./api.md#instrument).

`MeasurementProcessor` MUST have access to:

* The `Measurement`
* The `Instrument`, which is used to report the `Measurement`
* The `Resource`, which is associated with the `MeterProvider`

In addition to things listed above, if the `Measurement` is reported by a
synchronous `Instrument` (e.g. [Counter](./api.md#counter)),
`MeasurementProcessor` MUST have access to:

* [Baggage](../baggage/api.md)
* [Context](../context/context.md)
* The [Span](../trace/api.md#span) which is associated with the `Measurement`

Depending on the programming language and runtime model, these can be provided
explicitly (e.g. as input arguments) or implicitly (e.g. [implicit
Context](../context/context.md#optional-global-operations) and the [currently
active span](../trace/api.md#context-interaction)).

```text
+------------------+
| MeterProvider    |                 +----------------------+            +-----------------+
|   Meter A        | Measurements... |                      | Metrics... |                 |
|     Instrument X |-----------------> MeasurementProcessor +------------> In-memory state |
|     Instrument Y +                 |                      |            |                 |
|   Meter B        |                 +----------------------+            +-----------------+
|     Instrument Z |
|     ...          |                 +----------------------+            +-----------------+
|     ...          | Measurements... |                      | Metrics... |                 |
|     ...          |-----------------> MeasurementProcessor +------------> In-memory state |
|     ...          |                 |                      |            |                 |
|     ...          |                 +----------------------+            +-----------------+
+------------------+
```

### Aggregation MeasurementProcessor

An `Aggregation` `MeasurementProcessor` is responsible for computing instrument
`Measurements` into [Pre-Aggregated Metrics](./datamodel.md##opentelemetry-protocol-data-model).

The `Aggregation` `MeasurementProcessor` MUST have access to `In-Memory State`.

The `Aggregation` `MeasurementProcessor` MUST create and configure [`Aggregators`](#Aggregator)
based on [View](./sdk.md) configuration.

e.g. Create a Sum Aggregator with monotonic values and delta temporality.

The `Aggregation` `MeasurementProcessor` MUST provide `Measurements` to the
properly configured `Aggregators` based on [View](./sdk.md) configuration.

e.g. A View re-configures a temperature Gauge Instrument to use Histogram
aggregator (configured for Cumulative temporality).

e.g. A View re-configures a temperature Gauge Instrument to count only by
Attribute "Location" (e.g. Location=Portland or Location=Seattle). The
Aggregation MeasurementProcessor provides measurements only to the
Aggregator instance that handles the specific Attribute Key/Value combination.
(i.e. "Location=Portland" => Aggregator #1, "Location=Seattle" => Aggregator #2)

```text
                 +---------------------------+
                 | Aggregation               |
                 |    MeasurementProcessor   |
                 |                           |   +-----------------+
                 |    ...                    |   |                 |
 [Measurements]-----> ... <--------------------->| In-Memory State |
                 |    ...                    |   |                 |     
                 |     |                     |   +-----------------+
                 |     |  +--------------+   |
                 |     |  | Aggregator   |   |
                 |     |  |              |   |
                 |     +---->"Update"    |   |
                 |     |  |    ...       |   |
                 |     |  |    "Collect"--------[Pre-Aggregated Metrics]-->
                 |     |  +--------------+   |
                 |     |                     |
                 |     |  +--------------+   |
                 |     |  | Aggregator   |   |
                 |     |  |              |   |
                 |     +---->"Update"    |   |
                 |        |    ...       |   |
                 |        |    "Collect"--------[Pre-Aggregated Metrics]-->
                 |        +--------------+   |
                 |                           |
                 +---------------------------+
```

#### Default Instrument to Aggregator Mapping

| Instrument Kind | Default Aggregator | Monotonic | Temporality | Notes |
| --- | --- | --- | --- | --- |
| [Counter](./api.md#counter) | [Sum Aggregator](#SumAggregator) | Monotonic | Delta | |
| [Asynchronous Counter](./api.md#asynchronous-counter) | [Sum Aggregator](#SumAggregator) | Monotonic | Cumulative | |
| [UpDownCounter](./api.md#updowncounter) | [Sum Aggregator](#SumAggregator) | Non-Monotonic | Delta | |
| [Asynchrounous UpDownCounter](./api.md#asynchronous-updowncounter) | [Sum Aggregator](#SumAggregator) | Non-Monotonic | Cumulative | |
| [Asynchronous Gauge](./api.md#asynchronous-gauge) | [Gauge Aggregator](#GaugeAggregator) | n/a | Cumulative | |
| [Histogram](./api.md#histogram) | [Histogram Aggregator](#HistogramAggregator) | n/a | Delta | TBD Boundaries|

### Aggregator

An `Aggregator` computes incoming [Measurements](./api.md#measurement) into a
[Pre-Aggregated Metric](./datamodel.md#opentelemetry-protocol-data-model).

An `Aggregator` MUST provide an interface to "update" itself given [Measurement](./api.md#measurement)
data.

An `Aggregator` MUST provide an interface to "collect" [Pre-Aggregated Metric](./datamodel.md#timeseries-model)
data. The collect call should be treated as a stateful action and may reset its
internal state.

The SDK MUST provide the following Aggregators to support the [Metric Points](./datamodel.md#metric-points)
in the [Metrics Data Model](./datamodel.md).

- [Sum Aggregator](#SumAggregator)
- [Gauge Aggregator](#GaugeAggregator)
- [Histogram Aggregator](#HistogramAggregator)

### SumAggregator

The Sum Aggregator collect data for the [Sum Metric Point](./datamodel.md#sums)
and MUST be configurable to support Monotonicity and/or Temporality.

Sum Aggregator maintains the following state:

* Start Time<sup>1</sup>
* Sum (sum of Measurements)

\[1\]: Start Time is exclusive (aka not inclusive) of the provided time.

### GaugeAggregator

The Gauge Aggregator collect data for the [Gauge Metric Point](./datamodel.md#gauge).

Gauge Aggregator maintains the following state:

* Last Timestamp<sup>2</sup>
* Last Value<sup>2</sup>

\[2\]: Data from latest Measurement given, avoiding any time comparison.

### HistogramAggregator

The Histogram Aggregator collect data for the [Histogram Metric Point](./datamodel.md#histogram)
and MUST be configurable to support Temporality and Bucket Boundary values.

Histogram Aggregator maintains the following state:

* Start Time<sup>3</sup>
* Count (count of points in population)
* Sum (sum of point values in population)
* Bucket Boundary values
* Bucket Counts (count of values falling within configured Boundary Values)

\[3\]: Start Time is exclusive (aka not inclusive) of the provided time.

## MetricProcessor

`MetricProcessor` is an interface which allows hooks for [pre-aggregated metrics
data](./datamodel.md#timeseries-model).

Built-in metric processors are responsible for batching and conversion of
metrics data to exportable representation and passing batches to exporters.

The following diagram shows `MetricProcessor`'s relationship to other components
in the SDK:

```text
+-----------------+            +-----------------+            +-----------------------+
|                 | Metrics... |                 | Metrics... |                       |
> In-memory state | -----------> MetricProcessor | -----------> MetricExporter (push) |--> Another process
|                 |            |                 |            |                       |
+-----------------+            +-----------------+            +-----------------------+

+-----------------+            +-----------------+            +-----------------------+
|                 | Metrics... |                 | Metrics... |                       |
> In-memory state |------------> MetricProcessor |------------> MetricExporter (pull) |--> Another process (scraper)
|                 |            |                 |            |                       |
+-----------------+            +-----------------+            +-----------------------+
```

## MetricExporter

`MetricExporter` defines the interface that protocol-specific exporters must
implement so that they can be plugged into OpenTelemetry SDK and support sending
of telemetry data.

The goal of the interface is to minimize burden of implementation for
protocol-dependent telemetry exporters. The protocol exporter is expected to be
primarily a simple telemetry data encoder and transmitter.

Metric Exporter has access to the [pre-aggregated metrics
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

### Push Metric Exporter

Push Metric Exporter sends the data on its own schedule. Here are some examples:

* Sends the data based on a user configured schedule, e.g. every 1 minute.
* Sends the data when there is a severe error.

### Pull Metric Exporter

Pull Metric Exporter reacts to the metrics scrapers and reports the data
passively. This pattern has been widely adopted by
[Prometheus](https://prometheus.io/).
