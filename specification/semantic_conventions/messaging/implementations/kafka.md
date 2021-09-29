# Apache Kafka

**Status**: [Experimental](../../../document-status.md)

## Requirements

For Apache Kafka producers, [`peer.service`](./span-general.md#general-remote-service-attributes) SHOULD be set to the name of the broker or service the message will be sent to.
The `service.name` of a Consumer's Resource SHOULD match the `peer.service` of the Producer, when the message is directly passed to another service.
If an intermediary broker is present, `service.name` and `peer.service` will not be the same.

## Attributes

<!-- semconv messaging.kafka -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `messaging.kafka.message_key` | string | Message keys in Kafka are used for grouping alike messages to ensure they're processed on the same partition. They differ from `messaging.message_id` in that they're not unique. If the key is `null`, the attribute MUST NOT be set. [1] | `myKey` | No |
| `messaging.kafka.consumer_group` | string | Name of the Kafka Consumer Group that is handling the message. Only applies to consumers, not producers. | `my-group` | No |
| `messaging.kafka.client_id` | string | Client Id for the Consumer or Producer that is handling the message. | `client-5` | No |
| `messaging.kafka.partition` | int | Partition the message is sent to. | `2` | No |
| `messaging.kafka.tombstone` | boolean | A boolean that is true if the message is a tombstone. |  | If missing, it is assumed to be false. |

**[1]:** If the key type is not string, it's string representation has to be supplied for the attribute. If the key has no unambiguous, canonical string form, don't include its value.
<!-- endsemconv -->

## Examples

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