# Metric User-facing API

TODO Table of contents.

## Overview

Metric instruments are the entry point for application and framework
developers to instrument their code using counters, gauges, and
measures.

### Metric names

Metric instruments have names, which are how we refer to them in
external systems.  Metric names conform to the following syntax:

1 They are non-empty strings
1 They are case-insensitive
1 The first character must be non-numeric, non-space, non-punctuation
1 Subsequent characters must be belong to the alphanumeric characters, '_', '.', and '-'.

Metrics names belong to a namespace by virtue of a "Named" `Meter`
instance.  A "Named" `Meter` refers to the requirement that every
`Meter` instance must have an associated `component` label, determined
statically in the code.  The `component` label value of the associated
`Meter` serves as its namespace, allowing the same metric name to be
used in multiple libraries of code, unambiguously, within the same
application.

Metric instruments are defined using a `Meter` instance, using a
variety of `New` methods.  The Meter will return an error when a
metric name is registered with a different kind with the same
component name.  Metric systems are expected to automatically prefix
exported metrics by the `component` namespace in a manner consistent
with the target system.  For example, a Prometheus exporter SHOULD use
the component followed by `_` as the [application
prefix](https://prometheus.io/docs/practices/naming/#metric-names).

### Format of a metric event

Regardless of the instrument kind or method, metric events include the
instrument descriptor, a numerical value, and an optional set of
labels.  The descriptor, discussed in detail below, contains the
metric name and various optional settiungs.  Labels are key:value
pairs associated with events describing various dimensions or
categories that describe the event.  A "label key" refers to the key
component while "label value" refers to the correlated value component
of a label.  Label refers to the pair of label key and value.

Metric events always have an associated `component` label, by virtue
of the named `Meter` used in their definition.  Other labels are
passed in to the metric event in the form of a `LabelSet` argument,
using several input methods discussed below.

### New constructors

The `Meter` interface allows creating of a registered metric
instrument using methods specific to each kind of metric.  There are
six constructors representing the three kinds of instrument taking
either floating point or integer inputs.  

| `Meter` method | Kind of instrument |
|-------|------|
| `NewIntCounter` | An integer counter |
| `NewFloatCounter` | A floating point counter |
| `NewIntGauge` | An integer gauge |
| `NewFloatGauge` | A floating point gauge |
| `NewIntMeasure` | An integer measure |
| `NewFloatMeasure` | A floating point measure |

As in all OpenTelemetry specifications, these names are examples.
Each language committee will decide on the appropriate names based on
conventions in that language.

Binding instruments to a single `Meter` instance has two benefits:

1 The instruments are exported even in the zero state, prior to first use
1 The namespace provided by the named `Meter` satisfies a namespace requirement
1 There is no explicit `Register` call

The recommended practice is to define structures to contain the
instruments in use and keep references only to the instruments that
are specifically needed.

We recognize that many existing metric systems support allocating
metric instruments statically and providing the `Meter` interface at
the time-of-use.  In this example, typical of statsd clients, existing
code may not be structured with a convenient place to store new metric
instruments.  Where this becomes a burden, it may be acceptable to use
the global `Meter` as a workaround.

The situation is similar for users of Prometheus clients, where
instruments are allocated statically and there is an implicit global.
Such code may not have access to the appropriate `Meter` where
instruments are defined.  Where this becomes a burden, it may be
acceptable to use the global `Meter` as a workaround.

#### Metric instrument descriptors

An instrument `Descriptor` is a structure describing all the
configurable aspects of an instrument that the user can elect.
Although the API provides a common `Descriptor` type--not the
SDK--users do not construct these directly.  Users pass all common
configuration options to the appropriate `Meter.New` method, which
itself will use a helper method provided by the API to build the new
`Descriptor`.  Users can access the descriptor of the built
instrument, in any case.

Given descripors and a `Meter` instance you can construct new
instruments that are ready to use.  Applications are expected to
construct long-lived instruments.  Instruments are considered
permanent, there is no method to delete them forget the metrics they
produce in the SDK.

The structure of the descriptor and various options are given in
detail below.

####  Metric instrument constructor example code

In this Golang example, a struct holding four instruments is built
given the provided `Meter`.  These calls give examples of the kind of
configuration options available for descriptors as well.

```golang
type instruments struct {
    counter1 metric.Int64Counter
    counter2 metric.Float64Counter
    gauge3   metric.Int64Gauge
    measure4 metric.Float64Measure
}

func newInstruments(metric.Meter meter) *instruments {
  return &instruments{
    counter1: meter.NewCounter("counter1", metric.WithKeys("client.service"))
    counter2: meter.NewCounter("counter2", metric.WithNonMonotonic(true))
    gauge3:   meter.NewGauge("gauge3", metric.WithUnit(unit.Bytes)).
    measure4: meter.NewMeasure("measure4", metric.WithDescription("Measure of ...")).
  }
}```

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

     s.counter1.Add(ctx, 1, s.meter.Labels(
     		label1.String("..."),
		label2.String("...")))
}
```

### Metric calling conventions

This API is factored into three core concepts: instruments, handles,
and label sets.  In doing so, we provide several ways of capturing
measurements that are semantically equivalent and generate equivalent
metric events, but offer varying degrees of performance and
convenience.

#### Metric handle calling convention

As described above, metric events consist of an instrument, a set of
labels, and a numerical value.  The performance of a metric API
depends on the steps taken to enter a new measurement.  One approach
to reduce cost is to pre-aggregate results, so that subsequent events
in the same collection period combine into the same working memory.

This approach requires locating an entry for the instrument and label
set in a table of some kind, finding the place where a group of metric
events are being aggregated.  This lookup can be successfully
precomputed, giving rise to the Handle calling convention.

In situations where performance is a requirement and a metric is
repeatedly used with the same set of labels, the developer may elect
to use Handles as an optimization.  For handles to be a benefit, it
requires that a specific instrument will be re-used with specific
labels.

To obtain a handle given an instrument and label set, use the
`GetHandle()` method to return an interface that supports the `Add()`,
`Set()`, or `Record()` method of the instrument in question.

A high-performace metrics SDK will take steps to ensure that
operations on handles are very fast.  Application developers are
required to delete handles when they are no-longer in use.

```golang
func (s *server) processStream(ctx context.Context) {

  streamLabels = []core.KeyValue{
      labelA.String("..."),
      labelB.String("..."),
  }
  counter2Handle := s.instruments.counter2.GetHandle(streamLabels)

  for _, item := <-s.channel {
     // ... other work

     // High-performance metric calling convention: use of handles.
     counter2Handle.Add(ctx, item.size())
  }
}
```

#### Direct metric calling convention

When convenience is more important than performance, or there is no
re-use to potentially optimize, users may elect to operate directly on
metric instruments, supplying a label set at the call site.

For example, to update a single counter:

```golang
func (s *server) method(ctx context.Context) {
    // ... other work

    s.instruments.counter1.Add(ctx, 1, s.meter.Labels(...))
}
```

This method offers the greatest convenience possible.  If performance
becomes a problem, one option is to use handles as described above.
Another performance option, in some cases, is to just re-use the
labels.  In the example here, `meter.Labels(...)` constructs a
re-usable label set which may be a useful performance optimization, as
discussed next.

#### Label set calling convention

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
scenarios where handles might not be effective.  For example, if the
label set will be re-used but only used once per metric, handles do
not offer any optimization.  It may be best to pre-compute a
canonicalized `LabelSet` once and re-use it with the direct calling
convention.

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

#### RecordBatch calling convention

There is one final API for entering measurements, which is like the
direct access calling convention but supports multiple simultaneous
measurements.  The use of a RecordBatch API supports entering multiple
measurements, implying a semantically atomic update to several
instruments.  Using the RecordBatch calling convention is otherwise
like the direct access calling convention.

The preceding example could be rewritten:

```golang
func (s *server) method(ctx context.Context) {
    // ... other work

    labelSet := s.meter.Labels(...)

    // ... more work

    s.meter.RecordBatch(ctx, labelSet, []metric.Measurement{
    	{ s.instruments.counter1, 1 },
	{ s.instruments.gauge1, 10 },
	{ s.instruments.measure1, 100 },
    })
}
```

## Detailed specification

See the [SDK-facing Metrics API](api-metrics-meter.md) specification
for an in-depth summary of each method in the Metrics API.

TODO more specifics on constructing metrics and the meaning of "recommended keys".

### Metric Descriptor

A metric instrument is completely described by its descriptor, through
arguments and optional parameters passed to the constructor.  The
complete contents of a metric `Descriptor` are:

- **Name** The unique name of this metric.  Naming conventions are not discussed here.
- **Kind** An enumeration, one of `CounterKind`, `GaugeKind`, `ObserverKind`, or `MeasureKind`
- **Keys** The recommended label keys.
- **ID** A unique identifier associated with new instrument object.
- **Description** A string describing the meaning and use of this instrument.
- **Unit** The unit of measurement, optional.
- _Kind-specific options_
  - **NonMonotonic** (Counter): add positive and negative values
  - **Monotonic** (Gauge): set a monotonic counter value
  - **Signed** (Measure): record positive and negative values

