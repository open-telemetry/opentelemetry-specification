# Messaging systems

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
- [Examples](#examples)
  * [Topic with multiple consumers](#topic-with-multiple-consumers)
  * [Batch receiving](#batch-receiving)
  * [Batch processing](#batch-processing)

<!-- tocstop -->

## Definitions

Although messaging systems are not as standardized as, e.g., HTTP, it is assumed that the following definitions are applicable to most of them that have similar concepts at all (names borrowed mostly from JMS):

A *message* usually consists of headers (or properties, or meta information) and an optional body. It is sent by a single message *producer* to:

* Physically: some message *broker* (which can be e.g., a single server, or a cluster, or a local process reached via IPC). The broker handles the actual routing, delivery, re-delivery, persistence, etc. In some messaging systems the broker may be identical or co-located with (some) message consumers.
* Logically: some particular message *destination*.

### Destinations

A destination is usually identified by some name unique within the messaging system instance, which might look like an URL or a simple one-word identifier.
Two kinds of destinations are distinguished: *topic*s and *queue*s.
A message that is sent (the send-operation is often called "*publish*" in this context) to a *topic* is broadcasted to all *subscribers* of the topic.
A message submitted to a queue is processed by a message *consumer* (usually exactly once although some message systems support a more performant at-least-once mode for messages with [idempotent][] processing).

[idempotent]: https://en.wikipedia.org/wiki/Idempotence

### Message consumption

The consumption of a message can happen in multiple steps.
First, the lower-level receiving of a message at a consumer, and then the logical processing of the message.
Often, the waiting for a message is not particularly interesting and hidden away in a framework that only invokes some handler function to process a message once one is received
(in the same way that the listening on a TCP port for an incoming HTTP message is not particularly interesting).
However, in a synchronous conversation, the wait time for a message is important.

### Conversations

In some messaging systems, a message can receive a reply message that answers a particular other message that was sent earlier. All messages that are grouped together by such a reply-relationship are called a *conversation*.
The grouping usually happens through some sort of "In-Reply-To:" meta information or an explicit *conversation ID* (sometimes called *correlation ID*).
Sometimes a conversation can span multiple message destinations (e.g. initiated via a topic, continued on a temporary one-to-one queue).

### Temporary destinations

Some messaging systems support the concept of *temporary destination* (often only temporary queues) that are established just for a particular set of communication partners (often one to one) or conversation.
Often such destinations are unnamed or have an auto-generated name.

## Conventions

Given these definitions, the remainder of this section describes the semantic conventions that shall be followed for Spans describing interactions with messaging systems.

### Span name

The span name SHOULD be set to the message destination name and the operation being performed in the following format:

```
<destination name> <operation name>
```

The destination name SHOULD only be used for the span name if it is known to be of low cardinality (cf. [general span name guidelines](../api.md#span)).
This can be assumed if it is statically derived from application code or configuration.
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

| Attribute name |                          Notes and examples                            | Required? |
| -------------- | ---------------------------------------------------------------------- | --------- |
| `messaging.system` | A string identifying the messaging system such as `kafka`, `rabbitmq` or `activemq`. | Yes |
| `messaging.destination` | The message destination name, e.g. `MyQueue` or `MyTopic`. This might be equal to the span name but is required nevertheless. | Yes |
| `messaging.destination_kind` | The kind of message destination: Either `queue` or `topic`. | Yes, if either of them applies. |
| `messaging.temp_destination` | A boolean that is `true` if the message destination is [temporary](#temporary-destinations). | If temporary (assumed to be `false` if missing). |
| `messaging.protocol` | The name of the transport protocol such as `AMQP` or `MQTT`. | No |
| `messaging.protocol_version` | The version of the transport protocol such as `0.9.1`. | No |
| `messaging.url` | Connection string such as `tibjmsnaming://localhost:7222` or `https://queue.amazonaws.com/80398EXAMPLE/MyQueue`. | No |
| `messaging.message_id` | A value used by the messaging system as an identifier for the message, represented as a string. | No |
| `messaging.conversation_id` | The [conversation ID](#conversations) identifying the conversation to which the message belongs, represented as a string. Sometimes called "Correlation ID". | No |
| `messaging.message_payload_size_bytes` | The (uncompressed) size of the message payload in bytes. Also use this attribute if it is unknown whether the compressed or uncompressed payload size is reported. | No |
| `messaging.message_payload_compressed_size_bytes` | The compressed size of the message payload in bytes. | No |

Additionally at least one of `net.peer.name` or `net.peer.ip` from the [network attributes][] is required and `net.peer.port` is recommended.
Furthermore, it is strongly recommended to add the [`net.transport`][] attribute and follow its guidelines, especially for in-process queueing systems (like [Hangfire][], for example).
These attributes should be set to the broker to which the message is sent/from which it is received.

[network attributes]: span-general.md#general-network-connection-attributes
[`net.transport`]: span-general.md#nettransport-attribute
[Hangfire]: https://www.hangfire.io/

For message consumers, the following additional attributes may be set:

| Attribute name |                          Notes and examples                            | Required? |
| -------------- | ---------------------------------------------------------------------- | --------- |
| `messaging.operation` | A string identifying the kind of message consumption as defined in the [Operation names](#operation-names) section above. Only `"receive"` and `"process"` are used for this attribute. If the operation is `"send"`, this attribute MUST NOT be set, since the operation can be inferred from the span kind in that case. | No |

The _receive_ span is be used to track the time used for receiving the message(s), whereas the _process_ span(s) track the time for processing the message(s).
Note that one or multiple Spans with `messaging.operation` = `process` may often be the children of a Span with `messaging.operation` = `receive`.
The distinction between receiving and processing of messages is not always of particular interest or sometimes hidden away in a framework (see the [Message consumption](#message-consumption) section above) and therefore the attribute can be left out.
For batch receiving and processing (see the [Batch receiving](#batch-receiving) and [Batch processing](#batch-processing) examples below) in particular, the attribute SHOULD be set.
Even though in that case one might think that the processing span's kind should be `INTERNAL`, that kind MUST NOT be used.
Instead span kind should be set to either `CONSUMER` or `SERVER` according to the rules defined above.

### Attributes specific to certain messaging systems

#### RabbitMQ

In RabbitMQ, the destination is defined by an _exchange_ and a _routing key_.
`messaging.destination` MUST be set to the name of the exchange. This will be an empty string if the default exchange is used.
The routing key MUST be provided to the attribute `messaging.rabbitmq.routing_key`, unless it is empty.

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
| `messaging.system` | `"kafka"` | `"kafka"` | `"kafka"` |
| `messaging.destination` | `"T"` | `"T"` | `"T"` |
| `messaging.destination_kind` | `"topic"` | `"topic"` | `"topic"` |
| `messaging.operation` |  | `"process"` | `"process"` |
| `messaging.message_id` | `"a1"` | `"a1"`| `"a1"` |

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
| `messaging.system` | `"kafka"` | `"kafka"` | `"kafka"` | `"kafka"` | `"kafka"` |
| `messaging.destination` | `"Q"` | `"Q"` | `"Q"` | `"Q"` | `"Q"` |
| `messaging.destination_kind` | `"queue"` | `"queue"` | `"queue"` | `"queue"` | `"queue"` |
| `messaging.operation` |  |  | `"receive"` | `"process"` | `"process"` |
| `messaging.message_id` | `"a1"` | `"a2"` | | `"a1"` | `"a2"` |

### Batch processing

Given is a process P, that sends two messages to a queue Q on messaging system MS, and a process C, which receives both of them separately (Span Recv1 and Recv2) and processes both messages in one batch (Span Proc1).

Since each span can only have one parent, C3 should not choose a random parent out of C1 and C2, but rather rely on the implicitly selected parent as defined by the [tracing API spec](../api.md).
Similarly, only one value can be set as `message_id`, so C3 cannot report both `a1` and `a2` and therefore attribute is left out.
Depending on the implementation, the producing spans might still be available in the meta data of the messages and should be added to C3 as links.
The client library or application could also add the receiver span's span context to the data structure it returns for each message. In this case, C3 could also add links to the receiver spans C1 and C2.

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
| `messaging.system` | `"kafka"` | `"kafka"` | `"kafka"` | `"kafka"` | `"kafka"` |
| `messaging.destination` | `"Q"` | `"Q"` | `"Q"` | `"Q"` | `"Q"` |
| `messaging.destination_kind` | `"queue"` | `"queue"` | `"queue"` | `"queue"` | `"queue"` |
| `messaging.operation` |  |  | `"receive"` | `"receive"` | `"process"` |
| `messaging.message_id` | `"a1"` | `"a2"` | `"a1"` | `"a2"` | |
