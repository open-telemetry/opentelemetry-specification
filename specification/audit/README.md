<!--- Hugo front matter used to generate the website version of this page:
linkTitle: Audit Logging
path_base_for_github_subdir:
  from: tmp/otel/specification/audit/_index.md
  to: audit/README.md
--->

# OpenTelemetry Audit Logging

**Status**: [Development](../document-status.md)

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [OpenTelemetry Audit Logging](#opentelemetry-audit-logging)
  - [Introduction](#introduction)
  - [Why a Dedicated Audit Logging Signal?](#why-a-dedicated-audit-logging-signal)
  - [Compliance Use Cases](#compliance-use-cases)
  - [Signal Overview](#signal-overview)
  - [Relationship to the Log Signal](#relationship-to-the-log-signal)
  - [Specifications](#specifications)
  - [References](#references)

<!-- tocstop -->

</details>

## Introduction

Audit logging is a compliance-critical signal that records
security-relevant events for regulatory and accountability purposes.
Compliance frameworks such as ISO 27001, SOC 2, PCI-DSS, and HIPAA
require that audit records be delivered without loss, modification, or
sampling to a tamper-protected audit sink.

The OpenTelemetry Audit Logging signal provides a purpose-built pipeline
with the delivery and integrity guarantees that compliance frameworks
demand. It extends OpenTelemetry's unified observability approach to
the domain of security and compliance auditing.

## Why a Dedicated Audit Logging Signal?

The existing OpenTelemetry [Log signal](../logs/README.md) is designed
for general-purpose observability. Its pipeline is intentionally subject
to behaviours that are incompatible with audit logging:

- **Sampling** – processors and exporters may drop records for
  performance reasons.
- **Back-pressure shedding** – SDK queues may overflow and silently
  discard records.
- **Transformation** – processors may modify, redact, or aggregate
  records before export.

For audit logging, every record MUST be delivered to the designated audit
sink without modification or loss. A feature flag on a `LogRecord` cannot
fulfil this requirement because it still shares the existing pipeline and
inherits all the above behaviours.

A dedicated Audit Logging signal provides:

- A purpose-built SDK pipeline with no sampling, no transformation, and
  at-least-once delivery semantics.
- A distinct OTLP endpoint (`/v1/audit`) so the audit sink can be
  isolated from the observability backend, enabling independent access
  control and QoS policies.
- A dedicated data model with mandatory integrity fields.
- Clear separation of audit records from operational logs, as required
  by ISO 27001 Annex A and similar frameworks.

## Compliance Use Cases

The following table illustrates representative audit events and the
compliance drivers that motivate them:

| Actor           | Audit event                   | Compliance driver            |
|-----------------|-------------------------------|------------------------------|
| End user        | Successful / failed login     | ISO 27001 A.8.15, SOC 2 CC6  |
| End user        | Access to sensitive data      | GDPR Art. 30, HIPAA §164.312 |
| Operator        | Configuration change          | ISO 27001 A.8.15             |
| Service account | Elevated-privilege action     | ISO 27001 A.5.18             |
| Service         | Outbound call to external API | PCI-DSS Req. 10              |
| Runtime         | Antivirus / IDs rule fired    | ISO 27001 A.8.16             |

## Signal Overview

The Audit Logging signal is modelled structurally after the Log signal.
It reuses the OTLP `LogRecord` as its wire-format transport and adds a
small set of mandatory fields that satisfy compliance requirements.

```
Application code
      │
      ▼
 AuditLogger.emit(AuditRecord) ──► returns AuditReceipt
      │   RecordId (caller-generated)
      ▼
 AuditProvider  (no sampling, no dropping)
      │   └── AuditRecordProcessor (enrich only – never redact or drop)
      │           ├── Simple processor (sync, default)
      │           ├── Batching processor (async, high-volume)
      │           └── Signing processor (adds IntegrityValue)
      ▼
 AuditExporter  ──► Tier-2 Collector (optional)  ──► Audit sinks
             or ──► Audit sink directly                    │
                        │                    (OpenSearch, Splunk, S3 WORM …)
                        └── returns AuditReceipt
                              (RecordId + IntegrityHash + SinkTimestamp)
```

The principal API components are:

- **AuditProvider** – the entry point of the API. It provides named
  `AuditLogger` instances and MUST NOT expose a sampler configuration
  option. See [Audit Logging API](./api.md#auditprovider).
- **AuditLogger** – emits `AuditRecord`s and returns an `AuditReceipt`
  once the sink has acknowledged the record.
  See [Audit Logging API](./api.md#auditlogger).

The principal data components are:

- **AuditRecord** – the audit event payload containing mandatory fields
  for actor, action, outcome, timestamps, and optional integrity
  metadata. See [Audit Record Data Model](./data-model.md#auditrecord-definition).
- **AuditReceipt** – proof-of-delivery returned by the sink, containing
  a unique record identifier and a SHA-256 integrity hash.
  See [Audit Record Data Model](./data-model.md#auditreceipt-definition).

## Relationship to the Log Signal

The Audit Logging signal is **independent** of the Log signal. Audit
records MUST NOT be routed through the standard `LoggerProvider`
pipeline.

An application or instrumentation library MAY emit both an `AuditRecord`
(for compliance) and a regular `LogRecord` (for observability) for the
same event. The two records travel through independent pipelines to
independent backends.

The OTLP wire format reuses the `LogRecord` protobuf message as the
payload carrier. The following OTLP envelope layers apply:

| OTLP layer             | Role in audit logging                                  |
|------------------------|--------------------------------------------------------|
| `Resource`             | Emitting service / host; integrity attrs on Resource.  |
| `LogRecord`            | Carries AuditRecord via dedicated fields + Attributes. |
| `Attributes`           | Mandatory and optional `audit.*` semantic attributes.  |
| `InstrumentationScope` | **Not applicable.** MUST be left empty by exporters.   |

## Specifications

- [Audit Logging API](./api.md)
- [Audit Logging SDK](./sdk.md)
- [Audit Record Data Model](./data-model.md)
- [Audit Logging Collector (Tier-2)](./collector.md)

## References

- [OTEP 0267 – Audit Logging Signal](../../oteps/0267-audit-logging.md)
- [OTEP 0092 – OpenTelemetry Logs Vision](../../oteps/logs/0092-logs-vision.md)
- [OTEP 0097 – Log Data Model](../../oteps/logs/0097-log-data-model.md)
- [OTEP 0202 – Events and Logs API](../../oteps/0202-events-and-logs-api.md)
