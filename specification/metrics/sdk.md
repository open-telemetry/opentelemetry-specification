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

### Aggregator

An `Aggregator` is a type of `MeasurementProcessor` and computes "aggregate"
data from [Measurements](./api.md#measurement) and its `In-Memory State` into
zero or more [Pre-Aggregated Metrics](./datamodel.md#timeseries-model).

```text

                 +---------------------+
                 | Aggregator          |
                 |                     |
 [Measurements]------> "Aggregate"     |
                 |         |           |
                 | +-------V---------+ |
                 | |                 | |
                 | | In-Memory State | |
                 | |                 | |
                 | +-------+---------+ |
                 |         |           |
                 |         V           |
                 |      "Collect" +------[Pre-Aggregated Metrics]-->
                 |                     |
                 +---------------------+
```

An `Aggregator` MUST provide an interface to "aggregate" [Measurement](./api.md#measurement)
data into its `In-Memory State`.

An `Aggregator` MUST provide an interface to "collect" [Pre-Aggregated Metric](./datamodel.md#timeseries-model)
data from its `In-Memory State`. The collect call should be treated as a
stateful action and may reset in-memory state data. e.g. Resetting the time window
for delta temporality instruments.

An `Aggregator` MUST have read/write access to memory storage (`In-Memory
State`) where it can store/retrieve/manage its own internal state.

Note: SDK SHOULD provide configuration and control for memory availability to
optimize usage. Aggregators MUST log errors when memory limits are reached
and/or data lost occurs due to memory mitigation strategy. e.g dropping high
cardinality attributes.

SDK MUST instantiate and configure aggregator/s based on [View](./sdk.md)
configuration. e.g. Create a Sum aggregator with monotonic values and delta
temporality (per mapping/routing).

SDK MUST map/route measurements, based on [View](./sdk.md) configuration, to the
configured aggregator/s. Each map/route has zero or more instances of
aggregators.

e.g. [View](./sdk.md) configuration specify which Attribute Keys to include,
thus creating a map/route per configured Key/Value combination. The measurement
is routed to each route and its configured aggregator/s.

e.g. Support for multiple exporters creates a map/route per Exporter. The
measurement is routed to each route and its configured aggregator/s.

**Note:** An `Aggregator` instance is scoped to "aggregate" values that result
in one metric timeseries (see [Metrics Data Model](./datamodel.md)). The SDK
(via the [View](./sdk.md) configuration) allows Measurements to map/route into
zero or more resulting metric timeseries (aka Aggregators). One map/route scheme
involve expanding measurement `Attributes` to combinations of keys and values.
The SDK will facilitate this map/route scheme. Thus, SDK will create and
configure aggregators and route measurments to these aggregator instances.

SDK MUST provide aggregators to support the default configured aggregator
per instrument kind. e.g. Counter instruments default to a "Sum" aggregator
configured for monotonic values.

### Last Value Aggregator

The Last Value Aggregator collect data for the [Gauge Metric Point](./datamodel.md#gauge)
and is default aggregator for the following instruments:

* [Asynchronous Gauge](./api.md#asynchronous-gauge) instrument.

Last Value Aggregator maintains the following in memory:

* Last Timestamp<sup>1</sup>
* Last Value<sup>1</sup>

\[1\]: Data from latest Measurement given, avoiding any time comparison.

### Sum Aggregator

The Sum Aggregator collect data for the [Sum Metric Point](./datamodel.md#sums)
and is default aggregator for the following instruments:

* [Counter](./api.md#counter) instrument.
* [Asynchronous Counter](./api.md#asynchronous-counter) instrument.
* [UpDownCounter](./api.md#updowncounter) instrument.
* [Asynchrounous UpDownCounter](./api.md#asynchronous-updowncounter) instrument.

The Sum Aggregator MUST be configurable to support different Monoticity and/or
Temporality.

Sum Aggregator maintains the following in memory:

* Time window (e.g. start time, end time)
* Sum (sum of Measurements per Monoticity and Temporality configuration.)

### Histogram Aggregator

The Histogram Aggregator collect data for the [Histogram Metric Point](./datamodel.md#histogram)
and is default aggregator for the following instruments:

* [Histogram](./api.md#histogram) instrument.

The Histogram Aggregator MUST be configurable to support different Temporality
and bucket Boundary Values.

Histogram Aggregator maintains the following in memory:

* Start Time<sup>2</sup>
* Count (count of points in population)
* Sum (sum of point values in population)
* Boundary Values
* Bucket Counts (count of values falling within configured Boundary Values)

\[2\]: Start Time is exclusive (aka not inclusive) of the provided time.

### An example of SDK implementation

SDK expand each Measurement's Attribute by the combination of key/value pairs.
For each distinct combination, SDK will route to an instance of a configured
aggregator.

```text
+------------------+  +-------------------------------------------------------------+
| MeterProvider    |  | SDK                                                         |
|   Meter A        |  |                     +----------------------+                |
|     Instrument X |-----[Measurements]---->| MeasurementProcessor |                |
|     Instrument Y |  |                     +-----------+----------+                |
|     ...          |  |                                 |                           |
|     ...          |  |                           [Measurements]                    |
+------------------+  |                                 |                           |
                      |        SDK expand Measurements per View configuration       |
                      |        (e.g. by Attribute key/value pairs)                  |
                      |                                 |                           |
                      |                                 |"Aggregate"                |
                      | Measurement #1:                 V                           |
                      |                      +---------------------+                |
                      |      B=Y ----------->| Aggregator #1 (B=Y) |---->+          |
                      |                      | In-Memory State:    |     |          |
                      |                      |   count=1           |     |          |
                      |                      +---------------------+     |          |
                      |      A=X -------+                                |          |
                      |                 |    +---------------------+     |          |
                      | Measurment #2:  +--->| Aggregator #2 (A=X) |---->|          |
                      |                 |    | In-Memory State:    |     |          |
                      |                 |    |   count=2           |     |          |
                      |                 |    +---------------------+     |          |
                      |      A=X -------+                                |          |
                      |                      +---------------------+     |          |
                      |      B=Z ----------->| Aggregator #3 (B=Z) |---->|          |
                      |                      | In-Memory State:    |     |          |
                      |                      |   count=1           |     |          |
                      |                      +---------------------+     |          |
                      |                                                  |"Collect" |
                      |                                                  |          |
                      |                                              [Metrics]      |
                      |                                                  |          |
                      |                                        +---------V-------+  |
                      |                                        | MetricProcessor |  |
                      |                                        +---------+-------+  |
                      |                                                  |          |
                      |                                              [Metrics]      |
                      |                                                  |          |
                      |                                        +---------V-------+  |
                      |                                        | MetricExporter  |=====> OTLP Collector
                      |                                        +-----------------+  |
                      +-------------------------------------------------------------+
```

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
