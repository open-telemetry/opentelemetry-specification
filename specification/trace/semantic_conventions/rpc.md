# Semantic conventions for RPC spans

**Status**: [Experimental](../../document-status.md)

This document defines how to describe remote procedure calls
(also called "remote method invocations" / "RMI") with spans.

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [Common remote procedure call conventions](#common-remote-procedure-call-conventions)
  * [Span name](#span-name)
  * [Attributes](#attributes)
    + [Service name](#service-name)
  * [Events](#events)
  * [Distinction from HTTP spans](#distinction-from-http-spans)
- [gRPC](#grpc)
  * [gRPC Attributes](#grpc-attributes)
  * [gRPC Status](#grpc-status)
- [JSON RPC](#json-rpc)
  * [JSON RPC Attributes](#json-rpc-attributes)

<!-- tocstop -->

## Common remote procedure call conventions

A remote procedure calls is described by two separate spans, one on the client-side and one on the server-side.

For outgoing requests, the `SpanKind` MUST be set to `CLIENT` and for incoming requests to `SERVER`.

Remote procedure calls can only be represented with these semantic conventions, when the names of the called service and method are known and available.

### Span name

The _span name_ MUST be the full RPC method name formatted as:

```
$package.$service/$method
```

(where $service MUST NOT contain dots and $method MUST NOT contain slashes)

If there is no package name or if it is unknown, the `$package.` part (including the period) is omitted.

Examples of span names:

- `grpc.test.EchoService/Echo`
- `com.example.ExampleRmiService/exampleMethod`
- `MyCalcService.Calculator/Add` reported by the server and
  `MyServiceReference.ICalculator/Add` reported by the client for .NET WCF calls
- `MyServiceWithNoPackage/theMethod`

### Attributes

<!-- semconv rpc -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `rpc.system` | string | A string identifying the remoting system. See below for a list of well-known identifiers. | `grpc` | Yes |
| `rpc.service` | string | The full (logical) name of the service being called, including its package name, if applicable. [1] | `myservice.EchoService` | No, but recommended |
| `rpc.method` | string | The name of the (logical) method being called, must be equal to the $method part in the span name. [2] | `exampleMethod` | No, but recommended |
| [`net.peer.ip`](span-general.md) | string | Remote address of the peer (dotted decimal for IPv4 or [RFC5952](https://tools.ietf.org/html/rfc5952) for IPv6) | `127.0.0.1` | See below |
| [`net.peer.name`](span-general.md) | string | Remote hostname or similar, see note below. | `example.com` | See below |
| [`net.peer.port`](span-general.md) | int | Remote port number. | `80`; `8080`; `443` | See below |
| [`net.transport`](span-general.md) | string | Transport protocol used. See note below. | `ip_tcp` | See below |

**[1]:** This is the logical name of the service from the RPC interface perspective, which can be different from the name of any implementing class. The `code.namespace` attribute may be used to store the latter (despite the attribute name, it may include a class name; e.g., class with method actually executing the call on the server side, RPC client stub class on the client side).

**[2]:** This is the logical name of the method from the RPC interface perspective, which can be different from the name of any implementing method/function. The `code.function` attribute may be used to store the latter (e.g., method actually executing the call on the server side, RPC client stub method on the client side).

**Additional attribute requirements:** At least one of the following sets of attributes is required:

* [`net.peer.ip`](span-general.md)
* [`net.peer.name`](span-general.md)

`rpc.system` has the following list of well-known values. If one of them applies, then the respective value MUST be used, otherwise a custom value MAY be used.

| Value  | Description |
|---|---|
| `grpc` | gRPC |
| `java_rmi` | Java RMI |
| `dotnet_wcf` | .NET WCF |
| `apache_dubbo` | Apache Dubbo |
<!-- endsemconv -->

For client-side spans `net.peer.port` is required if the connection is IP-based and the port is available (it describes the server port they are connecting to).
For server-side spans `net.peer.port` is optional (it describes the port the client is connecting from).
Furthermore, setting [net.transport][] is required for non-IP connection like named pipe bindings.

#### Service name

On the server process receiving and handling the remote procedure call, the service name provided in `rpc.service` does not necessarily have to match the [`service.name`][] resource attribute.
One process can expose multiple RPC endpoints and thus have multiple RPC service names. From a deployment perspective, as expressed by the `service.*` resource attributes, it will be treated as one deployed service with one `service.name`.
Likewise, on clients sending RPC requests to a server, the service name provided in `rpc.service` does not have to match the [`peer.service`][] span attribute.

As an example, given a process deployed as `QuoteService`, this would be the name that goes into the `service.name` resource attribute which applies to the entire process.
This process could expose two RPC endpoints, one called `CurrencyQuotes` (= `rpc.service`) with a method called `getMeanRate` (= `rpc.method`) and the other endpoint called `StockQuotes`  (= `rpc.service`) with two methods `getCurrentBid` and `getLastClose` (= `rpc.method`).
In this example, spans representing client request should have their `peer.service` attribute set to `QuoteService` as well to match the server's `service.name` resource attribute.
Generally, a user SHOULD NOT set `peer.service` to a fully qualified RPC service name.

[network attributes]: span-general.md#general-network-connection-attributes
[net.transport]: span-general.md#network-transport-attributes
[`service.name`]: ../../resource/semantic_conventions/README.md#service
[`peer.service`]: span-general.md#general-remote-service-attributes

### Events

In the lifetime of an RPC stream, an event for each message sent/received on
client and server spans SHOULD be created. In case of unary calls only one sent
and one received message will be recorded for both client and server spans.

<!-- semconv rpc.message -->
The event name MUST be `message`.

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

### Distinction from HTTP spans

HTTP calls can generally be represented using just [HTTP spans](./http.md).
If they address a particular remote service and method known to the caller, i.e., when it is a remote procedure call transported over HTTP, the `rpc.*` attributes might be added additionally on that span, or in a separate RPC span that is a parent of the transporting HTTP call.
Note that _method_ in this context is about the called remote procedure and _not_ the HTTP verb (GET, POST, etc.).

## gRPC

For remote procedure calls via [gRPC][], additional conventions are described in this section.

`rpc.system` MUST be set to `"grpc"`.

### gRPC Attributes

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

### gRPC Status

The [Span Status](../api.md#set-status) MUST be left unset for an `OK` gRPC status code, and set to `Error` for all others.

## JSON RPC

Conventions specific to [JSON RPC](https://www.jsonrpc.org/).

`rpc.system` MUST be set to `"jsonrpc"`.

### JSON RPC Attributes

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
