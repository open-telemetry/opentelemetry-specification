# General attributes

**NOTICE** Semantic Conventions are moving to a
[new location](http://github.com/open-telemetry/semantic-conventions).

No changes to this document are allowed.

**Status**: [Experimental](../../document-status.md)

The attributes described in this section are rather generic.
They may be used in any Log Record they apply to.

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [General log identification attributes](#general-log-identification-attributes)

<!-- tocstop -->

## General log identification attributes

These attributes may be used for identifying a Log Record.

<!-- semconv log.record -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `log.record.uid` | string | A unique identifier for the Log Record. [1] | `01ARZ3NDEKTSV4RRFFQ69G5FAV` | Opt-In |

**[1]:** If an id is provided, other log records with the same id will be considered duplicates and can be removed safely. This means, that two distinguishable log records MUST have different values.
The id MAY be an [Universally Unique Lexicographically Sortable Identifier (ULID)](https://github.com/ulid/spec), but other identifiers (e.g. UUID) may be used as needed.
<!-- endsemconv -->
