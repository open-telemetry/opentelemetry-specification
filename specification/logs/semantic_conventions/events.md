# Semantic Convention for event attributes

**Status**: [Experimental](../../document-status.md)

This document describes the attributes of standalone Events that are represented
in the data model by `LogRecord`s. Events are recorded as LogRecords that are shaped
in a special way: Event LogRecords have the attributes `event.domain`
and `event.name` (and possibly other LogRecord attributes).

The `event.domain` attribute is used to logically separate events from different
systems. For example, to record Events from browser apps, mobile apps and
Kubernetes, we could use `browser`, `device` and `k8s` as the domain for their
Events. This provides a clean separation of semantics for events in each of the
domains.

Within a particular domain, the `event.name` attribute identifies the event.
Events with same domain and name are structurally similar to one another. For
example, some domains could have well-defined schema for their events based on
event names.

When recording events from an existing system as OpenTelemetry Events, it is
possible that the existing system does not have the equivalent of a name or
requires multiple fields to identify the structure of the events. In such cases,
OpenTelemetry recommends using a combination of one or more fields as the name
such that the name identifies the event structurally. It is also recommended that
the event names have low-cardinality, so care must be taken to use fields
that identify the class of Events but not the instance of the Event.

Events MAY include domain-specific information about the occurrence (`payload`)
of the `event`, when present this information MUST be included in the `event.data`
attribute the values included SHOULD conform to the domain-specific defined schema
for the identified `event`. This is the primary container for details about the
`event`.

Events MAY also include one or more additional Attributes which can be used to
provide additional context about the `event`, whether an Attribute is required
or optional SHOULD be defined by the domain-specific schema definition of the
`event`.

| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `event.name` | string | The name identifies the event. | `click`; `exception` | Required |
| `event.domain` | string | The domain identifies the business context for the events. [1] | `browser` | Required |
| `event.data` | [any](../data-model.md#type-any) \| [map<string, any>](../data-model.md#type-mapstring-any) | The domain-specific `payload` of the `event` which provides details about the occurrence of the named event. | `{ connectStart: 100, connectEnd: 103, domainLookupStart: 80, domainLookupEnd: 90 }` | Optional |

**[1]:** Events across different domains may have same `event.name`, yet be
unrelated events.

`event.domain` has the following list of well-known values. If one of them applies, then the respective value MUST be used, otherwise a custom value MAY be used.

| Value  | Description |
|---|---|
| `browser` | Events from browser apps |
| `device` | Events from mobile apps |
| `k8s` | Events from Kubernetes |

`event.data` contains the domain-specific information about the occurrence of the
`event` (ie. the payload of the event). And may include details about the occurrence
or data that was change (depending on the schema of the domain-specific named event)

The specification does not place any restriction on the fields or type of the
information included in the `event.data` Attribute as it's contents SHOULD conform
to the `schema` of the domain-specific event.
