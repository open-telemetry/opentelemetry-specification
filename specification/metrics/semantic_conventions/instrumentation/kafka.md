# Instrumenting Kafka

**Status**: [Experimental](../../../document-status.md)

This document defines how to apply semantic conventions when instrumenting Kafka.

<!-- toc -->

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- tocstop -->

## Kafka Metrics

**Description:** General Kafka metrics.

| Name                                 | Instrument           | Value type | Unit | Unit ([UCUM](README.md#instrument-units)) | Description    | Attribute Key | Attribute Values |
| ------------------------------------ | -------------------- | ---------- | ---- | ----------------------------------------- | -------------- | ------------- | ---------------- |
| kafka.message.count                  | Asynchronous Counter | Int64      | messages | `{messages}` | The number of messages received by the broker. | | |
| kafka.request.count                  | Asynchronous Counter | Int64      | requests | `{requests}` | The number of requests received by the broker. | `type` | `produce`, `fetch` |
| kafka.request.failed                 | Asynchronous Counter | Int64      | requests | `{requests}` | The number of requests to the broker resulting in a failure. | `type`  | `produce`, `fetch` |
| kafka.request.time.total             | Asynchronous Counter | Int64      | milliseconds | `ms` | The total time the broker has taken to service requests. | `type` | `Produce`, `FetchConsumer`, `FetchFollower` |
| kafka.request.time.50p               | Asynchronous Gauge   | Double     | milliseconds | `ms` | The 50th percentile time the broker has taken to service requests. | `type` | `Produce`, `FetchConsumer`, `FetchFollower` |
| kafka.request.time.99p               | Asynchronous Gauge   | Double     | milliseconds | `ms` | The 99th percentile time the broker has taken to service requests. | `type` | `Produce`, `FetchConsumer`, `FetchFollower` |
| kafka.request.queue                  | Asynchronous Gauge   | Int64      | requests | `{requests}` | The number of requests in the request queue. | | |
| kafka.network.io                     | Asynchronous Counter | Int64      | bytes | `by` | The bytes received or sent by the broker. | `state` | `in`, `out` |
| kafka.purgatory.size                 | Asynchronous Gauge   | Int64      | requests | `{requests}` | The number of requests waiting in the purgatory.  | `type` | `produce`, `fetch` |
| kafka.partition.count                | Asynchronous Gauge   | Int64      | partitions | `{partitions}` | The number of partitions in the broker.  | | |
| kafka.partition.offline              | Asynchronous Gauge   | Int64      | partitions | `{partitions}` | The number of offline partitions. | | |
| kafka.partition.under_replicated     | Asynchronous Gauge   | Int64      | partition  | `{partitions}` | The number of under replicated partitions. | | |
| kafka.isr.operation.count            | Asynchronous Counter | Int64      | operations | `{operations}` | The number of in-sync replica shrink and expand operations. | `operation` | `shrink`, `expand` |
| kafka.max.lag                        | Asynchronous Gauge   | Int64      | messages   | `{messages}`   | Max lag in messages between follower and leader replicas. | | |
| kafka.controller.active.count        | Asynchronous Gauge   | Int64      | controllers | `{controllers}` | Number of active controllers in the broker. | | |
| kafka.leader.election.rate           | Asynchronous Counter | Int64      | elections | `{elections}` | Leader election rate (increasing values indicates broker failures). | | |
| kafka.unclean.election.rate          | Asynchronous Counter | Int64      | elections | `{elections}` | Unclean leader election rate (increasing values indicates broker failures). | | |
| kafka.logs.flush.time.count          | Asynchronous Counter | Int64      | milliseconds | `ms` | The time it has taken to flush logs. | | |
| kafka.logs.flush.time.50th           | Asynchronous Gauge   | Double     | milliseconds | `ms` | The 50th percentile time it has taken to flush logs. | | |
| kafka.logs.flush.time.99th           | Asynchronous Gauge   | Double     | milliseconds | `ms` | The 99th percentile time it has taken to flush logs. | | |

## Kafka Producer Metrics

**Description:** Kafka Producer level metrics.

| Name                                 | Instrument         | Value type | Unit | Unit ([UCUM](README.md#instrument-units)) | Description    | Attribute Key | Attribute Values |
| ------------------------------------ | ------------------ | ---------- | ---- | ----------------------------------------- | -------------- | ------------- | ---------------- |
| kafka.producer.io-wait-time-ns-avg   | Asynchronous Gauge | Double     | nanoseconds | `ns` | The average length of time the I/O thread spent waiting for a socket ready for reads or writes. | client-id | `client-id` value |
| kafka.producer.outgoing-byte-rate    | Asynchronous Gauge | Double     | bytes | `by`| The average number of outgoing bytes sent per second to all servers. | `client-id` | `client-id` value |
| kafka.producer.request-latency-avg   | Asynchronous Gauge | Double     | milliseconds | `ms` | The average request latency. | `client-id` | `client-id` value |
| kafka.producer.request-rate          | Asynchronous Gauge | Double     | requests | `{requests}` | The average number of requests sent per second. | `client-id` | `client-id` value |
| kafka.producer.response-rate         | Asynchronous Gauge | Double     | responses | `{responses}` | Responses received per second. | `client-id` | `client-id` value |
| kafka.producer.byte-rate             | Asynchronous Gauge | Double     | bytes | `by` | The average number of bytes sent per second for a specific topic. | `client-id` | `client-id` value |
|                                      |                    |            |       |      |                                                                   | `topic`     | topic name        |
| kafka.producer.compression-rate      | Asynchronous Gauge | Double     | compression rate | `{compressionrate}` | The average compression rate of record batches for a specific topic. | `client-id` | `client-id` value |
|                                      |                    |            |                  |                     |                                                                      | `topic`     | topic name        |
| kafka.producer.record-error-rate     | Asynchronous Gauge | Double     | error rate | `{errorrate}` | The average per-second number of record sends that resulted in errors for a specifific topic.  | `client-id` | `client-id` value |
|                                      |                    |            |            |               |                                                                                                | `topic`     | topic name        |
| kafka.producer.record-retry-rate     | Asynchronous Gauge | Double     | retry rate | `{retryrate}` | The average per-second number of retried record sends for a specific topic. | `client-id` | `client-id` value  |
|                                      |                    |            |            |               |                                                                             | `topic`     | topic name         |
| kafka.producer.record-send-rate      | Asynchronous Gauge | Double     | records sent rate | `{recordssentrate}` | The average number of records sent per second for a specific topic.  | `client-id` | `client-id` value  |
|                                      |                    |            |                   |                     |                                                                      | `topic`     | topic name         |

