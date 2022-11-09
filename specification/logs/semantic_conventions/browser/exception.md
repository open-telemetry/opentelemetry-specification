# exception

**Status**: [Experimental](../../../../document-status.md)

**type:** `exception`

**Description**: Represents the exception event.

**Note**: This event will be sent as a log event and will follow the semantic convention for a log.  The below attributes will be present as nested attributes in the event.data attribute of the log event.

> Below is a sample representation attributes to get the folder structure approved, as a first step.

## data

[common attributes](.\common.md)
| Attribute  | Type | Value  | Requirement Level |
|---|---|---|---|
| `message` | string | `VM516:1 Uncaught ReferenceError: a is not defined at <anonymous>:1:1` | Required |
| `type` | string | `sendAppErrorEvent`  | Required |

