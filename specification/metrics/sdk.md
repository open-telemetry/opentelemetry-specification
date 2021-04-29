# Metrics SDK

**Status**: [Experimental](../document-status.md)

**Owner:**

* [Reiley Yang](https://github.com/reyang)

**Domain Experts:**

* [Bogdan Brutu](https://github.com/bogdandrutu)
* [Josh Suereth](https://github.com/jsuereth)
* [Joshua MacDonald](https://github.com/jmacd)

Note: this specification is subject to major changes. To avoid thrusting
language client maintainers, we don't recommend OpenTelemetry clients to start
the implementation unless explicitly communicated via
[OTEP](https://github.com/open-telemetry/oteps#opentelemetry-enhancement-proposal-otep).

<details>
<summary>
Table of Contents
</summary>

* [Overview](#overview)
* [MeterProvider](#meterprovider)
* [View](#view)
* [MeasurementProcessor](#measurementprocessor)
* [MetricProcessor](#metricprocessor)
* [MetricExporter](#metricexporter)
  * [PushMetricExporter](#pushmetricexporter)
  * [PullMetricExporter](#pullmetricexporter)

</details>

## Overview

## MeterProvider

Q: How do we describe which data we care about vs. not (e.g. if a library
exposes both CPU and memory, and the application developer only wants memory
metrics)?

Q: How do we know which meters / instruments are available from the
instrumentation library?

Q: For time series that we don't need, do we drop the them at processor level
(pay for the collection cost and then drop the data on the floor)?

## View

Q: Do we allow multiple Views provided for a single instrument? (my answer would
be yes)

Q: Do we want to View API to control the dimensions retrieved from
Baggage/Context? Or it should be handled by MeasurementProcessor?

## MeasurementProcessor

Note: This processor will run before the aggregator, which means it will have
access to the Baggage/Context if the measurements are reported by a synchronous
instrument.

## MetricProcessor

Note: This process will run after the aggregator, which means it will have no
access to the Baggage/Context.

## MetricExporter

Q: Do we allow a push exporter and a pull exporter to coexist on a single
MeterProvider?

### PushMetricExporter

Q: Do we allow multiple push exporters to be configured on a single
MeterProvider? If yes, do we allow them to push at different frequency (e.g.
hourly report for temperature, but 5 seconds report for CPU utilization)?

### PullMetricExporter

Q: Do we allow multiple pull exporters to be configured on a single
MeterProvider?

Q: Do we want to support the scenario where asynchronous instruments are
observed at a higher frequency than the pull exporter?
