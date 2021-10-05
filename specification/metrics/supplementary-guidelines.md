# Supplementary Guidelines

Note: this document is NOT a spec, it is provided to support the Metrics
[API](./api.md) and [SDK](./sdk.md) specifications, it does NOT add any extra
requirements to the existing specifications.

Table of Contents:

* [Guidelines for instrumentation library
  authors](#guidelines-for-instrumentation-library-authors)
  * [Instrument selection](#instrument-selection)
  * [Semantic convention](#semantic-convention)
* [Guidelines for SDK authors](#guidelines-for-sdk-authors)
  * [Aggregation temporality](#aggregation-temporality)
  * [Memory management](#memory-management)

## Guidelines for instrumentation library authors

### Instrument selection

The [Instruments](./api.md#instrument) are part of the [Metrics API](./api.md).
They allow [Measurements](./api.md#measurement) to be recorded
[synchronously](./api.md#synchronous-instrument) or
[asynchronously](./api.md#asynchronous-instrument).

Choosing the correct instrument is important, because:

* It helps the library to achieve better efficiency. For example, if we want to
  report room temperature to [Prometheus](https://prometheus.io), we want to
  consider using an [Asynchronous Gauge](./api.md#asynchronous-gauge) rather
  than periodically poll the sensor, so that we only access the sensor when
  scraping happened.
* It makes the consumption easier for the user of the library. For example, if
  we want to report HTTP server request latency, we want to consider a
  [Histogram](./api.md#histogram), so most of the users can get a reasonable
  experience (e.g. default buckets, min/max) by simply enabling the metrics
  stream, rather than doing extra configurations.
* It generates clarity to the semantic of the metrics stream, so the consumers
  have better understanding of the results. For example, if we want to report
  the process heap size, by using an [Asynchronous
  UpDownCounter](./api.md#asynchronous-updowncounter) rather than an
  [Asynchronous Gauge](./api.md#asynchronous-gauge), we've made it explicit that
  the consumer can add up the numbers across all processes to get the "total
  heap size".

Here is one way of choosing the correct instrument:

* I want to **count** something (by recording a delta value):
  * If the value is monotonically increasing (the delta value is always
    non-negative) - use a [Counter](./api.md#counter).
  * If the value is NOT monotonically increasing (the delta value can be
    positive, negative or zero) - use an
    [UpDownCounter](./api.md#updowncounter).
* I want to **record** or **time** something, and the **statistics** about this
  thing are likely to be meaningful - use a [Histogram](./api.md#histogram).
* I want to **measure** something (by reporting an absolute value):
  * If it makes NO sense to add up the values across different dimensions, use
    an [Asynchronous Gauge](./api.md#asynchronous-gauge).
  * If it makes sense to add up the values across different dimensions:
    * If the value is monotonically increasing - use an [Asynchronous
      Counter](./api.md#asynchronous-counter).
    * If the value is NOT monotonically increasing - use an [Asynchronous
      UpDownCounter](./api.md#asynchronous-updowncounter).

### Semantic convention

Once you decided [which instrument(s) to be used](#instrument-selection), you
will need to decide the names for the instruments and attributes.

It is highly recommended that you align with the `OpenTelemetry Semantic
Conventions`, rather than inventing your own semantics.

## Guidelines for SDK authors

### Aggregation temporality

The OpenTelemetry Metrics [Data Model](./datamodel.md) and [SDK](./sdk.md) are
designed to support both Cumulative and Delta
[Temporality](./datamodel.md#temporality). It is important to understand that
temporality will impact how the SDK could manage memory usage. Let's take the
following HTTP requests example:

* During the time range (T<sub>0</sub>, T<sub>1</sub>]:
  * verb = `GET`, status = `200`, duration = `50 (ms)`
  * verb = `GET`, status = `200`, duration = `100 (ms)`
  * verb = `GET`, status = `500`, duration = `1 (ms)`
* During the time range (T<sub>1</sub>, T<sub>2</sub>]:
  * no HTTP request has been received
* During the time range (T<sub>2</sub>, T<sub>3</sub>]
  * verb = `GET`, status = `500`, duration = `5 (ms)`
  * verb = `GET`, status = `500`, duration = `2 (ms)`
* During the time range (T<sub>3</sub>, T<sub>4</sub>]:
  * verb = `GET`, status = `200`, duration = `100 (ms)`
* During the time range (T<sub>4</sub>, T<sub>5</sub>]:
  * verb = `GET`, status = `200`, duration = `100 (ms)`
  * verb = `GET`, status = `200`, duration = `30 (ms)`
  * verb = `GET`, status = `200`, duration = `50 (ms)`

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

You can see that we are performing Delta->Cumulative conversion, and the SDK
**has to track what has happened prior to the latest collection/export cycle**,
in the worst case, the SDK **will have to remember what has happened since the
beginning of the process**.

Imagine if we have a long running service and we collect metrics with 7
dimensions and each dimension can have 30 different values. We might eventually
end up having to remember the complete set of all `21,870,000,000` permutations!
This **cardinality explosion** is a well-known challenge in the metrics space.

Making it even worse, if we export the permutations even if there are no recent
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

In the above case, we have Measurements reported by a [Histogram
Instrument](./api.md#histogram). What if we collect measurements from an
[Asynchronous Counter](./api.md#asynchronous-counter)?

The following example shows the number of [page
faults](https://en.wikipedia.org/wiki/Page_fault) of each thread since the
thread ever started:

* During the time range (T<sub>0</sub>, T<sub>1</sub>]:
  * pid = `1001`, tid = `1`, #PF = `50`
  * pid = `1001`, tid = `2`, #PF = `30`
* During the time range (T<sub>1</sub>, T<sub>2</sub>]:
  * pid = `1001`, tid = `1`, #PF = `53`
  * pid = `1001`, tid = `2`, #PF = `38`
* During the time range (T<sub>2</sub>, T<sub>3</sub>]
  * pid = `1001`, tid = `1`, #PF = `56`
  * pid = `1001`, tid = `2`, #PF = `42`
* During the time range (T<sub>3</sub>, T<sub>4</sub>]:
  * pid = `1001`, tid = `1`, #PF = `60`
  * pid = `1001`, tid = `2`, #PF = `47`
* During the time range (T<sub>4</sub>, T<sub>5</sub>]:
  * thread 1 died, thread 3 started
  * pid = `1001`, tid = `2`, #PF = `53`
  * pid = `1001`, tid = `3`, #PF = `5`

If we export the metrics using **Cumulative Temporality**:

* (T<sub>0</sub>, T<sub>1</sub>]
  * dimensions: {pid = `1001`, tid = `1`}, sum: `50`
  * dimensions: {pid = `1001`, tid = `2`}, sum: `30`
* (T<sub>0</sub>, T<sub>2</sub>]
  * dimensions: {pid = `1001`, tid = `1`}, sum: `53`
  * dimensions: {pid = `1001`, tid = `2`}, sum: `38`
* (T<sub>0</sub>, T<sub>3</sub>]
  * dimensions: {pid = `1001`, tid = `1`}, sum: `56`
  * dimensions: {pid = `1001`, tid = `2`}, sum: `42`
* (T<sub>0</sub>, T<sub>4</sub>]
  * dimensions: {pid = `1001`, tid = `1`}, sum: `60`
  * dimensions: {pid = `1001`, tid = `2`}, sum: `47`
* (T<sub>0</sub>, T<sub>5</sub>]
  * dimensions: {pid = `1001`, tid = `2`}, sum: `53`
  * dimensions: {pid = `1001`, tid = `3`}, sum: `5`

It is quite straightforward - we just take the data being reported from the
asynchronous instruments and send them. We might want to consider if [Resets and
Gaps](./datamodel.md#resets-and-gaps) should be used to denote the end of a
metric stream - e.g. thread 1 died, the thread ID might be reused by the
operating system, and we probably don't want to confuse the metrics backend.

If we export the metrics using **Delta Temporality**:

* (T<sub>0</sub>, T<sub>1</sub>]
  * dimensions: {pid = `1001`, tid = `1`}, delta: `50`
  * dimensions: {pid = `1001`, tid = `2`}, delta: `30`
* (T<sub>1</sub>, T<sub>2</sub>]
  * dimensions: {pid = `1001`, tid = `1`}, delta: `3`
  * dimensions: {pid = `1001`, tid = `2`}, delta: `8`
* (T<sub>2</sub>, T<sub>3</sub>]
  * dimensions: {pid = `1001`, tid = `1`}, delta: `3`
  * dimensions: {pid = `1001`, tid = `2`}, delta: `4`
* (T<sub>3</sub>, T<sub>4</sub>]
  * dimensions: {pid = `1001`, tid = `1`}, delta: `4`
  * dimensions: {pid = `1001`, tid = `2`}, delta: `5`
* (T<sub>4</sub>, T<sub>5</sub>]
  * dimensions: {pid = `1001`, tid = `2`}, delta: `6`
  * dimensions: {pid = `1001`, tid = `3`}, delta: `5`

You can see that we are performing Cumulative->Delta conversion, and it requires
us to remember the last value of **every single permutation we've encountered so
far**, because if we don't, we won't be able to calculate the delta value using
`current value - last value`. And as you can tell, this is super expensive.

Making it more interesting, if we have min/max value, it is **mathematically
impossible** to reliably deduce the Delta temporality from Cumulative
temporality. For example:

* If the maximum value is 10 during (T<sub>0</sub>, T<sub>2</sub>] and the
  maximum value is 20 during (T<sub>0</sub>, T<sub>3</sub>], we know that the
  maximum value during (T<sub>2</sub>, T<sub>3</sub>] must be 20.
* If the maximum value is 20 during (T<sub>0</sub>, T<sub>2</sub>] and the
  maximum value is also 20 during (T<sub>0</sub>, T<sub>3</sub>], we wouldn't
  know what the maximum value is during (T<sub>2</sub>, T<sub>3</sub>], unless
  we know that there is no value (count = 0).

So here are some suggestions that we encourage SDK implementers to consider:

* You probably don't want to encourage your users to do Cumulative->Delta
  conversion. Actually, you might want to discourage them from doing this.
* If you have to do Cumulative->Delta conversion, and you encountered min/max,
  rather than drop the data on the floor, you might want to convert them to
  something useful - e.g. [Gauge](./datamodel.md#gauge).

### Memory management

Memory management is a wide topic, here we will only cover some of the most
important things for OpenTelemetry SDK.

**Choose a better design so the SDK has less things to be memorized**, avoid
keeping things in memory unless there is a must need. One good example is the
[aggregation temporality](#aggregation-temporality).

**Design a better memory layout**, so the storage is efficient and accessing the
storage can be fast. This is normally specific to the targeting programming
language and platform. For example, aligning the memory to the CPU cache line,
keeping the hot memories close to each other, keeping the memory close to the
hardware (e.g. non-paged pool,
[NUMA](https://en.wikipedia.org/wiki/Non-uniform_memory_access)).

**Pre-allocate and pool the memory**, so the SDK doesn't have to allocate memory
on-the-fly. This is especially useful to language runtimes that have garbage
collectors, as it ensures the hot path in the code won't trigger garbage
collection.

**Limit the memory usage, and handle critical memory condition.** The general
expectation is that a telemetry SDK should not fail the application. This can be
done via some dimension-capping algorithm - e.g. start to combine/drop some data
points when the SDK hits the memory limit, and provide a mechanism to report the
data loss.

**Provide configurations to the application owner.** The answer to _"what is an
efficient memory usage"_ is ultimately depending on the goal of the application
owner. For example, the application owners might want to spend more memory in
order to keep more permutations of metrics dimensions, or they might want to use
memory aggressively for certain dimensions that are important, and keep a
conservative limit for dimensions that are less important.
