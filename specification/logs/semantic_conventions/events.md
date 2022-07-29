# Semantic Convention for event attributes

**Status**: [Experimental](../../document-status.md)

This document describes the attributes of standalone Events that are represented
by `LogRecord`s. All standalone Events have a name and a domain.The Event domain
is a namespace for event names and is used as a mechanism to avoid conflicts of
event names.

<!-- semconv event -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `event.name` | string | The name identifies the event. | `click`; `exception` | Required |
| `event.domain` | string | The domain identifies the context in which an event happened. An event name is unique only within a domain. [1] | `browser`; `mobile`; `kubernetes` | Recommended |

**[1]:** An `event.name` is supposed to be unique only in the context of an
`event.domain`, so this allows for two events in different domains to
have same `event.name`, yet be unrelated events. No claim is made
about the uniqueness of `event.name`s in the absence of `event.domain`.
<!-- endsemconv -->