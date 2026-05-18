<!--- Hugo front matter used to generate the website version of this page:
linkTitle: Data Model
weight: 2
--->

# Audit Record Data Model

**Status**: [Development](../document-status.md)

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [Audit Record Data Model](#audit-record-data-model)
  - [Design Notes](#design-notes)
    - [Requirements](#requirements)
    - [Relationship to LogRecord](#relationship-to-logrecord)
    - [OTLP Envelope Layers](#otlp-envelope-layers)
  - [AuditRecord Definition](#auditrecord-definition)
    - [LogRecord Field Usage](#logrecord-field-usage)
      - [Field: `Timestamp`](#field-timestamp)
      - [Field: `ObservedTimestamp`](#field-observedtimestamp)
      - [Field: `EventName`](#field-eventname)
      - [Field: `Body`](#field-body)
      - [Field: `Attributes`](#field-attributes)
    - [Audit Semantic Attributes](#audit-semantic-attributes)
      - [Mandatory Attributes](#mandatory-attributes)
      - [Attribute: `audit.record.id`](#attribute-auditrecordid)
      - [Actor Attributes](#actor-attributes)
      - [Attribute: `audit.action`](#attribute-auditaction)
      - [Attribute: `audit.outcome`](#attribute-auditoutcome)
      - [Optional Attributes](#optional-attributes)
      - [Target Attributes](#target-attributes)
      - [Source Attributes](#source-attributes)
      - [Integrity Attributes](#integrity-attributes)
      - [Ordering Attributes](#ordering-attributes)
    - [Integrity Resource Attributes](#integrity-resource-attributes)
      - [Attribute: `audit.integrity.algorithm`](#attribute-auditintegrityalgorithm)
      - [Attribute: `audit.integrity.certificate`](#attribute-auditintegritycertificate)
  - [AuditReceipt Definition](#auditreceipt-definition)
    - [Field: `RecordId`](#field-recordid)
    - [Field: `IntegrityHash`](#field-integrityhash)
    - [Field: `SinkTimestamp`](#field-sinktimestamp)
  - [Example AuditRecords](#example-auditrecords)
    - [Successful user login](#successful-user-login)
    - [Failed privileged configuration change](#failed-privileged-configuration-change)
  - [References](#references)

<!-- tocstop -->

</details>

## Design Notes

### Requirements

The Audit Record Data Model was designed to satisfy the following
requirements:

- Every audit record MUST carry sufficient information to identify the
  actor, the action performed, the target of the action, and the
  outcome. This is the minimum required by ISO 27001 Annex A (event
  logging) and equivalent compliance frameworks.

- The data model MUST include timestamps that allow clock-skew detection
  across distributed services (ISO 27001 – clock synchronisation).

- The data model MUST support optional cryptographic integrity proofs
  (asymmetric digital signatures or symmetric HMACs) so that records
  can be verified for integrity after delivery.

- The data model MUST be efficiently representable in OTLP by reusing
  the existing `LogRecord` proto message as a transport container.

- The data model MUST be extensible via arbitrary key-value attributes
  to accommodate application-specific compliance requirements.

### Relationship to LogRecord

An `AuditRecord` is a `LogRecord` that uses the standard dedicated
`LogRecord` fields for the universal concepts they represent, and
carries all audit-specific information as `Attributes` following the
`audit.*` semantic convention namespace.

This follows the established OTel convention: universal concepts
(timestamps, event name, body, context) receive dedicated top-level
`LogRecord` fields; signal- and domain-specific information is
expressed as semantic-convention attributes. Audit records are
therefore processable by any OTel tooling that understands `LogRecord`s.

The `SeverityNumber` and `SeverityText` fields of the underlying
`LogRecord` SHOULD NOT be set for audit records. Severity is not a
meaningful concept for audit events; the `audit.outcome` attribute
serves a structurally similar purpose.

### OTLP Envelope Layers

The following OTLP envelope layers apply to audit records:

| OTLP layer             | Role in audit logging                                            |
|------------------------|------------------------------------------------------------------|
| `Resource`             | Emitting service / host; integrity attrs (see below).            |
| `LogRecord`            | Carries the `AuditRecord` via dedicated fields and `Attributes`. |
| `InstrumentationScope` | **Not applicable.** MUST be left empty by exporters.             |

The `Resource` also carries `audit.integrity.algorithm` and
`audit.integrity.certificate` — see
[Integrity Resource Attributes](#integrity-resource-attributes).

## AuditRecord Definition

An `AuditRecord` is a single security-relevant event emitted by
application or system code on behalf of an actor. It is transported
as a `LogRecord`; the following two tables summarise how `LogRecord`
fields are used and which semantic attributes carry audit-specific
data.

### LogRecord Field Usage

| LogRecord Field        | Audit Usage                            | Required                       |
|------------------------|----------------------------------------|--------------------------------|
| `Timestamp`            | Time the auditable action occurred     | MUST be set                    |
| `ObservedTimestamp`    | Time the SDK observed the event        | MUST be set                    |
| `EventName`            | Semantic name of the audit event type  | MUST be set; MUST NOT be empty |
| `Body`                 | Free-form or structured event details  | MAY be set                     |
| `Attributes`           | Audit semantic attributes (see below)  | MUST contain mandatory attrs   |
| `Resource`             | Emitting service / host metadata       | MUST be set                    |
| `TraceId`              | Correlation to an active trace, if any | MAY be set                     |
| `SpanId`               | Correlation to an active span, if any  | MAY be set                     |
| `SeverityNumber`       | Not applicable for audit records       | SHOULD NOT be set              |
| `SeverityText`         | Not applicable for audit records       | SHOULD NOT be set              |
| `InstrumentationScope` | Not applicable for audit records       | MUST be left empty             |

#### Field: `Timestamp`

| Property   | Value                            |
|------------|----------------------------------|
| Type       | `fixed64`                        |
| Required   | MUST be set                      |
| Constraint | `Timestamp <= ObservedTimestamp` |

The time at which the audit event occurred, expressed as nanoseconds
since the UNIX epoch (UTC). The application MUST set this field to the
time the auditable action actually took place.

If the application cannot determine the precise event time, it SHOULD
use the current time at the moment of the `emit` call and document
this in the `Body` or `Attributes`.

The clock used for `Timestamp` MUST be a wall-clock source
synchronised via NTP or an equivalent protocol. The SDK SHOULD warn at
startup if the system clock offset exceeds one second.

#### Field: `ObservedTimestamp`

| Property   | Value                                              |
|------------|----------------------------------------------------|
| Type       | `fixed64`                                          |
| Required   | MUST be set                                        |
| Constraint | `ObservedTimestamp >= Timestamp` and `<= now(UTC)` |

The time at which the OpenTelemetry SDK observed the event, expressed
as nanoseconds since the UNIX epoch (UTC). The SDK MUST set this field
to the current time when `emit` is called if the application does not
provide it.

`ObservedTimestamp` enables the audit sink to detect clock skew between
the emitting service and the SDK host. A significant difference between
`Timestamp` and `ObservedTimestamp` SHOULD be treated as a clock
synchronisation warning.

#### Field: `EventName`

| Property | Value                          |
|----------|--------------------------------|
| Type     | `string`                       |
| Required | MUST be set; MUST NOT be empty |

A short, dot-separated semantic name that uniquely identifies the type
of audit event. `EventName` MUST be stable across releases and SHOULD
follow a hierarchical naming convention, for example:

- `user.login.success`
- `user.login.failure`
- `resource.file.read`
- `config.change`
- `privilege.escalation`

Semantic conventions for common `EventName` values SHOULD be defined
in the
[OpenTelemetry Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/).

#### Field: `Body`

| Property | Value      |
|----------|------------|
| Type     | `AnyValue` |
| Required | MAY be set |

Free-form additional information about the audit event. The value MAY
be a string, a byte buffer, or a structured object. Applications SHOULD
store information that does not fit naturally into the named mandatory
attributes here.

The `Body` MUST NOT duplicate information already present in the
mandatory `Attributes`.

#### Field: `Attributes`

| Property | Value                                   |
|----------|-----------------------------------------|
| Type     | `map<string, AnyValue>`                 |
| Required | MUST contain mandatory audit attributes |

Key-value pairs that carry audit-specific context. The mandatory and
optional attribute names are defined in
[Audit Semantic Attributes](#audit-semantic-attributes) below.
Applications MAY add additional attributes beyond those listed here
using standard OTel
[attribute naming conventions](../common/attribute-naming.md).

Attribute keys MUST be unique within a record. If the same key is set
multiple times, the last value MUST be used.

### Audit Semantic Attributes

All audit-specific data that does not map to a standard `LogRecord`
dedicated field is expressed as `Attributes` following the `audit.*`
semantic convention namespace, or by reusing existing semantic
convention attributes where a direct mapping exists.

#### Mandatory Attributes

| Attribute name     | Type     | Required | Description                                    |
|--------------------|----------|----------|------------------------------------------------|
| `audit.record.id`  | `string` | MUST     | Unique stable identifier; UUID v4 recommended. |
| `audit.actor.id`   | `string` | MUST     | Identity that performed the action.            |
| `audit.actor.type` | `string` | MUST     | `user`, `service`, or `system`.                |
| `audit.action`     | `string` | MUST     | Verb describing what was done.                 |
| `audit.outcome`    | `string` | MUST     | `success`, `failure`, or `unknown`.            |

#### Attribute: `audit.record.id`

A caller-generated unique identifier for this `AuditRecord`. The value
MUST be immutable once set and MUST remain stable across retries so
that receivers can deduplicate records delivered more than once.

The caller SHOULD use a UUID v4 or an equivalent unpredictable unique
identifier. The SDK MUST generate a UUID v4 if the caller does not
provide one.

`audit.record.id` is echoed back unchanged in the
[`AuditReceipt`](#auditreceipt-definition), allowing the emitting
application to correlate receipts with the original `emit` call.

#### Actor Attributes

Actor attributes identify the entity that performed the auditable
action. Together, `audit.actor.id` and `audit.actor.type` provide the
minimum identity context required by ISO 27001 Annex A item 1 (user
IDs).

**`audit.actor.id`**

The identity of the entity that performed the action. This MAY be a
user ID (string or integer cast to string), a service account name,
or a fully qualified system identifier. If the actor identity cannot
be determined (for example, an unauthenticated request),
`audit.actor.id` MUST still be set to a value indicating the unknown
state (e.g. `"anonymous"` or `"unknown"`).

Applications where the actor is an authenticated end user MAY set
`enduser.id` in addition to `audit.actor.id` when the values differ
(for example, when `audit.actor.id` is a stable internal identifier
and `enduser.id` is the authentication subject claim).

**`audit.actor.type`**

Classifies the kind of entity that performed the action:

| Value     | Meaning                                                |
|-----------|--------------------------------------------------------|
| `user`    | A human user, identified by a user account.            |
| `service` | An automated service, daemon, or service account.      |
| `system`  | The operating system or a privileged system component. |

Applications SHOULD choose the most appropriate value based on context.
Use `service` for non-human actors that operate autonomously, and
`user` for human-initiated actions, even if performed by an AI agent
on behalf of a user.

#### Attribute: `audit.action`

A short verb or verb phrase that describes what the actor did.
Applications SHOULD use uppercase verbs to distinguish action values
from event names. Common values include:

`LOGIN`, `LOGOUT`, `READ`, `WRITE`, `CREATE`, `UPDATE`, `DELETE`,
`EXECUTE`, `APPROVE`, `REJECT`, `EXPORT`, `IMPORT`.

Applications MAY define domain-specific action verbs. Action names
SHOULD be stable across releases.

#### Attribute: `audit.outcome`

The result of the auditable action:

| Value     | Meaning                                                      |
|-----------|--------------------------------------------------------------|
| `success` | The action completed successfully.                           |
| `failure` | The action was attempted but did not complete successfully.  |
| `unknown` | The outcome could not be determined at the time of emission. |

ISO 27001 Annex A items 5 and 6 require logging both successful and
unsuccessful access attempts. Using `unknown` SHOULD be avoided except
for fire-and-forget actions where acknowledgement is not possible.

#### Optional Attributes

| Attribute name          | Type     | Required | Description                                           |
|-------------------------|----------|----------|-------------------------------------------------------|
| `audit.target.id`       | `string` | SHOULD   | Identifier of the resource acted upon.                |
| `audit.target.type`     | `string` | SHOULD   | Type of the target resource.                          |
| `audit.source.id`       | `string` | MAY      | Network address or identifier of the source.          |
| `audit.source.type`     | `string` | MAY      | Type of the source (e.g. `ipv4`, `ipv6`, `hostname`). |
| `audit.integrity.value` | `string` | MAY      | Base64-encoded cryptographic integrity proof.         |
| `audit.sequence.number` | `int`    | MAY      | Monotonic counter for hash-chain continuity.          |
| `audit.prev.hash`       | `string` | MAY      | SHA-256 of the previous record in the stream.         |
| `audit.schema.version`  | `string` | SHOULD   | Schema version of the audit payload.                  |

#### Target Attributes

**`audit.target.id`** SHOULD be set to an identifier for the object
upon which the action was performed. Examples:

- A file path (`/etc/passwd`)
- A database table name (`users`)
- A REST endpoint path (`/api/v1/orders/42`)
- A cloud resource ARN or ID

**`audit.target.type`** SHOULD classify the type of resource, for
example `file`, `database.table`, `http.endpoint`, `k8s.configmap`.
When applicable, values SHOULD align with existing OTel semantic
convention resource types.

If the action was not directed at a specific resource (for example, a
system startup event), both attributes MAY be omitted.

#### Source Attributes

**`audit.source.id`** SHOULD be set for network-initiated actions (for
example, a login attempt over HTTPS). The value SHOULD be an IPv4
address in dotted-decimal notation (`203.0.113.42`) or a full IPv6
address (`2001:db8::1`), or a hostname.

**`audit.source.type`** SHOULD classify the address format. Recommended
values are `ipv4`, `ipv6`, and `hostname`. When the source cannot be
determined, both attributes MAY be omitted.

#### Integrity Attributes

**`audit.integrity.value`**

A base64-encoded cryptographic integrity proof over the canonical
serialization of the `AuditRecord`. The proof is either an asymmetric
digital signature or a symmetric HMAC, as indicated by the
`audit.integrity.algorithm` `Resource` attribute (see
[Integrity Resource Attributes](#integrity-resource-attributes)).

When `audit.integrity.value` is set, `audit.integrity.algorithm` MUST
be set as a `Resource` attribute.

#### Ordering Attributes

The optional ordering attributes enable hash-chain validation across a
sequence of `AuditRecord`s. When populated, receivers can detect
whether records have been deleted, inserted, or reordered by verifying
that the sequence numbers are monotonically increasing and that each
`audit.prev.hash` matches the `IntegrityHash` returned in the preceding
record's `AuditReceipt`.

Implementations that require strong tamper-evidence for ordered
sequences SHOULD populate both `audit.sequence.number` and
`audit.prev.hash`.

**`audit.sequence.number`**

A monotonically increasing integer counter, scoped to a single
`AuditLogger` instance or a named audit stream. The first record in a
stream SHOULD have `audit.sequence.number` equal to `1`. A gap between
two consecutive values indicates that one or more records were lost or
deleted and SHOULD trigger an alert.

**`audit.prev.hash`**

The `IntegrityHash` of the immediately preceding record in the same
audit stream (as returned in the preceding `AuditReceipt`). The first
record in a stream SHOULD set `audit.prev.hash` to the SHA-256 hash of
the empty string
(`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`).

A `audit.prev.hash` that does not match the stored `IntegrityHash` of
the previous record indicates tampering and MUST be treated as a
critical integrity violation.

### Integrity Resource Attributes

The signing algorithm and key reference are identical for every
`AuditRecord` emitted by a given service instance. They are therefore
carried once as OTel `Resource` attributes instead of being repeated
in every record.

#### Attribute: `audit.integrity.algorithm`

| Property | Value                                                                    |
|----------|--------------------------------------------------------------------------|
| Type     | `string`                                                                 |
| Required | MUST be set if `audit.integrity.value` is set on any record in the batch |

The algorithm used to compute `audit.integrity.value` for all records
produced by this resource.

- For asymmetric signatures the value SHOULD be a registered JWA
  algorithm identifier, for example `RS256`, `ES256`, or `EdDSA`.
- For symmetric HMACs the value SHOULD be a registered IANA MAC
  algorithm identifier, for example `HMAC-SHA256` or `HMAC-SHA512`.

#### Attribute: `audit.integrity.certificate`

| Property | Value      |
|----------|------------|
| Type     | `string`   |
| Required | MAY be set |

A reference to the signing key used to produce `audit.integrity.value`.
MUST NOT be set when `audit.integrity.algorithm` denotes a symmetric
MAC algorithm.

The value MUST be one of the following forms, listed from most to
least self-contained:

- **Full certificate** – base64 (standard encoding, no line wrapping)
  of the DER-encoded X.509 public-key certificate. Relying parties
  can verify `audit.integrity.value` without any out-of-band lookup.
- **Fingerprint** – a hash string in the form `sha256:<hex>` or
  `sha1:<hex>`, where `<hex>` is the colon-separated hex encoding of
  the DER certificate hash (e.g. `sha256:4A:6C:9F:…`). Requires
  matching against a locally trusted certificate.
- **Key ID** – an opaque string identifier (e.g. a JWK `kid` claim
  such as `key-2024-01`) agreed between emitter and relying party.
  Requires key retrieval via JWK Set URI or equivalent.
- **SKI** – Subject Key Identifier in colon-separated hex
  (e.g. `3C:F0:…`). Requires a PKI lookup.
- **Issuer + Serial** – Issuer Distinguished Name and serial number
  separated by a slash (e.g. `CN=MyCA,O=Acme Corp/12345`). Requires
  a PKI lookup.

If `audit.integrity.certificate` is omitted and
`audit.integrity.algorithm` denotes an asymmetric algorithm, the
relying party MUST obtain the public key through a separately
configured trust anchor.

## AuditReceipt Definition

An `AuditReceipt` is returned by `AuditLogger.emit` once the audit
sink has successfully persisted the record. It serves as proof-of-delivery
and enables integrity verification by the emitting application.

| Field           | Type      | Required    | Description                                                  |
|-----------------|-----------|-------------|--------------------------------------------------------------|
| `RecordId`      | `string`  | MUST be set | Echoes the caller's `audit.record.id` attribute.             |
| `IntegrityHash` | `string`  | MUST be set | SHA-256 of the record as persisted by the sink.              |
| `SinkTimestamp` | `fixed64` | MUST be set | Nanoseconds since UNIX epoch when the sink wrote the record. |

### Field: `RecordId`

The value of the `audit.record.id` attribute from the corresponding
`AuditRecord` as provided by the caller. The sink MUST echo this value
unchanged. Callers use it to correlate the receipt with the original
`emit` call and to confirm that the correct record was persisted.

### Field: `IntegrityHash`

The SHA-256 hash of the canonical serialization of the `AuditRecord`
as it was written to persistent storage, computed by the sink. Returned
to the emitting application so that it can verify that the record was
not altered between emission and persistence.

The emitting application SHOULD compute the same hash locally
immediately after calling `emit` and compare it to the received
`IntegrityHash`. A mismatch indicates that the record was altered in
transit or by the sink and SHOULD trigger an alert.

### Field: `SinkTimestamp`

Nanoseconds since the UNIX epoch (UTC) at which the audit sink
persisted the record. This value MAY differ from `ObservedTimestamp`
due to buffering or network latency, and MAY be used to detect
abnormally long delivery times.

## Example AuditRecords

The examples below show the `LogRecord` representation of an
`AuditRecord`. Resource attributes are shown separately.

### Successful user login

```json
{
  "Timestamp": 1714041600000000000,
  "ObservedTimestamp": 1714041600001000000,
  "EventName": "user.login.success",
  "Body": null,
  "Attributes": {
    "audit.record.id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "audit.actor.id": "u8472",
    "audit.actor.type": "user",
    "audit.action": "LOGIN",
    "audit.outcome": "success",
    "audit.target.id": "/api/auth/session",
    "audit.target.type": "http.endpoint",
    "audit.source.id": "203.0.113.42",
    "audit.source.type": "ipv4",
    "audit.schema.version": "1.0.0",
    "session.id": "sess-abc123",
    "tls.version": "TLSv1.3"
  }
}
```

Resource attributes:

```json
{
  "service.name": "auth-service",
  "service.version": "2.3.1"
}
```

### Failed privileged configuration change

```json
{
  "Timestamp": 1714041700000000000,
  "ObservedTimestamp": 1714041700002000000,
  "EventName": "config.change",
  "Body": "Authorization denied: missing role 'config-writer'",
  "Attributes": {
    "audit.record.id": "f7e8d9c0-b1a2-3456-cdef-0987654321ab",
    "audit.actor.id": "svc-deployer",
    "audit.actor.type": "service",
    "audit.action": "UPDATE",
    "audit.outcome": "failure",
    "audit.target.id": "production/app-secrets",
    "audit.target.type": "k8s.configmap",
    "audit.schema.version": "1.0.0",
    "request.id": "req-xyz789",
    "k8s.namespace": "production"
  }
}
```

## References

- [OTEP 0267 – Audit Logging Signal](../../oteps/0267-audit-logging.md)
- [OTEP 0097 – Log Data Model](../../oteps/logs/0097-log-data-model.md)
- [ISO 27001:2022 Annex A – Audit Logging controls](https://www.iso.org/standard/27001)
- [Common Event Format (CEF) specification](https://www.microfocus.com/documentation/arcsight/arcsight-smartconnectors-8.4/cef-implementation-standard/)
