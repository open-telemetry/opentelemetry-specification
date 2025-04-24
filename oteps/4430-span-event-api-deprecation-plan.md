# Span Event API deprecation plan

## Motivation

[OTEP 265: Event Vision](0265-event-vision.md) states that we intend to
deprecate Span Events in favor of (log-based) Events.

After further discussions, we are only planning to deprecate the Span Event
API, while retaining the ability to emit Span Events via the Logs API.

This achieves the primary goal of deprecation, which is to provide a single
consistent guidance to instrumentation authors to use the Logs API when
emitting events, while still supporting use cases that rely on Span Events
being emitted in the same proto envelope as their containing span.

## The plan

### In the proto

Stabilize (log-based) Events.

### In the Specification

1. Stabilize emitting exceptions and events via the Logs API.

   This will allow recording exceptions and events using the Logs API,
   instead of recording them using the Span Event API.

   Note: emitting exceptions via the Logs API is
   [already stable](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/exceptions/exceptions-logs.md#semantic-conventions-for-exceptions-in-logs),
   but there are a couple of open questions that need to be addressed:

   - Do we want to specify some kind of convenience function on Logs
     similar to RecordException?
   - Do we want to recommend that log-based exceptions do anything
     specific with the event name field?

2. Mark [Span RecordException](../specification/trace/api.md#record-exception)
   as [Deprecated](../specification/document-status.md#lifecycle-status),
   recommending instead that exceptions are recorded using the Logs API.

3. Mark [Span AddEvent](../specification/trace/api.md#add-events)
   as [Deprecated](../specification/document-status.md#lifecycle-status),
   recommending instead that events are recorded using the Logs API.

   This can be done in parallel with 2.

### Per API and SDK

1. Implement and stabilize emitting exceptions and events via the Logs API.

2. Implement the SDK-based backcompat story:

   - [Sending (log-based) exceptions and Events as Span Events](#via-the-sdk)

3. Mark
   [Span RecordException](../specification/trace/api.md#record-exception)
   as [Deprecated](../specification/document-status.md#lifecycle-status),
   recommending instead that exceptions are recorded using the Logs API.

4. Mark [Span AddEvent](../specification/trace/api.md#add-events)
   as [Deprecated](../specification/document-status.md#lifecycle-status),
   recommending instead that events are recorded using the Logs API.

   This can be done in parallel with 3.

### Per Instrumentation

For [stable](../specification/versioning-and-stability.md#stable)
instrumentations that are using
[Span RecordException](../specification/trace/api.md#record-exception)
and [Span AddEvent](../specification/trace/api.md#add-events):

- In the instrumentation's current major version
  - It SHOULD continue to use these
- In the instrumentation's next major version
  - It SHOULD stop using these,
    instead recording exceptions and events using the Logs API.
  - Users will be able to retain the prior telemetry output by opting in to
    [Sending (log-based) Events as Span Events](#sending-log-based-events-as-span-events)
  - In case the instrumentation was using span events previously to record
    additional details about a span (i.e. details that don't need a timestamp),
    it SHOULD instead record these details as attributes on the span. See
    [semantic-conventions#2010](https://github.com/open-telemetry/semantic-conventions/issues/2010)
    and
    [opentelemetry-specification#4446](https://github.com/open-telemetry/opentelemetry-specification/issues/4446)
    for more details about this case.

Non-stable instrumentations SHOULD use their best judgement on whether to follow
the above guidance.

## Sending (log-based) exceptions and Events as Span Events

### Via the SDK

There MUST be a way to send (log-based) exceptions and Events as Span Events
for use cases that rely on Span Events being emitted in the
same proto envelope as their containing span, and for users
who need to preserve the prior behavior when updating to
new instrumentation.

This mechanism SHOULD be implemented as follows (see
[prototype](https://github.com/open-telemetry/opentelemetry-java-contrib/blob/80adbe1cf8de647afa32c68f921aef2bbd4dfd71/processors/README.md#event-to-spanevent-bridge)):

- An SDK-based log processor that converts exception and Event records to Span Events
  and attaches them to the current span, whose behavior and configuration
  are defined in the OpenTelemetry Specification.
- A standard way to add this log processor via declarative configuration
  (assuming its package has been installed).

Users can add a batch log record processor and log exporter depending on
if they also want to export exception and Event records as logs or not.

This log processor SHOULD be included in the standard
OpenTelemetry zero-code distribution (if one exists for the language).

### Via the Collector

Note: this is a nice-to-have only and not required for any other part
of the Span Event API deprecation plan.

This mechanism MAY be implemented as follows:

- A Collector-based processor that buffers spans and moves (log-based)
  Events to the appropriate span.

This log processor MAY be included in the standard
OpenTelemetry Collector Contrib distribution.

## Communication plan

Publish a blog post if/when this OTEP is accepted, giving readers a way to
provide feedback (e.g. pointing to a specification issue where we are
gathering feedback). The blog post should include the rationale for the
decision to deprecate the Span Event API.
