# Metric Instruments

Removes the optional semantic declarations `Monotonic` and `Absolute`
for metric instruments, declares the Measure and Observer instruments
as _foundational_, and introduces a process for standardizing new
instrument _refinements_.

Note that [OTEP 93](https://github.com/open-telemetry/oteps/pull/93)
contains a final proposal for the set of instruments, of which there
are seven.  Note that [OTEP
96](https://github.com/open-telemetry/oteps/pull/96) contains a final
proposal for the names of the seven standard instruments.  These three
OTEPs will be applied as a group to the specification, using the names
finalized in OTEP 96.

## Motivation

With the removal of Gauge instruments and the addition of Observer
instruments in the specification, the existing `Monotonic` and
`Absolute` options began to create confusion.  For example, a Counter
instrument is used for capturing changes in a Sum, and we could say
that non-negative-valued metric events define a monotonic Counter, in
the sense that its Sum is monotonic.  The confusion arises, in this
case, because `Absolute` refers to the captured values, whereas
`Monotonic` refers to the semantic output.

From a different perspective, Counter instruments might be treated as
refinements of the Measure instrument.  Whereas the Measure instrument
is used for capturing all-purpose synchronous measurements, the
Counter instrument is used specifically for synchronously capturing
measurements of changes in a sum, therefore it uses `Add()` instead of
`Record()`, and it specifies `Sum` as the standard aggregation.

What this illustrates is that we have modeled this space poorly.  This
proposal does not propose to change any existing metrics APIs, only
our understanding of the three instruments currently included in the
specification: Measure, Observer, and Counter.

## Explanation

The Measure and Observer instrument are defined as _foundational_
here, in the sense that any kind of metric instrument must reduce to
one of these.  The foundational instruments are unrestricted, in the
sense that metric events support any numerical value, positive or
negative, zero or infinity.

The distinction between the two foundational instruments is whether
they are synchronous.  Measure instruments are called synchronously by
the user, while Observer instruments are called asynchronously by the
implementation.  Synchronous instruments (Measure and its refinements)
have three calling patterns (_Bound_, _Unbound_, and _Batch_) to
capture measurements.  Asynchronous instruments (Observer and its
refinements) use callbacks to capture measurements.

All measurement APIs produce metric events consisting of timestamp,
instrument descriptor, label set, and numerical
value.  Synchronous instrument
events additionally have [Context](../../specification/context/README.md), describing
properties of the associated trace and distributed correlation values.

### Terminology: Kinds of Aggregation

_Aggregation_ refers to the technique used to summarize many
measurements and/or observations into _some_ kind of summary of the
data.  As detailed in the [metric SDK specification (TODO:
WIP)](https://github.com/open-telemetry/opentelemetry-specification/pull/347/files?short_path=5b01bbf#diff-5b01bbf3430dde7fc5789b5919d03001),
there are generally two relevant modes of aggregation:

1. Within one collection interval, for one label set, the SDK's
`Aggregator.Add()` interface method incorporates one new measurement
value into the current aggregation value.  This happens at runtime,
therefore is referred to as _temporal aggregation_.  This mode applies
only to Measure instruments.
2. Within one collection interval, when combining label sets, the
SDK's `Aggregator.Merge()` interface method incorporates two
aggregation values into one aggregation value.  This is referred to as
_spatial aggregation_.  This mode applies to both Measure and Observer
instruments.

As discussed below, we are especially interested in aggregating rate
information, which sometimes requires that temporal and spatial
aggregation be treated differently.

### Last-value relationship

Observer instruments have a well-defined _Last Value_ measured by the
instrument, that can be useful in defining aggregations.  The Last
Value of an Observer instrument is the value that was captured during
the last-completed collection interval, and it is a useful
relationship because it is defined without relation to collection
interval timing.  The Last Value of an Observer is determined by the
single most-recently completed collection interval--it is not
necessary to consider prior collection intervals.  The Last Value of
an Observer is undefined when it is not observed during a collection
interval.

To maintain this property, we impose a requirement: two or more
`Observe()` calls with an identical LabelSet during a single Observer
callback invocation are treated as duplicates of each other, where the
last call to `Observe()` wins.

Based on the Last Value relationship, we can ask and answer questions
such as "what is the average last value of a metric at a point in
time?".  Observer instruments define the Last Value relationship
without referring to the collection interval and without ambiguity.

### Last-value and Measure instruments

Measure instruments do not define a Last Value relationship.  One
reason is that synchronous events can happen
simultaneously.

For Measure instruments, it is possible to compute an aggregation that
computes the last-captured value in a collection interval, but it is
potentially not unique and the result will vary depending on the
timing of the collection interval.  For example, a synchronous metric
event that last took place one minute ago will appear as the last
value for collection intervals one minute or longer, but the last
value will be undefined if the collection interval is shorter than one
minute.

### Aggregating changes to a sum: Rate calculation

The former `Monotonic` option had been introduced in order to support
reporting of a current sum, such that a rate calculation is implied.
Here we defined _Rate_ as an aggregation, defined for a subset of
instruments, that may be calculated differently depending on how the
instrument is defined.  The rate aggregation outputs the amount of
change in a quantity divided by the amount of change in time.

A rate can be computed from values that are reported as differences,
referred to as _delta_ reporting here, or as sums, referred to as
_cumulative_ reporting here.  The primary goal of the instrument
refinements introduced in this proposal is to facilitate rate
calculations in more than one way.

When delta reporting, a rate is calculated by summing individual
measurements or observations.  When cumulative reporting, a rate is
calculated by computing a difference between individual values.

Note that cumulative-reported metric data requires special treatment
of the time dimension when computing rates.  When aggregating across
the time dimension, the difference should be computed.  When
aggregating across spatial dimensions, the sum should be computed.

### Standard implementation of Measure and Observer

OpenTelemetry specifies how the default SDK should treat metric
events, by default, when asked to export data from an instrument.
Measure and Observer instruments compute `Sum` and `Count`
aggregations, by default, in the standard implementation.  This pair
of measurements, of course, defines an average value.  There are no
restrictions placed on the numerical value in an event for the two
foundational instruments.

### Refinements to Measure and Observer

The `Monotonic` and `Absolute` options were removed in the 0.3
specification.  Here, we propose to regain the equivalent effects
through instrument refinements.  Instrument refinements are added to
the foundational instruments, yielding new instruments with the same
calling patterns as the foundational instrument they refine.  These
refinements support adding either a different standard implementation
or a restriction of the input domain to the instrument.

We have done away with instrument options, in other words, in favor of
optional metric instruments.  Here we discuss four significant
instrument refinements.

#### Non-negative

For some instruments, such as those that measure real quantities,
negative values are meaningless.  For example, it is impossible for a
person to weigh a negative amount.

A non-negative instrument refinement accepts only non-negative values.
For instruments with this property, negative values are considered
measurement errors.  Both Measure and Observer instruments support
non-negative refinements.

#### Sum-only

A sum-only instrument is one where only the sum is considered to be of
interest.  For a sum-only instrument refinement, we have a semantic
property that two events with numeric values `M` and `N` are
semantically equivalent to a single event with value `M+N`.  For
example, in a sum-only count of users arriving by bus to an event, we
are not concerned with the number of buses that arrived.

A sum-only instrument is one where the number of events is not
counted, only the `Sum`.  A key property of sum-only instruments is
that they always support a Rate aggregation, whether reporting delta-
or cumulative-values.  Both Measure and Observer instruments support
sum-only refinements.

#### Precomputed-sum

A precomputed-sum refinement indicates that values reported through an
instrument are observed or measured in terms of a sum that changes
over time.  Pre-computed sum instruments support cumulative reporting,
meaning the rate aggregation is defined by computing a difference
across timestamps or collection intervals.

A precomputed sum refinement implies a sum-only refinement.  Note that
values associated with a precomputed sum are still sums.  Precomputed
sum values are combined using addition, when aggregating over the
spatial dimensions; only the time dimension receives special treatment.

#### Non-negative-rate

A non-negative-rate instrument refinement states that rate aggregation
produces only non-negative results.  There are non-negative-rate cases
of interest for delta reporting and cumulative reporting, as follows.

For delta reporting, any non-negative and sum-only instrument is also
a non-negative-rate instrument.

For cumulative reporting, a sum-only and pre-computed sum instrument
does not necessarily have a non-negative rate, but adding an explicit
non-negative-rate refinement makes it the equivalent of `Monotonic` in
the 0.2 specification.

For example, the CPU time used by a process, as read in successive
collection intervals, cannot change by a negative amount, because it
is impossible to use a negative amount of CPU time.  CPU time a
typical value to report through an Observer instrument, so the rate
for a specific set of labels is defined by subtracting the prior
observation from the current observation.  Using a non-negative-rate
refinement asserts that the values increases by a non-negative amount
on subsequent collection intervals.

#### Discussion: Additive vs. Non-Additive numbers

The refinements proposed above may leave us wondering about the
distinction between an unrefined Measure and the
_UpDownCumulativeCounter_.  Both values are unrestricted, in terms of
range, so why should they be treated differently?

The _UpDownCumulativeCounter_ has sum-only and precomputed-sum
refinements, which indicate that the numbers being observed are the
result of addition.  These instruments have the additive property that
observing `N` and `M` separately is equivalent to observing `N+M`.
When performing spatial aggregation over data with these additive
properties, it is natural to compute the sum.

When performing spatial aggregation over data without additive
properties, it is natural to combine the distributions.  The
distinction is about how we interpret the values when aggregating.
Use one of the sum-only refinements to report a sum in the default
configuration, otherwise use one of the non-sum-only instruments to
report a distribution.

#### Language-level refinements

OpenTelemetry implementations may wish to add instrument refinements
to accommodate built-in types.  Languages with distinct integer and
floating point should offer instrument refinements for each, leading
to type names like `Int64Measure` and `Float64Measure`.

A language with support for unsigned integer types may wish to create
dedicated instruments to report these values, leading to type names
like `UnsignedInt64Observer` and `UnsignedFloat64Observer`.  These
would naturally apply a non-negative refinement.

Other uses for built-in type refinements involve the type for duration
measurements.  For example, where there is built-in type for the
difference between two clock measurements, OpenTelemetry APIs should
offer a refinement to automatically apply the correct unit of time to
the measurement.

### Counter refinement

Counter is a sum-only, non-negative, thus non-negative-rate refinement
of the Measure instrument.

### Standardizing new instruments

With these refinements we can exhaustively list each distinct kind of
instrument.  There are a total of twelve hypothetical instruments
listed in the table below, of which only one has been standardized.
Hypothetical future instrument names are _italicized_.

| Foundation instrument | Sum-only? | Precomputed-sum? | Non-negative? | Non-negative-rate? | Instrument name _(hypothetical)_ |
| --- | ---- | ---- | ---- | --- | --- |
| Measure | sum-only | | non-negative | non-negative-rate | Counter |
| Measure | sum-only | precomputed-sum | | non-negative-rate | _CumulativeCounter_ |
| Measure | sum-only | | | | _UpDownCounter_ |
| Measure | sum-only | precomputed-sum | | | _UpDownCumulativeCounter_ |
| Measure | | | non-negative | | _AbsoluteDistribution_ |
| Measure | | | | | _Distribution_ |
| Observer | sum-only | | non-negative | non-negative-rate | _DeltaObserver_ |
| Observer | sum-only | precomputed-sum | | non-negative-rate | _CumulativeObserver_ |
| Observer | sum-only | | | | _UpDownDeltaObserver_ |
| Observer | sum-only | precomputed-sum | | | _UpDownCumulativeObserver_ |
| Observer | | | non-negative | | _AbsoluteLastValueObserver_ |
| Observer | | | | | _LastValueObserver_ |

To arrive at this listing, several assumptions have been made.  For
example, the precomputed-sum and non-negative-rate refinements are
only applicable in conjunction with a sum-only refinement.

For the precomputed-sum instruments, we technically do not care
whether the inputs are non-negative, because rate aggregation computes
differences.  However, it is useful for other aggregations to assume
that precomputed sums start at zero, and we will ignore the case where
a precomputed sum has an initial value other than zero.

#### Gauge instrument

A Measure instrument with a default Last Value aggregation could be
defined, hypothetically named a _Gauge_ instrument.  This would offer
convenience for users that want this behavior, for there is otherwise
no standard Measure refinement with Last Value aggregation.

Sum-only uses for this hypothetical instrument should instead use
either _CumulativeCounter_ or _UpDownCumulativeCounter_, since they
are reporting a sum.  This (hypothetical) _Gauge_ instrument would be
useful when a value is time-dependent and the average value is not of
interest.

## Internal details

This is a change of understanding.  It does not request any new
instruments be created or APIs be changed, but it does specify how we
should think about adding new instruments.

No API changes are called for in this proposal.

### Translation into well-known systems

#### Prometheus

The Prometheus system defines four kinds of [synchronous metric
instrument](https://prometheus.io/docs/concepts/metric_types/).  

| System     | Metric Kind  | Operation           | Aggregation          | Notes                                |
| ---------- | ------------ | ------------------- | -------------------- | ------------------------------------ |
| Prometheus | Counter      | Inc()               | Sum                  | Sum of positive deltas               |
| Prometheus | Counter      | Add()               | Sum                  | Sum of positive deltas               |
| Prometheus | Gauge        | Set()               | Last Value           | Non-additive or monotonic cumulative |
| Prometheus | Gauge        | Inc()/Dec()         | Sum                  | Sum of deltas                        |
| Prometheus | Gauge        | Add()/Sub()         | Sum                  | Sum of deltas                        |
| Prometheus | Histogram    | Observe()           | Histogram            | Non-negative values                  |
| Prometheus | Summary      | Observe()           | Summary              | Aggregation does not merge           |

Note that the Prometheus Gauge supports five methods (`Set`, `Inc`,
`Dec`, `Add`, and `Sub`), one which sets the last value while the
others modify the last value.  This interface is not compatible with
OpenTelemetry, because it requires the SDK to maintain long-lived
state about Gauge values in order to compute the last value following
one of the additive methods (`Inc`, `Dec`, `Add`, and `Sub`).

If we restrict Prometheus Gauges to support only a `Set` method, or to
support only the additive methods, then we can model these two
instruments separately, in a way that is compatible with OpenTelemetry.
A Prometheus Gauge that is used exclusively with `Set()` can be
modeled as a Measure instrument with Last Value aggregation.  A
Prometheus Gauge that is used exclusively with the additive methods be
modeled as a `UpDownCounter`

Prometheus has support for asynchronous reporting via the "Collector"
interface, but this is a low-level API to support directly exporting
encoded metric data.  The Prometheus "Collector" interface could be
used to implement Observer-like instruments, but they are not natively
supported in Prometheus.

#### Statsd

The Statsd system supports only synchronous reporting.  

| System | Metric Event | Operation           | Aggregation          | Notes                                                 |
| ------ | ------------ | ------------------- | -------------------- | ----------------------------------------------------- |
| Statsd | Count        | Count()             | Sum                  | Sum of deltas                                         |
| Statsd | Gauge        | Gauge()             | Last Value           |                                                       |
| Statsd | Histogram    | Histogram()         | Histogram            |                                                       |
| Statsd | Distribution | Distribution()      | _Not specified_      | A distribution summary                                |
| Statsd | Timing       | Timing()            | _Not specified_      | Non-negative, distribution summary, Millisecond units |
| Statsd | Set          | Set()               | Cardinality          | Unique value count                                    |

The Statsd Count operation translates into either a Counter, if
increments are non-negative, or an _UpDownCounter_ if values may be
negative.  The Statsd Gauge operation translates into a Measure
instrument configured with Last Value aggregation.

The Histogram, Distribution, and Timing operations are semantically
identical, but have different units and default behavior in statsd
systems.  Each of these distribution-valued instruments can be
replaced using a Measure with a distribution-valued aggregation such
as MinMaxSumCount, Histogram, Exact, or Summary.

The Set operation does not have a direct replacement in OpenTelemetry,
however one can be constructed using a Measure or Observer instrument
and a dummy value.  Each distinct label set is naturally output each
collection interval, whether reported synchronously or asynchronously,
so the set size can be computed by using a metric label as the unique
element and no aggregation operator.

#### OpenCensus

The OpenCensus system defines three kinds of instrument:

| System     | Metric Kind  | Operation      | Aggregation                       | Notes               |
| ---------- | ------------ | -------------- | --------------------------------- | ------------------- |
| OpenCensus | Cumulative   | Inc()          | Sum                               | Positive deltas     |
| OpenCensus | Gauge        | Set()          | LastValue                         |                     |
| OpenCensus | Gauge        | Add()          | Sum                               | Deltas              |
| OpenCensus | Raw-Stats    | Record()       | Sum, Count, Mean, or Distribution |                     |

OpenCensus departed from convention with the introduction of a Views
API, which makes it possible to support fewer kinds of instrument
directly, since they can be configured in multiple ways.

Like Prometheus, the combination of multiple APIs in the Gauge
instrument is not compatible with OpenTelemetry.  A Gauge used with
Set() generally implies last-value aggregation, whereas a Gauge used
with Add() is additive and uses Sum aggregation.

Raw statstistics can be aggregated using any aggregation, and all the
OpenCensus aggregations have equivalents in OpenTelemetry.

OpenCensus supported callback-oriented asynchronous forms of both
Cumulative and Gauge instruments.  An asynchronous Cumulative
instrument would be replaced by a CumulativeObserver in OpenTelemetry.
An asynchronous Last-value Gauge would be replaced by AbsoluteObserver
or just the unrestricted Observer.  An asynchronous Additive Gauge
would be replaced by a DeltaObserver.

### Sample Proposal

The the information above will be used to propose a set of refinements
for both synchronous and asynchronous instruments in a follow-on OTEP.
What follows is a sample of the forthcoming proposal, to motivate the
discussion here.

#### Synchronous instruments

The foundational `Measure` instrument without refinements or
restrictions will be called a `Distribution` instrument.  

Along with `Counter` and `Distribution`, we recognize several less-common
but still important cases and reasons why they should be standardized:

- _UpDownCounter_: Support Prometheus additive Gauge instrument use
- _Timing_: Support Prometheus and Statsd timing measurements.

Instruments that are not standardized but may be in the future (and why):

- _CumulativeCounter_: Support a synchronous monotonic cumulative instrument
- _AbsoluteDistribution_: Support non-negative valued distributions

Instruments that are probably not seen as widely useful:

- _UpDownCumulativeCounter_: We believe this is better handled asynchronously.

#### Observer instruments

The foundational `Observer` instrument without refinements or
restrictions shall be called a `LastValueObserver` instrument.

We have identified important cases that should be standardized:

- _CumulativeObserver_: Support a cumulative monotone counter
- _DeltaObserver_: Support an asynchronous delta counter.

Observer refinements that could be standardized in the future:

- _UpDownCumulativeObserver_: Observe a non-monotonic cumulative counter
- _UpDownDeltaObserver_: Observe positive and negative deltas
- _AbsoluteLastValueObserver_: Observe non-negative current values.

## Example: Observer aggregation

Suppose you wish to capture the CPU usage of a process broken down by
the CPU core ID.  The operating system provides a mechanism to read
the current usage from the `/proc` file system, which will be reported
once per collection interval using an Observer instrument.  Because
this is a precomputed sum with a non-negative rate, use a
_CumulativeObserver_ to report this quantity with a metric label
indicating the CPU core ID.

It will be common to compute a rate of CPU usage over this data.  The
rate can be calculated for an individual CPU core by computing a
difference between the value of two metric events.  To compute the
aggregate rate across all cores–a spatial aggregation–these
differences are added together.

## Open Questions

Are there still questions surrounding the former Monotonic refinement?

Should the _CumulativeObserver_ instrument be named
_MonotonicObserver_?  In this proposal, we prefer _Cumulative_ and
_UpDownCumulative_.  _Cumulative_ is a good descriptive term in this
setting (i.e., some additive values are _cumulative_, some are
_delta_).  Being _Cumulative_ and not _UpDownCumulative_ implies
monotonicity in this proposal.

For synchronous instruments, this proposals does not standardize
_CumulativeCounter_. Such an instrument might be named
_MonotonicCounter_.

## Trade-offs and mitigations

The trade-off explicitly introduced here is that we should prefer to
create new instrument refinements, each for a dedicated purpose,
rather than create generic instruments with support for multiple
semantic options.

## Prior art and alternatives

The optional behaviors `Monotonic` and `Absolute` were first discussed
in the August 2019 Metrics working group meeting.

## Future possibilities

A future OTEP will request the introduction of two standard
refinements for the 0.4 API specification.  This will be the
`CumulativeObserver` instrument described above plus a synchronous
timing instrument named `TimingMeasure` that is equivalent to
_AbsoluteMeasure_ with the correct unit and a language-specific
duration type for measuring time.

If the above open question is decided in favor of treating the
foundational instruments as abstract, instrument names like
_NonAbsoluteMeasure_ and _NonAbsoluteCounter_ will need to be
standardized.
