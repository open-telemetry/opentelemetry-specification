# Scenarios for Tracing semantic conventions for messaging

This document aims to capture scenarios and a road map, both of which will
serve as a basis for [stabilizing](../../specification/versioning-and-stability.md#stable)
the [existing semantic conventions for messaging](https://github.com/open-telemetry/semantic-conventions/tree/main/docs/messaging),
which are currently in an [experimental](../../specification/versioning-and-stability.md#development)
state. The goal is to declare messaging semantic conventions stable before the
end of 2021.

## Motivation

Many observability scenarios involve messaging systems, event streaming, or
event-driven architectures. For Distributed Tracing to be useful across the
entire scenario, having good observability for messaging or eventing operations
is critical. To achieve this, OpenTelemetry must provide stable conventions and
guidelines for instrumenting those operations. Popular messaging systems that
should be supported include Kafka, RabbitMQ, Apache RocketMQ, Azure Event Hubs
and Service Bus, Amazon SQS, SNS, and Kinesis.

Bringing the existing experimental semantic conventions for messaging to a
stable state is a crucial step for users and instrumentation authors, as it
allows them to rely on [stability guarantees](../../specification/versioning-and-stability.md#semantic-conventions-stability),
and thus to ship and use stable instrumentation.

## Roadmap

1. This OTEP, consisting of scenarios and a proposed roadmap, is approved and
   merged.
2. [Stability guarantees](../../specification/versioning-and-stability.md#semantic-conventions-stability)
   for semantic conventions are approved and merged. This is not strictly related
   to semantic conventions for messaging but is a prerequisite for stabilizing any
   semantic conventions.
3. OTEPs proposing guidance for general instrumentation problems that also
   pertain to messaging are approved and merged. Those general instrumentation
   problems include retries and instrumentation layers.
4. An OTEP proposing a set of attributes and conventions covering the scenarios
   in this document is approved and merged.
5. Proposed specification changes are verified by prototypes for the scenarios
   and examples below.
6. The [specification for messaging semantic conventions for tracing](https://github.com/open-telemetry/semantic-conventions/tree/main/docs)
   are updated according to the OTEP mentioned above and are declared
   [stable](../../specification/versioning-and-stability.md#stable).

The steps in the roadmap don't necessarily need to happen in the given order,
some steps can be worked on in parallel.

## Terminology

The terminology used in this document is based on the [CloudEvents specification](https://github.com/cloudevents/spec/blob/v1.0.1/spec.md).
CloudEvents is hosted by the CNCF and provides a specification for describing
event data in common formats to provide interoperability across services,
platforms and systems.

### Message

A "message" is a transport envelope for the transfer of information. The
information is a combination of a payload and metadata. Metadata can be
directed at consumers or at intermediaries on the message path. Messages are
transferred via one or more intermediaries.  Messages are uniquely
identifiable.

In the strict sense, a _message_ is a payload that is sent to a specific
destination, whereas an _event_ is a signal emitted by a component upon
reaching a given state. This document is agnostic of those differences and uses
the term "message" in a wider sense to cover both concepts.

### Producer

The "producer" is a specific instance, process or device that creates and
publishes a message. "Publishing" is the process of sending a message or batch
to the intermediary or consumer.

### Consumer

A "consumer" receives the message and acts upon it. It uses the context and
data to execute some logic, which might lead to the occurrence of new events.

The consumer receives, processes, and settles a message. "Receiving" is the
process of obtaining a message from the intermediary, "processing" is the
process of acting on the information a message contains, "settling" is the
process of notifying an intermediary that a message was processed successfully.

### Intermediary

An "intermediary" receives a message to forward it to the next receiver, which
might be another intermediary or a consumer.

## Scenarios

Producing and consuming a message involves five stages:

```
PRODUCER

Create
  |                            CONSUMER
  v        +--------------+                   
Publish -> | INTERMEDIARY | -> Receive
           +--------------+       |
                  ^               v
                  .            Process
                  .               |
                  .               v
                  . . . . . .  Settle
```

1. The producer creates a message.
2. The producer publishes the message to an intermediary.
3. The consumer receives the message from an intermediary.
4. The consumer processes the message.
5. The consumer settles the message by notifying the intermediary that the
   message was processed. In some cases (fire-and-forget), the settlement stage
   does not exist.

The messaging semantic conventions need to define how to model those stages in
traces, how to propagate context, and how to enrich traces with attributes.
Failures and retries need to be handled in all stages that interface with the
intermediary (publish, receive and settle) and will be covered by general
instrumentation guidance.

Based on this model, the following scenarios capture major requirements and
can be used for prototyping, as examples, and as test cases.

### Individual settlement

Individual settlement systems imply independent logical message flows. A single
message is created and published in the same context, and it's delivered,
consumed, and settled as a single entity. Each message needs to be settled
individually. Usually, settlement information is stored by the intermediary, not
by the consumer.

Transport batching can be treated as a special case: messages can be
transported together as an optimization, but are produced and consumed
individually.

As the diagram below shows, each message can be settled individually,
regardless of the position of the message in the stream or queue. In contrast
to checkpoint-based settlement, settlement information is related to individual
messages and not to the overall message stream.

```
+---------+ +---------+ +---------+ +---------+ +---------+ +---------+
|Message A| |Message B| |Message C| |Message D| |Message E| |Message F|
+---------+ +---------+ +---------+ +---------+ +---------+ +---------+
 Settled                 Settled                             Settled 
```

#### Examples

1. The following configurations should be instrumented and tested for RabbitMQ
   or a similar messaging system:

   * 1 producer, 1 queue, 2 consumers
   * 1 producer, fanout exchange to 2 queues, 2 consumers
   * 2 producers, fanout exchange to 2 queues, 2 consumers

   Each of the producers continuously produces messages.

### Checkpoint-based settlement

Messages are processed as a stream and settled by moving a checkpoint. A
checkpoint points to a position of the stream up to which messages were
processed and settled. Messages cannot be settled individually, instead, the
checkpoint needs to be forwarded. Usually, the consumer is responsible for
storing checkpointing information, not the intermediary.

Checkpoint-based settlement systems are designed to efficiently receive and
settle batches of messages. However, it is not possible to settle messages
independent of their position in the stream (e. g., if message B is located at
a later position in the stream than message A, then message B cannot be settled
without also settling message A).

As the diagram below shows, messages cannot be settled individually. Instead,
settlement information is related to the overall ordered message stream.

```
                               Checkpoint
                                   | 
                                   v                                
+---------+ +---------+ +---------+ +---------+ +---------+ +---------+
|Message A| |Message B| |Message C| |Message D| |Message E| |Message F|
+---------+ +---------+ +---------+ +---------+ +---------+ +---------+
                     <---  Settled
```

#### Examples

1. The following configurations should be instrumented and tested for Kafka or
   a similar messaging system:

   * 1 producer, 2 consumers in the same consumer group
   * 1 producer, 2 consumers in different consumer groups
   * 2 producers, 2 consumers in the same consumer group

   Each of the producers produces a continuous stream of messages.

## Open questions

The following areas are considered out-of-scope of a first stable release of
semantic conventions for messaging. While not being explicitly considered for
a first stable release, it is important to ensure that this first stable
release can serve as a solid foundation for further improvements in these areas.

### Sampling

The current experimental semantic conventions rely heavily on span links as
a way to correlate spans. This is necessary, as several traces are needed to
model the complete path that a message takes through the system. With the currently
available sampling capabilities of OpenTelemetry, it is not possible to ensure
that a set of linked traces is sampled. As a result, it is unlikely to sample a
set of traces that covers the complete path a message takes.

Solving this problem requires a solution for sampling based on span links,
which is not in scope for this OTEP.

However, having a too high number of span links in a single trace or having too
many traces linked together can make the visualization and analysis of traces
inefficient. This problem is not related to sampling and needs to be addressed
by the semantic conventions.

### Instrumenting intermediaries

Instrumenting intermediaries can be valuable for debugging configuration or
performance issues, or for detecting specific intermediary failures.

Stable semantic conventions for instrumenting intermediaries can be provided at
a future point in time, but are not in scope for this OTEP. The messaging
semantic conventions this document refers to need to provide instrumentation
that works well without the need to have intermediaries instrumented.

### Metrics

Messaging semantic conventions for tracing and for metrics overlap and should
be as consistent as possible. However, semantic conventions for metrics will be
handled separately and are not in scope for this OTEP.

### Asynchronous message passing in the wider sense

Asynchronous message passing in the wider sense is a communication method
wherein the system puts a message in a queue or channel and does not require an
immediate response to continue processing. This can range from utilizing a
simple queue implementation to a full-fledged messaging system.

Messaging semantic conventions are intended for systems that fit into one of
the [scenarios laid out in the previous section](#scenarios), which cover a
significant part of asynchronous message passing applications. However, there
are low-level patterns of asynchronous message passing that don't fit in any of
those scenarios, e. g. channels in Go, or message passing in Erlang. Those
might be covered by a different set of semantic conventions in the future.

There also exist several frameworks for queuing and executing background jobs,
often those frameworks utilize patterns of asynchronous message passing to
queue jobs. Those frameworks might utilize messaging semantic conventions if
they fit in any of the [scenarios laid out in the previous section](#scenarios),
but otherwise targeting those various frameworks is not an explicit goal for
these conventions. Those frameworks might be covered by [semantic conventions for "jobs"](https://github.com/open-telemetry/opentelemetry-specification/pull/1582)
in the future.

## Further reading

* [CloudEvents](https://github.com/cloudevents/spec/blob/v1.0.1/spec.md)
* [Message-Driven (in contrast to Event-Driven)](https://www.reactivemanifesto.org/glossary#Message-Driven)
* [Asynchronous message passing](https://en.wikipedia.org/wiki/Message_passing#Asynchronous_message_passing)
* [Existing semantic conventions for messaging](https://github.com/open-telemetry/semantic-conventions/tree/main/docs/messaging)
