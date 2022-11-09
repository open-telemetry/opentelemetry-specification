# fetchtiming

**Status**: [Experimental](../../../../document-status.md)

**type:** `fetchtiming`

**Description**: Represents the fetchtiming  event that has page fetch timing details.

**Note**: This event will be sent as a log event and will follow the semantic convention for a log.  The below attributes will be present as nested attributes in the event.data attribute of the log event.

> Below is a sample representation attributes to get the folder structure approved, as a first step.

## data

[common attributes](.\common.md)
| Attribute  | Type | Value  | Requirement Level |
|---|---|---|---|
| `browser.requesttype` | string | `fetch`, `XHR`| Required |
