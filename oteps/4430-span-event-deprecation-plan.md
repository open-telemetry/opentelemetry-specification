# Span event deprecation plan

## Motivation

As stated in [OTEP 265: Event Vision](0265-event-vision.md),
the long-term plan is to deprecate span events in favor of
(log-based) events.

Since there are some backends that only support tracing and have no plans to
ingest log-based events directly, this statement has caused concern and worry
since there are no further details in that OTEP about how the deprecation
will work and whether these backends' needs will still be met by OpenTelemetry.

This OTEP lays out some requirements around the deprecation plan
to reduce confusion and hopefully alleviate these worries.

## Prerequisites

The prerequisites for the deprecation plan are:

- The event specification has been stabilized.
- There is [stable](../specification/versioning-and-stability.md#stable)
  support for (log-based) events in the relevant SDK.
- The [opt-in mechanism to emit (log-based) events
  as span events](#emitting-log-based-events-as-span-events)
  exists (and is stable) in the relevant SDK.

## Deprecation plan by component

### Proto

Span events SHOULD be marked as deprecated in the proto definitions,
recommending that people use (log-based) events instead. Per
[OpenTelemetry proto stability rules](https://github.com/open-telemetry/opentelemetry-proto/blob/main/README.md#stability-definition)
span events MUST NOT be removed from the proto.

### Span event API

The [Span AddEvent](../specification/trace/api.md#add-events) API
SHOULD be marked as
[deprecated](../specification/versioning-and-stability.md#deprecated),
recommending that people use the OpenTelemetry Logs (Events) API instead.
The default behavior of this method MUST NOT change.

The [Span AddEvent](../specification/trace/api.md#add-events) API
MAY only be [removed](../specification/versioning-and-stability.md#removed)
if the API (ever) bumps the major version
and the [opt-in mechanism to emit (log-based) events
as span events](#emitting-log-based-events-as-span-events)
does not rely on its presence.

The [Span RecordException](../specification/trace/api.md#record-exception) API
SHOULD be marked as
[deprecated](../specification/versioning-and-stability.md#deprecated),
recommending that people use the OpenTelemetry Logs API instead.
The default behavior of this method MUST NOT change.

The [Span RecordException](../specification/trace/api.md#record-exception) API
MAY only be [removed](../specification/versioning-and-stability.md#removed)
if the API (ever) bumps the major version
and the [opt-in mechanism to emit (log-based) events
as span events](#emitting-log-based-events-as-span-events)
does not rely on its presence.

### Tracing SDK

The tracing SDK SHOULD provide an opt-in mechanism that allows
users to emit span events as (log-based) events.

This would be a short-term solution until existing instrumentations are
updated to emit (log-based) events.

### Instrumentation

For [stable](../specification/versioning-and-stability.md#stable)
instrumentations that are emitting span events:

- In the instrumentation's current major version
  - It SHOULD continue to emit span events.
- In the instrumentation's next major version
  - It SHOULD stop emitting span events and only emit log-based events.
    Users will be able to continue receiving span events by using the
    [opt-in mechanism to emit (log-based) events
    as span events](#emitting-log-based-events-as-span-events).

Non-stable instrumentations SHOULD use their best judgement on whether to follow
the above guidance.

## Emitting (log-based) events as span events

There are some backends that only support tracing and have no plans
to ingest log-based events.

To support this use case, there SHOULD be an opt-in mechanism that allows
users to emit log-based events as span events.

This opt-in mechanism SHOULD NOT be removed, even in a major version bump.

This mechanism SHOULD be implemented as follows (see
[prototype](https://github.com/open-telemetry/opentelemetry-java-contrib/blob/80adbe1cf8de647afa32c68f921aef2bbd4dfd71/processors/README.md#event-to-spanevent-bridge)):

- A log processor that converts event records to span events and attaches them
  to the current span, whose behavior and configuration are defined
  in the OpenTelemetry Specification.
- A standard way to add this log processor via declarative configuration
  (assuming its package has been installed).

Additionally, this log processor SHOULD be included in the standard
OpenTelemetry zero-code distribution (if one exists for the language).
