# Explain the metric instruments

Propose and explain final names for the standard metric instruments theorized in [OTEP 88][otep-88] and address related confusion.

## Motivation

[OTEP 88][otep-88] introduced a logical structure for metric instruments with two foundational categories of instrument, called "synchronous" vs. "asynchronous", named "Measure" and "Observer" in the abstract sense.  The proposal identified four kinds of "refinement" and mapped out the space of _possible_ instruments, while not proposing which would actually be included in the standard.

[OTEP 93](https://github.com/open-telemetry/oteps/pull/93) proposed with a list of six standard instruments, the most necessary and useful combination of instrument refinements, plus one special case used to record timing measurements.  OTEP 93 was closed without merging after a more consistent approach to naming was uncovered.  [OTEP 96](https://github.com/open-telemetry/oteps/pull/96) made another proposal, that was closed in favor of this one after more debate surfaced.

This proposal finalizes the naming proposal for the standard instruments, seeking to address core confusion related to the "Measure" and "Observer" terms:

1. [OTEP 88][otep-88] stipulates that the terms currently in use to name synchronous and asynchronous instruments--"Measure" and "Observer"--become _abstract_ terms.  It also used phrases like "Measure-like" and "Observer-like" to discuss instruments with refinements.  This proposal states that we shall prefer the adjectives, commonly abbreviated "Sync" and "Async", when describing the kind of an instrument.  "Measure-like" means an instrument is synchronous.  "Observer-like" means that an instrument is asynchronous.
2. There is inconsistency in the hypothetical naming scheme for instruments presented in [OTEP 88][otep-88].  Note that "Counter" and "Observer" end in "-er", a noun suffix used in the sense of "[person occupationally connected with](https://www.merriam-webster.com/dictionary/-er)", while the term "Measure" does not fit this pattern.  This proposal proposes to replace the abstract term "Measure" by "Recorder", since the associated function name (verb) is specified as `Record()`.

This proposal also repeats the current specification--and the justification--for the default aggregation of each standard instrument.

## Explanation

The following table summarizes the final proposed standard instruments resulting from this set of proposals.  The columns are described in more detail below.

| Existing name | **Standard name** | Instrument kind | Function name | Input temporal quality | Default aggregation | Rate support (Monotonic) | Notes |
| ------------- | ----------------------- | ----- | --------- | -------------- | ------------- | --- | ------------------------------------ |
| Counter       | **Counter**             | Sync  | Add()     | Delta | Sum | Yes | Per-request, part of a monotonic sum |
|               | **UpDownCounter**       | Sync  | Add()     | Delta | Sum | No  | Per-request, part of a non-monotonic sum |
| Measure       | **ValueRecorder**       | Sync  | Record()  | Instantaneous | MinMaxSumCount | No  | Per-request, any non-additive measurement |
|               | **SumObserver**         | Async | Observe() | Cumulative | Sum | Yes | Per-interval, reporting a monotonic sum |
|               | **UpDownSumObserver**   | Async | Observe() | Cumulative | Sum | No  | Per-interval, reporting a non-monotonic sum |
| Observer      | **ValueObserver**       | Async | Observe() | Instantaneous | MinMaxSumCount | No  | Per-interval, any non-additive measurement |

There are three synchronous instruments and three asynchronous instruments in this proposal, although a hypothetical 10 instruments were discussed in [OTEP 88][otep-88].  Although we consider them rational and logical, two categories of instrument are excluded in this proposal: synchronous cumulative instruments and asynchronous delta instruments.

Synchronous cumulative instruments are excluded from the standard based on the [OpenTelemetry library performance guidelines](https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/performance.md).  To report a cumulative value correctly at runtime requires a degree of order dependence--thus synchronization--that OpenTelemetry API will not itself admit.  In a hypothetical example, if two actors both synchronously modify a sum and were to capture it using a synchronous cumulative metric event, the OpenTelemetry library would have to guarantee those measurements were processed in order.  The library guidelines do not support this level of synchronization; we cannot block for the sake of instrumentation, therefore we do not support synchronous cumulative instruments.

Asynchronous delta instruments are excluded from the standard based on the lack of motivating examples, but we could also justify this as a desire to keep asynchronous callbacks stateless. An observer has to have memory in order to compute deltas; it is simpler for asynchronous code to report cumulative values.

With six instruments in total, one may be curious--how does the historical Metrics API term _Gauge_ translate into this specification?  _Gauge_, in Metrics API terminology, may cover all of these instrument use-cases with the exception of `Counter`.  As defined in [OTEP 88][otep-88], the OpenTelemetry Metrics API will disambiguate these use-cases by requiring *single purpose instruments*.  The choice of instrument implies a default interpretation, a standard aggregation, and suggests how to treat Metric data in observability systems, out of the box.  Uses of `Gauge` translate into the various OpenTelemetry Metric instruments depending on what kind of values is being captured and whether the measurement is made synchronously or not.

Summarizing the naming scheme:

- If you've measured an amount of something that adds up to a total, where you are mainly interested in that total, use one of the additive instruments:
  - If synchronous and monotonic, use `Counter` with non-negative values
  - If synchronous and not monotonic, use `UpDownCounter` with arbitrary values
  - If asynchronous and a cumulative, monotonic sum is measured, use `SumObserver`
  - If asynchronous and a cumulative, arbitrary sum is measured, use `UpDownSumObserver`
- If the measurements are non-additive or additive with an interest in the distribution, use an instantaneous instrument:
  - If synchronous, use `ValueRecorder` to record a value that is part of a distribution
  - If asynchronous use `ValueObserver` to record a single measurement nearing the end of a collection interval.

### Sync vs Async instruments

Synchronous instruments are called in a request context, meaning they potentially have an associated tracing context and distributed correlation values.  Multiple metric events may occur for a synchronous instrument within a given collection interval.  Note that synchronous instruments may be called outside of a request context, such as for background computation.  In these scenarios, we may simply consider the Context to be empty.

Asynchronous instruments are reported by a callback, once per collection interval, and lack request context.  They are permitted to report only one value per distinct label set per period.  If the application observes multiple values in a single callback, for one collection interval, the last value "wins".

### Temporal quality

Measurements can be described in terms of their relationship with time.  Note: although this term logically applies and is used throughout this OTEP, discussion in the Metrics SIG meeting (4/30/2020) leads us to exclude this term from use in documenting the Metric API.  The explanation of terms here is consistent with the [terminology used in the protocol], but we will prefer to use these adjectives to describe properties of an aggregation, not properties of an instrument (despite this document continuing to use the terms freely).  In the API specification, this distinction will be described using "additive synchronous" in contrast with "additive asynchronous".

Delta measurements are those that measure a change to a sum.  Delta instruments are usually selected because the program does not need to compute the sum for itself, but is able to measure the change.  In these cases, it would require extra state for the user to report cumulative values and reporting deltas is natural.

Cumulative measurements are those that report the current value of a sum.  Cumulative instruments are usually selected because the program maintains a sum for its own purposes, or because changes in the sum are not instrumented.  In these cases, it would require extra state for the user to report delta values and reporting cumulative values is natural.

Instantaneous measurements are those that report a non-additive measurement, one where it is not natural to compute a sum.  Instantaneous instruments are usually chosen when the distribution of values is of interest, not only the sum.

The terms "Delta", "Cumulative", and "Instantaneous" as used in this proposal refer to measurement values passed to the Metric API.  The argument to an (additive) instrument with the Delta temporal quality is the change in a sum.  The argument to an (additive) instrument with the Cumulative temporal quality is itself a sum.  The argument to an instrument with the Instantaneous temporal quality is simply a value.  In the SDK specification, as measurements are aggregated and transformed for export, these terms will be used again, with the same meanings, to describe aggregates.

### Function names

Synchronous delta instruments support an `Add()` function, signifying that they add to a sum and are not cumulative.

Synchronous instantaneous instruments support a `Record()` function, signifying that they capture individual events, not only a sum.

Asynchronous instruments all support an `Observe()` function, signifying that they capture only one value per measurement interval.

### Rate support

Rate aggregation is supported for Counter and SumObserver instruments in the default implementation.

The `UpDown-` forms of additive instrument are not suitable for aggregating rates because the up- and down-changes in state may cancel each other.

Non-additive instruments can be used to derive a sum, meaning rate aggregation is possible when the values are non-negative. There is not a standard non-additive instrument with a non-negative refinement in the standard.

### Default Aggregations

Additive instruments use `Sum` aggregation by default, since by definition they are used when only the sum is of interest.

Instantaneous instruments use `MinMaxSumCount` aggregation by default, which is an inexpensive way to summarize a distribution of values.

## Detail

Here we discuss the six proposed instruments individually and mention other names considered for each.

### Counter

`Counter` is the most common synchronous instrument.  This instrument supports an `Add(delta)` function for reporting a sum, and is restricted to non-negative deltas.  The default aggregation is `Sum`, as for any additive instrument, which are those instruments with Delta or Cumulative measurement kind.

Example uses for `Counter`:

- count the number of bytes received
- count the number of accounts created
- count the number of checkpoints run
- count a number of 5xx errors.

These example instruments would be useful for monitoring the rate of any of these quantities.  In these situations, it is usually more convenient to report a change of the associated sums, as the change happens, as opposed to maintaining and reporting the sum.

Other names considered: `Adder`, `SumCounter`.

### UpDownCounter

`UpDownCounter` is similar to `Counter` except that `Add(delta)` supports negative deltas.  This makes `UpDownCounter` not useful for computing a rate aggregation.  It aggregates a `Sum`, only the sum is non-monotonic.  It is generally useful for counting changes in an amount of resources used, or any quantity that rises and falls, in a request context.

Example uses for `UpDownCounter`:

- count memory in use by instrumenting `new` and `delete`
- count queue size by instrumenting `enqueue` and `dequeue`
- count semaphore `up` and `down` operations.

These example instruments would be useful for monitoring resource levels across a group of processes.

Other names considered: `NonMonotonicCounter`.

### ValueRecorder

`ValueRecorder` is a non-additive synchronous instrument useful for recording any non-additive number, positive or negative.  Values captured by a `ValueRecorder` are treated as individual events belonging to a distribution that is being summarized.  `ValueRecorder` should be chosen either when capturing measurements that do not contribute meaningfully to a sum, or when capturing numbers that are additive in nature, but where the distribution of individual increments is considered interesting.

One of the most common uses for `ValueRecorder` is to capture latency measurements.  Latency measurements are not additive in the sense that there is little need to know the latency-sum of all processed requests.  We use a `ValueRecorder` instrument to capture latency measurements typically because we are interested in knowing mean, median, and other summary statistics about individual events.

The default aggregation for `ValueRecorder` computes the minimum and maximum values, the sum of event values, and the count of events, allowing the rate, the mean, and and range of input values to be monitored.

Example uses for `ValueRecorder` that are non-additive:

- capture any kind of timing information
- capture the acceleration experienced by a pilot
- capture nozzle pressure of a fuel injector
- capture the velocity of a MIDI key-press.

Example _additive_ uses of `ValueRecorder` capture measurements that are cumulative or delta values, but where we may have an interest in the distribution of values and not only the sum:

- capture a request size
- capture an account balance
- capture a queue length
- capture a number of board feet of lumber.

These examples show that although they are additive in nature, choosing `ValueRecorder` as opposed to `Counter` or `UpDownCounter` implies an interest in more than the sum.  If you did not care to collect information about the distribution, you would have chosen one of the additive instruments instead.  Using `ValueRecorder` makes sense for distributions that are likely to be important in an observability setting.

Use these with caution because they naturally cost more than the use of additive measurements.

Other names considered: `Distribution`, `Measure`, `LastValueRecorder`, `GaugeRecorder`, `DistributionRecorder`.

### SumObserver

`SumObserver` is the asynchronous instrument corresponding to `Counter`, used to capture a monotonic count.  "Sum" appears in the name to remind users that it is a cumulative instrument.  Use a `SumObserver` to capture any value that starts at zero and rises throughout the process lifetime but never falls.

Example uses for `SumObserver`.

- capture process user/system CPU seconds
- capture the number of cache misses.

A `SumObserver` is a good choice in situations where a measurement is expensive to compute, such that it would be wasteful to compute on every request.  For example, a system call is needed to capture process CPU usage, therefore it should be done periodically, not on each request.  A `SumObserver` is also a good choice in situations where it would be impractical or wasteful to instrument individual deltas that comprise a sum.  For example, even though the number of cache misses is a sum of individual cache-miss events, it would be too expensive to synchronously capture each event using a `Counter`.

Other names considered: `CumulativeObserver`.

### UpDownSumObserver

`UpDownSumObserver` is the asynchronous instrument corresponding to `UpDownCounter`, used to capture a non-monotonic count.  "Sum" appears in the name to remind users that it is a cumulative instrument.  Use a `UpDownSumObserver` to capture any value that starts at zero and rises or falls throughout the process lifetime.

Example uses for `UpDownSumObserver`.

- capture process heap size
- capture number of active shards
- capture number of requests started/completed
- capture current queue size.

The same considerations mentioned for choosing `SumObserver` over the synchronous `Counter` apply for choosing `UpDownSumObserver` over the synchronous `UpDownCounter`.  If a measurement is expensive to compute, or if the corresponding delta events happen so frequently that it would be impractical to instrument them, use a `UpDownSumObserver`.

Other names considered: `UpDownCumulativeObserver`.

### ValueObserver

`ValueObserver` is the asynchronous instrument corresponding to `ValueRecorder`, used to capture non-additive measurements that are expensive to compute and/or are not request-oriented.

Example uses for `ValueObserver`:

- capture CPU fan speed
- capture CPU temperature.

Note that these examples use non-additive measurements.  In the `ValueRecorder` case above, example uses were given for capturing synchronous cumulative measurements in a request context (e.g., current queue size seen by a request).  In the asynchronous case, however, how should users decide whether to use `ValueObserver` as opposed to `UpDownSumObserver`?

Consider how to report the (cumulative) size of a queue asynchronously.  Both `ValueObserver` and `UpDownSumObserver` logically apply in this case.  Asynchronous instruments capture only one measurement per interval, so in this example the `SumObserver` reports a current sum, while the `ValueObserver` reports a current sum (equal to the max and the min) and a count equal to 1.  When there is no aggregation, these results are equivalent.

The recommendation is to choose the instrument with the more-appropriate default aggregation.  If you are observing a queue size across a group of machines and the only thing you want to know is the aggregate queue size, use `SumObserver`.  If you are observing a queue size across a group of machines and you are interested in knowing the distribution of queue sizes across those machines, use `ValueObserver`.

Other names considered: `GaugeObserver`, `LastValueObserver`, `DistributionObserver`.

## Details Q&A

### Why MinMaxSumCount for `ValueRecorder`, `ValueObserver`?

There has been a question about the choice of `MinMaxSumCount` for the two non-additive instruments. The use of four values in the default aggregation for these instruments means that four values will be exported for these two instrument kinds.  The choice of Min, Max, Sum, and Count was intended to be an inexpensive default, but there is an even-more-minimal default aggregation we could choose.  The question was: Should "SumCount" be the default aggregation for these instruments?  The use of "SumCount" implies the ability to monitor the rate and the average, but not the range of values.

This proposal continues to specify the use of MinMaxSumCount for these two instruments.  Our belief is that in cases where performance and cost are concerns, usually the is an additive instruments that can be applied to lower cost.  In the case of `ValueObserver`, consider using a `SumObserver` or `UpDownSumObserver`.  In the case of `ValueRecorder`, consider configuring a less expensive view of these instruments than the default.

### `ValueObserver` temporal quality: Delta or Instantaneous?

There has been a question about labeling `ValueObserver` measurements with the temporal quality Delta vs. Instantaneous.  There is a related question: What does it mean aggregate a Min and Max value for an asynchronous instrument, which may only produce one measurement per collection interval?

The purpose of defining the default aggregation, when there is only one measurement per interval, is to specify how values will be aggregated across multiple collection intervals.  When there is no aggregation being applied, the result of MinMaxSumCount aggregation for a single collection interval is a single measurement equal to the Min, the Max, and the Sum, as well as a Count equal to 1.  Before we apply aggregation to a `ValueObserver` measurement, we can clearly define it as an Intantaneous measurement.  A measurement, captured at an instant near the end of the collection interval, is neither a cumulative nor a delta with respect to the prior collection interval.

[OTEP 88][otep-88] discusses the Last Value relationship to help address this question.  After capturing a single `ValueObserver` measurement for a given instrument and label set, that measurement becomes the Last value associated with that instrument until the next measurement is taken.

To aggregate `ValueObserver` measurements across spatial dimensions means to combine last values into a distribution at an effective moment in time.  MinMaxSumCount aggregation, in this case, means computing the Min and Max values, the measurement sum, and the count of distinct label sets that contributed measurements.  The aggregated result is considered instantaneous: it may have been computed using data points from different machines, potentially using different collection intervals.  The aggregate value must be considered approximate, with respect to time, since it averages the results from uncoordinated collection intervals.  We may have combined the last-value from a 1-minute collection interval with the last-value from a 10-second collection interval: the result is an instantaneous summary of the distribution across spatial dimensions.

Aggregating `ValueObserver` measurements across the time dimension for a given instrument and label set yields a set of measurements that were taken across a span of time, but this does not automatically lead us to consider them delta measurements.  If we aggregate 10 consecutive collection intervals for a given label set, what we have is distribution of instantaneous measurements with Count equal to 10, with the Min, Max and Sum serving to convey the average value and the range of values present in the distribution.  The result is a time-averaged distribution of instantaneous measurements.

Whether aggregating across time or space, it has been argued, the result of a `ValueObserver` instrument has the Instantaneous temporal quality.

#### Temporal and spatial aggregation of `ValueObserver` measurements

Aggregating `ValueObserver` measurements across both spatial and time dimensions must be done carefully to avoid a bias toward results computed over shorter collection intervals.  A time-averaged aggregation across spatial dimensions must take the collection interval into account, which can be done as follows:

1. Decide the time span being queried, say [T_begin, T_end].
2. Divide the time span into a list of timestamps, say [T_begin, T_begin+(T_end-T_begin)/2, T_end].
3. For each distinct label set and timestamp, compute the spatial aggregation using the last-value definition at that timestamp.  This results in a set of timestamped aggregate measurements with comparable counts.
4. Aggregate the timestamped measurements from step 3.

Steps 2 and 3 ensure that measurements taken less frequently have equal representation in the output, by virtue of computing the spatial aggregation first.  If we were to compute the temporal aggregation first, then aggreagate across spatial dimensions, then instruments collected at a higher frequency will contribute correspondingly more points to the aggregation.  Thus, we must aggregate across `ValueObserver` instruments across spatial dimensions before averaging across time.

## Open Questions

### Timing instrument

One potentially important special-purpose instrument, found in some metrics APIs, is a dedicated instrument for reporting timings.  The rationale is that when reporting timings, getting the units right is important and often not easy.  Many programming languages use a different type to represent time or a difference between times.  To correctly report a timing distribution, OpenTelemetry requires using a `ValueRecorder` but also configuring it for the units output by the clock that was used.

In the past, a proposal to create a dedicated `TimingValueRecorder` instrument was rejected.  This instrument would be identical to a `ValueRecorder`, but its `Record()` method would be specialized for the correct type used to represent a duration, so that the units could be set correctly and automatically.  A related pattern is a `Timer` or `StopWatch` instrument, one responsible for both measuring and capturing a timing.

Should types such as these be added as helpers?  For example, should `TimingValueRecorder` be a real instrument, or should it be a helper that wraps around a `ValueRecorder`?  There is a concern that making `TimingValueRecorder` into a helper makes it less visible, less standard, and that not having it at all will encourage instrumentation mistakes.

This may be revisited in the future.

### Synchronous cumulative and asynchronous delta helpers

A cumulative measurement can be converted into delta measurement by remembering the last-reported value.  A helper instrument could offer to emulate synchronous cumulative measurements by remembering the last-reported value and reporting deltas synchronously.

A delta measurement can be converted into a cumluative measurement by remembering the sum of all reported values.  A helper instrument could offer to emulate asynchronous delta measurements in this way.

Should helpers of this nature be standardized, if there is demand?  These helpers are excluded from the standard because they carry a number of caveats, but as helpers they can easily do what an OpenTelemery SDK cannot do in general.  For example, we are avoiding synchronous cumulative instruments because they seem to imply ordering that an SDK is not required to support, however an instrument helper that itself uses a lock can easily convert to deltas.

Should such helpers be standardized?  The answer is probably no.

[otep-88]: https://github.com/open-telemetry/oteps/blob/master/text/0088-metric-instrument-optional-refinements.md
