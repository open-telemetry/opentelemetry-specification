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

### Meter Creation

New `Meter` instances are always created through a `MeterProvider` (see
[API](./api.md#meterprovider)). The `name` and `version` arguments supplied to
the `MeterProvider` must be used to create an
[`InstrumentationLibrary`](https://github.com/open-telemetry/oteps/blob/main/text/0083-component.md)
instance which is stored on the created `Meter`.

Configuration (i.e., [MeasurementProcessors](#measurementprocessor),
[MetricProcessors](#metricprocessor), [MetricExporters](#metricexporter) and
[`Views`](#view)) MUST be managed solely by the `MeterProvider` and it MUST
provide some way to configure all of them that are implemented in the SDK, at
least when creating or initializing it.

The `MeterProvider` MAY provide methods to update the configuration. If
configuration is updated (e.g., adding a `MetricProcessor`), the updated
configuration MUST also apply to all already returned `Meters` (i.e. it MUST NOT
matter whether a `Meter` was obtained from the `MeterProvider` before or after
the configuration change). Note: Implementation-wise, this could mean that
`Meter` instances have a reference to their `MeterProvider` and access
configuration only via this reference.

### Shutdown

TODO

### ForceFlush

TODO

### View

`View` gives the SDK users flexibility to customize the metrics they want. Here
are some examples when `View` is needed:

* Customize which [Instrument](./api.md#instrument) to be processed/ignored. For
  example, an [instrumented library](../glossary.md#instrumented-library) can
  provide both temperature and humidity, but the application developer only
  wants temperature information.
* Customize the aggregation - if the default aggregation associated with the
  Instrument does not meet the expectation. For example, an HTTP client library
  might expose HTTP client request duration as [Histogram](./api.md#histogram)
  by default, but the application developer only wants the total count (sum
  aggregation) of outgoing requests.
* Customize which metrics dimension(s) to be reported. For example, an HTTP
  server library might expose HTTP verb (e.g. GET, POST), HTTP status code (e.g.
  200, 301, 404), and a [Baggage](../baggage/api.md) value indicating whether
  the request is coming from a bot/crawler or not. The application developer
  might only care about HTTP status code (e.g. reporting the total count of HTTP
  requests for each HTTP status code). There are also extreme scenario that the
  application developer does not need any dimension (e.g. just get the total
  count of all incoming requests).

The MeterProvider MUST provide a way to register Views, and here are the
inputs:

* The Instrument selection criteria (required), which MUST cover:
  * The `name` of the Meter.
  * The `version` of the Meter.
  * The `name` of the Instrument.
  * The `kind` of the Instrument.
* The `name` of the View (optional). If not provided, the Instrument `name`
  would be used by default.
* The `description` of the View (optional). If not provided, the Instrument
  `description` would be used by default.
* The `attribute keys` (optional). If not provided, all the attribute keys will
  be used by default (TODO: once the Hint API is available, the default behavior
  should respect the Hint if it is available).
* The `extra dimensions` which come from Baggage/Context (optional). If not
  provided, no extra dimension will be used.

TODO:

* Allow multiple pipelines (processors, exporters).
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
