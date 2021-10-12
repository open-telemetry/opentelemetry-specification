# Trace Data Model

**Status**: [Mixed](../document-status.md)

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [Overview](#overview)
- [Glossary](#glossary)
  * [Trace](#trace)
  * [Span](#span)
  * [Root span](#root-span)
  * [Context](#context)
  * [Span context](#span-context)
  * [Trace flags](#trace-flags)
  * [Tracestate](#tracestate)
- [Span fields](#span-fields)
  * [TraceID](#traceid)
  * [SpanID](#spanid)
  * [TraceState](#tracestate)
  * [ParentSpanID](#parentspanid)
  * [Name](#name)
  * [SpanKind](#spankind)
  * [StartTimeUnixNano](#starttimeunixnano)
  * [EndTimeUnixNano](#endtimeunixnano)
  * [Attributes](#attributes)
  * [Events](#events)
  * [Links](#links)
  * [Status](#status)

<!-- tocstop -->

## Overview

**Status**: [Stable](../document-status.md)

The OpenTelemetry data model for tracing consists of a protocol
specification for encoding spans, which represent an individual unit
of work done in a distributed system.

## Glossary

### Trace

A trace is comprised of a number of spans, connected with each other
through parent-child relationships, that describes a unit of work in a
distributed system.

### Span

Each component in a distributed system contributes a span
corresponding to a named operation, representing its part in the
overall, distributed unit of work.

### Root span

A root span is the span that initiates a unit of work in a distributed
system.  The root span is considered to have caused all the subsequent
spans belonging to the trace.

### Context

OpenTelemetry defines [Context](../context/context.md) as a means of
passing values for use in telemetry across program execution
boundaries.

### Span context

Span context is the portion of the OpenTelemetry Context that makes up
the tracing data model.  This is specified by reference to the [W3C
trace context](https://www.w3.org/TR/trace-context/) specification,
which defines four parts of the span context:

1. TraceID
2. SpanID
3. Trace flags
4. Tracestate

The first three of these fields are included in the W3C trace context
[`traceparent`](https://www.w3.org/TR/trace-context/#traceparent-header)
header.

### Trace flags

The W3C trace context defines one flag at present, `sampled`, which
OpenTelemetry uses to make sampling decisions based on the context.

### Tracestate

The W3C trace context defines a field known as
[`tracestate`](https://www.w3.org/TR/trace-context/#tracestate-header)
which enables extending the context with vendor-specific information.

## Span fields

### TraceID

**Status**: [Stable](../document-status.md)

The OpenTelemetry TraceID is defined to be equivalent to the W3C trace
context `trace-id` field, consisting of 128-bits of information and
assigned to the new trace when starting a root span.

### SpanID

**Status**: [Stable](../document-status.md)

The OpenTelemetry SpanID is defined to identify the span that is the
parent of a new trace context, equivalent to the W3C trace context
`parent-id` identifier in the context of a new span, consisting of
64-bits of informaiton.

### TraceState

**Status**: [Stable](../document-status.md)

The OpenTelemetry Span encodes the `tracestate` that was computed when
the Span started.

### ParentSpanID

**Status**: [Stable](../document-status.md)

The OpenTelemetry Span contains a ParentSpanID field which for
non-root spans refers to the W3C `parent-id` identifiers that was in
the trace context when it started (i.e., it is the SpanID of the
parent span for non-root spans).

### Name

**Status**: [Stable](../document-status.md)

The OpenTelemetry Span name is a short, human-readable description of
the work performed within the span's context.

### SpanKind

TODO(issue #1929): complete the span data model text.

### StartTimeUnixNano

TODO(issue #1929): complete the span data model text.

### EndTimeUnixNano

TODO(issue #1929): complete the span data model text.

### Attributes

TODO(issue #1929): complete the span data model text.

Define dropped_attributes_count here.

### Events

TODO(issue #1929): complete the span data model text.

Define dropped_events_count here.

### Links

TODO(issue #1929): complete the span data model text.

Define dropped_links_count here.

### Status

TODO(issue #1929): complete the span data model text.
