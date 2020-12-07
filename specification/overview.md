# Overview

<details>
<summary>
Table of Contents
</summary>
<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [Distributed Tracing](#distributed-tracing)
  * [Trace](#trace)
  * [Span](#span)
  * [SpanContext](#spancontext)
  * [Links between spans](#links-between-spans)
- [Metrics](#metrics)
  * [Recording raw measurements](#recording-raw-measurements)
    + [Measure](#measure)
    + [Measurement](#measurement)
  * [Recording metrics with predefined aggregation](#recording-metrics-with-predefined-aggregation)
  * [Metrics data model and SDK](#metrics-data-model-and-sdk)
- [Logs](#logs)
  * [Data model](#data-model)
- [Baggage](#baggage)
- [Resources](#resources)
- [Context Propagation](#context-propagation)
- [Propagators](#propagators)
- [Collector](#collector)
- [Instrumentation Libraries](#instrumentation-libraries)
- [Semantic Conventions](#semantic-conventions)

<!-- tocstop -->

</details>

This document provides an overview of the pillars of telemetry that
OpenTelemetry supports and defines important fundamental terms.

You can find additional definitions for the terms in this document in the [glossary](glossary.md).

## Distributed tracing

A distributed trace is a set of events that are triggered as a result of a single
logical operation and consolidated across various components of an application. A
distributed trace contains events that cross process, network, and security
boundaries. For example, a distributed trace might be initiated when someone 
presses a button to start an action on a website. The trace represents
calls made between the downstream services that handled the chain of requests
initiated by the button being pressed.

### Trace

**Traces** in OpenTelemetry are defined implicitly by their spans. In
particular, you can think of a trace as a directed acyclic graph (DAG) of
spans, where the edges between spans are defined as parent/child
relationship.

For example, the following is an example trace made up of 6 spans:

```
Causal relationships between spans in a single trace

        [Span A]  ←←←(the root span)
            |
     +------+------+
     |             |
 [Span B]      [Span C] ←←←(Span C is a `child` of Span A)
     |             |
 [Span D]      +---+-------+
               |           |
           [Span E]    [Span F]
```

Sometimes it's easier to visualize traces with a time axis as in the diagram
below:

```
Temporal relationships between spans in a single trace

––|–––––––|–––––––|–––––––|–––––––|–––––––|–––––––|–––––––|–> time

 [Span A···················································]
   [Span B··············································]
      [Span D··········································]
    [Span C········································]
         [Span E·······]        [Span F··]
```

### Span

Each **Span** encapsulates the following state:

- An operation name
- A start and finish timestamp
- [**Attributes**](./common/common.md#attributes): A list of key-value pairs.
- A set of zero or more **Events**, each of which is itself a tuple (timestamp, name, [**Attributes**](./common/common.md#attributes)). The name must be a string.
- The parent's span identifier.
- [**Links**](#links-between-spans) to zero or more causally-related spans
  (via the **SpanContext** of those related spans).
- **SpanContext** information required to reference a span. See the next section for more information.

### SpanContext

**SpanContext** represents all the information that identifies a span in the trace.
It must be propagated to child spans and across process boundaries. A
SpanContext contains the tracing identifiers and the options that are
propagated from parent to child spans.

- **TraceId** is the identifier for a trace. It's worldwide unique with
  practically sufficient probability by being made as 16 randomly generated
  bytes. TraceId is used to group all spans for a specific trace together across
  all processes.
- **SpanId** is the identifier for a span. It's globally unique with
  practically sufficient probability by being made as 8 randomly generated
  bytes. When passed to a child Span, this identifier becomes the parent span ID
  for the child span.
- **TraceFlags** represent the options for a trace. They're represented as one
  byte (bitmap).
  - Sampling bit -  Bit to represent whether a trace is sampled or not (mask
    `0x1`).
- **Tracestate** carries tracing system-specific context in a list of key-value
  pairs. Tracestate lets different vendors propagate additional
  information and interoperate with their legacy ID formats. For more information,
  see [Trace Context Level 2](https://w3c.github.io/trace-context/#tracestate-field)
  in the W3C Editor's Draft.

### Links between spans

A span can be linked to zero or more other spans (defined by
SpanContext) that are causally related. Links can point to
spans inside a single trace or across different traces.
You can use links to represent batched operations where a span was
initiated by multiple initiating spans, each representing a single incoming
item being processed in the batch.

Another example of using a link is to declare the relationship between
the originating and following trace. This functionality is useful when a span
enters trusted boundaries of a service and service policy requires the generation of a new
trace rather than trusting the incoming trace context. The new linked trace can
also represent a long-running asynchronous data processing operation
initiated by one of many fast incoming requests.

When you use the scatter/gather (or fork/join) pattern, the root
operation starts multiple downstream processing operations that are
aggregated back into a single span. The last span is linked to many
operations that it aggregates. All the spans are from the same trace and are
similar to the parent field of a span. However, in this scenario it's a best 
practice to not set the parent of the spans because semantically the parent field
represents a single-parent scenario. In many cases the parent span fully
encloses the child spans, which is not the case in scatter/gather and batch
scenarios.

## Metrics

OpenTelemetry let you record raw measurements or metrics with a predefined
aggregation and set of labels.

Recording raw measurements using OpenTelemetry API allows to defer to end-user
the decision on what aggregation algorithm should be applied for this metric as
well as defining labels (dimensions). It will be used in client libraries like
gRPC to record raw measurements "server_latency" or "received_bytes". So end
user will decide what type of aggregated values should be collected out of these
raw measurements. It may be simple average or elaborate histogram calculation.

Recording of metrics with the pre-defined aggregation using OpenTelemetry API is
not less important. It allows to collect values like cpu and memory usage, or
simple metrics like "queue length".

### Recording raw measurements

The main classes used to record raw measurements are `Measure` and
`Measurement`. List of `Measurement`s alongside the additional context can be
recorded using OpenTelemetry API. So user may define to aggregate those
`Measurement`s and use the context passed alongside to define additional
dimensions of the resulting metric.

#### Measure

`Measure` describes the type of the individual values recorded by a library. It
defines a contract between the library exposing the measurements and an
application that will aggregate those individual measurements into a `Metric`.
`Measure` is identified by name, description and a unit of values.

#### Measurement

`Measurement` describes a single value to be collected for a `Measure`.
`Measurement` is an empty interface in API surface. This interface is defined in
SDK.

### Recording metrics with predefined aggregation

The base class for all types of pre-aggregated metrics is called `Metric`. It
defines basic metric properties like a name and labels. Classes inheriting from
the `Metric` define their aggregation type as well as a structure of individual
measurements or Points. API defines the following types of pre-aggregated
metrics:

- Counter metric to report instantaneous measurement. Counter values can go
  up or stay the same, but can never go down. Counter values cannot be
  negative. There are two types of counter metric values - `double` and `long`.
- Gauge metric to report instantaneous measurement of a numeric value. Gauges can
  go both up and down. The gauges values can be negative. There are two types of
  gauge metric values - `double` and `long`.

API allows to construct the `Metric` of a chosen type. SDK defines the way to
query the current value of a `Metric` to be exported.

Every type of a `Metric` has it's API to record values to be aggregated. API
supports both - push and pull model of setting the `Metric` value.

### Metrics data model and SDK

Metrics data model is defined in SDK and is based on
[metrics.proto](https://github.com/open-telemetry/opentelemetry-proto/blob/master/opentelemetry/proto/metrics/v1/metrics.proto).
This data model is used by all the OpenTelemetry exporters as an input.
Different exporters have different capabilities (e.g. which data types are
supported) and different constraints (e.g. which characters are allowed in label
keys). Metrics is intended to be a superset of what's possible, not a lowest
common denominator that's supported everywhere. All exporters consume data from
Metrics Data Model via a Metric Producer interface defined in OpenTelemetry SDK.

Because of this, Metrics puts minimal constraints on the data (e.g. which
characters are allowed in keys), and code dealing with Metrics should avoid
validation and sanitization of the Metrics data. Instead, pass the data to the
backend, rely on the backend to perform validation, and pass back any errors
from the backend.

## Logs

### Data model

[Log Data Model](logs/data-model.md) defines how logs and events are understood by
OpenTelemetry.

## Baggage

In addition to trace propagation, OpenTelemetry provides a simple mechanism for propagating
name/value pairs, called `Baggage`. `Baggage` is intended for
indexing observability events in one service with attributes provided by a prior service in
the same transaction. This helps to establish a causal relationship between these events.

While `Baggage` can be used to prototype other cross-cutting concerns, this mechanism is primarily intended
to convey values for the OpenTelemetry observability systems.

These values can be consumed from `Baggage` and used as additional dimensions for metrics,
or additional context for logs and traces. Some examples:

- a web service can benefit from including context around what service has sent the request
- a SaaS provider can include context about the API user or token that is responsible for that request
- determining that a particular browser version is associated with a failure in an image processing service

For backward compatibility with OpenTracing, Baggage is propagated as `Baggage` when
using the OpenTracing bridge. New concerns with different criteria should consider creating a new
cross-cutting concern to cover their use-case; they may benefit from the W3C encoding format but
use a new HTTP header to convey data throughout a distributed trace.

## Resources

`Resource` captures information about the entity for which telemetry is
recorded. For example, metrics exposed by a Kubernetes container can be linked
to a resource that specifies the cluster, namespace, pod, and container name.

`Resource` may capture an entire hierarchy of entity identification. It may
describe the host in the cloud and specific container or an application running
in the process.

Note, that some of the process identification information can be associated with
telemetry automatically by OpenTelemetry SDK or specific exporter. See
OpenTelemetry
[proto](https://github.com/open-telemetry/opentelemetry-proto/blob/a46c815aa5e85a52deb6cb35b8bc182fb3ca86a0/src/opentelemetry/proto/agent/common/v1/common.proto#L28-L96)
for an example.

## Context Propagation

All of OpenTelemetry cross-cutting concerns, such as traces and metrics,
share an underlying `Context` mechanism for storing state and
accessing data across the lifespan of a distributed transaction.

See the [Context](context/context.md)

## Propagators

OpenTelemetry uses `Propagators` to serialize and deserialize cross-cutting concern values
such as `Span`s (usually only the `SpanContext` portion) and `Baggage`. Different `Propagator` types define the restrictions
imposed by a specific transport and bound to a data type.

The Propagators API currently defines one `Propagator` type:

- `TextMapPropagator` injects values into and extracts values from carriers as text.

## Collector

The OpenTelemetry collector is a set of components that can collect traces,
metrics and eventually other telemetry data (e.g. logs) from processes
instrumented by OpenTelementry or other monitoring/tracing libraries (Jaeger,
Prometheus, etc.), do aggregation and smart sampling, and export traces and
metrics to one or more monitoring/tracing backends. The collector will allow to
enrich and transform collected telemetry (e.g. add additional attributes or
scrub personal information).

The OpenTelemetry collector has two primary modes of operation: Agent (a daemon
running locally with the application) and Collector (a standalone running
service).

Read more at OpenTelemetry Service [Long-term
Vision](https://github.com/open-telemetry/opentelemetry-collector/blob/master/docs/vision.md).

## Instrumentation Libraries

See [Instrumentation Library](glossary.md#instrumentation-library)

The inspiration of the project is to make every library and application
observable out of the box by having them call OpenTelemetry API directly. However,
many libraries will not have such integration, and as such there is a need for
a separate library which would inject such calls, using mechanisms such as
wrapping interfaces, subscribing to library-specific callbacks, or translating
existing telemetry into the OpenTelemetry model.

A library that enables OpenTelemetry observability for another library is called
an [Instrumentation Library](glossary.md#instrumentation-library).

An instrumentation library should be named to follow any naming conventions of
the instrumented library (e.g. 'middleware' for a web framework).

If there is no established name, the recommendation is to prefix packages
with "opentelemetry-instrumentation", followed by the instrumented library
name itself. Examples include:

* opentelemetry-instrumentation-flask (Python)
* @opentelemetry/instrumentation-grpc (Javascript)

## Semantic Conventions

OpenTelemetry defines standard names and values of Resource attributes and
Span attributes.

* [Resource Conventions](resource/semantic_conventions/README.md)
* [Span Conventions](trace/semantic_conventions/README.md)
* [Metrics Conventions](metrics/semantic_conventions/README.md)

The type of the attribute SHOULD be specified in the semantic convention
for that attribute. See more details about [Attributes](./common/common.md#attributes).
