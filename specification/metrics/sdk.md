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
[`Views`](#view)) MUST be managed solely by the `MeterProvider` and the SDK MUST
provide a way to configure all options that are implemented by the SDK. This MAY be done at the
time of MeterProvider creation if appropriate.

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
  * Individual language client MAY choose to support more criteria. For example,
    a strong typed language MAY support point type (e.g. allow the users to
    select Instruments based on whether the underlying type is integer or
    double).
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
    applies to [synchronous Instruments](./api.md#synchronous-instrument).
  * The `aggregation` (optional) to be used. If not provided, a default
    aggregation will be applied by the SDK. The default aggregation is a TODO.

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
    .set_exporter(PrometheusExporter())
```

```python
# all the metrics will be exported using the default configuration
meter_provider.set_exporter(ConsoleExporter())
```

```python
# all the metrics will be exported using the default configuration
meter_provider
    .add_view("*") # a wildcard view that matches everything
    .set_exporter(ConsoleExporter())
```

```python
# Counter X will be exported as cumulative sum
meter_provider
    .add_view("X", aggregation=SumAggregation(CUMULATIVE))
    .set_exporter(ConsoleExporter())
```

```python
# Counter X will be exported as delta sum
# Histogram Y and Gauge Z will be exported with 2 dimensions (a and b)
meter_provider
    .add_view("X", aggregation=SumAggregation(DELTA))
    .add_view("*", attribute_keys=["a", "b"])
    .set_exporter(ConsoleExporter())
```

## Aggregator

An `Aggregator` computes incoming Instrument [Measurements](./api.md#measurement)
into [Pre-Aggregated Metrics](./datamodel.md#opentelemetry-protocol-data-model).

The [View](./sdk.md#view) informs the SDK on creation and configuration of
Aggregators. An [Aggregator Name](./sdk.md#aggregator-name) may be use to
refer to an Aggregator and configuration.

e.g. The View specifies the string name of an Aggregator (i.e. "Histogram")
and an optional list of configuration parameter overrides.

```c#
// Use default Histogram
meter_provider
  .add_view(
    instrument_name = "X",
    aggregator = "Histogram");

// Use Histogram with custom boundaries and monotonic values
meter_provider
  .add_view(
    instrument_name = "X",
    aggregator = "Histogram",
    aggregator_params = new KeyValuePair<string, object>[]
    {
      new KeyValuePair<string, object>("Monotonic", true),
      new KeyValuePair<string, object>("Boundaries", new double[] { 0.0, 10.0, 100.0 }),
    });
```

The [View](./sdk.md#view) informs the SDK to provide correct
Instrument [Measurements](./api.md#measurement) to the correct Aggregators.

An `Aggregator` is created with optional configuration parameters
(i.e. Monotonic=true, Boundaries=[0, 10, 100]).
Default configuration parameters will be use unless overridden by
optional configuration parameters.

An `Aggregator` has a means to "update" with incoming Instrument
[Measurement](./api.md#measurement) data.

An `Aggregator` has a means to "collect"
[Pre-Aggregated Metric](./datamodel.md#timeseries-model) data.
The "collect" action should be treated as stateful and may update its
internal state.

e.g. When "collect" is acted on a Sum Aggregator, configured for delta
temporality, it will return a delta metric and reset its internal
counts and time-period window. A downstream Exporter, supporting only
cumulative temporality, may choose to 1. drop the delta metric
OR 2. support [Delta to Cumulative](./datamodel.md#sums-delta-to-cumulative)
conversion.

**TBD**:
The [View](./sdk.md#view) may inform an `Aggregator` to collect
[Examplars](./datamodel.md#exemplars).

### Aggregator Name

The [View](./sdk.md#view) can refer to the following Aggregator by name.

| Name | Aggregator | Configuration Parameters |
| --- | --- | --- |
| Default<sup>1</sup> | Depends<sup>3</sup> | Depends<sup>3</sup> |
| None<sup>2</sup> | - | - |
| Sum | [Sum Aggregator](./sdk.md#sum-aggregator) | Depends<sup>3</sup> |
| Gauge | [Last Value Aggregator](./sdk.md#last-value-aggregator) | - |
| Histogram | [Explicit Bucket Histogram Aggregator](./sdk.md#explicit-bucket-histogram-aggregator) | Default |

\[1\]: The name "Default" is use to select Aggregator by Instrument Kind.
See [Default Aggregators](./sdk.md#default-aggregators).

\[2\]: The name "None" is use to specify no Aggregator or
a "virtual" Aggregator which ignores all measurements.

\[3\]: Depends on the Instrument Kind. See [Default Aggregators](./sdk.md#default-aggregators).

### Default Aggregators

The SDK MUST provide default Aggregators to support the
[Metric Points](./datamodel.md#metric-points) in the
[Metrics Data Model](./datamodel.md).

The "Default" Aggregator use the Instrument Kind (e.g. at View registration)
to select the correct Aggregator and default configuration parameters.

| Instrument Kind | Default Aggregator | Monotonic | Temporality | Boundaries |
| --- | --- | --- | --- | --- |
| [Counter](./api.md#counter) | [Sum Aggregator](./sdk.md#sum-aggregator) | true | Delta | - |
| [UpDownCounter](./api.md#updowncounter) | [Sum Aggregator](./sdk.md#sum-aggregator) | false | Delta | - |
| [Asynchronous Counter](./api.md#asynchronous-counter) | [Sum Aggregator](./sdk.md#sum-aggregator) | true | Cumulative | - |
| [Asynchrounous UpDownCounter](./api.md#asynchronous-updowncounter) | [Sum Aggregator](./sdk.md#sum-aggregator) | false | Cumulative | - |
| [Asynchronous Gauge](./api.md#asynchronous-gauge) | [Last Value Aggregator](./sdk.md#last-value-aggregator) | - | - | - |
| [Histogram](./api.md#histogram) | [Explicit Bucket Histogram Aggregator](./sdk.md#explicit-bucket-histogram-aggregator) | true | Delta | Default<sup>1</sup> |

\[1\]: See Default Bucket Boundaries in [Explicit Bucket Histogram Aggregator](./sdk.md#explicit-bucket-histogram-aggregator).

### Last Value Aggregator

The Last Value Aggregator collect data for the
[Gauge Metric Point](./datamodel.md#gauge).

This Aggregator does not have any configuration parameter keys.

This Aggregator reports on:

- The last `Measurement`.

### Sum Aggregator

The Sum Aggregator collect data for the [Sum Metric Point](./datamodel.md#sums).

This Aggregator honors the following configuration parameter keys:

| Key | Value | Default | Description |
| --- | --- | --- | --- |
| Monotonic | boolean | Depends<sup>1</sup> | if true, non-positive values are treated as errors<sup>2</sup>. |
| Temporality | Delta, Cummulative | Depends<sup>1</sup> | See [Temporality](./datamodel.md#temporality). |

\[1\]: Depends on the Instrument Kind. See [Default Aggregators](./sdk.md#default-aggregators).

\[2\]: Language implementation may choose best strategy for handling errors. (i.e. Logged, Discard, etc...)

This Aggregator reports on:

- The arithmetic sum of `Measurement` values.

### Explicit Bucket Histogram Aggregator

The Explicit Bucket Histogram Aggregator collect data for the
[Histogram Metric Point](./datamodel.md#histogram). It supports a set of
explicit boundary values for histogram bucketing.

This Aggregator honors the following configuration parameter keys:

| Key | Value | Default | Description |
| --- | --- | --- | --- |
| Monotonic | boolean | true | if true, non-positive values are treated as errors<sup>1</sup>. |
| Temporality | Delta, Cummulative | Delta | See [Temporality](./datamodel.md#temporality). |
| Boundaries | double\[\] | Default<sup>2</sup> | Array of increasing values representing explicit bucket boundary values. |

\[1\]: Language implementation may choose best strategy for handling errors. (i.e. Logged, Discard, etc...)

\[2\]: Default Bucket Boundaries: (-&infin;, 0], (0, 5.0], (5.0, 10.0], (10.0, 25.0], (25.0, 50.0], (50.0, 75.0], (75.0, 100.0], (100.0, 250.0], (250.0, 500.0], (500.0, 1000.0], (1000.0, +&infin;)

This Aggregator reports on:

- Count of `Measurement` values falling within explicit bucket boundaries.
- Arithmetic sum of `Measurement` values in population.

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
