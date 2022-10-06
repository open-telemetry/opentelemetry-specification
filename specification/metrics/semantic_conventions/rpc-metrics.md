<!--- Hugo front matter used to generate the website version of this page:
linkTitle: RPC
--->

# General RPC conventions

**Status**: [Experimental](../../document-status.md)

The conventions described in this section are RPC specific. When RPC operations
occur, measurements about those operations are recorded to instruments. The
measurements are aggregated and exported as metrics, which provide insight into
those operations. By including RPC properties as attributes on measurements, the
metrics can be filtered for finer grain analysis.

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [Metric instruments](#metric-instruments)
  * [RPC Server](#rpc-server)
  * [RPC Client](#rpc-client)
- [Attributes](#attributes)
  * [Service name](#service-name)
- [gRPC conventions](#grpc-conventions)
  * [gRPC Attributes](#grpc-attributes)

<!-- tocstop -->

## Metric instruments

The following metric instruments MUST be used to describe RPC operations. They
MUST be of the specified type and units.

*Note: RPC server and client metrics are split to allow correlation across client/server boundaries, e.g. Lining up an RPC method latency to determine if the server is responsible for latency the client is seeing.*

### RPC Server

Below is a table of RPC server metric instruments.

| Name | Instrument Type ([*](README.md#instrument-types)) | Unit | Unit ([UCUM](README.md#instrument-units)) | Description | Status | Streaming |
|------|------------|------|-------------------------------------------|-------------|--------|-----------|
| `rpc.server.duration` | Histogram  | milliseconds | `ms` | measures duration of inbound RPC | Recommended | N/A.  While streaming RPCs may record this metric as start-of-batch to end-of-batch, it's hard to interpret in practice. |
| `rpc.server.request.size` | Histogram  | Bytes | `By` | measures size of RPC request messages (uncompressed) | Optional | Recorded per message in a streaming batch |
| `rpc.server.response.size` | Histogram  | Bytes | `By` | measures size of RPC response messages (uncompressed) | Optional | Recorded per response in a streaming batch |
| `rpc.server.requests_per_rpc` | Histogram  | count | `{count}` | measures the number of messages received per RPC.  Should be 1 for all non-streaming RPCs | Optional | Required |
| `rpc.server.responses_per_rpc` | Histogram  | count | `{count}` | measures the number of messages sent per RPC.  Should be 1 for all non-streaming RPCs | Optional | Required |

### RPC Client

Below is a table of RPC client metric instruments.  These apply to traditional
RPC usage, not streaming RPCs.

| Name | Instrument Type ([*](README.md#instrument-types)) | Unit | Unit ([UCUM](README.md#instrument-units)) | Description | Status | Streaming |
|------|------------|------|-------------------------------------------|-------------|--------|-----------|
| `rpc.client.duration` | Histogram | milliseconds | `ms` | measures duration of outbound RPC | Recommended | N/A.  While streaming RPCs may record this metric as start-of-batch to end-of-batch, it's hard to interpret in practice. |
| `rpc.client.request.size` | Histogram | Bytes | `By` | measures size of RPC request messages (uncompressed) | Optional | Recorded per message in a streaming batch |
| `rpc.client.response.size` | Histogram | Bytes | `By` | measures size of RPC response messages (uncompressed) | Optional | Recorded per message in a streaming batch |
| `rpc.client.requests_per_rpc` | Histogram | count | `{count}` | measures the number of messages received per RPC.  Should be 1 for all non-streaming RPCs | Optional | Required |
| `rpc.client.responses_per_rpc` | Histogram | count | `{count}` | measures the number of messages sent per RPC.  Should be 1 for all non-streaming RPCs | Optional | Required |

## Attributes

Below is a table of attributes that SHOULD be included on client and server RPC
measurements.

<!-- semconv rpc -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| [`rpc.system`](../../trace/semantic_conventions/rpc.md) | string | A string identifying the remoting system. See below for a list of well-known identifiers. | `grpc` | Required |
| [`rpc.service`](../../trace/semantic_conventions/rpc.md) | string | The full (logical) name of the service being called, including its package name, if applicable. [1] | `myservice.EchoService` | Recommended |
| [`rpc.method`](../../trace/semantic_conventions/rpc.md) | string | The name of the (logical) method being called, must be equal to the $method part in the span name. [2] | `exampleMethod` | Recommended |
| [`net.peer.name`](../../trace/semantic_conventions/span-general.md) | string | RPC server [host name](https://grpc.github.io/grpc/core/md_doc_naming.html). [3] | `example.com` | Required |
| [`net.peer.port`](../../trace/semantic_conventions/span-general.md) | int | Logical remote port number | `80`; `8080`; `443` | Conditionally Required: See below |
| [`net.sock.family`](../../trace/semantic_conventions/span-general.md) | string | Protocol [address family](https://man7.org/linux/man-pages/man7/address_families.7.html) which is used for communication. | `inet6`; `bluetooth` | Conditionally Required: If and only if `net.sock.peer.addr` is set. |
| [`net.sock.peer.addr`](../../trace/semantic_conventions/span-general.md) | string | Remote socket peer address: IPv4 or IPv6 for internet protocols, path for local communication, [etc](https://man7.org/linux/man-pages/man7/address_families.7.html). | `127.0.0.1`; `/tmp/mysql.sock` | See below |
| [`net.sock.peer.name`](../../trace/semantic_conventions/span-general.md) | string | Remote socket peer name. | `proxy.example.com` | Recommended: [4] |
| [`net.sock.peer.port`](../../trace/semantic_conventions/span-general.md) | int | Remote socket peer port. | `16456` | Recommended: [5] |
| [`net.transport`](../../trace/semantic_conventions/span-general.md) | string | Transport protocol used. See note below. | `ip_tcp` | Conditionally Required: See below |

**[1]:** This is the logical name of the service from the RPC interface perspective, which can be different from the name of any implementing class. The `code.namespace` attribute may be used to store the latter (despite the attribute name, it may include a class name; e.g., class with method actually executing the call on the server side, RPC client stub class on the client side).

**[2]:** This is the logical name of the method from the RPC interface perspective, which can be different from the name of any implementing method/function. The `code.function` attribute may be used to store the latter (e.g., method actually executing the call on the server side, RPC client stub method on the client side).

**[3]:** May contain server IP address, DNS name, or local socket name. When host component is an IP address, instrumentations SHOULD NOT do a reverse proxy lookup to obtain DNS name and SHOULD set `net.peer.name` to the IP address provided in the host component.

**[4]:** If different than `net.peer.name` and if `net.sock.peer.addr` is set.

**[5]:** If different than `net.peer.port` and if `net.sock.peer.addr` is set.

**Additional attribute requirements:** At least one of the following sets of attributes is required:

* [`net.sock.peer.addr`](../../trace/semantic_conventions/span-general.md)
* [`net.peer.name`](../../trace/semantic_conventions/span-general.md)

`rpc.system` has the following list of well-known values. If one of them applies, then the respective value MUST be used, otherwise a custom value MAY be used.

| Value  | Description |
|---|---|
| `grpc` | gRPC |
| `java_rmi` | Java RMI |
| `dotnet_wcf` | .NET WCF |
| `apache_dubbo` | Apache Dubbo |
<!-- endsemconv -->

To avoid high cardinality, implementations should prefer the most stable of `net.peer.name` or
`net.sock.peer.addr`, depending on expected deployment profile.  For many cloud applications, this is likely
`net.peer.name` as names can be recycled even across re-instantiation of a server with a different `ip`.

For client-side metrics `net.peer.port` is required if the connection is IP-based and the port is available (it describes the server port they are connecting to).
For server-side spans `net.peer.port` is optional (it describes the port the client is connecting from).
Furthermore, setting [net.transport][] is required for non-IP connection like named pipe bindings.

[net.transport]: ../../trace/semantic_conventions/span-general.md#network-transport-attributes

### Service name

On the server process receiving and handling the remote procedure call, the service name provided in `rpc.service` does not necessarily have to match the [`service.name`][] resource attribute.
One process can expose multiple RPC endpoints and thus have multiple RPC service names. From a deployment perspective, as expressed by the `service.*` resource attributes, it will be treated as one deployed service with one `service.name`.

[`service.name`]: ../../resource/semantic_conventions/README.md#service

## gRPC conventions

For remote procedure calls via [gRPC][], additional conventions are described in this section.

`rpc.system` MUST be set to `"grpc"`.

### gRPC Attributes

Below is a table of attributes that SHOULD be included on client and server RPC measurements when `rpc.system` is `"grpc"`.

<!-- semconv rpc.grpc -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| [`rpc.grpc.status_code`](../../trace/semantic_conventions/rpc.md) | int | The [numeric status code](https://github.com/grpc/grpc/blob/v1.33.2/doc/statuscodes.md) of the gRPC request. | `0` | Required |

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
