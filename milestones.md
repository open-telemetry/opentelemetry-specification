# OpenTelemetry: A Roadmap to Convergence

This document covers the initial milestones for the project. Each repository in
OpenTelemetry project need to adjust milestones to this plan based on
project-specific estimations.

For each language, we want to quickly achieve parity with existing OpenTracing
and OpenCensus implementations. For languages which have both an OpenTracing and
OpenCensus implementation, we would like to achieve parity in OpenTelemetry by
**September, 2019**, and sunset the existing OpenTracing and OpenCensus projects
by **November, 2019**.

## Switching to OpenTelemetry

Parity can be defined as the following features:

- A set of interfaces which implement the OpenTelemetry specification in a given
  programming language.
- An SDK implementing OpenTelemetry specification.
- Backwards compatibility with OpenTracing and OpenCensus.
- Metadata helpers for recording common operations defined in the OpenTelemetry
  [semantic conventions](https://github.com/open-telemetry/opentelemetry-specification/blob/master/semantic-conventions.md).
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

### TL;DR;

Milestones for Java and cross-language specification:

- End of June:
  - [basic SDK implemented](https://github.com/open-telemetry/opentelemetry-java/milestone/2)
    in Java.
  - API feedback issues triage done.
- Mid July:
  - [exporters implemented](https://github.com/open-telemetry/opentelemetry-java/milestone/3)
    in Java.
  - [basic SDK specs](https://github.com/open-telemetry/opentelemetry-specification/milestone/3)
    complete.
  - [first API revision](https://github.com/open-telemetry/opentelemetry-specification/milestone/2)
    documented.
- Mid August:
  - [extended SDK documented](https://github.com/open-telemetry/opentelemetry-specification/milestone/4).
  - [second API revision](https://github.com/open-telemetry/opentelemetry-specification/milestone/5)
    documented.
- End of August:
  - [extended SDK implemented](https://github.com/open-telemetry/opentelemetry-java/milestone/4)
    and stabilized in Java.
  - Java SDK is production ready
- Mid September (or after end-user validation):
  - API is revised
- End of September (or after end-user validation):
  - Version 1.0 is declared.

### Current status

**API proposal**:

- [Done in Java](https://github.com/open-telemetry/opentelemetry-java/milestone/1)
- API proposal [documented](https://github.com/open-telemetry/opentelemetry-specification/milestone/1)
  in specs

**SDK proposal**:

- Basic telemetry pipeline for traces complete
- On track to finish by the **end of the month** in limited scope
- Specification work for SDK hasn’t been started

### Finish SDK proposal

We are limiting scope for SDK proposal work (roughly) to the following areas:

- Spans pipeline:
  - SpanBuilder interceptors interface
  - Built-in samplers (percentage sampler).
  - SpanProcessor interface and implementations:
  - Default and built-in processors
    - Simple processor
    - Batching processors
    - Block when the queue is full processor
  - Exporter interface
  - Reporting raw SpanData
- Distributed context
  - Basic implementation
- Metrics
  - Metrics aggregation implementation
  - MetricProducer interface

[**Java
implementation**](https://github.com/open-telemetry/opentelemetry-java/milestone/2).
In the limited scope we are working towards completing the SDK proposal in Java
by end of this month.

[**Specifications
writing**](https://github.com/open-telemetry/opentelemetry-specification/milestone/3).
We can start writing specs for SDK now. Realistically we need two weeks after
java implementation complete to document all aspects of SDK.

### Basic exporters

As part of OpenTelemetry we committed to deliver three basic exporters - Zipkin,
Jaeger and Prometheus.

Both - documentation and java implementation of those exporters is planned to be
completed in two weeks after SDK proposal in Java is done - **12th of July.**

Tracking this work in
[Java](https://github.com/open-telemetry/opentelemetry-java/milestone/3).

### Iterating on API

As proposed API was released we start getting feedback on it. The plan is to
triage feedback in three milestones:

[**API revision
07-2019**](https://github.com/open-telemetry/opentelemetry-specification/milestone/2)
**(target - mid July). Proposed API cleanup.**

- Easy fixes - renamings, polishing, removing unnecessary API surface
- Add missing features - adding histograms and forgotten getters
- Issues that quickly getting agreement. For example, adding component for tracer

This milestone is for the fast clean up of a proposed API.

**API revision 08-2019 (target - mid August). API Complete.**

- All issues not included into the first milestone

**API revision 09-2019 (target - mid September). API v1.0.**

- Reserved for the issues received as a result of an end user feedback

**Future:**

- Feature requests that we can postpone to after stable version
- New telemetry sources support

### Extending the SDK

Once basic SDK is complete in Java we will switch to the specs first approach on
advancing its feature set.

Example of scope for extended SDK:

1. OTSvc protocol and implementation
2. Add missing features
   1. More SpanProcessors. Example: non blocking queue processor with telemetry drop
   2. More samplers. Example - rate limiting sampler, etc.
   3. Histograms – API and SDK
   4. Metrics filters and processors
   5. etc.
3. Discussions like
   1. Native (POJO) object vs. Proto-generated object with proto dependency in
      SDK
4. Tracestate manipulation callbacks
5. Other

First iteration of SDK feedback – **mid August** we have specs, **End of
August** – first iteration of Java SDK complete.

### Getting to release

By mid August the Java basic SDK will be complete and we will begin
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
