# Metrics API

**Status**: [Experimental](../document-status.md)

**Owner:**

* [Reiley Yang](https://github.com/reyang)

**Domain Experts:**

* [Bogdan Brutu](https://github.com/bogdandrutu)
* [Josh Suereth](https://github.com/jsuereth)
* [Joshua MacDonald](https://github.com/jmacd)

Note: this specification is subject to major changes. To avoid thrusting
language client maintainers, we don't recommend OpenTelemetry clients to start
the implementation unless explicitly communicated via
[OTEP](https://github.com/open-telemetry/oteps#opentelemetry-enhancement-proposal-otep).

<!-- toc -->

- [Overview](#overview)
  * [Measurements](#measurements)
  * [Metric Instruments](#metric-instruments)
  * [Labels](#labels)
  * [Meter Interface](#meter-interface)
  * [Aggregations](#aggregations)
  * [Time](#time)
  * [Metric Event Format](#metric-event-format)
- [Meter provider](#meter-provider)
  * [Obtaining a Meter](#obtaining-a-meter)
  * [Global Meter provider](#global-meter-provider)
    + [Get the global MeterProvider](#get-the-global-meterprovider)
    + [Set the global MeterProvider](#set-the-global-meterprovider)
- [Instrument properties](#instrument-properties)
  * [Instrument naming requirements](#instrument-naming-requirements)
  * [Synchronous and asynchronous instruments compared](#synchronous-and-asynchronous-instruments-compared)
  * [Adding and grouping instruments compared](#adding-and-grouping-instruments-compared)
  * [Monotonic and non-monotonic instruments compared](#monotonic-and-non-monotonic-instruments-compared)
  * [Function names](#function-names)
- [The instruments](#the-instruments)
  * [Counter](#counter)
  * [UpDownCounter](#updowncounter)
  * [ValueRecorder](#valuerecorder)
  * [SumObserver](#sumobserver)
  * [UpDownSumObserver](#updownsumobserver)
  * [ValueObserver](#valueobserver)
  * [Interpretation](#interpretation)
  * [Constructors](#constructors)
- [Sets of labels](#sets-of-labels)
  * [Label performance](#label-performance)
  * [Option: Ordered labels](#option-ordered-labels)
- [Synchronous instrument details](#synchronous-instrument-details)
  * [Synchronous calling conventions](#synchronous-calling-conventions)
    + [Bound instrument calling convention](#bound-instrument-calling-convention)
    + [Direct instrument calling convention](#direct-instrument-calling-convention)
    + [RecordBatch calling convention](#recordbatch-calling-convention)
  * [Association with distributed context](#association-with-distributed-context)
    + [Baggage into metric labels](#baggage-into-metric-labels)
- [Asynchronous instrument details](#asynchronous-instrument-details)
  * [Asynchronous calling conventions](#asynchronous-calling-conventions)
    + [Single-instrument observer](#single-instrument-observer)
    + [Batch observer](#batch-observer)
  * [Asynchronous observations form a current set](#asynchronous-observations-form-a-current-set)
    + [Asynchronous instruments define moment-in-time ratios](#asynchronous-instruments-define-moment-in-time-ratios)
- [Concurrency](#concurrency)
- [Related OpenTelemetry work](#related-opentelemetry-work)
  * [Metric Views](#metric-views)
  * [OTLP Metric protocol](#otlp-metric-protocol)
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
several calling conventions that offer different levels of
performance.  Regardless of calling convention, we define a _metric
event_ as the logical thing that happens when a new measurement is
captured.  This moment of capture (at "run time") defines an implicit
timestamp, which is the wall time an SDK would read from a clock at
that moment.

The word "semantic" or "semantics" as used here refers to _how we give
meaning_ to metric events, as they take place under the API.  The term
is used extensively in this document to define and explain these API
functions and how we should interpret them.  As far as possible, the
terminology used here tries to convey the intended semantics, and a
_standard implementation_ will be described below to help us
understand their meaning.  Standard implementations perform
aggregation corresponding to the default interpretation for each kind
of metric event.

Monitoring and alerting systems commonly use the data provided through metric
events, after applying various [aggregations](#aggregations) and converting into
various exposition formats. However, we find that there are many other uses for
metric events, such as to record aggregated or raw measurements in tracing and
logging systems.  For this reason, [OpenTelemetry requires a separation of the
API from the SDK](../library-guidelines.md#requirements), so that different SDKs
can be configured at run time.

### Behavior of the API in the absence of an installed SDK

In the absence of an installed Metrics SDK, the Metrics API MUST consist only
of no-ops. None of the calls on any part of the API can have any side effects
or do anything meaningful. Meters MUST return no-op implementations of any
instruments. From a user's perspective, calls to these should be ignored without raising errors
(i.e., *no* `null` references MUST be returned in languages where accessing these results in errors).
The API MUST NOT throw exceptions on any calls made to it.

### Measurements

The term _capture_ is used in this document to describe the action
performed when the user passes a measurement to the API.  The result
of a capture depends on the configured SDK, and if there is no SDK
installed, the default action is to do nothing in response to captured
events.  This usage is intended to convey that _anything can happen_
with the measurement, depending on the SDK, but implying that the user
has put effort into taking some kind of measurement.  For both
performance and semantic reasons, the API let users choose between two
kinds of measurement.

The term _adding_ is used to specify a characteristic of some
measurements, meant to indicate that only the sum is considered useful
information.  These are measurements that you would naturally combine
using arithmetic addition, usually real quantities of something
(e.g., number of bytes).

Grouping measurements are used when the set of values, also known
as the population, is presumed to have useful information.  A
grouping measurement is either one that you would not naturally
combine using arithmetic addition (e.g., request latency), or it is a
measurement you would naturally add where the intention is to monitor
the distribution of values (e.g., queue size).  The median value is
considered useful information for grouping measurements.

Grouping instruments semantically capture more information than
adding instruments.  Grouping measurements are more expensive
than adding measurements, by this definition.  Users will choose
adding instruments except when they expect to get value from the
additional cost of information about individual values.  None of this
is to prevent an SDK from re-interpreting measurements based on
configuration.  Anything can happen with any kind of measurement.

### Metric Instruments

A _metric instrument_ is a device for capturing raw measurements in
the API.  The standard instruments, listed in the table below, each have a dedicated
purpose.  The API purposefully avoids optional features that change
the semantic interpretation of an instrument; the API instead prefers
instruments that support a single method each with fixed interpretation.

All measurements captured by the API are associated with the
instrument used to make the measurement, thus giving the measurement its semantic properties.
Instruments are created and defined through calls to a `Meter` API,
which is the user-facing entry point to the SDK.

Instruments are classified in several ways that distinguish them from
one another.

1. Synchronicity: A synchronous instrument is called by the user in a distributed [Context](../context/context.md) (i.e., with associated Span, Baggage, etc.). An asynchronous instrument is called by the SDK once per collection interval, lacking a Context.
2. Adding vs. Grouping: An adding instrument is one that records adding measurements, as opposed to a grouping instrument as described above.
3. Monotonicity: A monotonic instrument is an adding instrument, where the progression of sums is non-decreasing.  Monotonic instruments are useful for monitoring rate information.

The metric instruments names are shown below along with whether they
are synchronous, adding, and/or monotonic.

| Name | Synchronous | Adding | Monotonic |
| ---- | ----------- | -------- | --------- |
| Counter           | Yes | Yes | Yes |
| UpDownCounter     | Yes | Yes | No  |
| ValueRecorder     | Yes | No  | No  |
| SumObserver       | No  | Yes | Yes |
| UpDownSumObserver | No  | Yes | No  |
| ValueObserver     | No  | No  | No  |

The synchronous instruments are useful for measurements that are
gathered in a distributed [Context](../context/context.md) (i.e., with associated Span, Baggage, etc.).  The asynchronous instruments are
useful when measurements are expensive, therefore should be gathered
periodically.  Read more [characteristics of synchronous and
asynchronous instruments](#synchronous-and-asynchronous-instruments-compared) below.

The synchronous and asynchronous adding instruments have a
significant difference: synchronous instruments are used to capture
changes in a sum, whereas asynchronous instruments are used to capture
sums directly.  Read more [characteristics of adding
instruments](#adding-and-grouping-instruments-compared) below.

The monotonic adding instruments are significant because they support rate
calculations.  Read more information about [choosing metric
instruments](#monotonic-and-non-monotonic-instruments-compared) below.

An _instrument definition_ describes several properties of the
instrument, including its name and its kind.  The other properties of
a metric instrument are optional, including a description and the unit
of measurement.  An instrument definition is associated with the
data that it produces.

### Labels

_Label_ is the term used to refer to a key-value attribute associated
with a metric event, similar to a [Span
attribute](../trace/api.md#span) in the tracing API.  Each label
categorizes the metric event, allowing events to be filtered and
grouped for analysis.

Each of the instrument calling conventions (detailed below) accepts a
set of labels as an argument.  The set of labels is defined as a
unique mapping from key to value.  Typically, labels are passed to the
API in the form of a list of key:values, in which case the
specification dictates that duplicate entries for a key are resolved
by taking the last value to appear in the list.

Measurements by a synchronous instrument are commonly combined with
other measurements having exactly the same label set, which enables
significant optimizations.  Read more about [combining measurements
through aggregation](#aggregations) below.

### Meter Interface

The API defines a `Meter` interface.  This interface consists of a set
of instrument constructors, and a facility for capturing batches of
measurements in a semantically atomic way.

There is a global `Meter` instance available for use that facilitates
automatic instrumentation for third-party code.  Use of this instance
allows code to statically initialize its metric instruments, without
explicit dependency injection.  The global `Meter` instance acts as a
no-op implementation until the application initializes a global
`Meter` by installing an SDK either explicitly, through a service
provider interface, or other language-specific support.  Note that it
is not necessary to use the global instance: multiple instances of the
OpenTelemetry SDK may run simultaneously.

As an obligatory step, the API requires the caller to provide the name of the
instrumenting library (optionally, the version) when obtaining a `Meter`
implementation.  The library name is meant to be used for identifying
instrumentation produced from that library, for such purposes as disabling
instrumentation, configuring aggregation, and applying sampling policies.  See
the specification on [TracerProvider](../trace/api.md#tracerprovider) for more
details.

### Aggregations

_Aggregation_ refers to the process of combining multiple measurements
into exact or estimated statistics about the measurements that took
place during an interval of time, during program execution.

Each instrument specifies a default aggregation that is suited to the
semantics of the instrument, that serves to explain its properties and
give users an understanding of how it is meant to be used.
Instruments, in the absence of any configuration override, can be
expected to deliver a useful, economical aggregation out of the box.

The adding instruments (`Counter`, `UpDownCounter`, `SumObserver`,
`UpDownSumObserver`) use a Sum aggregation by default.  Details about
computing a Sum aggregation vary, but from the user's perspective this
means they will be able to monitor the sum of values captured.  The
distinction between synchronous and asynchronous instruments is
crucial to specifying how exporters work, a topic that is covered in
the [SDK specification (WIP)](https://github.com/open-telemetry/opentelemetry-specification/pull/347).

The `ValueRecorder` instrument uses [TBD issue
636](https://github.com/open-telemetry/opentelemetry-specification/issues/636)
aggregation by default.

The `ValueObserver` instrument uses LastValue aggregation by default.
This aggregation keeps track of the last value that was observed and
its timestamp.

Other standard aggregations are available, especially for grouping
instruments, where we are generally interested in a variety of
different summaries, such as histograms, quantile summaries,
cardinality estimates, and other kinds of sketch data structure.

The default OpenTelemetry SDK implements a [Views API (WIP)](https://github.com/open-telemetry/oteps/pull/89), which
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
[Context](../context/context.md) (containing Span, Baggage, etc.)
that was active at the time.

## Meter provider

A concrete `MeterProvider` implementation can be obtained by initializing and
configuring an OpenTelemetry Metrics SDK.  This document does not
specify how to construct an SDK, only that they must implement the
`MeterProvider`.  Once configured, the application or library chooses
whether it will use a global instance of the `MeterProvider`
interface, or whether it will use dependency injection for greater
control over configuring the provider.

### Obtaining a Meter

New `Meter` instances can be created via a `MeterProvider` and its
`GetMeter(name, version)` method.  `MeterProvider`s are generally expected to
be used as singletons.  Implementations SHOULD provide a single global
default `MeterProvider`. The `GetMeter` method expects two string
arguments:

- `name` (required): This name must identify the instrumentation library (e.g. `io.opentelemetry.contrib.mongodb`)
  and *not* the instrumented library.
  In case an invalid name (null or empty string) is specified, a working default `Meter` implementation is returned as a fallback
  rather than returning null or throwing an exception.
  A `MeterProvider` could also return a no-op `Meter` here if application owners configure the SDK to suppress telemetry produced by this library.
- `version` (optional): Specifies the version of the instrumentation library (e.g. `1.0.0`).

Each distinctly named `Meter` establishes a separate namespace for its
metric instruments, making it possible for multiple instrumentation
libraries to report the metrics with the same instrument name used by
other libraries.  The name of the `Meter` is explicitly not intended
to be used as part of the instrument name, as that would prevent
instrumentation libraries from capturing metrics by the same name.

### Global Meter provider

Use of a global instance may be seen as an anti-pattern in many
situations, but in most cases it is the correct pattern for telemetry
data, in order to combine telemetry data from inter-dependent
libraries _without use of dependency injection_.  OpenTelemetry
language APIs SHOULD offer a global instance for this reason.
Languages that offer a global instance MUST ensure that `Meter`
instances allocated through the global `MeterProvider` and instruments
allocated through those `Meter` instances have their initialization
deferred until the a global SDK is first initialized.

#### Get the global MeterProvider

Since the global `MeterProvider` is a singleton and supports a single
method, callers can obtain a global `Meter` using a global `GetMeter`
call.  For example, `global.GetMeter(name, version)` calls `GetMeter`
on the global `MeterProvider` and returns a named `Meter` instance.

#### Set the global MeterProvider

A global function installs a MeterProvider as the global SDK.  For
example, use `global.SetMeterProvider(MeterProvider)` to install the
SDK after it is initialized.

## Instrument properties

Because the API is separated from the SDK, the implementation
ultimately determines how metric events are handled.  Therefore, the
choice of instrument should be guided by semantics and the intended
interpretation.  The semantics of the individual instruments is
defined by several properties, detailed here, to assist with
instrument selection.

### Instrument naming requirements

Metric instruments are primarily defined by their name, which is how
we refer to them in external systems.  Metric instrument names conform
to the following syntax:

1. They are non-empty strings
2. They are case-insensitive
3. The first character must be non-numeric, non-space, non-punctuation
4. Subsequent characters must belong to the alphanumeric characters, '\_', '.', and '-'.

Metric instrument names belong to a namespace, established by the the
associated `Meter` instance.  `Meter` implementations MUST return an
error when multiple instruments are registered by the same name.

TODO: [The following paragraph is a placeholder for a more-detailed
document that is needed.](https://github.com/open-telemetry/opentelemetry-specification/issues/600)

Metric instrument names SHOULD be semantically meaningful, independent
of the originating Meter name.  For example, when instrumenting an
http server library, "latency" is not an appropriate instrument name,
as it is too generic.  Instead, as an example, we should favor a name
like "http\_request\_latency", as it would inform the viewer of the
semantic meaning of the latency measurement.  Multiple instrumentation
libraries may be written to generate this metric.

### Synchronous and asynchronous instruments compared

Synchronous instruments are called inside a request, meaning they
have an associated distributed [Context](../context/context.md) (with Span, Baggage, etc.).  Multiple metric events may occur for a
synchronous instrument within a given collection interval.

Asynchronous instruments are reported by a callback, once per
collection interval, and lack Context.  They are permitted to
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

### Adding and grouping instruments compared

Adding instruments are used to capture information about a sum,
where, by definition, only the sum is of interest.  Individual events
are considered not meaningful for these instruments, the event count
is not computed.  This means, for example, that two `Counter` events
`Add(N)` and `Add(M)` are equivalent to one `Counter` event `Add(N +
M)`.  This is the case because `Counter` is synchronous, and
synchronous adding instruments are used to capture changes to a sum.

Asynchronous, adding instruments (e.g., `SumObserver`) are used to
capture sums directly.  This means, for example, that in any sequence
of `SumObserver` observations for a given instrument and label set,
the Last Value defines the sum of the instrument.

In both synchronous and asynchronous cases, the adding instruments
are inexpensively aggregated into a single number per collection interval
without loss of information.  This property makes adding instruments
higher performance, in general, than grouping instruments.

Grouping instruments use a relatively inexpensive aggregation,
by default, compared with recording full data, but still more expensive aggregation than the
default for adding instruments (Sum).  Unlike adding instruments,
where only the sum is of interest by definition, grouping
instruments can be configured with even more expensive aggregators.

### Monotonic and non-monotonic instruments compared

Monotonicity applies only to adding instruments.  `Counter` and
`SumObserver` instruments are defined as monotonic because the sum
captured by either instrument is non-decreasing.  The `UpDown-`
variations of these two instruments are non-monotonic, meaning the sum
can increase, decrease, or remain constant without any guarantees.

Monotonic instruments are commonly used to capture information about a
sum that is meant to be monitored as a rate.  The Monotonic property
is defined by this API to refer to a non-decreasing sum.
Non-increasing sums are not considered a feature in the Metric API.

### Function names

Each instrument supports a single function, named to help convey the
instrument's semantics.

Synchronous adding instruments support an `Add()` function,
signifying that they add to a sum and do not directly capture a sum.

Synchronous grouping instruments support a `Record()` function,
signifying that they capture individual events, not only a sum.

Asynchronous instruments all support an `Observe()` function,
signifying that they capture only one value per measurement interval.

## The instruments

### Counter

`Counter` is the most common synchronous instrument.  This instrument
supports an `Add(increment)` function for reporting a sum, and is
restricted to non-negative increments.  The default aggregation is
`Sum`, as for any adding instrument.

Example uses for `Counter`:

- count the number of bytes received
- count the number of requests completed
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
amount of resources used, or any quantity that rises and falls during a
request.

Example uses for `UpDownCounter`:

- count the number of active requests
- count memory in use by instrumenting `new` and `delete`
- count queue size by instrumenting `enqueue` and `dequeue`
- count semaphore `up` and `down` operations.

These example instruments would be useful for monitoring resource
levels across a group of processes.

### ValueRecorder

`ValueRecorder` is a grouping synchronous instrument useful for
recording any grouping number, positive or negative.  Values
captured by a `Record(value)` are treated as individual events
belonging to a distribution that is being summarized.  `ValueRecorder`
should be chosen either when capturing measurements that do not
contribute meaningfully to a sum, or when capturing numbers that are
adding in nature, but where the distribution of individual
increments is considered interesting.

One of the most common uses for `ValueRecorder` is to capture latency
measurements.  Latency measurements are not adding in the sense that
there is little need to know the latency-sum of all processed
requests.  We use a `ValueRecorder` instrument to capture latency
measurements typically because we are interested in knowing mean,
median, and other summary statistics about individual events.

The default aggregation for `ValueRecorder` computes the minimum and
maximum values, the sum of event values, and the count of events,
allowing the rate, the mean, and range of input values to be
monitored.

Example uses for `ValueRecorder` that are grouping:

- capture any kind of timing information
- capture the acceleration experienced by a pilot
- capture nozzle pressure of a fuel injector
- capture the velocity of a MIDI key-press.

Example _adding_ uses of `ValueRecorder` capture measurements that
are adding, but where we may have an interest in the distribution of
values and not only the sum:

- capture a request size
- capture an account balance
- capture a queue length
- capture a number of board feet of lumber.

These examples show that although they are adding in nature,
choosing `ValueRecorder` as opposed to `Counter` or `UpDownCounter`
implies an interest in more than the sum.  If you did not care to
collect information about the distribution, you would have chosen one
of the adding instruments instead.  Using `ValueRecorder` makes
sense for capturing distributions that are likely to be important in
an observability setting.

Use these with caution because they naturally cost more than the use
of adding measurements.

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
`ValueRecorder`, used to capture grouping measurements with
`Observe(value)`.  These instruments are especially useful for
capturing measurements that are expensive to compute, since it gives
the SDK control over how often they are evaluated.

Example uses for `ValueObserver`:

- capture CPU fan speed
- capture CPU temperature.

Note that these examples use grouping measurements.  In the
`ValueRecorder` case above, example uses were given for capturing
synchronous adding measurements during a request (e.g.,
current queue size seen by a request).  In the asynchronous case,
however, how should users decide whether to use `ValueObserver` as
opposed to `UpDownSumObserver`?

Consider how to report the size of a queue asynchronously.  Both
`ValueObserver` and `UpDownSumObserver` logically apply in this case.
Asynchronous instruments capture only one measurement per interval, so
in this example the `UpDownSumObserver` reports a current sum, while the
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

### Interpretation

How are the instruments fundamentally different, and why are there
only three?  Why not one instrument?  Why not ten?

As we have seen, the instruments are categorized as to whether
they are synchronous, adding, and/or and monotonic.  This approach
gives each of the instruments unique semantics, in ways that
meaningfully improve the performance and interpretation of metric
events.

Establishing different kinds of instrument is important because in
most cases it allows the SDK to provide good default functionality
"out of the box", without requiring alternative behaviors to be
configured.  The choice of instrument determines not only the meaning
of the events but also the name of the function called by the user.
The function names--`Add()` for adding instruments, `Record()` for
grouping instruments, and `Observe()` for asynchronous
instruments--help convey the meaning of these actions.

The properties and standard implementation described for the
individual instruments is summarized in the table below.

| **Name** | Instrument kind | Function(argument) | Default aggregation | Notes |
| ----------------------- | ----- | --------- | ------------- | --- |
| **Counter**             | Synchronous adding monotonic | Add(increment) | Sum | Per-request, part of a monotonic sum |
| **UpDownCounter**       | Synchronous adding | Add(increment) | Sum | Per-request, part of a non-monotonic sum |
| **ValueRecorder**       | Synchronous  | Record(value) | [TBD issue 636](https://github.com/open-telemetry/opentelemetry-specification/issues/636)  | Per-request, any grouping measurement |
| **SumObserver**         | Asynchronous adding monotonic | Observe(sum) | Sum | Per-interval, reporting a monotonic sum |
| **UpDownSumObserver**   | Asynchronous adding | Observe(sum) | Sum | Per-interval, reporting a non-monotonic sum |
| **ValueObserver**       | Asynchronous | Observe(value) | LastValue  | Per-interval, any grouping measurement |

### Constructors

The `Meter` interface supports functions to create new, registered
metric instruments.  Instrument constructors are named by adding a
`New-` prefix to the kind of instrument it constructs, with a
builder pattern, or some other idiomatic approach in the language.

There is at least one constructor representing each kind of instrument in
this specification (see [above](#metric-instruments)), and possibly
more as dictated by the language.  For example, if specializations are
provided for integer and floating pointer numbers, the OpenTelemetry
API would support 2 constructors per instrument kind.

Binding instruments to a single `Meter` instance has two benefits:

1. Instruments can be exported from the zero state, prior to first use, without an explicit registration call
2. The library-name and version are implicitly associated with the metric event.

Some existing metric systems support allocating metric instruments
statically and providing the equivalent of a `Meter` interface at the
time of use.  In one example, typical of statsd clients, existing code
may not be structured with a convenient place to store new metric
instruments.  Where this becomes a burden, it is recommended to use
the global `MeterProvider` to construct a static `Meter`, and to
construct and use globally-scoped metric instruments.

The situation is similar for users of existing Prometheus clients, where
instruments can be allocated to the global `Registerer`.  
Such code may not have access to an appropriate `MeterProvider` or `Meter`
instance at the location where instruments are defined.
Where this becomes a burden, it is
recommended to use the global meter provider to construct a static
named `Meter`, to construct metric instruments.

Applications are expected to construct long-lived instruments.
Instruments are considered permanent for the lifetime of a SDK, there
is no method to delete them.

## Sets of labels

Semantically, a set of labels is a unique mapping from string key to
value.  Across the API, a set of labels MUST be passed in the same,
idiomatic form.  Common representations include an ordered list of
key:values, or a map of key:values.

When labels are passed as an ordered list of key:values, and there are
duplicate keys found, the last value in the list for any given key is
taken in order to form a unique mapping.

The type of the label value is generally presumed to be a string by
exporters, although as a language-level decision, the label value type
could be any idiomatic type in that language that has a string
representation.

Users are not required to pre-declare the set of label keys that will
be used with metric instruments in the API.  Users can freely use any
set of labels for any metric event when calling the API.

### Label performance

Label handling can be a significant cost in the production of metric
data overall.

SDK support for in-process aggregation depends on the ability to find
an active record for an instrument, label set combination pair.  This
allows measurements to be combined.  Label handling costs can be
lowered through the use of bound synchronous instruments and
batch-reporting functions (`RecordBatch`, `BatchObserver`).

### Option: Ordered labels

As a language-level decision, APIs MAY support label key ordering.  In this
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

## Synchronous instrument details

The following details are specified for synchronous instruments.

### Synchronous calling conventions

The metrics API provides three semantically equivalent ways to capture
measurements using synchronous instruments:

- calling bound instruments, which have a pre-associated set of labels
- directly calling instruments, passing the associated set of labels
- batch recording measurements for multiple instruments using a single set of labels.

All three methods generate equivalent metric events, but offer varying degrees
of performance and convenience.

The performance of the metric API depends on the work done to enter a
new measurement, which is typically dominated by the cost of handling
labels.  Bound instruments are the highest-performance calling
convention, because they can amortize the cost of handling labels
across many uses.  Recording multiple measurements via
`RecordBatch()`, another calling convention, is a good option for
improving performance, since the cost of handling labels is spread
across multiple measurements.  The direct calling convention is the
most convenient, but least performant calling convention for entering
measurements through the API.

#### Bound instrument calling convention

In situations where performance is a requirement and a metric
instrument is repeatedly used with the same set of labels, the
developer may elect to use the _bound instrument_ calling convention
as an optimization.  For bound instruments to be a benefit, it
requires that a specific instrument will be re-used with specific
labels.  If an instrument will be used with the same labels more than
once, obtaining a bound instrument corresponding to the labels ensures
the highest performance available.

To bind an instrument, use the `Bind(labels...)` method to return an
interface that supports the corresponding synchronous API (i.e.,
`Add()` or `Record()`).  Bound instruments are invoked without labels;
the corresponding metric event is associated with the labels that were
bound to the instrument.

As a consequence of their performance advantage, bound instruments
also consume resources in the SDK.  Bound instruments MUST support an
`Unbind()` method for users to indicate they are finished with the
binding and release the associated resources.  Note that `Unbind()`
does not imply deletion of a timeseries, it only permits the SDK to
forget the timeseries existed after there are no pending updates.

For example, to repeatedly update a counter with the same labels:

```golang
func (s *server) processStream(ctx context.Context) {

  // The result of Bind() is a bound instrument
  // (e.g., a BoundInt64Counter).
  counter2 := s.instruments.counter2.Bind(
      kv.String("labelA", "..."),
      kv.String("labelB", "..."),
  )
  defer counter2.Unbind()

  for _, item := <-s.channel {
     // ... other work

     // High-performance metric calling convention: use of bound
     // instruments.
     counter2.Add(ctx, item.size())
  }
}
```

#### Direct instrument calling convention

When convenience is more important than performance, or when values
are not known ahead of time, users may elect to operate directly on
metric instruments, meaning to supply labels at the call site.  This
method offers the greatest convenience possible.

For example, to update a single counter:

```golang
func (s *server) method(ctx context.Context) {
    // ... other work

    s.instruments.counter1.Add(ctx, 1,
        kv.String("labelA", "..."),
        kv.String("labelB", "..."),
        )
}
```

Direct calls are convenient because they do not require allocating and
storing a bound instrument.  They are appropriate for use in cases
where an instrument will be used rarely, or rarely used with the same
set of labels.  Unlike bound instruments, there is not a long-term
consumption of SDK resources when using the direct calling convention.

#### RecordBatch calling convention

There is one final API for entering measurements, which is like the
direct access calling convention but supports multiple simultaneous
measurements.  The use of the `RecordBatch` API supports entering
multiple measurements, implying a semantically atomic update to
several instruments.  Calls to `RecordBatch` amortize the cost of
label handling across multiple measurements.

For example:

```golang
func (s *server) method(ctx context.Context) {
    // ... other work

    s.meter.RecordBatch(ctx, labels,
        s.instruments.counter.Measurement(1),
        s.instruments.updowncounter.Measurement(10),
        s.instruments.valuerecorder.Measurement(123.45),
    )
}
```

Another valid interface for recording batches uses a builder pattern:

```java
    meter.RecordBatch(labels).
        put(s.instruments.counter, 1).
        put(s.instruments.updowncounter, 10).
        put(s.instruments.valuerecorder, 123.45).
        record();
```

Using the _record batch_ calling convention is semantically identical to
a sequence of direct calls, with the addition of atomicity.  Because
values are entered in a single call, the SDK is potentially able to
implement an atomic update, from the exporter's point of view, because
the SDK can enqueue a single bulk update, or take a lock only once,
for example.  Like the direct calling convention, there is not a
long-term consumption of SDK resources when using the batch calling
convention.

### Association with distributed context

Synchronous measurements are implicitly associated with the
distributed [Context](../context/context.md) at runtime, which may
include a Span and Baggage entries. The Metric SDK may use
this information in many ways, but one feature is of particular
interest in OpenTelemetry.

#### Baggage into metric labels

Baggage is supported in OpenTelemetry as a means for
labels to propagate from one process to another in a distributed
computation.  Sometimes it is useful to aggregate metric data using
distributed baggage entries as metric labels.

The use of Baggage must be explicitly configured, using
the [Views API (WIP)](https://github.com/open-telemetry/oteps/pull/89)
to select specific key baggage entries that should be applied as
labels.  The default SDK will not automatically use Baggage
labels in the export pipeline, since using Baggage labels
can be a significant expense.

Configuring views for applying Baggage labels is a [work in
progress](https://github.com/open-telemetry/oteps/pull/89).

## Asynchronous instrument details

The following details are specified for asynchronous instruments.

### Asynchronous calling conventions

The metrics API provides two semantically equivalent ways to capture
measurements using asynchronous instruments, either through
single-instrument callbacks or through multi-instrument batch
callbacks.

Whether single or batch, asynchronous instruments must be observed
through only one callback.  The constructors return no-op instruments
for `null` observer callbacks.  It is considered an error when more
than one callback is specified for any asynchronous instrument.

Instruments may not observe more than one value per distinct label set
per instrument.  When more than one value is observed for a single
instrument and label set, the last observed value is taken and earlier
values are discarded without error.

#### Single-instrument observer

A single instrument callback is bound to one instrument.  Its
callback receives an `ObserverResult` with an `Observe(value,
labels...)` function.

```golang
func (s *server) registerObservers(.Context) {
     s.observer1 = s.meter.NewInt64SumObserver(
         "service_load_factor",
          metric.WithCallback(func(result metric.Float64ObserverResult) {
             for _, listener := range s.listeners {
                 result.Observe(
                     s.loadFactor(),
                     kv.String("name", server.name),
                     kv.String("port", listener.port),
                 )
             }
          }),
          metric.WithDescription("The load factor use for load balancing purposes"),
    )
}

```

#### Batch observer

A `BatchObserver` callback supports observing multiple instruments in
one callback.  Its callback receives an `BatchObserverResult` with an
`Observe(labels, observations...)` function.

An observation is returned by calling `Observation(value)`, on an
asynchronous instrument.

```golang
func (s *server) registerObservers(.Context) {
     batch := s.meter.NewBatchObserver(func (result BatchObserverResult) {
          result.Observe(
             []kv.KeyValue{
                 kv.String("name", server.name),
                 kv.String("port", listener.port),
             },
             s.observer1.Observation(value1),
             s.observer2.Observation(value2),
             s.observer3.Observation(value3),
          },
    )

     s.observer1 = batch.NewSumObserver(...)
     s.observer2 = batch.NewUpDownSumObserver(...)
     s.observer3 = batch.NewValueObserver(...)
}
```

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

## Concurrency

For languages which support concurrent execution the Metrics APIs provide
specific guarantees and safeties. Not all of API functions are safe to
be called concurrently.

**MeterProvider** - all methods are safe to be called concurrently.

**Meter** - all methods are safe to be called concurrently.

**Instrument** - All methods of any Instrument are safe to be called concurrently.

**Bound Instrument** - All methods of any Bound Instrument are safe to be called concurrently.

## Related OpenTelemetry work

Several ongoing efforts are underway as this specification is being
written.

### Metric Views

The API does not support configurable aggregations for metric
instruments.

A _View API_ is defined as an interface to an SDK mechanism that
supports configuring aggregations, including which operator is applied
(sum, p99, last-value, etc.) and which dimensions are used.

See the [current issue discussion on this topic](https://github.com/open-telemetry/opentelemetry-specification/issues/466) and the [current OTEP draft](https://github.com/open-telemetry/oteps/pull/89).

### OTLP Metric protocol

The OTLP protocol is designed to export metric data in a memoryless
way, as documented above.  Several details of the protocol are being
worked out.  See the [current protocol](https://github.com/open-telemetry/opentelemetry-proto/blob/master/opentelemetry/proto/metrics/v1/metrics.proto).

### Metric SDK default implementation

The OpenTelemetry SDK includes default support for the metric API.  The specification for the default SDK is underway, see the [current draft](https://github.com/open-telemetry/opentelemetry-specification/pull/347).
