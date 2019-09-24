# Metrics API

## Overview

The _Metrics API_ supports reporting diagnostic measurements using
three basic kinds of instrument.  "Metrics" are the thing being
produced--mathematical, statistical summaries of certain observable
behavior in the program.  "Instruments" are the devices used by the
program to record observations about their behavior.  Therefore, we
use "metric instrument" to refer to a program object, allocated
through the API, used for recording metrics.  There are three distinct
instruments in the Metrics API, commonly known as Counters, Gauges,
and Measures.

Monitoring and alerting are the common use-case for the data provided
through metric instruments, after various collection and aggregation
strategies are applied to the data.  We find there are many other uses
for the _metric events_ that stream into these instruments.  We
imagine metric data being aggregated and recorded as events in tracing
and logging systems too, and for this reason OpenTelemetry requires a
separation of the API from the SDK.

### Meter

The user-facing OpenTelemetry API consists of an SDK-independent part
for defining metric instruments and a part named `Meter` that is
implemented by the SDK.  According to the specification, the `Meter`
implementation ultimately determines how metrics events are handled.
The specification's task is to define the semantics of the event and
describe standard interpretation in high-level terms.  How the `Meter`
accomplishes its goals and the export capabilities it supports are not
specified.

The standard interpretation for `Meter` implementations to follow is
specified so that users understand the intended use for each kind of
metric.  For example, a monotonic Counter instrument supports
`Add()` events, so the standard interpretation is to compute a sum;
the sum may be exported as an absolute value or as the change in
value, but either way the purpose of using a Counter with `Add()` is
to monitor a sum.

## Metric kinds and inputs

The API distinguishes metric instruments by semantic meaning, not by
the type of value produced in an exporter.  This is a departure from
convention, compared with a number of common metric libraries, and
stems from the separation of the API and the SDK.  The SDK ultimately
determines how to handle metric events and could potentially implement
non-standard behavior.

This explains why the metric API does not have metric instrument kinds
for exporting "Histogram" and "Summary" distribution explicitly, for
example.  These are both semantically `Measure` instruments and an SDK
can be configured to produce histograms or distribution summaries from
Measure events.  It is out of scope for the Metrics API to specify how
these alternatives are configured in a particular SDK.

We believe the three metric kinds Counter, Gauge, and Measure form a
sufficient basis for expression of a wide variety of metric data.
Programmers write and read these as `Add()`, `Set()`, and `Record()`
method calls, signifying the semantics and standard interpretation,
and we believe these three methods are all that are needed.

Nevertheless, it is common to apply restrictions on metric values, the
inputs to `Add()`, `Set()`, and `Record()`, in order to refine their
standard interpretation.  Generally, there is a question of whether
the instrument can be used to compute a rate, because that is usually
a desireable analysis.  Each metric instrument offers an optional
declaration, specifying restrictions on values input to the metric.
For example, Measures are declared as non-negative by default,
appropriate for reporting sizes and durations; a Measure option is
provided to record positive or negative values, but it does not change
the kind of instrument or the method name used, as the semantics are
unchanged.

### Metric selection

To guide the user in selecting the right kind of metric for an
application, we'll consider the following questions about the primary
intent of reporting given data. We use "of primary interest" here to
mean information that is almost certainly useful in understanding
system behavior. Consider these questions:

- Does the measurement represent a quantity of something? Is it also non-negative?
- Is the sum a matter of primary interest?
- Is the event count a matter of primary interest?
- Is the distribution (p50, p99, etc.) a matter of primary interest?

With answers to these questions, a user should be able to select the
kind of metric instrument based on its primary purpose.

### Counter

Counters support `Add(value)`.  Choose this kind of metric when the
value is a quantity, the sum is of primary interest, and the event
count and value distribution are not of primary interest.

Counters are defined as monotonic by default, meaning that positive
values are expected.  Monotonic counters are typically used because
they can automatically be interpreted as a rate.

As an option, counters can be declared as `NonMonotonic`, in which
case they support positive and negative increments.  Non-monotonic
counters are useful to report changes in an accounting scheme, such as
the number of bytes allocated and deallocated.

### Gauge

Gauges support `Set(value)`.  Gauge metrics express a pre-calculated
value that is either Set() by explicit instrumentation or observed
through a callback.  Generally, this kind of metric should be used
when the metric cannot be expressed as a sum or because the
measurement interval is arbitrary. Use this kind of metric when the
measurement is not a quantity, and the sum and event count are not of
interest.

Gauges are defined as non-monotonic by default, meaning that any value
(positive or negative) is allowed.

As an option, gauges can be declared as `Monotonic`, in which case
successive values are expected to rise monotonically.  Monotonic
gauges are useful in reporting computed cumulative sums, allowing an
application to compute a current value and report it, without
remembering the last-reported value in order to report an increment.

A special case of gauge is supported, called an `Observer` metric
instrument, which is semantically equivalent to a gauge but uses a
callback to report the current value.  Observer instruments are
defined by a callback, instead of supporting `Set()`, but the
semantics are the same.  The only difference between `Observer` and
ordinary gauges is that their events do not have an associated
OpenTelemetry context.  Observer instruments are non-monotonic by
default and monotonic as an option, like ordinary gauges.

### Measure

Measures support `Record(value)`, signifying that events report
individual measurements.  This kind of metric should be used when the
count or rate of events is meaningful and either:

- The sum is of interest in addition to the count (rate)
- Quantile information is of interest.

Measures are defined as `NonNegative` by default, meaning that
negative values are invalid.  Non-negative measures are typically used
to record absolute values such as durations and sizes.

As an option, measures can be declared as `Signed` to indicate support
for positive and negative values.

## Detailed Description

### Structure

Metric instruments are named.  Regardless of the instrument kind,
metric events include the instrument name, a numerical value, and an
optional set of labels.  Labels are key:value pairs associated with
events describing various dimensions or categories that describe the
event.  A "label key" refers to the key component while "label value"
refers to the correlated value component of a label.  Label refers to
the pair of label key and value.

The Metrics API supports applying explicit labels through the
API itself, while labels can also be applied to metric events
implicitly, through the current OpenTelemetry context and resources.

A metric `Descriptor` is a structural description of the instrument
itself, including its name and various options.  Instruments may be
annotated with with specific `Units` and a description, for the
purpose of self-documentation.

Metric instruments are constructed independently of the SDK.  They are
"pure" API objects, in this sense, able to be used by more than one
active `Meter` implementation.

#### Disabled option

Instruments support a `Disabled` option.  Metric instruments
configured with `Disabled: True` are considered "off" unless
explicitly requested via SDK configuration.  Unless the SDK is
otherwise configured to enable a disabled metric, operations on these
instruments will be treated as no-ops.

Metric instruments are enabled by default (i.e., have `Disabled: False`).

### Handles and LabelSets

Metric instruments support a _Handle_ interface.  Metric handles are a
pair consisting of an instrument and a specific set of pre-defined
labels, allowing for efficient repeated measurements.  The use of
pre-defined labels is so important for performance that we make it a
first-class concept in the API.

A `LabelSet` represents a set of labels, i.e., a set of key:value
assignments.  `LabelSets` are returned by the SDK through a call to
`Meter.DefineLabels(labels)`.  Applications cannot read the labels
belonging to a `LabelSet` object, they are simply a reference to a
specific `Meter.DefineLabels()` event.

Handles and LabelSets support different ways to achieve the same kind
of optimization.  Generally, there is a high cost associated with
computing a canonicalized form of the label set that can be used as a
map key, in order to look up a corresponding group entry for
aggregation.  Handles offer the most optimization potential, but
require the programmer to allocate and store one handle per metric.
LabelSets offer most of the optimization potential without managing
one handle per metric.

Handles and LabelSets, unlike metric instruments themselves, are
SDK-dependent objects.  LabelSets should only be used with the SDK
that provided them, an unrecognized LabelSet error will result if used
with a different SDK.

### Export pipeline

A metrics export pipeline consists of an SDK-provided `Meter`
implementation that processes metrics events (somehow), paired with a
metrics data exporter that sends the data (somehow).

### Required label keys

Metric instruments list an optional set of _required label keys_ to
support potential optimizations in the metric export pipeline.  This
is an option in the sense that the empty set (of required label keys)
is a valid setting.  If required label keys are provided, it implies
that the SDK can infer a value for the required label from the
`LabelSet`.

To support efficient pre-aggregation in the metrics export pipeline,
we must be able to infer the label value from the `LabelSet`, which
implies that they are not dependent on dynamic context.  Required
label keys address this relationship.  The value of a required label
key is explicitly unspecified unless it is provided in the `LabelSet`,
by definition, and not to be taken from other context.

### Input methods

The API surface supports three ways to produce metrics events, after
obtaining a re-usable `LabelSet` via `Meter.DefineLabels(labels)`:

1. Through the Instrument directly.  Use `Counter.Add(LabelSet,
value)`, `Gauge.Set(LabelSet, value)`, or `Measure.Record(LabelSet,
value)` to produce an event (with no Handle).

2. Through an instrument Handle.  Use the
`Instrument.GetHandle(LabelSet)` API to construct a new handle that
implements the respective `Add(value)`, `Set(value)`, or
`Record(value)` method.

3. Through a `Meter.RecordBatch` call.  Use the batch API to enter
simultaneous measurements, where a measurement is a tuple consisting
of the `Instrument`, a `LabelSet` and the value for the appropriate
`Add()`, `Set()`, or `Record()` method.

For instrument `Monotonic` (Counter: default), `Monotonic` (Gauge:
option), and `NonNegative` options (Measure: default), certain inputs
are invalid.  These invalid inputs must not panic or throw unhandled
exceptions, however the SDK chooses to handle them.  The SDK should
reject these invalid inputs, but it is not required to.

# Method summary

Programming APIs should follow idiomatic naming and style conventions
in each language.  The names given here are suggestions aimed at
giving a consistent interface across languages in OpenTelemetry, but
these decisions will be made by individual language SIGs.

Languages with strong typing and/or a distinction between signed and
unsigned types may choose to implement variations on these interfaces
with the correct signatures for operating on integer vs. floating
point and signed vs. unsigned values.  The specification only requires
the three fundamental instrument types, whether or not they are
specialized for strong typing.

## `Meter` interface

Meter is an interface consisting of methods to define a label set, to
create or delete instrument handles, and to record a batch of measurements.

### `DefineLabels(labels) -> LabelSet`

`DefineLabels` allows the SDK to process an ordered collection of
labels and return an opaque handle, allowing the caller to amortize
the cost by re-using the returned `LabelSet`.  The `LabelSet` returned
has indefinite lifetime, allowing the application to hold on to it as
long as it remains useful.  The `LabelSet` cannot be explicitly
deleted.

LabelSets have map semantics.  When multiple labels are present in
`DefineLabels()`, the last value is taken.  The SDK is not required to
return a unique `LabelSet` object when called for equivalent sets of
labels.

There is no limit on label set size imposed by the API, although SDKs
may choose to.  Label sets may contain arbitrary labels.  At the point
of use, a label set may contain more or fewer than the required set of
labels, in which case the additional labels may be used (e.g.,
sampled) or reported by the SDK.

### `NewHandle(Instrument, LabelSet) -> language-specific`

`NewHandle` returns a language-specific interface to support
instrument handles.  The user calls `Instrument.GetHandle(LabelSet)`
directly, which calls through to `NewHandle(Instrument, LabelSet)`.
The `NewHandle` method is not a user-facing API and the return type
will vary depending on the language.

User-level method calls on the handle, `Add(value)`, `Set(value)`, and
`Record(value)`, interact with the result of `NewHandle` in a
language- and API-specific way.  SDKs are expected to hold resources
corresponding to each handle, so users are encouraged to delete
handles when they are no longer in use.

### `DeleteHandle(language-specific)`

After the application is finished with an instrument handle, deleting
the handle will result in `DeleteHandle()` on the underlying,
language- and API-specific type.  The SDK may release any
pre-aggregation state associated with the handle after exporting a
final update.

### `RecordBatch(LabelSet, measurements...)`

`RecordBatch` offers primitive support for entering multiple
simultaneous measurements.  The `Measurement` struct contains:

- *Instrument*: the instrument `Descriptor`
- *Value*: the numerical value of the measurement event.

Every measurement in the `RecordBatch` is associated with the
`LabelSet` argument (explicitly) and the current context and
resources (implicitly).

### `RegisterObserver(Observer, callback)`

Register an `Observer` instrument with the `Meter` to include it in
the metrics export pipeline.  The SDK provides its own logic for when
to call the observer.  When finished with an observer, use
`UnregisterObserver(Observer)`.

## Metric `Descriptor`

A metric instrument is completely described by its descriptor, through
arguments and optional parameters passed to the constructor.  The
complete contents of a metric `Descriptor` are:

- **Name** The unique name of this metric.  Naming conventions are not discussed here.
- **Kind** An enumeration, one of `CounterKind`, `GaugeKind`, `ObserverKind`, or `MeasureKind`
- **Keys** The required label keys.
- **ID** A unique identifier associated with new instrument object.
- **Description** A string describing the meaning and use of this instrument.
- **Unit** The unit of measurement, optional.
- **Disabled** True value tells the SDK not to report by default.
- _Kind-specific options_
  - **NonMonotonic** (Counter): add positive and negative values
  - **Monotonic** (Gauge): set a monotonic counter value
  - **Signed** (Measure): record positive and negative values

## `Instrument` classes

`Counter`, `Gauge`, and `Measure` instruments have consistent method
names and behavior, with the exception of their respective action
verb, `Add()`, `Set()`, or `Record()`.  These three are covered here.

### `New`

To construct a new instrument, the specific `Kind` and thus the return
value depend on the choice of (`Counter`, `Gauge`, or `Measure`).
`Name` is the only required parameter.  `ID` is automatically assigned
by the API.  The other fields (Description, Keys, Unit, Disabled,
Kind-specific) are options to the various constructors in a
language-appropriate style.

Metric units are defined according to the
[UCUM](http://unitsofmeasure.org/ucum.html) specification.

Metric instruments are not associated with an SDK. They can be used
with multiple `Meter` instances in the same process.

For example,

```
requestKeys    = ["path", "host"]
requestBytes   = NewIntCounter("request.bytes",
				WithKeys(requestKeys),
				WithUnit(unit.Bytes))
requestLatency = NewFloatMeasure("request.latency",
				WithKeys(requestKeys),
				WithUnit(unit.Second))
loadAvg60s     = NewFloatGauge("load.avg.60s")
```

### `Add`, `Set`, `Record`

Using a `LabelSet` obtained via `Meter.DefineLabels()` and an `Instrument` object directly, call the appropriate `Instrument.Action(LabelSet, value)` method, where `Action` is one of `Add`, `Set`, or `Record`.

Continuing the example above,

```
labels = meter.DefineLabels({ "path": "/doc/{id}", "host": "h123", "port": 123, "frag": "#abc" })

requestBytes.Add(labels, req.bytes)
requestLatency.Record(labels, req.latency)
```

Operating on the instrument directly is expected to be relatively
fast, compared with defining a new label set, but not as fast as
operating through handles.

Use `meter.DefineLabels()` as the label set for label-free metric instruments.

### `Handle` operation

Using a `LabelSet` obtained via `Meter.DefineLabels()` and an
`Instrument` object, call `GetHandle` to obtain a handle.  The handle
should be stored for re-use.

For example, using `labels` as shown above:

```
requestBytesHandle   = requestBytes.GetHandle(labels)
requestLatencyHandle = requestLatency.GetHandle(labels)

for req in requestBatch {
  ...
  requestsBytesHandle.Add(req.bytes)
  requestsLatencyHandle.Record(req.latency)
}
```

Operating on handles should be faster than operating directly on the
instrument in the standard OpenTelemetry SDK.

After the application finishes with the handle, it should be
explicitly deleted in a language-appropriate way, which must call
`Meter.DeleteHandle`.

### `RecordBatch` operation

Using a `LabelSet` obtained via `Meter.DefineLabels()` call
`RecordBatch(LabelSet, measurements)`, where `measurements` is a list
of (`Instrument`, `Value`) pairs.  `RecordBatch` applies to the `Meter`
bound to the `LabelSet`.

For example, to record two metrics simultaneously:

```
RecordBatch(labels,
    Measurement(requestBytes, req.bytes),
    Measurement(requestLatency, req.latency))
```

## `Observer` instrument

`Observer` instruments are like `Gauge` instruments, but they are
registered directly with the `Meter` instance, allowing the
application to provide a `Meter`-specific callback.  Use
`Meter.RegisterObserver(Observer, Callback)` to register an observer
and begin exporting data.

### `New`

A new `Observer` is constructed similar to a new `Gauge`, supporting
the same options.  The `Observer` instrument does not support `Set()`
or `GetHandle()`.

### `Callback` interface

The callback takes a (`Meter`, `Observer`) argument.  The `Meter` and
`Observer` passed to a `Callback` match an individual registration.

The callback returns a map from `LabelSet` to the current gauge value.
The return `LabelSets` must have been defined by the corresponding
`Meter` of the `Observer` registration.

### `Callback` requirements

Callbacks should avoid blocking. The implementation may be required to
cancel computation if the callback blocks for too long.

Callbacks must not be called synchronously with application code via
any OpenTelemetry API. Implementations that cannot provide this
guarantee should prefer not to implement observer callbacks.

Callbacks may be called synchronously in the SDK on behalf of an
exporter.

Callbacks should avoid calling OpenTelemetry APIs, but we recognize
this may be impossible to enforce.
