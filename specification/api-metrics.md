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

### Three kinds of instrument

#### Counter

Counter instruments are used to report sums.  These are sometimes used
to monitor _rates_, and they are sometimes used to report _totals_.
One key property of Counter instruments is that two `Add(1)` events
are semantically equivalent to one `Add(2)` event, meaning that
Counter events can be combined using addition by definition.

Labels associated with Counter instrument events can be used to
compute rates and totals over selected dimensions.  When aggregating
Counter events we naturally combine values using addition.  Counter
`Add(0)` events are no-ops by definition.

Counters are monotonic by default, meaning `Add()` logically accepts
only non-negative values.  Monotonicity is useful for defining rates,
especially; non-monotonic Counter instruments are an option to support
sums that rise and fall.

Examples: requests processed, bytes read or written, memory allocated
and deallocated.

#### Measure

Measure instruments are used to report individual measurements.
Measure events are semantically independent and cannot be naturally
combined like with Counters.  Measure instruments are used to report
many kinds of information, recommended for reporting measurements
associated with real events in a computer program.

As a synchronous API, Measure `Record()` events can be used to record
information with associated labels and context.  This is the more
general of the two synchronous metric instruments.

Measure instruments support non-negative values by default, also known
as "absolute" in the sense that, mathematically, absolute values are
never negative.  As an option, Measure instruments can be defined as
not absolute, supporting both postive and negative values.

Examples: request latency, number of query terms, temperature, fan
speed, account balance, load average, screen width.

#### Observer

Observer instruments are used to report a current set of values at the
time of collection.  Observer instruments report not only current
values, but also _which label sets are current_ at the moment of
collection, as a coherent set of values.  These instruments reduce
collection cost because they are computed and reported only once per
collection interval, by definition.

Unlike Counter and Measure instruments, Observer instruments are
synchronized with collection, used to report values, on demand,
calculated by the program itself.  There is no aggregation across time
for Observer instruments by definition, only the current value is
defined.

Observer instruments can be declared as monotonic.  A monotonic
measure instrument supports reporting values that are not less than
the value reported in the previous collection interval.

When aggregating Observer instrument values across dimensions other
than time, Observer instruments may be treated like Counters (to
combine a rate or sum) or like Measures (to combine a distribution).
Unless otherwise configured, Observers are aggregated as Counters
would be.

Examples: memory held per shard, queue size by name.

### Standard Interpretation

We believe the three instrument kinds Counter, Measure, and Observer
form a sufficient basis for expressing nearly all metric data.  But if
the API and SDK are separated, and the SDK can handle any metric event
as it pleases, why not have just one kind of instrument?  How are the
instruments fundamentally different, despite all metric events having
the same form (i.e., a timestamp, an instrument, a number, and a label
set)?

Establishing different kinds of instrument is important because in
most cases it allows the SDK to provide good default functionality
without requiring alternative behaviors to be configured.  The choice
of instrument determines not only the meaning of the events but also
the name of the function used to report data.  The function
names--`Add()` for Counter instruments, `Record()` for Measure
instruments, and `Observe()` for Observer instruments--help convey and
reinforce the standard interpretation of the event.

The standard implementation for the three instruments is defined as
follows:

1. Counter.  The `Add()` function accumulates a total for each
distinct label set.  When aggregating over distinct label sets for a
Counter, combine using addition.  Export as a set of calculated sums.
2. Measure.  Use the `Record()` function to report summary statistics
about the distribution of values, for each distinct label set.  Which
statistics are used is determined by the implementation, but they
usually include at least the sum of values, the count of measurements,
and the minimum and maximum values.  When aggregating distinct label
sets for a Measure, report summary statistics of the combined value
distribution.  Exposition formats for Measure data vary widely by
backend service.
3. Observer.  Current values are provided by the Observer callback at
the end of each Metric collection period.  When aggregating values
_for the same label set_, combine using the most-recent value.  When
aggregating values _for different label sets_, combine using the sum.
Export as pairs of label set and calculated value.

We recognize that the standard behavior of the three instruments does
not cover all use-cases perfectly.  There is a natural tension between
offering dedicated metric instruments for every distinct metric
application and combining use-cases, generalizing semantics to reduce
the API surface area.  We could have define more than or fewer than
three kinds of instrument; we have three because these seem like
enough.  Where uncommon use-cases call for a non-standard
implementation configuration (e.g., a Measure instrument configured
with last-value aggregation), we accept that users will be required to
provide additional input on how to view certain metric data.

### Optional semantic restrictions

The instruments support optional declarations that indicate
restrictions on the valid range of inputs.  There are two options, one
to indicate whether the value is signed or not, the other to indicate
monotonicity.  These options are meant to be used as a signal to the
observability system, since they impact the way these data are exposed
to users.

In both cases, the optional restriction does not change the semantics
of the instrument.  The options are independent, both can be
meaningfully set on any instrument kind.

The specification describes enforcement of these options as "best
effort", not required.  Users are expected to honor their own
declarations when using instruments, and the SDK is expected to
perform checking of these options only when it can be done
inexpensively.

#### Absolute vs. Non-Absolute

Absolute refers to whether an instrument accepts negative values.
Absolute instruments can be described as accepting non-negative
inputs, whereas non-absolute instruments can be described as accepting
signed inputs.

When an instrument is absolute (i.e., accepts non-negative updates),
we know that the sum can be used to express a rate automatically.
This is true for all kinds of instrument.

When exporting measure values as a histogram, for example, knowing the
instrument is absolute facilitates the use of logarithmic buckets
(which are difficult to use when the input range spans zero).

Absolute behavior is the default for all instrument kinds. The
Non-Absolute option is supported for all instrument kinds.

Because this is a simple property for the SDK to test, the
specification recommends that SDKs SHOULD reject metric events for
absolute instruments when negative values are used, and instead issue
a warning to the user.

#### Monotonic vs. Non-Monotonic

Monotonic refers to whether an instrument only accepts values that are
greater than or equal to the previously recorded value.  Non-monotonic
instruments are those which accept any change in the value, positive
or negative.

Absolute-valued counters are naturally monotonic, so that Absolute and
Monotonic have the same interpretation for Counter instruments.

Measure and Observer instruments may be declared as monotonic, however
since this property is expensive to test, the specification recommends
that SDKs SHOULD implement monotonicity checking only when computing a
last-value aggregation.  The SDK SHOULD only perform this test against
the last known value when it holds the necessary information, it
should not go out of its way to save data simply to perform
monotonicity testing.

### Option: Dedicated Measure for timer values

As a language-optional feature, the API may support a dedicated
instrument for reporting timing measurements.  This kind of
instrument, with recommended name `TimingMeasure` (and
`BoundTimingMeasure`), is semantically equivalent to a Measure
instrument, and like the Measure instrument supports a `Record()`
function, but the input value to this instrument is in the language's
conventional data type for timing measurements.

For example, in Go the API will accept a `time.Duration`, and in C++
the API will accept a `std::chrono::duration`.  These advantage of
using these instruments is that they use the correct units
automatically, avoiding the potential for confusion over timing metrics.

## Metric instrument selection




@@@ HERE add many more examples.

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
