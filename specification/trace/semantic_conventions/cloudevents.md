# CloudEvents

**Status**: [Experimental](../../document-status.md)

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [Definitions](#definitions)
- [Overview](#overview)
- [Conventions](#conventions)
  * [Spans](#spans)
    + [Creation](#creation)
    + [Processing](#processing)
  * [Attributes](#attributes)

<!-- tocstop -->

## Definitions

 From the
 [CloudEvents specification](https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md#overview):

> CloudEvents is a specification for describing event data in common formats
to provide interoperability across services, platforms and systems.
>

For more information on the concepts, terminology and background of CloudEvents
consult the
[CloudEvents Primer](https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/primer.md)
document.

## Overview

A CloudEvent can be sent directly from producer to consumer.
For such a scenario, the traditional parent-child trace model works well.
However, CloudEvents are also used in distributed systems where an event
can go through many [hops](https://en.wikipedia.org/wiki/Hop_(networking))
until it reaches a consumer. In this scenario, the traditional parent-child
trace model is not sufficient to produce a meaningful trace.

Consider the following scenario:

```
+----------+                  +--------------+
| Producer | ---------------> | Intermediary |
+----------+                  +--------------+
                                     |        
                                     |        
                                     |        
                                     v        
+----------+                    +----------+  
| Consumer | <----------------- |  Queue   |  
+----------+                    +----------+ 
```

With the traditional parent-child trace model, the above scenario would produce
two traces, completely independent from each other because the consumer
starts receiving (and thus has to specify a parent span) before it receives the event.
It is not possible to correlate a producer with a consumer(s) solely via a parent-child relationship.

```
+-------------------------------------------------+
|    Trace 1                                      |
|                                                 |
|    +---------------------------------------+    |
|    | Send (auto-instr)                     |    |
|    +---------------------------------------+    |
|       +------------------------------------+    |
|       | Intermediary: Received (auto-instr)|    |
|       +------------------------------------+    |
|       +------------------------------------+    |
|       | Intermediary: Send (auto-instr)    |    |
|       +------------------------------------+    |
|                                                 |
|    Trace 2                                      |
|                                                 |
|    +---------------------------------------+    |
|    | Consumer: Receive (auto-instr)        |    |
|    +---------------------------------------+    |
|                                                 |
+-------------------------------------------------+
```

This document defines semantic conventions to model the different stages
a CloudEvent can go through in a system, making it possible to create traces
that are meaningful and consistent. It covers creation, processing,
context propagation between producer and consumer(s) and attributes
to be added to spans.

With the proposed model, it is possible to have an overview of everything
that happened as the result of an event. One can, for example, answer the
following questions:

- What components in a system reacted to an event
- What further events were sent due to an incoming event
- Which event caused the exception

With the conventions in this document, the application scenario above would
produce a trace where it is possible to correlate a producer with a consumer(s):

```
+-------------------------------------------------------+
|          Trace 1                                      |
|                                                       |
|          +---------------------------------------+    |
|    +---> | Create event                          |    |
|    |     +---------------------------------------+    |
|    |     +---------------------------------------+    |
|    |     | Send (auto-instr)                     |    |
|    |     +---------------------------------------+    |
|    |        +------------------------------------+    |
|    |        | Intermediary: Received (auto-instr)|    |
|    |        +------------------------------------+    |
|    |        +------------------------------------+    |
|    |        | Intermediary: Send (auto-instr)    |    |
|    |Link    +------------------------------------+    |
|    |                                                  |
|    |                                                  |
|    |                                                  |
|    |     Trace 2                                      |
|    |                                                  |
|    |     +---------------------------------------+    |
|    |     | Consumer: Receive (auto-instr)        |    |
|    |     +---------------------------------------+    |
|    |       +-------------------------------------+    |
|    +------ | Consumer: Process                   |    |
|            +-------------------------------------+    |
|                                                       |
+-------------------------------------------------------+
```

## Conventions

To achieve the trace above, it is necessary to capture the context of
the event creation so that when the CloudEvent reaches its destination(s), this
context can be continued. Each CloudEvent acts then as the medium of this
context propagation.

This document relies on the CloudEvents specification, which defines this
context propagation mechanism via the
[CloudEvents Distributed Tracing Extension](https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/extensions/distributed-tracing.md).
Once the trace context is set on the event
via the Distributed Tracing Extension, it MUST not be modified.

The remainder of this section describes the semantic conventions for Spans
required to achieve the proposed trace.

### Spans

#### Creation

Instrumentation SHOULD create a new span and populate the
[CloudEvents Distributed Tracing Extension](https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/extensions/distributed-tracing.md)
on the event. This applies when:

- A CloudEvent is created by the instrumented library.
It may be impossible or impractical to create the Span during event
creation (e.g. inside the constructor or in a factory method),
so instrumentation MAY create the Span later, when passing the event to the transport layer.
- A CloudEvent is created outside of the instrumented library
(e.g. directly constructed by the application owner, without calling a constructor or factory method),
and passed without the Distributed Tracing Extension populated.

In case a CloudEvent is passed to the instrumented library with the
Distributed Tracing Extension already populated, instrumentation MUST NOT create
a span and MUST NOT modify the Distributed Tracing Extension on the event.

- Span name: `CloudEvents Create <event_type>`

- Span kind: PRODUCER

- Span attributes: Instrumentation MUST add the required attributes defined
in the [table below](#attributes).

#### Processing

When an instrumented library supports processing of a single CloudEvent,
instrumentation SHOULD create a new span to trace it.

Instrumentation SHOULD set the remote trace context from the
Distributed Tracing Extension as a link on the processing span.
Instrumentation MAY add attributes to the link to further describe it.

- Span name: `CloudEvents Process <event_type>`

- Span kind: CONSUMER

- Span attributes: Instrumentation MUST add the required attributes defined
in the [table below](#attributes).

### Attributes

The following attributes are applicable to creation and processing Spans.

<!-- semconv cloudevents -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `cloudevents.event_id` | string | The [event_id](https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md#id) uniquely identifies the event. | `123e4567-e89b-12d3-a456-426614174000`; `0001` | Required |
| `cloudevents.event_source` | string | The [source](https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md#source-1) identifies the context in which an event happened. | `https://github.com/cloudevents`; `/cloudevents/spec/pull/123`; `my-service` | Required |
| `cloudevents.event_spec_version` | string | The [version of the CloudEvents specification](https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md#specversion) which the event uses. | `1.0` | Recommended |
| `cloudevents.event_type` | string | The [event_type](https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md#type) contains a value describing the type of event related to the originating occurrence. | `com.github.pull_request.opened`; `com.example.object.deleted.v2` | Recommended |
| `cloudevents.event_subject` | string | The [subject](https://github.com/cloudevents/spec/blob/v1.0.2/cloudevents/spec.md#subject) of the event in the context of the event producer (identified by source). | `mynewfile.jpg` | Recommended |
<!-- endsemconv -->
