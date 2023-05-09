# Semantic conventions for RPC spans

**NOTICE** Semantic Conventions are moving to a
[new location](http://github.com/open-telemetry/semantic-conventions).

No changes to this document are allowed.

**Status**: [Experimental](../../document-status.md)

This document defines how to describe remote procedure calls
(also called "remote method invocations" / "RMI") with spans.

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [Common remote procedure call conventions](#common-remote-procedure-call-conventions)
  * [Span name](#span-name)
  * [Common attributes](#common-attributes)
    + [Service name](#service-name)
  * [Client attributes](#client-attributes)
  * [Server attributes](#server-attributes)
  * [Events](#events)
  * [Distinction from HTTP spans](#distinction-from-http-spans)
- [gRPC](#grpc)
  * [gRPC Attributes](#grpc-attributes)
  * [gRPC Status](#grpc-status)
  * [gRPC Request and Response Metadata](#grpc-request-and-response-metadata)
- [Connect RPC conventions](#connect-rpc-conventions)
  * [Connect RPC Attributes](#connect-rpc-attributes)
  * [Connect RPC Status](#connect-rpc-status)
  * [Connect RPC Request and Response Metadata](#connect-rpc-request-and-response-metadata)
- [JSON RPC](#json-rpc)
  * [JSON RPC Attributes](#json-rpc-attributes)

<!-- tocstop -->

> **Warning**
> Existing RPC instrumentations that are using
> [v1.20.0 of this document](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.20.0/specification/trace/semantic_conventions/rpc.md)
> (or prior):
>
> * SHOULD NOT change the version of the networking attributes that they emit
>   until the HTTP semantic conventions are marked stable (HTTP stabilization will
>   include stabilization of a core set of networking attributes which are also used
>   in RPC instrumentations).
> * SHOULD introduce an environment variable `OTEL_SEMCONV_STABILITY_OPT_IN`
>   in the existing major version which supports the following values:
>   * `none` - continue emitting whatever version of the old experimental
>     networking attributes the instrumentation was emitting previously.
>     This is the default value.
>   * `http` - emit the new, stable networking attributes,
>     and stop emitting the old experimental networking attributes
>     that the instrumentation emitted previously.
>   * `http/dup` - emit both the old and the stable networking attributes,
>     allowing for a seamless transition.
> * SHOULD maintain (security patching at a minimum) the existing major version
>   for at least six months after it starts emitting both sets of attributes.
> * SHOULD drop the environment variable in the next major version (stable
>   next major version SHOULD NOT be released prior to October 1, 2023).

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

### Common attributes

<!-- semconv rpc -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `rpc.system` | string | A string identifying the remoting system. See below for a list of well-known identifiers. | `grpc` | Required |
| `rpc.service` | string | The full (logical) name of the service being called, including its package name, if applicable. [1] | `myservice.EchoService` | Recommended |
| `rpc.method` | string | The name of the (logical) method being called, must be equal to the $method part in the span name. [2] | `exampleMethod` | Recommended |
| [`network.transport`](span-general.md) | string | [OSI Transport Layer](https://osi-model.com/transport-layer/) or [Inter-process Communication method](https://en.wikipedia.org/wiki/Inter-process_communication). The value SHOULD be normalized to lowercase. | `tcp`; `udp` | Recommended |
| [`network.type`](span-general.md) | string | [OSI Network Layer](https://osi-model.com/network-layer/) or non-OSI equivalent. The value SHOULD be normalized to lowercase. | `ipv4`; `ipv6` | Recommended |
| [`server.address`](span-general.md) | string | RPC server [host name](https://grpc.github.io/grpc/core/md_doc_naming.html). [3] | `example.com` | Required |
| [`server.port`](span-general.md) | int | Logical server port number | `80`; `8080`; `443` | Conditionally Required: See below |
| [`server.socket.address`](span-general.md) | string | Physical server IP address or Unix socket address. | `10.5.3.2` | See below |
| [`server.socket.port`](span-general.md) | int | Physical server port. | `16456` | Recommended: [4] |

**[1]:** This is the logical name of the service from the RPC interface perspective, which can be different from the name of any implementing class. The `code.namespace` attribute may be used to store the latter (despite the attribute name, it may include a class name; e.g., class with method actually executing the call on the server side, RPC client stub class on the client side).

**[2]:** This is the logical name of the method from the RPC interface perspective, which can be different from the name of any implementing method/function. The `code.function` attribute may be used to store the latter (e.g., method actually executing the call on the server side, RPC client stub method on the client side).

**[3]:** May contain server IP address, DNS name, or local socket name. When host component is an IP address, instrumentations SHOULD NOT do a reverse proxy lookup to obtain DNS name and SHOULD set `server.address` to the IP address provided in the host component.

**[4]:** If different than `server.port` and if `server.socket.address` is set.

**Additional attribute requirements:** At least one of the following sets of attributes is required:

* [`server.socket.address`](span-general.md)
* [`server.address`](span-general.md)

`rpc.system` has the following list of well-known values. If one of them applies, then the respective value MUST be used, otherwise a custom value MAY be used.

| Value  | Description |
|---|---|
| `grpc` | gRPC |
| `java_rmi` | Java RMI |
| `dotnet_wcf` | .NET WCF |
| `apache_dubbo` | Apache Dubbo |
| `connect_rpc` | Connect RPC |
<!-- endsemconv -->

For client-side spans `server.port` is required if the connection is IP-based and the port is available (it describes the server port they are connecting to).
For server-side spans `client.socket.port` is optional (it describes the port the client is connecting from).

#### Service name

On the server process receiving and handling the remote procedure call, the service name provided in `rpc.service` does not necessarily have to match the [`service.name`][] resource attribute.
One process can expose multiple RPC endpoints and thus have multiple RPC service names. From a deployment perspective, as expressed by the `service.*` resource attributes, it will be treated as one deployed service with one `service.name`.
Likewise, on clients sending RPC requests to a server, the service name provided in `rpc.service` does not have to match the [`peer.service`][] span attribute.

As an example, given a process deployed as `QuoteService`, this would be the name that goes into the `service.name` resource attribute which applies to the entire process.
This process could expose two RPC endpoints, one called `CurrencyQuotes` (= `rpc.service`) with a method called `getMeanRate` (= `rpc.method`) and the other endpoint called `StockQuotes`  (= `rpc.service`) with two methods `getCurrentBid` and `getLastClose` (= `rpc.method`).
In this example, spans representing client request should have their `peer.service` attribute set to `QuoteService` as well to match the server's `service.name` resource attribute.
Generally, a user SHOULD NOT set `peer.service` to a fully qualified RPC service name.

[network attributes]: span-general.md#server-and-client-attributes
[`service.name`]: ../../resource/semantic_conventions/README.md#service
[`peer.service`]: span-general.md#general-remote-service-attributes

### Client attributes

<!-- semconv rpc.client -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| [`server.socket.domain`](span-general.md) | string | The domain name of an immediate peer. [1] | `proxy.example.com` | Recommended: [2] |

**[1]:** Typically observed from the client side, and represents a proxy or other intermediary domain name.

**[2]:** If different than `server.address` and if `server.socket.address` is set.
<!-- endsemconv -->

### Server attributes

<!-- semconv rpc.server -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| [`client.address`](span-general.md) | string | Client address - unix domain socket name, IPv4 or IPv6 address. [1] | `/tmp/my.sock`; `10.1.2.80` | Recommended |
| [`client.port`](span-general.md) | int | Client port number [2] | `65123` | Recommended |
| [`client.socket.address`](span-general.md) | string | Immediate client peer address - unix domain socket name, IPv4 or IPv6 address. | `/tmp/my.sock`; `127.0.0.1` | Recommended: If different than `client.address`. |
| [`client.socket.port`](span-general.md) | int | Immediate client peer port number | `35555` | Recommended: If different than `client.port`. |
| [`network.transport`](span-general.md) | string | [OSI Transport Layer](https://osi-model.com/transport-layer/) or [Inter-process Communication method](https://en.wikipedia.org/wiki/Inter-process_communication). The value SHOULD be normalized to lowercase. | `tcp`; `udp` | Recommended |
| [`network.type`](span-general.md) | string | [OSI Network Layer](https://osi-model.com/network-layer/) or non-OSI equivalent. The value SHOULD be normalized to lowercase. | `ipv4`; `ipv6` | Recommended |

**[1]:** When observed from the server side, and when communicating through an intermediary, `client.address` SHOULD represent client address behind any intermediaries (e.g. proxies) if it's available.

**[2]:** When observed from the server side, and when communicating through an intermediary, `client.port` SHOULD represent client port behind any intermediaries (e.g. proxies) if it's available.
<!-- endsemconv -->

### Events

In the lifetime of an RPC stream, an event for each message sent/received on
client and server spans SHOULD be created. In case of unary calls only one sent
and one received message will be recorded for both client and server spans.

<!-- semconv rpc.message -->
The event name MUST be `message`.

| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `message.type` | string | Whether this is a received or sent message. | `SENT` | Recommended |
| `message.id` | int | MUST be calculated as two different counters starting from `1` one for sent messages and one for received message. [1] |  | Recommended |
| `message.compressed_size` | int | Compressed size of the message in bytes. |  | Recommended |
| `message.uncompressed_size` | int | Uncompressed size of the message in bytes. |  | Recommended |

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
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `rpc.grpc.status_code` | int | The [numeric status code](https://github.com/grpc/grpc/blob/v1.33.2/doc/statuscodes.md) of the gRPC request. | `0` | Required |

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

The table below describes when
the [Span Status](../api.md#set-status) MUST be set
to `Error` or remain unset
depending on the [gRPC status code](https://github.com/grpc/grpc/blob/v1.33.2/doc/statuscodes.md)
and [Span Kind](../api.md#spankind).

| gRPC Status Code | `SpanKind.SERVER` Span Status | `SpanKind.CLIENT` Span Status |
|---|---|---|
| OK | unset | unset |
| CANCELLED | unset | `Error` |
| UNKNOWN | `Error` | `Error`  |
| INVALID_ARGUMENT | unset | `Error` |
| DEADLINE_EXCEEDED | `Error` | `Error` |
| NOT_FOUND | unset | `Error` |
| ALREADY_EXISTS | unset | `Error` |
| PERMISSION_DENIED | unset | `Error` |
| RESOURCE_EXHAUSTED | unset| `Error` |
| FAILED_PRECONDITION | unset | `Error` |
| ABORTED | unset | `Error` |
| OUT_OF_RANGE | unset | `Error` |
| UNIMPLEMENTED | `Error` | `Error` |
| INTERNAL | `Error` | `Error` |
| UNAVAILABLE | `Error` | `Error` |
| DATA_LOSS | `Error` | `Error` |
| UNAUTHENTICATED | unset | `Error` |

### gRPC Request and Response Metadata

| Attribute                     | Type     | Description                                                                                                                                                       | Examples                                                                   | Requirement Level |
|-------------------------------|----------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------|-------------------|
| `rpc.grpc.request.metadata.<key>`  | string[] | gRPC request metadata, `<key>` being the normalized gRPC Metadata key (lowercase, with `-` characters replaced by `_`), the value being the metadata values. [1]  | `rpc.grpc.request.metadata.my_custom_metadata_attribute=["1.2.3.4", "1.2.3.5"]` | Opt-In            |
| `rpc.grpc.response.metadata.<key>` | string[] | gRPC response metadata, `<key>` being the normalized gRPC Metadata key (lowercase, with `-` characters replaced by `_`), the value being the metadata values. [1] | `rpc.grpc.response.metadata.my_custom_metadata_attribute=["attribute_value"]`   | Opt-In            |

**[1]:** Instrumentations SHOULD require an explicit configuration of which metadata values are to be captured.
Including all request/response metadata values can be a security risk - explicit configuration helps avoid leaking sensitive information.

## Connect RPC conventions

For remote procedure calls via [connect](http://connect.build), additional conventions are described in this section.

`rpc.system` MUST be set to `"connect_rpc"`.

### Connect RPC Attributes

Below is a table of attributes that SHOULD be included on client and server RPC measurements when `rpc.system` is `"connect_rpc"`.

<!-- semconv rpc.connect_rpc -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `rpc.connect_rpc.error_code` | string | The [error codes](https://connect.build/docs/protocol/#error-codes) of the Connect request. Error codes are always string values. | `cancelled` | Conditionally Required: [1] |

**[1]:** If response is not successful and if error code available.

`rpc.connect_rpc.error_code` MUST be one of the following:

| Value  | Description |
|---|---|
| `cancelled` | cancelled |
| `unknown` | unknown |
| `invalid_argument` | invalid_argument |
| `deadline_exceeded` | deadline_exceeded |
| `not_found` | not_found |
| `already_exists` | already_exists |
| `permission_denied` | permission_denied |
| `resource_exhausted` | resource_exhausted |
| `failed_precondition` | failed_precondition |
| `aborted` | aborted |
| `out_of_range` | out_of_range |
| `unimplemented` | unimplemented |
| `internal` | internal |
| `unavailable` | unavailable |
| `data_loss` | data_loss |
| `unauthenticated` | unauthenticated |
<!-- endsemconv -->

### Connect RPC Status

If `rpc.connect_rpc.error_code` is set, [Span Status](../api.md#set-status) MUST be set to `Error` and left unset in all other cases.

### Connect RPC Request and Response Metadata

| Attribute                                 | Type     | Description                                                                                                                                                             | Examples                                                                   | Requirement Level |
|-------------------------------------------|----------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------|-------------------|
| `rpc.connect_rpc.request.metadata.<key>`  | string[] | Connect request metadata, `<key>` being the normalized Connect Metadata key (lowercase, with `-` characters replaced by `_`), the value being the metadata values. [1]  | `rpc.request.metadata.my_custom_metadata_attribute=["1.2.3.4", "1.2.3.5"]` | Optional          |
| `rpc.connect_rpc.response.metadata.<key>` | string[] | Connect response metadata, `<key>` being the normalized Connect Metadata key (lowercase, with `-` characters replaced by `_`), the value being the metadata values. [1] | `rpc.response.metadata.my_custom_metadata_attribute=["attribute_value"]`   | Optional          |

**[1]:** Instrumentations SHOULD require an explicit configuration of which metadata values are to be captured.
Including all request/response metadata values can be a security risk - explicit configuration helps avoid leaking sensitive information.

## JSON RPC

Conventions specific to [JSON RPC](https://www.jsonrpc.org/).

`rpc.system` MUST be set to `"jsonrpc"`.

### JSON RPC Attributes

<!-- semconv rpc.jsonrpc -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `rpc.jsonrpc.version` | string | Protocol version as in `jsonrpc` property of request/response. Since JSON-RPC 1.0 does not specify this, the value can be omitted. | `2.0`; `1.0` | Conditionally Required: If other than the default version (`1.0`) |
| `rpc.jsonrpc.request_id` | string | `id` property of request or response. Since protocol allows id to be int, string, `null` or missing (for notifications), value is expected to be cast to string for simplicity. Use empty string in case of `null` value. Omit entirely if this is a notification. | `10`; `request-7`; `` | Recommended |
| `rpc.jsonrpc.error_code` | int | `error.code` property of response if it is an error response. | `-32700`; `100` | Conditionally Required: If response is not successful. |
| `rpc.jsonrpc.error_message` | string | `error.message` property of response if it is an error response. | `Parse error`; `User already exists` | Recommended |
| `rpc.method` | string | The name of the (logical) method being called, must be equal to the $method part in the span name. [1] | `exampleMethod` | Required |

**[1]:** This is always required for jsonrpc. See the note in the general RPC conventions for more information.
<!-- endsemconv -->
