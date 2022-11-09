# common

**Status**: [Experimental](../../../../document-status.md)

**type:** `common`

**Description**: Represents the set of common attributes that will be present for all Browser events.

**Note**: This event will be sent as a log event and will follow the semantic convention for a log.  The below attributes will be present as nested attributes in the event.data attribute of the log event.

> Below is a sample representation of the common browser attributes to get the folder structure approved, as a first step.

## Fixed attributes

| Attribute  | Type | Value  | Requirement Level |
|------------|------|--------|-------------------|
| `browser.platform` | string | `windows`, `linux`, `iOS` | Required |

## Varying attributes

| Attribute  | Type | Value  | Requirement Level |
|------------|------|--------|-------------------|
| `screen_width` | integer | `1337` | Required |
| `screen_height` | integer | `1013` | Required |
