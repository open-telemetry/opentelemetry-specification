# Metrics SDK

**Status**: [Experimental](../document-status.md)

**Owner:**

* [Reiley Yang](https://github.com/reyang)

**Domain Experts:**

* [Bogdan Brutu](https://github.com/bogdandrutu)
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

`MeasurementProcessor` is an interface which allows hooks when a Measurement is
recorded by an Instrument.

`MeasurementProcessor` has access to the [raw
measurements](./datamodel.md#event-model) and the corresponding Instrument. It
could also access the [Baggage](../baggage/api.md) and
[Context](../context/context.md) if the Baggage/Context are available.

```text
+------------------+
| MeterProvider    |                 +----------------------+
|   Meter A        | Measurements... |                      | Metrics... +-----------------+
|     Instrument X |-----------------> MeasurementProcessor +------------>                 |
|     Instrument Y +                 |                      |            |                 |
|   Meter B        |                 +----------------------+            |                 |
|     Instrument Z |                                                     | In-memory state |
|     ...          |                 +----------------------+            |                 |
|     ...          | Measurements... |                      | Metrics... |                 |
|     ...          |-----------------> MeasurementProcessor +------------>                 |
|     ...          |                 |                      |            +-----------------+
|     ...          |                 +----------------------+
+------------------+
```

## MetricProcessor

`MetricProcessor` is an interface which allows hooks for [pre-aggregated metrics
data](./datamodel.md#timeseries-model).

Built-in metric processors are responsible for batching and conversion of
metrics data to exportable representation and passing batches to exporters.

The following diagram shows `MetricProcessor`'s relationship to other components
in the SDK:

```text
                     +-----------------+  +-----------------------+
+-----------------+  |                 |  |                       |
|                 |--> MetricProcessor |--> MetricExporter (push) |--> Another process
|                 |  |                 |  |                       |
|                 |  +-----------------+  +-----------------------+
| In-memory state |
|                 |  +-----------------+  +-----------------------+
|                 |  |                 |  |                       |
|                 |--> MetricProcessor |--> MetricExporter (pull) |--> Another process (scraper)
+-----------------+  |                 |  |                       |
                     +-----------------+  +-----------------------+
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
Metric Exporters](#pull-metric-exporter) or even a mixture of both configured on a
given MeterProvider.

### Push Metric Exporter

Push Metric Exporter sends the data on its own schedule. Here are some examples:

* Sends the data based on a user configured schedule, e.g. every 1 minute.
* Sends the data when there is a severe error.

### Pull Metric Exporter

Pull Metric Exporter reacts to the metrics scrapers and reports the data
passively. This pattern has been widely adopted by
[Prometheus](https://prometheus.io/).
