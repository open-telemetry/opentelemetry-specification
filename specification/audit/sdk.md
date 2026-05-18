<!--- Hugo front matter used to generate the website version of this page:
linkTitle: SDK
weight: 3
--->

# Audit Logging SDK

**Status**: [Development](../document-status.md)

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [Audit Logging SDK](#audit-logging-sdk)
  - [AuditProvider](#auditprovider)
    - [AuditProvider Creation](#auditprovider-creation)
    - [AuditLogger Creation](#auditlogger-creation)
    - [Configuration](#configuration)
    - [No Sampling](#no-sampling)
    - [Shutdown](#shutdown)
    - [ForceFlush](#forceflush)
  - [AuditLogger](#auditlogger)
    - [Emit an AuditRecord](#emit-an-auditrecord)
  - [AuditRecord Queue](#auditrecord-queue)
    - [Durability guarantees](#durability-guarantees)
    - [Back-pressure handling](#back-pressure-handling)
  - [AuditRecordProcessor](#auditrecordprocessor)
    - [Processor restrictions](#processor-restrictions)
    - [AuditRecordProcessor operations](#auditrecordprocessor-operations)
      - [OnEmit](#onemit)
      - [Shutdown](#shutdown-1)
      - [ForceFlush](#forceflush-1)
    - [Built-in processors](#built-in-processors)
      - [Simple processor](#simple-processor)
      - [Batching processor](#batching-processor)
      - [Signing processor (Sig)](#signing-processor-sig)
  - [AuditRecordExporter](#auditrecordexporter)
    - [AuditRecordExporter operations](#auditrecordexporter-operations)
      - [Export](#export)
      - [ForceFlush](#forceflush-2)
      - [Shutdown](#shutdown-2)
    - [OTLP transport requirements](#otlp-transport-requirements)
      - [Dedicated endpoint](#dedicated-endpoint)
      - [No partial success](#no-partial-success)
      - [Idempotency](#idempotency)
      - [InstrumentationScope](#instrumentationscope)
  - [Failure handling](#failure-handling)
  - [Clock synchronisation](#clock-synchronisation)
  - [Interaction with the Log signal](#interaction-with-the-log-signal)
  - [Collector pipeline (Tier-2)](#collector-pipeline-tier-2)
  - [Observability](#observability)
  - [Concurrency requirements](#concurrency-requirements)
  - [References](#references)

<!-- tocstop -->

</details>

The Audit Logging SDK is the implementation of the
[Audit Logging API](./api.md). It provides the guarantee that every
emitted `AuditRecord` is delivered to the configured audit sink without
loss, modification, or sampling.

All language implementations of OpenTelemetry that support the Audit
Logging signal MUST provide an SDK conforming to this specification.

## AuditProvider

A `AuditProvider` MUST provide a way to associate a
[Resource](../resource/sdk.md) with all `AuditRecord`s produced by any
`AuditLogger` obtained from it.

### AuditProvider Creation

The SDK SHOULD allow the creation of multiple independent
`AuditProvider` instances. Although most applications will only need one.

Each `AuditProvider` instance MUST have its own independent queue,
exporter pipeline, and failure counter.

### AuditLogger Creation

`AuditLogger` instances MUST only be created through an
`AuditProvider`.

The `AuditProvider` MUST implement the
[Get an AuditLogger](./api.md#get-an-auditlogger) operation. The
`name` and optional `version` / `schema_url` parameters are stored
internally on the created `AuditLogger` for diagnostic purposes.

If an invalid `name` (null or empty string) is provided, a working
`AuditLogger` MUST be returned rather than null or an exception. The
`name` SHOULD retain the invalid value and the SDK SHOULD emit a
warning.

### Configuration

The `AuditProvider` owns the following configuration:

- One or more [AuditRecordProcessor](#auditrecordprocessor) instances.
- The [AuditRecord Queue](#auditrecord-queue) parameters.
- The retry and back-pressure policy (see
  [Failure handling](#failure-handling)).

Configuration MUST be applied to all already-returned `AuditLogger`s
when it is changed after provider creation (that is, adding a processor
after the provider is created MUST affect all existing loggers).

### No Sampling

The `AuditProvider` MUST NOT accept or expose any sampler or
sampling-rate configuration. Any attempt to configure sampling on the
audit pipeline MUST be rejected at configuration time with an
explanatory error.

The SDK MUST NOT apply any record filtering, dropping, or aggregation
that reduces the number of `AuditRecord`s reaching the exporter.

### Shutdown

On the first call, `Shutdown` MUST:

1. Call `ForceFlush` to ensure all buffered records are exported.
2. Call `Shutdown` on every registered
   `AuditRecordProcessor`.

`Shutdown` SHOULD complete or abort within a configurable timeout.
After `Shutdown` returns, subsequent calls to `GetAuditLogger` SHOULD
return an error or throw an exception. Any call to `emit` on an
`AuditLogger` obtained from a shut-down `AuditProvider` MUST raise a
hard error or throw an exception and MUST NOT silently drop the record.

`Shutdown` SHOULD provide a way for the caller to determine whether it
succeeded, failed, or timed out.

Subsequent calls to `Shutdown` or `ForceFlush` after the first
`Shutdown` call MUST be no-ops and MUST NOT return an error.

### ForceFlush

`ForceFlush` requests that all buffered `AuditRecord`s be exported
immediately.

`ForceFlush` MUST invoke `ForceFlush` on all registered
`AuditRecordProcessor` instances.

`ForceFlush` SHOULD complete or abort within a configurable timeout and
SHOULD provide a way for the caller to determine whether it succeeded,
failed, or timed out.

If `Shutdown` has already been called, `ForceFlush` MUST be a no-op
and MUST NOT return an error.

## AuditLogger

### Emit an AuditRecord

If `emit` is called after the owning `AuditProvider` has been shut
down, the SDK MUST raise a hard error or throw an exception. The SDK
MUST NOT silently drop the record.

When `emit` is called, the SDK MUST:

1. If `Attributes` does not contain `audit.record.id`, generate a
   UUID v4 and inject it into `Attributes` before any further
   processing.
2. Set `ObservedTimestamp` to the current time if the caller did not
   provide it.
3. Validate that the required LogRecord fields (`Timestamp`,
   `EventName`) and the mandatory attributes (`audit.actor.id`,
   `audit.actor.type`, `audit.action`, `audit.outcome`) are present
   and non-empty. If any required field or attribute is missing,
   `emit` MUST surface a hard error to the caller and MUST NOT
   silently drop the record.
4. Enqueue the `AuditRecord` in the [AuditRecord Queue](#auditrecord-queue).
5. Pass the record through all registered
   `AuditRecordProcessor` instances via
   [`OnEmit`](#onemit).
6. Block until the exporter returns a successful acknowledgement from
   the audit sink.
7. Return the [`AuditReceipt`](./data-model.md#auditreceipt-definition) provided
   by the sink.

If the synchronous `emit` cannot obtain an acknowledgement within the
configured timeout, it MUST surface a hard error. It MUST NOT return
successfully without a valid receipt. It may implement retries with back-off,
but this MUST be transparent to the caller and MUST NOT cause `emit` to block
indefinitely.

## AuditRecord Queue

### Durability guarantees

The SDK MUST NOT use a bounded queue that silently drops records when
full. The SDK MUST use one of the following strategies:

- **Disk-backed queue** (default): records are persisted to local
  storage before acknowledgement by the exporter. This guarantees
  delivery across SDK restarts and process crashes.
- **Unbounded in-memory queue** (opt-in): the queue grows without a
  fixed limit. The SDK MUST expose a configurable high-water-mark
  warning threshold. When the queue depth exceeds this threshold, the
  SDK SHOULD emit a warning via the SDK's internal logging. The SDK SHOULD
  provide meaningfull metrics (for example, `audit.queue.depth`) to allow
  operators to monitor the queue depth and set up alerts.
- **Other lossless queuing strategy**: if the SDK implements a different
  strategy that guarantees no record loss (for example, DB persistence queue
  with back-pressure blocking), it MUST provide the same
  durability guarantees and operational visibility as the above options.
  The SDK MUST NOT use a strategy that can result in silent record loss
  under any circumstances.

### Back-pressure handling

If the in-memory queue is exhausted (for example, because the exporter
is unavailable for an extended period):

- The SDK MUST either block the calling thread (applying back-pressure
  to the application) or persist the record to a local durable buffer.
- The SDK MUST NOT silently discard the record.

The back-pressure strategy (blocking vs. disk-backed) MUST be
configurable.

## AuditRecordProcessor

`AuditRecordProcessor` is an interface that allows hooks into the
`AuditRecord` pipeline for enrichment and forwarding.

### Processor restrictions

The Audit Logging pipeline enforces strict restrictions on processors
to guarantee that no record is lost or altered:

- Only **additive** operations are permitted: processors MAY enrich
  records by adding `Attributes`, but MUST NOT remove existing
  attributes, filter records, aggregate records, or alter the mandatory
  LogRecord fields (`Timestamp`, `EventName`) or the mandatory
  attributes (`audit.actor.id`, `audit.actor.type`, `audit.action`,
  `audit.outcome`).
- Processors that delete attributes, suppress records, or aggregate
  records MUST be rejected at configuration time with an explanatory
  error.
- Processors MUST NOT introduce sampling or conditional forwarding.

### AuditRecordProcessor operations

#### OnEmit

`OnEmit` is called synchronously on the thread that called `emit`,
after the `AuditRecord` has been queued and before the response is
returned to the caller.

**Parameters:**

- `auditRecord` – a mutable `AuditRecord` for the emitted record.
  Processors MAY enrich the record (add attributes) but
  MUST NOT remove mandatory fields or filter the record.
- `context` – the resolved `Context` at the time of emission.

**Returns:** `Void`

`OnEmit` MUST NOT block indefinitely. It SHOULD complete quickly to
minimise the latency of synchronous `emit` calls.

Mutations made by a processor to `auditRecord` MUST be visible to
subsequently registered processors.

If `OnEmit` is called after the processor has been shut down, the
processor MUST raise a hard error or throw an exception and MUST NOT
silently accept or forward the record.

#### Shutdown

Shuts down the processor. Called when the `AuditProvider` is shut down.

On the first call, `Shutdown` MUST include the effects of `ForceFlush`.

`Shutdown` SHOULD complete or abort within a configurable timeout.

Subsequent calls to `Shutdown` or `ForceFlush` after the first
`Shutdown` call MUST be no-ops and MUST NOT return an error.

#### ForceFlush

Requests that the processor export all buffered records as soon as
possible, preferably before returning.

`ForceFlush` SHOULD provide a way for the caller to determine whether
it succeeded, failed, or timed out.

If `Shutdown` has already been called, `ForceFlush` MUST be a no-op
and MUST NOT return an error.

### Built-in processors

#### Simple processor

The simple processor passes each `AuditRecord` directly to the
configured `AuditRecordExporter` synchronously on the calling thread.
This guarantees that the exporter acknowledges the record before
`emit` returns.

The processor MUST synchronize calls to the exporter's `Export` to
prevent concurrent invocations.

**Configurable parameters:**

- `exporter` – the `AuditRecordExporter` to which records are pushed.

The SDK MUST provide the simple processor as a built-in. It is the
default processor for synchronous `emit`.

#### Batching processor

The batching processor accumulates `AuditRecord`s in an internal queue
and exports them in batches asynchronously. It reduces per-record
round-trip overhead while retaining the no-drop guarantee: records
MUST NOT be discarded when the batch queue is full; the processor MUST
apply back-pressure or switch to disk-backed storage instead.

The batching processor MUST still satisfy the at-least-once delivery
requirement: if the process exits before a batch is exported, buffered
records MUST be recoverable (e.g. via a disk-backed queue).

**Configurable parameters:**

- `exporter` – the `AuditRecordExporter` to which batches are pushed.
- `maxQueueSize` – maximum number of records held in memory before
  back-pressure is applied. Default: 2048.
- `scheduledDelayMillis` – how long the processor waits before
  exporting an incomplete batch. Default: 5000 ms.
- `exportTimeoutMillis` – maximum time allowed for a single `Export`
  call. Default: 30 000 ms.
- `maxExportBatchSize` – maximum number of records per exported batch.
  Default: 512.
- `maxRetryCount` – maximum export retry attempts before surfacing a
  hard error. Default: 5.
- `initialBackoffMillis` – initial wait between retries; doubled on
  each attempt (exponential back-off). Default: 1000 ms.

The SDK SHOULD provide the batching processor as a built-in.

#### Signing processor (Sig)

The signing processor computes an `audit.integrity.value` attribute
for each `AuditRecord` to provide tamper-evidence. The value is a
base64-encoded asymmetric digital signature or symmetric HMAC, as
determined by the `audit.integrity.algorithm` `Resource` attribute
configured on the `AuditProvider`. It MUST be implemented as a
separate processor that can be added to the pipeline in addition to
the simple processor, to allow flexibility in the choice of signing
algorithm and key management strategy.

## AuditRecordExporter

`AuditRecordExporter` is the interface that protocol-specific exporters
implement to transmit `AuditRecord`s to the audit sink.

Each implementation MUST document its concurrency characteristics.

### AuditRecordExporter operations

#### Export

Exports `AuditRecord`s to the audit sink.

`Export` MUST NOT be called concurrently on the same exporter instance.

`Export` MUST NOT block indefinitely. There MUST be a configurable
upper time limit after which the call times out with a `Failure` result.

**Parameters:**

- Optional `batch` – a collection of `AuditRecord`s to export. The concrete
  type is language-specific.

**Returns:** `ExportResult`

`ExportResult` has values of either `Success` or `Failure`:

- `Success` – all records in the batch have been acknowledged by the
  audit sink. The exporter MUST include the `AuditReceipt` for each
  record in the result.
- `Failure` – the export failed. The SDK MUST retain all records in
  the batch and retry according to the configured retry policy. The
  SDK MUST NOT drop records on a `Failure` result.

#### ForceFlush

Requests that any buffered `AuditRecord`s be exported immediately.

`ForceFlush` SHOULD provide a way for the caller to determine whether
it succeeded, failed, or timed out.

#### Shutdown

Shuts down the exporter. Called when the `AuditProvider` is shut down.

On the first call, `Shutdown` MUST flush any internally buffered records
and release all resources. After `Shutdown` completes, subsequent calls
to `Export` MUST return `Failure`.

Subsequent calls to `Shutdown` or `ForceFlush` after the first
`Shutdown` call MUST be no-ops and MUST NOT return an error.

### OTLP transport requirements

#### Dedicated endpoint

Audit records MUST be exported to a dedicated OTLP endpoint, distinct
from the standard `/v1/logs` endpoint. The default path is `/v1/audit`.

Using a dedicated endpoint enables:

- Network-level isolation (firewall rules, separate TLS certificates
  and credentials).
- Independent QoS policies with no back-pressure shedding from the
  observability pipeline.
- Clear separation in the sink's data model.

<!-- TODO revisit: ExportLogsServiceRequest + audit flag -->
The payload MUST use the standard `ExportLogsServiceRequest` proto,
with the `audit` flag set to `true` in the `ResourceLogs` message to
identify the batch as audit records.

#### No partial success

The OTLP receiver MUST NOT respond with a `partial_success` for an
audit log export request.

If the receiver cannot process one or more records in a batch, it MUST
reject the **entire** batch and return an error status. The SDK exporter
MUST treat any `partial_success` response as a hard `Failure`, retain
**all** records in the batch (including those that would have been
accepted), and retry the full batch.

This constraint ensures that no audit record can be silently lost by a
receiver that acknowledges only part of a batch.

#### Idempotency

The OTLP receiver SHOULD treat `audit.record.id` as an idempotency
key.

When a record with an already-known `audit.record.id` arrives:

- If the canonical payload hash is **identical**, the receiver SHOULD
  return a deterministic success response for the existing record
  without creating a duplicate entry.
- If the canonical payload hash **differs**, the receiver MUST return
  a conflict error (HTTP 409 or equivalent). The SDK exporter MUST
  treat a conflict error as a non-retryable `Failure`.

This ensures that retries after transient failures do not produce
duplicate audit entries, provided the caller uses a stable `RecordId`
across retry attempts.

#### InstrumentationScope

`InstrumentationScope` has no meaning for audit logging. Audit records
are emitted by application or system code acting on behalf of an actor,
not by instrumentation libraries.

Exporters MUST leave the `InstrumentationScope` field empty, or MAY
populate it with the SDK name and version as a technical marker.
Receivers MUST NOT use `InstrumentationScope` for routing, filtering,
or processing audit records.

## Failure handling

If the exporter cannot reach the audit sink, the SDK MUST follow this
failure-handling sequence:

1. **Buffer**: Retain the record in the SDK's queue (disk-backed or
   in-memory, depending on configuration). The record MUST NOT be
   discarded.
2. **Retry**: Attempt reexport with exponential back-off and a
   configurable maximum number of retries. The initial retry interval,
   back-off multiplier, and maximum interval SHOULD be configurable.
3. **Hard error**: If the retry budget is exhausted or the buffer is
   full (for example, the disk is full), the SDK MUST surface a hard
   error to the caller (exception, error code, or equivalent). It MUST
   NOT silently drop the record.
4. **Metric**: The SDK MUST increment the `audit.records.dropped`
   metric counter for every record that is lost due to an unrecoverable
   error. See [Observability](#observability).

## Clock synchronisation

Accurate timestamps are a requirement of ISO 27001 Annex A (clock
synchronisation). The SDK SHOULD:

- Warn at startup if the system clock NTP offset exceeds one second.
- Warn when `Timestamp` and `ObservedTimestamp` differ by more than a
  configurable threshold (default: 5 seconds), which may indicate clock
  skew between the event source and the SDK host.

The SDK MUST set `ObservedTimestamp` to the wall-clock time at the
moment `emit` is called, using the SDK host's system clock.

## Interaction with the Log signal

Audit records MUST NOT be routed through the standard `LoggerProvider`
pipeline. The two signals are independent and MUST use separate
providers, queues, and exporters.

An application or library MAY emit both an `AuditRecord` (for
compliance) and a regular `LogRecord` (for observability) for the same
event. The records travel through independent pipelines to independent
backends and MUST NOT interfere with each other.

## Collector pipeline (Tier-2)

In enterprise deployments an OpenTelemetry Collector typically sits
between the SDK exporter and the final audit sink. This collector acts
as a **Tier-2** intermediary that can verify record integrity,
distribute records to multiple sinks, and provide delivery tracking.

```
Application
    │
    ▼  /v1/audit  (SDK exporter)
OTel Collector  ──► verify hash/signature
    │                └── forward to required sinks
    ├──► Primary sink  (OpenSearch, Splunk, …)
    ├──► Secondary sink (S3 WORM, cold archive)
    └──► SIEM

Collector returns delivery status per sink to the SDK exporter.
```

The SDK exporter interacts with the Tier-2 collector via the same
`/v1/audit` endpoint; no API changes are required at the SDK level.

The Tier-2 collector SHOULD:

- Verify `audit.integrity.value` of each received record against the
  algorithm declared in the `Resource` attribute
  `audit.integrity.algorithm` and the key material referenced by
  `audit.integrity.certificate`.
- Validate `audit.sequence.number` continuity and `audit.prev.hash`
  chain integrity when these optional attributes are present.
- Deliver each record to every configured required sink before
  returning a success response to the SDK exporter.
- Return a conflict error (HTTP 409) when a duplicate `RecordId` with
  a differing payload hash is received.
- Expose per-sink delivery status in its response so that operators can
  detect partial delivery failures.

The Tier-2 collector MUST NOT respond with partial success (see
[No partial success](#no-partial-success)). If any required sink
rejects the record the collector MUST reject the entire request.

For the full Tier-2 collector specification see
[Audit Logging Collector](./collector.md).

## Observability

The SDK MUST expose the following internal metrics to allow operators
to monitor the health of the audit pipeline:

| Metric name              | Type      | Description                                 |
|--------------------------|-----------|---------------------------------------------|
| `audit.records.emitted`  | Counter   | Total records passed to the SDK pipeline.   |
| `audit.records.exported` | Counter   | Records successfully acknowledged by sink.  |
| `audit.records.dropped`  | Counter   | Records lost due to unrecoverable errors.   |
| `audit.queue.depth`      | Gauge     | Current number of records in the SDK queue. |
| `audit.export.duration`  | Histogram | Round-trip time from `Export` to receipt.   |

A non-zero value for `audit.records.dropped` MUST be treated as a
critical operational alert. SDK authors SHOULD provide a mechanism (for
example, a log message or a callback) to notify operators immediately
when this counter is incremented.

## Concurrency requirements

For languages that support concurrent execution:

- **AuditProvider** – logger creation, `ForceFlush`, and `Shutdown`
  MUST be safe for concurrent use.
- **AuditLogger** – `emit` MUST be safe for concurrent use.
- **AuditRecordExporter** – `ForceFlush` and `Shutdown` MUST be safe
  for concurrent use. `Export` MUST NOT be called concurrently on the
  same instance.

## References

- [OTEP 0267 – Audit Logging Signal](../../oteps/0267-audit-logging.md)
- [OTEP 0150 – Logging Library SDK Prototype Specification](../../oteps/logs/0150-logging-library-sdk.md)
