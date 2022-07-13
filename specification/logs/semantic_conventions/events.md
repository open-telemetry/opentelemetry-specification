# Semantic Convention for event attributes

**Status**: [Experimental](../../document-status.md)

This document describes the attributes of standalone Events that are represented by `LogRecord`s. All standalone Events have a name and a domain. The Event domain is used as a mechanism to avoid conflicts with event names.

**type:** `event`

**Description:** Event attributes.

| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `event.name` | string | Name or type of the event. | `network-change`; `button-click`; `exception` | Yes |
| `event.domain` | string | Domain or scope for the event. | `profiling`; `browser`, `db`, `k8s` | No |

An `event.name` is supposed to be unique only in the context of an `event.domain`, so this allows for two events in different domains to have same `event.name`, yet be unrelated events. No claim is made about the uniqueness of `event.name`s in the absence of `event.domain`.

Note that Scope attributes are equivalent to the attributes at Span and LogRecord level, so recording the attribute `event.domain` on the Scope is equivalent to recording it on Spans and LogRecords within the Scope.

