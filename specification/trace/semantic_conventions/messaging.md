# Messaging systems

**Status**: [Experimental](../../document-status.md)

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [Definitions](#definitions)
  * [Destinations](#destinations)
  * [Message consumption](#message-consumption)
  * [Conversations](#conversations)
  * [Temporary destinations](#temporary-destinations)
- [Conventions](#conventions)
  * [Span name](#span-name)
  * [Span kind](#span-kind)
  * [Operation names](#operation-names)
- [Messaging attributes](#messaging-attributes)
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

## Definitions

Although messaging systems are not as standardized as, e.g., HTTP, it is assumed that the following definitions are applicable to most of them that have similar concepts at all (names borrowed mostly from JMS):

A *message* is an envelope with a potentially empty payload.
This envelope may offer the possibility to convey additional metadata, often in key/value form.

A message is sent by a message *producer* to:

* Physically: some message *broker* (which can be e.g., a single server, or a cluster, or a local process reached via IPC). The broker handles the actual delivery, re-delivery, persistence, etc. In some messaging systems the broker may be identical or co-located with (some) message consumers.
With Apache Kafka, the physical broker a message is written to depends on the number of partitions, and which broker is the *leader* of the partition the record is written to.
* Logically: some particular message *destination*.

Messages can be delivered to 0, 1, or multiple consumers depending on the dispatching semantic of the protocol.

### Destinations

A destination is usually identified by some name unique within the messaging system instance, which might look like a URL or a simple one-word identifier.
Traditional messaging, such as JMS, involves two kinds of destinations: *topic*s and *queue*s.
A message that is sent (the send-operation is often called "*publish*" in this context) to a *topic* is broadcasted to all consumers that have *subscribed* to the topic.
A message submitted to a queue is processed by a message *consumer* (usually exactly once although some message systems support a more performant at-least-once mode for messages with [idempotent][] processing).

In a messaging system such as Apache Kafka, all destinations are *topic*s.
Each record, or message, is sent to a single consumer per consumer group.
Consumer groups provide *deliver once* semantics for consumers of a topic within a group.
Whether a specific message is processed as if it was sent to a topic or queue entirely depends on the consumer groups and their composition.
For instance, there can be multiple consumer groups processing records from the same topic.

[idempotent]: https://en.wikipedia.org/wiki/Idempotence

### Message consumption

The consumption of a message can happen in multiple steps.
First, the lower-level receiving of a message at a consumer, and then the logical processing of the message.
Often, the waiting for a message is not particularly interesting and hidden away in a framework that only invokes some handler function to process a message once one is received
(in the same way that the listening on a TCP port for an incoming HTTP message is not particularly interesting).

### Conversations

In some messaging systems, a message can receive one or more reply messages that answers a particular other message that was sent earlier. All messages that are grouped together by such a reply-relationship are called a *conversation*.
The grouping usually happens through some sort of "In-Reply-To:" meta information or an explicit *conversation ID* (sometimes called *correlation ID*).
Sometimes a conversation can span multiple message destinations (e.g. initiated via a topic, continued on a temporary one-to-one queue).

### Temporary destinations

Some messaging systems support the concept of *temporary destination* (often only temporary queues) that are established just for a particular set of communication partners (often one to one) or conversation.
Often such destinations are unnamed or have an auto-generated name.

## Conventions

Given these definitions, the remainder of this section describes the semantic conventions for Spans describing interactions with messaging systems.

### Span name

The span name SHOULD be set to the message destination name and the operation being performed in the following format:

```
<destination name> <operation name>
```

The destination name SHOULD only be used for the span name if it is known to be of low cardinality (cf. [general span name guidelines](../api.md#span)).
This can be assumed if it is statically derived from application code or configuration.
Wherever possible, the real destination names after resolving logical or aliased names SHOULD be used.
If the destination name is dynamic, such as a [conversation ID](#conversations) or a value obtained from a `Reply-To` header, it SHOULD NOT be used for the span name.
In these cases, an artificial destination name that best expresses the destination, or a generic, static fallback like `"(temporary)"` for [temporary destinations](#temporary-destinations) SHOULD be used instead.

The values allowed for `<operation name>` are defined in the section [Operation names](#operation-names) below.
If the format above is used, the operation name MUST match the `messaging.operation` attribute defined for message consumer spans below.

Examples:

* `shop.orders send`
* `shop.orders receive`
* `shop.orders process`
* `print_jobs send`
* `topic with spaces process`
* `AuthenticationRequest-Conversations process`
* `(temporary) send` (`(temporary)` being a stable identifier for randomly generated, temporary destination names)

### Span kind

A producer of a message should set the span kind to `PRODUCER` unless it synchronously waits for a response: then it should use `CLIENT`.
The processor of the message should set the kind to `CONSUMER`, unless it always sends back a reply that is directed to the producer of the message
(as opposed to e.g., a queue on which the producer happens to listen): then it should use `SERVER`.

### Operation names

The following operations related to messages are defined for these semantic conventions:

| Operation name | Description |
| -------------- | ----------- |
| `send`         | A message is sent to a destination by a message producer/client.       |
| `receive`      | A message is received from a destination by a message consumer/server. |
| `process`      | A message that was previously received from a destination is processed by a message consumer/server. |

## Messaging attributes

<!-- semconv messaging -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `messaging.system` | string | A string identifying the messaging system. | `kafka`; `rabbitmq`; `rocketmq`; `activemq`; `AmazonSQS` | Required |
| `messaging.destination` | string | The message destination name. This might be equal to the span name but is required nevertheless. | `MyQueue`; `MyTopic` | Required |
| `messaging.destination_kind` | string | The kind of message destination | `queue` | Conditionally Required: [1] |
| `messaging.temp_destination` | boolean | A boolean that is true if the message destination is temporary. |  | Conditionally Required: [2] |
| `messaging.protocol` | string | The name of the transport protocol. | `AMQP`; `MQTT` | Recommended |
| `messaging.protocol_version` | string | The version of the transport protocol. | `0.9.1` | Recommended |
| `messaging.url` | string | Connection string. | `tibjmsnaming://localhost:7222`; `https://queue.amazonaws.com/80398EXAMPLE/MyQueue` | Recommended |
| `messaging.message_id` | string | A value used by the messaging system as an identifier for the message, represented as a string. | `452a7c7c7c7048c2f887f61572b18fc2` | Recommended |
| `messaging.conversation_id` | string | The [conversation ID](#conversations) identifying the conversation to which the message belongs, represented as a string. Sometimes called "Correlation ID". | `MyConversationId` | Recommended |
| `messaging.message_payload_size_bytes` | int | The (uncompressed) size of the message payload in bytes. Also use this attribute if it is unknown whether the compressed or uncompressed payload size is reported. | `2738` | Recommended |
| `messaging.message_payload_compressed_size_bytes` | int | The compressed size of the message payload in bytes. | `2048` | Recommended |
| [`net.peer.name`](span-general.md) | string | Logical remote hostname, see note below. [3] | `example.com` | Conditionally Required: If available. |
| [`net.sock.family`](span-general.md) | string | Protocol [address family](https://man7.org/linux/man-pages/man7/address_families.7.html) which is used for communication. | `inet6`; `bluetooth` | Conditionally Required: [4] |
| [`net.sock.peer.addr`](span-general.md) | string | Remote socket peer address: IPv4 or IPv6 for internet protocols, path for local communication, [etc](https://man7.org/linux/man-pages/man7/address_families.7.html). | `127.0.0.1`; `/tmp/mysql.sock` | Recommended |
| [`net.sock.peer.name`](span-general.md) | string | Remote socket peer name. | `proxy.example.com` | Recommended: [5] |
| [`net.sock.peer.port`](span-general.md) | int | Remote socket peer port. | `16456` | Recommended: [6] |

**[1]:** If the message destination is either a `queue` or `topic`.

**[2]:** If value is `true`. When missing, the value is assumed to be `false`.

**[3]:** This should be the IP/hostname of the broker (or other network-level peer) this specific message is sent to/received from.

**[4]:** If different than `inet` and if any of `net.sock.peer.addr` or `net.sock.host.addr` are set. Consumers of telemetry SHOULD expect to receive IPv6 address in `net.sock.peer.addr` without `net.sock.family` coming from instrumentations that follow previous versions of this document.

**[5]:** If different than `net.peer.name` and if `net.sock.peer.addr` is set.

**[6]:** If defined for the address family and if different than `net.peer.port` and if `net.sock.peer.addr` is set.

`messaging.destination_kind` MUST be one of the following:

| Value  | Description |
|---|---|
| `queue` | A message sent to a queue |
| `topic` | A message sent to a topic |
<!-- endsemconv -->

Additionally `net.peer.port` from the [network attributes][] is recommended.
Furthermore, it is strongly recommended to add the [`net.transport`][] attribute and follow its guidelines, especially for in-process queueing systems (like [Hangfire][], for example).
These attributes should be set to the broker to which the message is sent/from which it is received.

[network attributes]: span-general.md#general-network-connection-attributes
[`net.transport`]: span-general.md#network-transport-attributes
[Hangfire]: https://www.hangfire.io/

For message consumers, the following additional attributes may be set:

<!-- semconv messaging.consumer -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `messaging.operation` | string | A string identifying the kind of message consumption as defined in the [Operation names](#operation-names) section above. If the operation is "send", this attribute MUST NOT be set, since the operation can be inferred from the span kind in that case. | `receive` | Recommended |
| `messaging.consumer_id` | string | The identifier for the consumer receiving a message. For Kafka, set it to `{messaging.kafka.consumer_group} - {messaging.kafka.client_id}`, if both are present, or only `messaging.kafka.consumer_group`. For brokers, such as RabbitMQ and Artemis, set it to the `client_id` of the client consuming the message. | `mygroup - client-6` | Recommended |

`messaging.operation` MUST be one of the following:

| Value  | Description |
|---|---|
| `receive` | receive |
| `process` | process |
<!-- endsemconv -->

The *receive* span is be used to track the time used for receiving the message(s), whereas the *process* span(s) track the time for processing the message(s).
Note that one or multiple Spans with `messaging.operation` = `process` may often be the children of a Span with `messaging.operation` = `receive`.
The distinction between receiving and processing of messages is not always of particular interest or sometimes hidden away in a framework (see the [Message consumption](#message-consumption) section above) and therefore the attribute can be left out.
For batch receiving and processing (see the [Batch receiving](#batch-receiving) and [Batch processing](#batch-processing) examples below) in particular, the attribute SHOULD be set.
Even though in that case one might think that the processing span's kind should be `INTERNAL`, that kind MUST NOT be used.
Instead span kind should be set to either `CONSUMER` or `SERVER` according to the rules defined above.

### Attributes specific to certain messaging systems

#### RabbitMQ

In RabbitMQ, the destination is defined by an *exchange* and a *routing key*.
`messaging.destination` MUST be set to the name of the exchange. This will be an empty string if the default exchange is used.

<!-- semconv messaging.rabbitmq -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `messaging.rabbitmq.routing_key` | string | RabbitMQ message routing key. | `myKey` | Conditionally Required: If not empty. |
<!-- endsemconv -->

#### Apache Kafka

For Apache Kafka, the following additional attributes are defined:

<!-- semconv messaging.kafka -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `messaging.kafka.message_key` | string | Message keys in Kafka are used for grouping alike messages to ensure they're processed on the same partition. They differ from `messaging.message_id` in that they're not unique. If the key is `null`, the attribute MUST NOT be set. [1] | `myKey` | Recommended |
| `messaging.kafka.consumer_group` | string | Name of the Kafka Consumer Group that is handling the message. Only applies to consumers, not producers. | `my-group` | Recommended |
| `messaging.kafka.client_id` | string | Client Id for the Consumer or Producer that is handling the message. | `client-5` | Recommended |
| `messaging.kafka.partition` | int | Partition the message is sent to. | `2` | Recommended |
| `messaging.kafka.tombstone` | boolean | A boolean that is true if the message is a tombstone. |  | Conditionally Required: [2] |

**[1]:** If the key type is not string, it's string representation has to be supplied for the attribute. If the key has no unambiguous, canonical string form, don't include its value.

**[2]:** If value is `true`. When missing, the value is assumed to be `false`.
<!-- endsemconv -->

For Apache Kafka producers, [`peer.service`](./span-general.md#general-remote-service-attributes) SHOULD be set to the name of the broker or service the message will be sent to.
The `service.name` of a Consumer's Resource SHOULD match the `peer.service` of the Producer, when the message is directly passed to another service.
If an intermediary broker is present, `service.name` and `peer.service` will not be the same.

#### Apache RocketMQ

Specific attributes for Apache RocketMQ are defined below.

<!-- semconv messaging.rocketmq -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `messaging.rocketmq.namespace` | string | Namespace of RocketMQ resources, resources in different namespaces are individual. | `myNamespace` | Required |
| `messaging.rocketmq.client_group` | string | Name of the RocketMQ producer/consumer group that is handling the message. The client type is identified by the SpanKind. | `myConsumerGroup` | Required |
| `messaging.rocketmq.client_id` | string | The unique identifier for each client. | `myhost@8742@s8083jm` | Required |
| `messaging.rocketmq.message_type` | string | Type of message. | `normal` | Recommended |
| `messaging.rocketmq.message_tag` | string | The secondary classifier of message besides topic. | `tagA` | Recommended |
| `messaging.rocketmq.message_keys` | string[] | Key(s) of message, another way to mark message besides message id. | `[keyA, keyB]` | Recommended |
| `messaging.rocketmq.consumption_model` | string | Model of message consumption. This only applies to consumer spans. | `clustering` | Recommended |

`messaging.rocketmq.message_type` MUST be one of the following:

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
| Span name | `"T send"` | `"T process"` | `"T process"` |
| Parent |  | Span Prod1 | Span Prod1 |
| Links |  |  |  |
| SpanKind | `PRODUCER` | `CONSUMER` | `CONSUMER` |
| Status | `Ok` | `Ok` | `Ok` |
| `net.peer.name` | `"ms"` | `"ms"` | `"ms"` |
| `net.peer.port` | `1234` | `1234` | `1234` |
| `messaging.system` | `"rabbitmq"` | `"rabbitmq"` | `"rabbitmq"` |
| `messaging.destination` | `"T"` | `"T"` | `"T"` |
| `messaging.destination_kind` | `"topic"` | `"topic"` | `"topic"` |
| `messaging.operation` |  | `"process"` | `"process"` |
| `messaging.message_id` | `"a1"` | `"a1"`| `"a1"` |

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
| Span name | `"T1 send"` | `"T1 receive"` | `"T1 process"` | `"T2 send"` | `"T2 receive`" |
| Parent |  | Span Prod1 | Span Rcv1 | Span Rcv1 | Span Prod2 |
| Links |  |  | |  |  |
| SpanKind | `PRODUCER` | `CONSUMER` | `CONSUMER` | `PRODUCER` | `CONSUMER` |
| Status | `Ok` | `Ok` | `Ok` | `Ok` | `Ok` |
| `peer.service` | `"myKafka"` |  |  | `"myKafka"` |  |
| `service.name` |  | `"myConsumer1"` | `"myConsumer1"` |  | `"myConsumer2"` |
| `messaging.system` | `"kafka"` | `"kafka"` | `"kafka"` | `"kafka"` | `"kafka"` |
| `messaging.destination` | `"T1"` | `"T1"` | `"T1"` | `"T2"` | `"T2"` |
| `messaging.destination_kind` | `"topic"` | `"topic"` | `"topic"` | `"topic"` | `"topic"` |
| `messaging.operation` |  |  | `"process"` |  | `"receive"` |
| `messaging.kafka.message_key` | `"myKey"` | `"myKey"` | `"myKey"` | `"anotherKey"` | `"anotherKey"` |
| `messaging.kafka.consumer_group` |  | `"my-group"` | `"my-group"` |  | `"another-group"` |
| `messaging.kafka.client_id` |  | `"5"` | `"5"` | `"5"` | `"8"` |
| `messaging.kafka.partition` |  | `"1"` | `"1"` |  | `"3"` |

### Batch receiving

Given is a process P, that sends two messages to a queue Q on messaging system MS, and a process C, which receives both of them in one batch (Span Recv1) and processes each message separately (Spans Proc1 and Proc2).

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
| Span name | `"Q send"` | `"Q send"` | `"Q receive"` | `"Q process"` | `"Q process"` |
| Parent |  |  |  | Span Recv1 | Span Recv1 |
| Links |  |  |  | Span Prod1 | Span Prod2 |
| SpanKind | `PRODUCER` | `PRODUCER` | `CONSUMER` | `CONSUMER` | `CONSUMER` |
| Status | `Ok` | `Ok` | `Ok` | `Ok` | `Ok` |
| `net.peer.name` | `"ms"` | `"ms"` | `"ms"` | `"ms"` | `"ms"` |
| `net.peer.port` | `1234` | `1234` | `1234` | `1234` | `1234` |
| `messaging.system` | `"rabbitmq"` | `"rabbitmq"` | `"rabbitmq"` | `"rabbitmq"` | `"rabbitmq"` |
| `messaging.destination` | `"Q"` | `"Q"` | `"Q"` | `"Q"` | `"Q"` |
| `messaging.destination_kind` | `"queue"` | `"queue"` | `"queue"` | `"queue"` | `"queue"` |
| `messaging.operation` |  |  | `"receive"` | `"process"` | `"process"` |
| `messaging.message_id` | `"a1"` | `"a2"` | | `"a1"` | `"a2"` |

### Batch processing

Given is a process P, that sends two messages to a queue Q on messaging system MS, and a process C, which receives both of them separately (Span Recv1 and Recv2) and processes both messages in one batch (Span Proc1).

Since each span can only have one parent, C3 should not choose a random parent out of C1 and C2, but rather rely on the implicitly selected parent as defined by the [tracing API spec](../api.md).
Similarly, only one value can be set as `message_id`, so C3 cannot report both `a1` and `a2` and therefore attribute is left out.
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
| Span name | `"Q send"` | `"Q send"` | `"Q receive"` | `"Q receive"` | `"Q process"` |
| Parent |  |  | Span Prod1 | Span Prod2 |  |
| Links |  |  |  |  | Span Prod1 + Prod2 |
| SpanKind | `PRODUCER` | `PRODUCER` | `CONSUMER` | `CONSUMER` | `CONSUMER` |
| Status | `Ok` | `Ok` | `Ok` | `Ok` | `Ok` |
| `net.peer.name` | `"ms"` | `"ms"` | `"ms"` | `"ms"` | `"ms"` |
| `net.peer.port` | `1234` | `1234` | `1234` | `1234` | `1234` |
| `messaging.system` | `"rabbitmq"` | `"rabbitmq"` | `"rabbitmq"` | `"rabbitmq"` | `"rabbitmq"` |
| `messaging.destination` | `"Q"` | `"Q"` | `"Q"` | `"Q"` | `"Q"` |
| `messaging.destination_kind` | `"queue"` | `"queue"` | `"queue"` | `"queue"` | `"queue"` |
| `messaging.operation` |  |  | `"receive"` | `"receive"` | `"process"` |
| `messaging.message_id` | `"a1"` | `"a2"` | `"a1"` | `"a2"` | |
