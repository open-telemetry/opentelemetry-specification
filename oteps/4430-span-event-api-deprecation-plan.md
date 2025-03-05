# Span Event API deprecation plan

## Motivation

[OTEP 265: Event Vision](0265-event-vision.md) states that we intend to
deprecate Span Events in favor of (log-based) Events.

After further discussions, we are only planning to deprecate the Span Event
API, while retaining the ability to emit Span Events via the (log-based)
Event API.

This achieves the primary goal of deprecation, which is to provide a single
consistent guidance to instrumentation authors to use the Event API,
while still supporting use cases that rely on Span Events being emitted in the
same proto envelope as their containing span.

## Span-terminating exceptions

As we look at the current usage of Span Events across OpenTelemetry
repositories, by far the most common use is for recording span-terminating
exceptions.

This OTEP proposes to record span-terminating exceptions directly as span
attributes (since there is only ever at most one of them on a span) instead
of recording them via the (log-based) Event API, for the following reasons:

- Span-terminating exceptions are (by their nature) recorded via tracing
  instrumentation and so there is a natural interest to keep them tightly
  coupled to the tracing (span) telemetry.
- It is _much_ simpler to build a backcompat collector processor that moves
  span-terminating exceptions from span attributes to a Span Event,
  compared to buffering spans and moving these span-terminating exceptions
  over to the appropriate span.

## The plan

### In the proto

Stabilize (log-based) Events.

### In the Specification

1. Introduce and stabilize the Span SetException API.

   This will allow recording span-terminating exceptions directly as span
   attributes, instead of recording them as Span Events.

   Stabilization will go through the normal process, requiring prototypes
   in at least three languages.

2. Stabilize the (log-based) Event API.

   This will allow recording events using the (log-based) Event API,
   instead of recording them using the Span Event API.

   This can be done in parallel with 1.

3. Mark [Span RecordException](../specification/trace/api.md#record-exception)
   as [Deprecated](../specification/document-status.md#lifecycle-status),
   recommending instead that span-terminating exceptions are recorded directly
   as span attributes via the new Span SetException API and
   that other exceptions are recorded using the (log-based) Event API.

4. Mark [Span AddEvent](../specification/trace/api.md#add-events)
   as [Deprecated](../specification/document-status.md#lifecycle-status),
   recommending instead that events are recorded using the (log-based) Event
   API.

   This can be done in parallel with 3.

### Per API and SDK

1. Implement and stabilize the Span SetException API and the (log-based)
   Event API.

2. Implement the two SDK-based backcompat stories below:

   - [Sending span-terminating exceptions as Span Events](#via-the-sdk)
   - [Sending (log-based) Events as Span Events](#sending-log-based-events-as-span-events)

3. Mark
   [Span RecordException](../specification/trace/api.md#record-exception)
   as [Deprecated](../specification/document-status.md#lifecycle-status),
   recommending instead that span-terminating exceptions are recorded directly
   as span attributes via the new Span SetException API and
   that other exceptions are recorded using the (log-based) Event API.

4. Mark [Span AddEvent](../specification/trace/api.md#add-events)
   as [Deprecated](../specification/document-status.md#lifecycle-status),
   recommending instead that events are recorded using the (log-based) Event
   API.

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
    instead calling the new Span SetException API for span-terminating exceptions
    and calling the (log-based) Event API for all other use cases.
  - Users will be able to retain the prior telemetry output by opting in to
    - [Sending span-terminating exceptions as Span Events](#sending-span-terminating-exceptions-as-span-events), and
    - [Sending (log-based) Events as Span Events](#sending-log-based-events-as-span-events)

Non-stable instrumentations SHOULD use their best judgement on whether to follow
the above guidance.

## Sending span-terminating exceptions as Span Events

There MUST be a way to send span-terminating exceptions as Span Events
for users who need to preserve the prior behavior when updating to
new instrumentation.

### Via the SDK

This mechanism SHOULD be implemented as follows:

- An SDK-based span processor that converts span-terminating exceptions
  recorded as span attributes into Span Events
  (with the option to either drop or retain the span-terminating exception
  span attributes).
- A standard way to add this span processor via declarative configuration
  (assuming its package has been installed).

This span processor SHOULD be included in the standard
OpenTelemetry zero-code distribution (if one exists for the language).

### Via the Collector

This mechanism SHOULD be implemented as follows:

- A Collector-based span processor that converts span-terminating exceptions
  recorded as span attributes into Span Events.

This log processor SHOULD be included in the standard
OpenTelemetry Collector Contrib distribution.

## Sending (log-based) Events as Span Events

There MUST be a way to send (log-based) Events as Span Events
for use cases that rely on Span Events being emitted in the
same proto envelope as their containing span, and for users
who need to preserve the prior behavior when updating to
new instrumentation.

This mechanism SHOULD be implemented as follows (see
[prototype](https://github.com/open-telemetry/opentelemetry-java-contrib/blob/80adbe1cf8de647afa32c68f921aef2bbd4dfd71/processors/README.md#event-to-spanevent-bridge)):

- An SDK-based log processor that converts Event records to Span Events
  and attaches them to the current span, whose behavior and configuration
  are defined in the OpenTelemetry Specification.
- A standard way to add this log processor via declarative configuration
  (assuming its package has been installed).

Users can add a batch log record processor and log exporter depending on
if they also want to export Event records as logs or not.

This log processor SHOULD be included in the standard
OpenTelemetry zero-code distribution (if one exists for the language).

## Communication plan

Publish a blog post if/when this OTEP is accepted, giving readers a way to
provide feedback (e.g. pointing to a specification issue where we are
gathering feedback). The blog post should include the rationale for the
decision to deprecate the Span Event API.

## Nice to haves

- Make [sending span-terminating exceptions as Span Events via the
  Collector](#via-the-collector)
  a prerequisite for stabilizing Span SetException in SDKs.
- Forward compatibility story: A collector-based span processor that infers
  if a Span Event represents a span-terminating exception, and adds it
  directly as span attributes
  (with the option to either drop or retain the Span Event).
