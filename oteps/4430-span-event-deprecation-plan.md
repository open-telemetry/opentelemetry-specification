# Span event deprecation plan

## Motivation

[OTEP 265: Event Vision](0265-event-vision.md) states that we intend to
deprecate span events in favor of (log-based) events.

After further discussions, we are only planning to deprecate the Span Event
API, while retaining the ability to emit Span Events via the Events API.

This achieves the primary goal, which is to provide a single consistent
guidance to instrumentation authors to use the Event API, while still
enabling use cases that rely on Span Events being emitted in the same proto
envelope as their containing Span.

Further, as we look at the current usage of span events across OpenTelemetry
repositories though, by far the most common
use is for recording span-terminating exceptions, and it will be much less
disruptive to record these span-terminating exceptions directly as span
attributes (since there is only ever at most one of these) compared to
recording them using the Logs API:

- It is _much_ simpler to build a backcompat collector processor that moves
  span-terminating exceptions from span attributes to a span event,
  compared to buffering spans and moving these span-terminating exceptions
  over to the appropriate span.
- Some backends only support tracing and have no current plans to ingest
  log-based events directly.

## The plan

### Specification

1. Introduce and stabilize Span SetException in the specification.

   This will allow recording span-terminating exceptions directly as span
   attributes, instead of recording them as span events.

   Stabilization will go through the normal process, requiring prototypes
   in at least three languages.

2. Stabilize (log-based) events in the proto and specification.

   This will allow recording events using the Logs API, instead of recording
   them as span events.

   This can be done in parallel with 1.

3. Mark [Span RecordException](../specification/trace/api.md#record-exception)
   as [Deprecated](../specification/document-status.md#lifecycle-status),
   recommending instead that span-terminating exceptions are recorded directly
   as span attributes via a new Span function "SetException", and recommending
   that other exceptions are recorded using the Logs API.

4. Mark [Span AddEvent](../specification/trace/api.md#add-events)
   as [Deprecated](../specification/document-status.md#lifecycle-status),
   recommending instead that events are recorded using the Logs (Events) API.

   This can be done in parallel with 3.

### Per SDK

1. Implement and stabilize Span SetException and (log-based) events.

2. Implement the two SDK-based backcompat stories below:

   - [Emitting (log-based) events as span events](#emitting-log-based-events-as-span-events)
   - [Backcompat story for span-terminating exceptions](#backcompat-story-for-span-terminating-exceptions)

3. Mark
   [Span RecordException](../specification/trace/api.md#record-exception)
   as [Deprecated](../specification/document-status.md#lifecycle-status),
   recommending instead that span-terminating exceptions are recorded directly
   as span attributes via a new Span function "SetException", and recommending
   that other exceptions are recorded using the Logs API.

4. Mark [Span AddEvent](../specification/trace/api.md#add-events)
   as [Deprecated](../specification/document-status.md#lifecycle-status),
   recommending instead that events are recorded using the Logs (Events) API.

   This can be done in parallel with 3.

### Per Instrumentation

For [stable](../specification/versioning-and-stability.md#stable)
instrumentations that are emitting span events:

- In the instrumentation's current major version
  - It SHOULD continue to emit span events
    (continuing to call
    [Span RecordException](../specification/trace/api.md#record-exception)
    and [Span AddEvent](../specification/trace/api.md#add-events))
- In the instrumentation's next major version
  - It SHOULD stop emitting span events
    (instead calling Span "SetException" for span-terminating exceptions
    and calling the Logs API for all other use cases).
  - Users will be able to retain the old behavior by opting in to
    - [Emitting (log-based) events as span events](#emitting-log-based-events-as-span-events), and
    - [Backcompat story for span-terminating exceptions](#backcompat-story-for-span-terminating-exceptions)

Non-stable instrumentations SHOULD use their best judgement on whether to follow
the above guidance.

## Emitting (log-based) events as span events

### Via the SDK

This mechanism SHOULD be implemented as follows (see
[prototype](https://github.com/open-telemetry/opentelemetry-java-contrib/blob/80adbe1cf8de647afa32c68f921aef2bbd4dfd71/processors/README.md#event-to-spanevent-bridge)):

- An SDK-based log processor that converts event records to span events
  and attaches them to the current span, whose behavior and configuration
  are defined in the OpenTelemetry Specification.
- A standard way to add this log processor via declarative configuration
  (assuming its package has been installed).

Users can choose to register a log exporter depending on if they also want
to export event records as logs or not.

This log processor SHOULD be included in the standard
OpenTelemetry zero-code distribution (if one exists for the language).

### Via the Collector

This mechanism SHOULD be implemented as follows:

- A Collector-based span processor that converts span-terminating exceptions
  recorded as span attributes into span events.

This log processor SHOULD be included in the standard
OpenTelemetry Collector Contrib distribution.

## Backcompat story for span-terminating exceptions

This mechanism SHOULD be implemented as follows:

- An SDK-based span processor that converts span-terminating exceptions
  recorded as span attributes into span events
  (with the option to either drop or retain the span-terminating exception
  span attributes).
- A standard way to add this span processor via declarative configuration
  (assuming its package has been installed).

This span processor SHOULD be included in the standard
OpenTelemetry zero-code distribution (if one exists for the language).

## Communication plan

Publish a blog post if/when this OTEP is accepted, giving readers a way to
provide feedback (e.g. pointing to a specification issue where we are
gathering feedback). The blog post should include the rationale for the
decision to deprecate span events.

## Nice to haves

- Make [emitting span-terminating exceptions as span events via the
  Collector](#emitting-span-terminating-exceptions-as-span-events-via-the-collector)
  a prerequisite for stabilizing Span SetException in any SDK.
- Forward compatibility story: A collector-based span processor that infers
  if a span event represents a span-terminating exception, and adds it
  directly as span attributes
  (with the option to either drop or retain the span event).
