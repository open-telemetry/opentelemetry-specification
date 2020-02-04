# Link Conventions

This document is about standard attributes for
[Links](api-tracing.md#add-links).

## Document conventions

Attributes are divided into groups, depending on the link type. Attributes in
each group are prefixed with the link type and a dot.

Certain attribute groups in this document have a **Required** column. If an
attribute in the group that is described by the link type is marked as required
then the attribute MUST be present in the Link. If the **Required** column is
missing, then it is assumed that all the attributes in the group are optional.

## Link types

A link may be of a certain type and this can be described by the `link.type`
attribute. The value of the attribute MUST be a string. Each type of the link
below will provide a description with the value of the attribute.

* [Ignored parent](#ignored-parent)

### Ignored parent

**Link type:** `ignored-parent`

**Description:** These attributes are used to denote a span context that was
ignored during a span creation as a parent and thus became only linked to the
span.

| Attribute | Description | Example | Required? |
|---|---|---|---|
| ignored-parent.kind | Kind of ignored span context. It MUST be either "local" or "remote". "local" denotes a span context that was a part of a current span at the time of a creation of the link. "remote" denotes a span context that was a part of remote span at the time of a creation of the link. | "local" | Yes |
