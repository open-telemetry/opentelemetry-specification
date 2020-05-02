# Metrics API

<!-- toc -->

- [Overview](#overview)
  * [Metric Instruments](#metric-instruments)
  * [Labels](#labels)
  * [Meter Interface](#meter-interface)
  * [Aggregations](#aggregations)
  * [Time](#time)
  * [Metric Event Format](#metric-event-format)
- [Three kinds of instrument](#three-kinds-of-instrument)
  * [Counter](#counter)
  * [Measure](#measure)
  * [Observer](#observer)
- [Interpretation](#interpretation)
  * [Standard implementation](#standard-implementation)
  * [Future Work: Option Support](#future-work-option-support)
  * [Future Work: Configurable Aggregations / View API](#future-work-configurable-aggregations--view-api)
- [Metric instrument selection](#metric-instrument-selection)
  * [Counters and Measures compared](#counters-and-measures-compared)
  * [Observer instruments](#observer-instruments)
- [Examples](#examples)
  * [Reporting total bytes read](#reporting-total-bytes-read)
  * [Reporting total bytes read and bytes per request](#reporting-total-bytes-read-and-bytes-per-request)
  * [Reporting system call duration](#reporting-system-call-duration)
  * [Reporting request size](#reporting-request-size)
  * [Reporting a per-request finishing account balance](#reporting-a-per-request-finishing-account-balance)
  * [Reporting process-wide CPU usage](#reporting-process-wide-cpu-usage)
  * [Reporting per-shard memory holdings](#reporting-per-shard-memory-holdings)
  * [Reporting number of active requests](#reporting-number-of-active-requests)
  * [Reporting bytes read and written correlated by end user](#reporting-bytes-read-and-written-correlated-by-end-user)

<!-- tocstop -->

## Overview

The OpenTelemetry Metrics API supports capturing measurements about
the execution of a computer program at run time.  The Metrics API is
designed explicitly for processing raw measurements, generally with
the intent to produce continuous summaries of those measurements,
efficiently and simultaneously.  Hereafter, "the API" refers to the
OpenTelemetry Metrics API.

The API provides functions for capturing raw measurements, through
several [calling
conventions](api-user.md#metric-calling-conventions) that
offer different levels of performance.  Regardless of calling
convention, we define a _metric event_ as the logical thing that
happens when a new measurement is captured.  This moment of capture
(at "run time") defines an implicit timestamp, which is the wall time
an SDK would read from a clock at that moment.

The word "semantic" or "semantics" as used here refers to _how we give
meaning_ to metric events, as they take place under the API.  The term
is used extensively in this document to define and explain these API
functions and how we should interpret them.  As far as possible, the
terminology used here tries to convey the intended semantics, and a
_standard implementation_ will be described below to help us
understand their meaning.  The standard implementation performs
aggregation corresponding to the default interpretation for each kind
of metric event.

Monitoring and alerting systems commonly use the data provided through
metric events, after applying various [aggregations](#aggregations)
and converting into various [exposition formats](#exposition-formats).
However, we find that there are many other uses for metric events,
such as to record aggregated or raw measurements in tracing and
logging systems.  For this reason, [OpenTelemetry requires a
separation of the API from the SDK](../library-guidelines.md#requirements),
so that different SDKs can be configured at run time.

### Metric Instruments

A _metric instrument_ is a device for capturing raw measurements in
the API.  There are six kinds of instrument, each with a dedicated
purpose.  The API purposefully avoids optional features that change
the semantic interpretation of an instrument; the API instead prefers
instruments that support a single method with fixed interpretation.

All measurements captured by the API are associated with an
instrument, which gives the measurement its semantic properties.
Instruments are created and defined through calls to a `Meter` API,
which is the user-facing entry point to the SDK.

Instruments are classified in several ways that distinguish them from
one another.

1. Synchronicity: A synchronous instrument is called by the user in an OpenTelemetry [Context](../context/context.md). An asynchronous instrument is called by the SDK once per collection interval, lacking a Context.
2. Additivity: An additive instrument is used to capture information about a sum of values.  A non-additive instrument is used to capture information about individual values.
3. Monotonicity: An additive instrument can be monotonic, when the sequence of captured sums is non-descending.  Monotonic instruments are useful for monitoring rate information.

The metric instruments names are shown below along with whether they
are synchronous, additive, and/or monotonic.

| Name | Synchronous | Additive | Monotonic |
| ---- | ----------- | -------- | --------- |
| Counter           | Yes | Yes | Yes |
| UpDownCounter     | Yes | Yes | No  |
| ValueRecorder     | Yes | No  | No  |
| SumObserver       | No  | Yes | Yes |
| UpDownSumObserver | No  | Yes | No  |
| ValueObserver     | No  | No  | No  |

The synchronous instruments are useful for measurements that are
gathered in a tracing context.  The asynchronous instruments are
useful when measurements are expensive, therefore should be gathered
periodically.  Read more [characteristics of synchronous and
asynchronous instruments](TODO) below.

The additive instruments are useful in situations where we are only
interested in the sum, as this enables significant optimizations in
the export pipeline.  The synchronous and asynchronous additive
instruments have a significant difference: synchronous instruments are
used to capture changes in a sum, whereas asynchronous instruments are
used to capture sums directly.  Read more [characteristics of additive
instruments](TODO) below.

The monotonic instruments are significant because they support rate
calculations.  Read more information about [choosing metric
instruments](TODO) below.

An _instrument definition_ describes several properties of the
instrument, including its name and its kind.  The other properties of
a metric instrument are optional, including a description and the unit
of measurement.  An instrument definition is associated with the
events that it produces.

Details about calling conventions for each kind of instrument are
covered in the [user-level API specification](api-user.md).

### Labels

_Label_ is the term used to refer to a key-value attribute associated
with a metric event, similar to a [Span
attribute](../trace/api.md#span) in the tracing API.  Each label
categorizes the metric event, allowing events to be filtered and
grouped for analysis.

Each of the instrument calling conventions detailed in the [user-level
API specification](api-user.md) accepts a list of labels as an
argument, which are used to compute a label set.  The set of labels is
defined as a unique mapping from key to value, but since they are
passed in as a list, the specification dictates that duplicate keys are
empowersresolved by taking the last value to appear in the list.  This is known
as "last-value wins".

Measurements by a synchronous instrument are commonly combined with
other measurements having exactly the same label set, which enables
significant optimizations.  Read more about [combining measurements
through aggregation](TODO) below.

Asynchronous instruments are permitted to observe at most one value
per distinct label set, per callback invocation.  Read more about
[current label sets for asynchronous instruments](TODO) below.

### Meter Interface

To produce measurements using an instrument, you need an SDK that implements
the `Meter` API.  This interface consists of a set of instrument constructors,
and a facility for capturing batches of measurements in a semantically atomic
way.

There is a global `Meter` instance available for use that facilitates
automatic instrumentation for third-party code.  Use of this instance
allows code to statically initialize its metric instruments, without
explicit dependency injection.  The global `Meter` instance acts as a
no-op implementation until the application explicitly initializes a
global `Meter` by installing an SDK.  Note that it is not necessary to
use the global instance: multiple instances of the OpenTelemetry SDK
may run simultaneously.

As an obligatory step, the API requires the caller to provide the name
of the instrumenting library (optionally, the version) when obtaining
a `Meter` implementation.  The library name is meant to be used for
identifying instrumentation produced from that library, for such
purposes as disabling instrumentation, configuring aggregation, and
applying sampling policies.  See the specification on [obtaining a
Tracer](../trace/api.md#obtaining-a-tracer) for more details.

Details about installing an SDK and obtaining a named `Meter` are
covered in the [SDK-level API specification](api-meter.md).

### Aggregations

_Aggregation_ refers to the process of combining multiple measurements
into exact or estimated statistics about the metric
events that took place during an interval time, during program
execution.

Each instrument specifies a default aggregation that is suited to the
semantics of the instrument, that serves to explain its properties and
give users an understanding of how it is meant to be used.
Instruments, in the absence of any configuration override, can be
expected to deliver a useful, economical aggregation out of the box.

The additive instruments (`Counter`, `UpDownCounter`, `SumObserver`,
`UpDownSumObserver`) use Sum aggregation, by default.  Details about
computing a Sum aggregation vary, but from the user's perspective this
means they will be able to monitor the sum of values entered.  The
distinction between synchronous and asynchronous instruments is
crucial to specifying how exporters work, a topic that is covered in
the [SDK specification](TODO).

The non-additive instruments (`ValueRecorder`, `ValueObserver`) use
MinMaxSumCount aggregation, by default.  This aggregation keeps track
of the minimum value, the maximum value, the sum of values, and the
count of values.  These four values support monitoring the range of
values, the rate of events, and the average event value.  

Other standard aggregations are available, especially for non-additive
instruments, where we are generally interested in a variety of
different summaries, such as histograms, quantile summaries,
cardinality estimates, and other kinds of sketch data structure.

The default OpenTelemetry SDK implements a [Views API](TODO), which
supports configuring non-default aggregation behavior(s) on the level
of an individual instrument.  Even though OpenTelemetry SDKs can be
configured to treat instruments in non-standard ways, users are
expected to select instruments based on their semantic meaning, which
is explained using the default aggregation.

### Time

Time is a fundamental property of metric events, but not an explicit
one.  Users do not provide explicit timestamps for metric events.
SDKs are discouraged from capturing the current timestamp for each
event (by reading from a clock) unless there is a definite need for
high-precision timestamps calculated on every event.

This non-requirement stems from a common optimization in metrics
reporting, which is to configure metric data collection with a
relatively small period (e.g., 1 second) and use a single timestamp to
describe a batch of exported data, since the loss of precision is
insignificant when aggregating data across minutes or hours of data.

Aggregations are commonly computed over a series of events that fall
into a contiguous region of time, known as the collection interval.
Since the SDK controls the decision to start collection, it is possible to
collect aggregated metric data while only reading the clock once per
collection interval.  The default SDK takes this approach.

Metric events produced with synchronous instruments happen at an
instant in time, thus fall into a collection interval where they are
aggregated together with other events from the same instrument and
label set.  Because events may happen simultaneously with one another,
the _most recent event_ is technically not well defined.

Asynchronous instruments allow the SDK to evaluate metric instruments
through observations made once per collection interval.  Because they
are synchronized with collection (unlike synchronous instruments),
these instruments unambiguously define the most recent event.  We
define the _Last Value_ of an instrument and label set, with repect to
a moment in time, as the value that was measured during the most
recent prior collection interval.

Because metric events are implicitly timestamped, we could refer to a
series of metric events as a _time series_. However, we reserve the
use of this term for the SDK specification, to refer to parts of a
data format that express explicitly timestamped values, in a sequence,
resulting from an aggregation of raw measurements over time.

### Metric Event Format

Metric events have the same logical representation, regardless of
instrument kind.  Metric events captured through any instrument
consist of:

- timestamp (implicit)
- instrument definition (name, kind, description, unit of measure)
- label set (keys and values)
- value (signed integer or floating point number)
- [resources](../resource/sdk.md) associated with the SDK at startup.

Synchronous events have one additional property, the distributed
[Context](../context/context.md) (Span context, Correlation context)
that was active at the time.

## Instrument categories

Because the API is separated from the SDK, the implementation
ultimately determines how metric events are handled.  Therefore, the
choice of instrument should be guided by semantics and the intended
interpretation.  Here we detail the instruments and their
individual semantics.

### Synchronous and asynchronous instruments compared

Synchronous instruments are called in a request context, meaning they
potentially have an associated tracing context and distributed
correlation values.  Multiple metric events may occur for a
synchronous instrument within a given collection interval.

Asynchronous instruments are reported by a callback, once per
collection interval, and lack request context.  They are permitted to
report only one value per distinct label set per period.  If the
application observes multiple values for the same label set, in a
single callback, the last value "wins".

To ensure that the definition of last value is consistent across
asynchronous instruments, the timestamp associated with asynchronous
events is fixed to the timestamp at the end of the interval in which
it was computed.  All asynchronous events are timestamped with the end
of the interval, which is the moment they become the last value
corresponding to the instrument and label set.  (For this reasons,
SDKs SHOULD capture observer instruments near the end of the
collection interval.)

### Additive and non-additive instruments compared

Additive instruments are used to capture information about a sum,
where, by definition, only the sum is of interest.  Individual events
are considered not meaningful for these instruments, the event count
is not computed.  This means, for example, that two `Counter` events
`Add(N)` and `Add(M)` are equivalent to one `Counter` event `Add(N +
M)`.  This is the case because `Counter` is synchronous, and
synchronous additive instruments are used to capture changes to a sum.

Asynchronous, additive instruments (e.g., `SumObserver`) are used to
capture sums directly.  This means, for example, that in any sequence
of `SumObserver` observations for a given instrument and label set,
the Last Value defines the sum of the instrument.

In both synchronous and asynchronous cases, the additive instruments
are easily aggregated into a single number per collection interval
without loss of information.  This property makes additive instruments
higher performance, in general, than non-additive instruments.

Non-additive instruments use a relatively inexpensive aggregation by
method default (MinMaxSumCount), but still more expensive than the
default for additive instruments (Sum).  Unlike additive instruments,
where only the sum is of interest by definition, non-additive
instruments can be configured with even more expensive aggregators.

### Monotonic and non-monotonic instruments compared

Monotonicity applies only to additive instruments.  `Counter` and
`SumObserver` instruments are defined as monotonic because the sum
captured by either instrument is non-descending.  The `UpDown-`
varations of these two instruments are non-monotonic, meaning the sum
is ascending or descending.

Monotonic instruments are commonly used to capture information about a
sum, where the sum itself is less relevant than the rate expressed by
the sum's change over time.  The Monotonic property is defined by this
API to refer to a non-decreasing sum.  Non-increasing sums are not
considered a feature in the Metric API.

### Function names

Each instrument supports a single function, named to help convey the
instrument's semantics.

Synchronous additive instruments support an `Add()` function,
signifying that they add to a sum and do not directly capture a sum.

Synchronous non-additive instruments support a `Record()` function,
signifying that they capture individual events, not only a sum.

Asynchronous instruments all support an `Observe()` function,
signifying that they capture only one value per measurement interval.

## Instrument kinds

### Counter

`Counter` is the most common synchronous instrument.  This instrument
supports an `Add(increment)` function for reporting a sum, and is
restricted to non-negative increments.  The default aggregation is
`Sum`, as for any additive instrument.

Example uses for `Counter`:
- count the number of bytes received
- count the number of accounts created
- count the number of checkpoints run
- count a number of 5xx errors.

These example instruments would be useful for monitoring the rate of
any of these quantities.  In these situations, it is usually more
convenient to report by how much a sum changes, as it happens, than to
calculate and report the sum on every measurement.

### UpDownCounter

`UpDownCounter` is similar to `Counter` except that `Add(increment)`
supports negative increments.  This makes `UpDownCounter` not useful
for computing a rate aggregation.  It aggregates a `Sum`, only the sum
is non-monotonic.  It is generally useful for capturing changes in an
amount of resources used, or any quantity that rises and falls in a
request context.

Example uses for `UpDownCounter`:
- count memory in use by instrumenting `new` and `delete`
- count queue size by instrumenting `enqueue` and `dequeue`
- count semaphore `up` and `down` operations.

These example instruments would be useful for monitoring resource
levels across a group of processes.

### ValueRecorder

`ValueRecorder` is a non-additive synchronous instrument useful for
recording any non-additive number, positive or negative.  Values
captured by a `ValueRecorder` are treated as individual events
belonging to a distribution that is being summarized.  `ValueRecorder`
should be chosen either when capturing measurements that do not
contribute meaningfully to a sum, or when capturing numbers that are
additive in nature, but where the distribution of individual
increments is considered interesting.

One of the most common uses for `ValueRecorder` is to capture latency
measurements.  Latency measurements are not additive in the sense that
there is little need to know the latency-sum of all processed
requests.  We use a `ValueRecorder` instrument to capture latency
measurements typically because we are interested in knowing mean,
median, and other summary statistics about individual events.

The default aggregation for `ValueRecorder` computes the minimum and
maximum values, the sum of event values, and the count of events,
allowing the rate, the mean, and and range of input values to be
monitored.

Example uses for `ValueRecorder` that are non-additive:
- capture any kind of timing information
- capture the acceleration experienced by a pilot
- capture nozzle pressure of a fuel injector
- capture the velocity of a MIDI key-press.

Example _additive_ uses of `ValueRecorder` capture measurements that
are additive, but where we may have an interest in the distribution of
values and not only the sum:
- capture a request size
- capture an account balance
- capture a queue length
- capture a number of board feet of lumber.

These examples show that although they are additive in nature,
choosing `ValueRecorder` as opposed to `Counter` or `UpDownCounter`
implies an interest in more than the sum.  If you did not care to
collect information about the distribution, you would have chosen one
of the additive instruments instead.  Using `ValueRecorder` makes
sense for capturing distributions that are likely to be important in
an observability setting.

Use these with caution because they naturally cost more than the use
of additive measurements.

### SumObserver

`SumObserver` is the asynchronous instrument corresponding to
`Counter`, used to capture a monotonic sum.  "Sum" appears in the
name to remind users that it is used to capture sums directly.  Use a
`SumObserver` to capture any value that starts at zero and rises
throughout the process lifetime and never falls.

Example uses for `SumObserver`.
- capture process user/system CPU seconds
- capture the number of cache misses.

A `SumObserver` is a good choice in situations where a measurement is
expensive to compute, such that it would be wasteful to compute on
every request.  For example, a system call is needed to capture
process CPU usage, therefore it should be done periodically, not on
each request.  A `SumObserver` is also a good choice in situations
where it would be impractical or wasteful to instrument individual
changes that comprise a sum.  For example, even though the number of
cache misses is a sum of individual cache-miss events, it would be too
expensive to synchronously capture each event using a `Counter`.

### UpDownSumObserver

`UpDownSumObserver` is the asynchronous instrument corresponding to
`UpDownCounter`, used to capture a non-monotonic count.  "Sum" appears
in the name to remind users that it is used to capture sums directly.
Use a `UpDownSumObserver` to capture any value that starts at zero and
rises or falls throughout the process lifetime.

Example uses for `UpDownSumObserver`.
- capture process heap size
- capture number of active shards
- capture number of requests started/completed
- capture current queue size.

The same considerations mentioned for choosing `SumObserver` over the
synchronous `Counter` apply for choosing `UpDownSumObserver` over the
synchronous `UpDownCounter`.  If a measurement is expensive to
compute, or if the corresponding changes happen so frequently that it
would be impractical to instrument them, use a `UpDownSumObserver`.

### ValueObserver

`ValueObserver` is the asynchronous instrument corresponding to
`ValueRecorder`, used to capture non-additive measurements that are
expensive to compute and/or are not request-oriented.

Example uses for `ValueObserver`:
- capture CPU fan speed
- capture CPU temperature.

Note that these examples use non-additive measurements.  In the
`ValueRecorder` case above, example uses were given for capturing
synchronous cumulative measurements in a request context (e.g.,
current queue size seen by a request).  In the asynchronous case,
however, how should users decide whether to use `ValueObserver` as
opposed to `UpDownSumObserver`?

Consider how to report the size of a queue asynchronously.  Both
`ValueObserver` and `UpDownSumObserver` logically apply in this case.
Asynchronous instruments capture only one measurement per interval, so
in this example the `SumObserver` reports a current sum, while the
`ValueObserver` reports a current sum (equal to the max and the min)
and a count equal to 1.  When there is no aggregation, these results
are equivalent.

The recommendation is to choose the instrument with the
more-appropriate default aggregation.  If you are observing a queue
size across a group of machines and the only thing you want to know is
the aggregate queue size, use `SumObserver`.  If you are observing a
queue size across a group of machines and you are interested in
knowing the distribution of queue sizes across those machines, use
`ValueObserver`.

@@@

### Observer

Observer instruments are used to capture a _current set of values_ at
a point in time.  Observer instruments are asynchronous, with the use
of callbacks allowing the user to capture multiple values per
collection interval.  Observer instruments are not associated with a
Context, by definition.  This means, for example, it is not possible
to associate Observer instrument events with Correlation or Span
context.

Observer instruments capture not only current values, but also effectively
_which labels are current_ at the moment of collection.  These instruments can
be used to compute probabilities and ratios, because values are part of a set.

Unlike Counter and Measure instruments, Observer instruments are
synchronized with collection.  There is no aggregation across time for
Observer instruments by definition, only the current set of values is
semantically defined.  Because Observer instruments are activated by
the SDK, they can be effectively disabled at low cost.

These values are considered coherent, because measurements from an
Observer instrument in a single collection interval are captured at
the same logical time.  A single callback invocation generates (zero
or more) simultaneous metric events, all sharing an implicit timestamp.

## Interpretation

We believe the three instrument kinds Counter, Measure, and Observer
form a sufficient basis for expressing nearly all metric data.  But if
the API and SDK are separated, and the SDK can handle any metric event
as it pleases, why not have just one kind of instrument?  How are the
instruments fundamentally different, and why are there only three?

Establishing different kinds of instrument is important because in
most cases it allows the SDK to provide good default functionality,
without requiring alternative behaviors to be configured.  The choice
of instrument determines not only the meaning of the events but also
the name of the function used to report data.  The function
names--`Add()` for Counter instruments, `Record()` for Measure
instruments, and `Observe()` for Observer instruments--help convey the
meaning of these actions.

### Standard implementation

The standard implementation for the three instruments is defined as
follows:

1. Counter.  The `Add()` function accumulates a total for each distinct set of labels.  When aggregating over labels for a Counter, combine using arithmetic addition and export as a sum. Depending on the exposition format, sums are exported either as pairs of labels and cumulative _delta_ or as pairs of labels and cumulative _total_.

2. Measure.  Use the `Record()` function to report events for which the SDK will compute summary statistics about the distribution of values, for each distinct set of labels.  The summary statistics to use are determined by the aggregation, but they usually include at least the sum of values, the count of measurements, and the minimum and maximum values.  When aggregating distinct Measure events, report summary statistics of the combined value distribution.  Exposition formats for summary statistics vary widely, but typically include pairs of labels and (sum, count, minimum and maximum value).

3. Observer.  Current values are provided by the Observer callback at the end of each Metric collection period.  When aggregating values _for the same set of labels_, combine using the most-recent value.  When aggregating values _for different sets of labels_, combine the value distribution as for Measure instruments.  Export as pairs of labels and (sum, count, minimum and maximum value).

We believe that the standard behavior of one of these three
instruments covers nearly all use-cases for users of OpenTelemetry in
terms of the intended semantics.

### Future Work: Option Support

We are aware of a number of reasons to iterate on these
instrumentation kinds, in order to offer:

1. Range restrictions on input data.  Instruments accepting negative values is rare in most applications, for example, and it is useful to offer both a semantic declaration (e.g., "negative values are meaningless") and a data validation step (e.g., "negative values should be dropped").
2. Monotonicity support.  When a series of values is known to be monotonic, it is useful to declare this..

For the most part, these behaviors are not necessary for correctness
within the local process or the SDK, but they are valuable in
down-stream services that use this data.  We look to future work on
this subject.

### Future Work: Configurable Aggregations / View API

The API does not support configurable aggregations, in this
specification.  This is a requirement for OpenTelemetry, but there are
two ways this has been requested.

A _View API_ is defined as an interface to an SDK mechanism that
supports configuring aggregations, including which operator is applied
(sum, p99, last-value, etc.) and which dimensions are used.

1. Should the API user be provided with options to configure specific views, statically, in the source?
2. Should the View API be a stand-alone facility, able to install configurable aggregations, at runtime?

See the [current issue on this topic](https://github.com/open-telemetry/opentelemetry-specification/issues/466).

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
