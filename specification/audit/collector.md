<!--- Hugo front matter used to generate the website version of this page:
linkTitle: Collector (Tier-2)
weight: 4
--->

# Audit Logging Collector (Tier-2)

**Status**: [Development](../document-status.md)

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [Audit Logging Collector (Tier-2)](#audit-logging-collector-tier-2)
  - [Overview](#overview)
  - [Endpoint Definition](#endpoint-definition)
    - [Single-Record Ingest](#single-record-ingest)
    - [Batch Ingest](#batch-ingest)
  - [Request Model](#request-model)
    - [Required Record Fields](#required-record-fields)
    - [Optional Record Fields](#optional-record-fields)
  - [Response Model](#response-model)
    - [Single-Record Response Fields](#single-record-response-fields)
    - [Batch Response Fields](#batch-response-fields)
    - [Domain Status Values](#domain-status-values)
  - [HTTP Status Codes](#http-status-codes)
  - [Idempotency and Duplicate Handling](#idempotency-and-duplicate-handling)
  - [Verification and Sink Delivery](#verification-and-sink-delivery)
    - [Integrity Verification](#integrity-verification)
    - [Hash-Chain Validation](#hash-chain-validation)
    - [Per-Sink Delivery Status](#per-sink-delivery-status)
    - [Record Lifecycle](#record-lifecycle)
  - [Retry Guidance](#retry-guidance)
  - [Security Requirements](#security-requirements)
  - [References](#references)

<!-- tocstop -->

</details>

## Overview

This document specifies the behavior of an OpenTelemetry Collector
acting as a Tier-2 intermediary in an audit logging pipeline. The
collector receives `AuditRecord`s from SDK exporters (Tier-1),
verifies their integrity, and distributes them to one or more required
audit sinks.

The Tier-2 collector is optional. SDK exporters MAY deliver directly
to the audit sink when no collector is deployed. When a collector is
present it MUST satisfy the same no-drop and at-least-once delivery
guarantees as the SDK itself.

```
SDK Exporter  ──POST /v1/audit──►  Tier-2 Collector
                                       │
                                   verify integrity
                                   validate hash-chain
                                       │
                          ┌────────────┼────────────┐
                          ▼            ▼            ▼
                     Primary sink  Secondary   SIEM / archive
                     (OpenSearch)  (S3 WORM)   (Splunk)
```

## Endpoint Definition

The Tier-2 collector MUST expose an HTTP endpoint that accepts audit
records from SDK exporters.

### Single-Record Ingest

- **Path**: `/v1/audit` (MUST; matches the SDK exporter default).
- **Method**: `POST`.
- **Body**: one serialized `AuditRecord` payload.

### Batch Ingest

- **Path**: `/v1/audit` (same endpoint; batch indicated by content).
- **Method**: `POST`.
- **Body**: batch payload containing multiple `AuditRecord`s.

The collector MUST support both single-record and batch requests on
the same endpoint. The request content type MUST follow the OTLP
serialization convention (protobuf or JSON).

## Request Model

Request payloads MUST follow the
[Audit Record Data Model](./data-model.md).

### Required Record Fields

Each record MUST include the following LogRecord fields:

- `Timestamp`
- `EventName`

And the following mandatory attributes in the `Attributes` map:

- `audit.record.id`
- `audit.actor.id`
- `audit.actor.type`
- `audit.action`
- `audit.outcome`

### Optional Record Fields

Each record MAY include any attribute defined in the
[Audit Semantic Attributes](./data-model.md#audit-semantic-attributes)
section, including `audit.schema.version`, `audit.integrity.value`,
`audit.sequence.number`, and `audit.prev.hash`. The signing algorithm
and key reference are carried as `Resource` attributes
`audit.integrity.algorithm` and `audit.integrity.certificate`.

## Response Model

Tier-2 responses MUST include:

- A transport-level HTTP status code.
- A domain-level processing status in the response body.

### Single-Record Response Fields

- `record_id` – echoes the `RecordId` from the request.
- `status` – domain status value (see [Domain Status Values](#domain-status-values)).
- `integrity_hash` – SHA-256 of the record as persisted by the
  collector (same semantics as `AuditReceipt.IntegrityHash`).
- `sink_timestamp` – nanoseconds since UNIX epoch when the collector
  persisted the record to all required sinks.
- `verify_status` – `passed`, `failed`, or `deferred`.
- `sink_status_map` – map of sink name → delivery status (see
  [Per-Sink Delivery Status](#per-sink-delivery-status)).
- `reason` – human-readable explanation when `status` is not success.
- `retry_after` – seconds to wait before retrying, when applicable.

### Batch Response Fields

- `batch_id` – collector-assigned identifier for the batch.
- `status` – aggregate domain status.
- `record_status_map` – map of `RecordId` → single-record response.
- `sink_status_aggregate` – aggregate delivery status across all sinks.

### Domain Status Values

The collector SHOULD use the following domain status values:

- `accepted_pending_verify` – received; integrity check in progress.
- `verified_queued` – integrity passed; queued for sink delivery.
- `verified_exporting` – actively delivering to required sinks.
- `delivered_all_sinks` – every required sink confirmed receipt.
- `delivered_partial` – at least one required sink failed; treated as
  non-success (see [Verification and Sink Delivery](#verification-and-sink-delivery)).
- `rejected_verify_failed` – integrity check failed.
- `rejected_schema_invalid` – schema validation failed.
- `rejected_authz` – authentication or authorisation failure.
- `failed_internal` – unexpected internal collector error.

## HTTP Status Codes

The collector SHOULD use the following HTTP status codes:

| Code          | Meaning                                                        |
|---------------|----------------------------------------------------------------|
| `200`         | Fully processed; all required sinks confirmed.                 |
| `202`         | Accepted for async verify or export; final state pending.      |
| `400`         | Malformed payload, schema mismatch, or canonicalization error. |
| `401` / `403` | Authentication or authorisation failure.                       |
| `409`         | Duplicate `RecordId` with differing payload hash.              |
| `413`         | Payload too large.                                             |
| `429`         | Intake throttled by policy.                                    |
| `500`         | Unexpected internal error.                                     |
| `503`         | Temporarily unavailable or no reliable intake capacity.        |

The collector MUST NOT return HTTP 207 (Multi-Status) to indicate
partial success. If any required sink fails the collector MUST reject
the entire batch (see
[No partial success](./sdk.md#no-partial-success)).

## Idempotency and Duplicate Handling

The collector MUST treat `audit.record.id` as the primary idempotency
key.

When a duplicate `audit.record.id` is received:

- If the canonical payload hash is **identical**, the collector SHOULD
  return a deterministic success response for the existing record
  without creating a duplicate entry.
- If the canonical payload hash **differs**, the collector MUST return
  HTTP 409. The SDK exporter MUST treat HTTP 409 as a non-retryable
  `Failure`.

## Verification and Sink Delivery

### Integrity Verification

When `audit.integrity.value` is present the collector SHOULD verify
it against the algorithm declared in the `Resource` attribute
`audit.integrity.algorithm` and the key material referenced by
`audit.integrity.certificate` in the collector's trust policy.

The collector MAY defer verification for low-latency ingest (returning
`accepted_pending_verify`) but MUST complete verification before
acknowledging delivery to any required sink.

If verification fails the collector MUST:

1. Reject the record with domain status `rejected_verify_failed`.
2. NOT forward the record to any sink.
3. Return HTTP 400 with a descriptive `reason`.

### Hash-Chain Validation

When `audit.sequence.number` and `audit.prev.hash` are present the
collector SHOULD validate chain continuity:

- `audit.sequence.number` MUST be strictly greater than the previous
  record's `audit.sequence.number` in the same audit stream.
- `audit.prev.hash` MUST equal the `IntegrityHash` of the preceding
  record.

A broken chain SHOULD be surfaced as a warning metric and logged as a
security event. The collector MAY still accept and forward a broken
chain record but MUST annotate the delivery status with a chain
validation warning.

### Per-Sink Delivery Status

For each required sink the collector SHOULD report:

- `exporter_name` – configured name of the sink exporter.
- `sink_type` – type of sink (e.g. `opensearch`, `s3`, `splunk`).
- `delivery_status` – `success`, `failed`, `timeout`, `retrying`, or
  `unknown`.
- `attempt_count` – number of delivery attempts made.
- `last_attempt_at` – timestamp of the most recent attempt.
- `sink_ack_id` – acknowledgement identifier returned by the sink, if
  available.
- `error_code` – sink-specific error code on failure.
- `error_message` – human-readable error description on failure.

A record outcome is successful only when every required sink reports
`delivery_status: success`.

### Record Lifecycle

Recommended state transitions:

```
received
  → accepted_pending_verify
    → verified_queued
      → verified_exporting
        → delivered_all_sinks   (terminal: success)
```

Alternative terminal states:

- `rejected_schema_invalid`
- `rejected_verify_failed`
- `rejected_authz`
- `delivered_partial` (treated as non-success)
- `failed_internal`

## Retry Guidance

SDK exporters SHOULD use the `retry_after` field when present.

Retry-ability by status code:

| Status                            | Behaviour                            |
|-----------------------------------|--------------------------------------|
| `202`, `429`, `503`               | Retryable with exponential back-off. |
| `400`, `401`, `403`, `409`, `413` | Non-retryable.                       |
| `500`                             | Implementation and policy dependent. |

## Security Requirements

The collector ingress MUST require secure transport and SHOULD support:

- TLS with server authentication (minimum TLS 1.2).
- mTLS for stronger client identity where required.
- Token-based authentication (e.g. Bearer token) where mTLS is not
  used.

The collector SHOULD validate `IntegrityValue` according to the
algorithm in `audit.integrity.algorithm` and the configured
verification policy before forwarding records to sinks.

## References

- [Audit Logging API](./api.md)
- [Audit Logging SDK](./sdk.md)
- [Audit Record Data Model](./data-model.md)
- [OTEP 0267 – Audit Logging Signal](../../oteps/0267-audit-logging.md)
