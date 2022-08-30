# Semantic Convention for event attributes

**Status**: [Experimental](../../document-status.md)

This document describes the attributes of standalone Events that are represented
by `LogRecord`s. All standalone Events have a name and a domain. The Event domain
is a namespace for event names and is used as a mechanism to avoid conflicts of
event names.

<!-- semconv event -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `event.name` | string | The name identifies the event. | `click`; `exception` | Required |
| `event.domain` | string | The domain identifies the context in which an event happened. An event name is unique only within a domain. [1] | `browser` | Required |

**[1]:** An `event.name` is supposed to be unique only in the context of an
`event.domain`, so this allows for two events in different domains to
have same `event.name`, yet be unrelated events.

`event.domain` has the following list of well-known values. If one of them applies, then the respective value MUST be used, otherwise a custom value MAY be used.

| Value  | Description |
|---|---|
| `browser` | Events from browser apps |
| `device` | Events from mobile apps |
| `k8s` | Events from Kubernetes |
<!-- endsemconv -->