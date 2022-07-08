<!--- Hugo front matter used to generate the website version of this page:
linkTitle: Kafka
--->

# Instrumenting Kafka

**Status**: [Experimental](../../../document-status.md)

This document defines how to apply semantic conventions when instrumenting Kafka.

<!-- toc -->

- [Kafka Metrics](#kafka-metrics)
- [Kafka Producer Metrics](#kafka-producer-metrics)
- [Kafka Consumer Metrics](#kafka-consumer-metrics)

<!-- tocstop -->

## Kafka Metrics

**Description:** General Kafka metrics.

| Name                                         | Instrument    | Value type | Unit   | Unit ([UCUM](../README.md#instrument-units)) | Description    | Attribute Key | Attribute Values |
| ---------------------------------------------| ------------- | ---------- | ------ | -------------------------------------------- | -------------- | ------------- | ---------------- |
| messaging.kafka.messages                     | Counter       | Int64      | messages | `{messages}` | The number of messages received by the broker. | | |
| messaging.kafka.requests.failed              | Counter       | Int64      | requests | `{requests}` | The number of requests to the broker resulting in a failure. | `type`  | `produce`, `fetch` |
| messaging.kafka.requests.queue               | UpDownCounter | Int64      | requests | `{requests}` | The number of requests in the request queue. | | |
| messaging.kafka.network.io                   | Counter       | Int64      | bytes | `by` | The bytes received or sent by the broker. | `state` | `in`, `out` |
| messaging.kafka.purgatory.size               | UpDownCounter | Int64      | requests | `{requests}` | The number of requests waiting in the purgatory.  | `type` | `produce`, `fetch` |
| messaging.kafka.partitions.all               | UpDownCounter | Int64      | partitions | `{partitions}` | The number of partitions in the broker.  | | |
| messaging.kafka.partitions.offline           | UpDownCounter | Int64      | partitions | `{partitions}` | The number of offline partitions. | | |
| messaging.kafka.partitions.under-replicated  | UpDownCounter | Int64      | partition  | `{partitions}` | The number of under replicated partitions. | | |
| messaging.kafka.isr.operations               | Counter       | Int64      | operations | `{operations}` | The number of in-sync replica shrink and expand operations. | `operation` | `shrink`, `expand` |
| messaging.kafka.max.lag                      | UpDownCounter | Int64      | messages   | `{messages}`   | Max lag in messages between follower and leader replicas. | | |
| messaging.kafka.controllers.active           | UpDownCounter | Int64      | controllers | `{controllers}` | The number of active controllers in the broker. | | |
| messaging.kafka.leader.elections             | Counter       | Int64      | elections | `{elections}` | Leader election rate (increasing values indicates broker failures). | | |
| messaging.kafka.leader.unclean-elections     | Counter       | Int64      | elections | `{elections}` | Unclean leader election rate (increasing values indicates broker failures). | | |
| messaging.kafka.brokers                      | UpDownCounter | Int64      | brokers   | `{brokers}`   | Number of brokers in the cluster. | | |
| messaging.kafka.topic.partitions             | UpDownCounter | Int64      | partitions | `{partitions}` | Number of partitions in topic. | `topic` | The ID (integer) of a topic |
| messaging.kafka.partition.current_offset     | Gauge         | Int64      | partition offset | `{partition offset}` | Current offset of partition of topic. | `topic` | The ID (integer) of a topic |
|                                              |               |            |                  |                      |                                       | `partition` | The number (integer) of the partition |
| messaging.kafka.partition.oldest_offset      | Gauge         | Int64      | partition offset | `{partition offset}` | Oldest offset of partition of topic | `topic` | The ID (integer) of a topic |
|                                              |               |            |                  |                      |                                     | `partition` | The number (integer) of the partition |
| messaging.kafka.partition.replicas.all       | UpDownCounter | Int64      | replicas | `{replicas}` | Number of replicas for partition of topic | `topic` | The ID (integer) of a topic |
|                                              |               |            |          |              |                                           | `partition` | The number (integer) of the partition |
| messaging.kafka.partition.replicas.in_sync   | UpDownCounter | Int64      | replicas | `{replicas}` | Number of synchronized replicas of partition | `topic` | The ID (integer) of a topic |
|                                              |               |            |          |              |                                              | `partition` | The number (integer) of the partition|

## Kafka Producer Metrics

**Description:** Kafka Producer level metrics.

| Name                                          | Instrument    | Value type | Unit   | Unit ([UCUM](../README.md#instrument-units)) | Description    | Attribute Key | Attribute Values |
| --------------------------------------------- | ------------- | ---------- | ------ | -------------------------------------------- | -------------- | ------------- | ---------------- |
| messaging.kafka.producer.outgoing-bytes.rate  | Gauge         | Double     | bytes per second | `by/s` | The average number of outgoing bytes sent per second to all servers. | `client-id` | `client-id` value |
| messaging.kafka.producer.responses.rate       | Gauge         | Double     | responses per second | `{responses}/s` | The average number of responses received per second. | `client-id` | `client-id` value |
| messaging.kafka.producer.bytes.rate           | Gauge         | Double     | bytes per second | `by/s` | The average number of bytes sent per second for a specific topic. | `client-id` | `client-id` value |
|                                               |               |            |                  |        |                                                                   | `topic`     | topic name        |
| messaging.kafka.producer.compression-ratio    | Gauge         | Double     | compression ratio | `{compression}` | The average compression ratio of record batches for a specific topic. | `client-id` | `client-id` value |
|                                               |               |            |                   |                 |                                                                       | `topic`     | topic name        |
| messaging.kafka.producer.record-error.rate    | Gauge         | Double     | error rate | `{errors}/s` | The average per-second number of record sends that resulted in errors for a specific topic.  | `client-id` | `client-id` value |
|                                               |               |            |            |              |                                                                                              | `topic`     | topic name        |
| messaging.kafka.producer.record-retry.rate    | Gauge         | Double     | retry rate | `{retries}/s` | The average per-second number of retried record sends for a specific topic. | `client-id` | `client-id` value  |
|                                               |               |            |            |               |                                                                             | `topic`     | topic name         |
| messaging.kafka.producer.record-sent.rate     | Gauge         | Double     | records sent rate | `{records_sent}/s` | The average number of records sent per second for a specific topic.  | `client-id` | `client-id` value  |
|                                               |               |            |                   |                    |                                                                      | `topic`     | topic name         |

## Kafka Consumer Metrics

**Description:** Kafka Consumer level metrics.

| Name                                          | Instrument    | Value type | Unit   | Unit ([UCUM](../README.md#instrument-units)) | Description    | Attribute Key | Attribute Values |
| --------------------------------------------- | ------------- | ---------- | ------ | -------------------------------------------- | -------------- | ------------- | ---------------- |
| messaging.kafka.consumer.members              | UpDownCounter | Int64      | members | `{members}` | Count of members in the consumer group | `group` | The ID (string) of a consumer group |
| messaging.kafka.consumer.offset               | Gauge         | Int64      | offset | `{offset}` | Current offset of the consumer group at partition of topic | `group` | The ID (string) of a consumer group |
|                                               |               |            |        |            |                                                            | `topic` | The ID (integer) of a topic |
|                                               |               |            |        |            |                                                            | `partition` | The number (integer) of the partition |
| messaging.kafka.consumer.offset_sum           | Gauge         | Int64      | offset sum | `{offset sum}` | Sum of consumer group offset across partitions of topic | `group` | The ID (string) of a consumer group |
|                                               |               |            |            |                |                                                         | `topic` | The ID (integer) of a topic |
| messaging.kafka.consumer.lag                  | Gauge         | Int64      | lag | `{lag}` | Current approximate lag of consumer group at partition of topic | `group` | The ID (string) of a consumer group |
|                                               |               |            |     |         |                                                                 | `topic` | The ID (integer) of a topic |
|                                               |               |            |     |         |                                                                 | `partition` | The number (integer) of the partition |
| messaging.kafka.consumer.lag_sum              | Gauge         | Int64      | lag sum | `{lag sum}` | Current approximate sum of consumer group lag across all partitions of topic | `group` | The ID (string) of a consumer group |
|                                               |               |            |         |             |                                                                              | `topic` | The ID (integer) of a topic |
