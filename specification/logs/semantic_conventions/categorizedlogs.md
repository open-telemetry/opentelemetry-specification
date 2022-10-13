# Semantic Convention for Categorize Logs

**Status**: [Experimental](../../document-status.md)

This document describes the attributes of Categorized Logs that are represented
by `LogRecord`s. All Categorized Logs have a name and a category. The category
is a namespace for names and is used as a mechanism to avoid conflicts of
names.

<!-- semconv event -->
| Attribute             | Type | Description                                                                                                                  | Examples  | Requirement Level |
|-----------------------|---|------------------------------------------------------------------------------------------------------------------------------|---|---|
| `log.name`            | string | The name identifies the log type.                                                                                            | `click`; `exception` | Required |
| `log.category` | string | The category identifies the context in which the log is defined. An log name is unique only within a cagtegory. [1] | `browser` | Required |

**[1]:** An `log.name` is supposed to be unique only in the context of an
`log.category`, so this allows for two logs in different categories to
have same `log.name`, yet be unrelated logs.

`log.category` has the following list of well-known values. If one of them applies, then the respective value MUST be used, otherwise a custom value MAY be used.

| Value  | Description              |
|---|--------------------------|
| `browser` | Events from browser apps |
| `device` | Events from mobile apps  |
| `k8s` | Events from Kubernetes   |
<!-- endsemconv -->