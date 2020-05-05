# Metric User-facing API

<!-- toc -->

- [Overview](#overview)
  * [Obtaining a Meter](#obtaining-a-meter)
  * [Metric names](#metric-names)
  * [Format of a metric event](#format-of-a-metric-event)
  * [New constructors](#new-constructors)
    + [Metric instrument constructor example code](#metric-instrument-constructor-example-code)
  * [Metric calling conventions](#metric-calling-conventions)
    + [Bound instrument calling convention](#bound-instrument-calling-convention)
    + [Direct instrument calling convention](#direct-instrument-calling-convention)
    + [RecordBatch calling convention](#recordbatch-calling-convention)
      - [Missing label keys](#missing-label-keys)
      - [Option: Ordered labels](#option-ordered-labels)
- [Detailed specification](#detailed-specification)
  * [Instrument construction](#instrument-construction)
    + [Recommended label keys](#recommended-label-keys)
    + [Instrument options](#instrument-options)
  * [Bound instrument API](#bound-instrument-api)
  * [Direct instrument API](#direct-instrument-api)
  * [Interaction with distributed correlation context](#interaction-with-distributed-correlation-context)

<!-- tocstop -->

## Overview

Metric instruments are the entry point for application and framework developers to instrument their code using counters, gauges, and measures.
Metrics are created by calling methods on a `Meter` which is in turn created by a global `MeterProvider`.

### Obtaining a Meter

New `Meter` instances can be created via a `MeterProvider` and its `getMeter` method.
`MeterProvider`s are generally expected to be used as singletons.
Implementations SHOULD provide a single global default `MeterProvider`. The `getMeter` method expects two string arguments:

- `name` (required): This name must identify the instrumentation library (also referred to as integration, e.g. `io.opentelemetry.contrib.mongodb`)
  and *not* the instrumented library.
  In case an invalid name (null or empty string) is specified, a working default `Meter` implementation is returned as a fallback
  rather than returning null or throwing an exception.
  A `MeterProvider` could also return a no-op `Meter` here if application owners configure the SDK to suppress telemetry produced by this library.
  This name will be used as the `namespace` for any metrics created using the returned `Meter`.
- `version` (optional): Specifies the version of the instrumentation library (e.g. `semver:1.0.0`).

### Metric Instrument names

Metric instruments have names, which are how we refer to them in
external systems.  Metric instrument names conform to the following syntax:

1. They are non-empty strings
2. They are case-insensitive
3. The first character must be non-numeric, non-space, non-punctuation
4. Subsequent characters must be belong to the alphanumeric characters, '_', '.', and '-'.

Metric instrument names belong to a namespace, which is the `name` of the associated `Meter`,
allowing the same metric name to be used in multiple libraries of code,
unambiguously, within the same application.

Metric instrument names SHOULD be semantically meaningful, even when viewed
outside of the context of the originating Meter name. For example, when instrumenting
an http server library, "latency" is not an appropriate instrument name, as it is too generic.
Instead, as an example, we should favor a name like "http_request_latency",
as it would inform the viewer of the semantic meaning of the latency being tracked.
(Note: this is just an example; actual semantic conventions for instrument naming will
be tracked elsewhere in the specifications.)

Metric instruments are defined using a `Meter` instance, using a variety
of `New` methods specific to the kind of metric and type of input (integer
or floating point).  The Meter will return an error when a metric name is
already registered with a different kind for the same name. Metric systems
are expected to automatically prefix exported metrics by the namespace, if
necessary, in a manner consistent with the target system. For example, a
Prometheus exporter SHOULD use the namespace followed by `_` as the
[application prefix](https://prometheus.io/docs/practices/naming/#metric-names).

### Format of a metric event

As [stated in the general API
specification](api.md#metric-event-format), metric events consist of
the timestamp, the instrument definition (name, kind, description,
unit), a numerical value, an optional label set, and a resource label
set.  

Labels are key:value pairs associated with events describing various dimensions
or categories that describe the event.  A "label key" refers to the key
component while "label value" refers to the correlated value component of a
label.  Label refers to the pair of label key and value.  Labels are passed in
to the metric event at construction time.

Metric events always have an associated reporting library name and
optional version, which are passed when constructing the corresponding
`Meter`.  Synchronous metric events are additionally associated with
the the OpenTelemetry [Context](../context/api.md), including
distributed correlation context and span context.

### New constructors

The `Meter` interface allows creating registered metric instruments
using a specific constructor for each kind of instrument.  There are
at least six constructors representing the six kinds of instrument,
and possible more as dictated by the language, for example, if
specializations are provided for integer and floating pointer numbers
(such languages might support 12 constructors).

Binding instruments to a single `Meter` instance has two benefits:

1. Instruments can be exported from the zero state, prior to first use, with no explicit `Register` call
2. The library-name and version are implicitly included in each metric event.

The recommended practice is to define structures to contain the
instruments in use and keep references only to the instruments that
are specifically needed in application code.

We recognize that many existing metric systems support allocating
metric instruments statically and providing the `Meter` interface at
the time of use.  In this example, typical of statsd clients, existing
code may not be structured with a convenient place to store new metric
instruments.  Where this becomes a burden, it is recommended to use
the global meter provider to construct a static `Meter`, to
construct metric instruments.

The situation is similar for users of Prometheus clients, where
instruments are allocated statically and there is an implicit global.
Such code may not have access to the appropriate `Meter` where
instruments are defined.  Where this becomes a burden, it is
recommended to use the global meter provider to construct a static
named `Meter`, to construct metric instruments.

Applications are expected to construct long-lived instruments.
Instruments are considered permanent for the lifetime of a SDK, there
is no method to delete them.

#### Metric instrument constructor example code

In this Golang example, a struct holding four instruments is built
using the provided, non-global `Meter` instance.

```golang
type instruments struct {
    counter1  metric.Int64Counter
    counter2  metric.Float64Counter
    recorder3 metric.Float64ValueRecorder
    observer4 metric.Int64SumObserver
    
}

func (s *server) setInstruments(metric.Meter meter) *instruments {
  s.instruments = &instruments{
    counter1: meter.NewInt64Counter("counter1", ...),  // Optional parameters
    counter2: meter.NewFloat64Counter("counter2", ...),  // are discussed below.
    recorder3: meter.NewFloat64ValueRecorder("recorder3", ...),
    observer4:   meter.NewInt64SumObserver("observer4",
                     metric.NewInt64ObserverCallback(server.observeSumNumber4)),
  }
}

func newServer(meter metric.Meter) *server {

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
     s := &server{
         meter:       meter,
         // ... other fields
     }
     s.setInstruments(meter)
     return s
}

// ...

func (s *server) operate(ctx context.Context) {
     // ... other work

     s.instruments.counter1.Add(ctx, 1,
        key.String("label1", "..."),
        key.String("label2", "..."),
}
```

### Metric calling conventions

The metrics API provides three semantically equivalent ways to capture measurements:

- calling bound metric instruments
- calling unbound metric instruments with labels
- batch recording without a metric instrument

All three methods generate equivalent metric events, but offer varying degrees
of performance and convenience.

This section applies to calling conventions for counter, gauge, and
measure instruments.

As described above, metric events consist of an instrument, a set of labels,
and a numerical value, plus associated context.  The performance of a metric
API depends on the work done to enter a new measurement.  One approach to
reduce cost is to aggregate intermediate results in the SDK, so that subsequent
events happening in the same collection period, for the same set of labels,
combine into the same working memory.

In this document, the term "aggregation" is used to describe the
process of coalescing metric events for a complete set of labels,
whereas "grouping" is used to describe further coalescing aggregate
metric data into a reduced number of key dimensions.  SDKs may be
designed to perform aggregation and/or grouping in the process, with
various trade-offs in terms of complexity and performance.

#### Bound instrument calling convention

In situations where performance is a requirement and a metric instrument is
repeatedly used with the same set of labels, the developer may elect to use the
_bound instrument_ calling convention as an optimization.  For bound
instruments to be a benefit, it requires that a specific instrument will be
re-used with specific labels.  If an instrument will be used with the same
labels more than once, obtaining a bound instrument corresponding to the labels
ensures the highest performance available.

To bind an instrument, use the `Bind(labels)` method to return an interface
that supports the `Add()`, `Set()`, or `Record()` method of the instrument in
question.

Bound instruments may consume SDK resources indefinitely.

```golang
func (s *server) processStream(ctx context.Context) {

  // The result of Bind() is a bound instrument
  // (e.g., a BoundInt64Counter).
  counter2 := s.instruments.counter2.Bind(
      key.String("labelA", "..."),
      key.String("labelB", "..."),
  )

  for _, item := <-s.channel {
     // ... other work

     // High-performance metric calling convention: use of bound
     // instruments.
     counter2.Add(ctx, item.size())
  }
}
```

#### Direct instrument calling convention

When convenience is more important than performance, or there is no re-use to
potentially optimize with bound instruments, users may elect to operate
directly on metric instruments, supplying labels at the call site.  This method
offers the greatest convenience possible

For example, to update a single counter:

```golang
func (s *server) method(ctx context.Context) {
    // ... other work

    s.instruments.counter1.Add(ctx, 1, ...)
}
```

#### RecordBatch calling convention

There is one final API for entering measurements, which is like the direct
access calling convention but supports multiple simultaneous measurements.  The
use of a RecordBatch API supports entering multiple measurements, implying a
semantically atomic update to several instruments.

For example:

```golang
func (s *server) method(ctx context.Context) {
    // ... other work

    s.meter.RecordBatch(ctx, labels,
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

##### Missing label keys

When the SDK interprets labels in the context of grouping aggregated values for
an exporter, and where there are keys that are missing, the SDK is required to
consider these values _explicitly unspecified_, a distinct value type of the
exported data model.

##### Option: Ordered labels

As a language-level decision, APIs may support label key ordering.  In this
case, the user may specify an ordered sequence of label keys, which is used to
create an unordered set of labels from a sequence of similarly ordered label
values.  For example:

```golang

var rpcLabelKeys = OrderedLabelKeys("a", "b", "c")

for _, input := range stream {
    labels := rpcLabelKeys.Values(1, 2, 3)  // a=1, b=2, c=3

    // ...
}
```

This is specified as a language-optional feature because its safety, and
therefore its value as an input for monitoring, depends on the availability of
type-checking in the source language.  Passing unordered labels (i.e., a
mapping from keys to values) is considered the safer alternative.

## Detailed specification

See the [SDK-facing Metrics API](api-meter.md) specification
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

SDKs should consider grouping exported metric data by the recommended label
keys of each instrument, unless superceded by another form of configuration.
Recommended keys that are missing will be considered explicitly unspecified, as
for missing labels in general.

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

See the Metric API [specification overview](api.md) for more
information about the kind-specific monotonic and absolute options.

### Bound instrument API

Counter, gauge, and measure instruments each support allocating bound
instruments for the high-performance calling convention.  The
`Instrument.Bind(labels)` method returns an interface which implements the
`Add()`, `Set()` or `Record()` method, respectively, for counter, gauge, and
measure instruments.

### Direct instrument API

Counter, gauge, and measure instruments support the appropriate
`Add()`, `Set()`, and `Record()` method for submitting individual
metric events.

### Interaction with distributed correlation context

As described above, labels are strictly "local".  I.e., the application
explicitly declares these labels, whereas distributed correlation context
labels are implicitly associated with the event.

There is a clear intention to pre-aggregate metrics within the SDK, using
labels to derive grouping keys.  There are two available options for users to
apply distributed correlation context to the local grouping function used for
metrics pre-aggregation:

1. The distributed context, whether implicit or explicit, is
  associated with every metric event.  The SDK could _automatically_
  project selected label keys from the distributed correlation into the
  metric event.
2. The user can explicitly perform the same projection of distributed
  correlation into labels by extracting labels from the correlation
  context and including them in the call to create the metric or bound
  instrument.

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

## Metric instrument selection

To guide the user in selecting the right kind of metric instrument for
an application, we'll consider several questions about the kind of
numbers being reported.  Here are some ways to help choose.  Examples
are provided in the following section.

### Counters and Measures compared

Counters and Measures are both recommended for reporting measurements
taken during synchronous activity, driven by events in the program.
These measurements include an associated distributed context, the
effective span context (if any), the correlation context, and
user-provided LabelSet values.

Start with an application for metrics data in mind.  It is useful to
consider whether you are more likely to be interested in the sum of
values or any other aggregate value (e.g., average, histogram), as
processed by the instrument.  Counters are useful when only the sum is
interesting.  Measures are useful when the sum and any other kind of
summary information about the individual values are of interest.

If only the sum is of interest, use a Counter instrument.

If you are interested in any other kind of summary value or statistic,
such as mean, median and other quantiles, or minimum and maximum
value, use a Measure instrument.  Measure instruments are used to
report any kind of measurement that is not typically expressed as a
rate or as a total sum.

### Observer instruments

Observer instruments are recommended for reporting measurements about
the state of the program periodically.  These expose current
information about the program itself, not related to individual events
taking place in the program.  Observer instruments are reported
outside of a context, thus do not have an effective span context or
correlation context.

Observer instruments are meant to be used when measured values report
on the current state of the program, as opposed to an event or a
change of state in the program.

## Examples

### Reporting total bytes read

You wish to monitor the total number of bytes read from a messaging
server that supports several protocols.  The number of bytes read
should be labeled with the protocol name and aggregated in the
process.

This is a typical application for the Counter instrument.  Use one Counter for
capturing the number bytes read.  When handling a request, compute a LabelSet
containing the name of the protocol and potentially other useful labels, then
call `Add()` with the same labels and the number of bytes read.

To lower the cost of this reporting, you can `Bind()` the instrument with each
of the supported protocols ahead of time.

### Reporting total bytes read and bytes per request

You wish to monitor the total number of bytes read as well as the
number of bytes read per request, to have observability into total
traffic as well as typical request size.  As with the example above,
these metric events should be labeled with a protocol name.

This is a typical application for the Measure instrument.  Use one
Measure for capturing the number of bytes per request.  A sum
aggregation applied to this data yields the total bytes read; other
aggregations allow you to export the minimum and maximum number of
bytes read, as well as the average value, and quantile estimates.

In this case, the guidance is to create a single instrument.  Do not
create a Counter instrument to export a sum when you want to export
other summary statistics using a Measure instrument.

### Reporting system call duration

You wish to monitor the duration of a specific system call being made
frequently in your application, with a label to indicate a file name
associated with the operation.

This is a typical application for the Measure instrument.  Use a timer
to measure the duration of each call and `Record()` the measurement
with a label for the file name.

### Reporting request size

You wish to monitor a trend in request sizes, which means you are
interested in characterizing individual events, as opposed to a sum.
Label these with relevant information that may help explain variance
in request sizes, such as the type of the request.

This is a typical application for a Measure instrument.  The standard
aggregation for Measure instruments will compute a measurement sum and
the event count, which determines the mean request size, as well as
the minimum and maximum sizes.

### Reporting a per-request finishing account balance

There's a number that rises and falls such as a bank account balance.
You wish to monitor the average account balance at the end of
requests, broken down by transaction type (e.g., withdrawal, deposit).

Use a Measure instrument to report the current account balance at the
end of each request.  Use a label for the transaction type.

### Reporting process-wide CPU usage

You are interested in reporting the CPU usage of the process as a
whole, which is computed via a (relatively expensive) system call
which returns two values, process-lifetime user and system
cpu-seconds.  It is not necessary to update this measurement
frequently, because it is meant to be used only for accounting
purposes.

A single Observer instrument is recommended for this case, with a
label value to distinguish user from system CPU time.  The Observer
callback will be called once per collection interval, which lowers the
cost of collecting this information.

CPU usage is something that we naturally sum, which raises several
questions.

- Why not use a Counter instrument?  In order to use a Counter instrument, we would need to convert total usage figures into deltas.  Calculating deltas from the previous measurement is easy to do, but Counter instruments are not meant to be used from callbacks.
- Why not report deltas in the Observer callback?  Observer instruments are meant to be used to observe current values. Nothing prevents reporting deltas with an Observer, but the standard aggregation for Observer instruments is to sum the current value across distinct labels.  The standard behavior is useful for determining the current rate of CPU usage, but special configuration would be required for an Observer instrument to use Counter aggregation.

### Reporting per-shard memory holdings

Suppose you have a widely-used library that acts as a client to a
sharded service.  For each shard it maintains some client-side state,
holding a variable amount of memory per shard.

Observe the current allocation per shard using an Observer instrument with a
shard label.  These can be aggregated across hosts to compute cluster-wide
memory holdings by shard, for example, using the standard aggregation for
Observers, which sums the current value across distinct labels.

### Reporting number of active requests

Suppose your server maintains the count of active requests, which
rises and falls as new requests begin and end processing.

Observe the number of active requests periodically with an Observer
instrument.  Labels can be used to indicate which application-specific
properties are associated with these events.

### Reporting bytes read and written correlated by end user

An application uses storage servers to read and write from some
underlying media.  These requests are made in the context of the end
user that made the request into the frontend system, with Correlation
Context passed from the frontend to the storage servers carrying these
properties.

Use Counter instruments to report the number of bytes read and written
by the storage server.  Configure the SDK to use a Correltion Context
label key (e.g., named "app.user") to aggregate events by all metric
instruments.
