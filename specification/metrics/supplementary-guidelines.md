# Supplementary Guidelines

Note: this document is NOT a spec, it is provided to support the Metrics
[API](./api.md) and [SDK](./sdk.md) specifications, it does NOT add any extra
requirements to the existing specifications.

Table of Contents:

* [Guidelines for instrumentation library
  authors](#guidelines-for-instrumentation-library-authors)
* [Guidelines for SDK authors](#guidelines-for-sdk-authors)
  * [Memory efficiency](#memory-efficiency)

## Guidelines for instrumentation library authors

TBD

## Guidelines for SDK authors

### Memory efficiency

The OpenTelemetry Metrics [Data Model](./datamodel.md) and [SDK](./sdk.md) are
designed to support both Cumulative and Delta
[Temporality](./datamodel.md#temporality). It is important to understand that
temporality will impact how the SDK could manage memory usage. Let's take the
following example:

* During the time range (T<sub>0</sub>, T<sub>1</sub>]:
  * HTTP verb = `GET`, status = `200`, duration = `50 (ms)`
  * HTTP verb = `GET`, status = `200`, duration = `100 (ms)`
  * HTTP verb = `GET`, status = `500`, duration = `1 (ms)`
* During the time range (T<sub>1</sub>, T<sub>2</sub>]:
  * no HTTP request has been received
* During the time range (T<sub>2</sub>, T<sub>3</sub>]
  * HTTP verb = `GET`, status = `500`, duration = `5 (ms)`
  * HTTP verb = `GET`, status = `500`, duration = `2 (ms)`
* During the time range (T<sub>3</sub>, T<sub>4</sub>]:
  * HTTP verb = `GET`, status = `200`, duration = `100 (ms)`
* During the time range (T<sub>4</sub>, T<sub>5</sub>]:
  * HTTP verb = `GET`, status = `200`, duration = `100 (ms)`
  * HTTP verb = `GET`, status = `200`, duration = `30 (ms)`
  * HTTP verb = `GET`, status = `200`, duration = `50 (ms)`

Let's imagine we export the metrics as [Histogram](./datamodel.md#histogram),
and to simplify the story we will only have one histogram bucket `(-Inf, +Inf)`:

If we export the metrics using **Delta Temporality**:

* (T<sub>0</sub>, T<sub>1</sub>]
  * dimensions: {verb = `GET`, status = `200`}, count: `2`, min: `50 (ms)`, max:
    `100 (ms)`
  * dimensions: {verb = `GET`, status = `500`}, count: `1`, min: `1 (ms)`, max:
    `1 (ms)`
* (T<sub>1</sub>, T<sub>2</sub>]
  * nothing since we don't have any Measurement received
* (T<sub>2</sub>, T<sub>3</sub>]
  * dimensions: {verb = `GET`, status = `500`}, count: `2`, min: `2 (ms)`, max:
    `5 (ms)`
* (T<sub>3</sub>, T<sub>4</sub>]
  * dimensions: {verb = `GET`, status = `200`}, count: `1`, min: `100 (ms)`,
    max: `100 (ms)`
* (T<sub>4</sub>, T<sub>5</sub>]
  * dimensions: {verb = `GET`, status = `200`}, count: `3`, min: `30 (ms)`, max:
    `100 (ms)`

You can see that the SDK **only needs to track what has happened after the
latest collection/export cycle**. For example, when the SDK started to process
measurements in (T<sub>1</sub>, T<sub>2</sub>], it can completely forget about
what has happened during (T<sub>0</sub>, T<sub>1</sub>].

If we export the metrics using **Cumulative Temporality**:

* (T<sub>0</sub>, T<sub>1</sub>]
  * dimensions: {verb = `GET`, status = `200`}, count: `2`, min: `50 (ms)`, max:
    `100 (ms)`
  * dimensions: {verb = `GET`, status = `500`}, count: `1`, min: `1 (ms)`, max:
    `1 (ms)`
* (T<sub>0</sub>, T<sub>2</sub>]
  * dimensions: {verb = `GET`, status = `200`}, count: `2`, min: `50 (ms)`, max:
    `100 (ms)`
  * dimensions: {verb = `GET`, status = `500`}, count: `1`, min: `1 (ms)`, max:
    `1 (ms)`
* (T<sub>0</sub>, T<sub>3</sub>]
  * dimensions: {verb = `GET`, status = `200`}, count: `2`, min: `50 (ms)`, max:
    `100 (ms)`
  * dimensions: {verb = `GET`, status = `500`}, count: `3`, min: `1 (ms)`, max:
    `5 (ms)`
* (T<sub>0</sub>, T<sub>4</sub>]
  * dimensions: {verb = `GET`, status = `200`}, count: `3`, min: `50 (ms)`, max:
    `100 (ms)`
  * dimensions: {verb = `GET`, status = `500`}, count: `3`, min: `1 (ms)`, max:
    `5 (ms)`
* (T<sub>0</sub>, T<sub>5</sub>]
  * dimensions: {verb = `GET`, status = `200`}, count: `6`, min: `30 (ms)`, max:
    `100 (ms)`
  * dimensions: {verb = `GET`, status = `500`}, count: `3`, min: `1 (ms)`, max:
    `5 (ms)`

If we choose **Cumulative Temporality**, the SDK **has to track what has
happened prior to the latest collection/export cycle**, in this worst case, the
SDK **will remember what has happened since the ever beginning of the process**.
This is known as Delta->Cumulative conversion.

Imagine if we have a long running service and we collect metrics with 7
dimensions, and each dimension can have 30 different values. We might eventually
end up having to remember the complete set of all `21,870,000,000` permutations!
This **cardinality explosion** a well known challenge in the metrics space.

Making it even worse, if we export the permutations even if there is no recent
updates, the export batch could become huge and will be very costly. For
example, do we really need/want to export the same thing for (T<sub>0</sub>,
T<sub>2</sub>] in the above case?

So here are some suggestions that we encourage SDK implementers to consider:

* You want to control the memory usage rather than allow it to grow indefinitely
  / unbounded - regardless of what aggregation temporality is being used.
* You want to improve the memory efficiency by being able to **forget about
  things that are no longer needed**.
* You probably don't want to keep exporting the same thing over and over again,
  if there is no updates. You might want to consider [Resets and
  Gaps](./datamodel.md#resets-and-gaps). For example, if a Cumulative metrics
  stream hasn't received any updates for a long period of time, would it be okay
  to reset the start time?

Now we can explore a more interesting topic, Cumulative->Delta conversion.

In the above case, we have Measurements reported by a [Histogram
Instrument](./api.md#histogram). What if we collect measurements from an
[Asynchronous Counter](./api.md#asynchronous-counter)?

The following example shows the number page faults of each thread since the
thread ever started:

* During the time range (T<sub>0</sub>, T<sub>1</sub>]:
  * ProcessId = `1001`, ThreadId = `1`, PageFaults = `50`
  * ProcessId = `1001`, ThreadId = `2`, PageFaults = `30`
* During the time range (T<sub>1</sub>, T<sub>2</sub>]:
  * ProcessId = `1001`, ThreadId = `1`, PageFaults = `53`
  * ProcessId = `1001`, ThreadId = `2`, PageFaults = `38`
* During the time range (T<sub>2</sub>, T<sub>3</sub>]
  * ProcessId = `1001`, ThreadId = `1`, PageFaults = `56`
  * ProcessId = `1001`, ThreadId = `2`, PageFaults = `42`
* During the time range (T<sub>3</sub>, T<sub>4</sub>]:
  * ProcessId = `1001`, ThreadId = `1`, PageFaults = `60`
  * ProcessId = `1001`, ThreadId = `2`, PageFaults = `47`
* During the time range (T<sub>4</sub>, T<sub>5</sub>]:
  * thread 1 died, thread 3 started
  * ProcessId = `1001`, ThreadId = `2`, PageFaults = `53`
  * ProcessId = `1001`, ThreadId = `3`, PageFaults = `5`

If we export the metrics using **Cumulative Temporality**, it is actually quite
straightforward - we just take the data being reported from the asynchronous
instruments and send them. We might want to consider if [Resets and
Gaps](./datamodel.md#resets-and-gaps) should be used to denote the end of a
metric stream - e.g. thread 1 died, the thread ID might be reused by the
operating system, and we probably don't want to confuse the metrics backend.

If we export the metrics using **Delta Temporality**, we will have to remember
the last value of **everything single permutation we've encountered so far**,
because if we don't, we won't be able to calculate the delta value using
`current value - last value`. And you can tell, this is super expensive.

Making it more interesting, if we have min/max value, it is **mathematically
impossible** to reliably deduce the Delta temporality from Cumulative
temporality. For example, if the maximum value is 10 during (T<sub>0</sub>,
T<sub>2</sub>] and the maximum value is 20 during (T<sub>0</sub>,
T<sub>3</sub>], we know that the maximum value druing (T<sub>2</sub>,
T<sub>3</sub>] must be 20. But if the maximum value is 20 during (T<sub>0</sub>,
T<sub>2</sub>] and the maximum value is also 20 during (T<sub>0</sub>,
T<sub>3</sub>], we wouldn't know what is the maximum value during
(T<sub>2</sub>, T<sub>3</sub>], unless we know that there is no value (count =
0).

So here are some suggestions that we encourage SDK implementers to consider:

* You probably don't want to encourage your users to do Cumulative to Delta
  conversion. Actually you might want to discourage them from doing this.
* If you have to do Cumulative to Delta conversion, and you encountered min/max,
  rather than drop the data on the floor, you might want to convert to something
  useful - e.g. [Gauge](./datamodel.md#gauge).
