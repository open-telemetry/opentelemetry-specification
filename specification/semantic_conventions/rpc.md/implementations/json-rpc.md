# JSON RPC

**Status**: [Experimental](../../../document-status.md)

Conventions specific to [JSON RPC](https://www.jsonrpc.org/).

## Requirements

`rpc.system` MUST be set to `"jsonrpc"`.

## Attributes

<!-- semconv rpc.jsonrpc -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `rpc.jsonrpc.version` | string | Protocol version as in `jsonrpc` property of request/response. Since JSON-RPC 1.0 does not specify this, the value can be omitted. | `2.0`; `1.0` | If missing, it is assumed to be "1.0". |
| `rpc.jsonrpc.request_id` | string | `id` property of request or response. Since protocol allows id to be int, string, `null` or missing (for notifications), value is expected to be cast to string for simplicity. Use empty string in case of `null` value. Omit entirely if this is a notification. | `10`; `request-7`; `` | No |
| `rpc.jsonrpc.error_code` | int | `error.code` property of response if it is an error response. | `-32700`; `100` | If missing, response is assumed to be successful. |
| `rpc.jsonrpc.error_message` | string | `error.message` property of response if it is an error response. | `Parse error`; `User already exists` | No |
| `rpc.method` | string | The name of the (logical) method being called, must be equal to the $method part in the span name. [1] | `exampleMethod` | Yes |

**[1]:** This is always required for jsonrpc. See the note in the general RPC conventions for more information.
<!-- endsemconv -->
