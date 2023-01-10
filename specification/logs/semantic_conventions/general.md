# General attributes

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
| `log.record.id` | string | A unique identifier for the Log Record. [1] | `click`; `exception` | Recommended |

**[1]:** MUST be an [Universally Unique Lexicographically Sortable Identifier (ULID)](https://github.com/ulid/spec). If a value is provided other log records, with the same value, will be considered to be duplicates and can be removed safely. This means, that two distinguishable log records MUST have different values. However in the case of duplication it is not guaranteed that duplicated log records have the same value.
<!-- endsemconv -->
