# pageview

**Status**: [Experimental](../../../../document-status.md)

**type:** `pageview`

**Description**: Represents a page impression event.

**Note**: This event will be sent as a log event and will follow the semantic convention for a log.  The below attributes will be present as nested attributes in the event.data attribute of the log event.

<!-- semconv browser -->
| Attribute  | Type | Value  | Requirement Level |
|---|---|---|---|
| `timestamp` | time | `navigation` | Required |
| `event.domain` | string | `browser` | Required |
<!-- endsemconv -->