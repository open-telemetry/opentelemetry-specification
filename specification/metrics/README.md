<!--- Hugo front matter used to generate the website version of this page:
linkTitle: Metrics
path_base_for_github_subdir:
  from: tmp/otel/specification/metrics/_index.md
  to: metrics/README.md
--->

# OpenTelemetry Metrics

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [Overview](#overview)
  * [Design Goals](#design-goals)
  * [Concepts](#concepts)
    + [API](#api)
    + [SDK](#sdk)
    + [Programming Model](#programming-model)
- [Specifications](#specifications)
- [References](#references)

<!-- tocstop -->

</details>

## Overview

### Design Goals

Given there are many well-established metrics solutions that exist today, it is
important to understand the goals of OpenTelemetry’s metrics effort:

* **Being able to connect metrics to other signals**. For example, metrics and
  traces can be correlated via [exemplars](data-model.md#exemplars), and metrics attributes can be enriched
  via [Baggage](../baggage/api.md) and [Context](../context/README.md).
  Additionally, [Resource](../resource/sdk.md) can be applied to
  [logs](../overview.md#log-signal)/[metrics](../overview.md#metric-signal)/[traces](../overview.md#tracing-signal)
  in a consistent way.

* **Providing a path for [OpenCensus](https://opencensus.io/) customers to
  migrate to OpenTelemetry**. This was the original goal of OpenTelemetry -
  converging OpenCensus and OpenTracing. We will focus on providing the
  semantics and capability, instead of doing a 1-1 mapping of the APIs.

* **Working with existing metrics instrumentation protocols and standards**.
  Here is the minimum set of goals:
  * Providing full support for [Prometheus](https://prometheus.io/) - users
    should be able to use OpenTelemetry clients and
    [Collector](../overview.md#collector) to collect and export metrics, with
    the ability to achieve the same functionality as the native Prometheus
    clients.
  * Providing the ability to collect [StatsD](https://github.com/statsd/statsd)
    metrics using the [OpenTelemetry Collector](../overview.md#collector).

### Concepts

#### API

The **OpenTelemetry Metrics API** ("the API" hereafter) serves two purposes:

* Capturing raw measurements efficiently and simultaneously.
* Decoupling the instrumentation from the [SDK](#sdk), allowing the SDK to be
  specified/included in the application.

When no [SDK](#sdk) is explicitly included/enabled in the application, no
telemetry data will be collected. Please refer to the overall [OpenTelemetry
API](../overview.md#api) concept and [API and Minimal
Implementation](../library-guidelines.md#api-and-minimal-implementation) for
more information.

#### SDK

The **OpenTelemetry Metrics SDK** ("the SDK" hereafter) implements the API,
providing functionality and extensibility such as configuration, aggregation,
processors and exporters.

OpenTelemetry requires a [separation of the API from the
SDK](../library-guidelines.md#requirements), so that different SDKs can be
configured at run time. Please refer to the overall [OpenTelemetry
SDK](../overview.md#sdk) concept for more information.

#### Programming Model

```text
+------------------+
| MeterProvider    |                 +-----------------+             +--------------+
|   Meter A        | Measurements... |                 | Metrics...  |              |
|     Instrument X +-----------------> In-memory state +-------------> MetricReader |
|     Instrument Y |                 |                 |             |              |
|   Meter B        |                 +-----------------+             +--------------+
|     Instrument Z |
|     ...          |                 +-----------------+             +--------------+
|     ...          | Measurements... |                 | Metrics...  |              |
|     ...          +-----------------> In-memory state +-------------> MetricReader |
|     ...          |                 |                 |             |              |
|     ...          |                 +-----------------+             +--------------+
+------------------+
```

## Specifications

* [Metrics API](./api.md)
* [Metrics SDK](./sdk.md)
* [Metrics Data Model and Protocol](./data-model.md)
* [Metrics Requirement Levels](./metric-requirement-level.md)

## References

* Scenarios for Metrics API/SDK Prototyping ([OTEP
  146](../../oteps/metrics/0146-metrics-prototype-scenarios.md))
