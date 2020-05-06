# Metrics API

<!-- toc -->

- [Overview](#overview)
  * [Metric Instruments](#metric-instruments)
  * [Labels](#labels)
  * [Meter Interface](#meter-interface)
  * [Aggregations](#aggregations)
  * [Time](#time)
  * [Metric Event Format](#metric-event-format)
- [Instrument properties](#instrument-properties)
  * [Synchronous and asynchronous instruments compared](#synchronous-and-asynchronous-instruments-compared)
  * [Additive and non-additive instruments compared](#additive-and-non-additive-instruments-compared)
  * [Monotonic and non-monotonic instruments compared](#monotonic-and-non-monotonic-instruments-compared)
  * [Function names](#function-names)
- [Six kinds of instrument](#six-kinds-of-instrument)
  * [Counter](#counter)
  * [UpDownCounter](#updowncounter)
  * [ValueRecorder](#valuerecorder)
  * [SumObserver](#sumobserver)
  * [UpDownSumObserver](#updownsumobserver)
  * [ValueObserver](#valueobserver)
- [Interpretation](#interpretation)
- [User-facing API specification with examples](#user-facing-api-specification-with-examples)
- [Details](#details)
  * [Memory requirements](#memory-requirements)
  * [Asynchronous observations form a current set](#asynchronous-observations-form-a-current-set)
    + [Asynchronous instruments define moment-in-time ratios](#asynchronous-instruments-define-moment-in-time-ratios)
  * [Related OpenTelemetry work](#related-opentelemetry-work)
    + [Metric Views](#metric-views)
    + [OTLP Metric protocol](#otlp-metric-protocol)
  * [Metric SDK default implementation](#metric-sdk-default-implementation)

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

All measurements captured by the API are associated with
instrument used to make the measurement, thus giving the measurement its semantic properties.
Instruments are created and defined through calls to a `Meter` API,
which is the user-facing entry point to the SDK.

Instruments are classified in several ways that distinguish them from
one another.

1. Synchronicity: A synchronous instrument is called by the user in an OpenTelemetry [Context](../context/context.md). An asynchronous instrument is called by the SDK once per collection interval, lacking a Context.
2. Additivity: An additive instrument is used to capture information about a sum of values.  A non-additive instrument is used to capture information about individual values.
3. Monotonicity: An additive instrument can be monotonic, when the sequence of captured sums is non-decreasing.  Monotonic instruments are useful for monitoring rate information.

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
asynchronous instruments](#synchronous-and-asynchronous-instruments-compared) below.

The additive instruments are useful in situations where we are only
interested in the sum, as this enables significant optimizations in
the export pipeline.  The synchronous and asynchronous additive
instruments have a significant difference: synchronous instruments are
used to capture changes in a sum, whereas asynchronous instruments are
used to capture sums directly.  Read more [characteristics of additive
instruments](#additive-and-non-additive-instruments-compared) below.

The monotonic instruments are significant because they support rate
calculations.  Read more information about [choosing metric
instruments](#monotonic-and-non-monotonic-instruments-compared) below.

An _instrument definition_ describes several properties of the
instrument, including its name and its kind.  The other properties of
a metric instrument are optional, including a description and the unit
of measurement.  An instrument definition is associated with the
data that it produces.

Details about calling conventions for each kind of instrument are
covered in the [user-level API specification](api-user.md).

### Labels

_Label_ is the term used to refer to a key-value attribute associated
with a metric event, similar to a [Span
attribute](../trace/api.md#span) in the tracing API.  Each label
categorizes the metric event, allowing events to be filtered and
grouped for analysis.

Each of the instrument calling conventions detailed in the [user-level
API specification](api-user.md) accepts a set of labels as an
argument.  The set of labels is defined as a unique mapping from key to value.
Typically, labels are passed to the API in the form of a list of
key:values, in which case the specification dictates that duplicate
entries for a key are resolved by taking the last value to appear in the list.
This is known as "last-value wins".

Measurements by a synchronous instrument are commonly combined with
other measurements having exactly the same label set, which enables
significant optimizations.  Read more about [combining measurements
through aggregation](#aggregations) below.

Asynchronous instruments are permitted to observe at most one value
per distinct label set, per callback invocation.  Read more about
[current label sets for asynchronous instruments](#asynchronous-observations-form-a-current-set) below.

### Meter Interface

The API defines a `Meter` interface.  This interface consists of a set
of instrument constructors, and a facility for capturing batches of
measurements in a semantically atomic way.

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
into exact or estimated statistics about the measurements that took
place during an interval of time, during program execution.

Each instrument specifies a default aggregation that is suited to the
semantics of the instrument, that serves to explain its properties and
give users an understanding of how it is meant to be used.
Instruments, in the absence of any configuration override, can be
expected to deliver a useful, economical aggregation out of the box.

The additive instruments (`Counter`, `UpDownCounter`, `SumObserver`,
`UpDownSumObserver`) use a Sum aggregation by default.  Details about
computing a Sum aggregation vary, but from the user's perspective this
means they will be able to monitor the sum of values captured.  The
distinction between synchronous and asynchronous instruments is
crucial to specifying how exporters work, a topic that is covered in
the [SDK specification](TODO).

The non-additive instruments (`ValueRecorder`, `ValueObserver`) use
a MinMaxSumCount aggregation, by default.  This aggregation keeps track
of the minimum value, the maximum value, the sum of values, and the
count of values.  These four values support monitoring the range of
values, the rate of events, and the average event value.

Other standard aggregations are available, especially for non-additive
instruments, where we are generally interested in a variety of
different summaries, such as histograms, quantile summaries,
cardinality estimates, and other kinds of sketch data structure.

The default OpenTelemetry SDK implements a [Views API (WIP)](TODO), which
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
through observations made once per collection interval.  Because of this
coupling with collection (unlike synchronous instruments),
these instruments unambiguously define the most recent event.  We
define the _Last Value_ of an instrument and label set, with repect to
a moment in time, as the value that was measured during the most
recent collection interval.

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

## Instrument properties

Because the API is separated from the SDK, the implementation
ultimately determines how metric events are handled.  Therefore, the
choice of instrument should be guided by semantics and the intended
interpretation.  The semantics of the individual instruments is
defined by several properties, detailed here, to assist with
instrument selection.

### Synchronous and asynchronous instruments compared

Synchronous instruments are called in a request context, meaning they
have an associated tracing context and distributed
correlation values.  Multiple metric events may occur for a
synchronous instrument within a given collection interval.

Asynchronous instruments are reported by a callback, once per
collection interval, and lack request context.  They are permitted to
report only one value per distinct label set per period.  If the
application observes multiple values for the same label set, in a
single callback, the last value is the only value kept.

To ensure that the definition of last value is consistent across
asynchronous instruments, the timestamp associated with asynchronous
events is fixed to the timestamp at the end of the interval in which
it was computed.  All asynchronous events are timestamped with the end
of the interval, which is the moment they become the last value
corresponding to the instrument and label set.  (For this reasons,
SDKs SHOULD run asynchronous instrument callbacks near the end of the
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
are inexpensively aggregated into a single number per collection interval
without loss of information.  This property makes additive instruments
higher performance, in general, than non-additive instruments.

Non-additive instruments use a relatively inexpensive aggregation
method default (MinMaxSumCount), but still more expensive than the
default for additive instruments (Sum).  Unlike additive instruments,
where only the sum is of interest by definition, non-additive
instruments can be configured with even more expensive aggregators.

### Monotonic and non-monotonic instruments compared

Monotonicity applies only to additive instruments.  `Counter` and
`SumObserver` instruments are defined as monotonic because the sum
captured by either instrument is non-decreasing.  The `UpDown-`
varations of these two instruments are non-monotonic, meaning the sum
can increase, decrease, or remain constant without any guarantees.

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

## Six kinds of instrument

### Counter

`Counter` is the most common synchronous instrument.  This instrument
supports an `Add(increment)` function for reporting a sum, and is
restricted to non-negative increments.  The default aggregation is
`Sum`, as for any additive instrument.

Example uses for `Counter`:

- count the number of bytes received
- count the number of accounts created
- count the number of checkpoints run
- count the number of 5xx errors.

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
captured by a `Record(value)` are treated as individual events
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
`Counter`, used to capture a monotonic sum with `Observe(sum)`.  "Sum"
appears in the name to remind users that it is used to capture sums
directly.  Use a `SumObserver` to capture any value that starts at
zero and rises throughout the process lifetime and never falls.

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
`UpDownCounter`, used to capture a non-monotonic count with
`Observe(sum)`.  "Sum" appears in the name to remind users that it is
used to capture sums directly.  Use a `UpDownSumObserver` to capture
any value that starts at zero and rises or falls throughout the
process lifetime.

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
`ValueRecorder`, used to capture non-additive measurements with
`Observe(value)`.  These instruments are especially useful for
capturing measurements that are expensive to compute, since it gives
the SDK control over how often they are evaluated.

Example uses for `ValueObserver`:

- capture CPU fan speed
- capture CPU temperature.

Note that these examples use non-additive measurements.  In the
`ValueRecorder` case above, example uses were given for capturing
synchronous additive measurements in a request context (e.g.,
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

It may seem pointless to define a default aggregation when there is
exactly one data point.  The default aggregation is specified to apply
when performing spatial aggregation, meaning to combine measurements
across label sets or in a distributed setting.  Although a
`ValueObserver` observes one value per collection interval, the
default aggregation specifies how it will be aggregated with other
values, absent any other configuration.

Therefore, considering the choice between `ValueObserver` and
`UpDownSumObserver`, the recommendation is to choose the instrument
with the more-appropriate default aggregation.  If you are observing a
queue size across a group of machines and the only thing you want to
know is the aggregate queue size, use `SumObserver` because it
produces a sum, not a distribution.  If you are observing a queue size
across a group of machines and you are interested in knowing the
distribution of queue sizes across those machines, use
`ValueObserver`.

## Interpretation

How are the instruments fundamentally different, and why are there
only three?  Why not one instrument?  Why not ten?

As we have seen, the six instruments are categorized as to whether
they are synchronous, additive, and/or and monotonic.  This approach
gives each of the six instruments unique semantics, in ways that
meaningfully improve the performance and interpreation of metric
events.

Establishing different kinds of instrument is important because in
most cases it allows the SDK to provide good default functionality
"out of the box", without requiring alternative behaviors to be
configured.  The choice of instrument determines not only the meaning
of the events but also the name of the function called by the user.
The function names--`Add()` for additive instruments, `Record()` for
non-additive instruments, and `Observe()` for asynchronous
instruments--help convey the meaning of these actions.

The properties and standard implementation described for the
individual instruments is summarized in the table below.

| **Name** | Instrument kind | Function(argument) | Default aggregation | Notes |
| ----------------------- | ----- | --------- | ------------- | --- |
| **Counter**             | Synchronous additive monotonic | Add(increment) | Sum | Per-request, part of a monotonic sum |
| **UpDownCounter**       | Synchronous additive | Add(increment) | Sum | Per-request, part of a non-monotonic sum |
| **ValueRecorder**       | Synchronous  | Record(value) | MinMaxSumCount  | Per-request, any non-additive measurement |
| **SumObserver**         | Asynchronous additive monotonic | Observe(sum) | Sum | Per-interval, reporting a monotonic sum |
| **UpDownSumObserver**   | Asynchronous additive | Observe(sum) | Sum | Per-interval, reporting a non-monotonic sum |
| **ValueObserver**       | Asynchronous | Observe(value) | MinMaxSumCount  | Per-interval, any non-additive measurement |

## User-facing API specification with examples

See the [user-level API specification](api-user.md) for more description of the
user-facing, function-level Metrics API, including the the calling
conventions.  [Examples and guides for selecting instruments are
included for users in this document](api-user.md).

## Details

### Memory requirements

The API is designed not to impose long-lived memory requirements on
the user, although for some exporters it cannot be avoided.  The
potential for unbounded memory growth comes from "momentary-use"
labels, labels which are used briefly and then are not used again.
If the SDK is required to retain memory of every combination of
instrument and label set it has ever seen, long-lived memory can
become a problem.

Nevertheless, exporters may be forced to allocate long-lived memory to
perform their function, particularly with respect to the additive
instruments.  Metric exposition formats commonly have two ways of
exposing additive instrument data: in terms of the change in a sum, or
in terms of the sum itself.  (The terms "delta" and "cumulative" are
used to describe these two approaches in an export pipeline, we avoid
their use to describe the additive instruments.)

There are two cases where an exporter must retain memory in order to
operate correctly.

1. An exporter that exports sums but receives changes in the sum
2. An exporter that exports changes in a sum but receives the sum.

In both of these cases, the exporter must maintain memory of the last
value of the sum, to convert between the two representations of
additive data when both forms of input are present.

An exporter can avoid this memory requirement by supporting exposition
of additive metric data in both ways, as with the [OpenTelemetry
protocol
buffer](https://github.com/open-telemetry/opentelemetry-proto) (OTLP).
A client configured to export OTLP does not have a long-lived
memory requirement, because that protocol supports both forms of
additive data.  Although, the memory requirement then arises in the
downstream system for any exporter that does not support both forms.

It is tempting to consider not supporting one of these forms of
additive metric data, as a way to avoid exporter memory requirements.
However, legacy protocols exist with both forms, so this would not
necessarily help.  Besides, the fact that synchronous additive
instruments accept one, while asynchronous additive instruments
accepts the other, is ultimately meant as a user convenience.  Had
OpenTelemetry not specified that asynchronous additive instruments
accept sums directly, this burden would fall to the user (e.g., since
operating systems report heap usage as a sum, the user would be forced
into a memory requirement in order to report changes in the sum).

### Asynchronous observations form a current set

Asynchronous instrument callbacks are permitted to observe one value
per instrument, per distinct label set, per callback invocation.  The
set of values recorded by one callback invocation represent a current
snapshot of the instrument; it is this set of values that defines the
Last Value for the instrument until the next collection interval.

Asynchronous instruments are expected to record an observation for
every label set that it considers "current".  This means that
asynchronous callbacks are expected to observe a value, even when the
value has not changed since the last callback invocation.  To not
observe a label set implies that a value is no longer current.  The
Last Value becomes undefined, as it is no longer current, when it is
not observed during a collection interval.

The definition of Last Value is possible for asynchronous instruments,
because their collection is coordinated by the SDK and because they
are expected to report all current values.  Another expression of this
property is that an SDK can keep just one collection interval worth of
observations in memory to lookup the current Last Value of any
instrument and label set.  In this way, asynchronous instruments
support querying current values, independent of the duration of a
collection interval, using data collected at a single point in time.

Recall that Last Value is not defined for synchronous instruments, and
it is precisely because there is not a well-defined notion of what is
"current".  To determine the "last-recorded" value for a synchronous
instrument could require inspecting multiple collection windows of
data, because there is no mechanism to ensure that a current value is
recorded during each interval.

#### Asynchronous instruments define moment-in-time ratios

The notion of a current set developed for asynchronous instruments
above can be useful for monitoring ratios.  When the set of observed
values for an instrument add up to a whole, then each observation may
be divided by the sum of observed values from the same interval to
calculate its current relative contribution.  Current relative
contribution is defined in this way, independent of the collection
interval duration, thanks to the properties of asynchronous
instruments.

### Related OpenTelemetry work

Several ongoing efforts are underway as this specification is being
written.

#### Metric Views

The API does not support configurable aggregations for metric
instruments.

A _View API_ is defined as an interface to an SDK mechanism that
supports configuring aggregations, including which operator is applied
(sum, p99, last-value, etc.) and which dimensions are used.

See the [current issue discussion on this topic](https://github.com/open-telemetry/opentelemetry-specification/issues/466) and the [current OTEP draft](https://github.com/open-telemetry/oteps/pull/89).

#### OTLP Metric protocol

The OTLP protocol is designed to export metric data in a memoryless
way, as documented above.  Several details of the protocol are being
worked out.  See the [current protocol](https://github.com/open-telemetry/opentelemetry-proto/blob/master/opentelemetry/proto/metrics/v1/metrics.proto).

### Metric SDK default implementation

The OpenTelemetry SDK includes default support for the metric API.  The specification for the default SDK is underway, see the [current draft](https://github.com/open-telemetry/opentelemetry-specification/pull/347).
