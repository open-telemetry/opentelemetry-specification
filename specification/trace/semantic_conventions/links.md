# Semantic Conventions for Links

**Status**: [Experimental](../../document-status.md)

This document defines semantic conventions for recording soft
links.

<!-- toc -->

- [Recording a Link](#recording-a-link)
- [Attributes](#attributes)

<!-- tocstop -->

## Recording a Link

A `Link` SHOULD be recorded as an `Event` on the span during which it occurred.
The name of the event MUST be `"link"`.

A typical template for an instrumentation implementing this semantic convention
using an [API-provided `recordLink` method](../api.md#record-link)
could look like this (pseudo-Java):

```java
Span span = myTracer.startSpan(/*...*/);
// Code that does actual work which the Span represents.

SpanContext producerSpanContext = getProducerSpanContext();
span.recordLink(producerSpanContext, Attributes.of("messaging.source.kind", "queue"));
```

## Attributes

The table below indicates which attributes should be added to the `Event` and
their types.

<!-- semconv trace-link -->
The event name MUST be `link`.

| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `link.traceid` | string | The lowercase hex encoded trace id, as [retrieved](../api.md#retrieving-the-traceid-and-spanid) by `SpanContext`. | `af9d5aa4-a685-4c5f-a22b-444f80b3cc28` | Recommended |
| `link.spanid` | string | The lowercase hex encoded span id, as [retrieved](../api.md#retrieving-the-traceid-and-spanid) by `SpanContext`. | `af9d5aa4-a685-4c5f-a22b-444f80b3cc28` | Recommended |
| `link.tracestate` | string | The trace state, as specified in the [API](../api.md#tracestate). | `congo=t61rcWkgMzE` | Recommended |
<!-- endsemconv -->
