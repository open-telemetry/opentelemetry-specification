		# Metrics API

<!-- toc -->

- [Overview](#overview)
  * [User-facing API](#user-facing-api)
  * [Meter API](#meter-api)
  * [Purpose of this document](#purpose-of-this-document)
- [Metric API / SDK separation](#metric-api--sdk-separation)
  * [Three kinds of instrument](#three-kinds-of-instrument)
    + [Counter](#counter)
    + [Measure](#measure)
    + [Observer](#observer)
  * [Standard Interpretation](#standard-interpretation)
  * [Optional semantic restrictions](#optional-semantic-restrictions)
    + [Absolute vs. Non-Absolute](#absolute-vs-non-absolute)
    + [Monotonic vs. Non-Monotonic](#monotonic-vs-non-monotonic)
- [Metric instrument selection](#metric-instrument-selection)
  * [Counters and Measures compared](#counters-and-measures-compared)
  * [Observer instruments](#observer-instruments)
- [Examples](#examples)

<!-- tocstop -->

## Overview

The OpenTelemetry Metrics API supports capturing measurements about
the execution of a computer program in real time.  The Metrics API is
designed explicitly for processing raw measurements, generally with
the intent to produce continuous summaries of those measurements, also
in real time.  Hereafter, "the API" refers to the OpenTelemetry
Metrics API.

The API provides functions for entering raw measurements, through
several [calling conventions](TODO: link to user doc) that offer
different levels of performance.  Regardless of calling convention, we
define a _metric event_ as the logical thing that happens when a new
measurement is entered.

Monitoring and alerting systems commonly use the data provided through
metric events, after applying various [aggregations](#aggregations)
and converting into various [exposition formats](#exposition-formats).
However, we find that there are many other uses for metric events,
such as to record aggregated or raw measurements in tracing and
logging systems.  For this reason, [OpenTelemetry requires a
separation of the API from the SDK](library-guidelines.md#requirements),
so that different SDKs can be configured at runtime.

The word "semantic" or "semantics" as used here refers to _how we give
meaning_ to metric events, as they take place under the API.  The term
is used extensively in this document to define and explain these API
functions and how we should interpret them.  As far as possible, the
terminology used here tries to convey the intended semantics, and a
_standard implementation_ will be described below to help us
understand their meaning.  The standard implementation performs
aggregation corresponding to the default interpretation for each kind
of metric event.

### Metric Instruments

A _metric instrument_, of which there are three kinds, is a device for
entering raw measurements into the API.  There are Counter, Measure,
and Observer instruments, each with different semantics and intended
uses, that will be specified here.  All measurements that enter the
API are associated with an instrument, which gives the measurement its
properties.  Instruments are created and defined through calls to a
`Meter` API, which is the user-facing entry point to the SDK.

Each kinds of metric instrument has its own semantics, briefly
described as:

- Counter: metric events of this kind _Add_ to a value that you would sum over time
- Measure: metric events of this kind _Record_ a value that you would average over time
- Observer: metric events of this kind _Observe_ a coherent set of values at an instant in time.

An _instrument definition_ describes several properties of the
instrument, including its name and its kind.  The other properties of
a metric instrument are optional, including a description, the unit of
measurement, and several settings that convey additional meaning
(e.g., monotonicity).  An instrument definition is associated with the
events that it produces.

Details about calling conventions for each kind of instrument are
covered in the [user-level API specification](api-metrics-user.md).

### Label sets

_Label_ is the term used to refer to a key-value attribute associated
with a metric event.  Although they are fundamentally similar to [Span
attributes](api-tracing.md#span) in the tracing API, a [label
set](TODO: link to user doc) is given its own type in the Metrics API
(generally: `LabelSet`).  Label sets are a feature of the API meant to
facilitate re-use, to lower the cost of processing metric events.
Users are encouraged to re-use label sets whenever possible, as they
may contain a previously encoded representation of the labels.

Users obtain label sets by calling a `Meter` API function.  Each of
the instrument calling conventions detailed in the [user-level API
specification](api-metrics-user.md) accepts a label set.

### Meter Interface

To produce measurements using an instrument, you need an SDK that
supports the `Meter` API, which consists of a set of instrument
constructors, functionality related to label sets, and a facility for
reporting batches of measurements in a semantically atomic way.

There is a global `Meter` instance available for use.  Use of the this
instance allows library code that uses it to be automatically enabled
whenever the main application configures an SDK at the global level.

Details about installing an SDK and obtaining a `Meter` are covered in
the [SDK-level API specification](api-metrics-meter.md).

### Aggregations

_Aggregation_ refers to the process of combining a large number of
measurements into exact or estimated statistics about the metric
events that took place during a window of real time, during program
execution.  Computing aggregations is mainly a subject of the SDK
specification.

Users do not have a facility in the API to select the aggregation they
want for particular instruments.  The choice of instrument dictates
semantics and thus gives a default interpretation.  For the standard
implementation:

- Counter instruments use _Sum_ aggregation
- Measure instruments use _MinMaxSumCount_ aggregation
- Observer instruments use _LastValue_ aggregation.

The default Metric SDK specification includes support for configuring
alternative aggregations, so that metric instruments can be repuposed
and their data can be examined in different ways.  Using the default
SDK, or an alternate one, we are able to change the interpretation of
metric events at runtime.

Other standard aggregations are available, especially for Measure
instruments, where we are generally interested in a variety of forms
of statistics, such as histogram and quantile summaries.

### Time

Time is a fundamental property of metric events, but not an explicit
one.  Users do not provide explicit timestamps for metric events.  The
SDK is welcome to, but not required to capture the current timestamp
for each event by reading from a clock.

This non-requirement stems from a common optimization in metrics
reporting, which is to configure metric data collection with a
relatively small period (e.g., 1 second) and use a single timestamp to
describe a batch of exported data, since the loss of precision is
insignificant when aggregating data across minutes or hours of data.

Aggregations are commonly computed over a series of events that fall
into a contiguous region of time, known as the collection interval.
Since the SDK controls decision to start collection, it is possible to
collect aggregated metric data while only reading the clock once per
collection interval.

Counter and Measure instruments offer synchronous APIs for entering
measurements.  Metric events from Counter and Measure instruments
happen when they happen, the moment the SDK receives the function
call.

The Observer instrument supports an asynchronous API, allowing the SDK
to collect metric data on demand, once per collection interval.  A
single Observer instrument callback can enter multiple metric events
associated with different label sets.  Semantically, by definition,
these observations are captured at a single instant in time, the
instant that they became the current set of last-measured values.

Because metric events are implicitly timestamped, we could refer to a
series of metric events as a _time series_. However, we reserve the
use of this term for the SDK specification, to refer to parts of a
data format that express explicitly timestamped values, in a sequence,
resulting from an aggregation of raw measurements over time.

### Metric Event Format

Metric events have the same logical representation, regardless of
kind.  Whether a Counter, a Measure, or an Observer instrument, metric
events produced through an instrument consist of:

- an implicit timestamp at the moment the API function is called
- the instrument definition (name, kind, and options)
- a value (numeric)
- a [Context](api-context.md) (span context, correlation context)
- a label set

This is the outcome of separating the API from the SDK--a common
representation for metric events, where the only semantic distinction
is the kind of instrument that was used.

## Three kinds of instrument

Because the API is separated from the SDK, the implementation
ultimately determines how metric events are handled.  Therefore, the
choice of instrument should be guided by semantics and the intended
interpretation.  Here we detail the three instruments and their semantics.

### Counter

Counter instruments are used to report sums.  These are commonly used
to monitor rates, and they are sometimes used to report totals.  One
key property of Counter instruments is that two `Add(1)` events are
semantically equivalent to one `Add(2)` event--`Add(m)` and `Add(n)`
is equivalent to `Add(m+n)`.  This means that Counter events can be
combined using addition, by definition, which makes them relatively
inexpensive

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

### Measure

Measure instruments are used to report individual measurements.
Measure events are semantically independent and cannot be naturally
combined like with Counters.  Measure instruments are used to report
many kinds of information, recommended for reporting measurements
associated with real events in the program.

As a synchronous API, Measure `Record()` events can be used to record
information with associated labels and context.  This is the more
general of the two synchronous metric instruments.

Measure instruments support non-negative values by default, also known
as "absolute" in the sense that, mathematically, absolute values are
never negative.  As an option, Measure instruments can be defined as
not absolute, supporting both postive and negative values.

Examples: request latency, number of query terms, temperature, fan
speed, account balance, load average, screen width.

### Observer

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

## Interpretation

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
values or the average value, as processed by the instrument.  Counters
are useful when only the sum is interesting.  Measures are useful when
the sum and any other kind of summary information about the individual
values are of interest.

If only the sum is of interest, use a Counter instrument.  If the
Counter instrument accepts non-negative `Add()` values, use a
(default) monotonic Counter which will typically be expressed as a
rate (i.e., change per unit time).  If the Counter accepts both
positive and negative `Add()` values, use a non-monotonic Counter
which will typically be expressed as the total sum.

If you are interested in any other kind of summary value or statistic,
such as mean, median and other quantiles, or minimum and maximum
value, use a Measure instrument.  Measure instruments are used to
report any kind of measurement that is not typically expressed as a
rate or as a total sum.

If the Measure instrument accepts only non-negative values, as is
typically the case for measuring physical quantities, use a (default)
absolute Measure.  If the Measure instrument accepts both positive and
negative values, use a non-absolute Measure.  Both of these are
typically expressed in terms of a distribution of values, independent
from and _in addition to_ the rate of these measurements.

### Observer instruments

Observer instruments are recommended for reporting measurements about
the state of the program at a moment in time.  These expose current
information about the program itself, not related to individual events
taking place in the program.  Observer instruments are reported
b
outside of a context, thus do not have an effective span context or
correlation context.

Observer instruments are meant to be used when measured values report
on the current state of the program, as opposed to a change of state
in the program.  When Observer instruments are used to report physical
quantities, use a (default) absolute Observer.  When Observer
instruments are used to report measurements that can be negative for any
reason, use a non-absolute Observer.

If the Observer reports a current total sum, declare it as a monotonic
Observer.  Monotonic values are typically expressed as a rate of
change.

## Examples

### Reporting bytes read and written

You wish to monitor the number of bytes read and written from a
messaging server that supports several protocols.  The number of bytes
read and written should be labeled with the protocol name and
aggregated in the process.

This is a typical application for the Counter instrument.  Use one
Counter for bytes read and one Counter for bytes written.  When
handling a request, compute a LabelSet containing the name of the
protocol and potentially other useful labels, then call `Add()` twice
with the same label set and the number of bytes read and written.

To lower the cost of this reporting, you can `Bind()` the
instrument with each of the supported protocols ahead of time and
avoid computing the label set for each request.

### Reporting per-request CPU usage

Suppose you have a way to measure the CPU usage of processing an
individual request.  This is given to you in terms of cpu-seconds
consumed.  You may wish to monitor total CPU usage, or you could be
interested in the peak rate of CPU usage.

Use a Counter instrument to `Add()` this quantity to an instrument
named `cpu.seconds.used` after sending the response.  A Counter is
called for, in this case, because a sum is requested, meaning a sum of
all `Add()` events for the instrument in the specified time range.

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
label value to distinguish user from system CPU time.  Declare this as
a monotonic instrument, since CPU usage never falls.  The Observer
callback will be called once per collection interval, which lowers the
cost of collecting this information.

CPU usage is something that we naturally sum, which raises several
questions.

- Why not use a Counter instrument?  In order to use a Counter
instrument, we would need to convert total usage figures into
differences.  Calculating differences from the previous measurement is
easy to do, but Counter instruments are not meant to be used from
callbacks.
- Why not report differences in the Observer callback?  Observer
instruments are meant to be used to observe current values. Nothing
prevents reporting differences with an Observer, but the standard
aggregation for Observer instruments is to sum the current value
across distinct label sets.  The standard behavior is useful for
determining the current rate of CPU usage, but special configuration
would be required for an Observer instrument to use Counter
aggregation.

### Reporting per-shard memory holdings

Suppose you have a widely-used library that acts as a client to a
sharded service.  For each shard it maintains some client-side state,
holding a variable amount of memory per shard.

Observe the current allocation per shard using an Observer instrument
with a shard label.  These can be aggregated across hosts to compute
cluster-wide memory holdings by shard, for example, using the standard
aggregation for Observers, which sums the current value across
distinct label sets.
