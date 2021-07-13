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
[API](./api.md#meterprovider)). The `name`, `version` (optional), and
`schema_url` (optional) arguments supplied to the `MeterProvider` MUST be used
to create an
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

### Pipeline

A pipeline is a logical group of:

* An ordered list of [View](#view)s
* A [MeasurementProcessor](#measurementprocessor)
* An ordered list of [MetricProcessor](#metricprocessor)s
* A [MetricExporter](#metricexporter)

```text
               +----------------------+  +-----------------+
               |                      |  |                 |
Measurements --> MeasurementProcessor +--> In-memory state +--+
               |                      |  |                 |  |
               +----------------------+  +-----------------+  |
                                                              |
  +-----------------------------------------------------------+
  |
  |  +-------------------+             +-------------------+ 
  |  |                   |             |                   | 
  +--> MetricProcessor 1 +--> ... ... -> MetricProcessor N +--+
     |                   |             |                   |  |
     +-------------------+             +-------------------+  |
                                                              |
  +-----------------------------------------------------------+
  |
  |  +----------------+
  |  |                |
  +--> MetricExporter +--> Another process
     |                |
     +----------------+
```

`MeterProvider` MUST support multiple pipelines:

```text
+------------------+
| MeterProvider    |
|   Meter A        +-----> Pipeline 1
|     Counter X    |
|     Histogram Y  +-----> ...
|   Meter B        |       ...
|     Gauge Z      |
|     ...          +-----> Pipeline N
|   ...            |
+------------------+
```

Each pipeline has an ordered list of [View](#view)s, which provides
configuration for:

* Whether the Measurements from a certain Instrument should go through the
  pipeline or not.
* How should the Measurements turn into Metrics.

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
  by default, but the application developer only wants the total count of
  outgoing requests.
* Customize which attribute(s) to be reported as metrics dimension(s). For
  example, an HTTP server library might expose HTTP verb (e.g. GET, POST) and
  HTTP status code (e.g. 200, 301, 404). The application developer might only
  care about HTTP status code (e.g. reporting the total count of HTTP requests
  for each HTTP status code). There are also extreme scenario that the
  application developer does not need any dimension (e.g. just get the total
  count of all incoming requests).
* Add additional dimension(s) from the [Context](../context/context.md). For
  example, a [Baggage](../baggage/api.md) value might be available indicating
  whether an HTTP request is coming from a bot/crawler or not. The application
  developer might want this to be converted to a dimension for HTTP server
  metrics (e.g. the request/second from bots vs. real users).

The SDK MUST provide the means to register Views with a [MeterProvider
Pipeline](#pipeline). Here are the inputs:

* The Instrument selection criteria (required), which covers:
  * The `name` of the Instrument(s), with wildcard support (required).
  * The `name` of the Meter (optional).
  * The `version` of the Meter (optional).
  * The `schema_url` of the Meter (optional).
  * Individual language client MAY choose to support more criteria. For example,
    a strong typed language MAY support point type (e.g. allow the users to
    select Instruments based on whether the underlying type is integer or
    double).
* The `name` of the View (optional). If not provided, the Instrument `name`
  would be used by default. This will be used as the name of the [metrics
  stream](./datamodel.md#events--data-stream--timeseries).
* The configuration for the resulting [metrics
  stream](./datamodel.md#events--data-stream--timeseries):
  * The `description`. If not provided, the Instrument `description` would be
    used by default.
  * A list of `attribute keys` (optional). If not provided, all the attribute
    keys will be used by default (TODO: once the Hint API is available, the
    default behavior should respect the Hint if it is available).
  * The `extra dimensions` which come from Baggage/Context (optional). If not
    provided, no extra dimension will be used. Please note that this only
    applies to [synchronous Instruments](./api.md#synchronous-instrument), any
    `extra dimensions` configured on [asynchronous
    Instruments](./api.md#asynchronous-instrument) will be considered as error.
  * The `aggregation` (optional) to be used. If not provided, a default
    aggregation will be applied by the SDK. The default aggregation is a TODO
    (e.g. first see if there is an explicitly specified aggregation from the
    View, if not, see if there is a Hint, if not, fallback to the default
    aggregation that is associated with the Instrument type), and for histogram,
    the default buckets would be (-&infin;, 0], (0, 5.0], (5.0, 10.0], (10.0,
    25.0], (25.0, 50.0], (50.0, 75.0], (75.0, 100.0], (100.0, 250.0], (250.0,
    500.0], (500.0, 1000.0], (1000.0, +&infin;).

The SDK SHOULD use the following logic to determine how to process an
Instrument:

* Determine the MeterProvider which "owns" the Instrument.
* If the MeterProvider has no [Pipeline](#pipeline) registered, go to the END.
* For each Pipeline:
  * If the Pipeline has no `View` registered, take the Instrument and apply the
    default configuration.
  * If the Pipeline has one or more `View`(s) registered, for each View:
    * If the Instrument could match the instrument selection criteria:
      * Try to apply the View configuration. If there is an error (e.g. the View
        asks for extra dimensions from the Baggage, but the Instrument is
        [asynchronous](./api.md#asynchronous-instrument) which doesn't have
        Context) or a conflict (e.g. the View requires to export the metrics
        using a certain name, but the name is already used by another View),
        provide a way to let the user know (e.g. expose [self-diagnostics
        logs](../error-handling.md#self-diagnostics)).
      * Stop processing the remaining Views (proceed to the next Pipeline).
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

meter_provider.start_pipeline(
    # all the metrics will be exported using the default configuration
    pipeline: pipeline
        .set_exporter(ConsoleExporter())
).start_pipeline(
    # metrics from X and Y (reported as Foo and Bar) will be exported to Prometheus upon scraping
    pipeline: pipeline
        .add_view("X")
        .add_view("Foo", instrument_name="Y")
        .add_view(
            "Bar",
            instrument_name="Y",
            aggregation=HistogramAggregation(buckets=[5.0, 10.0, 25.0, 50.0, 100.0]))
        .set_exporter(PrometheusExporter())
)
```

```python
meter_provider.start_pipeline(
    # all the metrics will be exported using the default configuration
    pipeline: pipeline
        .add_view("*") # a wildcard view that matches everything
        .set_exporter(ConsoleExporter())
)
```

```python
meter_provider.start_pipeline(
    # Counter X will be exported as cumulative sum
    pipeline: pipeline
        .add_view("X", aggregation=SumAggregation(CUMULATIVE))
        .set_exporter(ConsoleExporter())
)
```

```python
meter_provider.start_pipeline(
    # Counter X will be exported as delta sum
    # Histogram Y and Gauge Z will be exported with 2 dimensions (a and b)
    pipeline: pipeline
        .add_view("X", aggregation=SumAggregation(DELTA))
        .add_view("*", attribute_keys=["a", "b"])
        .set_exporter(ConsoleExporter())
)
```

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
|     Instrument X +-----------------> MeasurementProcessor +------------> In-memory state |
|     Instrument Y |                 |                      |            |                 |
|   Meter B        |                 +----------------------+            +-----------------+
|     Instrument Z |
|     ...          |                 +----------------------+            +-----------------+
|     ...          | Measurements... |                      | Metrics... |                 |
|     ...          +-----------------> MeasurementProcessor +------------> In-memory state |
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
| In-memory state +------------> MetricProcessor +------------> MetricExporter (push) +--> Another process
|                 |            |                 |            |                       |
+-----------------+            +-----------------+            +-----------------------+

+-----------------+            +-----------------+            +-----------------------+
|                 | Metrics... |                 | Metrics... |                       |
| In-memory state +------------> MetricProcessor +------------> MetricExporter (pull) +--> Another process (scraper)
|                 |            |                 |            |                       |
+-----------------+            +-----------------+            +-----------------------+
```

## MetricExporter

`MetricExporter` defines the interface that protocol-specific exporters MUST
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
