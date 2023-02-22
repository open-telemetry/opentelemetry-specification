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

The primary container for (`payload`) details describing an `event` SHOULD
include the domain-specific information about the occurrence in the `event.data`
attribute, where the definition of the values included SHOULD conform to the
domain-specific schema. The schema SHOULD be identified by the `domain` and
`name` combination.

The `event.data` MUST only include the values as defined by it's domain-specific
schema, and if required one or more additional top-level Attributes MAY be added
to provide additional context about the `event`, but these attitional Attributes
SHOULD not be treated as a replacement for the details (`payload`) of the `event`.
For custom (Non-OpenTelemetry / User / System defined) `events` SHOULD define
their own domain-specific schema (domain + name combination) and include their
payload in the `event.data`.

This allows a standard processing model of an `event` as represented by a `LogRecord`
so that systems MAY choose how to route, validate and/or process known `events`
based on the domain-specific schema semantic-conventions for the `event.data`.
For example, common known events MAY have special meaning or representation while
unknown events are simply treated as generic custom events.

| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `event.name` | string | The name identifies the event. | `click`; `exception` | Required |
| `event.domain` | string | The domain identifies the business context for the events. [1] | `browser` | Required |
| `event.data` | [any](../data-model.md#type-any) \| [map<string, any>](../data-model.md#type-mapstring-any) | The domain-specific [2] `payload` of the `event` which provides details about the occurrence of the named event. | `{ connectStart: 100, connectEnd: 103, domainLookupStart: 80, domainLookupEnd: 90 }` | Optional [3] |

**[1]:** Events across different domains may have same `event.name`, yet be
unrelated events.

`event.domain` has the following list of well-known values. If one of them applies,
then the respective value MUST be used, otherwise a custom value MAY be used.
To avoid clashes custom event domains SHOULD use a reversed internet domain name
style [`com.github`, `com.example`]

| Value  | Description |
|---|---|
| `browser` | Events from browser apps |
| `device` | Events from mobile apps |
| `k8s` | Events from Kubernetes |

**[2]:** Each OpenTelemetry defined event will have it's own documented
semantic-conventions for `event.data`, while custom events SHOULD define
and document their own.

`event.data` MUST only contain the values as defined by it's domain-specific
schema which identifies information about the occurrence of the `event` (the
`payload` of the event). Which may include details about the occurrence
or data that was changed (depending on the schema of the domain-specific named
event)

The specification does not place any restriction on the fields or type of the
information included in the `event.data` Attribute as it's contents SHOULD conform
to the `schema` of the domain-specific event.

**[3]:** `event.data` is optional to support simple events which do not require
any form of payload, when a payload is required `events` SHOULD define a schema
and include an `event.data` with the payload over adding a collection of top-level
general Attributes.

## Possible Open [Experimental](../../document-status.md) Issues / Extensions

- `event.data` schema versioning support, options include :-
  - Defined at a higher OpenTelemetry level for Logs;
  - Included as part of the `event.name`;
  - Additional `event.schema` (Seems overkill for now);

- User/Application provided custom data
  - This is data that does not conform to any OpenTelemetry semantic conventions
    and is purely user provided data that they want persisted with the event,
    options include (with suggested names only):-
  - Define an OpenTelemetry semantic convention Attribute for `user.data` which
    would be un-validated / defined a nested Attributes (no-schema);
  - Define an event specific semantic convention Attribute for `event.user_data`
    which would also be an un-validated / defined nested Attributes (no-schema);
  - Explicitly excluded, would be an Attribute within the `event.data` to
    contain the same as this would overly complicate backend processing and could
    cause a name clash within the `event.data` as some `event` schema(s) are
    being defined in terms of existing external definitions (`browser`+`FetchTiming`
    `event.data` is based on [W3C PerformanceResourceTiming](https://w3c.github.io/resource-timing/#sec-performanceresourcetiming) ).
