# Context propagation requirements for messaging semantic conventions

The [existing messaging semantic conventions for tracing](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.11.0/specification/trace/semantic_conventions/messaging.md)
implicitly impose certain requirements on context propagation mechanisms used.
This document proposes a way to make these requirements explicit.

This OTEP is based on [OTEP 0173](0173-messaging-semantic-conventions.md),
which defines basic terms and describes messaging scenarios that should be
supported by messaging semantic conventions.

* [Terminology](#terminology)
* [Motivation](#motivation)
  - [Example](#example)
* [Proposed addition to the messaging semantic conventions](#proposed-addition-to-the-messaging-semantic-conventions)
  - [Context propagation](#context-propagation)
  - [Requirements](#requirements)
* [Future possibilities](#future-possibilities)
  - [Transport context propagation](#transport-context-propagation)
  - [Standards for context propagation](#standards-for-context-propagation)

## Terminology

For terms used in this document, refer to [OTEP 173](0173-messaging-semantic-conventions.md#terminology).

## Motivation

The current [messaging semantic conventions for tracing](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.11.0/specification/trace/semantic_conventions/messaging.md)
provide a list of [examples](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.11.0/specification/trace/semantic_conventions/messaging.md#examples).
Those examples illustrate how producer and consumer spans can be correlated by
parent/child relationships or links. All the examples assume that context
information for a given message is propagated from the producer to the
consumer.

However, this is not a trivial assumption, and it is not easily accommodated by
existing established context propagation mechanisms. Those mechanisms propagate
context on a per-request basis, whereas the messaging semantic conventions
assume that context is propagated on a per-message basis. This means, that
although several requests might be involved in the processing of a single
message (publishing a message, fetching a message, potentially multiple times by
multiple consumers), it is assumed that all components have access to the same
per-message context information that allows correlating all the stages of
processing a message.

To achieve this desired outcome, a context needs to be attached to a message,
and intermediaries must not alter the context attached to the message. _This
requirement should be documented, as it is an important factor in deciding how
to propagate context for message scenarios and how to standardize context
propagation for existing message protocols._

The additions proposed in this document neither break nor invalidate any of
the existing semantic conventions for messaging, but rather make an implicit
requirement explicit.

### Example

Many intermediaries (message brokers) offer REST APIs for publishing and
fetching messages. A producer can publish a message by sending an HTTP request
to the intermediary and a consumer can pull a message by sending an HTTP request
to the intermediary:

```
  +----------+
  | Producer |
  +----------+
       |
       | HTTP POST (publishing a message)
       v
+--------------+
| Intermediary |
+--------------+
       ^
       | HTTP GET (fetching a message)
       |
  +----------+
  | Consumer |
  +----------+
```

Existing semantic conventions suppose that the consumer can use context
information from the producer trace to create links or parent/child
relationships between consumer and producer traces. For this to be possible,
context information from the producer needs to be propagated to the consumer.
In the example outlined above, the consumers sends an HTTP GET request to the
intermediary to fetch a message, the message is returned as part of the
response. Via this HTTP request, context information can be propagated from the
consumer to the intermediary, but not from the intermediary to the consumer.
The consumer can obtain the necessary producer context information only if it
is propagated as part of the message itself, independent of HTTP context
propagation.

For correlating producer and consumer traces without special intermediary
instrumentation it is thus necessary to attach a producer context to the
message so it can be extracted and used by the consumer, regardless of the
contexts that are propagated on HTTP requests for publishing and fetching the
message.

Although OpenTelemetry semantic conventions cannot specify the exact mechanisms
to achieve this for every intermediary and every protocol, this requirement
must be clearly formulated, so that it can be implemented by protocols and
instrumentations.

## Proposed addition to the messaging semantic conventions

### Context propagation

A message may pass many different components and layers in one or more
intermediaries when it is propagated from the producer to the consumer. It
cannot be assumed, and in many cases, it is not even desired, that all those
components and layers are instrumented and propagate context according to
OpenTelemetry requirements.

A _message creation context_ allows correlating the producer with the
consumer(s) of a message, regardless of intermediary instrumentation. The
message creation context is created by the producer and should be propagated to
the consumer(s). It should not be altered by intermediaries. This context
helps to model dependencies between producers and consumers, regardless of the
underlying messaging transport mechanism and its instrumentation.

Instrumentors are required to instrument producer and consumer applications
so that context is attached to messages and extracted from messages in a
coordinated way. Future versions of these conventions might recommend [context propagation according to certain industry standards](#standards-for-context-propagation).
If the message creation context cannot be attached to the message and
propagated, consumer traces cannot be directly correlated to producer traces.

### Requirements

A producer SHOULD attach a message creation context to each message. The message creation context
SHOULD be attached in a way so that it is not possible to be changed by intermediaries.

## Future possibilities

### Transport context propagation

A message creation context can be attached to a message, while different
contexts are propagated with requests that publish and fetch a message. When
coming up with conventions and guidance for intermediary instrumentation, it
will be beneficial to clearly outline those two layers of context propagation
and build conventions for intermediary instrumentation on top of this outline:

1. The _message context layer_ allows correlating the producer with the
   consumers of a message, regardless of intermediary instrumentation. The
   creation context is created by the producer and must be propagated to the
   consumers. It must not be altered by intermediaries.

   This layer helps to model dependencies between producers and consumers,
   regardless of the underlying messaging transport mechanism and its
   instrumentation.
2. An additional _transport context layer_ allows correlating the producer and
   the consumer with an intermediary. It also allows correlating multiple
   intermediaries among each other. The transport context can be changed by
   intermediaries, according to intermediary instrumentations.

   This layer helps to gain insights into details of the message transport.

This would keep the existing correlation between producers and consumers intact
while allowing intermediaries to use the transport context to correlate
intermediary instrumentation with existing producer and consumer
instrumentations.

### Standards for context propagation

Currently, instrumentation authors have to decide how to attach and extract
context from messages to fulfil the [requirements for context propagation](#context-propagation).
While preserving the freedom for instrumentation authors to choose how to
propagate context, in the future these conventions should list recommended ways
of how to propagate context using well-established messaging protocols.

There are several work-in-progress efforts to standardize context propagation for different
messaging protocols and scenarios:

* [AMQP](https://w3c.github.io/trace-context-amqp/)
* [MQTT](https://w3c.github.io/trace-context-mqtt/)
* [CloudEvents via HTTP](https://github.com/cloudevents/spec/blob/v1.0.1/extensions/distributed-tracing.md)

Once the standards reach a stable state and define how the message creation
context and transport context are represented, these semantic conventions will
give a clear and stable recommendation for each protocol and scenario.
