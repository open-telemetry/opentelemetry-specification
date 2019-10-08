# Overview

## Distributed Tracing

A distributed trace is a set of events, triggered as a result of a single
logical operation, consolidated across various components of an application. A
distributed trace contains events that cross process, network and security
boundaries. A distributed trace may be initiated when someone presses a button
to start an action on a website - in this example, the trace will represent
calls made between the downstream services that handled the chain of requests
initiated by this button being pressed.

### Trace

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

### Span

Each **Span** encapsulates the following state:

- An operation name
- A start and finish timestamp
- A set of zero or more key:value **Attributes**. The keys must be strings. The
  values may be strings, bools, or numeric types.
- A set of zero or more **Events**, each of which is itself a key:value map
  paired with a timestamp. The keys must be strings, though the values may be of
  the same types as Span **Attributes**.
- Parent's **Span** identifier.
- [**Links**](#links-between-spans) to zero or more causally-related **Spans**
  (via the **SpanContext** of those related **Spans**).
- **SpanContext** identification of a Span. See below.

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
**SpanContexts** inside a single **Trace** or across different **Traces**.
**Links** can be used to represent batched operations where a **Span** was
initiated by multiple initiating **Span**s, each representing a single incoming
item being processed in the batch. Another example of using a **Link** is to
declare relationship between originating and followed trace. This can be used
when **Trace** enters trusted boundaries of a service and service policy
requires to generate a new Trace instead of trusting incoming Trace context. Or
when long running Trace representing asynchronous data processing operation was
initiated by one of many fast incoming request.

In case of scatter/gather pattern, when the root operation starts multiple
downstream processing operations and all of them being aggregated back in a
single **Span**, this last **Span** is linked to many operations it
aggregates. All of them are the **Span**s from the same Trace. And similar to
the Parent field of a **Span**. It is recommended, however, to not set parent of
the **Span** in this scenario as semantically parent field represents a single
parent scenario, in many cases parent **Span** fully encloses the child
**Span**. Which is not the case in scatter/gather and batch scenarios.

## Metrics

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

OpenTelemetry defines the naming convention for metric names as well as a
well-known metric names in [Semantic Conventions](data-semantic-conventions.md)
document.

## DistributedContext

The **DistributedContext** exists to store labels that describe the context of an operation an application performs. It is intended to enable context that are custom to the application or integrations in contrast to other contexts, such as `SpanContext`. Only one **DistributedContext** should be associated with any particular operation.

For example, a web service can benefit from including context around what service has sent the request. Or a SaaS provider can include context about the API user or token that is responsible for that request. These values can be consumed from **DistributedContext** and used as an additional dimension for a metric, or additional context for logs and traces.

**DistributedContext** is a collection of key-value `Entry` pairs, with each key of associated with exactly one value. **DistributedContext** is serializable,
to facilitate propagating it not only inside the process but also across process boundaries.

**DistributedContext** is a recommended name but languages can have more language-specific names like **dctx**.

### Entry

An **Entry** is used to represent the labels that are contained inside the `DistributedContext`, representing values such as the service that originated the request, or vendor-specific data. It consists of an **EntryKey**, an **EntryValue** and an **EntryMetadata**.

- **EntryKey** is the name of the **Entry**. **EntryKey** along with **EntryValue**
can be used to aggregate and group stats, annotate traces and logs, etc. **EntryKey** is
a string that contains only printable ASCII (codes between 32 and 126 inclusive) and with
a length greater than zero and less than 256.
- **EntryValue** is a string that contains only printable ASCII (codes between 32 and 126).
- **EntryMetadata** contains properties associated with an **Entry**.
For now only the property **EntryTTL** is defined.
- **EntryTTL** is an integer that represents number of hops an entry can propagate.
Anytime a sender serializes an entry, sends it over the wire and a receiver deserializes
the entry then the entry is considered to have travelled one hop.

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

**TODO**: Better describe the difference between the resource and a Node
https://github.com/open-telemetry/opentelemetry-proto/issues/17

## Propagators

OpenTelemetry uses `Propagators` to serialize and deserialize `SpanContext` and `DistributedContext`
into a binary or text format. Currently there are two types of propagators:

- `BinaryFormat` which is used to serialize and deserialize a value into a binary representation.
- `HTTPTextFormat` which is used to inject and extract a value as text into carriers that travel
in-band across process boundaries.

## Agent/Collector

The OpenTelemetry service is a set of components that can collect traces,
metrics and eventually other telemetry data (e.g. logs) from processes
instrumented by OpenTelementry or other monitoring/tracing libraries (Jaeger,
Prometheus, etc.), do aggregation and smart sampling, and export traces and
metrics to one or more monitoring/tracing backends. The service will allow to
enrich and transform collected telemetry (e.g. add additional attributes or
scrub personal information).

The OpenTelemetry service has two primary modes of operation: Agent (a locally
running daemon) and Collector (a standalone running service).

Read more at OpenTelemetry Service [Long-term
Vision](https://github.com/open-telemetry/opentelemetry-service/blob/master/docs/vision.md).

## Instrumentation adapters

The inspiration of the project is to make every library and application
manageable out of the box by instrumenting it with OpenTelemetry. However on the
way to this goal there will be a need to enable instrumentation by plugging
instrumentation adapters into the library of choice. These adapters can be
wrapping library APIs, subscribing to the library-specific callbacks or
translating telemetry exposed in other formats into OpenTelemetry model.

Instrumentation adapters may be called different names. It is often referred as
plugin, collector or auto-collector, telemetry module, bridge, etc. It is always
recommended to follow the library and language standards. For instance, if
instrumentation adapter is implemented as "log appender" - it will probably be
called an `appender`, not an instrumentation adapter. However if there is no
established name - the recommendation is to call packages "Instrumentation
Adapter" or simply "Adapter".

## Code injecting adapters

TODO: fill out as a result of SIG discussion.
