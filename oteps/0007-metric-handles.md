# Metric Handle API specification

**Status:** `proposed`

Specify the behavior of the Metrics API `Handle` type, for efficient repeated-use of metric instruments.

## Motivation

The specification currently names this concept `TimeSeries`, the object returned by `GetOrCreateTimeseries`, which supports binding a metric to a pre-defined set of labels for repeated use.  This proposal renames these `Handle` and `GetHandle`, respectively, and adds further detail to the API specification for handles.  

## Explanation

The `TimeSeries` is renamed to `Handle` as the former name suggests an implementation, not an API concept. `Handle`, we feel, is more descriptive of the intended use.  Likewise with `GetOrCreateTimeSeries` to `GetHandle` and `GetDefaultTimeSeries` to `GetDefaultHandle`, these names suggest an implementation and not the intended use.

Applications are encouraged to re-use metric handles for efficiency.

Handles are useful to reduce the cost of repeatedly recording a metric instrument (cumulative, gauge, or measure) with a pre-defined set of label values.  All metric kinds support declaring a set of required label keys.  These label keys, by definition, must be specified in every metric `Handle`.  We permit "unspecified" label values in cases where a handle is requested but a value was not provided.  The default metric handle has all its required keys unspecified.  We presume that fast pre-aggregation of metrics data is only possible, in general, when the pre-aggregation keys are a subset of the required keys on the metric.

`GetHandle` specifies two calling patterns that may be supported: one with ordered label values and one without.  The facility for ordered label values is provided as a potential optimization that facilitates a simple lookup for the SDK; in this form, the API is permitted to thrown an exception or return an error when there is a mismatch in the arguments to `GetHandle`.  When label values are accepted in any order, some SDKs may perform an expensive lookup to find an existing metrics handle, but they must not throw exceptions.

`GetHandle` and `GetDefaultHandle` support additional label values not required in the definition of the metric instrument.  These optional labels act the same as pre-defined labels in the low-level metrics data representation, only that they are not required.  Some SDKs may elect to use additional label values as the "attachment" data on metrics.

## Internal details

The names (`Handle`, `GetHandle`, ...) are just language-neutral recommendations.  Because each of the metric kinds supports a different operation (`Add()`, `Set()`, and `Record()`), there are logically distinct kinds of handle.  Language APIs should feel free to choose type and method names with attention to the language's style.

An implementation of `GetHandle` may elect to return a unique object to multiple callers for its own purposes, but implementations are not required to do so.  When unique objects are a guarantee, implementation should consider additional label values in the uniqueness of the handle, to maintain the low-level metric event respresentation discussed in RFC [0003-measure-metric-type](./0003-measure-metric-tuype.md).

The `Observer` API for observing gauge metrics on demand via a callback does not support handles.

## Trade-offs and mitigations

The addition of additional label values, for handles, is not essential for pre-aggregation purposes, so it may be seen as non-essential in that regard.  However, API support for pre-defined labels also benefits program readability because it allows metric handles to be defined once in the source, rather than once per call site.

This benefit could be extended even further, as a potential future improvement. Instead of creating one handle per instance of a metric with pre-defined values, it may be even more efficient to support pre-defining a set of label values for use constructing multiple metric handles.  Consider the code for declaring three metrics:

```
  var gauge = metric.NewFloat64Gauge("example.com/gauge", metric.WithKeys("a", "b", "c"))
  var counter = metric.NewFloat64Cumulative("example.com/counter", metric.WithKeys("a", "b", "c"))
  var measure = metric.NewFloat64Measure("example.com/measure", metric.WithKeys("a", "b", "c"))
```

and three handles:

```
  gaugeHandle := gauge.GetHandleOrdered(1, 2, 3)      // values for a, b, c
  counterHandle := counter.GetHandleOrdered(1, 2, 3)  // values for a, b, c
  measureHandle := measure.GetHandleOrdered(1, 2, 3)  // values for a, b, c
```

This can be potentially improved as by making the label map a first-class concept.  This has the potential to further reduce the cost of getting a group of handles with the same map of labels:

```
  var commonKeys = metric.DefineKeys("a", "b", "c")
  var gauge = metric.NewFloat64Gauge("example.com/gauge", metric.WithKeys(commonKeys))
  var counter = metric.NewFloat64Cumulative("example.com/counter", metric.WithKeys(commonKeys))
  var measure = metric.NewFloat64Measure("example.com/measure", metric.WithKeys(commonKeys))

  labelMap := commonKeys.Values(1, 2, 3)  // values for a, b, c
  gaugeHandle := gauge.GetHandle(labelMap)
  counterHandle := counter.GetHandle(labelMap)
  measureHandle := measure.GetHandle(labelMap)
```

## Open questions

Should the additional scope concept shown above be implemented?

### Metric `Attachment` support

OpenCensus has the notion of a metric attachment, allowing the application to include additional information associated with the event, for sampling purposes.  The position taken here is that additional label values on the metric handle (specified here) or the context are a suitable replacement.

## Issues addressed

[Agreements reached on handles and naming in the working group convened on 8/21/2019](https://docs.google.com/document/d/1d0afxe3J6bQT-I6UbRXeIYNcTIyBQv4axfjKF4yvAPA/edit#).

[`record` should take a generic `Attachment` class instead of having tracing dependency](https://github.com/open-telemetry/opentelemetry-specification/issues/144)

