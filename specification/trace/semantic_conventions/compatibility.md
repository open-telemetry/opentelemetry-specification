# Semantic conventions for Compatibility components

**Status**: [Experimental](../../document-status.md)

This document defines trace semantic conventions used by the
compatibility components, e.g. OpenTracing Shim layer.

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [OpenTracing](#opentracing)

<!-- tocstop -->

## OpenTracing

`Link`s created by the OpenTracing Shim MUST set `opentracing.ref_type`
with one of the accepted values, describing the direct causal relationships
between a child Span and a parent Span, as defined by
[OpenTracing](https://github.com/opentracing/specification/blob/master/specification.md).

<!-- semconv opentracing -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `opentracing.ref_type` | string | Parent-child Reference type [1] | `child_of` | Recommended |

**[1]:** The causal relationship between a child Span and a parent Span.

`opentracing.ref_type` MUST be one of the following:

| Value  | Description |
|---|---|
| `child_of` | The parent Span depends on the child Span in some capacity |
| `follows_from` | The parent Span does not depend in any way on the result of the child Span |
<!-- endsemconv -->
