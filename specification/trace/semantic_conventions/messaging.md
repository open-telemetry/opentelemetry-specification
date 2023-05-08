# Messaging systems

**Status**: [Experimental](../../document-status.md)

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [Definitions](#definitions)
  * [Message](#message)
  * [Producer](#producer)
  * [Consumer](#consumer)
  * [Intermediary](#intermediary)
  * [Destinations and sources](#destinations-and-sources)
  * [Message consumption](#message-consumption)
  * [Conversations](#conversations)
  * [Temporary and anonymous destinations](#temporary-and-anonymous-destinations)
- [Conventions](#conventions)
  * [Context propagation](#context-propagation)
  * [Span name](#span-name)
  * [Span kind](#span-kind)
  * [Operation names](#operation-names)
- [Messaging attributes](#messaging-attributes)
  * [Attribute namespaces](#attribute-namespaces)
  * [Producer attributes](#producer-attributes)
  * [Consumer attributes](#consumer-attributes)
  * [Per-message attributes](#per-message-attributes)
  * [Attributes specific to certain messaging systems](#attributes-specific-to-certain-messaging-systems)
    + [RabbitMQ](#rabbitmq)
    + [Apache Kafka](#apache-kafka)
    + [Apache RocketMQ](#apache-rocketmq)
- [Examples](#examples)
  * [Topic with multiple consumers](#topic-with-multiple-consumers)
  * [Apache Kafka with Quarkus or Spring Boot Example](#apache-kafka-with-quarkus-or-spring-boot-example)
  * [Batch receiving](#batch-receiving)
  * [Batch processing](#batch-processing)

<!-- tocstop -->

> **Warning**
> Existing Messaging instrumentations that are using
> [v1.20.0 of this document](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.20.0/specification/trace/semantic_conventions/messaging.md)
> (or prior):
>
> * SHOULD NOT change the version of the networking attributes that they emit
>   until the HTTP semantic conventions are marked stable (HTTP stabilization will
>   include stabilization of a core set of networking attributes which are also used
>   in Messaging instrumentations).
> * SHOULD introduce an environment variable `OTEL_SEMCONV_STABILITY_OPT_IN`
>   in the existing major version which supports the following values:
>   * `none` - continue emitting whatever version of the old experimental
>     networking attributes the instrumentation was emitting previously.
>     This is the default value.
>   * `http` - emit the new, stable networking attributes,
>     and stop emitting the old experimental networking attributes
>     that the instrumentation emitted previously.
>   * `http/dup` - emit both the old and the stable networking attributes,
>     allowing for a seamless transition.
> * SHOULD maintain (security patching at a minimum) the existing major version
>   for at least six months after it starts emitting both sets of attributes.
> * SHOULD drop the environment variable in the next major version (stable
>   next major version SHOULD NOT be released prior to October 1, 2023).

## Definitions

### Message

Although messaging systems are not as standardized as, e.g., HTTP, it is assumed that the following definitions are applicable to most of them that have similar concepts at all (names borrowed mostly from JMS):

A *message* is an envelope with a potentially empty payload.
This envelope may offer the possibility to convey additional metadata, often in key/value form.

A message is sent by a message *producer* to:

* Physically: some message *broker* (which can be e.g., a single server, or a cluster, or a local process reached via IPC). The broker handles the actual delivery, re-delivery, persistence, etc. In some messaging systems the broker may be identical or co-located with (some) message consumers.
With Apache Kafka, the physical broker a message is written to depends on the number of partitions, and which broker is the *leader* of the partition the record is written to.
* Logically: some particular message *destination*.

Messages can be delivered to 0, 1, or multiple consumers depending on the dispatching semantic of the protocol.

### Producer

The "producer" is a specific instance, process or device that creates and
publishes a message. "Publishing" is the process of sending a message or batch
of messages to the intermediary or consumer.

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

### Destinations and sources

A destination is usually uniquely identified by name within the messaging system instance. Examples of a destination name would be a URL or a simple one-word identifier.
Sending messages to a destination is called "*publish*" in context of this specification.

A source represents an entity within messaging system messages are consumed from. Source and destination for specific message may be the same. However, if message is routed within one or multiple brokers, source and destination can be different.

Typical examples of destinations and sources include Kafka topics, RabbitMQ queues and topics.

### Message consumption

The consumption of a message can happen in multiple steps.
First, the lower-level receiving of a message at a consumer, and then the logical processing of the message.
Often, the waiting for a message is not particularly interesting and hidden away in a framework that only invokes some handler function to process a message once one is received
(in the same way that the listening on a TCP port for an incoming HTTP message is not particularly interesting).

### Conversations

In some messaging systems, a message can receive one or more reply messages that answers a particular other message that was sent earlier. All messages that are grouped together by such a reply-relationship are called a *conversation*.
The grouping usually happens through some sort of "In-Reply-To:" meta information or an explicit *conversation ID* (sometimes called *correlation ID*).
Sometimes a conversation can span multiple message destinations (e.g. initiated via a topic, continued on a temporary one-to-one queue).

### Temporary and anonymous destinations

Some messaging systems support the concept of *temporary destination* (often only temporary queues) that are established just for a particular set of communication partners (often one to one) or conversation.
Often such destinations are also unnamed (anonymous) or have an auto-generated name.

## Conventions

Given these definitions, the remainder of this section describes the semantic conventions for Spans describing interactions with messaging systems.

### Context propagation

A message may traverse many different components and layers in one or more intermediaries
when it is propagated from the producer to the consumer(s). To be able to correlate
consumer traces with producer traces using the existing context propagation mechanisms,
all components must propagate context down the chain.

Messaging systems themselves may trace messages as the messages travels from
producers to consumers. Such tracing would cover the transport layer but would
not help in correlating producers with consumers. To be able to directly
correlate producers with consumers, another context that is propagated with
the message is required.

A message *creation context* allows correlating producers with consumers
of a message and model the dependencies between them,
regardless of the underlying messaging transport mechanism and its instrumentation.

The message creation context is created by the producer and should be propagated
to the consumer(s). Consumer traces cannot be directly correlated with producer
traces if the message creation context is not attached and propagated with the message.

A producer SHOULD attach a message creation context to each message.
If possible, the message creation context SHOULD be attached
in such a way that it cannot be changed by intermediaries.

> This document does not specify the exact mechanisms on how the creation context
> is attached/extracted to/from messages. Future versions of these conventions
> will give clear recommendations, following industry standards including, but not limited to
> [Trace Context: AMQP protocol](https://w3c.github.io/trace-context-amqp/) and
> [Trace Context: MQTT protocol](https://w3c.github.io/trace-context-mqtt/)
> once those standards reach a stable state.

### Span name

The span name SHOULD be set to the message destination name and the operation being performed in the following format:

```
<destination name> <operation name>
```

The destination name SHOULD only be used for the span name if it is known to be of low cardinality (cf. [general span name guidelines](../api.md#span)).
This can be assumed if it is statically derived from application code or configuration.
Wherever possible, the real destination names after resolving logical or aliased names SHOULD be used.
If the destination name is dynamic, such as a [conversation ID](#conversations) or a value obtained from a `Reply-To` header, it SHOULD NOT be used for the span name.
In these cases, an artificial destination name that best expresses the destination, or a generic, static fallback like `"(anonymous)"` for [anonymous destinations](#temporary-and-anonymous-destinations) SHOULD be used instead.

The values allowed for `<operation name>` are defined in the section [Operation names](#operation-names) below.
If the format above is used, the operation name MUST match the `messaging.operation` attribute defined for message consumer spans below.

Examples:

* `shop.orders publish`
* `shop.orders receive`
* `shop.orders process`
* `print_jobs publish`
* `topic with spaces process`
* `AuthenticationRequest-Conversations process`
* `(anonymous) publish` (`(anonymous)` being a stable identifier for an unnamed destination)

### Span kind

A producer of a message should set the span kind to `PRODUCER` unless it synchronously waits for a response: then it should use `CLIENT`.
The processor of the message should set the kind to `CONSUMER`, unless it always sends back a reply that is directed to the producer of the message
(as opposed to e.g., a queue on which the producer happens to listen): then it should use `SERVER`.

### Operation names

The following operations related to messages are defined for these semantic conventions:

| Operation name | Description |
| -------------- | ----------- |
| `publish`      | A message is sent to a destination by a message producer/client.       |
| `receive`      | A message is received from a destination by a message consumer/server. |
| `process`      | A message that was previously received from a destination is processed by a message consumer/server. |

## Messaging attributes

<!-- semconv messaging -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `messaging.system` | string | A string identifying the messaging system. | `kafka`; `rabbitmq`; `rocketmq`; `activemq`; `AmazonSQS` | Required |
| `messaging.operation` | string | A string identifying the kind of messaging operation as defined in the [Operation names](#operation-names) section above. [1] | `publish` | Required |
| `messaging.batch.message_count` | int | The number of messages sent, received, or processed in the scope of the batching operation. [2] | `0`; `1`; `2` | Conditionally Required: [3] |
| `messaging.client_id` | string | A unique identifier for the client that consumes or produces a message. | `client-5`; `myhost@8742@s8083jm` | Recommended: If a client id is available |
| `messaging.message.conversation_id` | string | The [conversation ID](#conversations) identifying the conversation to which the message belongs, represented as a string. Sometimes called "Correlation ID". | `MyConversationId` | Recommended: [4] |
| `messaging.message.id` | string | A value used by the messaging system as an identifier for the message, represented as a string. | `452a7c7c7c7048c2f887f61572b18fc2` | Recommended: [5] |
| `messaging.message.payload_compressed_size_bytes` | int | The compressed size of the message payload in bytes. | `2048` | Recommended: [6] |
| `messaging.message.payload_size_bytes` | int | The (uncompressed) size of the message payload in bytes. Also use this attribute if it is unknown whether the compressed or uncompressed payload size is reported. | `2738` | Recommended: [7] |
| [`net.peer.name`](span-general.md) | string | Logical remote hostname, see note below. [8] | `example.com` | Conditionally Required: If available. |
| [`net.protocol.name`](span-general.md) | string | Application layer protocol used. The value SHOULD be normalized to lowercase. | `amqp`; `mqtt` | Recommended |
| [`net.protocol.version`](span-general.md) | string | Version of the application layer protocol used. See note below. [9] | `3.1.1` | Recommended |
| [`net.sock.family`](span-general.md) | string | Protocol [address family](https://man7.org/linux/man-pages/man7/address_families.7.html) which is used for communication. | `inet6`; `bluetooth` | Conditionally Required: [10] |
| [`net.sock.peer.addr`](span-general.md) | string | Remote socket peer address: IPv4 or IPv6 for internet protocols, path for local communication, [etc](https://man7.org/linux/man-pages/man7/address_families.7.html). | `127.0.0.1`; `/tmp/mysql.sock` | Recommended |
| [`net.sock.peer.name`](span-general.md) | string | Remote socket peer name. | `proxy.example.com` | Recommended: [11] |
| [`net.sock.peer.port`](span-general.md) | int | Remote socket peer port. | `16456` | Recommended: [12] |

**[1]:** If a custom value is used, it MUST be of low cardinality.

**[2]:** Instrumentations SHOULD NOT set `messaging.batch.message_count` on spans that operate with a single message. When a messaging client library supports both batch and single-message API for the same operation, instrumentations SHOULD use `messaging.batch.message_count` for batching APIs and SHOULD NOT use it for single-message APIs.

**[3]:** If the span describes an operation on a batch of messages.

**[4]:** Only if span represents operation on a single message.

**[5]:** Only for spans that represent an operation on a single message.

**[6]:** Only if span represents operation on a single message.

**[7]:** Only if span represents operation on a single message.

**[8]:** This should be the IP/hostname of the broker (or other network-level peer) this specific message is sent to/received from.

**[9]:** `net.protocol.version` refers to the version of the protocol used and might be different from the protocol client's version. If the HTTP client used has a version of `0.27.2`, but sends HTTP version `1.1`, this attribute should be set to `1.1`.

**[10]:** If different than `inet` and if any of `net.sock.peer.addr` or `net.sock.host.addr` are set. Consumers of telemetry SHOULD accept both IPv4 and IPv6 formats for the address in `net.sock.peer.addr` if `net.sock.family` is not set. This is to support instrumentations that follow previous versions of this document.

**[11]:** If different than `net.peer.name` and if `net.sock.peer.addr` is set.

**[12]:** If defined for the address family and if different than `net.peer.port` and if `net.sock.peer.addr` is set.

`messaging.operation` has the following list of well-known values. If one of them applies, then the respective value MUST be used, otherwise a custom value MAY be used.

| Value  | Description |
|---|---|
| `publish` | publish |
| `receive` | receive |
| `process` | process |
<!-- endsemconv -->

Additionally `net.peer.port` from the [network attributes][] is recommended.
Furthermore, it is strongly recommended to add the [`net.transport`][] attribute and follow its guidelines, especially for in-process queueing systems (like [Hangfire][], for example).
These attributes should be set to the broker to which the message is sent/from which it is received.

### Attribute namespaces

- `messaging.message`: Contains attributes that describe individual messages
- `messaging.destination`: Contains attributes that describe the logical entity messages are published to.
  See [Destinations and sources](#destinations-and-sources) for more details
- `messaging.source`: Contains attributes that describe the logical entity messages are received from
- `messaging.batch`: Contains attributes that describe batch operations
- `messaging.consumer`: Contains attributes that describe application instance that consumes a message. See [consumer](#consumer) for more details

Communication with broker is described with general [network attributes].

Messaging system-specific attributes MUST be defined in the corresponding `messaging.{system}` namespace
as described in [Attributes specific to certain messaging systems](#attributes-specific-to-certain-messaging-systems).

[network attributes]: span-general.md#general-network-connection-attributes
[`net.transport`]: span-general.md#network-transport-attributes
[Hangfire]: https://www.hangfire.io/

### Producer attributes

The following additional attributes describe message producer operations.

<!-- semconv messaging.producer -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `messaging.destination.anonymous` | boolean | A boolean that is true if the message destination is anonymous (could be unnamed or have auto-generated name). |  | Conditionally Required: [1] |
| `messaging.destination.name` | string | The message destination name [2] | `MyQueue`; `MyTopic` | Conditionally Required: [3] |
| `messaging.destination.template` | string | Low cardinality representation of the messaging destination name [4] | `/customers/{customerId}` | Conditionally Required: [5] |
| `messaging.destination.temporary` | boolean | A boolean that is true if the message destination is temporary and might not exist anymore after messages are processed. |  | Conditionally Required: [6] |

**[1]:** If value is `true`. When missing, the value is assumed to be `false`.

**[2]:** Destination name SHOULD uniquely identify a specific queue, topic or other entity within the broker. If
the broker does not have such notion, the destination name SHOULD uniquely identify the broker.

**[3]:** If one message is being published or if the value applies to all messages in the batch.

**[4]:** Destination names could be constructed from templates. An example would be a destination name involving a user name or product id. Although the destination name in this case is of high cardinality, the underlying template is of low cardinality and can be effectively used for grouping and aggregation.

**[5]:** If available. Instrumentations MUST NOT use `messaging.destination.name` as template unless low-cardinality of destination name is guaranteed.

**[6]:** If value is `true`. When missing, the value is assumed to be `false`.
<!-- endsemconv -->

### Consumer attributes

The following additional attributes describe message consumer operations.

> Note: Consumer spans can have attributes describing source and destination. Since messages could be routed by brokers, source and destination don't always match. If original destination information is available on the consumer, consumer instrumentations SHOULD populate corresponding `messaging.destination` attributes.

<!-- semconv messaging.consumer -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `messaging.destination.anonymous` | boolean | A boolean that is true if the message destination is anonymous (could be unnamed or have auto-generated name). |  | Recommended: If known on consumer |
| `messaging.destination.name` | string | The message destination name [1] | `MyQueue`; `MyTopic` | Recommended: If known on consumer |
| `messaging.destination.temporary` | boolean | A boolean that is true if the message destination is temporary and might not exist anymore after messages are processed. |  | Recommended: If known on consumer |
| `messaging.source.anonymous` | boolean | A boolean that is true if the message source is anonymous (could be unnamed or have auto-generated name). |  | Recommended: [2] |
| `messaging.source.name` | string | The message source name [3] | `MyQueue`; `MyTopic` | Conditionally Required: [4] |
| `messaging.source.template` | string | Low cardinality representation of the messaging source name [5] | `/customers/{customerId}` | Conditionally Required: [6] |
| `messaging.source.temporary` | boolean | A boolean that is true if the message source is temporary and might not exist anymore after messages are processed. |  | Recommended: [7] |

**[1]:** Destination name SHOULD uniquely identify a specific queue, topic or other entity within the broker. If
the broker does not have such notion, the destination name SHOULD uniquely identify the broker.

**[2]:** When supported by messaging system and only if the source is anonymous. When missing, the value is assumed to be `false`.

**[3]:** Source name SHOULD uniquely identify a specific queue, topic, or other entity within the broker. If
the broker does not have such notion, the source name SHOULD uniquely identify the broker.

**[4]:** If the value applies to all messages in the batch.

**[5]:** Source names could be constructed from templates. An example would be a source name involving a user name or product id. Although the source name in this case is of high cardinality, the underlying template is of low cardinality and can be effectively used for grouping and aggregation.

**[6]:** If available. Instrumentations MUST NOT use `messaging.source.name` as template unless low-cardinality of source name is guaranteed.

**[7]:** When supported by messaging system and only if the source is temporary. When missing, the value is assumed to be `false`.
<!-- endsemconv -->

The *receive* span is be used to track the time used for receiving the message(s), whereas the *process* span(s) track the time for processing the message(s).
Note that one or multiple Spans with `messaging.operation` = `process` may often be the children of a Span with `messaging.operation` = `receive`.
The distinction between receiving and processing of messages is not always of particular interest or sometimes hidden away in a framework (see the [Message consumption](#message-consumption) section above) and therefore the attribute can be left out.
For batch receiving and processing (see the [Batch receiving](#batch-receiving) and [Batch processing](#batch-processing) examples below) in particular, the attribute SHOULD be set.
Even though in that case one might think that the processing span's kind should be `INTERNAL`, that kind MUST NOT be used.
Instead span kind should be set to either `CONSUMER` or `SERVER` according to the rules defined above.

### Per-message attributes

All messaging operations (`publish`, `receive`, `process`, or others not covered by this specification) can describe both single and/or batch of messages.
Attributes in the `messaging.message` or `messaging.{system}.message` namespace describe individual messages. For single-message operations they SHOULD be set on corresponding span.

For batch operations, per-message attributes are usually different and cannot be set on the corresponding span. In such cases the attributes MAY be set on links. See [Batch Receiving](#batch-receiving) and [Batch Processing](#batch-processing) for more information on correlation using links.

Some messaging systems (e.g., Kafka, Azure EventGrid) allow publishing a single batch of messages to different topics. In such cases, the attributes in `messaging.destination` and `messaging.source` MAY be
set on links. Instrumentations MAY set source and destination attributes on the span if all messages in the batch share the same destination or source.

### Attributes specific to certain messaging systems

All attributes that are specific for a messaging system SHOULD be populated in `messaging.{system}` namespace. Attributes that describe a message, a destination, a source, a consumer or a batch of messages SHOULD be populated under the corresponding namespace:

* `messaging.{system}.message`: Describes attributes for individual messages
* `messaging.{system}.destination` and `messaging.{system}.source`: Describe the destination and source a message (or a batch) are published to and received from respectively. The combination of attributes in these namespaces should uniquely identify the entity and include properties significant for this messaging system. For example, Kafka instrumentations should include partition identifier.
* `messaging.{system}.consumer`: Describes message consumer properties
* `messaging.{system}.batch`: Describes message batch properties

#### RabbitMQ

In RabbitMQ, the destination is defined by an *exchange* and a *routing key*.
`messaging.destination.name` MUST be set to the name of the exchange. This will be an empty string if the default exchange is used.

<!-- semconv messaging.rabbitmq -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `messaging.rabbitmq.destination.routing_key` | string | RabbitMQ message routing key. | `myKey` | Conditionally Required: If not empty. |
<!-- endsemconv -->

#### Apache Kafka

For Apache Kafka, the following additional attributes are defined:

<!-- semconv messaging.kafka -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `messaging.kafka.message.key` | string | Message keys in Kafka are used for grouping alike messages to ensure they're processed on the same partition. They differ from `messaging.message.id` in that they're not unique. If the key is `null`, the attribute MUST NOT be set. [1] | `myKey` | Recommended |
| `messaging.kafka.consumer.group` | string | Name of the Kafka Consumer Group that is handling the message. Only applies to consumers, not producers. | `my-group` | Recommended |
| `messaging.kafka.destination.partition` | int | Partition the message is sent to. | `2` | Recommended |
| `messaging.kafka.source.partition` | int | Partition the message is received from. | `2` | Recommended |
| `messaging.kafka.message.offset` | int | The offset of a record in the corresponding Kafka partition. | `42` | Recommended |
| `messaging.kafka.message.tombstone` | boolean | A boolean that is true if the message is a tombstone. |  | Conditionally Required: [2] |

**[1]:** If the key type is not string, it's string representation has to be supplied for the attribute. If the key has no unambiguous, canonical string form, don't include its value.

**[2]:** If value is `true`. When missing, the value is assumed to be `false`.
<!-- endsemconv -->

For Apache Kafka producers, [`peer.service`](./span-general.md#general-remote-service-attributes) SHOULD be set to the name of the broker or service the message will be sent to.
The `service.name` of a Consumer's Resource SHOULD match the `peer.service` of the Producer, when the message is directly passed to another service.
If an intermediary broker is present, `service.name` and `peer.service` will not be the same.

`messaging.client_id` SHOULD be set to the `client-id` of consumers, or to the `client.id` property of producers.

#### Apache RocketMQ

Specific attributes for Apache RocketMQ are defined below.

<!-- semconv messaging.rocketmq -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `messaging.rocketmq.namespace` | string | Namespace of RocketMQ resources, resources in different namespaces are individual. | `myNamespace` | Required |
| `messaging.rocketmq.client_group` | string | Name of the RocketMQ producer/consumer group that is handling the message. The client type is identified by the SpanKind. | `myConsumerGroup` | Required |
| `messaging.rocketmq.message.delivery_timestamp` | int | The timestamp in milliseconds that the delay message is expected to be delivered to consumer. | `1665987217045` | Conditionally Required: [1] |
| `messaging.rocketmq.message.delay_time_level` | int | The delay time level for delay message, which determines the message delay time. | `3` | Conditionally Required: [2] |
| `messaging.rocketmq.message.group` | string | It is essential for FIFO message. Messages that belong to the same message group are always processed one by one within the same consumer group. | `myMessageGroup` | Conditionally Required: If the message type is FIFO. |
| `messaging.rocketmq.message.type` | string | Type of message. | `normal` | Recommended |
| `messaging.rocketmq.message.tag` | string | The secondary classifier of message besides topic. | `tagA` | Recommended |
| `messaging.rocketmq.message.keys` | string[] | Key(s) of message, another way to mark message besides message id. | `[keyA, keyB]` | Recommended |
| `messaging.rocketmq.consumption_model` | string | Model of message consumption. This only applies to consumer spans. | `clustering` | Recommended |

**[1]:** If the message type is delay and delay time level is not specified.

**[2]:** If the message type is delay and delivery timestamp is not specified.

`messaging.rocketmq.message.type` MUST be one of the following:

| Value  | Description |
|---|---|
| `normal` | Normal message |
| `fifo` | FIFO message |
| `delay` | Delay message |
| `transaction` | Transaction message |

`messaging.rocketmq.consumption_model` MUST be one of the following:

| Value  | Description |
|---|---|
| `clustering` | Clustering consumption model |
| `broadcasting` | Broadcasting consumption model |
<!-- endsemconv -->

`messaging.client_id` SHOULD be set to the client ID that is automatically generated by the Apache RocketMQ SDK.

## Examples

### Topic with multiple consumers

Given is a process P, that publishes a message to a topic T on messaging system MS, and two processes CA and CB, which both receive the message and process it.

```
Process P:  | Span Prod1 |
--
Process CA:              | Span CA1 |
--
Process CB:                 | Span CB1 |
```

| Field or Attribute | Span Prod1 | Span CA1 | Span CB1 |
|-|-|-|-|
| Span name | `"T publish"` | `"T process"` | `"T process"` |
| Parent |  | Span Prod1 | Span Prod1 |
| Links |  |  |  |
| SpanKind | `PRODUCER` | `CONSUMER` | `CONSUMER` |
| Status | `Ok` | `Ok` | `Ok` |
| `net.peer.name` | `"ms"` | `"ms"` | `"ms"` |
| `net.peer.port` | `1234` | `1234` | `1234` |
| `messaging.system` | `"rabbitmq"` | `"rabbitmq"` | `"rabbitmq"` |
| `messaging.destination.name` | `"T"` | | |
| `messaging.source.name` | | `"T"` | `"T"` |
| `messaging.operation` |  | `"process"` | `"process"` |
| `messaging.message.id` | `"a1"` | `"a1"`| `"a1"` |

### Apache Kafka with Quarkus or Spring Boot Example

Given is a process P, that publishes a message to a topic T1 on Apache Kafka.
One process, CA, receives the message and publishes a new message to a topic T2 that is then received and processed by CB.

Frameworks such as Quarkus and Spring Boot separate processing of a received message from producing subsequent messages out.
For this reason, receiving (Span Rcv1) is the parent of both processing (Span Proc1) and producing a new message (Span Prod2).
The span representing message receiving (Span Rcv1) should not set `messaging.operation` to `receive`,
as it does not only receive the message but also converts the input message to something suitable for the processing operation to consume and creates the output message from the result of processing.

```
Process P:  | Span Prod1 |
--
Process CA:              | Span Rcv1 |
                                | Span Proc1 |
                                  | Span Prod2 |
--
Process CB:                           | Span Rcv2 |
```

| Field or Attribute | Span Prod1 | Span Rcv1 | Span Proc1 | Span Prod2 | Span Rcv2
|-|-|-|-|-|-|
| Span name | `"T1 publish"` | `"T1 receive"` | `"T1 process"` | `"T2 publish"` | `"T2 receive`" |
| Parent |  | Span Prod1 | Span Rcv1 | Span Rcv1 | Span Prod2 |
| Links |  |  | |  |  |
| SpanKind | `PRODUCER` | `CONSUMER` | `CONSUMER` | `PRODUCER` | `CONSUMER` |
| Status | `Ok` | `Ok` | `Ok` | `Ok` | `Ok` |
| `peer.service` | `"myKafka"` |  |  | `"myKafka"` |  |
| `service.name` |  | `"myConsumer1"` | `"myConsumer1"` |  | `"myConsumer2"` |
| `messaging.system` | `"kafka"` | `"kafka"` | `"kafka"` | `"kafka"` | `"kafka"` |
| `messaging.destination.name` | `"T1"` | | | | |
| `messaging.source.name` |  | `"T1"` | `"T1"` | `"T2"` | `"T2"` |
| `messaging.operation` |  |  | `"process"` |  | `"receive"` |
| `messaging.client_id` |  | `"5"` | `"5"` | `"5"` | `"8"` |
| `messaging.kafka.message.key` | `"myKey"` | `"myKey"` | `"myKey"` | `"anotherKey"` | `"anotherKey"` |
| `messaging.kafka.consumer.group` |  | `"my-group"` | `"my-group"` |  | `"another-group"` |
| `messaging.kafka.partition` | `"1"` | `"1"` | `"1"` | `"3"` | `"3"` |
| `messaging.kafka.message.offset` | `"12"` | `"12"` | `"12"` | `"32"` | `"32"` |

### Batch receiving

Given is a process P, that publishes two messages to a queue Q on messaging system MS, and a process C, which receives both of them in one batch (Span Recv1) and processes each message separately (Spans Proc1 and Proc2).

Since a span can only have one parent and the propagated trace and span IDs are not known when the receiving span is started, the receiving span will have no parent and the processing spans are correlated with the producing spans using links.

```
Process P: | Span Prod1 | Span Prod2 |
--
Process C:                      | Span Recv1 |
                                        | Span Proc1 |
                                               | Span Proc2 |
```

| Field or Attribute | Span Prod1 | Span Prod2 | Span Recv1 | Span Proc1 | Span Proc2 |
|-|-|-|-|-|-|
| Span name | `"Q publish"` | `"Q publish"` | `"Q receive"` | `"Q process"` | `"Q process"` |
| Parent |  |  |  | Span Recv1 | Span Recv1 |
| Links |  |  |  | Span Prod1 | Span Prod2 |
| SpanKind | `PRODUCER` | `PRODUCER` | `CONSUMER` | `CONSUMER` | `CONSUMER` |
| Status | `Ok` | `Ok` | `Ok` | `Ok` | `Ok` |
| `net.peer.name` | `"ms"` | `"ms"` | `"ms"` | `"ms"` | `"ms"` |
| `net.peer.port` | `1234` | `1234` | `1234` | `1234` | `1234` |
| `messaging.system` | `"rabbitmq"` | `"rabbitmq"` | `"rabbitmq"` | `"rabbitmq"` | `"rabbitmq"` |
| `messaging.destination.name` | `"Q"` | `"Q"` | | | |
| `messaging.source.name` | | | `"Q"` | `"Q"` | `"Q"` |
| `messaging.operation` |  |  | `"receive"` | `"process"` | `"process"` |
| `messaging.message.id` | `"a1"` | `"a2"` | | `"a1"` | `"a2"` |
| `messaging.batch.message_count` |  |  | 2 |  |  |

### Batch processing

Given is a process P, that publishes two messages to a queue Q on messaging system MS, and a process C, which receives them separately in two different operations (Span Recv1 and Recv2) and processes both messages in one batch (Span Proc1).

Since each span can only have one parent, C3 should not choose a random parent out of C1 and C2, but rather rely on the implicitly selected parent as defined by the [tracing API spec](../api.md).
Depending on the implementation, the producing spans might still be available in the meta data of the messages and should be added to C3 as links.
The client library or application could also add the receiver span's SpanContext to the data structure it returns for each message. In this case, C3 could also add links to the receiver spans C1 and C2.

The status of the batch processing span is selected by the application. Depending on the semantics of the operation. A span status `Ok` could, for example, be set only if all messages or if just at least one were properly processed.

```
Process P: | Span Prod1 | Span Prod2 |
--
Process C:                              | Span Recv1 | Span Recv2 |
                                                                   | Span Proc1 |
```

| Field or Attribute | Span Prod1 | Span Prod2 | Span Recv1 | Span Recv2 | Span Proc1 |
|-|-|-|-|-|-|
| Span name | `"Q publish"` | `"Q publish"` | `"Q receive"` | `"Q receive"` | `"Q process"` |
| Parent |  |  | Span Prod1 | Span Prod2 |  |
| Links |  |  |  |  | [Span Prod1, Span Prod2 ] |
| Link attributes |  |  |  |  | Span Prod1: `messaging.message.id`: `"a1"`  |
|                 |  |  |  |  | Span Prod2: `messaging.message.id`: `"a2"`  |
| SpanKind | `PRODUCER` | `PRODUCER` | `CONSUMER` | `CONSUMER` | `CONSUMER` |
| Status | `Ok` | `Ok` | `Ok` | `Ok` | `Ok` |
| `net.peer.name` | `"ms"` | `"ms"` | `"ms"` | `"ms"` | `"ms"` |
| `net.peer.port` | `1234` | `1234` | `1234` | `1234` | `1234` |
| `messaging.system` | `"rabbitmq"` | `"rabbitmq"` | `"rabbitmq"` | `"rabbitmq"` | `"rabbitmq"` |
| `messaging.destination.name` | `"Q"` | `"Q"` | | | |
| `messaging.source.name` | | | `"Q"` | `"Q"` | `"Q"` |
| `messaging.operation` |  |  | `"receive"` | `"receive"` | `"process"` |
| `messaging.message.id` | `"a1"` | `"a2"` | `"a1"` | `"a2"` | |
| `messaging.batch.message_count` | | | 1 | 1 | 2 |
