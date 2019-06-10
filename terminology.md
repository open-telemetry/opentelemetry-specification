# Terminology

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

For example, the following is an example **Trace** made up of 8 **Spans**:

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
- **TraceOptions** represents the options for a trace. It is represented as 1
  byte (bitmap).
  - Sampling bit -  Bit to represent whether trace is sampled or not (mask
    `0x1`).
- **Tracestate** carries tracing-system specific context in a list of key value
  pairs. **Tracestate** allows different vendors propagate additional
  information and inter-operate with their legacy Id formats. For more details
  see [this][https://w3c.github.io/trace-context/#tracestate-field].

### Links between spans

A **Span** may be linked to zero or more other **Spans** (defined by
**SpanContext**) that are causally related. **Links** can point to
**SpanContexts** inside a single **Trace** or across different **Traces**.
**Links** can be used to represent batched operations where a **Span** has
multiple parents, each representing a single incoming item being processed in
the batch. Another example of using a **Link** is to declare relationship
between originating and restarted trace. This can be used when **Trace** enters
trusted boundaries of an service and service policy requires to generate a new
Trace instead of trusting incoming Trace context. 

## Metrics

TODO: Describe metrics terminology https://github.com/open-telemetry/opentelemetry-specification/issues/45

## Tags

TODO: Describe tags terminology https://github.com/open-telemetry/opentelemetry-specification/issues/46

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

## Agent/Collector

The OpenTelemetry service is a set of components that can collect traces,
metrics and eventually other telemetry data (e.g. logs) from processes
instrumented by OpenTelementry or other monitoring/tracing libraries (Jaeger,
Prometheus, etc.), do aggregation and smart sampling, and export traces and
metrics to one or more monitoring/tracing backends. The service will allow to
enrich and transform collected telemetry (e.g. add additional attributes or
scrab personal information).

The OpenTelemetry service has two primary modes of operation: Agent (a locally
running daemon) and Collector (a standalone running service).

Read more at OpenTelemetry Service [Long-term
Vision](https://github.com/open-telemetry/opentelemetry-service/blob/master/docs/VISION.md).

## Instrumentation adapters

The inspiration of the project is to make every library and application
manageable out of the box by instrumenting it with OpenTelemery. However on the
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
