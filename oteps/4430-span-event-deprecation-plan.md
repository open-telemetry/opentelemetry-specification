# Span event deprecation plan

## Motivation

[OTEP 265: Event Vision](0265-event-vision.md) states that we intend to
deprecate span events in favor of (log-based) events.

Span events and log-based events both capture point-in-time telemetry.
However, span events are limited because they need tracing instrumentation
and can only be reported when a recording span ends.
While both serve similar purposes, log-based events support a wider range of
use cases.

As we look at the current usage of span events though, by far the most common
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

## Prerequisites

The prerequisites for deprecating span events in the specification:

- The (log-based) event specification has been stabilized
  ([#4362](https://github.com/open-telemetry/opentelemetry-specification/issues/4362)).
- There is [stable](../specification/versioning-and-stability.md#stable)
  support for (log-based) events in the relevant SDK.
- The [backcompat story](#backcompat-story) exists (and is stable)
  in the relevant SDK.

## The plan

### Proto and specification

1. Introduce and stabilize Span SetException in the specification.

   This will allow recording span-terminating exceptions directly as span
   attributes, instead of recording them as span events.

   Stabilization will go through the normal process, requiring prototypes
   in at least three languages.

2. Stabilize (log-based) events in the proto and specification.

   This will allow recording events using the Logs API, instead of recording
   them as span events.

   This can be done in parallel with 1.

3. Deprecate
   [Span RecordException](../specification/trace/api.md#record-exception),
   recommending instead that span-terminating exceptions are recorded directly
   as span attributes via a new Span function "SetException", and recommending
   that other exceptions are recorded using the Logs API.

4. Deprecate [Span AddEvent](../specification/trace/api.md#add-events),
   recommending instead that events are recorded using the Logs (Events) API.

   This can be done in parallel with 3.

5. Deprecate span events in the proto, recommending the replacements mentioned
   in 3 and 4 above.

### Per SDK

1. Implement and stabilize Span SetException and (log-based) events.

2. Implement the two SDK-based backcompat stories below:

   - [Emitting span-terminating exceptions as span events](#emitting-span-terminating-exceptions-as-span-events-via-the-sdk)
   - [Emitting (log-based) events as span events](#emitting-log-based-events-as-span-events-via-the-sdk)

3. Deprecate
   [Span RecordException](../specification/trace/api.md#record-exception),
   recommending instead that span-terminating exceptions are recorded directly
   as span attributes via a new Span function "SetException", and recommending
   that other exceptions are recorded using the Logs API.

4. Deprecate [Span AddEvent](../specification/trace/api.md#add-events),
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
  - Users will be able to retain the old behavior by opting in to the
    [backcompat story](#backcompat-story).

Non-stable instrumentations SHOULD use their best judgement on whether to follow
the above guidance.

## Backcompat story

### Emitting span-terminating exceptions as span events via the SDK

This mechanism SHOULD be implemented as follows:

- An SDK-based span processor that converts span-terminating exceptions
  recorded as span attributes into span events.
- A standard way to add this span processor via declarative configuration
  (assuming its package has been installed).

Additionally, this span processor SHOULD be included in the standard
OpenTelemetry zero-code distribution (if one exists for the language)
for at least 1 year.

### Emitting (log-based) events as span events via the SDK

This mechanism SHOULD be implemented as follows (see
[prototype](https://github.com/open-telemetry/opentelemetry-java-contrib/blob/80adbe1cf8de647afa32c68f921aef2bbd4dfd71/processors/README.md#event-to-spanevent-bridge)):

- An SDK-based log processor that converts event records to span events
  and attaches them to the current span, whose behavior and configuration
  are defined in the OpenTelemetry Specification.
- A standard way to add this log processor via declarative configuration
  (assuming its package has been installed).

Additionally, this log processor SHOULD be included in the standard
OpenTelemetry zero-code distribution (if one exists for the language)
for at least 1 year.

### Emitting span-terminating exceptions as span events via the Collector

This mechanism SHOULD be implemented as follows:

- A Collector-based span processor that converts span-terminating exceptions
  recorded as span attributes into span events.

Additionally, this log processor SHOULD be included in the standard
OpenTelemetry Collector Contrib distribution for at least 1 year.

## Communication plan

Publish a blog post if/when this OTEP is accepted, giving readers a way to
provide feedback (e.g. pointing to a specification issue where we are
gathering feedback).

## Future possibilities

- An SDK-based log processor that converts all log records (not only event
  records) to span events and attaches them to the current span.
- An opt-in mechanism in the tracing SDK that allows users to emit span events
  as (log-based) events. This would only be a short-term solution until
  existing instrumentations are updated to emit (log-based) events.
