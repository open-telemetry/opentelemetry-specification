# Metrics API

<details>
<summary>
Table of Contents
</summary>

* [Overview](#overview)
  * [User-facing API](#user-facing-api)
  * [Meter API](#meter-api)
  * [Purpose of this document](#purpose-of-this-document)
* [Metric kinds and inputs](#metric-kinds-and-inputs)
  * [Metric selection](#metric-selection)
  * [Counter](#counter)
  * [Measure](#measure)
  * [Observer](#observer)

</details>

## Overview

The OpenTelemetry Metrics API supports producing diagnostic
measurements using three basic kinds of instrument.  "Metrics" are the
thing being produced--mathematical, statistical summaries of certain
observable behaviors in the program.  "Instruments" are the devices
used by the program to record observations about their behavior.
Therefore, we use "metric instrument" to refer to a programmatic
interface, allocated through the API, used for capturing metric
events.  There are three kinds of instruments known as Counters,
Measures, and Observers.

Monitoring and alerting are the common use-case for the data provided
through metric instruments, after various collection and aggregation
strategies are applied to the data.  We find there are many other uses
for the _metric events_ that stream into these instruments.  We
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

To capture measurements using an instrument, you need an SDK that
supports the `Meter` API, which consists of a set of constructors, the
`Labels` function for building label sets, and the `RecordBatch`
function for batch reporting.  Refer to the [sdk-facing OpenTelemetry
API specification](api-metrics-user.md) for more implementation notes.

Because of API-SDK separation, the `Meter` implementation ultimately
determines how metrics events are handled.  The specification's task
is to define the semantics of the event and describe standard
interpretation in high-level terms.  How the `Meter` accomplishes its
goals and the export capabilities it supports are specified for the
default SDK in the (Metric SDK
specification WIP)[#WIP-spec-issue-347].

The standard interpretation for `Meter` implementations to follow is
given so that users understand the intended use for each kind of
metric.  For example, a Counter instrument supports `Add()` events,
and the standard interpretation is to compute a sum.  The sum may be
exported as an absolute value or as the change in value, but
regardless of the exporter and the implementation, the purpose of
using a Counter with `Add()` is to monitor a sum.  Counters were used
in the example because they require almost no introduction.  A
detailed explanation for how to select metric instruments for common
use-cases is given below, according to the semantics defined next.

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
have metric instrument explicitly tied to specific metric "exposition"
types, such as "Histogram", "Summary", or "Last values" (also known,
traditionally, as "Gauges").  In the case of Histogram and Summary
value types, both are appropriate outputs for Measure instruments,
because Measure instruments are meant to used for recording individual
measurements synchronously.

There is a common metric instrument known as a "Gauge" that is not
included in this API, the term "Gauge" referring to an instrument,
often mechanical, for reading the current (also "last") value of a
measuring device (e.g., a speedometer on your car's dashboard).  The
problem with "Gauge" starts from the term itself, which is figurative
in nature.  Describing the instrument as a gauge implies how it will
be used, but not its semantics.

There are use-cases for traditional gauge instruments that fall into
both Observer and Measure instrument use-cases under the semantics
defined here, according to the intended use of number being reported.
This will be discussed in detail after instruments have been
introduced and the distinctions between them have been made clear.

### Justification for three kinds of instrument

We believe the three metric kinds Counter, Measure, and Observer form
a sufficient basis for expressing nearly all metric data.  But if the
API and SDK are separated, and the SDK can handle metric events as it
pleases, why not have just one kind of instrument?  This section
explains how the instruments are fundamentally different, despite all
metric events having the same form (i.e., a timestamp, an instrument,
a number, and a label set).

Establishing three kinds of instrument is important because it allows
the SDK to provide good functionality, without external configuration,
in most cases by default.

Factors that come up:

- is zero meaningful?  (i.e., sum important?)
- are the number of measurements important? (is there an implied rate?)
- is the measurement part of a current value set?
- if so ^^^, is it natural to sum current values or average them.
- (is it an interval or a ratio or a count)
- is there a measurement "interval"?  is the numnber of measurements meaningful.




Counter and Measure instruments offer synchronous APIs, . 

Programmers write and read these as `Add()` and `Record()` function
calls , signifying the semantics and standard interpretation, and we
believe these three methods are all that are needed.

Nevertheless, it is common to apply restrictions on metric values, the
inputs to `Add()`, `Set()`, and `Record()`, in order to refine their
standard interpretation.  Generally, there is a question of whether
the instrument can be used to compute a rate, because that is usually
a desirable analysis.  Each metric instrument offers an optional
declaration, specifying restrictions on values input to the metric.
For example, Measures are declared as non-negative by default,
appropriate for reporting sizes and durations; a Measure option is
provided to record positive or negative values, but it does not change
the kind of instrument or the method name used, as the semantics are
unchanged.

### Metric instrument selection

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
