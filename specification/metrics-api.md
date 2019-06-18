# Metrics API

Metrics API allows to report raw measurements as well as metrics with the known
aggregation and labels.

Main class that is used to work with Metrics API is called `Meter`. It is used
to construct `Measure`s and `Metric`s.

## Meter

### Meter creation

TODO: follow the spec for the Tracer

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
used.

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



## Measure

Measure is a 

### Creating of Measure

`Measure` can be created