# Overview

<details>
<summary>
Table of Contents
</summary>
<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [OpenTelemetry Client Architecture](#opentelemetry-client-architecture)
  * [API](#api)
  * [SDK](#sdk)
  * [Semantic Conventions](#semantic-conventions)
  * [Contrib Packages](#contrib-packages)
  * [Versioning and Stability](#versioning-and-stability)
- [Tracing Signal](#tracing-signal)
  * [Traces](#traces)
  * [Spans](#spans)
  * [SpanContext](#spancontext)
  * [Links between spans](#links-between-spans)
- [Metric Signal](#metric-signal)
  * [Recording raw measurements](#recording-raw-measurements)
    + [Measure](#measure)
    + [Measurement](#measurement)
  * [Recording metrics with predefined aggregation](#recording-metrics-with-predefined-aggregation)
  * [Metrics data model and SDK](#metrics-data-model-and-sdk)
- [Log Signal](#log-signal)
  * [Data model](#data-model)
- [Baggage Signal](#baggage-signal)
- [Resources](#resources)
- [Context Propagation](#context-propagation)
- [Propagators](#propagators)
- [Collector](#collector)
- [Instrumentation Libraries](#instrumentation-libraries)

<!-- tocstop -->

</details>

This document provides an overview of the OpenTelemetry project and defines important fundamental terms.

Additional term definitions can be found in the [glossary](glossary.md).

## OpenTelemetry Client Architecture

![Cross cutting concerns](../internal/img/architecture.png)

At the highest architectural level, OpenTelemetry clients are organized into [**signals**](glossary.md#signals).
Each signal provides a specialized form of observability. For example, tracing, metrics, and baggage are three separate signals.
Signals share a common subsystem – **context propagation** – but they function independently from each other.

Each signal provides a mechanism for software to describe itself. A codebase, such as web framework or a database client, takes a dependency on various signals in order to describe itself. OpenTelemetry instrumentation code can then be mixed into the other code within that codebase.
This makes OpenTelemetry a **cross-cutting concern** - a piece of software which is mixed into many other pieces of software in order to provide value. Cross-cutting concerns, by their very nature, violate a core design principle – separation of concerns. As a result, OpenTelemetry client design requires extra care and attention to avoid creating issues for the codebases which depend upon these cross-cutting APIs.

OpenTelemetry clients are designed to separate the portion of each signal which must be imported as cross-cutting concerns from the portions which can be managed independently. OpenTelemetry clients are also designed to be an extensible framework.
To accomplish these goals, each signal consists of four types of packages: API, SDK, Semantic Conventions, and Contrib.

### API

API packages consist of the cross-cutting public interfaces used for instrumentation. Any portion of an OpenTelemetry client which is imported into third-party libraries and application code is considered part of the API.

### SDK

The SDK is the implementation of the API provided by the OpenTelemetry project. Within an application, the SDK is installed and managed by the [application owner](glossary.md#application-owner).
Note that the SDK includes additional public interfaces which are not considered part of the API package, as they are not cross-cutting concerns. These public interfaces are defined as [constructors](glossary.md#constructors) and [plugin interfaces](glossary.md#sdk-plugins).
Application owners use the SDK constructors; [plugin authors](glossary.md#plugin-author) use the SDK plugin interfaces.
[Instrumentation authors](glossary.md#instrumentation-author) MUST NOT directly reference any SDK package of any kind, only the API.

### Semantic Conventions

The **Semantic Conventions** define the keys and values which describe commonly observed concepts, protocols, and operations used by applications.

* [Resource Conventions](resource/semantic_conventions/README.md)
* [Span Conventions](trace/semantic_conventions/README.md)
* [Metrics Conventions](metrics/semantic_conventions/README.md)

Both the collector and the client libraries SHOULD autogenerate semantic
convention keys and enum values into constants (or language idomatic
equivalent). Generated values shouldn't be distributed in stable packages
until semantic conventions are stable.
The [YAML](../semantic_conventions/README.md) files MUST be used as the
source of truth for generation. Each language implementation SHOULD
provide language-specific support to the
[code generator](https://github.com/open-telemetry/build-tools/tree/main/semantic-conventions#code-generator).

### Contrib Packages

The OpenTelemetry project maintains integrations with popular OSS projects which have been identified as important for observing modern web services.
Example API integrations include instrumentation for web frameworks, database clients, and message queues.
Example SDK integrations include plugins for exporting telemetry to popular analysis tools and telemetry storage systems.

Some plugins, such as OTLP Exporters and TraceContext Propagators, are required by the OpenTelemetry specification. These required plugins are included as part of the SDK.

Plugins and instrumentation packages which are optional and separate from the SDK are referred to as **Contrib** packages.
**API Contrib** refers to packages which depend solely upon the API; **SDK Contrib** refers to packages which also depend upon the SDK.

The term Contrib specifically refers to the collection of plugins and instrumentation maintained by the OpenTelemetry project; it does not refer to third-party plugins hosted elsewhere.

### Versioning and Stability

OpenTelemetry values stability and backwards compatibility. Please see the [versioning and stability guide](./versioning-and-stability.md) for details.

## Tracing Signal

A distributed trace is a set of events, triggered as a result of a single
logical operation, consolidated across various components of an application. A
distributed trace contains events that cross process, network and security
boundaries. A distributed trace may be initiated when someone presses a button
to start an action on a website - in this example, the trace will represent
calls made between the downstream services that handled the chain of requests
initiated by this button being pressed.

### Traces

**Traces** in OpenTelemetry are defined implicitly by their **Spans**. In
particular, a **Trace** can be thought of as a directed acyclic graph (DAG) of
**Spans**, where the edges between **Spans** are defined as parent/child
relationship.

For example, the following is an example **Trace** made up of 6 **Spans**:

```
Causal relationships between Spans in a single Trace

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

Sometimes it's easier to visualize **Traces** with a time axis as in the diagram
below:

```
Temporal relationships between Spans in a single Trace

––|–––––––|–––––––|–––––––|–––––––|–––––––|–––––––|–––––––|–> time

 [Span A···················································]
   [Span B··············································]
      [Span D··········································]
    [Span C········································]
         [Span E·······]        [Span F··]
```

### Spans

A span represents an operation within a transaction. Each **Span** encapsulates
the following state:

- An operation name
- A start and finish timestamp
- [**Attributes**](./common/common.md#attributes): A list of key-value pairs.
- A set of zero or more **Events**, each of which is itself a tuple (timestamp, name, [**Attributes**](./common/common.md#attributes)). The name must be strings.
- Parent's **Span** identifier.
- [**Links**](#links-between-spans) to zero or more causally-related **Spans**
  (via the **SpanContext** of those related **Spans**).
- **SpanContext** information required to reference a Span. See below.

### SpanContext

Represents all the information that identifies **Span** in the **Trace** and
MUST be propagated to child Spans and across process boundaries. A
**SpanContext** contains the tracing identifiers and the options that are
propagated from parent to child **Spans**.

- **TraceId** is the identifier for a trace. It is worldwide unique with
  practically sufficient probability by being made as 16 randomly generated
  bytes. TraceId is used to group all spans for a specific trace together across
  all processes.
- **SpanId** is the identifier for a span. It is globally unique with
  practically sufficient probability by being made as 8 randomly generated
  bytes. When passed to a child Span this identifier becomes the parent span id
  for the child **Span**.
- **TraceFlags** represents the options for a trace. It is represented as 1
  byte (bitmap).
  - Sampling bit -  Bit to represent whether trace is sampled or not (mask
    `0x1`).
- **Tracestate** carries tracing-system specific context in a list of key value
  pairs. **Tracestate** allows different vendors propagate additional
  information and inter-operate with their legacy Id formats. For more details
  see [this](https://w3c.github.io/trace-context/#tracestate-field).

### Links between spans

A **Span** may be linked to zero or more other **Spans** (defined by
**SpanContext**) that are causally related. **Links** can point to
**Spans** inside a single **Trace** or across different **Traces**.
**Links** can be used to represent batched operations where a **Span** was
initiated by multiple initiating **Spans**, each representing a single incoming
item being processed in the batch.

Another example of using a **Link** is to declare the relationship between
the originating and following trace. This can be used when a **Trace** enters trusted
boundaries of a service and service policy requires the generation of a new
Trace rather than trusting the incoming Trace context. The new linked Trace may
also represent a long running asynchronous data processing operation that was
initiated by one of many fast incoming requests.

When using the scatter/gather (also called fork/join) pattern, the root
operation starts multiple downstream processing operations and all of them are
aggregated back in a single **Span**. This last **Span** is linked to many
operations it aggregates. All of them are the **Spans** from the same Trace. And
similar to the Parent field of a **Span**. It is recommended, however, to not
set parent of the **Span** in this scenario as semantically the parent field
represents a single parent scenario, in many cases the parent **Span** fully
encloses the child **Span**. This is not the case in scatter/gather and batch
scenarios.

## Metric Signal

OpenTelemetry allows to record raw measurements or metrics with predefined
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

Metrics data model is [specified here](metrics/datamodel.md) and is based on
[metrics.proto](https://github.com/open-telemetry/opentelemetry-proto/blob/master/opentelemetry/proto/metrics/v1/metrics.proto).
This data model defines three semantics: An Event model used by the API, an
in-flight data model used by the SDK and OTLP, and a TimeSeries model which
denotes how exporters should interpret the in-flight model.

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

See [Metrics Data Model Specification](metrics/datamodel.md) for more
information.

## Log Signal

### Data model

[Log Data Model](logs/data-model.md) defines how logs and events are understood by
OpenTelemetry.

## Baggage Signal

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
instrumented by OpenTelemetry or other monitoring/tracing libraries (Jaeger,
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
