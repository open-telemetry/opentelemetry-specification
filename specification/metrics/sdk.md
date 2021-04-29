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

## View

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
MeterProvider? If yes, do we allow them to push at different frequency?

### PullMetricExporter

Q: Do we allow multiple pull exporters to be configured on a single
MeterProvider?

Q: Do we want to support the scenario where asynchronous instruments are
observed at a higher frequency than the pull exporter?
