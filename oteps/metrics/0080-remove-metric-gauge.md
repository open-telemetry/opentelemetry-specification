# Remove the Metric API Gauge instrument

The [Observer instrument](./0072-metric-observer.md) is semantically
identical to the metric Gauge instrument, only it is reported via a
callback instead of synchronous API calls.  Implementation has shown
that Gauge instruments are difficult to reason about because the
semantics of a "last value" Aggregator have to address questions about
statefulness--the SDK's ability to recall old values.  Observer
instruments avoid some of these concerns because they are reported
once per collection period, making it easier to reason about "all
values" in an aggregator.

## Motivation

Observer instruments improve on our ability to compute well-defined
sum and average-value aggregations over a set of last-value aggregated
data, compared with the existing Gauge instrument.  Using data from an
Observer instrument, we are easily able to pose queries about the
current sum of all current values as well as the number of distinct
values, which together define the average value.

To do the same with synchronous Gauge instruments, the SDK would
potentially be required to maintain state outside a single collection
window, which complicates memory management.  The SDK is required to
maintain state about all distinct label sets over the query evaluation
interval.  

The question is: how long should the SDK remember a gauge value?
Observer instruments do not pose this complication, because
observations are synchronized with collection instead of with the
application.

Unlike with Gauge instruments, Observer instruments naturally define
the current set of all values for a single collection period, making
sum and average-value aggregations possible without mention of the
query evaluation interval, and without the implied additional state
management.

## Explanation

The Gauge instrument's most significant feature is that its
measurement interval is arbitrary -- controlled by the application
through explicit, synchronous calls to `Set()`.  It is used to report
a current value in a synchronous context, meaning the metric event is
associated with a label set determined by some "request".

This proposal recommends that synchronously reporting Gauge values can
always be accomplished using one of the three other kinds of
instrument.

It was _already_ recommended in the specification that if the
instrument reports values you would naturally sum, you should have
used a Counter in the first place.  These are not really "current"
values when reported, they are current contributions to the sum.  We
still recommend Counters in this case.

If the gauge reports values, where you would naturally average the
last value across distinct label sets, use a Measure instrument.
Configure the instrument for last-value aggregation.  Since last-value
aggregation is not the default for Measure instruments, this will be
non-standard and require extra configuration.

If the gauge reports values, where you would naturally sum the last
value across distinct label sets, use an Observer instrument.  The
current set of entities (e.g., shards, active users, etc) constributes
a last value that should be summed.  These are different from Counter
instruments because we are not interested in a sum across time, we are
interested in a sum across distinct instances.

### Example: Reporting per-request CPU usage

Use a counter to report a quantity that is naturally summed over time,
such as CPU usage.

### Example: Reporting per-shard memory holdings

There are a number of current shards holding variable amounts of
memory by a widely-used library.  Observe the current allocation per
shard using an Observer instrument.  These can be aggregated across
hosts to compute cluster-wide memory holdings by shard, for example.

It does not make sense to compute a sum of memory holdings over
multiple periods, as these are not additive quantities.  It does makes
sense to sum the last value across hosts.

### Example: Reporting a per-request finishing account balance

There's a number that rises and falls such as a bank account balance.
This was being `Set()` at the finish of all transactions.  Replace it
with a Measure instrument and `Record()` the last value.

Similar cases: report a cpu load, specific temperature, fan speed, or
altitude measurement associated with a request.

## Internal details

The Gauge instrument will be removed from the specification at the
same time the Observer instrument is added.  This will make the
transition easier because in many cases, Observer instruments simply
replace Gauge instruments in the text.

## Trade-offs and mitigations

Not much is lost to the user from removing Gauge instruments.

There may be situations where an Observer instrument is the natural
choice but it is undesirable to be interrupted by the Metric SDK in
order to execute an Observer callback.  Situations where Observer
semantics are correct (not Counter, not Measure) but a synchronous API
is more acceptable are expected to be very rare.

To address such rare cases, here are two possibilities:

1. Implement a Gauge Set instrument backed by an Observer instrument.
The Gauge Set's job is to maintain the current set of label sets
(e.g., explicitly managed or by time-limit) and their last value, to
be reported by the Observer at each collection interval.
2. Implement an application-specific metric collection API that would
allow the application to synchronize with the SDK on collection
intervals.  For example, a transactional API allowing the application
to BEGIN and END synchronously reporting Observer instrument
observations.

## Prior art and alternatives

Many existing Metric libraries support both synchronous and
asynchronous Gauge-like instruments.

See the initial discussion in [Spec issue
412](https://github.com/open-telemetry/opentelemetry-specification/issues/412).
