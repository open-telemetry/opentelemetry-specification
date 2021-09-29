# Metrics Data Model

**Status**: [Mixed](../document-status.md)

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->
<!-- Note: `Events → Data Stream → Timeseries` breaks markdown-toc -->

<!-- toc -->

- [Overview](#overview)
- [Events → Data Stream → Timeseries](#events--data-stream--timeseries)
  * [Example Use-cases](#example-use-cases)
  * [Out of Scope Use-cases](#out-of-scope-use-cases)
- [Model Details](#model-details)
  * [Event Model](#event-model)
  * [Timeseries Model](#timeseries-model)
  * [OpenTelemetry Protocol data model](#opentelemetry-protocol-data-model)
- [Metric points](#metric-points)
  * [Sums](#sums)
  * [Gauge](#gauge)
  * [Histogram](#histogram)
  * [Summary (Legacy)](#summary-legacy)
- [Exemplars](#exemplars)
- [Single-Writer](#single-writer)
- [Temporality](#temporality)
- [Resets and Gaps](#resets-and-gaps)
  * [Cumulative streams: handling unknown start time](#cumulative-streams-handling-unknown-start-time)
  * [Cumulative streams: inserting true reset points](#cumulative-streams-inserting-true-reset-points)
- [Overlap](#overlap)
  * [Overlap resolution](#overlap-resolution)
  * [Overlap observability](#overlap-observability)
  * [Overlap interpolation](#overlap-interpolation)
- [Stream Manipulations](#stream-manipulations)
  * [Sums: Delta-to-Cumulative](#sums-delta-to-cumulative)
    + [Sums: detecting alignment issues](#sums-detecting-alignment-issues)
    + [Sums: Missing Timestamps](#sums-missing-timestamps)
- [Footnotes](#footnotes)

<!-- tocstop -->

## Overview

**Status**: [Stable](../document-status.md)

The OpenTelemetry data model for metrics consists of a protocol specification
and semantic conventions for delivery of pre-aggregated metric timeseries data.
The data model is designed for importing data from existing systems and
exporting data into existing systems, as well as to support internal
OpenTelemetry use-cases for generating Metrics from streams of Spans or Logs.

Popular existing metrics data formats can be unambiguously translated into the
OpenTelemetry data model for metrics, without loss of semantics or fidelity.
Translation from the Prometheus and Statsd exposition formats is explicitly
specified.

The data model specifies a number of semantics-preserving data transformations
for use on the collection path, supporting flexible system configuration. The
model supports reliability and statelessness controls, through the choice of
cumulative and delta transport. The model supports cost controls, through
spatial and temporal reaggregation.

The OpenTelemetry collector is designed to accept metrics data in a number of
formats, transport data using the OpenTelemetry data model, and then export into
existing systems. The data model can be unambiguously translated into the
Prometheus Remote Write protocol without loss of features or semantics, through
well-defined translations of the data, including the ability to automatically
remove attributes and lower histogram resolution.

## Events → Data Stream → Timeseries

**Status**: [Stable](../document-status.md)

The OTLP Metrics protocol is designed as a standard for transporting metric
data. To describe the intended use of this data and the associated semantic
meaning, OpenTelemetry metric data stream types will be linked into a framework
containing a higher-level model, about Metrics APIs and discrete input values,
and a lower-level model, defining the Timeseries and discrete output values.
The relationship between models is displayed in the diagram below.

![Events → Data Stream → Timeseries Diagram](img/model-layers.png)

This protocol was designed to meet the requirements of the OpenCensus Metrics
system, particularly to meet its concept of Metrics Views. Views are
accomplished in the OpenTelemetry Metrics data model through support for data
transformation on the collection path.

OpenTelemetry has identified three kinds of semantics-preserving Metric data
transformation that are useful in building metrics collection systems as ways of
controlling cost, reliability, and resource allocation. The OpenTelemetry
Metrics data model is designed to support these transformations both inside an
SDK as the data originates, or as a reprocessing stage inside the OpenTelemetry
collector. These transformations are:

1. Temporal reaggregation: Metrics that are collected at a high-frequency can be
   re-aggregated into longer intervals, allowing low-resolution timeseries to be
   pre-calculated or used in place of the original metric data.
2. Spatial reaggregation: Metrics that are produced with unwanted dimensions can
   be re-aggregated into metrics having fewer dimensions.
3. Delta-to-Cumulative: Metrics that are input and output with Delta temporality
   unburden the client from keeping high-cardinality state. The use of deltas
   allows downstream services to bear the cost of conversion into cumulative
   timeseries, or to forego the cost and calculate rates directly.

OpenTelemetry Metrics data streams are designed so that these transformations
can be applied automatically to streams of the same type, subject to conditions
outlined below. Every OTLP data stream has an intrinsic
[decomposable aggregate function](https://en.wikipedia.org/wiki/Aggregate_function#Decomposable_aggregate_functions)
making it semantically well-defined to merge data points across both temporal
and spatial dimensions. Every OTLP data point also has two meaningful timestamps
which, combined with intrinsic aggregation, make it possible to carry out the
standard metric data transformations for each of the model’s basic points while
ensuring that the result carries the intended meaning.

As in OpenCensus Metrics, metrics data can be transformed into one or more
Views, just by selecting the aggregation interval and the desired dimensions.
One stream of OTLP data can be transformed into multiple timeseries outputs by
configuring different Views, and the required Views processing may be applied
inside the SDK or by an external collector.

### Example Use-cases

The metric data model is designed around a series of "core" use cases.  While
this list is not exhaustive, it is meant to be representative of the scope and
breadth of OTel metrics usage.

1. OTel SDK exports 10 second resolution to a single OTel collector, using
  cumulative temporality for a stateful client, stateless server:
    - Collector passes-through original data to an OTLP destination
    - Collector re-aggregates into longer intervals without changing dimensions
    - Collector re-aggregates into several distinct views, each with a subset of
      the available dimensions, outputs to the same destination
2. OTel SDK exports 10 second resolution to a single OTel collector, using delta
  temporality for a stateless client, stateful server:
    - Collector re-aggregates into 60 second resolution
    - Collector converts delta to cumulative temporality
3. OTel SDK exports both 10 seconds resolution (e.g. CPU, request latency) and
  15 minutes resolution (e.g. room temperature) to a single OTel Collector.
  The collector exports streams upstream with or without aggregation.
4. A number of OTel SDKs running locally each exports 10 second resolution, each
  reports to a single (local) OTel collector.
    - Collector re-aggregates into 60 second resolution
    - Collector re-aggregates to eliminate the identity of individual SDKs (e.g.,
      distinct `service.instance.id` values)
    - Collector outputs to an OTLP destination
5. Pool of OTel collectors receive OTLP and export Prometheus Remote Write
    - Collector joins service discovery with metric resources
    - Collector computes “up”, staleness marker
    - Collector applies a distinct external label
6. OTel collector receives Statsd and exports OTLP
    - With delta temporality: stateless collector
    - With cumulative temporality: stateful collector
7. OTel SDK exports directly to 3P backend

These are considered the "core" use-cases used to analyze tradeoffs and design
decisions within the metrics data model.

### Out of Scope Use-cases

The metrics data model is NOT designed to be a perfect rosetta stone of metrics.
Here are a set of use cases that, while won't be outright unsupported, are not
in scope for key design decisions:

- Using OTLP as an intermediary format between two non-compatible formats
  - Importing [statsd](https://github.com/statsd/statsd) => Prometheus PRW
  - Importing [collectd](https://collectd.org/wiki/index.php/Binary_protocol#:~:text=The%20binary%20protocol%20is%20the,some%20documentation%20to%20reimplement%20it)
    => Prometheus PRW
  - Importing Prometheus endpoint scrape => [statsd push | collectd | opencensus]
  - Importing OpenCensus "oca" => any non OC or OTel format
- TODO: define others.

## Model Details

**Status**: [Stable](../document-status.md)

OpenTelemetry fragments metrics into three interacting models:

- An Event model, representing how instrumentation reports metric data.
- A Timeseries model, representing how backends store metric data.
- A Metric Stream model, defining the *O*pen*T*e*L*emetry *P*rotocol (OTLP)
  representing how metric data streams are manipulated and transmitted between
  the Event model and the Timeseries storage.  This is the model specified
  in this document.

### Event Model

The event model is where recording of data happens. Its foundation is made of
[Instruments](api.md#instrument), which are used to record data observations via events.
These raw events are then transformed in some fashion before being sent to some
other system.  OpenTelemetry metrics are designed such that the same instrument
and events can be used in different ways to generate metric streams.

![Events → Streams](img/model-event-layer.png)

Even though observation events could be reported directly to a backend, in
practice this would be infeasible due to the sheer volume of data used in
observability systems, and the limited amount of network/CPU resources available
for telemetry collection purposes. The best example of this is the Histogram
metric where raw events are recorded in a compressed format rather than
individual timeseries.

> Note: The above picture shows how one instrument can transform events into
> more than one type of metric stream. There are caveats and nuances for when
> and how to do this.  Instrument and metric configuration are outlined
> in the [metrics API specification](api.md).

While OpenTelemetry provides flexibility in how instruments can be transformed
into metric streams, the instruments are defined such that a reasonable default
mapping can be provided. The exact
[OpenTelemetry instruments](api.md##instrument) are detailed in the API
specification.

In the Event model, the primary data are (instrument, number) points, originally
observed in real time or on demand (for the synchronous and asynchronous cases,
respectively).

### Timeseries Model

In this low-level metrics data model, a Timeseries is defined by an entity
consisting of several metadata properties:

- Metric name
- Attributes (dimensions)
- Kind of point (integer, floating point, etc)
- Unit of measurement

The primary data of each timeseries are ordered (timestamp, value) points, for
three value types:

1. Counter (Monotonic, Cumulative)
2. Gauge
3. Histogram

This model may be viewed as an idealization of
[Prometheus Remote Write](https://docs.google.com/document/d/1LPhVRSFkGNSuU1fBd81ulhsCPR4hkSZyyBj1SZ8fWOM/edit#heading=h.3p42p5s8n0ui).
Like that protocol, we are additionally concerned with knowing when a point
value is defined, as compared with being implicitly or explicitly absent. A
metric stream of delta data points defines time-interval values, not
point-in-time values.  To precisely define presence and absence of data requires
further development of the correspondence between these models.

Note: Prometheus is not the only possible timeseries model for OpenTelemetry
to map into, but is used as a reference throughout this document.

### OpenTelemetry Protocol data model

The OpenTelmetry protocol data model is composed of Metric data streams. These
streams are in turn composed of metric data points. Metric data streams
can be converted directly into Timeseries, and share the same identity
characteristics for a Timeseries. A metric stream is identified by:

- The originating `Resource`
- The metric stream's `name`.
- The attached `Attribute`s
- The metric stream's point kind.

It is possible (and likely) that more than one metric stream is created per
`Instrument` in the event model.

__Note: The same `Resource`, `name` and `Attribute`s but differing point kind
coming out of an OpenTelemetry SDK is considered an "error state" that SHOULD
be handled by an SDK.__

A metric stream can use one of three basic point kinds, all of
which satisfy the requirements above, meaning they define a decomposable
aggregate function (also known as a “natural merge” function) for points of the
same kind. <sup>[1](#otlpdatapointfn)</sup>

The basic point kinds are:

1. [Sum](https://github.com/open-telemetry/opentelemetry-proto/blob/v0.9.0/opentelemetry/proto/metrics/v1/metrics.proto#L230)
2. [Gauge](https://github.com/open-telemetry/opentelemetry-proto/blob/v0.9.0/opentelemetry/proto/metrics/v1/metrics.proto#L200)
3. [Histogram](https://github.com/open-telemetry/opentelemetry-proto/blob/v0.9.0/opentelemetry/proto/metrics/v1/metrics.proto#L258)

Comparing the OTLP Metric Data Stream and Timeseries data models, OTLP does
not map 1:1 from its point types into timeseries points. In OTLP, a Sum point
can represent a monotonic count or a non-monotonic count. This means an OTLP Sum
is either translated into a Timeseries Counter, when the sum is monotonic, or
a Gauge when the sum is not monotonic.

![Stream → Timeseries](img/model-layers-stream.png)

Specifically, in OpenTelemetry Sums always have an aggregate function where
you can combine via addition. So, for non-monotonic sums in OpenTelemetry we
can aggregate (naturally) via addition.  In the timeseries model, you cannot
assume that any particular Gauge is a sum, so the default aggregation would not
be addition.

In addition to the core point kinds used in OTLP, there are also data types
designed for compatibility with existing metric formats.

- [Summary](#summary-legacy)

## Metric points

**Status**: [Stable](../document-status.md)

### Sums

[Sum](https://github.com/open-telemetry/opentelemetry-proto/blob/v0.9.0/opentelemetry/proto/metrics/v1/metrics.proto#L230)s
in OTLP consist of the following:

- An *Aggregation Temporality* of delta or cumulative.
- A flag denoting whether the Sum is
  [monotonic](https://en.wikipedia.org/wiki/Monotonic_function). In this case of
  metrics, this means the sum is nominally increasing, which we assume without
  loss of generality.
  - For delta monotonic sums, this means the reader SHOULD expect non-negative
    values.
  - For cumulative monotonic sums, this means the reader SHOULD expect values
    that are not less than the previous value.
- A set of data points, each containing:
  - An independent set of Attribute name-value pairs.
  - A time window (of `(start, end]`) time for which the Sum was calculated.
    - The time interval is inclusive of the end time.
    - Times are specified in Value is UNIX Epoch time in nanoseconds since
      `00:00:00 UTC on 1 January 1970`
    - (optional) a set of examplars (see [Exemplars](#exemplars)).

The aggregation temporality is used to understand the context in which the sum
was calculated. When the aggregation temporality is "delta", we expect to have
no overlap in time windows for metric streams, e.g.

![Delta Sum](img/model-delta-sum.png)

Contrast with cumulative aggregation temporality where we expect to report the
full sum since 'start' (where usually start means a process/application start):

![Cumulative Sum](img/model-cumulative-sum.png)

There are various tradeoffs between using Delta vs. Cumulative aggregation, in
various use cases, e.g.:

- Detecting process restarts
- Calculating rates
- Push vs. Pull based metric reporting

OTLP supports both models, and allows APIs, SDKs and users to determine the
best tradeoff for their use case.

### Gauge

A [Gauge](https://github.com/open-telemetry/opentelemetry-proto/blob/v0.9.0/opentelemetry/proto/metrics/v1/metrics.proto#L200)
in OTLP represents a sampled value at a given time.  A Gauge stream consists of:

- A set of data points, each containing:
  - An independent set of Attribute name-value pairs.
  - A sampled value (e.g. current cpu temperature)
  - A timestamp when the value was sampled (`time_unix_nano`)
  - (optional) A timestamp (`start_time_unix_nano`) which has [TBD semantics](https://github.com/open-telemetry/opentelemetry-proto/pull/295).
  - (optional) a set of examplars (see [Exemplars](#exemplars)).

In OTLP, a point within a Gauge stream represents the last-sampled event for a
given time window.

![Gauge](img/model-gauge.png)

In this example, we can see an underlying timeseries we are sampling with our
Gauge.  While the event model *can* sample more than once for a given metric
reporting interval, only the last value is reported in the metric stream via
OTLP.

Gauges do not provide an aggregation semantic, instead "last sample value" is
used when performing operations like temporal alignment or adjusting resolution.

Gauges can be aggregated through transformation into histograms, or other
metric types. These operations are not done by default, and require direct
user configuration.

### Histogram

[Histogram](https://github.com/open-telemetry/opentelemetry-proto/blob/v0.9.0/opentelemetry/proto/metrics/v1/metrics.proto#L258)
metric data points convey a population of recorded measurements in a compressed
format. A histogram bundles a set of events into divided populations with an
overall event count and aggregate sum for all events.

![Delta Histogram](img/model-delta-histogram.png)

Histograms consist of the following:

- An *Aggregation Temporality* of delta or cumulative.
- A set of data points, each containing:
  - An independent set of Attribute name-value pairs.
  - A time window (of `(start, end]`) time for which the Histogram was bundled.
    - The time interval is inclusive of the end time.
    - Time values are specified as nanoseconds since the UNIX Epoch
      (00:00:00 UTC on 1 January 1970).
  - A count (`count`) of the total population of points in the histogram.
  - A sum (`sum`) of all the values in the histogram.
  - (optional) A series of buckets with:
    - Explicit boundary values.  These values denote the lower and upper bounds
      for buckets and whether not a given observation would be recorded in this
      bucket.
    - A count of the number of observations that fell within this bucket.
  - (optional) a set of examplars (see [Exemplars](#exemplars)).

Like Sums, Histograms also define an aggregation temporality.  The picture above
denotes Delta temporality where accumulated event counts are reset to zero after reporting
and a new aggregation occurs. Cumulative, on the other hand, continues to
aggregate events, resetting with the use of a new start time.

Bucket counts are optional.  A Histogram without buckets conveys a
population in terms of only the sum and count, and may be interpreted
as a histogram with single bucket covering `(-Inf, +Inf)`.

Bucket upper-bounds are inclusive (except for the case where the
upper-bound is +Inf) while bucket lower-bounds are exclusive. That is,
buckets express the number of values that are greater than their lower
bound and less than or equal to their upper bound.  Importers and
exporters working with OpenTelemetry Metrics data are meant to
disregard this specification when translating to and from histogram
formats that use inclusive lower bounds and exclusive upper bounds.
Changing the inclusivity and exclusivity of bounds is an example of
worst-case Histogram error; users should choose Histogram boundaries
so that worst-case error is within their error tolerance.

### Summary (Legacy)

[Summary](https://github.com/open-telemetry/opentelemetry-proto/blob/v0.9.0/opentelemetry/proto/metrics/v1/metrics.proto#L268)
metric data points convey quantile summaries, e.g. What is the 99-th percentile
latency of my HTTP server.  Unlike other point types in OpenTelemetry, Summary
points cannot always be merged in a meaningful way. This point type is not
recommended for new applications and exists for compatibility with other
formats.

## Exemplars

**Status**: [Stable](../document-status.md)

An exemplar is a recorded value that associates OpenTelemetry context to
a metric event within a Metric. One use case is to allow users to link
Trace signals w/ Metrics.

Exemplars consist of:

- (optional) The trace associated with a recording (`trace_id`, `span_id`)
- The time of the observation (`time_unix_nano`)
- The recorded value (`value`)
- A set of filtered attributes (`filtered_attributes`) which provide
  additional insight into the Context when the observation was made.

For Histograms, when an exemplar exists, its value already participates
in `bucket_counts`, `count` and `sum` reported by the histogram point.

For Sums, when an exemplar exists, its value is already included in the overall
sum.

For Gauges, when an exemplar exists, its value was seen at some point within
the gauge interval for the same source.

## Single-Writer

**Status**: [Stable](../document-status.md)

All metric data streams within OTLP MUST have one logical writer.  This means,
conceptually, that any Timeseries created from the Protocol MUST have one
originating source of truth.  In practical terms, this implies the following:

- All metric data streams produced by OTel SDKs MUST be globally uniquely
  produced and free from duplicates.   All metric data streams can be uniquely
  identified in some way.
- Aggregations of metric streams MUST only be written from a single logical
  source.
  __Note: This implies aggregated metric streams must reach one destination__.

In systems, there is the possibility of multiple writers sending data for the
same metric stream (duplication).  For example, if an SDK implementation fails
to find uniquely identifying Resource attributes for a component, then all
instances of that component could be reporting metrics as if they are from the
same resource.  In this case, metrics will be reported at inconsistent time
intervals.  For metrics like cumulative sums, this could cause issues where
pairs of points appear to reset the cumulative sum leading to unusable metrics.

Multiple writers for a metric stream is considered an error state, or
misbehaving system. Receivers SHOULD presume a single writer was intended and
eliminate overlap / deduplicate.

Note: Identity is an important concept in most metrics systems.  For example,
[Prometheus directly calls out uniqueness](https://prometheus.io/docs/prometheus/latest/configuration/configuration/#metric_relabel_configs):

> Take care with `labeldrop` and `labelkeep` to ensure that metrics
> are still uniquely labeled once the labels are removed.

For OTLP, the Single-Writer principle grants a way to reason over error
scenarios and take corrective actions.  Additionally, it ensures that
well-behaved systems can perform metric stream manipulation without undesired
degradation or loss of visibility.

## Temporality

**Status**: [Stable](../document-status.md)

The notion of temporality refers to the way additive quantities are
expressed, in relation to time, indicating whether reported values
incorporate previous measurements or not.  Sum and Histogram data
points, in particular, support a choice of aggregation temporality.

Every OTLP metric data point has two associated timestamps.  The
first, mandatory timestamp is the one associated with the observation,
the moment when the measurement became current or took effect, and is
referred to as `TimeUnixNano`.  The second, optional timestamp is used
to indicate when a sequence of points is unbroken, and is referred to as
`StartTimeUnixNano`.

The second timestamp is strongly recommended for Sum, Histogram, and
Summary points, as it is necessary to correctly interpret the rate
from an OTLP stream, in a manner that is aware of restarts.  The use
of `StartTimeUnixNano` to indicate the start of an unbroken sequence
of points means it can also be used to encode implicit gaps in
the stream.

- *Cumulative temporality* means that successive data points repeat the starting
  timestamp. For example, from start time T0, cumulative data points cover time
  ranges (T<sub>0</sub>, T<sub>1</sub>), (T<sub>0</sub>, T<sub>2</sub>),
  (T<sub>0</sub>, T<sub>3</sub>), and so on.
- *Delta temporality* means that successive data points advance the starting
  timestamp. For example, from start time T0, delta data points cover time
  ranges (T<sub>0</sub>, T<sub>1</sub>), (T<sub>1</sub>, T<sub>2</sub>),
  (T<sub>2</sub>, T<sub>3</sub>), and so on.

The use of cumulative temporality for monotonic sums is common, exemplified by
Prometheus. Systems based in cumulative monotonic sums are naturally simpler, in
terms of the cost of adding reliability. When collection fails intermittently,
gaps in the data are naturally averaged from cumulative measurements.
Cumulative data requires the sender to remember all previous measurements, an
“up-front” memory cost proportional to cardinality.

The use of delta temporality for metric sums is also common, exemplified by
Statsd. There is a connection between OpenTelemetry tracing, in which a Span
event commonly is translated into two metric events (a 1-count and a timing
measurement). Delta temporality enables sampling and supports shifting the cost
of cardinality outside of the process.

## Resets and Gaps

**Status**: [Experimental](../document-status.md)

When the `StartTimeUnixNano` field is present, it allows the consumer
to observe when there are gaps and overlapping writers in a stream.
Correctly used, the consumer can observe both transient and ongoing
violations of the single-writer principle as well as reset events.  In
an unbroken sequence of observations, the `StartTimeUnixNano` always
matches either the `TimeUnixNano` or the `StartTimeUnixNano` of other
points in the same sequence.  For the initial points in an unbroken
sequence:

- When `StartTimeUnixNano` is less than `TimeUnixNano`, a new unbroken sequence
  of observations begins with a "true" reset at a known start time. The zero
  value is implicit, it is not necessary to record the starting point.
- When `StartTimeUnixNano` equals `TimeUnixNano`, a new unbroken sequence of
  observations begins with a reset at an unknown start time. The initial
  observed value is recorded to indicate that an unbroken sequence of
  observations resumes. These points have zero duration, and indicate that
  nothing is known about previously-reported points and that data may have been
  lost.

For subsequent points in an unbroken sequence:

- For points with delta aggregation temporality, the `StartTimeUnixNano` of
  each point matches the `TimeUnixNano` of the preceding point
- Otherwise, the `StartTimeUnixNano` of each point matches the
  `StartTimeUnixNano` of the initial observation.

A metric stream has a gap, where it is implicitly undefined, anywhere
there is a range of time such that no point covers that range range
with its `StartTimeUnixNano` and `TimeUnixNano` fields.

### Cumulative streams: handling unknown start time

An unbroken stream of observations is resumed with a zero-duration
point and non-zero value, as described above.  For points with
cumulative aggregation temporality, the rate contributed to the
timeseries by each point depends on the prior point value in the
stream.

To correctly compute the rate contribution of the first point in a
unbroken sequence requires knowing whether it is the first point.
Unknown start-time reset points appear with `TimeUnixNano` equal to
the `StartTimeUnixNano` of a stream of points, in which case the rate
contribution of the first point is considered zero.  An earlier
sequence of observations is expected to have reported the same
cumulative state prior to a gap in observations.

The presence or absence of a point with `TimeUnixNano` equal to the
`StartTimeUnixNano` indicates how to count rate contribution from the
first point in a sequence.  If the first point in an unknown
start-time reset sequence is lost, the consumer of this data might
overcount the rate contribution of the second point, as it then appears
like a "true" reset.

Various approaches can be taken to avoid overcounting.  A system could
use state from earlier in the stream to resolve start-time ambiguity,
for example.

### Cumulative streams: inserting true reset points

The absolute value of the cumulative counter is often considered
meaningful, but when the cumulative value is only used to calculate a
rate function, it is possible to drop the initial unknown start-time
reset point, but remember the initially observed value in order to
modify subsequent observations.  Later in the cumulative sequence are
output relative to the initial value, thus appears as a true reset
offset by an unknown constant.

This process is known as inserting true reset points, a special case
of reaggregation for cumulative series.

## Overlap

**Status**: [Experimental](../document-status.md)

Overlap occurs when more than one metric data point is defined for a
metric stream within a time window.  Overlap is usually caused through
mis-configuration, and it can lead to serious mis-interpretation of
the data.  `StartTimeUnixNano` is recommended so that consumers can
recognize and response to overlapping points.

We define three principles for handling overlap:

- Resolution (correction via dropping points)
- Observability (allowing the data to flow to backends)
- Interpolation (correction via data manipulation)

### Overlap resolution

When more than one process writes the same metric data stream, OTLP data points
may appear to overlap. This condition typically results from misconfiguration, but
can also result from running identical processes (indicative of operating system
or SDK bugs, like missing
[process attributes](../resource/semantic_conventions/process.md)). When there
are overlapping points, receivers SHOULD eliminate points so that there are no
overlaps. Which data to select in overlapping cases is not specified.

### Overlap observability

OpenTelemetry collectors SHOULD export telemetry when they observe overlapping
points in data streams, so that the user can monitor for erroneous
configurations.

### Overlap interpolation

When one process starts just as another exits, the appearance of overlapping
points may be expected. In this case, OpenTelemetry collectors SHOULD modify
points at the change-over using interpolation for Sum data points, to reduce
gaps to zero width in these cases, without any overlap.

## Stream Manipulations

**Status**: [Experimental](../document-status.md)

Pending introduction.

### Sums: Delta-to-Cumulative

While OpenTelemetry (and some metric backends) allows both Delta and Cumulative
sums to be reported, the timeseries model we target does not support delta
counters.  To this end, converting from delta to cumulative needs to be defined
so that backends can use this mechanism.

> Note: This is not the only possible Delta to Cumulative algorithm.  It is
> just one possible implementation that fits the OTel Data Model.

Converting from delta points to cumulative point is inherently a stateful
operation.  To successfully translate, we need all incoming delta points to
reach one destination which can keep the current counter state and generate
a new cumulative stream of data (see [single writer principle](#single-writer)).

The algorithm is scheduled out as follows:

- Upon receiving the first Delta point for a given counter we set up the
  following:
  - A new counter which stores the cumulative sum, set to the initial counter.
  - A start time that aligns with the start time of the first point.
  - A "last seen" time that aligns with the time of the first point.
- Upon receiving future Delta points, we do the following:
  - If the next point aligns with the expected next-time window
    (see [detecting delta restarts](#sums-detecting-alignment-issues))
    - Update the "last seen" time to align with the time of the current point.
    - Add the current value to the cumulative counter
    - Output a new cumulative point with the original start time and current
      last seen time and count.
  - if the current point precedes the start time, then drop this point.
    Note: there are algorithms which can deal with late arriving points.
  - if the next point does NOT align with the expected next-time window, then
    reset the counter following the same steps performed as if the current point
    was the first point seen.

#### Sums: detecting alignment issues

When the next delta sum reported for a given metric stream does not align with
where we expect it, one of several things could have occurred:

- the process reporting metrics was rebooted, leading to a new reporting
  interval for the metric.
- A Single-Writer principle violation where multiple processes are reporting the
  same metric stream.
- There was a lost data point, or dropped information.

In all of these scenarios we do our best to give any cumulative metric knowledge
that some data was lost, and reset the counter.

We detect alignment via two mechanisms:

- If the incoming delta time interval has significant overlap with the previous
  time interval, we assume a violation of the single-writer principle.
- If the incoming delta time interval has a significant gap from the last seen
  time, we assume some kind of reboot/restart and reset the cumulative counter.

#### Sums: Missing Timestamps

One degenerate case for the delta-to-cumulative algorithm is when timestamps
are missing from metric data points. While this shouldn't be the case when
using OpenTelemetry generated metrics, it can occur when adapting other metric
formats, e.g.
[StatsD counts](https://github.com/statsd/statsd/blob/master/docs/metric_types.md#counting).

In this scenario, the algorithm listed above would reset the cumulative sum on
every data point due to not being able to determine alignment or point overlap.
For comparison, see the simple logic used in
[statsd sums](https://github.com/statsd/statsd/blob/master/stats.js#L281)
where all points are added, and lost points are ignored.

## Footnotes

<a name="otlpdatapointfn">[1]</a>: OTLP supports data point kinds that do not
satisfy these conditions; they are well-defined but do not support standard
metric data transformations.
