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
- [Connect RPC conventions](#connect-rpc-conventions)
  * [Connect RPC Attributes](#connect-rpc-attributes)

<!-- tocstop -->

> **Warning**
> Existing RPC instrumentations that are using
> [v1.20.0 of this document](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.20.0/specification/metrics/semantic_conventions/rpc-metrics.md)
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
| [`network.transport`](../../trace/semantic_conventions/span-general.md) | string | [OSI Transport Layer](https://osi-model.com/transport-layer/) or [Inter-process Communication method](https://en.wikipedia.org/wiki/Inter-process_communication). The value SHOULD be normalized to lowercase. | `tcp`; `udp` | Recommended |
| [`network.type`](../../trace/semantic_conventions/span-general.md) | string | [OSI Network Layer](https://osi-model.com/network-layer/) or non-OSI equivalent. The value SHOULD be normalized to lowercase. | `ipv4`; `ipv6` | Recommended |
| [`server.address`](../../trace/semantic_conventions/span-general.md) | string | RPC server [host name](https://grpc.github.io/grpc/core/md_doc_naming.html). [3] | `example.com` | Required |
| [`server.port`](../../trace/semantic_conventions/span-general.md) | int | Logical server port number | `80`; `8080`; `443` | Conditionally Required: See below |
| [`server.socket.address`](../../trace/semantic_conventions/span-general.md) | string | Physical server IP address or Unix socket address. | `10.5.3.2` | See below |
| [`server.socket.port`](../../trace/semantic_conventions/span-general.md) | int | Physical server port. | `16456` | Recommended: [4] |

**[1]:** This is the logical name of the service from the RPC interface perspective, which can be different from the name of any implementing class. The `code.namespace` attribute may be used to store the latter (despite the attribute name, it may include a class name; e.g., class with method actually executing the call on the server side, RPC client stub class on the client side).

**[2]:** This is the logical name of the method from the RPC interface perspective, which can be different from the name of any implementing method/function. The `code.function` attribute may be used to store the latter (e.g., method actually executing the call on the server side, RPC client stub method on the client side).

**[3]:** May contain server IP address, DNS name, or local socket name. When host component is an IP address, instrumentations SHOULD NOT do a reverse proxy lookup to obtain DNS name and SHOULD set `server.address` to the IP address provided in the host component.

**[4]:** If different than `server.port` and if `server.socket.address` is set.

**Additional attribute requirements:** At least one of the following sets of attributes is required:

* [`server.socket.address`](../../trace/semantic_conventions/span-general.md)
* [`server.address`](../../trace/semantic_conventions/span-general.md)

`rpc.system` has the following list of well-known values. If one of them applies, then the respective value MUST be used, otherwise a custom value MAY be used.

| Value  | Description |
|---|---|
| `grpc` | gRPC |
| `java_rmi` | Java RMI |
| `dotnet_wcf` | .NET WCF |
| `apache_dubbo` | Apache Dubbo |
| `connect_rpc` | Connect RPC |
<!-- endsemconv -->

To avoid high cardinality, implementations should prefer the most stable of `server.address` or
`server.socket.address`, depending on expected deployment profile.  For many cloud applications, this is likely
`server.address` as names can be recycled even across re-instantiation of a server with a different `ip`.

For client-side metrics `server.port` is required if the connection is IP-based and the port is available (it describes the server port they are connecting to).
For server-side spans `server.port` is optional (it describes the port the client is connecting from).

[network.transport]: ../../trace/semantic_conventions/span-general.md#network-attributes

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

## Connect RPC conventions

For remote procedure calls via [connect](http://connect.build), additional conventions are described in this section.

`rpc.system` MUST be set to `"connect_rpc"`.

### Connect RPC Attributes

Below is a table of attributes that SHOULD be included on client and server RPC measurements when `rpc.system` is `"connect_rpc"`.

<!-- semconv rpc.connect_rpc -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| [`rpc.connect_rpc.error_code`](../../trace/semantic_conventions/rpc.md) | string | The [error codes](https://connect.build/docs/protocol/#error-codes) of the Connect request. Error codes are always string values. | `cancelled` | Conditionally Required: [1] |

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
