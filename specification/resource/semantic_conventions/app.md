# Configuration

**Status**: [Experimental](../../document-status.md)

**type:** `app`

**Description:** The end-user application.

<!-- semconv app -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `app.config_version` | string | A configuration version [1] | `42`; `5.6.2`; `808c8a73edef058f84e4b51da57c07779e48ed94` | No |
| `app.lang` | string | A BCP 47 language tag [2] | `en-US`; `zh-Hant-CN` | No |
| `app.region` | string | An ISO country code or a UN M49 code [3] | `US`; `419` | No |
| `app.version` | string | The version string of the application. | `6.5.0` | No |

**[1]:** An opaque configuration version identifier for applications with versioned configuration files. This may be a hash, semantic version, or similar identifying value.

**[2]:** Identifies the language translation being used by the running application as a [BCP 47 language tag](https://tools.ietf.org/rfc/bcp/bcp47.txt). Note that this may match one of the values listed in `os.langs`, or be a fallback language, depending on the application's bundled localizations.

**[3]:** Identifies the configured region of the running application using an [ISO 3166 alpha 2](https://www.iso.org/iso-3166-country-codes.html) country code or a [UN M49](https://en.wikipedia.org/wiki/UN_M49) code. This may be derived from OS APIs, such as `Locale.current.regionCode` on iOS, `Locale.getDefault().getCountry()` on Android, or `GlobalizationPreferences.HomeGeographicRegion` on Windows.
<!-- endsemconv -->
