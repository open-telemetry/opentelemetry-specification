# Metric Handle API specification

Specify the behavior of the Metrics API "Handle" type, for efficient repeated-use of metric instruments.

## Motivation

The specification currently names this concept "TimeSeries", the type returned by `GetOrCreateTimeseries`, which supports binding a metric to a pre-defined set of labels for repeated use.  This proposal renames these "Handle" and `GetHandle`, respectively, and adds further detail to the API specification for handles.  

## Explanation

The `TimeSeries` is referred to as a "Handle", as the former name suggests an implementation, not an API concept. "Handle", we feel, is more descriptive of the intended use.  Likewise with `GetOrCreateTimeSeries` to `GetHandle` and `GetDefaultTimeSeries` to `GetDefaultHandle`, these names suggest an implementation and not the intended use.

Applications are encouraged to re-use metric handles for efficiency.

Handles are useful to reduce the cost of repeatedly recording a metric instrument (cumulative, gauge, or measure) with a pre-defined set of label values.

`GetHandle` gets a new handle given a [`LabelSet`](./0049-metric-label-set.md).

As a language-optional feature, the API may provide an _ordered_ form of the API for supplying labels in known order.  The ordered label-value API is provided as a (language-optional) potential optimization that facilitates a simple lookup for the SDK.  In this ordered-value form, the API is permitted to throw an exception or return an error when there is a mismatch in the arguments to `GetHandle`, although languages without strong type-checking may wish to omit this feature.  When label values are accepted in any order, SDKs may be forced to canonicalize the labels in order to find an existing metrics handle, but they must not throw exceptions.

`GetHandle` supports arbitrary label sets.  There is no requirement that the LabelSet used to construct a handle covers the recommended aggregation keys of a metric instrument.

## Internal details

Because each of the metric kinds supports a different operation (`Add()`, `Set()`, and `Record()`), there are logically distinct kinds of handle.  The names of the distinct handle types should reflect their instrument kind.

The names (`Handle`, `GetHandle`, ...) are just language-neutral recommendations.  Language APIs should feel free to choose type and method names with attention to the language's style.

### Metric `Attachment` support

OpenCensus has the notion of a metric attachment, allowing the application to include additional information associated with the event, for sampling purposes.  Any label value not used for aggregation may be used as a sample "attachment", including the OpenTelemetry span context, to associate sample trace context with exported metrics.

## Issues addressed

[Agreements reached on handles and naming in the working group convened on 8/21/2019](https://docs.google.com/document/d/1d0afxe3J6bQT-I6UbRXeIYNcTIyBQv4axfjKF4yvAPA/edit#).

[`record` should take a generic `Attachment` class instead of having tracing dependency](https://github.com/open-telemetry/opentelemetry-specification/issues/144)
