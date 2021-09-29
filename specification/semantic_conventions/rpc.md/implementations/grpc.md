# gRPC

**Status**: [Experimental](../../../document-status.md)

For remote procedure calls via [gRPC][], additional conventions are described in this section.

## Requirements

[Span Status](../../../trace/api.md#set-status) MUST be left unset for an `OK` gRPC status code, and set to `Error` for all others.

`rpc.system` MUST be set to `"grpc"`.

## Attributes

<!-- semconv rpc.grpc -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `rpc.grpc.status_code` | int | The [numeric status code](https://github.com/grpc/grpc/blob/v1.33.2/doc/statuscodes.md) of the gRPC request. | `0` | Yes |

`rpc.grpc.status_code` MUST be one of the following:

| Value  | Description |
|---|---|
| `0` | OK |
| `1` | CANCELLED |
| `2` | UNKNOWN |
| `3` | INVALID_ARGUMENT |
| `4` | DEADLINE_EXCEEDED |
| `5` | NOT_FOUND |
| `6` | ALREADY_EXISTS |
| `7` | PERMISSION_DENIED |
| `8` | RESOURCE_EXHAUSTED |
| `9` | FAILED_PRECONDITION |
| `10` | ABORTED |
| `11` | OUT_OF_RANGE |
| `12` | UNIMPLEMENTED |
| `13` | INTERNAL |
| `14` | UNAVAILABLE |
| `15` | DATA_LOSS |
| `16` | UNAUTHENTICATED |
<!-- endsemconv -->

[gRPC]: https://grpc.io/

## Events

In the lifetime of a gRPC stream, an event for each message sent/received on
client and server spans SHOULD be created. In case of
unary calls only one sent and one received message will be recorded for both
client and server spans.

The event name MUST be `"message"`.

<!-- semconv rpc.grpc.message -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `message.type` | string | Whether this is a received or sent message. | `SENT` | No |
| `message.id` | int | MUST be calculated as two different counters starting from `1` one for sent messages and one for received message. [1] |  | No |
| `message.compressed_size` | int | Compressed size of the message in bytes. |  | No |
| `message.uncompressed_size` | int | Uncompressed size of the message in bytes. |  | No |

**[1]:** This way we guarantee that the values will be consistent between different implementations.

`message.type` MUST be one of the following:

| Value  | Description |
|---|---|
| `SENT` | sent |
| `RECEIVED` | received |
<!-- endsemconv -->