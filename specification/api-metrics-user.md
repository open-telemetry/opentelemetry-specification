# Metric User-facing API

Note: This specification for the v0.2 OpenTelemetry milestone does not
cover the Observer gauge instrument discussed in the
[overview](api-metrics.md).  Observer instruments will be added in the
v0.3 milestone.

TODO: Add a table of contents.

## Overview

Metric instruments are the entry point for application and framework developers to instrument their code using counters, gauges, and measures.
Metrics are created by calling methods on a `Meter` which is in turn created by a global `MeterFactory`.

### Obtaining a Meter

New `Meter` instances can be created via a `MeterFactory` and its `getMeter` method.
`MeterFactory`s are generally expected to be used as singletons.
Implementations SHOULD provide a single global default `MeterFactory`. The `getMeter` method expects two string arguments:

- `name` (required): This name must identify the instrumentation library (also referred to as integration, e.g. `io.opentelemetry.contrib.mongodb`)
  and *not* the instrumented library.
  In case an invalid name (null or empty string) is specified, a working default `Meter` implementation as a fallback is returned
  rather than returning null or throwing an exception.
  A `MeterFactory` could also return a no-op `Meter` here if application owners configure the SDK to suppress telemetry produced by this library.
- `version` (optional): Specifies the version of the instrumentation library (e.g. `semver:1.0.0`).

### Metric names

Metric instruments have names, which are how we refer to them in
external systems.  Metric names conform to the following syntax:

1. They are non-empty strings
2. They are case-insensitive
3. The first character must be non-numeric, non-space, non-punctuation
4. Subsequent characters must be belong to the alphanumeric characters, '_', '.', and '-'.

Metric names belong to a namespace. The `name` of the associated `Meter`
serves as its namespace, allowing the same metric name to be used in
multiple libraries of code, unambiguously, within the same application.

Metric instruments are defined using a `Meter` instance, using a variety
of `New` methods specific to the kind of metric and type of input(integer
or floating point).  The Meter will return an error when a metric name is
already registered with a different kind for the same name.  Metric systems
are expected to automatically prefix exported metrics by the namespace in a
manner consistent with the target system.  For example, a Prometheus exporter
SHOULD use the namespace followed by `_` as the
[application prefix](https://prometheus.io/docs/practices/naming/#metric-names).

### Format of a metric event

Regardless of the instrument kind or method of input, metric events
include the instrument, a numerical value, and an optional
set of labels.  The instrument, discussed in detail below, contains
the metric name and various optional settings.

Labels are key:value pairs associated with events describing various
dimensions or categories that describe the event.  A "label key"
refers to the key component while "label value" refers to the
correlated value component of a label.  Label refers to the pair of
label key and value.  Labels are passed in to the metric event in the
form of a `LabelSet` argument, using several input methods discussed
below.

Metric events always have an associated component name, the name
passed when constructing the corresponding `Meter`.  Metric events are
associated with the current (implicit or explicit) OpenTelemetry
context, including distributed correlation context and span context.

### New constructors

The `Meter` interface allows creating of a registered metric
instrument using methods specific to each kind of metric.  There are
six constructors representing the three kinds of instrument taking
either floating point or integer inputs, see the detailed design below.

Binding instruments to a single `Meter` instance has two benefits:

1. Instruments can be exported from the zero state, prior to first use, with no explicit `Register` call
2. The name provided by the `Meter` satisfies a namespace requirement

The recommended practice is to define structures to contain the
instruments in use and keep references only to the instruments that
are specifically needed.

We recognize that many existing metric systems support allocating
metric instruments statically and providing the `Meter` interface at
the time of use.  In this example, typical of statsd clients, existing
code may not be structured with a convenient place to store new metric
instruments.  Where this becomes a burden, it is recommended to use
the global meter factory to construct a static `Meter`, to
construct metric instruments.

The situation is similar for users of Prometheus clients, where
instruments are allocated statically and there is an implicit global.
Such code may not have access to the appropriate `Meter` where
instruments are defined.  Where this becomes a burden, it is
recommended to use the global meter factory to construct a static
named `Meter`, to construct metric instruments.

Applications are expected to construct long-lived instruments.
Instruments are considered permanent for the lifetime of a SDK, there
is no method to delete them.

#### Metric instrument constructor example code

In this Golang example, a struct holding four instruments is built
using the provided, non-global `Meter` instance.

```golang
type instruments struct {
    counter1 metric.Int64Counter
    counter2 metric.Float64Counter
    gauge3   metric.Int64Gauge
    measure4 metric.Float64Measure
}

func newInstruments(metric.Meter meter) *instruments {
  return &instruments{
    counter1: meter.NewCounter("counter1", ...),  // Optional parameters
    counter2: meter.NewCounter("counter2", ...),  // are discussed below.
    gauge3:   meter.NewGauge("gauge3", ...),
    measure4: meter.NewMeasure("measure4", ...),
  }
}
```

Code will be structured to call `newInstruments` somewhere in a
constructor and keep the `instruments` reference for use at runtime.
Here's an example of building a server with configured instruments and
a single metric operation.

```golang
type server struct {
    meter        metric.Meter
    instruments *instruments

    // ... other fields
}

func newServer(meter metric.Meter) *server {
     return &server{
         meter:       meter,
         instruments: newInstruments(meter),
         // ... other fields
     }
}

// ...

func (s *server) operate(ctx context.Context) {
     // ... other work

     s.instruments.counter1.Add(ctx, 1, s.meter.Labels(
         label1.String("..."),
         label2.String("...")))
}
```

### Metric calling conventions

This API is factored into three core types: instruments, bound instruments,
and label sets.  In doing so, we provide several ways of capturing
measurements that are semantically equivalent and generate equivalent
metric events, but offer varying degrees of performance and
convenience.

This section applies to calling conventions for counter, gauge, and
measure instruments.

As described above, metric events consist of an instrument, a set of
labels, and a numerical value, plus associated context.  The
performance of a metric API depends on the work done to enter a new
measurement.  One approach to reduce cost is to aggregate intermediate
results in the SDK, so that subsequent events happening in the same
collection period, for the same label set, combine into the same
working memory.

In this document, the term "aggregation" is used to describe the
process of coalescing metric events for a complete set of labels,
whereas "grouping" is used to describe further coalescing aggregate
metric data into a reduced number of key dimensions.  SDKs may be
designed to perform aggregation and/or grouping in the process, with
various trade-offs in terms of complexity and performance.

#### Bound instrument calling convention

In situations where performance is a requirement and a metric instrument is
repeatedly used with the same set of labels, the developer may elect
to use the _bound instrument_ calling convention as an optimization.
For bound instruments to be a benefit, it requires that a specific
instrument will be re-used with specific labels.  If an instrument
will be used with the same label set more than once, obtaining an
bound instrument corresponding to the label set ensures the highest
performance available.

To bind an instrument and label set, use the `Bind(LabelSet)` method to
return an interface that supports the `Add()`, `Set()`, or `Record()`
method of the instrument in question.

Bound instruments may consume SDK resources indefinitely.

```golang
func (s *server) processStream(ctx context.Context) {

  streamLabels := s.meter.Labels(
      labelA.String("..."),
      labelB.String("..."),
  )
  // The result of Bind() is a bound instrument
  // (e.g., a BoundInt64Counter).
  counter2 := s.instruments.counter2.Bind(streamLabels)

  for _, item := <-s.channel {
     // ... other work

     // High-performance metric calling convention: use of bound
     // instruments.
     counter2.Add(ctx, item.size())
  }
}
```

#### Direct instrument calling convention

When convenience is more important than performance, or there is no
re-use to potentially optimize with bound instruments, users may
elect to operate directly on metric instruments, supplying a label set
at the call site.

For example, to update a single counter:

```golang
func (s *server) method(ctx context.Context) {
    // ... other work

    s.instruments.counter1.Add(ctx, 1, s.meter.Labels(...))
}
```

This method offers the greatest convenience possible.  If performance
becomes a problem, one option is to use bound instruments as described above.
Another performance option, in some cases, is to just re-use the
labels.  In the example here, `meter.Labels(...)` constructs a
re-usable label set which may be an important performance
optimization.

#### RecordBatch calling convention

There is one final API for entering measurements, which is like the
direct access calling convention but supports multiple simultaneous
measurements.  The use of a RecordBatch API supports entering multiple
measurements, implying a semantically atomic update to several
instruments.

For example:

```golang
func (s *server) method(ctx context.Context) {
    // ... other work

    labelSet := s.meter.Labels(...)

    // ... more work

    s.meter.RecordBatch(ctx, labelSet,
        s.instruments.counter1.Measurement(1),
        s.instruments.gauge1.Measurement(10),
        s.instruments.measure2.Measurement(123.45),
    )
}
```

Using the RecordBatch calling convention is semantically identical to
a sequence of direct calls, with the addition of atomicity.  Because
values are entered in a single call,
the SDK is potentially able to implement an atomic update, from the
exporter's point of view.  Calls to `RecordBatch` may potentially
reduce costs because the SDK can enqueue a single bulk update, or take
a lock only once, for example.

#### Label set re-use is encouraged

A significant factor in the cost of metrics export is that labels,
which arrive as an unordered list of keys and values, must be
canonicalized in some way before they can be used for lookup.
Canonicalizing labels can be an expensive operation as it may require
sorting or de-duplicating by some other means, possibly even
serializing, the set of labels to produce a valid map key.

The operation of converting an unordered set of labels into a
canonicalized set of labels, useful for pre-aggregation, is expensive
enough that we give it first-class treatment in the API.  The
`meter.Labels(...)` API canonicalizes labels, returning an opaque
`LabelSet` object, another form of pre-computation available to the
user.

Re-usable `LabelSet` objects provide a potential optimization for
scenarios where bound instruments might not be effective.  For example, if the
label set will be re-used but only used once per metric, bound instruments do
not offer any optimization.  It may be best to pre-compute a
canonicalized `LabelSet` once and re-use it with the direct calling
convention.

Constructing a bound instrument is considered the higher-performance
option, when the bound instrument will be used more than once.  Still, consider
re-using the result of `Meter.Labels(...)` when constructing more than
one bound instrument.

```golang
func (s *server) method(ctx context.Context) {
    // ... other work

    labelSet := s.meter.Labels(...)

    s.instruments.counter1.Add(ctx, 1, labelSet)

    // ... more work

    s.instruments.gauge1.Set(ctx, 10, labelSet)

    // ... more work

    s.instruments.measure1.Record(ctx, 100, labelSet)
}
```

##### Missing label keys

When the SDK interprets a `LabelSet` in the context of grouping
aggregated values for an exporter, and where there are keys that are
missing, the SDK is required to consider these values _explicitly
unspecified_, a distinct value type of the exported data model.

##### Option: Convenience method to bypass `meter.Labels(...)`

As a language-optional feature, the direct and bound instrument calling
convention APIs may support alternate convenience methods to pass raw
labels at the call site.  These may be offered as overloaded methods
for `Add()`, `Set()`, and `Record()` (direct calling convention) or
`Bind()` (bound instrument calling convention), in both cases bypassing a
call to `meter.Labels(...)`.  For example:

```java
  public void method() {
    // pass raw labels, no explicit `LabelSet`
    s.instruments.counter1.add(1, labelA.value(...), labelB.value(...))

    // ... or

    // pass raw labels, no explicit `LabelSet`
    BoundIntCounter counter = s.instruments.gauge1.bind(labelA, ..., labelB, ...)
    for (...) {
      counter.add(1)
    }
  }
```

##### Option: Ordered LabelSet construction

As a language-level decision, APIs may support _ordered_ LabelSet
construction, in which a pre-defined set of ordered label keys is
defined such that values can be supplied in order.  For example,

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
unordered labels (i.e., a list of bound keys and values) to the
`Meter.Labels(...)` constructor is considered the safer alternative.

## Detailed specification

See the [SDK-facing Metrics API](api-metrics-meter.md) specification
for an in-depth summary of each method in the Metrics API.

### Instrument construction

Instruments are constructed using the appropriate `New` method for the
kind of instrument (Counter, Gauge, Measure) and for the type of input
(integer or floating point).

| `Meter` method                      | Kind of instrument |
|-------------------------------------|--------------------|
| `NewIntCounter(name, options...)`   | An integer counter |
| `NewFloatCounter(name, options...)` | A floating point counter |
| `NewIntGauge(name, options...)`     | An integer gauge |
| `NewFloatGauge(name, options...)`   | A floating point gauge |
| `NewIntMeasure(name, options...)`   | An integer measure |
| `NewFloatMeasure(name, options...)` | A floating point measure |

As in all OpenTelemetry specifications, these names are examples.
Each language committee will decide on the appropriate names based on
conventions in that language.

#### Recommended label keys

Instruments may be defined with a recommended set of label keys.  This
setting may be used by SDKs as a good default for grouping exported
metrics, where used with pre-aggregation.  The recommended label keys
are usually selected by the developer for exhibiting low cardinality,
importance for monitoring purposes, and _an intention to provide these
variables locally_.

SDKs should consider grouping exported metric data by the recommended
label keys of each instrument, unless superceded by another form of
configuration.  Recommended keys that are missing will be considered
explicitly unspecified, as for missing `LabelSet` keys in general.

#### Instrument options

Instruments provide several optional settings, summarized here.  The
kind of instrument and input value type are implied by the constructor
that it used, and the metric name is the only required field.

| Option                 | Option name               | Explanation |
|------------------------|---------------------------|-------------|
| Description            | WithDescription(string)   | Descriptive text documenting the instrument. |
| Unit                   | WithUnit(string)          | Units specified according to the [UCUM](http://unitsofmeasure.org/ucum.html). |
| Recommended label keys | WithRecommendedKeys(list) | Recommended grouping keys for this instrument. |
| Monotonic              | WithMonotonic(boolean)    | Configure a counter or gauge that accepts only monotonic/non-monotonic updates. |
| Absolute               | WithAbsolute(boolean)     | Configure a measure that does or does not accept negative updates. |

See the Metric API [specification overview](api-metrics.md) for more
information about the kind-specific monotonic and absolute options.

### Bound instrument API

Counter, gauge, and measure instruments each support allocating
bound instruments for the high-performance calling convention.  The
`Instrument.Bind(LabelSet)` method returns an interface which
implements the `Add()`, `Set()` or `Record()` method, respectively,
for counter, gauge, and measure instruments.

### Direct instrument API

Counter, gauge, and measure instruments support the appropriate
`Add()`, `Set()`, and `Record()` method for submitting individual
metric events.

### Interaction with distributed correlation context

The `LabelSet` type introduced above applies strictly to "local"
labels, meaning provided in a call to `meter.Labels(...)`.  The
application explicitly declares these labels, whereas distributed
correlation context labels are implicitly associated with the event.

There is a clear intention to pre-aggregate metrics within the SDK,
using the contents of a `LabelSet` to derive grouping keys.  There are
two available options for users to apply distributed correlation
context to the local grouping function used for metrics
pre-aggregation:

1. The distributed context, whether implicit or explicit, is
  associated with every metric event.  The SDK could _automatically_
  project selected label keys from the distributed correlation into the
  metric event.  This would require some manner of dynamic mapping from
  `LabelSet` to grouping key during aggregation.
2. The user can explicitly perform the same projection of distributed
  correlation into a `LabelSet` by extracting from the correlation
  context and including it in the call to `metric.Labels(...)`.

An example of an explicit projection follows.

```golang
import "go.opentelemetry.io/api/distributedcontext"

func (s *server) doThing(ctx context.Context) {
    var doLabels []core.KeyValue{
     key1.String("..."),
 key2.String("..."),
    }

    correlations := distributedcontext.FromContext()
    if val, ok := correlations.Value(key3); ok {
        doLabels = append(doLabels, key3.Value(val))
    }
    labels := s.meter.Labels(doLabels)

    // ...
}
```
