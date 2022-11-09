# pageview

**Status**: [Experimental](../../../../document-status.md)

**type:** `pageview`

**Description**: Represents a page impression event.

**Note**: This event will be sent as a log event and will follow the semantic convention for a log.  The below attributes will be present as nested attributes in the event.data attribute of the log event.

> Below is a sample representation attributes to get the folder structure approved, as a first step.

## data

[common attributes](.\common.md)
| Attribute  | Type | Value  | Requirement Level |
|---|---|---|---|
| `referrer` | string | "https://www.sitexyz.com/homepage.html" | Optional |
| `type` | integer | 0 - Physical page, 1 - Virtual page | Required |
| `userconsent` | boolean | true - consented, false - not consented | Required |
