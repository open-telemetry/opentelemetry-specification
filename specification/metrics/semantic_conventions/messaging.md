# Semantic conventions for messaging system metrics

The conventions described in this section are specific to messaging systems. When interactions with messaging systems occur,
metric events about those operations will be generated and reported, providing insight into those
operations.

**Disclaimer:** These are initial messaging system metric instruments and labels, more may be added
 in the future.

## Definitions

The [Trace Messaging Semantic Conventions Definitions](../../trace/semantic_conventions/messaging.md#definitions) is a resource for the messaging system terminology used in this document.

## Common Labels

The following labels **SHOULD** be applied to all messaging metric instruments.

<!-- semconv metrics-messaging -->
| Attribute  | Type | Description  | Example  | Required |
|---|---|---|---|---|
| [`messaging.destination`](../../trace/semantic_conventions/messaging.md) | string | The message destination name. This might be equal to the span name but is required nevertheless. | `MyQueue`<br>`MyTopic` | Yes |
| [`messaging.destination_kind`](../../trace/semantic_conventions/messaging.md) | string enum | The kind of message destination | `queue` | Yes |
| [`messaging.protocol`](../../trace/semantic_conventions/messaging.md) | string | The name of the transport protocol. | `AMQP`<br>`MQTT` | No |
| [`messaging.protocol_version`](../../trace/semantic_conventions/messaging.md) | string | The version of the transport protocol. | `0.9.1` | No |
| [`messaging.system`](../../trace/semantic_conventions/messaging.md) | string | A string identifying the messaging system. | `kafka`<br>`rabbitmq`<br>`activemq` | Yes |
| [`messaging.temp_destination`](../../trace/semantic_conventions/messaging.md) | boolean | A boolean that is true if the message destination is temporary. |  | No |
| [`messaging.url`](../../trace/semantic_conventions/messaging.md) | string | Connection string. | `tibjmsnaming://localhost:7222`<br>`https://queue.amazonaws.com/80398EXAMPLE/MyQueue` | No |
| [`net.peer.ip`](../../trace/semantic_conventions/span-general.md) | string | Remote address of the peer (dotted decimal for IPv4 or [RFC5952](https://tools.ietf.org/html/rfc5952) for IPv6) | `127.0.0.1` | No |
| [`net.peer.name`](../../trace/semantic_conventions/span-general.md) | string | Remote hostname or similar, see note below. | `example.com` | No |
| [`net.peer.port`](../../trace/semantic_conventions/span-general.md) | number | Remote port number. | `80`<br>`8080`<br>`443` | No |
| [`net.transport`](../../trace/semantic_conventions/span-general.md) | string enum | Transport protocol used. See note below. | `IP.TCP` | No |
<!-- endsemconv -->

For messaging metric labels, one of the following sets of labels is RECOMMENDED (in order of usual preference unless for a particular messaging system it is known that some other set is preferable for some reason; all strings must be non-empty):

* `messaging.url`
* `net.peer.name`, `net.peer.port`, `net.peer.ip`, `net.transport`

## Send Message Metric Instruments

The following metric instruments SHOULD be captured for every message send operation
 unless the producer is batching. If the producer is batching some metrics may be
 omitted (e.g. `messaging.producer.duration` and `messaging.producer.compressed.bytes`).

| Name                 | Instrument    | Units        | Description |
|----------------------|---------------|--------------|-------------|
| `messaging.producer.duration` | ValueRecorder | milliseconds | Time spent producing a message to a queue/topic. |
| `messaging.producer.bytes` | ValueRecorder | bytes | The (uncompressed) size of the payload sent in bytes. Also use this metric if it is unknown whether the compressed or uncompressed payload size is reported. |
| `messaging.producer.compressed.bytes` | ValueRecorder | bytes | The compressed size of the payload sent in bytes. |

### Send Batch Metric Instruments

When a message system uses batching the following metric instruments SHOULD
be captured for every batch send operation.

| Name                 | Instrument    | Units        | Description |
|----------------------|---------------|--------------|-------------|
| `messaging.producer.batch.duration` | ValueRecorder | milliseconds | Time spent prodcing a batch of messages to a queue/topic. |
| `messaging.producer.batch.size` | ValueRecorder | messages | The number of messages in each batch if this producer/client is batching messages. |
| `messaging.producer.batch.bytes` | ValueRecorder | bytes | The (uncompressed) size of the batch sent in bytes. Also use this metric if it is unknown whether the compressed or uncompressed batch size is reported. |
| `messaging.producer.batch.compressed.bytes` | ValueRecorder | bytes | The compressed size of the batch sent in bytes. |

## Receive Message Metric Instruments

The following metric instruments SHOULD be captured for every message receive operation
 unless the consumer is receiving batches. If the consumer is receiving batches some metrics
 may be omitted (e.g. `messaging.consumer.duration` and `messaging.consumer.compressed.bytes`).

| Name                 | Instrument    | Units        | Description |
|----------------------|---------------|--------------|-------------|
| `messaging.consumer.received.duration` | ValueRecorder | milliseconds | Time spent receiving a message from a queue/topic. |
| `messaging.consumer.received.bytes` | ValueRecorder | bytes | The (uncompressed) size of the message received in bytes. Also use this metric if it is unknown whether the compressed or uncompressed payload size is reported. |
| `messaging.consumer.received.compressed.bytes` | ValueRecorder | bytes | The compressed size of the payload sent in bytes. |

### Receive Batch Metric Instruments

When a message system uses batching the following metric instruments SHOULD
be captured for every batch receive operation.

| Name                 | Instrument    | Units        | Description |
|----------------------|---------------|--------------|-------------|
| `messaging.consumer.received.batch.duration` | ValueRecorder | milliseconds | Time spent receiving a batch of messages from a queue/topic. |
| `messaging.consumer.received.batch.size` | ValueRecorder | messages | The number of messages in each batch if messages are consumed in batches. |
| `messaging.consumer.received.batch.bytes` | ValueRecorder | bytes | The (uncompressed) size of the batch received in bytes. Also use this metric if it is unknown whether the compressed or uncompressed batch size is reported. |
| `messaging.consumer.received.batch.compressed.bytes` | ValueRecorder | bytes | The compressed size of the batch received in bytes. |

## Process Message Metric Instruments

The following metric instruments SHOULD be captured for every message process operation.

| Name                 | Instrument    | Units        | Description |
|----------------------|---------------|--------------|-------------|
| `messaging.consumer.processed.duration` | ValueRecorder | milliseconds | Time spent processing a message. |
