# Browser

**Status**: [Experimental](../../document-status.md)

**type:** `browser`

**Description**: The web browser in which the application represented by the resource is running. The `browser.*` attributes MUST be used only for resources that represent applications running in a web browser. The presence of these attributes is intended to identify client-side telemetry.

<!-- semconv device -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `browser.name` | string | The web browser name | `Chrome` | No |
| `browser.version` | string | The web browser version | `90` | No |
| `browser.platform` | string | The operating system | `Windows` | No |
| `browser.mobile` | boolean | Flag indicating a mobile device | | No |
| `browser.user_agent` | string | Full user-agent string provided by the browser [1] | `'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36'` | No |

**[1]:** The user-agent value should be provided only from browsers that do not have a mechanism to retrieve name, version, and platform individually (for example from the User-Agent Client Hints API). 
