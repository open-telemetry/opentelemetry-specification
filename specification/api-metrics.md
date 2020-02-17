# Metrics API

<!-- toc -->

- [Overview](#overview)
  * [Metric Instruments](#metric-instruments)
  * [Label sets](#label-sets)
  * [Meter Interface](#meter-interface)
  * [Aggregations](#aggregations)
  * [Time](#time)
  * [WithRecommendedKeys declaration on metric instruments](#withrecommendedkeys-declaration-on-metric-instruments)
  * [Metric Event Format](#metric-event-format)
- [Three kinds of instrument](#three-kinds-of-instrument)
  * [Counter](#counter)
  * [Measure](#measure)
  * [Observer](#observer)
- [Interpretation](#interpretation)
  * [Standard implementation](#standard-implementation)
  * [Option: Dedicated Measure instrument for timing measurements](#option-dedicated-measure-instrument-for-timing-measurements)
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
the intent to produce continuous summaries of those measurements
simultaneously.  Hereafter, "the API" refers to the OpenTelemetry
Metrics API.

The API provides functions for capturing raw measurements, through
several [calling
conventions](api-metrics-user.md#metric-calling-conventions) that
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
separation of the API from the SDK](library-guidelines.md#requirements),
so that different SDKs can be configured at run time.

### Metric Instruments

A _metric instrument_, of which there are three kinds, is a device for
capturing raw measurements into the API.  There are Counter, Measure,
and Observer instruments, each with different semantics and intended
uses, that will be specified here.  All measurements captured by the
API are associated with an instrument, which gives the measurement its
properties.  Instruments are created and defined through calls to a
`Meter` API, which is the user-facing entry point to the SDK.

Each kind of metric instrument has its own semantics, briefly
described as:

- Counter: metric events of this kind _Add_ to a value that is summed over time.
- Measure: metric events of this kind _Record_ a value that is aggregated over time.
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
attributes](api-tracing.md#span) in the tracing API, a label set is
given its own type in the Metrics API (generally: `LabelSet`).  Label
sets are a feature of the API meant to facilitate re-use and thereby
to lower the cost of processing metric events.  Users are encouraged
to re-use label sets whenever possible, as they may contain a
previously encoded representation of the labels.

Users obtain label sets by calling a `Meter` API function.  Each of
the instrument calling conventions detailed in the [user-level API
specification](api-metrics-user.md) accepts a label set.

### Meter Interface

To produce measurements using an instrument, you need an SDK that
implements the `Meter` API.  This interface consists of a set of
instrument constructors, functionality related to label sets, and a
facility for capturing batches of measurements in a semantically atomic
way.

There is a global `Meter` instance available for use that facilitates
automatic instrumentation for third-party code.  Use of this instance
allows code to statically initialize its metric instruments, without
explicit dependency injection.  The global `Meter` instance acts as a
no-op implementation until the application explicitly initializes a
global `Meter` by installing an SDK.

As an obligatory step, the API requires the caller to provide the name
of the instrumenting library (optionally, the version) when obtaining
a `Meter` implementation, that is meant to be used for identifying
instrumentation produced from that library for such purposes as
disabling instrumentation, configuring aggregation, and applying
sampling policies.  (TODO: refer to the semantic convention on the
reporting library name).

Details about installing an SDK and obtaining a named `Meter` are
covered in the [SDK-level API specification](api-metrics-meter.md).

### Aggregations

_Aggregation_ refers to the process of combining a large number of
measurements into exact or estimated statistics about the metric
events that took place during a window of real time, during program
execution.  Computing aggregations is mainly a subject of the SDK
specification, with the goal of reducing the amount of data that must
be sent to the telemetry collection backend.

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
one.  Users do not provide explicit timestamps for metric events.
SDKs are discouraged from capturing the current timestamp for each
event (by reading from a clock) unless there is a definite need for
high-precision timestamps.

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

Counter and Measure instruments offer synchronous APIs for capturing
measurements.  Metric events from Counter and Measure instruments are
captured at the moment they happen, when the SDK receives the
corresponding function call.

The Observer instrument supports an asynchronous API, allowing the SDK
to collect metric data on demand, once per collection interval.  A
single Observer instrument callback can capture multiple metric events
associated with different label sets.  Semantically, by definition,
these observations are captured at a single instant in time, the
instant that they became the current set of last-measured values.

Because metric events are implicitly timestamped, we could refer to a
series of metric events as a _time series_. However, we reserve the
use of this term for the SDK specification, to refer to parts of a
data format that express explicitly timestamped values, in a sequence,
resulting from an aggregation of raw measurements over time.

### WithRecommendedKeys declaration on metric instruments

A standard feature of metric SDKs is to pre-aggregate metric events
according to a specified set of label keys (i.e., dimensions).  To
perform this task, the SDK must aggregate metric events over the
collection interval: (1) across time, (2) across key dimensions in
_label space_.

When aggregating across spatial dimensions, metric events for
different label sets are combined into an aggregated value for each
distinct "group" of values for the key dimensions.  It means that
measurements are combined for all metric events having the same values
for selected keys, explicitly disregarding any additional labels with
keys not in the set of aggregation keys.  Some exporters are known to
require pre-specifying the label keys used for aggregation (e.g.,
Prometheus).

For example, if `[ak1, ak2]` are the aggregation keys and `[ik1,
ik2]` are the ignored keys, then a metric event having labels
`{ak1=A, ak2=B, ik1=C, ik1=D}` will be combined with a metric
event having labels `{ak1=A, ak2=B, ik1=Y, ik1=Z}` because they
have identical label values for all of the aggregation keys.

The API provides a `WithRecommendedKeys` option for the user to declare the
recommended aggregation keys when declaring new metric instruments,
intended as the default way to configure an exporter for
pre-aggregation, if it is expected.  Since this is only expected in
some exporters, it is regarded as an option relevant to the exporter,
whether keys configured through `WithRecommendedKeys` are applied for aggregation
purposes or not.  This allows the user to influence the standard
implementation behavior, especially for exporters that require
pre-specified aggregation keys.

### Metric Event Format

Metric events have the same logical representation, regardless of
kind.  Whether a Counter, a Measure, or an Observer instrument, metric
events produced through an instrument consist of:

- [Context](context.md) (Span context, Correlation context)
- timestamp (implicit to the SDK)
- instrument definition (name, kind, and semantic options)
- label set (associated key-values)
- value (a signed integer or floating point number)

This format is the result of separating the API from the SDK--a common
representation for metric events, where the only semantic distinction
is the kind of instrument that was specified by the user.

## Three kinds of instrument

Because the API is separated from the SDK, the implementation
ultimately determines how metric events are handled.  Therefore, the
choice of instrument should be guided by semantics and the intended
interpretation.  Here we detail the three instruments and their
individual semantics.

### Counter

Counter instruments are used to capture changes in running sums,
synchronously.  These are commonly used to monitor rates, and they are
sometimes used to capture totals that rise and fall.  An essential
property of Counter instruments is that two events `Add(m)` and
`Add(n)` are semantically equivalent to one event `Add(m+n)`.  This
property means that Counter events can be combined inexpensively, by
definition.

Note that `Add(0)` events are not considered a special case, despite
contributing nothing to a sum.  `Add(0)` events MUST be observed by
the SDK in case non-default aggregations are configured for the
instrument.

Counter instruments can be seen as special cases of Measure
instruments with the additive property described above and a
more-specific verb to improve readability (i.e., "Add" instead of
"Record").  Counter instruments are special cases of Measure
instruments in that they only preserve a Sum, by default, and no other
summary statistics.

Labels associated with Counter instrument events can be used to
compute rates and totals from the instrument, over selected
dimensions.

### Measure

Semantically, metric events from Measure instruments are independent,
meaning they cannot be combined naturally, as with Counters.  Measure
instruments are used to capture many kinds of information,
synchronously, and are recommended for all cases that reflect an event
in the application where the additive property of Counter instruments
does not apply.

Labels associated with Measure instrument events can be used to
compute information about the distribution of values from the
instrument, over selected dimensions.  When aggregating Measure
events, the output statistics are expected to reflect the combined
data set.

### Observer

Observer instruments are used to capture a _current set of values_ at
a point in time.  Observer instruments are asynchronous, with the use
of callbacks allowing the user to capture multiple values per
collection interval.  Observer instruments are not associated with a
Context, by definition.  This means, for example, it is not possible
to associate Observer instrument events with Correlation or Span
context.

Observer instruments capture not only current values, but also
effectively _which label sets are current_ at the moment of
collection.  These instruments can be used to compute probabilities
and ratios, because values are part of a set.

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

1. Counter.  The `Add()` function accumulates a total for each distinct label set.  When aggregating over distinct label sets for a Counter, combine using arithmetic addition and export as a sum. Depending on the exposition format, sums are exported either as pairs of label set and cumulative _delta_ or as pairs of label set and cumulative _total_.

2. Measure.  Use the `Record()` function to report events for which the SDK will compute summary statistics about the distribution of values, for each distinct label set.  The summary statistics to use are determined by the aggregation, but they usually include at least the sum of values, the count of measurements, and the minimum and maximum values.  When aggregating distinct Measure events, report summary statistics of the combined value distribution.  Exposition formats for summary statistics vary widely, but typically include pairs of label set and (sum, count, minimum and maximum value).

3. Observer.  Current values are provided by the Observer callback at the end of each Metric collection period.  When aggregating values _for the same label set_, combine using the most-recent value.  When aggregating values _for different label sets_, combine the value distribution as for Measure instruments.  Export as pairs of label set and (sum, count, minimum and maximum value).

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

This is a typical application for the Counter instrument.  Use one
Counter for capturing the number bytes read.  When handling a request,
compute a LabelSet containing the name of the protocol and potentially
other useful labels, then call `Add()` with the same label set and the
number of bytes read.

To lower the cost of this reporting, you can `Bind()` the
instrument with each of the supported protocols ahead of time and
avoid computing the label set for each request.

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
- Why not report deltas in the Observer callback?  Observer instruments are meant to be used to observe current values. Nothing prevents reporting deltas with an Observer, but the standard aggregation for Observer instruments is to sum the current value across distinct label sets.  The standard behavior is useful for determining the current rate of CPU usage, but special configuration would be required for an Observer instrument to use Counter aggregation.

### Reporting per-shard memory holdings

Suppose you have a widely-used library that acts as a client to a
sharded service.  For each shard it maintains some client-side state,
holding a variable amount of memory per shard.

Observe the current allocation per shard using an Observer instrument
with a shard label.  These can be aggregated across hosts to compute
cluster-wide memory holdings by shard, for example, using the standard
aggregation for Observers, which sums the current value across
distinct label sets.

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