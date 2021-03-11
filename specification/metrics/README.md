# OpenTelemetry Metrics

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
  * [Design Goals](#design-goals)
* [Specifications](#specifications)
  * [Metrics API](./api.md)
  * Metrics SDK (not available yet)
  * Metrics Data Model and Protocol (not available yet)
  * [Semantic Conventions](./semantic_conventions/README.md)

</details>

## Overview

### Design Goals

Given there are many well-established metrics solutions that exist today, it is
important to understand the goals of OpenTelemetry’s metrics effort:

* **Being able to connect metrics to other signals**. For example, metrics and
  traces can be correlated via exemplars, and metrics dimensions can be enriched
  via [Baggage](../baggage/api.md) and [Context](../context/context.md).
  Additionally, [Resource](../resource/sdk.md) can be applied to
  [logs](../overview.md#log-signal)/[metrics](../overview.md#metric-signal)/[traces](../overview.md#tracing-signal)
  in a consistent way.

* **Providing a path for [OpenCensus](https://opencensus.io/) customers to
  migrate to OpenTelemetry**. This was the original goal of OpenTelemetry -
  converging OpenCensus and OpenTracing. We will focus on providing the
  semantics and capability, instead of doing a 1-1 mapping of the APIs.

* **Working with existing metrics instrumentation protocols and standards**. The
  minimum goal is to provide full support for
  [Prometheus](https://prometheus.io/) and
  [StatsD](https://github.com/statsd/statsd) - users should be able to use
  OpenTelemetry clients and [Collector](../overview.md#collector) to collect and export metrics, with the
  ability to achieve the same functionality as their native clients.

### Concepts

The **OpenTelemetry Metrics API** supports capturing measurements about the
execution of a computer program at run time. The Metrics API is designed
explicitly for processing raw measurements, generally with the intent to produce
continuous summaries of those measurements, efficiently and simultaneously.
Hereafter, "the API" refers to the OpenTelemetry Metrics API.

The API provides functions for capturing raw measurements, through
several calling conventions that offer different levels of
performance. Regardless of calling convention, we define a _metric
event_ as the logical thing that happens when a new measurement is
captured. This moment of capture (at "run time") defines an implicit
timestamp, which is the wall time an SDK would read from a clock at
that moment.

The word "semantic" or "semantics" as used here refers to _how we give
meaning_ to metric events, as they take place under the API. The term
is used extensively in this document to define and explain these API
functions and how we should interpret them. As far as possible, the
terminology used here tries to convey the intended semantics, and a
_standard implementation_ will be described below to help us
understand their meaning. Standard implementations perform
aggregation corresponding to the default interpretation for each kind
of metric event.

Monitoring and alerting systems commonly use the data provided through metric
events, after applying various [aggregations](#aggregations) and converting into
various exposition formats. However, we find that there are many other uses for
metric events, such as to record aggregated or raw measurements in tracing and
logging systems. For this reason, [OpenTelemetry requires a separation of the
API from the SDK](../library-guidelines.md#requirements), so that different SDKs
can be configured at run time.

## Specifications

* [Metrics API](./api.md)
* Metrics SDK (not available yet)
* Metrics Data Model and Protocol (not available yet)
* [Semantic Conventions](./semantic_conventions/README.md)

## References

* Scenarios for Metrics API/SDK Prototyping ([OTEP 146](https://github.com/open-telemetry/oteps/blob/main/text/metrics/0146-metrics-prototype-scenarios.md))