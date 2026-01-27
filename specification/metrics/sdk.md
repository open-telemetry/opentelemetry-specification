<!--- Hugo front matter used to generate the website version of this page:
linkTitle: SDK
weight: 3
--->

# Metrics SDK

**Status**: [Mixed](../document-status.md)

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [MeterProvider](#meterprovider)
  * [MeterProvider Creation](#meterprovider-creation)
  * [Meter Creation](#meter-creation)
  * [Configuration](#configuration)
    + [MeterConfigurator](#meterconfigurator)
  * [Shutdown](#shutdown)
  * [ForceFlush](#forceflush)
  * [View](#view)
    + [Instrument selection criteria](#instrument-selection-criteria)
    + [Stream configuration](#stream-configuration)
    + [Measurement processing](#measurement-processing)
    + [View examples](#view-examples)
  * [Aggregation](#aggregation)
    + [Drop Aggregation](#drop-aggregation)
    + [Default Aggregation](#default-aggregation)
    + [Sum Aggregation](#sum-aggregation)
    + [Last Value Aggregation](#last-value-aggregation)
    + [Histogram Aggregations](#histogram-aggregations)
      - [Explicit Bucket Histogram Aggregation](#explicit-bucket-histogram-aggregation)
      - [Base2 Exponential Bucket Histogram Aggregation](#base2-exponential-bucket-histogram-aggregation)
        * [Handle all normal values](#handle-all-normal-values)
        * [Support a minimum and maximum scale](#support-a-minimum-and-maximum-scale)
        * [Use the maximum scale for single measurements](#use-the-maximum-scale-for-single-measurements)
        * [Maintain the ideal scale](#maintain-the-ideal-scale)
  * [Observations inside asynchronous callbacks](#observations-inside-asynchronous-callbacks)
  * [Start timestamps](#start-timestamps)
  * [Cardinality limits](#cardinality-limits)
    + [Configuration](#configuration-1)
    + [Overflow attribute](#overflow-attribute)
    + [Synchronous instrument cardinality limits](#synchronous-instrument-cardinality-limits)
    + [Asynchronous instrument cardinality limits](#asynchronous-instrument-cardinality-limits)
- [Meter](#meter)
  * [MeterConfig](#meterconfig)
  * [Duplicate instrument registration](#duplicate-instrument-registration)
    + [Name conflict](#name-conflict)
  * [Instrument name](#instrument-name)
  * [Instrument unit](#instrument-unit)
  * [Instrument description](#instrument-description)
  * [Instrument advisory parameters](#instrument-advisory-parameters)
    + [Instrument advisory parameter: `ExplicitBucketBoundaries`](#instrument-advisory-parameter-explicitbucketboundaries)
    + [Instrument advisory parameter: `Attributes`](#instrument-advisory-parameter-attributes)
  * [Instrument enabled](#instrument-enabled)
- [Attribute limits](#attribute-limits)
- [Exemplar](#exemplar)
  * [ExemplarFilter](#exemplarfilter)
    + [AlwaysOn](#alwayson)
    + [AlwaysOff](#alwaysoff)
    + [TraceBased](#tracebased)
  * [ExemplarReservoir](#exemplarreservoir)
  * [Exemplar defaults](#exemplar-defaults)
    + [SimpleFixedSizeExemplarReservoir](#simplefixedsizeexemplarreservoir)
    + [AlignedHistogramBucketExemplarReservoir](#alignedhistogrambucketexemplarreservoir)
  * [Custom ExemplarReservoir](#custom-exemplarreservoir)
- [MetricReader](#metricreader)
  * [MetricReader operations](#metricreader-operations)
    + [Collect](#collect)
    + [Shutdown](#shutdown-1)
  * [Periodic exporting MetricReader](#periodic-exporting-metricreader)
    + [ForceFlush](#forceflush-1)
- [MetricExporter](#metricexporter)
  * [Push Metric Exporter](#push-metric-exporter)
    + [Interface Definition](#interface-definition)
      - [Export(batch)](#exportbatch)
      - [ForceFlush](#forceflush-2)
      - [Shutdown](#shutdown-2)
  * [Pull Metric Exporter](#pull-metric-exporter)
- [MetricProducer](#metricproducer)
  * [Interface Definition](#interface-definition-1)
    + [Produce batch](#produce-batch)
- [MetricFilter](#metricfilter)
  * [Interface Definition](#interface-definition-2)
    + [TestMetric](#testmetric)
    + [TestAttributes](#testattributes)
- [Defaults and configuration](#defaults-and-configuration)
- [Numerical limits handling](#numerical-limits-handling)
- [Compatibility requirements](#compatibility-requirements)
- [Concurrency requirements](#concurrency-requirements)
- [References](#references)

<!-- tocstop -->

</details>

Users of OpenTelemetry need a way for instrumentation interactions with the
OpenTelemetry API to actually produce telemetry. The OpenTelemetry SDK
(henceforth referred to as the SDK) is an implementation of the OpenTelemetry
API that provides users with this functionally.

All language implementations of OpenTelemetry MUST provide an SDK.

## MeterProvider

**Status**: [Stable](../document-status.md)

A `MeterProvider` MUST provide a way to allow a [Resource](../resource/sdk.md) to
be specified. If a `Resource` is specified, it SHOULD be associated with all the
metrics produced by any `Meter` from the `MeterProvider`. The [tracing SDK
specification](../trace/sdk.md#additional-span-interfaces) has provided some
suggestions regarding how to implement this efficiently.

### MeterProvider Creation

The SDK SHOULD allow the creation of multiple independent `MeterProvider`s.

### Meter Creation

It SHOULD only be possible to create `Meter` instances through a `MeterProvider`
(see [API](./api.md#meterprovider)).

The `MeterProvider` MUST implement the [Get a Meter API](api.md#get-a-meter).

The input provided by the user MUST be used to create
an [`InstrumentationScope`](../common/instrumentation-scope.md) instance which
is stored on the created `Meter`.

In the case where an invalid `name` (null or empty string) is specified, a
working Meter MUST be returned as a fallback rather than returning null or
throwing an exception, its `name` SHOULD keep the original invalid value, and a
message reporting that the specified value is invalid SHOULD be logged.

**Status**: [Development](../document-status.md) - The `MeterProvider` MUST
compute the relevant [MeterConfig](#meterconfig) using the
configured [MeterConfigurator](#meterconfigurator), and create
a `Meter` whose behavior conforms to that `MeterConfig`.

### Configuration

Configuration (
i.e. [MetricExporters](#metricexporter), [MetricReaders](#metricreader), [Views](#view),
and (**Development**) [MeterConfigurator](#meterconfigurator)) MUST be
owned by the `MeterProvider`. The configuration MAY be applied at the time
of `MeterProvider` creation if appropriate.

The `MeterProvider` MAY provide methods to update the configuration. If
configuration is updated (e.g., adding a `MetricReader`), the updated
configuration MUST also apply to all already returned `Meters` (i.e. it MUST NOT
matter whether a `Meter` was obtained from the `MeterProvider` before or after
the configuration change). Note: Implementation-wise, this could mean that
`Meter` instances have a reference to their `MeterProvider` and access
configuration only via this reference.

#### MeterConfigurator

**Status**: [Development](../document-status.md)

A `MeterConfigurator` is a function which computes
the [MeterConfig](#meterconfig) for a [Meter](#meter).

The function MUST accept the following parameter:

* `meter_scope`:
  The [`InstrumentationScope`](../common/instrumentation-scope.md) of
  the `Meter`.

The function MUST return the relevant `MeterConfig`, or some signal indicating
that the [default MeterConfig](#meterconfig) should be used. This signal MAY
be nil, null, empty, or an instance of the default `MeterConfig` depending on
what is idiomatic in the language.

This function is called when a `Meter` is first created, and for each
outstanding `Meter` when a `MeterProvider`'s `MeterConfigurator` is
updated (if updating is supported). Therefore, it is important that it returns
quickly.

`MeterConfigurator` is modeled as a function to maximize flexibility.
However, implementations MAY provide shorthand or helper functions to
accommodate common use cases:

* Select one or more Meters by name, with exact match or pattern matching.
* Disable one or more specific Meters.
* Disable all Meters, and selectively enable one or more specific Meters.

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
[MetricReader](#metricreader) instances that have an associated
[Push Metric Exporter](#push-metric-exporter), so they can do as much
as they could to collect and send the metrics.
Note: [Pull Metric Exporter](#pull-metric-exporter) can only send the
data when it is being asked by the scraper, so `ForceFlush` would not make much
sense.

`ForceFlush` MUST invoke `ForceFlush` on all registered
[MetricReader](#metricreader) instances that implement `ForceFlush`.

`ForceFlush` SHOULD provide a way to let the caller know whether it succeeded,
failed or timed out. `ForceFlush` SHOULD return some **ERROR** status if there
is an error condition; and if there is no error condition, it should return some
**NO ERROR** status, language implementations MAY decide how to model **ERROR**
and **NO ERROR**.

`ForceFlush` SHOULD complete or abort within some timeout. `ForceFlush` MAY be
implemented as a blocking API or an asynchronous API which notifies the caller
via a callback or an event. [OpenTelemetry SDK](../overview.md#sdk) authors MAY
decide if they want to make the flush timeout configurable.

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

The SDK MUST provide functionality for a user to create Views for a
`MeterProvider`. This functionality MUST accept as inputs the [Instrument
selection criteria](#instrument-selection-criteria) and the resulting [stream
configuration](#stream-configuration).

The SDK MUST provide the means to register Views with a `MeterProvider`.

#### Instrument selection criteria

Instrument selection criteria are the predicates that determine if a View will
be applied to an Instrument or not.

Criteria SHOULD be treated as additive. This means an Instrument has to match
_all_ the provided criteria for the View to be applied. For example, if the
criteria are _instrument name == "Foobar"_ and _instrument type is Histogram_,
it will be treated as _(instrument name == "Foobar") AND (instrument type is
Histogram)_.

The SDK MUST accept the following criteria:

* `name`: The name of the Instrument(s) to match. This `name` is evaluated to
  match an Instrument in the following manner.

  1. If the value of `name` is `*`, the criterion matches all Instruments.
  2. If the value of `name` is exactly the same as an Instrument, then the
     criterion matches that instrument.

  Additionally, the SDK MAY support wildcard pattern matching for the `name`
  criterion using the following characters.

  * A question mark (`?`): matches any single character
  * An asterisk (`*`): matches any number of any characters including none

  If wildcard pattern matching is supported, the `name` criterion will match if
  the wildcard pattern is evaluated to match the Instrument name.

  If the SDK does not support wildcards in general, it MUST still recognize the
  special single asterisk (`*`) character as matching all Instruments.

  Users can provide a `name`, but it is up to their discretion. Therefore, the
  instrument selection criteria parameter needs to be structured to accept a
  `name`, but MUST NOT obligate a user to provide one.
* `type`: The type of Instruments to match. If the value of `type` is the same
  as an Instrument's type, then the criterion matches that Instrument.

  Users can provide a `type`, but it is up to their discretion. Therefore, the
  instrument selection criteria parameter needs to be structured to accept a
  `type`, but MUST NOT obligate a user to provide one.
* `unit`: If the value of `unit` is the same as an Instrument's unit, then the
  criterion matches that Instrument.

  Users can provide a `unit`, but it is up to their discretion. Therefore, the
  instrument selection criteria parameter needs to be structured to accept a
  `unit`, but MUST NOT obligate a user to provide one.
* `meter_name`: If the value of `meter_name` is the same as the Meter that
  created an Instrument, then the criterion matches that Instrument.

  Users can provide a `meter_name`, but it is up to their discretion.
  Therefore, the instrument selection criteria parameter needs to be structured
  to accept a `meter_name`, but MUST NOT obligate a user to provide one.
* `meter_version`: If the value of `meter_version` is the same version as the
  Meter that created an Instrument, then the criterion matches that Instrument.

  Users can provide a `meter_version`, but it is up to their discretion.
  Therefore, the instrument selection criteria parameter needs to be structured
  to accept a `meter_version`, but MUST NOT obligate a user to provide one.
* `meter_schema_url`: If the value of `meter_schema_url` is the same schema URL
  as the Meter that created an Instrument, then the criterion matches that
  Instrument.

  Users can provide a `meter_schema_url`, but it is up to their discretion.
  Therefore, the instrument selection criteria parameter needs to be structured
  to accept a `meter_schema_url`, but MUST NOT obligate a user to provide one.

The SDK MAY accept additional criteria. For example, a strongly typed language
may support point type criterion (e.g. allow the users to select Instruments
based on whether the underlying number is integral or rational). Users can
provide these additional criteria the SDK accepts, but it is up to their
discretion. Therefore, the instrument selection criteria can be structured to
accept the criteria, but MUST NOT obligate a user to provide them.

#### Stream configuration

Stream configuration are the parameters that define the [metric
stream](./data-model.md#events--data-stream--timeseries) a `MeterProvider` will
use to define telemetry pipelines.

The SDK MUST accept the following stream configuration parameters:

* `name`: The metric stream name that SHOULD be used.

  In order to avoid conflicts, if a `name` is provided the View SHOULD have an
  instrument selector that selects at most one instrument. If the Instrument
  selection criteria for a View with a stream configuration `name` parameter
  can select more than one instrument (i.e. wildcards) the SDK MAY fail fast in
  accordance with initialization [error handling
  principles](../error-handling.md#basic-error-handling-principles).

  Users can provide a `name`, but it is up to their discretion. Therefore, the
  stream configuration parameter needs to be structured to accept a `name`, but
  MUST NOT obligate a user to provide one. If the user does not provide a
  `name` value, name from the Instrument the View matches MUST be used by
  default.
* `description`: The metric stream description that SHOULD be used.
  
  Users can provide a `description`, but it is up to their discretion.
  Therefore, the stream configuration parameter needs to be structured to
  accept a `description`, but MUST NOT obligate a user to provide one. If the
  user does not provide a `description` value, the description from the
  Instrument a View matches MUST be used by default.
* `attribute_keys`: This is, at a minimum, an allow-list of attribute keys for
  measurements captured in the metric stream. The allow-list contains attribute
  keys that identify the attributes that MUST be kept, and all other attributes
  MUST be ignored.

  Implementations MAY accept additional attribute filtering functionality for
  this parameter.

  Users can provide `attribute_keys`, but it is up to their discretion.
  Therefore, the stream configuration parameter needs to be structured to
  accept `attribute_keys`, but MUST NOT obligate a user to provide them.
  If the user does not provide any value, the SDK SHOULD use
  the [`Attributes`](./api.md#instrument-advisory-parameters) advisory
  parameter configured on the instrument instead. If the `Attributes`
  advisory parameter is absent, all attributes MUST be kept.

  Additionally, implementations SHOULD support configuring an exclude-list of
  attribute keys. The exclude-list contains attribute keys that identify the
  attributes that MUST be excluded, all other attributes MUST be kept. If an
  attribute key is both included and excluded, the SDK MAY fail fast in
  accordance with initialization [error handling
  principles](../error-handling.md#basic-error-handling-principles).

* `aggregation`: The name of an [aggregation](#aggregation) function to use in
  aggregating the metric stream data.

  Users can provide an `aggregation`, but it is up to their discretion.
  Therefore, the stream configuration parameter needs to be structured to
  accept an `aggregation`, but MUST NOT obligate a user to provide one. If the
  user does not provide an `aggregation` value, the `MeterProvider` MUST apply
  a [default aggregation](#default-aggregation) configurable on the basis of
  instrument type according to the [MetricReader](#metricreader) instance.
* `exemplar_reservoir`: A
  functional type that generates an exemplar reservoir a `MeterProvider` will
  use when storing exemplars. This functional type needs to be a factory or
  callback similar to aggregation selection functionality which allows
  different reservoirs to be chosen by the aggregation.

  Users can provide an `exemplar_reservoir`, but it is up to their discretion.
  Therefore, the stream configuration parameter needs to be structured to
  accept an `exemplar_reservoir`, but MUST NOT obligate a user to provide one.
  If the user does not provide an `exemplar_reservoir` value, the
  `MeterProvider` MUST apply a [default exemplar
  reservoir](#exemplar-defaults).
* `aggregation_cardinality_limit`: A positive integer value defining the
  maximum number of data points allowed to be emitted in a collection cycle by
  a single instrument. See [cardinality limits](#cardinality-limits), below.

  Users can provide an `aggregation_cardinality_limit`, but it is up to their
  discretion. Therefore, the stream configuration parameter needs to be
  structured to accept an `aggregation_cardinality_limit`, but MUST NOT
  obligate a user to provide one. If the user does not provide an
  `aggregation_cardinality_limit` value, the `MeterProvider` MUST apply the
  [default aggregation cardinality limit](#metricreader) the `MetricReader` is
  configured with.

#### Measurement processing

The SDK SHOULD use the following logic to determine how to process Measurements
made with an Instrument:

* Determine the `MeterProvider` which "owns" the Instrument.
* If the `MeterProvider` has no `View` registered, take the Instrument
    and apply the default Aggregation on the basis of instrument kind according
    to the [MetricReader](#metricreader) instance's `aggregation` property.
    [Instrument advisory parameters](#instrument-advisory-parameters), if any,
    MUST be honored.
* If the `MeterProvider` has one or more `View`(s) registered:
  * If the Instrument could match the instrument selection criteria, for each
    View:
    * Try to apply the View's stream configuration independently of any other
      Views registered for the same matching Instrument (i.e. Views are not
      merged). This may result in [conflicting metric identities](./data-model.md#opentelemetry-protocol-data-model-producer-recommendations)
      even if stream configurations specify non-overlapping properties (e.g.
      one View setting `aggregation` and another View setting `attribute_keys`,
      both leaving the stream `name` as the default configured by the
      Instrument). If applying the View results in conflicting metric identities
      the implementation SHOULD apply the View and emit a warning. If it is not
      possible to apply the View without producing semantic errors (e.g. the
      View sets an asynchronous instrument to use the [Explicit bucket
      histogram aggregation](#explicit-bucket-histogram-aggregation)) the
      implementation SHOULD emit a warning and proceed as if the View did not
      If both a View and [Instrument advisory parameters](#instrument-advisory-parameters)
      specify the same aspect of the [Stream configuration](#stream-configuration),
      the setting defined by the View MUST take precedence over the advisory parameters.
  * If the Instrument could not match with any of the registered `View`(s), the
    SDK SHOULD enable the instrument using the default aggregation and temporality.
    Users can configure match-all Views using [Drop aggregation](#drop-aggregation)
    to disable instruments by default.

#### View examples

The following are examples of an SDK's functionality to create Views for a
`MeterProvider`.

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
# Counter X will be exported as a delta sum and the default attributes
# Counter X, Histogram Y, and Gauge Z will be exported with 2 attributes (a and b)
# A warning will be emitted for conflicting metric identities on Counter X (as two Views matching that Instrument
# are configured with the same default name X) and streams from both views will be exported
meter_provider
    .add_view("X", aggregation=SumAggregation())
    .add_view("*", attribute_keys=["a", "b"]) # wildcard view matches everything, including X
    .add_metric_reader(PeriodicExportingMetricReader(ConsoleExporter()),
              temporality=lambda kind: Delta if kind in [Counter, AsyncCounter, Histogram] else Cumulative)
```

```python
# Only Counter X will be exported, with the default configuration (match-all drop aggregation does not result in
# conflicting metric identities)
meter_provider
    .add_view("X")
    .add_view("*", aggregation=DropAggregation()) # a wildcard view to disable all instruments
    .add_metric_reader(PeriodicExportingMetricReader(ConsoleExporter()))
```

### Aggregation

An `Aggregation`, as configured via the [View](./sdk.md#view),
informs the SDK on the ways and means to compute
[Aggregated Metrics](./data-model.md#opentelemetry-protocol-data-model)
from incoming Instrument [Measurements](./api.md#measurement).

Note: the term _aggregation_ is used instead of _aggregator_. It is RECOMMENDED
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

The SDK MUST provide the following `Aggregation` to support the
[Metric Points](./data-model.md#metric-points) in the
[Metrics Data Model](./data-model.md).

- [Drop](./sdk.md#drop-aggregation)
- [Default](./sdk.md#default-aggregation)
- [Sum](./sdk.md#sum-aggregation)
- [Last Value](./sdk.md#last-value-aggregation)
- [Explicit Bucket Histogram](./sdk.md#explicit-bucket-histogram-aggregation)

The SDK SHOULD provide the following `Aggregation`:

- [Base2 Exponential Bucket Histogram](./sdk.md#base2-exponential-bucket-histogram-aggregation)

#### Drop Aggregation

The Drop Aggregation informs the SDK to ignore/drop all Instrument Measurements
for this Aggregation.

This Aggregation does not have any configuration parameters.

#### Default Aggregation

The Default Aggregation informs the SDK to use the Instrument `kind` to select
an aggregation and `advisory` parameters to influence aggregation configuration
parameters (as noted in the "Selected Aggregation" column).

| Instrument Kind                                                   | Selected Aggregation                                                                                                                                                                                   |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [Counter](./api.md#counter)                                       | [Sum Aggregation](./sdk.md#sum-aggregation)                                                                                                                                                            |
| [Asynchronous Counter](./api.md#asynchronous-counter)             | [Sum Aggregation](./sdk.md#sum-aggregation)                                                                                                                                                            |
| [UpDownCounter](./api.md#updowncounter)                           | [Sum Aggregation](./sdk.md#sum-aggregation)                                                                                                                                                            |
| [Asynchronous UpDownCounter](./api.md#asynchronous-updowncounter) | [Sum Aggregation](./sdk.md#sum-aggregation)                                                                                                                                                            |
| [Gauge](./api.md#gauge)                                           | [Last Value Aggregation](./sdk.md#last-value-aggregation)                                                                                                                                              |
| [Asynchronous Gauge](./api.md#asynchronous-gauge)                 | [Last Value Aggregation](./sdk.md#last-value-aggregation)                                                                                                                                              |
| [Histogram](./api.md#histogram)                                   | [Explicit Bucket Histogram Aggregation](./sdk.md#explicit-bucket-histogram-aggregation), with the `ExplicitBucketBoundaries` [advisory parameter](./api.md#instrument-advisory-parameters) if provided |

This Aggregation does not have any configuration parameters.

#### Sum Aggregation

The Sum Aggregation informs the SDK to collect data for the
[Sum Metric Point](./data-model.md#sums).

The monotonicity of the aggregation is determined by the instrument type:

| Instrument Kind                                                   | `SumType`     |
|-------------------------------------------------------------------|---------------|
| [Counter](./api.md#counter)                                       | Monotonic     |
| [UpDownCounter](./api.md#updowncounter)                           | Non-Monotonic |
| [Histogram](./api.md#histogram)                                   | Monotonic     |
| [Gauge](./api.md#gauge)                                           | Non-Monotonic |
| [Asynchronous Gauge](./api.md#asynchronous-gauge)                 | Non-Monotonic |
| [Asynchronous Counter](./api.md#asynchronous-counter)             | Monotonic     |
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
| Boundaries | double\[\] | [ 0, 5, 10, 25, 50, 75, 100, 250, 500, 750, 1000, 2500, 5000, 7500, 10000 ] | Array of increasing values representing explicit bucket boundary values.<br><br>The Default Value represents the following buckets (heavily influenced by the default buckets of Prometheus clients, e.g. [Java](https://github.com/prometheus/client_java/blob/6730f3e32199d6bf0e963b306ff69ef08ac5b178/simpleclient/src/main/java/io/prometheus/client/Histogram.java#L88) and [Go](https://github.com/prometheus/client_golang/blob/83d56b1144a0c2eb10d399e7abbae3333bebc463/prometheus/histogram.go#L68)):<br>(-&infin;, 0], (0, 5.0], (5.0, 10.0], (10.0, 25.0], (25.0, 50.0], (50.0, 75.0], (75.0, 100.0], (100.0, 250.0], (250.0, 500.0], (500.0, 750.0], (750.0, 1000.0], (1000.0, 2500.0], (2500.0, 5000.0], (5000.0, 7500.0], (7500.0, 10000.0], (10000.0, +&infin;). SDKs SHOULD use the default value when boundaries are not explicitly provided, unless they have good reasons to use something different (e.g. for backward compatibility reasons in a stable SDK release). |
| RecordMinMax | true, false | true | Whether to record min and max. |

Explicit buckets are stated in terms of their upper boundary.  Buckets
are exclusive of their lower boundary and inclusive of their upper
bound (except at positive infinity).  A measurement is defined to fall
into the greatest-numbered bucket with boundary that is greater than
or equal to the measurement.

##### Base2 Exponential Bucket Histogram Aggregation

The Base2 Exponential Histogram Aggregation informs the SDK to collect data
for the [Exponential Histogram Metric
Point](./data-model.md#exponentialhistogram), which uses a base-2 exponential
formula to determine bucket boundaries and an integer `scale`
parameter to control resolution. Implementations adjust scale as necessary given
the data.

This Aggregation honors the following configuration parameters:

| Key          | Value       | Default Value | Description                                                                                                  |
|--------------|-------------|---------------|--------------------------------------------------------------------------------------------------------------|
| MaxSize      | integer     | 160           | Maximum number of buckets in each of the positive and negative ranges, not counting the special zero bucket. |
| MaxScale     | integer     | 20            | Maximum `scale` factor.                                                                                      |
| RecordMinMax | true, false | true          | Whether to record min and max.                                                                               |

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

1. The `MaxScale` (see configuration parameters), generally used for
   single-value histogram Aggregations where scale is not otherwise constrained.
2. The largest value of scale such that no more than the maximum number of
   buckets are needed to represent the full range of input data in either of the
   positive or negative ranges.

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
parameters that the automatic scale parameter will not exceed. The maximum scale
is defined by the `MaxScale` configuration parameter.

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

The implementation SHOULD disregard the use of asynchronous instrument
APIs outside of registered callbacks.

The implementation SHOULD use a timeout to prevent indefinite callback
execution.

The implementation MUST complete the execution of all callbacks for a
given instrument before starting a subsequent round of collection.

The implementation SHOULD NOT produce aggregated metric data for a
previously-observed attribute set which is not observed during a successful
callback. See [MetricReader](#metricreader) for more details on the persistence
of metrics across successive collections.

### Start timestamps

**Status**: [Development](../document-status.md)

The start timestamp for a timeseries is the timestamp which best represents
the first possible moment a measurement for this timeseries could have been
recorded.

For delta aggregations, the start timestamp MUST equal the previous collection
interval's timestamp, or the creation time of the instrument if this is the
first collection interval for the instrument. This implies that all delta
aggregations for an instrument MUST share the same start timestamp.

Cumulative aggregations for synchronous instruments MUST use the time of the
first measurement for each attribute set as the start time. Cumulative
aggregations for asynchronous instruments MUST use the previous collection
interval's timestamp, or the creation time of the instrument if this is the
first collection interval for the instrument, when the instrument records a
measurement for an attribute set it has no record of. To do this, the SDK MUST
track the start timestamp for each unique attribute set of cumulative
aggregations. All cumulative timeseries MUST use the initial start timestamp in
subsequent collection intervals.

### Cardinality limits

**Status**: [Stable](../document-status.md)

SDKs SHOULD support being configured with a cardinality limit. The number of
unique combinations of attributes is called cardinality. For a given metric, the
cardinality limit is a hard limit on the number of [Metric
Points](./data-model.md#metric-points) that can be collected during a collection
cycle. Cardinality limit enforcement SHOULD occur _after_ attribute filtering,
if any. This ensures users can filter undesired attributes using [views](#view)
and prevent reaching the cardinality limit.

#### Configuration

The cardinality limit for an aggregation is defined in one of three ways:

1. A [view](#view) with criteria matching the instrument an aggregation is
   created for has an `aggregation_cardinality_limit` value defined for the
   stream, that value SHOULD be used.
2. If there is no matching view, but the `MetricReader` defines a default
   cardinality limit value based on the instrument an aggregation is created
   for, that value SHOULD be used.
3. If none of the previous values are defined, the default value of 2000 SHOULD
   be used.

#### Overflow attribute

An overflow attribute set is defined, containing a single attribute
`otel.metric.overflow` having (boolean) value `true`, which is used to report a
synthetic aggregation of the [Measurements](./api.md#measurement) that could not
be independently aggregated because of the limit.

The SDK MUST create an Aggregator with the overflow attribute set prior to
reaching the cardinality limit and use it to aggregate
[Measurements](./api.md#measurement) for which the correct Aggregator could not
be created.  The SDK MUST provide the guarantee that overflow would not happen
if the maximum number of distinct, non-overflow attribute sets is less than or
equal to the limit.

#### Synchronous instrument cardinality limits

Aggregators for synchronous instruments with cumulative temporality MUST
continue to export all attribute sets that were observed prior to the beginning
of overflow.  [Measurements](./api.md#measurement) corresponding with attribute
sets that were not observed prior to the overflow will be reflected in a single
data point described by (only) the overflow attribute.

Aggregators of synchronous instruments with delta aggregation temporality MAY
choose an arbitrary subset of attribute sets to output to maintain the stated
cardinality limit.

Regardless of aggregation temporality, the SDK MUST ensure that every
[Measurement](./api.md#measurement) is reflected in exactly one Aggregator,
which is either an Aggregator associated with the correct attribute set or an
aggregator associated with the overflow attribute set.

[Measurements](./api.md#measurement) MUST NOT be double-counted or dropped
during an overflow.

#### Asynchronous instrument cardinality limits

Aggregators of asynchronous instruments SHOULD prefer the first-observed
attributes in the callback when limiting cardinality, regardless of
temporality.

## Meter

Distinct meters MUST be treated as separate namespaces for the purposes of detecting
[duplicate instrument registrations](#duplicate-instrument-registration).

**Status**: [Development](../document-status.md) - `Meter` MUST behave
according to the [MeterConfig](#meterconfig) computed
during [Meter creation](#meter-creation). If the `MeterProvider` supports
updating the [MeterConfigurator](#meterconfigurator), then upon update
the `Meter` MUST be updated to behave according to the new `MeterConfig`.

### MeterConfig

**Status**: [Development](../document-status.md)

A `MeterConfig` defines various configurable aspects of a `Meter`'s behavior.
It consists of the following parameters:

* `enabled`: A boolean indication of whether the Meter is enabled.

  If not explicitly set, the `enabled` parameter SHOULD default to `true` (
  i.e. `Meter`s are enabled by default).

  If a `Meter` is disabled, it MUST behave equivalently
  to [No-op Meter](./noop.md#meter).

  The value of `enabled` MUST be used to resolve whether an instrument
  is [Enabled](./api.md#enabled). See [Instrument Enabled](#instrument-enabled)
  for details.

It is not necessary for implementations to ensure that changes to any of these
parameters are immediately visible to callers of `Enabled`.
However, the changes MUST be eventually visible.

### Duplicate instrument registration

A _duplicate instrument registration_ occurs when more than one Instrument of
the same [`name`](./api.md#instrument-name-syntax) is created for identical
Meters from the same MeterProvider but they have different [identifying
fields](./api.md#instrument).

Whenever this occurs, users still need to be able to make measurements with the
duplicate instrument. This means that the Meter MUST return a functional
instrument that can be expected to export data even if this will cause
[semantic error in the data
model](data-model.md#opentelemetry-protocol-data-model-producer-recommendations).

Additionally, users need to be informed about this error. Therefore, when a
duplicate instrument registration occurs, and it is not corrected with a View,
a warning SHOULD be emitted. The emitted warning SHOULD include information for
the user on how to resolve the conflict, if possible.

1. If the potential conflict involves multiple `description`
   properties, setting the `description` through a configured View
   SHOULD avoid the warning.
2. If the potential conflict involves instruments that can be distinguished by
   a supported View selector (e.g. name, instrument kind) a renaming View
   recipe SHOULD be included in the warning.
3. Otherwise (e.g., use of multiple units), the SDK SHOULD pass through the
   data by reporting both `Metric` objects and emit a generic warning
   describing the duplicate instrument registration.

It is unspecified whether or under which conditions the same or
different Instrument instance will be returned as a result of
duplicate instrument registration. The term _identical_ applied to
Instruments describes instances where all [identifying
fields](./api.md#instrument) are equal.  The term _distinct_ applied
to Instruments describes instances where at least one field value is
different.

To accommodate [the recommendations from the data
model](data-model.md#opentelemetry-protocol-data-model-producer-recommendations),
the SDK MUST aggregate data from [identical Instruments](api.md#instrument)
together in its export pipeline.

#### Name conflict

The [`name`](./api.md#instrument-name-syntax) of an Instrument is defined to be
case-insensitive. If an SDK uses a case-sensitive encoding to represent this
`name`, a duplicate instrument registration will occur when a user passes
multiple casings of the same `name`. When this happens, the Meter MUST return
an instrument using the first-seen instrument name and log an appropriate error
as described above.

For example, if a user creates an instrument with the name `requestCount` and
then makes another request to the same `Meter` to create an instrument with the
name `RequestCount`, in both cases an instrument with the name `requestCount`
needs to be returned to the user and a log message needs to be emitted for the
second request.

### Instrument name

When a Meter creates an instrument, it SHOULD validate the instrument name
conforms to the [instrument name syntax](./api.md#instrument-name-syntax)

If the instrument name does not conform to this syntax, the Meter SHOULD emit
an error notifying the user about the invalid name. It is left unspecified if a
valid instrument is also returned.

### Instrument unit

When a Meter creates an instrument, it SHOULD NOT validate the instrument unit.
If a unit is not provided or the unit is null, the Meter MUST treat it the same
as an empty unit string.

### Instrument description

When a Meter creates an instrument, it SHOULD NOT validate the instrument
description. If a description is not provided or the description is null, the
Meter MUST treat it the same as an empty description string.

### Instrument advisory parameters

**Status**: [Stable](../document-status.md), except where otherwise specified

When a Meter creates an instrument, it SHOULD validate the instrument advisory
parameters. If an advisory parameter is not valid, the Meter SHOULD emit an error
notifying the user and proceed as if the parameter was not provided.

If multiple [identical Instruments](api.md#instrument) are created with
different advisory parameters, the Meter MUST return an instrument using the
first-seen advisory parameters and log an appropriate error as described in
[duplicate instrument registrations](#duplicate-instrument-registration).

If both a [View](#view) and advisory parameters specify the same aspect of the
[Stream configuration](#stream-configuration), the setting defined by the View
MUST take precedence over the advisory parameters.

#### Instrument advisory parameter: `ExplicitBucketBoundaries`

This advisory parameter applies when the [Explicit Bucket
Histogram](#explicit-bucket-histogram-aggregation) aggregation is used.

If a matching View specifies Explicit Bucket Histogram aggregation (with or
without bucket boundaries), the `ExplicitBucketBoundaries` advisory parameter is
ignored.

If no View matches, or if a matching View selects the [default
aggregation](#default-aggregation), the `ExplicitBucketBoundaries` advisory
parameter MUST be used. If neither is provided, the default bucket boundaries
apply.

#### Instrument advisory parameter: `Attributes`

**Status**: [Development](../document-status.md)

This advisory parameter applies to all aggregations.

`Attributes` (a list of [attribute keys](../common/README.md#attribute))
specifies the recommended set of attribute keys for measurements aggregated to
produce a metric stream.

If the user has provided attribute keys via View(s), those keys take precedence.
If no View is configured, or if a matching view does not specify attribute keys,
the advisory parameter should be used. If neither is provided, all attributes
must be retained.

### Instrument enabled

The synchronous instrument [`Enabled`](./api.md#enabled) MUST return `false`
when either:

- **Status**: [Development](../document-status.md) - The [MeterConfig](#meterconfig)
  of the `Meter` used to create the instrument has parameter `enabled=false`.
- All [resolved views](#measurement-processing) for the instrument are
  configured with the [Drop Aggregation](#drop-aggregation).

Otherwise, it SHOULD return `true`.
It MAY return `false` to support additional optimizations and features.

Note: If a user makes no configuration changes, `Enabled` returns `true` since by
default `MeterConfig.enabled=true` and instruments use the default
aggregation when no matching views match the instrument.

## Attribute limits

**Status**: [Stable](../document-status.md)

Attributes which belong to Metrics are exempt from the
[common rules of attribute limits](../common/README.md#attribute-limits) at this
time. Attribute truncation or deletion could affect identity of metric time
series and the topic requires further analysis.

## Exemplar

**Status**: [Stable](../document-status.md)

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
- The `time` when the `add` method was called.
- The `Attributes` of `{"Z": "z-value"}`, as these are not preserved in the
  resulting metric point.
- The trace/span id for the `makeRequest` span.

While the metric data point for the counter would carry the attributes `X` and
`Y`.

A Metric SDK MUST provide a mechanism to sample `Exemplar`s from measurements
via the `ExemplarFilter` and `ExemplarReservoir` hooks.

`Exemplar` sampling SHOULD be turned on by default. If `Exemplar` sampling is
off, the SDK MUST NOT have overhead related to exemplar sampling.

A Metric SDK MUST allow exemplar sampling to leverage the configuration of
metric aggregation. For example, Exemplar sampling of histograms should be able
to leverage bucket boundaries.

A Metric SDK SHOULD provide configuration for Exemplar sampling, specifically:

- `ExemplarFilter`: filter which measurements can become exemplars.
- `ExemplarReservoir`: storage and sampling of exemplars.

### ExemplarFilter

The `ExemplarFilter` configuration MUST allow users to select between one of the
built-in ExemplarFilters. While `ExemplarFilter` determines which measurements
are _eligible_ for becoming an `Exemplar`, the `ExemplarReservoir` makes the
final decision if a measurement becomes an exemplar and is stored.

The ExemplarFilter SHOULD be a configuration parameter of a `MeterProvider` for
an SDK. The default value SHOULD be `TraceBased`. The filter configuration
SHOULD follow the [environment variable specification](../configuration/sdk-environment-variables.md#exemplar).

An OpenTelemetry SDK MUST support the following filters:

- [AlwaysOn](#alwayson)
- [AlwaysOff](#alwaysoff)
- [TraceBased](#tracebased)

#### AlwaysOn

An ExemplarFilter which makes all measurements eligible for being an Exemplar.

#### AlwaysOff

An ExemplarFilter which makes no measurements eligible for being an Exemplar.
Using this ExemplarFilter is as good as disabling the Exemplar feature.

#### TraceBased

An ExemplarFilter which makes those measurements eligible for being an
Exemplar, which are recorded in the context of a sampled parent span.

### ExemplarReservoir

The `ExemplarReservoir` interface MUST provide a method to offer measurements
to the reservoir and another to collect accumulated Exemplars.

A new `ExemplarReservoir` MUST be created for every known timeseries data point,
as determined by aggregation and view configuration. This data point, and its
set of defining attributes, are referred to as the associated timeseries point.

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

The "offer" method MAY accept a filtered subset of `Attributes` which diverge
from the timeseries the reservoir is associated with. This MUST be clearly
documented in the API and the reservoir MUST be given the `Attributes`
associated with its timeseries point either at construction so that additional
sampling performed by the reservoir has access to all attributes from a
measurement in the "offer" method. SDK authors are encouraged to benchmark
whether this option works best for their implementation.

The "collect" method MUST return accumulated `Exemplar`s. Exemplars are expected
to abide by the `AggregationTemporality` of any metric point they are recorded
with. In other words, Exemplars reported against a metric data point SHOULD have
occurred within the start/stop timestamps of that point. SDKs are free to
decide whether "collect" should also reset internal storage for delta temporal
aggregation collection, or use a more optimal implementation.

`Exemplar`s MUST retain any attributes available in the measurement that
are not preserved by aggregation or view configuration for the associated
timeseries. Joining together attributes on an `Exemplar` with
those available on its associated metric data point should result in the
full set of attributes from the original sample measurement.

The `ExemplarReservoir` SHOULD avoid allocations when sampling exemplars.

### Exemplar defaults

The SDK MUST include two types of built-in exemplar reservoirs:

1. `SimpleFixedSizeExemplarReservoir`
2. `AlignedHistogramBucketExemplarReservoir`

By default:

- Explicit bucket histogram aggregation with more than 1 bucket SHOULD
use `AlignedHistogramBucketExemplarReservoir`.
- Base2 Exponential Histogram Aggregation SHOULD use a
  `SimpleFixedSizeExemplarReservoir` with a reservoir equal to the
  smaller of the maximum number of buckets configured on the aggregation or
  twenty (e.g. `min(20, max_buckets)`).
- All other aggregations SHOULD use `SimpleFixedSizeExemplarReservoir`.

Exemplar default reservoirs MAY change in
a [minor version bump](./../versioning-and-stability.md#minor-version-bump). No
guarantees are made on the shape or statistical properties of returned
exemplars.

#### SimpleFixedSizeExemplarReservoir

This reservoir MUST use a uniformly-weighted sampling algorithm based on the
number of samples the reservoir has seen so far to determine if the offered
measurements should be sampled. For example, the [simple reservoir sampling
algorithm](https://en.wikipedia.org/wiki/Reservoir_sampling) can be used:

  ```
  if num_measurements_seen < num_buckets then
    bucket = num_measurements_seen
  else
    bucket = random_integer(0, num_measurements_seen)
  end
  if bucket < num_buckets then
    reservoir[bucket] = measurement
  end
  num_measurements_seen += 1
  ```

Any stateful portion of sampling computation SHOULD be reset every collection
cycle. For the above example, that would mean that the `num_measurements_seen`
count is reset every time the reservoir is collected.

This Exemplar reservoir MAY take a configuration parameter for the size of the
reservoir. If no size configuration is provided, the default size MAY be
the number of possible concurrent threads (e.g., number of CPUs) to help reduce
contention. Otherwise, a default size of `1` SHOULD be used.

#### AlignedHistogramBucketExemplarReservoir

This Exemplar reservoir MUST take a configuration parameter that is the
configuration of a Histogram.  This implementation MUST store at most one
measurement that falls within a histogram bucket, and SHOULD use a
uniformly-weighted sampling algorithm based on the number of measurements the
bucket has seen so far to determine if the offered measurements should be
sampled. Alternatively, the implementation MAY instead keep the last seen
measurement that falls within a histogram bucket.

The reservoir will accept measurements using the equivalent of the following
naive algorithm:

  ```
  bucket = find_histogram_bucket(measurement)
  num_measurements_seen_bucket = num_measurements_seen[bucket]
  if random_integer(0, num_measurements_seen_bucket) == 0 then
    reservoir[bucket] = measurement
  end
  num_measurements_seen[bucket] += 1

  def find_histogram_bucket(measurement):
    for boundary, idx in bucket_boundaries do
      if value <= boundary then
        return idx
      end
    end
    return boundaries.length
  ```

This Exemplar reservoir MAY take a configuration parameter for the bucket
boundaries used by the reservoir. The size of the reservoir is always the
number of bucket boundaries plus one. This configuration parameter SHOULD have
the same format as specifying bucket boundaries to
[Explicit Bucket Histogram Aggregation](./sdk.md#explicit-bucket-histogram-aggregation).

### Custom ExemplarReservoir

The SDK MUST provide a mechanism for SDK users to provide their own
ExemplarReservoir implementation. This extension MUST be configurable on
a metric [View](#view), although individual reservoirs MUST still be
instantiated per metric-timeseries (see
[Exemplar Reservoir - Paragraph 2](#exemplarreservoir)).

## MetricReader

**Status**: [Stable](../document-status.md)

`MetricReader` is an SDK implementation object that provides the
common configurable aspects of the OpenTelemetry Metrics SDK and
determines the following capabilities:

* Collecting metrics from the SDK and any registered
  [MetricProducers](#metricproducer) on demand.
* Handling the [ForceFlush](#forceflush) and [Shutdown](#shutdown) signals from
  the SDK.

To construct a `MetricReader` when setting up an SDK, at least the following
SHOULD be provided:

* The `exporter` to use, which is a `MetricExporter` instance.
* The default output `aggregation` (optional), a function of instrument kind. This function SHOULD be obtained from the `exporter`. If not configured, the [default aggregation](#default-aggregation) SHOULD be used.
* The output `temporality` (optional), a function of instrument kind. This function SHOULD be obtained from the `exporter`. If not configured, the Cumulative temporality SHOULD be used.
* The default aggregation [cardinality limit](#cardinality-limits) (optional) to use, a function of instrument kind.  If not configured, a default value of 2000 SHOULD be used.
* **Status**: [Development](../document-status.md) - The [MetricFilter](#metricfilter) to apply to metrics and attributes during `MetricReader#Collect`.
* Zero of more [MetricProducer](#metricproducer)s (optional) to collect metrics from in addition to metrics from the SDK.

**Status**: [Development](../document-status.md) - A `MetricReader` SHOULD provide the [MetricFilter](#metricfilter) to the SDK or registered [MetricProducer](#metricproducer)(s)
when calling the `Produce` operation.

The [MetricReader.Collect](#collect) method allows general-purpose
`MetricExporter` instances to explicitly initiate collection, commonly
used with pull-based metrics collection.  A common implementation of
`MetricReader`, the [periodic exporting
`MetricReader`](#periodic-exporting-metricreader) SHOULD be provided to be used
typically with push-based metrics collection.

The `MetricReader` MUST ensure that data points from OpenTelemetry
[instruments](./api.md#instrument) are output in the configured aggregation
temporality for each instrument kind. For synchronous instruments with
Cumulative aggregation temporality, this means
converting [Delta to Cumulative](supplementary-guidelines.md#synchronous-example-cumulative-aggregation-temporality)
aggregation temporality. For asynchronous instruments with Delta temporality,
this means
converting [Cumulative to Delta](supplementary-guidelines.md#asynchronous-example-delta-temporality)
aggregation temporality.

The `MetricReader` is not required to ensure data points from a non-SDK
[MetricProducer](#metricproducer) are output in the configured aggregation
temporality, as these data points are not collected using OpenTelemetry
instruments.

The `MetricReader` selection of `temporality` as a function of instrument kind
influences the persistence of metric data points across collections. For
synchronous instruments with Cumulative aggregation
temporality, [MetricReader.Collect](#collect) MUST receive data points exposed
in previous collections regardless of whether new measurements have been
recorded. For synchronous instruments with Delta aggregation
temporality, [MetricReader.Collect](#collect) MUST only receive data points with
measurements recorded since the previous collection. For asynchronous
instruments with Delta or Cumulative aggregation
temporality, [MetricReader.Collect](#collect) MUST only receive data points with
measurements recorded since the previous collection. These rules apply to all
metrics, not just those whose [point kinds](./data-model.md#point-kinds)
includes an aggregation temporality field.

The `MetricReader` selection of `temporality` as a function of instrument kind
influences the starting timestamp (i.e. `StartTimeUnixNano`) of metrics data
points received by [MetricReader.Collect](#collect). For instruments with
Cumulative aggregation temporality, successive data points received by
successive calls to [MetricReader.Collect](#collect) MUST repeat the same
starting timestamps (e.g. `(T0, T1], (T0, T2], (T0, T3]`). For instruments with
Delta aggregation temporality, successive data points received by successive
calls to [MetricReader.Collect](#collect) MUST advance the starting timestamp (
e.g. `(T0, T1], (T1, T2], (T2, T3]`). The ending timestamp (i.e. `TimeUnixNano`)
MUST always be equal to time the metric data point took effect, which is equal
to when [MetricReader.Collect](#collect) was invoked. These rules apply to all
metrics, not just those whose [point kinds](./data-model.md#point-kinds) includes
an aggregation temporality field.
See [data model temporality](./data-model.md#temporality) for more details.

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

Collects the metrics from the SDK and any registered
[MetricProducers](#metricproducer). If there are
[asynchronous SDK Instruments](./api.md#asynchronous-instrument-api) involved,
their callback functions will be triggered.

`Collect` SHOULD provide a way to let the caller know whether it succeeded,
failed or timed out. When the `Collect` operation fails or times out on
some of the instruments, the SDK MAY return successfully collected results
and a failed reasons list to the caller.

`Collect` does not have any required parameters, however, [OpenTelemetry
SDK](../overview.md#sdk) authors MAY choose to add parameters (e.g. callback,
filter, timeout). [OpenTelemetry SDK](../overview.md#sdk) authors MAY choose the
return value type, or do not return anything.

`Collect` SHOULD invoke [Produce](#produce-batch) on registered
[MetricProducers](#metricproducer). If the batch of metric points from
`Produce` includes [Resource](../resource/sdk.md) information, `Collect` MAY
replace the `Resource` from the MetricProducer with the `Resource` provided
when constructing the MeterProvider instead.

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

The reader MUST synchronize calls to `MetricExporter`'s `Export`
to make sure that they are not invoked concurrently.

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

#### ForceFlush

This method provides a way for the periodic exporting MetricReader
so it can do as much as it could to collect and send the metrics.

`ForceFlush` SHOULD collect metrics, call [`Export(batch)`](#exportbatch)
and [`ForceFlush()`](#forceflush-2) on the configured
[Push Metric Exporter](#push-metric-exporter).

`ForceFlush` SHOULD provide a way to let the caller know whether it succeeded,
failed or timed out. `ForceFlush` SHOULD return some **ERROR** status if there
is an error condition; and if there is no error condition, it should return some
**NO ERROR** status, language implementations MAY decide how to model **ERROR**
and **NO ERROR**.

`ForceFlush` SHOULD complete or abort within some timeout. `ForceFlush` MAY be
implemented as a blocking API or an asynchronous API which notifies the caller
via a callback or an event.

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

The goal of the interface is to minimize the burden of implementation for
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

Exports a batch of [Metric Points](./data-model.md#metric-points). Protocol
exporters that will implement this function are typically expected to serialize
and transmit the data to the destination.

The SDK MUST provide a way for the exporter to get the [Meter](./api.md#meter)
information (e.g. name, version, etc.) associated with each `Metric Point`.

`Export` should never be called concurrently with other `Export` calls for the
same exporter instance.

`Export` MUST NOT block indefinitely, there MUST be a reasonable upper limit
after which the call must time out with an error result (Failure).

Any retry logic that is required by the exporter is the responsibility of the
exporter. The default SDK SHOULD NOT implement retry logic, as the required
logic is likely to depend heavily on the specific protocol and backend the metrics
are being sent to.

**Parameters:**

`batch` - a batch of [Metric Points](./data-model.md#metric-points). The exact
data type of the batch is language specific, typically it is some kind of list.
The exact type of `Metric Point` is language specific, and is typically
optimized for high performance. Here are some examples:

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

Refer to the [Metric Points](./data-model.md#metric-points) section from the
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

##### ForceFlush

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

##### Shutdown

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

## MetricProducer

**Status**: [Stable](../document-status.md) except where otherwise specified

`MetricProducer` defines the interface which bridges to third-party metric
sources MUST implement, so they can be plugged into an OpenTelemetry
[MetricReader](#metricreader) as a source of aggregated metric data. The SDK's
in-memory state MAY implement the `MetricProducer` interface for convenience.

`MetricProducer` implementations SHOULD accept configuration for the
`AggregationTemporality` of produced metrics. SDK authors MAY provide utility
libraries to facilitate conversion between delta and cumulative temporalities.

```text
+-----------------+            +--------------+
|                 | Metrics... |              |
| In-memory state +------------> MetricReader |
|                 |            |              |
+-----------------+            |              |
                               |              |
+-----------------+            |              |
|                 | Metrics... |              |
| MetricProducer  +------------>              |
|                 |            |              |
+-----------------+            +--------------+
```

When new OpenTelemetry integrations are added, the API is the preferred
integration point. The `MetricProducer` is only meant for integrations that
bridge pre-processed data.

### Interface Definition

A `MetricProducer` MUST support the following functions:

#### Produce batch

`Produce` provides metrics from the MetricProducer to the caller. `Produce`
MUST return a batch of [Metric Points](./data-model.md#metric-points), filtered by the optional
`metricFilter` parameter. Implementation SHOULD use the filter as early as
possible to gain as much performance gain possible (memory allocation,
internal metric fetching, etc).

If the batch of [Metric Points](./data-model.md#metric-points) includes
resource information, `Produce` SHOULD require a resource as a parameter.
`Produce` does not have any other required parameters, however, [OpenTelemetry
SDK](../overview.md#sdk) authors MAY choose to add required or optional
parameters (e.g. timeout).

`Produce` SHOULD provide a way to let the caller know whether it succeeded,
failed or timed out. When the `Produce` operation fails, the `MetricProducer`
MAY return successfully collected results and a failed reasons list to the
caller.

If a batch of [Metric Points](./data-model.md#metric-points) can include
[`InstrumentationScope`](../common/instrumentation-scope.md) information,
`Produce` SHOULD include a single InstrumentationScope which identifies the
`MetricProducer`.

**Parameters:**

**Status**: [Development](../document-status.md) `metricFilter`: An optional [MetricFilter](#metricfilter).

## MetricFilter

**Status**: [Development](../document-status.md)

`MetricFilter` defines the interface which enables the [MetricReader](#metricreader)'s
registered [MetricProducers](#metricproducer) or the SDK's [MetricProducer](#metricproducer) to filter aggregated data points
([Metric Points](./data-model.md#metric-points)) inside its `Produce` operation.
The filtering is done at the [MetricProducer](#metricproducer) for performance reasons.

The `MetricFilter` allows filtering an entire metric stream - dropping or allowing all its attribute sets -
by its `TestMetric` operation, which accepts the metric stream information
(scope, name, kind and unit)  and returns an enumeration: `Accept`, `Drop`
or `Accept_Partial`. If the latter returned, the `TestAttributes` operation
is to be called per attribute set of that metric stream, returning an enumeration
determining if the data point for that (metric stream, attributes) pair is to be
allowed in the result of the [MetricProducer](#metricproducer) `Produce` operation.

### Interface Definition

A `MetricFilter` MUST support the following functions:

#### TestMetric

This operation is called once for every metric stream, in each [MetricProducer](#metricproducer) `Produce`
operation.

**Parameters:**

- `instrumentationScope`: the metric stream instrumentation scope
- `name`: the name of the metric stream
- `kind`: the metric stream [kind](./data-model.md#point-kinds)
- `unit`: the metric stream unit

Returns: `MetricFilterResult`

`MetricFilterResult` is one of:

* `Accept` - All attributes of the given metric stream are allowed (not to be filtered).
   This provides a "short-circuit" as there is no need to call `TestAttributes` operation
   for each attribute set.
* `Drop` - All attributes of the given metric stream are NOT allowed (filtered out - dropped).
  This provides a "short-circuit" as there is no need to call `TestAttributes` operation
  for each attribute set, and no need to collect those data points be it synchronous or asynchronous:
  e.g. the callback for this given instrument does not need to be invoked.
* `Accept_Partial` - Some attributes are allowed and some aren't, hence `TestAttributes`
  operation must be called for each attribute set of that instrument.

#### TestAttributes

An operation which determines for a given metric stream and attribute set if it should be allowed
or filtered out.

This operation should only be called if `TestMetric` operation returned `Accept_Partial` for
the given metric stream arguments (`instrumentationScope`, `name`, `kind`, `unit`).

**Parameters:**

- `instrumentationScope`: the metric stream instrumentation scope
- `name`: the name of the metric stream
- `kind`: the metric stream kind
- `unit`: the metric stream unit
- `attributes`: the attributes

Returns: `AttributesFilterResult`

`AttributesFilterResult` is one of:

* `Accept` - This given `attributes` are allowed (not to be filtered).
* `Drop` - This given `attributes` are NOT allowed (filtered out - dropped).

## Defaults and configuration

The SDK MUST provide configuration according to the [SDK environment
variables](../configuration/sdk-environment-variables.md) specification.

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

**ExemplarReservoir** - all methods are safe to be called concurrently.

**MetricReader** - `Collect`, `ForceFlush` (for periodic exporting MetricReader)
and `Shutdown` are safe to be called concurrently.

**MetricExporter** - `ForceFlush` and `Shutdown` are safe to be called
concurrently.

## References

- [OTEP0113 Integrate Exemplars with Metrics](../../oteps/metrics/0113-exemplars.md)
- [OTEP0126 A Proposal For SDK Support for Configurable Batching and Aggregations (Basic Views)](../../oteps/metrics/0126-Configurable-Metric-Aggregations.md)
- [OTEP0146 Scenarios for Metrics API/SDK Prototyping](../../oteps/metrics/0146-metrics-prototype-scenarios.md)
