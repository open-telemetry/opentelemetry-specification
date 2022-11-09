# useraction

**Status**: [Experimental](../../../../document-status.md)

**type:** `useraction`

**Description**: Represents an interaction event like click, scroll, etc.

**Note**: This event will be sent as a log event and will follow the semantic convention for a log.  The below attributes will be present as nested attributes in the event.data attribute of the log event.

> Below is a sample representation of the common browser attributes to get the folder structure approved, as a first step.

## data

[common attributes](.\common.md)
| Attribute  | Type | Value  | Requirement Level |
|---|---|---|---|
| `element.xpath` | string | `/bookstore/book/title` | Required |
