# Metric observer specification (refinement)

The metric observer gauge was described in [OTEP
0008](0008-metric-observer.md) but left out of the current metrics
specification because the prior OTEP did not clarify the valid calling
conventions for observer gauge metric instruments.  This proposal
completely replaces OTEP 0008.

## Motivation

An [earlier version of the metrics specification](
https://github.com/open-telemetry/opentelemetry-specification/blob/597718b3fcfaf10bcf45d93f99b66f94a28048cb/specification/api-metrics.md)
described metric callbacks as an alternate means of generating metric
events, allowing the application to generate metric events only as
often as desired by the collection interval.  It specified this
support for all instrument kinds.

This proposal restores the ability to use callbacks only with a
dedicated `Observer` kind of instrument with the same semantics as
Gauge instruments.  Like a Gauge instrument, Observer instruments are
used to report the current value of a variable.

We may ask, why should Observer instruments be a first-class part of
the API, as opposed to simply registering non-instrument-specific
callbacks to call user-level code on the metrics collection interval?
That would permit the use of ordinary Gauge instruments as a stand-in
for the Observer instrument proposed here.  The approach proposed here
is more flexible because it permits the Meter implementation to
control the collection interval on a per-instrument basis as well as
to disable instruments.

## Explanation

Gauge metric instruments are typically used to reflect properties that
are pre-computed or instantaneously read by a system, where the
measurement interval is arbitrary.  When selecting a Gauge, as opposed
to the Counter or measure kind of metric instrument, there could be
significant computational cost in computing or reading the current
value.  When this is the case, it is understandable that we are
interested in providing values on demand, as an optimization.

The optimization aspect of Observer instruments is critical to their
purpose.  If the simpler alternative suggested above--registering
non-instrument-specific callbacks--were implemented instead, callers
would demand a way to ask whether an instrument was "recording" or
not, similar to the [`Span.IsRecording`
API](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/trace/api.md#isrecording).

Observer instruments are semantically equivalent to gauge instruments,
except they support callbacks instead of a `Set()` operation.
Observer callbacks support `Observe()` instead.  Why support callbacks
with Gauge semantics but not do the same for Counter and Measure
semantics?

### Why not Measure callbacks?

Measure instruments, by definition, carry information about the
individual measurements, so there is no benefit to be had in deferring
evaluation to a callback.  Observer callbacks are designed to reduce
the number of measurements, which is incompatible with the semantics
of Measure instruments.

### Why not Counter callbacks?

Counter instruments can be expressed as Observer instruments when they
are expensive to pre-compute or will be instantaneously read.  There
are two ways these can be treated using Observer instrument semantics.

Observer instruments, like Gauge instruments, use a "last value"
aggregation by default.  With this default interpretation in mind, a
monotonic Counter can be expressed as a monotonic Observer instrument
simply by reporting the current sum from `Observe()`, in which case
the "last value" may be interpreted directly as a sum.  Systems with
support for rate calculations over current sums (e.g., Prometheus)
will be able to use these metrics directly.  Non-monotonic Counters
may be expressed as their current value, but they cannot meaningfully
be aggregated in this way.

The preferred way to `Observe()` Counter-like data from an Observer
instrument callback is to report deltas in the callback and configure
a Sum aggregation in the exporter.  Data reported in this way will
support rate calculations just as if they were true Counters.

### Differences between Gauge and Observer

One significant difference between gauges that are explicitly `Set()`,
as compared with observer callbacks, is that `Set()` happens inside a
context (i.e., its distributed context), whereas the observer callback
does not execute with any distributed context.  

Whereas Gauge values do have context at the moment `Set()` is called,
Observer callbacks do not.  Observer instruments are appropriate for
reporting values that are not request specific.

## Details

Observer instruments are semantically equivalent to Gauge instruments
but use different calling conventions.  Use the language-specific
constructor for an Observer instrument (e.g.,
`metric.NewFloat64Observer()`).  Observer instruments support the
`Monotonic` and `NonMonotonic` options, the same as Gauge instruments.

Callbacks should avoid blocking.  The implementation may be required
to cancel computation if the callback blocks for too long.

Callbacks must not be called synchronously with application code via
any OpenTelemetry API.  This prevents the application from potentially
deadlocking itself by being called synchronously from its own thread.
Implementations that cannot provide this guarantee should prefer not
to implement Observer instrsuments.

Callbacks may be called synchronously in the SDK on behalf of an
exporter, provided it does not contradict the requirement above.

Callbacks should avoid calling OpenTelemetry APIs other than the
interface provided to `Observe()`.  This prevents the SDK from
potentially deadlocking itself by being called synchronously from its
own thread.  We recognize this may be impossible or expensive to
enforce.  SDKs should document how they respond to such attempts at
re-entry.

### Observer calling conventions

Observer callbacks are called with an `ObserverResult`, an interface
that supports capturing events directly in the callback, as follows.

To capture an observation with a specific `LabelSet`, call the
`ObserverResult` directly using `ObserverResult.Observe(value,
LabelSet)`.

There is no equivalent of a "bound" observer instrument as there is
with Counter, Gauge, and Measure instruments.  A bound calling
convention is not needed for Observer instruments because there is
little if any performance benefit in doing so (as Observer instruments
are called during collection, there is no need to maintain "active"
records concurrent with collection).

Multiple observations are permitted in a single callback invocation.

The `ObserverResult` passed to a callback should not be used outside the
invocation to which it is passed.

#### One callback per instrument

The API _could_ support registering independent callbacks tied to
registered ("bound") label sets, instead it takes the approach of
supporting one callback per instrument.  There are two cases to
consider: (a) where the source of an instrument's values provides one
value at a time, (b) where the source of an instrument's values
provides several values at once.

The decision to support one callback per instrument is justified
because it is relatively easy in case (a) above to call the source
multiple times for multiple values, while it is relatively difficult
in case (b) above to call the source once and report values from
multiple callbacks.

### Pseudocode

An example:

```
class YourClass {
  private static final Meter meter = ...;
  private static final ObserverDouble cpuLoad = ...;

  void init() {
    LabelSet labelSet = meter.createLabelSet("low_power", isLowPowerMode());
    cpuLoad.setCallback(
        new ObserverDouble.Callback<ObserverDouble.Result>() {
          @Override
          public void update(Result result) {
              result.Observe(getCPULoad(), labelSet);
        });
  }
}
```

## Trade-offs and mitigations

Callbacks are a relatively dangerous programming pattern, which may
require care to avoid deadlocks between the application and the API or
the SDK.  Implementations SHOULD consider preventing deadlocks through
any means that are safe and economical.
