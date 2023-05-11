# Device

**Status**: [Experimental](../../document-status.md)

**NOTICE** Semantic Conventions are moving to a
[new location](http://github.com/open-telemetry/semantic-conventions).

No changes to this document are allowed.

**type:** `device`

**Description**: The device on which the process represented by this resource is running.

<!-- semconv device -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `device.id` | string | A unique identifier representing the device [1] | `2ab2916d-a51f-4ac8-80ee-45ac31a28092` | Recommended |
| `device.model.identifier` | string | The model identifier for the device [2] | `iPhone3,4`; `SM-G920F` | Recommended |
| `device.model.name` | string | The marketing name for the device model [3] | `iPhone 6s Plus`; `Samsung Galaxy S6` | Recommended |
| `device.manufacturer` | string | The name of the device manufacturer [4] | `Apple`; `Samsung` | Recommended |

**[1]:** The device identifier MUST only be defined using the values outlined below. This value is not an advertising identifier and MUST NOT be used as such. On iOS (Swift or Objective-C), this value MUST be equal to the [vendor identifier](https://developer.apple.com/documentation/uikit/uidevice/1620059-identifierforvendor). On Android (Java or Kotlin), this value MUST be equal to the Firebase Installation ID or a globally unique UUID which is persisted across sessions in your application. More information can be found [here](https://developer.android.com/training/articles/user-data-ids) on best practices and exact implementation details. Caution should be taken when storing personal data or anything which can identify a user. GDPR and data protection laws may apply, ensure you do your own due diligence.

**[2]:** It's recommended this value represents a machine readable version of the model identifier rather than the market or consumer-friendly name of the device.

**[3]:** It's recommended this value represents a human readable version of the device model rather than a machine readable alternative.

**[4]:** The Android OS provides this field via [Build](https://developer.android.com/reference/android/os/Build#MANUFACTURER). iOS apps SHOULD hardcode the value `Apple`.
<!-- endsemconv -->
