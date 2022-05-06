# Instrumenting Kafka

**Status**: [Experimental](../../../document-status.md)

This document defines how to apply semantic conventions when instrumenting Kafka.

<!-- toc -->

<!-- Re-generate TOC with `markdown-toc no-first-h1 -i` -->

<!-- tocstop -->

## Kafka Metrics

**Description:** General Kafka metrics.

| Name                                 | Instrument    | Value type | Unit   | Unit ([UCUM](README.md#instrument-units)) | Description    | Attribute Key | Attribute Values |
| ------------------------------------ | ------------- | ---------- | ------ | ----------------------------------------- | -------------- | ------------- | ---------------- |
| kafka.message.count                  | Counter       | Int64      | messages | `{messages}` | The number of messages received by the broker. | | |
| kafka.request.failed                 | Counter       | Int64      | requests | `{requests}` | The number of requests to the broker resulting in a failure. | `type`  | `produce`, `fetch` |
| kafka.request.queue                  | UpDownCounter | Int64      | requests | `{requests}` | The number of requests in the request queue. | | |
| kafka.network.io                     | Counter       | Int64      | bytes | `by` | The bytes received or sent by the broker. | `state` | `in`, `out` |
| kafka.purgatory.size                 | UpDownCounter | Int64      | requests | `{requests}` | The number of requests waiting in the purgatory.  | `type` | `produce`, `fetch` |
| kafka.partition.count                | UpDownCounter | Int64      | partitions | `{partitions}` | The number of partitions in the broker.  | | |
| kafka.partition.offline              | UpDownCounter | Int64      | partitions | `{partitions}` | The number of offline partitions. | | |
| kafka.partition.under_replicated     | UpDownCounter | Int64      | partition  | `{partitions}` | The number of under replicated partitions. | | |
| kafka.isr.operation.count            | Counter       | Int64      | operations | `{operations}` | The number of in-sync replica shrink and expand operations. | `operation` | `shrink`, `expand` |
| kafka.max.lag                        | UpDownCounter | Int64      | messages   | `{messages}`   | Max lag in messages between follower and leader replicas. | | |
| kafka.controller.active.count        | UpDownCounter | Int64      | controllers | `{controllers}` | The number of active controllers in the broker. | | |
| kafka.leader.elections               | Counter       | Int64      | elections | `{elections}` | Leader election rate (increasing values indicates broker failures). | | |
| kafka.leader.unclean-elections       | Counter       | Int64      | elections | `{elections}` | Unclean leader election rate (increasing values indicates broker failures). | | |

## Kafka Producer Metrics

**Description:** Kafka Producer level metrics.

| Name                                 | Instrument    | Value type | Unit   | Unit ([UCUM](README.md#instrument-units)) | Description    | Attribute Key | Attribute Values |
| ------------------------------------ | ------------- | ---------- | ------ | ----------------------------------------- | -------------- | ------------- | ---------------- |
| kafka.producer.outgoing-byte-rate    | UpDownCounter | Double     | bytes | `by`| The average number of outgoing bytes sent per second to all servers. | `client-id` | `client-id` value |
| kafka.producer.response-rate         | UpDownCounter | Double     | responses | `{responses}` | The average number of responses received per second. | `client-id` | `client-id` value |
| kafka.producer.byte-rate             | UpDownCounter | Double     | bytes | `by` | The average number of bytes sent per second for a specific topic. | `client-id` | `client-id` value |
|                                      |               |            |       |      |                                                                   | `topic`     | topic name        |
| kafka.producer.compression-ratio     | Gauge         | Double     | compression ratio | `{compression}` | The average compression ratio of record batches for a specific topic. | `client-id` | `client-id` value |
|                                      |               |            |                  |                     |                                                                      | `topic`     | topic name        |
| kafka.producer.record-errors.rate    | Gauge         | Double     | error rate | `{error}s` | The average per-second number of record sends that resulted in errors for a specific topic.  | `client-id` | `client-id` value |
|                                      |               |            |            |               |                                                                                              | `topic`     | topic name        |
| kafka.producer.record-retry.rate     | Gauge         | Double     | retry rate | `{retries}` | The average per-second number of retried record sends for a specific topic. | `client-id` | `client-id` value  |
|                                      |               |            |            |               |                                                                             | `topic`     | topic name         |
| kafka.producer.record-sent.rate      | Gauge         | Double     | records sent rate | `{records_sent}` | The average number of records sent per second for a specific topic.  | `client-id` | `client-id` value  |
|                                      |               |            |                   |                     |                                                                      | `topic`     | topic name         |

