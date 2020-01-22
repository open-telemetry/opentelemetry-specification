# Messaging systems

> 🚧 WORK IN PROGRESS

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [Definitions](#definitions)
- [Conventions](#conventions)
- [Messaging attributes](#messaging-attributes)

<!-- tocstop -->

## Definitions

Although messaging systems are not as standardized as, e.g., HTTP, it is assumed that the following definitions are applicable to most of them that have similar concepts at all (names borrowed mostly from JMS):

A *message* usually consists of headers (or properties, or meta information) and an optional body. It is sent by a single message *producer* to:

* Physically: some message *broker* (which can be e.g., a single server, or a cluster, or a local process reached via IPC). The broker handles the actual routing, delivery, re-delivery, persistence, etc. In some messaging systems the broker may be identical or co-located with (some) message consumers.
* Logically: some particular message *destination*.

A destination is usually identified by some name unique within the messaging system instance, which might look like an URL or a simple one-word identifier. Two kinds of targets are are distinguished: *topic*s and *queue*s.
A message that is sent (the send-operation is often called "*publish*" in this context) to a *topic* is broadcasted to all *subscribers* of the topic.
A message submitted to a queue is processed by a message *consumer* (usually exactly once although some message systems support a more performant at least once-mode for messages with [idempotent][] processing).

The consumption of a message can happen in multiple steps:
First, the lower-level receiving of a message at a consumer, and then the logical processing of the message.
For receiving, the consumer may have the choice between peeking a destination to get a message back only if one is currently available
(for the purpose of this document, it is not relevant whether the message is removed from the destination or not by the "peek" operation),
or waiting until a message is received.
Often, the waiting for a message is not particularly interesting and hidden away in a framework that only invokes some handler function to process a message once one is received
(in the same way that the listening on a TCP port for an incoming HTTP message is not particularly interesting).
However, in a synchronous conversation, the wait time for a message is important.

In some messaging systems, a message can receive a reply message that answers a particular other message that was sent earlier. All messages that are grouped together by such a reply-relationship are called a *conversation*. The grouping usually happens through some sort of "In-Reply-To:" meta information or an explicit conversation ID. Sometimes a conversation can span multiple message targets (e.g. initiated via a topic, continued on a temporary one-to-one queue).

Some messaging systems support the concept of *temporary destination* (often only temporary queues) that are established just for a particular set of communication partners (often one to one) or conversation. Often such destinations are unnamed or have an auto-generated name.

[idempotent]: https://en.wikipedia.org/wiki/Idempotence

## Conventions

Given these definitions, the remainder of this section describes the semantic conventions that shall be followed for Spans describing interactions with messaging systems.

**Span name:** The span name should usually be set to the message destination name.
The conversation ID should be used instead when it is expected to have lower cardinality.
In particular, the conversation ID must be used if the message destination is unnamed or temporary.

**Span kind:** A producer of a message should set the span kind to `PRODUCER` unless it synchronously waits for a response: then it should use `CLIENT`.
The processor of the message should set the kind to `CONSUMER`, unless it always sends back a reply that is directed to the producer of the message
(as opposed to e.g., a queue on which the producer happens to listen): then it should use `SERVER`.

## Messaging attributes

| Attribute name |                          Notes and examples                            | Required? |
| -------------- | ---------------------------------------------------------------------- | --------- |
| `component`    | Denotes the type of the span and needs to be `"msg"`.                  | Yes       |
| `msg.flavor`   | A string identifying the messaging system kind used. Should be of the form `KIND.TECH`, e.g. `JMS.Web Sphere` or `AMQP.RabbitMQ`. | Yes |
| `msg.dst`      | The message destination name, e.g. `"MyQueue"` or `"MyTopic"`. | Yes       |
| `msg.dst_kind` | The kind of message destination: Either `"queue"` or `"topic"`.        | Yes       |
| `msg.tmp_dst`  | A boolean that is `true` if the message destination is temporary. | If temporary (assumed to be `false` if missing). |
| `msg.id`       | An integer or string used by the messaging system as an identifier for the message. | No |
| `msg.conversation_id` | An integer or string identifying the conversation to which the message belongs. Sometimes called "correlation ID". | No |

It is strongly recommended to also set at least the [network attributes][] `net.peer.ip`, `net.peer.name` and `net.peer.port`.

[network attributes]: data-span-general.md#general-network-connection-attributes

For message consumers, the following additional attributes may be set:

| Attribute name |                          Notes and examples                            | Required? |
| -------------- | ---------------------------------------------------------------------- | --------- |
| `msg.op` | A string identifying which part and kind of message consumption this span describes: `recv`, `peek` or `proc`. (If the operation is `send`, this attribute must not be set: the operation can be inferred from the span kind in that case.) | No |
| `msg.peeked_some` |  A boolean indicating whether a `peek` operation resulted in a received message or not. Must only be added if `msg.op` is `peek`. I missing, assumed to be `true` if `msg.id` is set, otherwise assumed to be `false`. | No |

Note that one or multiple Spans with `msg.op` = `proc` may often be the children of a Span with `msg.op` = `recv` or `peek`.
Even though in that case one might think that the span kind is `INTERNAL`, that kind MUST NOT be used.
Instead span kind should be set to either `CONSUMER` or `SERVER` according to the rules defined above.