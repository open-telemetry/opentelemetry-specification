# Supplementary Guidelines

Note: this document is NOT a spec, it is provided to support the Metrics
[API](./api.md) and [SDK](./sdk.md) specifications, it does NOT add any extra
requirements to the existing specifications.

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [Guidelines for instrumentation library authors](#guidelines-for-instrumentation-library-authors)
  * [Instrument selection](#instrument-selection)
  * [Additive property](#additive-property)
    + [Numeric type selection](#numeric-type-selection)
      - [Integer](#integer)
      - [Float](#float)
  * [Monotonicity property](#monotonicity-property)
  * [Semantic convention](#semantic-convention)
- [Guidelines for SDK authors](#guidelines-for-sdk-authors)
  * [Aggregation temporality](#aggregation-temporality)
    + [Synchronous example](#synchronous-example)
      - [Synchronous example: Delta aggregation temporality](#synchronous-example-delta-aggregation-temporality)
      - [Synchronous example: Cumulative aggregation temporality](#synchronous-example-cumulative-aggregation-temporality)
    + [Asynchronous example](#asynchronous-example)
      - [Asynchronous example: Cumulative temporality](#asynchronous-example-cumulative-temporality)
      - [Asynchronous example: Delta temporality](#asynchronous-example-delta-temporality)
      - [Asynchronous example: attribute removal in a view](#asynchronous-example-attribute-removal-in-a-view)
  * [Memory management](#memory-management)

<!-- tocstop -->

</details>

## Guidelines for instrumentation library authors

### Instrument selection

The [Instruments](./api.md#instrument) are part of the [Metrics API](./api.md).
They allow [Measurements](./api.md#measurement) to be recorded
[synchronously](./api.md#synchronous-instrument-api) or
[asynchronously](./api.md#asynchronous-instrument-api).

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
  * If the measurement values are [non-additive](#additive-property), use
    an [Asynchronous Gauge](./api.md#asynchronous-gauge).
  * If the measurement values are [additive](#additive-property):
    * If the value is monotonically increasing - use an [Asynchronous
      Counter](./api.md#asynchronous-counter).
    * If the value is NOT monotonically increasing - use an [Asynchronous
      UpDownCounter](./api.md#asynchronous-updowncounter).

### Additive property

In OpenTelemetry a [Measurement](./api.md#measurement) encapsulates a value and
a set of [`Attributes`](../common/README.md#attribute). Depending on the nature
of the measurements, they can be additive, non-additive or somewhere in the
middle. Here are some examples:

* The server temperature is non-additive. The temperatures in the table below
  add up to `226.2`, but this value has no practical meaning.

  | Hostname | Temperature (F) |
  | -------- | --------------- |
  | MachineA | 58.8            |
  | MachineB | 86.1            |
  | MachineC | 81.3            |

* The mass of planets is additive, the value `1.18e25` (`3.30e23 + 6.42e23 +
  4.87e24 + 5.97e24`) means the combined mass of terrestrial planets in the
  solar system.

  | Planet Name | Mass (kg)       |
  | ----------- | --------------- |
  | Mercury     | 3.30e23         |
  | Mars        | 6.42e23         |
  | Venus       | 4.87e24         |
  | Earth       | 5.97e24         |

* The voltage of battery cells can be added up if the batteries are connected in
  series. However, if the batteries are connected in parallel, it makes no sense
  to add up the voltage values anymore.

In OpenTelemetry, each [Instrument](./api.md#instrument) implies whether it is
additive or not.

| Instrument                                                        | Additive          |
| ----------------------------------------------------------------- | ----------------- |
| [Counter](./api.md#counter)                                       | additive          |
| [UpDownCounter](./api.md#updowncounter)                           | additive          |
| [Histogram](./api.md#histogram)                                   | mixed<sup>1</sup> |
| [Asynchronous Gauge](./api.md#asynchronous-gauge)                 | non-additive      |
| [Asynchronous Counter](./api.md#asynchronous-counter)             | additive          |
| [Asynchronous UpDownCounter](./api.md#asynchronous-updowncounter) | additive          |

1: The Histogram bucket counts are additive if the buckets are the same, the sum is additive, but the min and max are non-additive.

#### Numeric type selection

For Instruments which take increments and/or decrements as the input (e.g.
[Counter](./api.md#counter) and [UpDownCounter](./api.md#updowncounter)), the
underlying numeric types (e.g., signed integer, unsigned integer, double) have
direct impact on the dynamic range, precision, and how the data is interpreted.
Typically, integers are precise but have limited dynamic range, and might see
overflow/underflow. [IEEE-754 double-precision floating-point
format](https://en.wikipedia.org/wiki/Double-precision_floating-point_format) has a
wide dynamic range of numeric values with the sacrifice on precision.

##### Integer

Let's take an example: a 16-bit signed integer is used to count the committed
transactions in a database, reported as cumulative sum every 15 seconds:

* During (T<sub>0</sub>, T<sub>1</sub>], we reported `70`.
* During (T<sub>0</sub>, T<sub>2</sub>], we reported `115`.
* During (T<sub>0</sub>, T<sub>3</sub>], we reported `116`.
* During (T<sub>0</sub>, T<sub>4</sub>], we reported `128`.
* During (T<sub>0</sub>, T<sub>5</sub>], we reported `128`.
* During (T<sub>0</sub>, T<sub>6</sub>], we reported `173`.
* ...
* During (T<sub>0</sub>, T<sub>n+1</sub>], we reported `1,872`.
* During (T<sub>n+2</sub>, T<sub>n+3</sub>], we reported `35`.
* During (T<sub>n+2</sub>, T<sub>n+4</sub>], we reported `76`.

In the above case, a backend system could tell that there was likely a system
restart (because the start time has changed from T<sub>0</sub> to
T<sub>n+2</sub>) during (T<sub>n+1</sub>, T<sub>n+2</sub>], so it has chance to
adjust the data to:

* (T<sub>0</sub>, T<sub>n+3</sub>] : `1,907` (1,872 + 35).
* (T<sub>0</sub>, T<sub>n+4</sub>] : `1,948` (1,872 + 76).

Imagine we keep the database running:

* During (T<sub>0</sub>, T<sub>m+1</sub>], we reported `32,758`.
* During (T<sub>0</sub>, T<sub>m+2</sub>], we reported `32,762`.
* During (T<sub>0</sub>, T<sub>m+3</sub>], we reported `-32,738`.
* During (T<sub>0</sub>, T<sub>m+4</sub>], we reported `-32,712`.

In the above case, the backend system could tell that there was an integer
overflow during (T<sub>m+2</sub>, T<sub>m+3</sub>] (because the start time
remains the same as before, and the value becomes negative), so it has chance to
adjust the data to:

* (T<sub>0</sub>, T<sub>m+3</sub>] : `32,798` (32,762 + 36).
* (T<sub>0</sub>, T<sub>m+4</sub>] : `32,824` (32,762 + 62).

As we can see in this example, even with the limitation of 16-bit integer, we
can count the database transactions with high fidelity, without having to
worry about information loss caused by integer overflows.

It is important to understand that we are handling counter reset and integer
overflow/underflow based on the assumption that we've picked the proper dynamic
range and reporting frequency. Imagine if we use the same 16-bit signed integer
to count the transactions in a data center (which could have thousands if not
millions of transactions per second), we wouldn't be able to tell if `-32,738`
was a result of `32,762 + 36` or `32,762 + 65,572` or even `32,762 + 131,108` if
we report the data every 15 seconds. In this situation, either using a larger
number (e.g. 32-bit integer) or increasing the reporting frequency (e.g. every
microsecond, if we can afford the cost) would help.

##### Float

Let's take an example: an [IEEE-754 double precision floating
point](https://en.wikipedia.org/wiki/Double-precision_floating-point_format) is
used to count the number of positrons detected by an alpha magnetic
spectrometer. Each time a positron is detected, the spectrometer will invoke
`counter.Add(1)`, and the result is reported as cumulative sum every 1 second:

* During (T<sub>0</sub>, T<sub>1</sub>], we reported `131,108`.
* During (T<sub>0</sub>, T<sub>2</sub>], we reported `375,463`.
* During (T<sub>0</sub>, T<sub>3</sub>], we reported `832,019`.
* During (T<sub>0</sub>, T<sub>4</sub>], we reported `1,257,308`.
* During (T<sub>0</sub>, T<sub>5</sub>], we reported `1,860,103`.
* ...
* During (T<sub>0</sub>, T<sub>n+1</sub>], we reported `9,007,199,254,325,789`.
* During (T<sub>0</sub>, T<sub>n+2</sub>], we reported `9,007,199,254,740,992`.
* During (T<sub>0</sub>, T<sub>n+3</sub>], we reported `9,007,199,254,740,992`.

In the above case, the counter stopped increasing at some point between
T<sub>n+1</sub> and T<sub>n+2</sub>, because the IEEE-754 double counter is
"saturated", `9,007,199,254,740,992 + 1` will result in `9,007,199,254,740,992`
so the number stopped growing.

Note: in ECMAScript 6 the number `9,007,199,254,740,991` (`2 ^ 53 - 1`) is known
as `Number.MAX_SAFE_INTEGER`, which is the maximum integer that can be exactly
represented as an IEEE-754 double precision number, and whose IEEE-754
representation cannot be the result of rounding any other integer to fit the
IEEE-754 representation.

In addition to the "saturation" issue, we should also understand that IEEE-754
double supports [subnormal
numbers](https://en.wikipedia.org/wiki/Subnormal_number). For example,
`1.0E308 + 1.0E308` would result in `+Inf` (positive infinity). Certain metrics
backend might have trouble handling subnormal numbers.

### Monotonicity property

In the OpenTelemetry Metrics [Data Model](./data-model.md) and [API](./api.md)
specifications, the word `monotonic` has been used frequently.

It is important to understand that different
[Instruments](#instrument-selection) handle monotonicity differently.

Let's take an example with a network driver using a [Counter](./api.md#counter)
to record the total number of bytes received:

* During the time range (T<sub>0</sub>, T<sub>1</sub>]:
  * no network packet has been received
* During the time range (T<sub>1</sub>, T<sub>2</sub>]:
  * received a packet with `30` bytes - `Counter.Add(30)`
  * received a packet with `200` bytes - `Counter.Add(200)`
  * received a packet with `50` bytes - `Counter.Add(50)`
* During the time range (T<sub>2</sub>, T<sub>3</sub>]
  * received a packet with `100` bytes - `Counter.Add(100)`

You can see that the total increment during (T<sub>0</sub>, T<sub>1</sub>] is
`0`, the total increment during (T<sub>1</sub>, T<sub>2</sub>] is `280` (`30 +
200 + 50`), the total increment during (T<sub>2</sub>, T<sub>3</sub>] is `100`,
and the total increment during (T<sub>0</sub>, T<sub>3</sub>] is `380` (`0 +
280 + 100`). All the increments are non-negative, in other words, the **sum is
monotonically increasing**.

Note that it is inaccurate to say "the total bytes received by T<sub>3</sub> is
`380`", because there might be network packets received by the driver before we
started to observe it (e.g. before the last operating system reboot). The
accurate way is to say "the total bytes received during (T<sub>0</sub>,
T<sub>3</sub>] is `380`". In a nutshell, the count represents a **rate** which
is associated with a time range.

This monotonicity property is important because it gives the downstream systems
additional hints so they can handle the data in a better way. Imagine we report
the total number of bytes received in a cumulative sum data stream:

* At T<sub>n</sub>, we reported `3,896,473,820`.
* At T<sub>n+1</sub>, we reported `4,294,967,293`.
* At T<sub>n+2</sub>, we reported `1,800,372`.

The backend system could tell that there was integer overflow or system restart
during (T<sub>n+1</sub>, T<sub>n+2</sub>], so it has chance to "fix" the data.
Refer to [additive property](#additive-property) for more information about
integer overflow.

Let's take another example with a process using an [Asynchronous
Counter](./api.md#asynchronous-counter) to report the total page faults of the
process:

The page faults are managed by the operating system, and the process could
retrieve the number of page faults via some system APIs.

* At T<sub>0</sub>:
  * the process started
  * the process didn't ask the operating system to report the page faults
* At T<sub>1</sub>:
  * the operating system reported with `1000` page faults for the process
* At T<sub>2</sub>:
  * the process didn't ask the operating system to report the page faults
* At T<sub>3</sub>:
  * the operating system reported with `1050` page faults for the process
* At T<sub>4</sub>:
  * the operating system reported with `1200` page faults for the process

You can see that the number being reported is the absolute value rather than
increments, and the value is monotonically increasing.

If we need to calculate "how many page faults have been introduced during
(T<sub>3</sub>, T<sub>4</sub>]", we need to apply subtraction `1200 - 1050 =
150`.

### Semantic convention

Once you decided [which instrument(s) to be used](#instrument-selection), you
will need to decide the names for the instruments and attributes.

It is highly recommended that you align with the `OpenTelemetry Semantic
Conventions`, rather than inventing your own semantics.

## Guidelines for SDK authors

### Aggregation temporality

#### Synchronous example

The OpenTelemetry Metrics [Data Model](./data-model.md) and [SDK](./sdk.md) are
designed to support both Cumulative and Delta
[Temporality](./data-model.md#temporality). It is important to understand that
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

Note that in the following examples, Delta aggregation temporality is
discussed before Cumulative aggregation temporality because
synchronous Counter and UpDownCounter measurements are input to the
API with specified Delta aggregation temporality.

##### Synchronous example: Delta aggregation temporality

Let's imagine we export the metrics as [Histogram](./data-model.md#histogram),
and to simplify the story we will only have one histogram bucket `(-Inf, +Inf)`:

If we export the metrics using **Delta Temporality**:

* (T<sub>0</sub>, T<sub>1</sub>]
  * attributes: {verb = `GET`, status = `200`}, count: `2`, min: `50 (ms)`, max:
    `100 (ms)`
  * attributes: {verb = `GET`, status = `500`}, count: `1`, min: `1 (ms)`, max:
    `1 (ms)`
* (T<sub>1</sub>, T<sub>2</sub>]
  * nothing since we don't have any Measurement received
* (T<sub>2</sub>, T<sub>3</sub>]
  * attributes: {verb = `GET`, status = `500`}, count: `2`, min: `2 (ms)`, max:
    `5 (ms)`
* (T<sub>3</sub>, T<sub>4</sub>]
  * attributes: {verb = `GET`, status = `200`}, count: `1`, min: `100 (ms)`,
    max: `100 (ms)`
* (T<sub>4</sub>, T<sub>5</sub>]
  * attributes: {verb = `GET`, status = `200`}, count: `3`, min: `30 (ms)`, max:
    `100 (ms)`

You can see that the SDK **only needs to track what has happened after the
latest collection/export cycle**. For example, when the SDK started to process
measurements in (T<sub>1</sub>, T<sub>2</sub>], it can completely forget about
what has happened during (T<sub>0</sub>, T<sub>1</sub>].

##### Synchronous example: Cumulative aggregation temporality

If we export the metrics using **Cumulative Temporality**:

* (T<sub>0</sub>, T<sub>1</sub>]
  * attributes: {verb = `GET`, status = `200`}, count: `2`, min: `50 (ms)`, max:
    `100 (ms)`
  * attributes: {verb = `GET`, status = `500`}, count: `1`, min: `1 (ms)`, max:
    `1 (ms)`
* (T<sub>0</sub>, T<sub>2</sub>]
  * attributes: {verb = `GET`, status = `200`}, count: `2`, min: `50 (ms)`, max:
    `100 (ms)`
  * attributes: {verb = `GET`, status = `500`}, count: `1`, min: `1 (ms)`, max:
    `1 (ms)`
* (T<sub>0</sub>, T<sub>3</sub>]
  * attributes: {verb = `GET`, status = `200`}, count: `2`, min: `50 (ms)`, max:
    `100 (ms)`
  * attributes: {verb = `GET`, status = `500`}, count: `3`, min: `1 (ms)`, max:
    `5 (ms)`
* (T<sub>0</sub>, T<sub>4</sub>]
  * attributes: {verb = `GET`, status = `200`}, count: `3`, min: `50 (ms)`, max:
    `100 (ms)`
  * attributes: {verb = `GET`, status = `500`}, count: `3`, min: `1 (ms)`, max:
    `5 (ms)`
* (T<sub>0</sub>, T<sub>5</sub>]
  * attributes: {verb = `GET`, status = `200`}, count: `6`, min: `30 (ms)`, max:
    `100 (ms)`
  * attributes: {verb = `GET`, status = `500`}, count: `3`, min: `1 (ms)`, max:
    `5 (ms)`

You can see that we are performing Delta->Cumulative conversion, and the SDK
**has to track what has happened prior to the latest collection/export cycle**,
in the worst case, the SDK **will have to remember what has happened since the
beginning of the process**.

Imagine if we have a long running service and we collect metrics with 7
attributes and each attribute can have 30 different values. We might eventually
end up having to remember the complete set of all `21,870,000,000` combinations!
This **cardinality explosion** is a well-known challenge in the metrics space.

Making it even worse, if we export the combinations even if there are no recent
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
  Gaps](./data-model.md#resets-and-gaps). For example, if a Cumulative metrics
  stream hasn't received any updates for a long period of time, would it be okay
  to reset the start time?

#### Asynchronous example

In the above case, we have Measurements reported by a [Histogram
Instrument](./api.md#histogram). What if we collect measurements from an
[Asynchronous Counter](./api.md#asynchronous-counter)?

The following example shows the number of [page
faults](https://en.wikipedia.org/wiki/Page_fault) of each process since
it started:

* During the time range (T<sub>0</sub>, T<sub>1</sub>]:
  * pid = `1001`, #PF = `50`
  * pid = `1002`, #PF = `30`
* During the time range (T<sub>1</sub>, T<sub>2</sub>]:
  * pid = `1001`, #PF = `53`
  * pid = `1002`, #PF = `38`
* During the time range (T<sub>2</sub>, T<sub>3</sub>]
  * pid = `1001`, #PF = `56`
  * pid = `1002`, #PF = `42`
* During the time range (T<sub>3</sub>, T<sub>4</sub>]:
  * pid = `1001`, #PF = `60`
  * pid = `1002`, #PF = `47`
* During the time range (T<sub>4</sub>, T<sub>5</sub>]:
  * process 1001 died, process 1003 started
  * pid = `1002`, #PF = `53`
  * pid = `1003`, #PF = `5`
* During the time range (T<sub>5</sub>, T<sub>6</sub>]:
  * A new process 1001 started
  * pid = `1001`, #PF = `10`
  * pid = `1002`, #PF = `57`
  * pid = `1003`, #PF = `8`
  
Note that in the following examples, Cumulative aggregation
temporality is discussed before Delta aggregation temporality because
asynchronous Counter and UpDownCounter measurements are input to the
API with specified Cumulative aggregation temporality.

##### Asynchronous example: Cumulative temporality

If we export the metrics using **Cumulative Temporality**:

* (T<sub>0</sub>, T<sub>1</sub>]
  * attributes: {pid = `1001`}, sum: `50`
  * attributes: {pid = `1002`}, sum: `30`
* (T<sub>0</sub>, T<sub>2</sub>]
  * attributes: {pid = `1001`}, sum: `53`
  * attributes: {pid = `1002`}, sum: `38`
* (T<sub>0</sub>, T<sub>3</sub>]
  * attributes: {pid = `1001`}, sum: `56`
  * attributes: {pid = `1002`}, sum: `42`
* (T<sub>0</sub>, T<sub>4</sub>]
  * attributes: {pid = `1001`}, sum: `60`
  * attributes: {pid = `1002`}, sum: `47`
* (T<sub>0</sub>, T<sub>5</sub>]
  * attributes: {pid = `1002`}, sum: `53`
* (T<sub>4</sub>, T<sub>5</sub>]
  * attributes: {pid = `1003`}, sum: `5`
* (T<sub>5</sub>, T<sub>6</sub>]
  * attributes: {pid = `1001`}, sum: `10`
* (T<sub>0</sub>, T<sub>6</sub>]
  * attributes: {pid = `1002`}, sum: `57`
* (T<sub>4</sub>, T<sub>6</sub>]
  * attributes: {pid = `1003`}, sum: `8`

The behavior in the first four periods is quite straightforward - we
just take the data being reported from the asynchronous instruments
and send them.

The data model prescribes several valid behaviors at T<sub>5</sub> and
T<sub>6</sub> in this case, where one stream dies and another starts.
The [Resets and Gaps](./data-model.md#resets-and-gaps) section describes
how start timestamps and staleness markers can be used to increase the
receiver's understanding of these events.

Consider whether the SDK maintains individual timestamps for the
individual stream, or just one per process.  In this example, where a
process can die and restart, it starts counting page faults from zero.
In this case, the valid behaviors at T<sub>5</sub> and T<sub>6</sub>
are:

1. If all streams in the process share a start time, and the SDK is
   not required to remember all past streams: the thread restarts with
   zero sum, and the start time of the process.  Receivers with reset
   detection are able to calculate a correct rate (except for frequent
   restarts relative to the collection interval), however the precise
   time of a reset will be unknown.
2. If the SDK maintains per-stream start times, it provides the previous
   callback time as the start time, as this time is before the occurrence
   of any events which are measured during the subsequent callback. This
   makes the first observation in a stream more useful for diagnostics,
   as downstream consumers can perform overlap detection or duplicate
   suppression and do not require reset detection in this case.
3. Independent of above treatments, the SDK can add a staleness marker
   to indicate the start of a gap in the stream when one thread dies
   by remembering which streams have previously reported but are not
   currently reporting.  If per-stream start timestamps are used,
   staleness markers can be issued to precisely start a gap in the
   stream and permit forgetting streams that have stopped reporting.

It's OK to ignore the options to use per-stream start timestamps and
staleness markers. The first course of action above requires no
additional memory or code to achieve and is correct in terms of the
data model.

##### Asynchronous example: Delta temporality

If we export the metrics using **Delta Temporality**:

* (T<sub>0</sub>, T<sub>1</sub>]
  * attributes: {pid = `1001`}, delta: `50`
  * attributes: {pid = `1002`}, delta: `30`
* (T<sub>1</sub>, T<sub>2</sub>]
  * attributes: {pid = `1001`}, delta: `3`
  * attributes: {pid = `1002`}, delta: `8`
* (T<sub>2</sub>, T<sub>3</sub>]
  * attributes: {pid = `1001`}, delta: `3`
  * attributes: {pid = `1002`}, delta: `4`
* (T<sub>3</sub>, T<sub>4</sub>]
  * attributes: {pid = `1001`}, delta: `4`
  * attributes: {pid = `1002`}, delta: `5`
* (T<sub>4</sub>, T<sub>5</sub>]
  * attributes: {pid = `1002`}, delta: `6`
  * attributes: {pid = `1003`}, delta: `5`
* (T<sub>5</sub>, T<sub>6</sub>]
  * attributes: {pid = `1001`}, delta: `10`
  * attributes: {pid = `1002`}, delta: `4`
  * attributes: {pid = `1003`}, delta: `3`

You can see that we are performing Cumulative->Delta conversion, and it requires
us to remember the last value of **every single combination we've encountered so
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

* If you have to do Cumulative->Delta conversion, and you encountered min/max,
  rather than drop the data on the floor, you might want to convert them to
  something useful - e.g. [Gauge](./data-model.md#gauge).

##### Asynchronous example: attribute removal in a view

Suppose the metrics in the asynchronous example above are exported
through a view configured to remove the `pid` attribute, leaving a
count of page faults.  For each metric stream, two measurements are produced
covering the same interval of time, which the SDK is expected to aggregate
before producing the output.

The data model specifies to use the "natural merge" function, in this
case meaning to add the current point values together because they
are `Sum` data points.  The expected output is, still in **Cumulative
Temporality**:

* (T<sub>0</sub>, T<sub>1</sub>]
  * dimensions: {}, sum: `80`
* (T<sub>0</sub>, T<sub>2</sub>]
  * dimensions: {}, sum: `91`
* (T<sub>0</sub>, T<sub>3</sub>]
  * dimensions: {}, sum: `98`
* (T<sub>0</sub>, T<sub>4</sub>]
  * dimensions: {}, sum: `107`
* (T<sub>0</sub>, T<sub>5</sub>]
  * dimensions: {}, sum: `58`
* (T<sub>0</sub>, T<sub>6</sub>]
  * dimensions: {}, sum: `75`

As discussed in the asynchronous cumulative temporality example above,
there are various treatments available for detecting resets.  Even if
the first course is taken, which means doing nothing, a receiver that
follows the data model's rules for [unknown start
time](data-model.md#cumulative-streams-handling-unknown-start-time) and
[inserting true start
times](data-model.md#cumulative-streams-inserting-true-reset-points)
will calculate a correct rate in this case.  The "58" received at
T<sub>5</sub> resets the stream - the change from "107" to "58" will
register as a gap and rate calculations will resume correctly at
T<sub>6</sub>.  The rules for reset handling are provided so that the
unknown portion of "58" that was counted reflected in the "107" at
T<sub>4</sub> is not double-counted at T<sub>5</sub> in the reset.

If the option to use per-stream start timestamps is taken above, it
lightens the duties of the receiver, making it possible to monitor
gaps precisely and detect overlapping streams.  When per-stream state
is available, the SDK has several approaches for calculating Views
available in the presence of attributes that stop reporting and then
reset some time later:

1. By remembering the cumulative value for all streams across the
   lifetime of the process, the cumulative sum will be correct despite
   `attributes` that come and go.  The SDK has to detect per-stream resets
   itself in this case, otherwise the View will be calculated incorrectly.
2. When the cost of remembering all streams `attributes` becomes too
   high, reset the View and all its state, give it a new start
   timestamp, and let the caller see a gap in the stream.

When considering this matter, note also that the metrics API has a
recommendation for each asynchronous instrument: [User code is
recommended not to provide more than one `Measurement` with the same
`attributes` in a single callback.](api.md#instrument).  Consider
whether the impact of user error in this regard will impact the
correctness of the view.  When maintaining per-stream state for the
purpose of View correctness, SDK authors may want to consider
detecting when the user makes duplicate measurements.  Without
checking for duplicate measurements, Views may be calculated
incorrectly.

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
done via some cardinality-capping algorithm - e.g. start to combine/drop some data
points when the SDK hits the memory limit, and provide a mechanism to report the
data loss.

**Provide configurations to the application owner.** The answer to _"what is an
efficient memory usage"_ is ultimately depending on the goal of the application
owner. For example, the application owners might want to spend more memory in
order to keep more combinations of metrics attributes, or they might want to use
memory aggressively for certain attributes that are important, and keep a
conservative limit for attributes that are less important.
