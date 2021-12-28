# CloudEvents

**Status**: [Experimental](../../document-status.md)

This specification defines semantic conventions for [CloudEvents](https://cloudevents.io/).
It covers creation, processing and context propagation between producer and consumer.
It does not cover transport aspects of publishing and receiving cloud events.

## Overview

To be individually traceable, each CloudEvent has to have its own trace context.
The trace context is populated in the event using the
[CloudEvents Distributed Tracing Extension](https://github.com/cloudevents/spec/blob/v1.0.1/extensions/distributed-tracing.md).

Once the trace context is set on the event, it MUST not be modified.

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [Spans](#spans)
  * [Creation](#creation)
  * [Processing](#processing)
- [Attributes](#attributes)

<!-- tocstop -->

## Spans

### Creation

Instrumentation SHOULD create a new span and populate the
[CloudEvents Distributed Tracing Extension](https://github.com/cloudevents/spec/blob/v1.0.1/extensions/distributed-tracing.md)
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

**Span name:** `CloudEvents Create <event_type>`

**Span kind:** PRODUCER

### Processing

When an instrumented library supports processing of a single CloudEvent,
instrumentation SHOULD create a new span to trace it.

Instrumentation SHOULD set the remote trace context from the
Distributed Tracing Extension as a link on the processing span.

**Span name:** `CloudEvents Process <event_type>`

**Span kind:** CONSUMER

## Attributes

The following attributes are applicable to creation and processing Spans.

<!-- semconv cloudevents -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `cloudevents.event_id` | string | The [event_id](https://github.com/cloudevents/spec/blob/v1.0.1/spec.md#id) uniquely identifies the event. | `123e4567-e89b-12d3-a456-426614174000`; `0001` | No |
| `cloudevents.event_source` | string | The [source](https://github.com/cloudevents/spec/blob/v1.0.1/spec.md#source-1) identifies the context in which an event happened. | `https://github.com/cloudevents`; `/cloudevents/spec/pull/123`; `my-service` | No |
| `cloudevents.event_spec_version` | string | The [version of the CloudEvents specification](https://github.com/cloudevents/spec/blob/v1.0.1/spec.md#specversion) which the event uses. | `1.0` | No |
| `cloudevents.event_type` | string | The [event_type](https://github.com/cloudevents/spec/blob/v1.0.1/spec.md#type) contains a value describing the type of event related to the originating occurrence. | `com.github.pull_request.opened`; `com.example.object.deleted.v2` | No |
| `cloudevents.event_subject` | string | The [subject](https://github.com/cloudevents/spec/blob/v1.0.1/spec.md#subject) of the event in the context of the event producer (identified by source). | `mynewfile.jpg` | No |
<!-- endsemconv -->
