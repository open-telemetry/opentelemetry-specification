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

<!-- semconv messaging -->
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
| `messaging.producer.messages` | Counter | messages | Total number of messages sent. |
| `messaging.producer.duration` | ValueRecorder | milliseconds | Time spent producing a message to a queue/topic. |
| `messaging.producer.bytes` | ValueRecorder | bytes | The (uncompressed) size of the payload sent in bytes. Also use this metric if it is unknown whether the compressed or uncompressed payload size is reported. |
| `messaging.producer.compressed.bytes` | ValueRecorder | bytes | The compressed size of the payload sent in bytes. |

### Send Batch Metric Instruments

When a message system uses batching the following metric instruments SHOULD
be captured for every batch send operation.

| Name                 | Instrument    | Units        | Description |
|----------------------|---------------|--------------|-------------|
| `messaging.producer.batches` | Counter | batches | Total number of batches sent. |
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
| `messaging.consumer.messages` | Counter | messages | Total number of messages received. |
| `messaging.consumer.duration` | ValueRecorder | milliseconds | Time spent receiving a message from a queue/topic. |
| `messaging.consumer.bytes` | ValueRecorder | bytes | The (uncompressed) size of the message received in bytes. Also use this metric if it is unknown whether the compressed or uncompressed payload size is reported. |
| `messaging.consumer.compressed.bytes` | ValueRecorder | bytes | The compressed size of the payload sent in bytes. |

### Receive Batch Metric Instruments

When a message system uses batching the following metric instruments SHOULD
be captured for every batch receive operation.

| Name                 | Instrument    | Units        | Description |
|----------------------|---------------|--------------|-------------|
| `messaging.consumer.batches` | Counter | batches | Total number of batches received. |
| `messaging.consumer.batch.duration` | ValueRecorder | milliseconds | Time spent receiving a batch of messages from a queue/topic. |
| `messaging.consumer.batch.size` | ValueRecorder | messages | The number of messages in each batch if messages are consumed in batches. |
| `messaging.consumer.batch.bytes` | ValueRecorder | bytes | The (uncompressed) size of the batch received in bytes. Also use this metric if it is unknown whether the compressed or uncompressed batch size is reported. |
| `messaging.consumer.batch.compressed.bytes` | ValueRecorder | bytes | The compressed size of the batch received in bytes. |

## Process Message Metric Instruments

The following metric instruments SHOULD be captured for every message process operation.

| Name                 | Instrument    | Units        | Description |
|----------------------|---------------|--------------|-------------|
| `messaging.consumer.processed.messages` | Counter | messages | Total number of messages processed. |
| `messaging.consumer.processed.duration` | ValueRecorder | milliseconds | Time spent processing a message. |

Test
