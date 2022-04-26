# Configuration

**Status**: [Experimental](../../document-status.md)

**type:** `configuration`

**Description:** Any configurable software component.

<!-- semconv configuration -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `configuration.country` | string | An ISO country code [1] | `US` | No |
| `configuration.language` | string | A BCP 47 language tag [2] | `en-US`; `zh-Hant-CN` | No |
| `configuration.timezone` | string | An IANA Time Zone Database name [3] | `America/Los_Angeles`; `UTC` | No |
| `configuration.version` | string | A configuration version [4] | `42`; `5.6.2`; `808c8a73edef058f84e4b51da57c07779e48ed94` | No |

**[1]:** Identifies the country of the running environment using an [ISO 3166 alpha 2](https://www.iso.org/iso-3166-country-codes.html) country code.

**[2]:** Identifies the preferred language of the running environment using a [BCP 47 language tag](https://tools.ietf.org/rfc/bcp/bcp47.txt)

**[3]:** Identifies the timezone of the running environment, using a timezone identifier from the IANA [Time Zone Database](https://www.iana.org/time-zones).

**[4]:** An opaque configuration version identifier for systems with versioned configuration files. This may be a hash, semantic version, or similar identifying value.
<!-- endsemconv -->
