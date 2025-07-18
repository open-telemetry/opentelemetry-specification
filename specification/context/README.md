<!--- Hugo front matter used to generate the website version of this page:
aliases: [/docs/reference/specification/context/context]
path_base_for_github_subdir:
  from: tmp/otel/specification/context/_index.md
  to: context/README.md
--->

# Context

**Status**: [Stable](../document-status.md).

**Concept**: [Context](/docs/context-propagation/#context)

## Overview

A `Context` is a propagation mechanism which carries execution-scoped values
across API boundaries and between logically associated [execution units](../glossary.md#execution-unit).
Cross-cutting concerns access their data in-process using the same shared
`Context` object.

A `Context` MUST be immutable, and its write operations MUST
result in the creation of a new `Context` containing the original
values and the specified values updated.

Languages are expected to use the single, widely used `Context` implementation
if one exists for them. In the cases where an extremely clear, pre-existing
option is not available, OpenTelemetry MUST provide its own `Context`
implementation. Depending on the language, its usage may be either explicit
or implicit.

Users writing instrumentation in languages that use `Context` implicitly are
discouraged from using the `Context` API directly. In those cases, users will
manipulate `Context` through cross-cutting concerns APIs instead, in order to
perform operations such as setting trace or baggage entries for a specified
`Context`.

A `Context` is expected to have the following operations, with their
respective language differences:
