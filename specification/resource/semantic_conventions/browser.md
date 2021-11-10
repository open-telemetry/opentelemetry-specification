# Browser

**Status**: [Experimental](../../document-status.md)

**type:** `browser`

**Description**: The web browser in which the application represented by the resource is running. The `browser.*` attributes MUST be used only for resources that represent client-side devices - the presence of these attributes can be used to identify client-side telemetry.

<!-- semconv device -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `browser.name` | string | The web browser name | `Chrome` | No |
| `browser.version` | string | The web browser version | `90` | No |
| `browser.platform` | string | The operating system | `Windows` | No |
| `browser.mobile` | boolean | Flag indicating a mobile device | | No |
