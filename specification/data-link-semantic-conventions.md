# Link Conventions

This document is about standard attributes for
[Links](api-tracing.md#add-links).

## Document conventions

Attributes are divided into groups, describing certain characteristics of a
link. Attributes in each group start with a specified prefix and a dot.

Attribute groups in this document have a **Required** column. If a link has at
least one attribute from the group, then it MUST also contain all the required
attributes of the group.

## Link types

* [Ignored parent](#ignored-parent)

### Ignored parent

**Prefix:** parent

**Description:** These attributes are used to denote a span context that was
ignored during a span creation as a parent and thus became only linked to the
span.

| Attribute | Description | Example | Required? |
|---|---|---|---|
| parent.kind | Kind of ignored span context. It MUST be either "local" or "remote". "local" denotes a span context that was a part of a current span at the time of a creation of the link. "remote" denotes a span context that was a part of remote span at the time of a creation of the link. | "local" | Yes |
