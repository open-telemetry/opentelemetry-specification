# Device

**Status**: [Experimental](../../document-status.md)

**type:** `device`

**Description**: The device on which the process represented by this resource is running.

<!-- semconv device -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `device.id` | string | A unique identifier representing the device [1] | `2ab2916d-a51f-4ac8-80ee-45ac31a28092` | No |
| `device.model` | string | The model identifier for the device [2] | `iPhone3,4`; `SM-G920F` | No |

**[1]:** For example, in an iOS application this might be the  [vendor identifier](https://developer.apple.com/documentation/uikit/uidevice/1620059-identifierforvendor).

**[2]:** It's recommended this value represents a machine readable version of the model identifier rather than the market or consumer-friendly name of the device.
<!-- endsemconv -->