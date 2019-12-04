# Metrics API

TODO: Table of contents

## Overview

The user-facing metrics API supports producing diagnostic measurements
using three basic kinds of instrument.  "Metrics" are the thing being
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

### User-facing API

The user-facing OpenTelemetry API consists of an SDK-independent part
for defining metric instruments.  Review the [user-facing
OpenTelementry API specification](api-metrics-user.md) for more detail
about the variety of methods, options, and optimizations available for
users of the instrumentation API.

To capture measurements using an instrument, you need an SDK that
implements the `Meter` API.

### Meter API

`Meter` is an interface with the SDK used to capture measurements in
various ways.  Review the [SDK-facing OpenTelemetry API
specification](api-metrics-meter.md) known as `Meter`.

Because of API-SDK separation, the `Meter` implementation ultimately
determines how metrics events are handled, .  The specification's task
is to define the semantics of the event and describe standard
interpretation in high-level terms.  How the `Meter` accomplishes its
goals and the export capabilities it supports are not specified.

The standard interpretation for `Meter` implementations to follow is
specified so that users understand the intended use for each kind of
metric.  For example, a monotonic Counter instrument supports
`Add()` events, so the standard interpretation is to compute a sum;
the sum may be exported as an absolute value or as the change in
value, but either way the purpose of using a Counter with `Add()` is
to monitor a sum.

### Purpose of this document

This document gives an overview of the specification, introduces the
the three kinds of instrument, and discusses how end-users should
think about various options at a high-level, without getting into
detail about specific method calls.

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
a desirable analysis.  Each metric instrument offers an optional
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
