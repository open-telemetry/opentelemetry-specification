# Metric `LabelSet` specification

Introduce a first-class `LabelSet` API type as a handle on a pre-defined set of labels for the Metrics API.

## Motivation

Labels are the term for key-value pairs used in the OpenTelemetry Metrics API.  Treatment of labels in the Metrics API is especially important for performance across a variety of export strategies.

Label serialization is often one of the most expensive tasks when processing metric events. Creating a `LabelSet` once and re-using it many times can greatly reduce the overall cost of processing many events.

The Metrics API supports three calling conventions: the Handle convention, the Direct convention, and the Batch convention. Each of these conventions stands to benefit when a `LabelSet` is re-used, as it allows the SDK to process the label set once instead of once per call.  Whenever more than one handle will be created with the same labels, more than one instrument will be called directly with the same labels, or more than one batch of metric events will be recorded with the same labels, re-using a `LabelSet` makes it possible for the SDK to improve performance.

## Explanation

Metric instrument APIs which presently take labels in the form `{ Key: Value, ... }` will be updated to take an explicit `LabelSet`.  The `Meter.Labels()` API method supports getting a `LabelSet` from the API, allowing the programmer to acquire a pre-defined label set.  Here are several examples of `LabelSet` re-use.  Assume we have two instruments:

```golang
var (
    cumulative = metric.NewFloat64Cumulative("my_counter")
    gauge      = metric.NewFloat64Gauge("my_gauge")
)
```

Use a `LabelSet` to construct multiple Handles:

```golang
var (
    labels  = meter.Labels({ "required_key1": value1, "required_key2": value2 })
    chandle = cumulative.GetHandle(labels)
    ghandle = gauge.GetHandle(labels)
)
for ... {
   // ...
   chandle.Add(...)
   ghandle.Set(...)
}
```

Use a `LabelSet` to make multiple Direct calls:

```golang
labels := meter.Labels({ "required_key1": value1, "required_key2": value2 })
cumulative.Add(quantity, labels)
gauge.Set(quantity, labels)
```

Of course, repeated calls to `Meter.RecordBatch()` could re-use a `LabelSet` as well.

### Ordered `LabelSet` option

As a language-level decision, APIs may support _ordered_ LabelSet
construction, in which a pre-defined set of ordered label keys is
defined such that values can be supplied in order.  This allows a
faster code path to construct the `LabelSet`.  For example,

```golang

var rpcLabelKeys = meter.OrderedLabelKeys("a", "b", "c")

for _, input := range stream {
    labels := rpcLabelKeys.Values(1, 2, 3)  // a=1, b=2, c=3

    // ...
}
```

This is specified as a language-optional feature because its safety,
and therefore its value as an input for monitoring, depends on the
availability of type-checking in the source language.  Passing
unordered labels (i.e., a list of bound keys and values) to
`Meter.Labels(...)` is considered the safer alternative.

### Interaction with "Named" Meters

LabelSet values may be used with any named Meter originating from the
same Meter provider.  That is, LabelSets acquired through a named
Meter may be used by any Meter from the same Meter provider.

## Internal details

Metric SDKs that do not or cannot take advantage of the LabelSet optimizations are not especially burdened by having to support these APIs.  It is trivial to supply an implementation of `LabelSet` that simply stores a list of labels.  This may not be acceptable in performance-critical applications, but this is the common case in many metrics and diagnostics APIs today.

## Trade-offs and mitigations

In languages where overloading is a standard convenience, the metrics API may elect to offer alternate forms that elide the call to `Meter.Labels()`, for example:

```
instrument.GetHandle({ Key: Value, ... })
```

as opposed to this:

```
instrument.GetHandle(meter.Labels({ Key: Value, ... }))
```

A key distinction between `LabelSet` and similar concepts in existing metrics libraries is that it is a _write-only_ structure.  `LabelSet` allows the developer to input metric labels without being able to read them back.  This avoids forcing the SDK to retain a reference to memory that is not required.

## Prior art and alternatives

Some existing metrics APIs support this concept.  For example, see `Scope` in the [Tally metric API for Go](https://godoc.org/github.com/uber-go/tally#Scope).

Some libraries take `LabelSet` one step further.  In the future, we may add to the the `LabelSet` API a method to extend the label set with additional labels.  For example:

```
serviceLabels := meter.Labels({ "k1": "v1", "k2": "v2" })
// ...
requestLabels := serviceLabels.With({ "k3": "v3", "k4": "v4" })
```
