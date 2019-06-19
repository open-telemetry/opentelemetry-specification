# Metrics API

Metrics API allows to report raw measurements as well as metrics with the known
aggregation and labels.

Main class that is used to work with Metrics API is called `Meter`. It is used
to construct `Measure`s and `Metric`s.

## Meter

### Meter creation

TODO: follow the spec for the Tracer. See work in progress: https://github.com/open-telemetry/opentelemetry-specification/issues/39

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
aggregating these values into the `Metric`. Measure is constructed from the
Meter class, see [Create Measure](#create-measure) section, by providing set of
`Measure` identifiers.

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

Work in progress...
