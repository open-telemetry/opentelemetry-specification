# Metrics Data Model

**Status**: [Experimental](../document-status.md)

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

<!-- tocstop -->

## Overview

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

## Events → Data → Timeseries

The OTLP Metrics protocol is designed as a standard for transporting metric
data. To describe the intended use of this data and the associated semantic
meaning, OpenTelemetry metric data types will be linked into a framework
containing a higher-level model, about Metrics APIs and discrete input values,
and a lower-level model, defining the Timeseries and discrete output values.
The relationship between models is displayed in the diagram below.

![Events  → Data → Timeseries Diagram](img/model-layers.png)

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

OpenTelemetry Metrics data points are designed so that these transformations can
be applied automatically to points of the same type, subject to conditions
outlined below. Every OTLP data point has an intrinsic
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

OpenTelemetry fragments metrics into three interacting models:

- An Event model, representing how instrumentation reports metric data.
- A TimeSeries model, representing how backends store metric data.
- The *O*pen*T*e*L*emetry *P*rotocol (OTLP) data model representing how metrics
  are manipulated and transmitted between the Event model and the TimeSeries
  storage.

### Event Model

This specification uses as its foundation a
[Metrics API consisting of 6 model instruments](api.md), each having distinct
semantics, that were prototyped in several OpenTelemetry SDKs between July 2019
and June 2020. The model instruments and their specific use-cases are meant to
anchor our understanding of the OpenTelemetry data model and are divided into
three categories:

- Synchronous vs. Asynchronous. The act of calling a Metrics API in a
  synchronous context means the application/library calls the SDK, typically having
  associated trace context and baggage; an Asynchronous instrument is called at
  collection time, through a callback, and lacks context.
- Adding vs. Grouping. Whereas adding instruments express a sum, grouping
  instruments characterize a group of measurements. The numbers passed to adding
  instruments define division, in the algebraic sense, while the numbers passed
  to grouping instruments are generally not. Adding instrument values are always
  parts of a sum, while grouping instrument values are individual measurements.
- Monotonic vs. Non-Monotonic. The adding instruments are categorized by whether
  the derivative of the quantity they express is non-negative. Monotonic
  instruments are primarily useful for monitoring a rate value, whereas
  non-monotonic instruments are primarily useful for monitoring a total value.

In the Event model, the primary data are (instrument, number) points, originally
observed in real time or on demand (for the synchronous and asynchronous cases,
respectively). The instruments and model use-cases will be described in greater
detail as we link the event model with the other two.

### Timeseries Model

In this low-level metrics data model, a Timeseries is defined by an entity
consisting of several metadata properties:

- Metric name and description
- Label set
- Kind of point (integer, floating point, etc)
- Unit of measurement

The primary data of each timeseries are ordered (timestamp, value) points, for
three value types:

1. Counter (Monotonic, cumulative)
2. Gauge
3. Histogram

This model may be viewed as an idealization of
[Prometheus Remote Write](https://docs.google.com/document/d/1LPhVRSFkGNSuU1fBd81ulhsCPR4hkSZyyBj1SZ8fWOM/edit#heading=h.3p42p5s8n0ui).
Like that protocol, we are additionally concerned with knowing when a point
value is defined, as compared with being implicitly or explicitly absent. A
metric stream of delta data points defines time-interval values, not
point-in-time values.  To precisely define presence and absence of data requires
further development of the correspondence between these models.

### OpenTelemetry Protocol data model

The OpenTelemetry data model for metrics includes four basic point kinds, all of
which satisfy the requirements above, meaning they define a decomposable
aggregate function (also known as a “natural merge” function) for points of the
same kind. <sup>[1](#otlpdatapointfn)</sup>

The basic point kinds are:

1. Monotonic Sum
2. Non-Monotonic Sum
3. Gauge
4. Histogram

Comparing the OpenTelemetry and Timeseries data models, OTLP carries an
additional kind of point. Whereas an OTLP Monotonic Sum point translates into a
Timeseries Counter point, and an OTLP Histogram point translates into a
Timeseries Histogram point, there are two OTLP data points that become Gauges
in the Timeseries model: the OTLP Non-Monotonic Sum point and OTLP Gauge point.

The two points that become Gauges in the Timeseries model are distinguished by
their built in aggregate function, meaning they define re-aggregation
differently. Sum points combine using addition, while Gauge points combine into
histograms.

## Single-Writer

Pending

## Temporarily

Pending

## Resources

Pending

## Temporal Alignment

Pending

## External Labels

Pending

## Footnotes

<a name="otlpdatapointfn">[1]</a>: OTLP supports data point kinds that do not
satisfy these conditions; they are well-defined but do not support standard
metric data transformations.
