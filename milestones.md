# OpenTelemetry: A Roadmap to Convergence

This document covers the milestones for the project. Each repository in
OpenTelemetry project need to adjust milestones to this plan based on
project-specific estimates.

It is recommended to align language versions to the spec versions they
implement.

For each language, we want to quickly achieve parity with existing OpenTracing
and OpenCensus implementations. For languages which have both an OpenTracing and
OpenCensus implementation, we would like to achieve parity in OpenTelemetry by
**first quarter of 2020**, and sunset the existing OpenTracing and OpenCensus
projects in the **second quarter of 2020**.

Original plans of sunsetting older SDKs in **November, 2019** was changed as we
discovered a lot of unaccounted work and production testing will be delayed by
holidays season. We are still committed to deliver high quality previews of
languages SDKs in **2019**.

## Switching to OpenTelemetry

Parity can be defined as the following features:

- A set of interfaces which implement the OpenTelemetry specification in a given
  programming language.
- An SDK implementing OpenTelemetry specification.
- Backwards compatibility with OpenTracing and OpenCensus via bridges.
- Metadata helpers or other means for recording common operations defined in the
  OpenTelemetry [semantic conventions](specification/data-semantic-conventions.md).
- Tests which provide evidence of interoperability.
- Benchmarks which provide evidence of expected resource utilization.
- Documentation and getting started guide.

## Milestones

With OpenTelemetry we strive for consistency and unification. It is important
for users of OpenTelemetry to get the same look and feel of APIs and consistent
data collection across all languages. Consistency is achieved thru the
specifications and cross-language test cases.

As OpenTracing and OpenCensus projects converge we write specifications the same
time as we develop libraries.

We will refer to [API
Proposal](https://github.com/open-telemetry/opentelemetry-specification/milestone/1)
Alpha v0.1 release.

### Alpha v0.2

The spirit of this release is to have a demo-able product that anybody can start
playing with and start implementing instrumentation adaptors and data collectors
for various scenarios.

As part of this release we ask to implement Tracing and Metrics exporters so it
will be easy to visualize the scenarios. For Tracing - either Jaeger or Zipkin
can be selected, for Metrics - Prometheus.

**Proposed deadline:** Alpha v0.2 specs complete by 10/4

#### API specs for Alpha v0.2

Alpha v0.1 received a lot of feedback. As part of an Alpha release there will be
a few major areas of improvement - change for out of band span reporting API and
the merged pre-aggregated and non-aggregated metrics API. There are other
changes as well.

We already plan for the next iteration and we know that API is expected to be
changed for the Alpha v0.3 milestone. The big improvements in works are
initialization and configuring logic as well as context propagation detachment.

#### SDK specs for Alpha v0.2

There were no formal SDK proposal. So this milestone will define SDK data
structures and public methods for the first time.

In scope of SDK Alpha release are:

- Tracing
  - Built-in samplers (percentage sampler).
  - SpanProcessor interface
  - Batching SpanProcessor
  - Exporter interface
  - Jaeger and/or Zipkin exporter
- Context Propagation
  - In-process propagation
  - Inject and Extract 
  - DistributedContext
- Metrics
  - MetricsProcessor interface
  - Aggregation MetricsProcessor
  - Exporter interface
  - Prometheus Exporter
  
Also in scope:

- Jaeger and/or Zipkin exporter
- Prometheus exporter

### Alpha v0.2 release validation

Languages will ship alpha releases shortly after specification will be complete.
The main purpose of this release is to start implementing data collectors and
use API and SDK for the user scenarios. This will ensure validation of concepts
and public surface.

Note, we DO expect changes in APIs for the Alpha v0.3 release.

### Alpha v0.3 release

The spirit of v0.3 release is to deliver a product with the stable, almost the
release candidate level of APIs and interfaces.

After the v0.3 release of language SDKs we do expect that languages public
surface may change, but we do not expect any major changes in conceptual level
in specifications.

**Proposed deadline**: Specification complete by Nov 15th.

In scope of SDK Alpha v0.3 release are:

- Finalize the OpenTelemetry protocol

Required Spec RFCs for Alpha v0.3:

- Global Init
- Context (separate baggage, renaming, etc)
- Protocol
- Semantic Conventions

### Alpha v0.4 release

Collector support for OpenTelemetry protocol will be implemented by this time
and languages SDKs will implement OpenTelemetry collector exporter.

**Proposed deadline**: end of year 2019

### Getting to release

By end of year the basic language SDKs will be complete and we will begin
stabilization work. Also OpenCensus can be switched to the OpenTelemetry SDK. As
well as instrumentation adapters can be implemented. So we will have early
adopters.

By early September we committed to provide a production ready full-featured
OpenTelemetry SDK in Java. End user feedback is one the critical force to make
the API and SDK right. Thus we don’t plan to release **1.0** release and call it
**0.9**. As OpenTelemetry was built based on two mature SDKs we do not expect
major changes after September. However, as with any big projects, we anticipate
some issues with the new API and SDKs.

Depending on users engagement we hope to get to the 1.0 as early as the end of
September.

Note, as specification work delayed other languages may not have production
ready SDK in early September. Milestones have to be set individually in every
language.
