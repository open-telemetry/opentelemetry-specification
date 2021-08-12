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
* [Attribute Limits](#attribute-limits)
* [MeasurementProcessor](#measurementprocessor)
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
[MetricExporters](#metricexporter) and [`Views`](#view)) MUST be managed solely
by the `MeterProvider` and the SDK MUST provide a way to configure all options
that are implemented by the SDK. This MAY be done at the time of MeterProvider
creation if appropriate.

The `MeterProvider` MAY provide methods to update the configuration. If
configuration is updated (e.g., adding a `MeasurementProcessor`), the updated
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

## Attribute Limits

Attributes which belong to Metrics are exempt from the
[common rules of attribute limits](../common/common.md#attribute-limits) at this
time. Attribute truncation or deletion could affect identitity of metric time
series and it requires further analysis.

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

## MetricExporter

`MetricExporter` defines the interface that protocol-specific exporters MUST
implement so that they can be plugged into OpenTelemetry SDK and support sending
of telemetry data.

The goal of the interface is to minimize burden of implementation for
protocol-dependent telemetry exporters. The protocol exporter is expected to be
primarily a simple telemetry data encoder and transmitter.

The following diagram shows `MetricExporter`'s relationship to other components
in the SDK:

```text
+-----------------+            +-----------------------+
|                 | Metrics... |                       |
| In-memory state +------------> MetricExporter (push) +--> Another process
|                 |            |                       |
+-----------------+            +-----------------------+

+-----------------+            +-----------------------+
|                 | Metrics... |                       |
| In-memory state +------------> MetricExporter (pull) +--> Another process (scraper)
|                 |            |                       |
+-----------------+            +-----------------------+
```

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

### Interface Definition

`MetricExporter` must support the following functions:

#### Export(batch)

Exports a batch of `Metrics`. Protocol exporters that will implement this
function are typically expected to serialize and transmit the data to the
destination.

`Export` will never be called concurrently for the same exporter instance.
`Export` can be called again only after the current call returns.

`Export` MUST NOT block indefinitely, there MUST be a reasonable upper limit
after which the call must time out with an error result (Failure).

Any retry logic that is required by the exporter is the responsibility of the
exporter. The default SDK SHOULD NOT implement retry logic, as the required
logic is likely to depend heavily on the specific protocol and backend the spans
are being sent to.

Individual language clients can decide how to associate
[Resource](../resource/sdk.md) with `Metrics`. Refer to the [tracing SDK
specfication](../trace/sdk.md#additional-span-interfaces) for more information.

**Parameters:**

`batch` - a batch of `Metrics`. The exact data type of the batch is language
specific, typically it is some kind of list.

Returns: `ExportResult`

`ExportResult` is one of:

* `Success` - The batch has been successfully exported. For protocol exporters
  this typically means that the data is sent over the wire and delivered to the
  destination server.
* `Failure` - exporting failed. The batch must be dropped. For example, this can
  happen when the batch contains bad data and cannot be serialized.

Note: this result may be returned via an async mechanism or a callback, if that
is idiomatic for the language implementation.

#### ForceFlush()

This is a hint to ensure that the export of any `Metrics` the exporter has
received prior to the call to `ForceFlush` SHOULD be completed as soon as
possible, preferably before returning from this method.

`ForceFlush` SHOULD provide a way to let the caller know whether it succeeded,
failed or timed out.

`ForceFlush` SHOULD only be called in cases where it is absolutely necessary,
such as when using some FaaS providers that may suspend the process after an
invocation, but before the exporter exports the completed spans.

`ForceFlush` SHOULD complete or abort within some timeout. `ForceFlush` can be
implemented as a blocking API or an asynchronous API which notifies the caller
via a callback or an event. OpenTelemetry client authors can decide if they want
to make the flush timeout configurable.

#### Shutdown()

Shuts down the exporter. Called when SDK is shut down. This is an opportunity
for exporter to do any cleanup required.

Shutdown should be called only once for each `MetricExporter` instance. After
the call to `Shutdown` subsequent calls to `MetricExporter` are not allowed and
should return a Failure result.

`Shutdown` should not block indefinitely (e.g. if it attempts to flush the data
and the destination is unavailable). OpenTelemetry client authors can decide if
they want to make the shutdown timeout configurable.

### Push Metric Exporter

Push Metric Exporter sends the data on its own schedule. Here are some examples:

* Sends the data based on a user configured schedule, e.g. every 1 minute.
* Sends the data when there is a severe error.

### Pull Metric Exporter

Pull Metric Exporter reacts to the metrics scrapers and reports the data
passively. This pattern has been widely adopted by
[Prometheus](https://prometheus.io/).

Pull Metric Exporter SHOULD always return immediately with an indication of
failure when `ForceFlush` is called.
