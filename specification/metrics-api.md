# Metrics API

<details>
<summary>
Table of Content
</summary>

- [Meter](#meater)
  - [Meter Creation](#meter-creation)
  - [Create Metric](#create-metric)
  - [Create Measure](#create-measure)
  - [Record](#record)
- [Measure](#measure)
  - [CreateDoubleMeasurement](#createdoublemeasurement)
  - [CreateLongMeasurement](#createlongmeasurement)
- [Measurement](#measurement)
- [Metric](#metric)
  - [GetOrCreateTimeSeries](#getorcreatetimeseries)
  - [GetDefaultTimeSeries](#getdefaulttimeseries)
  - [SetCallback](#setcallback)
  - [RemoveTimeSeries](#removetimeseries)
  - [Clear](#clear)
  - [Type: Counter](#type--counter)
  - [Type: Gauge](#type--gauge)

</details>

Metrics API allows to report raw measurements as well as metrics with the known
aggregation and labels.

Main class that is used to work with Metrics API is called `Meter`. It is used
to construct [`Measure`s](../terminology.md#measure) to record raw measurements
and `Metric`s to record metrics with [predefined
aggregation](../terminology.md#recording-metrics-with-predefined-aggregation).

## Meter

### Meter creation

TODO: follow the spec for the Tracer. See work in progress:
https://github.com/open-telemetry/opentelemetry-specification/issues/39

### Create Metric

`Meter` MUST expose the APIs to create a `Metric` of every supported type.
Depending on the language - builder pattern (C#, Java) or options (Go) SHOULD be
used.

`Metric` creation API requires the following argument.

Required arguments:

- name of the `Metric`.
- type of the `Metric`. This argument may be implicit from the API method name
  on `Meter` was called to create this `Metric`.

Optional arguments:

- description of the `Metric`.
- unit of the `Metric` values.
- list of keys for the labels with dynamic values. Order of the list is
  important as the same order MUST be used on recording when supplying values
  for these labels.
- set of name/value pairs for the labels with the constant values.
- component name that reports this `Metric`. See [semantic
  convention](..\semantic-conventions.md) for the examples of well-known
  components.
- resource this `Metric` is associated with.

### Create Measure

`Meter` MUST expose the API to create a `Measure` that will be used for
recording raw `Measurements`.

Depending on the language - builder pattern (C#, Java) or options (Go) SHOULD be
used. When multiple `Measure`s with the same arguments were created,
implementation may decide to return the same or distinct object. Users of API
MUST NOT set any expectations about `Measure`s being unique objects.

`Measure` creation exposes the following arguments.

Required arguments:

- name of the `Measure`.

Optional arguments:

- description of the `Measure`.
- unit of the `Measure` values.
- type of the `Measure`. Can be one of two values - `long` and `double`. Default
  type is `double`.

### Record

`Meter` provides an API to record `Measurement`s. API built with the idea that
`Measurements`s aggregation will happen asynchronously. Typical library records
multiple `Measurement`s at once. Thus API accepts the collection of
`Measurement` so library can batch all the `Measurement`s that needs to be
recorded.  

Required argument:

- Set of `Measurement` to record.

Optional parameters:

- Explicit `DistributedContext` to use instead of the current context. Context
  is used to add dimensions for the resulting `Metric` calculated out of
  `Measurements`.
- Exemplar of the measurement in a form of `SpanContext`. This exemplar may be
  used to provide an example of Spans in specific buckets when histogram
  aggregation is used.

## Measure

`Measure` is a contract between the library exposing the raw measurement and SDK
aggregating these values into the `Metric`. `Measure` is constructed from the
`Meter` class, see [Create Measure](#create-measure) section, by providing set
of `Measure` identifiers.

### CreateDoubleMeasurement

Creates a `Measurement` with the value passes as an argument. It MUST only be
called on `Measure` of a type `double`. Implementation may return no-op
`Measurement` when there are no subscribers on this `Measure`. So `Measurement`
cannot be reused and MUST be re-created.

Arguments:

Double value representing the `Measurement`.

### CreateLongMeasurement

Creates a `Measurement` with the value passes as an argument. It MUST only be
called on `Measure` of a type `long`. Implementation may return no-op
`Measurement` when there are no subscribers on this `Measure`. So `Measurement`
cannot be reused and MUST be re-created.

Arguments:

Long value representing the `Measurement`.

## Measurement

`Measurement` is an empty interface that represents a single value recorded for
the `Measure`. `Measurement` MUST be treated as immutable short lived object.
Instrumentation logic MUST NOT hold on to the object and MUST only record it
once.

## Metric

`Metric` is a base class for various types of metrics. `Metric` is specialized
with the type of a time series that `Metric` holds. `Metric` is constructed from
the `Meter` class, see [Create Metric](#create-metric) section, by providing set
of `Metric` identifiers like name and set of label keys.

### GetOrCreateTimeSeries

Creates a `TimeSeries` and returns a `TimeSeries` if the specified label values
is not already associated with this gauge, else returns an existing
`TimeSeries`.

It is recommended to keep a reference to the `TimeSeries` instead of always
calling this method for every operations.

Arguments:

- List of label values. The order and number of labels MUST match the order and
  number of label keys used when `Metric` was created.

### GetDefaultTimeSeries

Returns a `TimeSeries` for a metric with all labels not set (default label
value).

Method takes no arguments.

### SetCallback

Sets a callback that gets executed every time before exporting this metric. It
MUST be used to provide polling of a `Metric`. Callback implementation MUST set
the value of a `Metric` to the value that will be exported.

### RemoveTimeSeries

Removes the `TimeSeries` from the `Metric`, if it is present.

### Clear

Removes all `TimeSeries` from the `Metric`.

### Type: Counter

`Counter` metric aggregates instantaneous values. Cumulative values can go up or
stay the same, but can never go down. Cumulative values cannot be negative.
`TimeSeries` for the `Counter` has two methods - `add` and `set`.

- `add` adds the given value to the current value. The values cannot be
  negative.
- `set` sets the given value. The value must be larger than the current recorded
  value. In general should be used in combination with `SetCallback` where the
  recorded value is guaranteed to be monotonically increasing.

### Type: Gauge

`Gauge` metric aggregates instantaneous values. Cummulative value can go both up
and down. `Gauge` values can be negative. `TimeSeries` for the `Gauge` has two
methods - `add` and `set`.

- `add` adds the given value to the current value. The values can be negative.
- `set` sets the given value.
