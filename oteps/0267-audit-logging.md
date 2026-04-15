# Audit Logging Signal

Introduce a dedicated Audit Logging signal to OpenTelemetry that guarantees
lossless, tamper-evident delivery of security-relevant events and satisfies
compliance requirements such as ISO 27001.

<!-- toc -->
<!-- tocstop -->

## Motivation

### The problem with re-using the existing Log signal

OpenTelemetry Logs are designed for general-purpose observability. They share
the same pipeline as traces and metrics, which means they are subject to:

- **Sampling** – processors and exporters may drop records for performance
  reasons.
- **Back-pressure shedding** – SDK queues may overflow and silently discard
  records.
- **Transformation** – processors may modify, redact, or aggregate records
  before export.

These behaviours are intentional and desirable for observability logs. They are
**incompatible** with audit logging, where every record MUST be delivered
exactly once to the designated audit sink, in order, without modification.

Furthermore, compliance frameworks such as ISO 27001, SOC 2, PCI-DSS and HIPAA
require:

- Guaranteed delivery to a tamper-protected sink.
- Proof of record integrity (i.e. the record was not altered in transit).
- Separation of audit records from operational logs.
- Clock synchronisation across all emitting services.

None of these guarantees are made today by any OTel signal.

### Use cases

| Actor           | Audit event                   | Compliance driver            |
|-----------------|-------------------------------|------------------------------|
| End user        | Successful / failed login     | ISO 27001 A.8.15, SOC 2 CC6  |
| End user        | Access to sensitive data      | GDPR Art. 30, HIPAA §164.312 |
| Operator        | Configuration change          | ISO 27001 A.8.15             |
| Service account | Elevated-privilege action     | ISO 27001 A.5.18             |
| Service         | Outbound call to external API | PCI-DSS Req. 10              |
| Runtime         | Antivirus / IDs rule fired    | ISO 27001 A.8.16             |

### Why a new signal and not a new Log feature flag?

A feature flag (e.g. `audit=true` on a `LogRecord`) still shares the existing
pipeline and therefore inherits all the behaviours listed above. A dedicated
signal allows:

- A purpose-built SDK pipeline with no sampling, no transformation, and
  at-least-once delivery semantics.
- A distinct OTLP service name / endpoint so the audit sink can be isolated
  from the observability backend.
- A different data model with mandatory integrity metadata.

## Explanation

### Signal overview

The new signal is called **Audit Logging**. It is modelled structurally after
the existing Log signal and reuses the `LogRecord` data model as its transport
layer, adding a small set of mandatory fields.

```
Application code
      │
      ▼
 AuditLogger.emit(AuditRecord)
      │
      ▼
 AuditProvider  (SDK-level, no sampling, no dropping)
      │   └── AttributeProcessor (enrich only, never redact/drop)
      ▼
 AuditExporter  ──► Audit sink  (e.g. OpenSearch SIEM, Splunk, S3 WORM)
                        │
                        └── returns SHA-256 receipt hash ◄──────┐
                                                                  │
                                               emit() return value (delivery proof)
```

### AuditProvider

`AuditProvider` is the entry point, analogous to `LoggerProvider`. It:

- Holds a reference to a configured `AuditExporter`.
- Provides named `AuditLogger` instances.
- MUST NOT expose a sampling configuration option.
- MUST guarantee at-least-once delivery: records are queued durably (or
  synchronously) until the exporter acknowledges receipt.

### AuditLogger

`AuditLogger` is obtained from `AuditProvider` and is scoped to an
instrumentation scope (library name + version). It exposes a single method:

```
receipt = AuditLogger.emit(AuditRecord) → AuditReceipt
```

`emit` is **synchronous by default**: it MUST block until the exporter
acknowledges the record, or return an error. An asynchronous variant MAY be
provided, but MUST still guarantee delivery and MUST NOT silently discard on
failure.

### AuditRecord data model

`AuditRecord` is quite similar to `LogRecord` with the following mandatory fields:

| Field               | Type                    | Description                                                                                                                          |
|---------------------|-------------------------|--------------------------------------------------------------------------------------------------------------------------------------|
| `Timestamp`         | `fixed64`               | Nanoseconds since UNIX epoch (UTC). MUST be set. `<= ObservedTimestamp <= now(UTC)`                                                  |
| `ObservedTimestamp` | `fixed64`               | Nanoseconds since UNIX epoch when the SDK observed the event. Used for clock skew detection. MUST be set. `>= Timestamp <= now(UTC)` |
| `EventName`         | `string`                | Semantic name of the audit event (e.g. `user.login.success`). MUST be set.                                                           |
| `Actor`             | `AnyValue`              | Identity that performed the action (user ID, service account, …). MUST be set.                                                       |
| `ActorType`         | `enum`                  | `USER`, `SERVICE`, `SYSTEM`. MUST be set.                                                                                            |
| `Outcome`           | `enum`                  | `SUCCESS`, `FAILURE`, `UNKNOWN`. MUST be set.                                                                                        |
| `Resource`          | `AnyValue`              | The target resource (file, endpoint, table, …). SHOULD be set.                                                                       |
| `Action`            | `string`                | Verb describing what was done (e.g. `READ`, `WRITE`, `DELETE`, `LOGIN`). MUST be set.                                                |
| `SourceIP`          | `string`                | Source network address, if applicable.                                                                                               |
| `Body`              | `AnyValue`              | Free-form text or protobuf with additional details about the event.                                                                  |
| `Attributes`        | `map<string, AnyValue>` | Arbitrary key-value pairs for additional context.                                                                                    |
| `Signature`         | `bytes`                 | Digital signature of the audit record for integrity verification.                                                                    |
| `Algorithm`         | `string`                | Algorithm used for the digital signature (e.g., `RS256`, `ES256`).                                                                   |
| `Certificate`       | `bytes`                 | Digital public certificate used for the signature verification.                                                                      |

### AuditReceipt

`AuditReceipt` is returned by `emit` once the record has been acknowledged by
the exporter/sink:

| Field           | Type      | Description                                                                                                                                |
|-----------------|-----------|--------------------------------------------------------------------------------------------------------------------------------------------|
| `RecordId`      | `string`  | Unique, stable identifier assigned by the sink.                                                                                            |
| `IntegrityHash` | `string`  | SHA-256 of the canonical serialization of the `AuditRecord`, computed by the sink after successful write. Used for integrity verification. |
| `SinkTimestamp` | `fixed64` | Nanoseconds since UNIX epoch when the sink persisted the record.                                                                           |

The `IntegrityHash` is computed by the **sink**, not the SDK, so it reflects the
record as actually persisted – not as emitted. The emitting service MAY store
the receipt for its own tamper-detection purposes. The emitting service SHOULD compute the same hash locally and compare it to the receipt to verify integrity. A mismatch indicates the record was altered in transit or by the sink, which should trigger an alert (e.g. log an error, raise an incident).

### OTLP transport

Audit records are exported using a dedicated OTLP endpoint (distinct from the
standard `/v1/logs` endpoint), tentatively `/v1/audit`. This allows:

- Network-level isolation (firewall rules, separate credentials).
- Independent QoS policies (no back-pressure shedding).
- Clear separation in the sink's data model.

The payload is the standard `ExportLogsServiceRequest` proto with an additional
`audit` boolean flag in the `ResourceLogs` message.

#### No partial success

The OTLP receiver MUST NOT respond with a `partial_success` for an audit log
export request. If the receiver cannot process one or more audit records in a
batch, it MUST reject the **entire** batch and return an error. The exporter
MUST treat any `partial_success` response as a hard failure, retain all
records, and retry the full batch.

This constraint ensures that no audit record can be silently lost by a receiver
that processes only part of a batch and acknowledges the rest.

#### Instrumentation Scope is not applicable

The `InstrumentationScope` field present in the standard `ScopeLogs` message
has no meaning for audit logging. Audit records are not emitted by
instrumentation libraries – they are emitted by application or system code
acting on behalf of an actor. Exporters MUST leave the `InstrumentationScope`
field empty (or populated with only the SDK name/version as a technical marker)
and receivers MUST NOT use it for routing, filtering, or processing audit
records.

The three OTLP envelope layers that **do** apply to audit logging are:

| OTLP layer         | Role in audit logging                                          |
|--------------------|----------------------------------------------------------------|
| `Resource`         | Identifies the emitting service/host – reused without change.  |
| `LogRecord` (body) | Carries the `AuditRecord` payload.                             |
| `Attributes`       | Key-value context (user ID, IP, outcome, …) – reused as-is.    |

#### Durability at the sink is out of scope

This OTEP does not prescribe how the audit sink (e.g. OpenSearch, Splunk,
S3 WORM, a SIEM) stores, retains, or protects records once they have been
successfully acknowledged. Requirements such as write-once/read-many storage,
retention periods, or geographic replication are deployment concerns that depend
on the specific sink technology and the applicable compliance framework.

The boundary of the OTel audit signal ends at the moment the sink acknowledges
receipt (and, optionally, returns an `AuditReceipt`). Everything beyond that
point – including long-term durability, tamper-proof storage, and retention
enforcement – is outside the scope of this specification.

## Internal details

### No sampling, no dropping

The SDK MUST reject any attempt to configure a sampler on the `AuditProvider`.
The SDK MUST use an unbounded (or disk-backed) queue. If the in-memory queue is
full, the SDK MUST either block the caller or persist the record to a local
durable buffer rather than silently drop it.

### Processor restrictions

Only **additive** processors (enrich, tag, forward) are permitted in the audit
pipeline. Processors that delete attributes, filter records, or aggregate
records MUST be rejected at configuration time.

### Clock synchronisation

The SDK SHOULD warn at startup if the system clock is not synchronised (e.g.
NTP offset > 1 second). The `ObservedTimestamp` field provides a second
timestamp from the SDK's perspective, which allows the sink to detect skewed
emitters.

### Interaction with the existing Log signal

Audit records MUST NOT be routed through the standard `LoggerProvider`
pipeline. The two signals are independent. An instrumentation library MAY emit
both an audit record (for compliance) and a regular log record (for
observability) for the same event.

### Failure handling

If the exporter cannot reach the sink:

1. The SDK MUST buffer the record (in memory or on disk, depending on
   configuration).
2. The SDK MUST retry with exponential back-off.
3. If the buffer is exhausted (disk full, etc.) the SDK MUST surface a
   hard error to the caller rather than silently drop the record.
4. The SDK MUST expose a metric (`audit.records.dropped`) that counts
   any records lost due to unrecoverable errors.

## Trade-offs and mitigations

| Trade-off                                                  | Mitigation                                                                                                                   |
|------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------|
| Synchronous `emit` adds latency to the calling thread      | An async variant with a durable local queue mitigates this; the queue size and flush interval are configurable.              |
| A separate pipeline increases SDK complexity               | The audit pipeline deliberately reuses `LogRecord` as its wire format, so OTLP exporters can be reused with minimal changes. |
| SHA-256 receipt requires a round-trip to the sink          | The receipt is optional for callers that do not need proof-of-delivery; a fire-and-forget async mode MAY omit it.            |
| Disk-backed queue introduces a dependency on localStorage  | This is opt-in; the default is an in-memory queue with blocking back-pressure.                                               |

## Prior art and alternatives

### Alternative 1 – Existing Log signal with a dedicated exporter

Tag `LogRecord`s with `audit=true` and route them to a dedicated exporter via a
filtering processor. **Rejected**: still subject to SDK queue overflow and
requires consumers to filter records; does not provide integrity receipts.

### Alternative 2 – Out-of-band audit library

Bypass OTel entirely and use a dedicated audit library (e.g. OWASP Enterprise
Security API Logger). **Rejected**: loses OTel's context propagation, semantic
conventions, and OTLP transport; introduces a second observability stack.

### Alternative 3 – W3C Audit Vocabulary / CEF

Map to an existing audit format. **Not rejected**: the `AuditRecord` semantic
conventions SHOULD map cleanly to Common Event Format (CEF) and the W3C audit
vocabulary. This OTEP does not prescribe a wire format beyond OTLP.

### Prior art in OTel

- [OTEP 0092 – Logs Vision](logs/0092-logs-vision.md): defines the overall
  logging architecture on which this proposal builds.
- [OTEP 0097 – Log Data Model](logs/0097-log-data-model.md): `AuditRecord`
  extends the `LogRecord` data model defined here.
- [OTEP 0202 – Events and Logs API](0202-events-and-logs-api.md): the
  `AuditLogger`/`AuditProvider` hierarchy mirrors the `Logger`/`LoggerProvider`
  hierarchy introduced here.

## Open questions

1. **OTLP endpoint path** – Should audit records share `/v1/logs` with a
   distinguishing flag, or use a dedicated `/v1/audit` path? A dedicated
   path makes routing and access control simpler but requires changes to all
   OTLP receivers.

2. **Receipt hash computation** – Should the hash be computed by the SDK
   (guaranteeing what was sent) or by the sink (guaranteeing what was stored)?
   The current proposal says sink, but this requires a synchronous
   acknowledgement that may not be supported by all exporters.

3. **Mandatory vs. optional receipt** – Should `emit` always block for a
   receipt, or should this be configurable? Blocking guarantees delivery proof
   but impacts throughput.

4. **Retention metadata** – Should the `AuditRecord` carry a `RetentionPolicy`
   field (e.g. `keep_for: 7_years`) so the sink can enforce retention
   automatically? This is application-domain logic that may be out of scope for
   OTel.

5. **Redaction / PII** – ISO 27001 requires protecting logs from unauthorised
   access but does not require storing PII in plain text. How should the signal
   interact with attribute-level encryption or redaction at the SDK layer?

6. **Multi-sink fan-out** – Some compliance frameworks require logs to be
   written to two independent sinks simultaneously. Should this be a first-class
   configuration option of `AuditProvider`?

## Prototypes

No prototype exists yet. A reference implementation is planned for:

- **Java** – extending the existing `io.opentelemetry:opentelemetry-sdk-logs`
  module.
- **Go** – extending `go.opentelemetry.io/otel/sdk/log`.

## Future possibilities

- **Semantic conventions** for common audit event names
  (`user.login.success`, `resource.delete`, `config.change`, ...) following the
  same pattern as existing OTel semantic conventions.
- **Integrity chain** – each record carries the hash of the previous record
  (blockchain-style) so gaps in the audit trail are detectable without a
  centralized sequence counter.
- **Declarative configuration** support so that audit pipeline parameters
  (sink URL, queue depth, retry policy, retention) can be specified in the
  [OTel configuration file schema](https://github.com/open-telemetry/opentelemetry-configuration).
- **Collector support** – a dedicated `auditlog` receiver/exporter pair in
  the OpenTelemetry Collector that enforces the no-drop guarantee end-to-end.
