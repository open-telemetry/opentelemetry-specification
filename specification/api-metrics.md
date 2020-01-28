# Metrics API

<!-- toc -->

- [Overview](#overview)
  * [User-facing API](#user-facing-api)
  * [Meter API](#meter-api)
  * [Purpose of this document](#purpose-of-this-document)
- [Metric API / SDK separation](#metric-api--sdk-separation)
  * [Justification for three kinds of instrument](#justification-for-three-kinds-of-instrument)
  * [Metric instrument selection](#metric-instrument-selection)
  * [Counter](#counter)
  * [Gauge](#gauge)
  * [Measure](#measure)

<!-- tocstop -->

## Overview

The OpenTelemetry Metrics API supports producing diagnostic
measurements using three basic kinds of instrument.  "Metrics" are the
thing being produced--mathematical, statistical summaries of certain
observable behaviors in the program.  "Instruments" are the devices
used by the program to record observations about their behavior.
Therefore, we use "metric instrument" to refer to a programmatic
interface, allocated through the API, used to produce metric events.
There are three kinds of instruments known as Counters, Measures, and
Observers.

Monitoring and alerting are the common use-case for the data provided
through metric instruments, after various collection and aggregation
strategies are applied to the data.  We find there are many other uses
for the _metric events_ recorded through these instruments.  We
imagine metric data being aggregated and recorded as events in tracing
and logging systems too, and for this reason OpenTelemetry requires a
separation of the API from the SDK.

### User-facing API

The user-facing OpenTelemetry API for Metrics begins with a `Meter`
interface, usually obtained through dependency injection or a global
instance.  The `Meter` API supports defining new metric instruments.
Review the [user-facing OpenTelemetry API
specification](api-metrics-user.md) for more detail about the variety
of methods, options, and optimizations available for users of the
instrumentation API and how to use the instruments defined here.

### Meter API

To produce measurements using an instrument, you need an SDK that
supports the `Meter` API, which consists of a set of constructors, the
`Labels` function for building label sets, and the `RecordBatch`
function for batch reporting.  Refer to the [sdk-facing OpenTelemetry
API specification](api-metrics-user.md) for more implementation notes.

Because of API-SDK separation, the `Meter` implementation ultimately
determines how metrics events are handled.  The specification's task
is to define the semantics of the events in high-level terms, so that
users and implementors can agree on their meaning.  How the `Meter`
accomplishes its goals and the export capabilities it supports are
specified for the default SDK in the (Metric SDK specification
WIP)[#WIP-spec-issue-347].

The standard interpretation for `Meter` implementations to follow is
given so that users understand the intended use for each kind of
metric.  For example, a Counter instrument supports `Add()` events,
and the default implementation is to compute a sum.  The sum may be
exported as an absolute value or as the change in value, but
regardless of the exporter and the implementation, the purpose of
using a Counter with `Add()` is to monitor a sum.  A detailed
explanation for how to select metric instruments for common use-cases
is given below, according to the semantics defined next.

### Purpose of this document

This document gives an overview of the specification, introduces the
the three kinds of instrument, and discusses how end-users should
think about various instruments and options at a high-level, without
getting into detail about specific function calls.  For details about
specific function calls, refer to the detailed specifications linked
above.

## Metric API / SDK separation

The API distinguishes metric instruments by semantic meaning, not by
the type of value produced in an exporter.  This is a departure from
convention, compared with a number of common metric libraries, and
stems from the separation of the API and the SDK.  The SDK ultimately
determines how to handle metric events and could potentially implement
non-standard behavior.  All metric events can be represented as
consisting of a timestamp, an instrument, a number (the value), and a
label set.  The semantics defined here are meant to assist both
application and SDK implementors, and examples will be given below.

The separation of API and SDK explains why the metric API does not
have metric instruments that generate specific metric "exposition"
values, for example "Histogram" and "Summary" values, which are
different ways to expose a distribution of measurements.  This API
specifies the use of a Measure kind of instrument with `Record()` for
recording individual measurements.  The instruments are defined so
that users and implementors understand what they mean, beacuse
different SDKs will handle events differently.

There is a common metric instrument known as a "Gauge" that is not
included in this API, the term "Gauge" referring to an instrument,
often mechanical, for reading the current "last" value of a measuring
device (e.g., a speedometer on your car's dashboard).  The problem
with "Gauge" starts from the term itself, which is figurative in
nature.  Using the word "gauge" suggests a behavior, that the
instrument will be used to expose the last value, not a semantic
definition.  Uses of traditional gauge instruments translate into an
Observer or the Measure instrument in this API.

### Brief: Three kinds of instrument

Two of the three kinds of instrument have been introduced through
examples above:

1. Counter.  Events contribute to a sum (i.e., a running total).  The
key property of Counter events is that they can be semantically
combined without affecting their meaning.  For example, two `Add(1)`
events are semantically equivalent to one `Add(2)` event.
2. Measure. Events are individual measurements.  The key property of
Measure events is that they correspond to real events, they cannot be
semantically combined.

The third kind of instrument is the Observer instrument, used for
recording the current value from a measurement source.  Each
collection interval, Observer instruments contribute the current value
for each distinct set of labels.  When aggregating Observer instrument
values across distinct label sets, the default implementation is to
compute a sum of current values.

Whereas Counter and Measure are both synchronous instruments, called
by the program to report on itself, the Observer instrument is
activated by the SDK through a callback, synchronized with collection.
Two key properties of an Observer instrument are (1) that it allows
the programmer to report a coherent set of values, (2) that it can
lower collection cost by computing values on demand.

### Interpretation

We believe the three instrument kinds Counter, Measure, and Observer
form a sufficient basis for expressing nearly all metric data.  But if
the API and SDK are separated, and the SDK can handle any metric event
as it pleases, why not have just one kind of instrument?  How are the
instruments fundamentally different, despite all metric events having
the same form (i.e., a timestamp, an instrument, a number, and a label
set)?

Establishing different kinds of instrument is important because in
most cases it allows the SDK to provide default functionality without
requiring alternative beahviors to be configured.  The choice of
instrument determines not only the meaning of the events but also the
name of the function used to report data.  The function names--`Add()`
for Counter instruments, `Record()` for Measure instruments, and
`Observe()` for Observer instruments--help convey and reinforce the
semantics of the event.

The standard implementation for the three instruments is defined as
follows:

1. Counter.  Accumulate a total for each distinct label set.  When
aggregating distinct label sets for a Counter, combine using addition.
Export as the computed sum.
2. Measure.  Compute summary statistics of the value distribution for
each distinct label set.  Which statistics are used is determined by
the implementation, but they usually include at least the sum of
values, the count of measurements, and the minimum and maximum values.
When aggregating distinct label sets for a Measure, report summary
statistics of the combined value distribution.  Exposition formats for
Measure data vary widely by backend service.

3. Observer.  Current values are provided by the Observer callback at
the end of each Metric collection period.  When aggregating values
_for the same label set_, combine using the more-recent value.  When
aggregating values _for different label sets_, combine using the sum.
Export as label set, calculated value pairs.

### Optional restrictions

It is common to apply restrictions on the input range of metric
values passed to inputs `Add()`, `Record()`, and `Observe()`.  

@@@ HERE

Generally, there is a question of whether the instrument can be used
to compute a rate, because that is usually a desirable analysis.  Each
metric instrument offers an optional declaration, specifying
restrictions on values input to the metric.  For example, Measures are
declared as non-negative by default, appropriate for reporting sizes
and durations; a Measure option is provided to record positive or
negative values, but it does not change the kind of instrument or the
method name used, as the semantics are unchanged.

## Metric instrument selection

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

Counters are defined as `Monotonic = true` by default, meaning that
positive values are expected.  `Monotonic = true` counters are
typically used because they can automatically be interpreted as a
rate.

As an option, counters can be declared as `Monotonic = false`, in which
case they support positive and negative increments.  `Monotonic = false`
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

Gauges are defined as `Monotonic = false` by default, meaning that new
values are permitted to make positive or negative changes to the
gauge.  There is no restriction on the sign of the input for gauges.

As an option, gauges can be declared as `Monotonic = true`, in which case
successive values are expected to rise monotonically.  `Monotonic = true`
gauges are useful in reporting computed cumulative sums, allowing an
application to compute a current value and report it, without
remembering the last-reported value in order to report an increment.

A special case of gauge is supported, called an `Observer` metric
instrument, which is semantically equivalent to a gauge but uses a
callback to report the current value.  Observer instruments are
defined by a callback, instead of supporting `Set()`, but the
semantics are the same.  The only difference between `Observer` and
ordinary gauges is that their events do not have an associated
OpenTelemetry context.  Observer instruments are `Monotonic = false` by
default and `Monotonic = true` as an option, like ordinary gauges.

### Measure

Measures support `Record(value)`, signifying that events report
individual measurements.  This kind of metric should be used when the
count or rate of events is meaningful and either:

- The sum is of interest in addition to the count (rate)
- Quantile information is of interest.

Measures are defined as `Absolute = true` by default, meaning that
negative values are invalid.  `Absolute = true` measures are typically
used to record absolute values such as durations and sizes.

As an option, measures can be declared as `Absolute = false` to
indicate support for positive and negative values.
