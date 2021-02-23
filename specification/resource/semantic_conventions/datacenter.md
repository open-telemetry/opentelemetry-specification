# DataCenter

**Status**: [Experimental](../../document-status.md)

**type:** `datacenter`

**Description:** Generic DataCenter infrastructure tagging.

<!-- semconv datacenter -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `dc.name` | string | Name of datacenter. | `dc-name` | No |
| `dc.provider.name` | string | Name of the datacenter provider | `corp` | No |
| `dc.provider.type` | string | Type of datacenter | `colocation` | No |
| `dc.suite` | string | Name of the datacenter suite | `suite-5` | No |
| `dc.site` | string | Name of the datacenter site | `site-1` | No |
| `dc.cage` | string | Name of the cage | `cage-1` | No |
| `dc.pod` | string | Name of the pod | `pod-4` | No |
| `dc.rack` | string | Name of the rack | `rack-7` | No |

`dc.provider.name` MUST be one of the following or, if none of the listed values apply, a custom value:

| Value  | Description |
|---|---|
| `aws` | Amazon Web Services |
| `azure` | Microsoft Azure |
| `gcp` | Google Cloud Platform |
| `corp` | Internally Hosted Platform |

`dc.provider.type` MUST be one of the following or, if none of the listed values apply, a custom value:

| Value  | Description |
|---|---|
| `cloud` | Amazon Web Services |
| `colocation` | Microsoft Azure |
| `internal` | Google Cloud Platform |

<!-- endsemconv -->
