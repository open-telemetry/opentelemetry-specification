# Semantic conventions for RPC spans

This document defines how to describe remote procedure calls
(also called "remote method invocations" / "RMI") with spans.

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [gRPC](#grpc)
  * [Attributes](#attributes)
  * [Status](#status)
  * [Events](#events)

<!-- tocstop -->

## gRPC

Implementations MUST create a span, when the gRPC call starts, one for
client-side and one for server-side. Outgoing requests should be a span `kind`
of `CLIENT` and incoming requests should be a span `kind` of `SERVER`.

Span `name` MUST be full gRPC method name formatted as:

```
$package.$service/$method
```

Examples of span name: `grpc.test.EchoService/Echo`.

### Attributes

| Attribute name | Notes and examples                                           | Required? |
| -------------- | ------------------------------------------------------------ | --------- |
| `component`    | Declares that this is a grpc component. Value MUST be `"grpc"`. | Yes       |
| `rpc.service`  | The service name, must be equal to the $service part in the span name. | Yes |
| `net.peer.ip`  | See [network attributes][]. | See below |
| `net.peer.name`  | See [network attributes][]. | See below |
| `net.peer.port`  | See [network attributes][]. | See below |

At least one of [network attributes][] `net.peer.name` or `net.peer.ip` is required.
For client-side spans `net.peer.port` is required (it describes the server port they are connecting to).
For server-side spans `net.peer.port` is optional (it describes the port the client is connecting from).

[network attributes]: data-span-general.md#general-network-connection-attributes

### Status

Implementations MUST set status which MUST be the same as the gRPC client/server
status. The mapping between gRPC canonical codes and OpenTelemetry status codes
is 1:1 as OpenTelemetry canonical codes is just a snapshot of grpc codes which
can be found [here](https://github.com/grpc/grpc-go/blob/master/codes/codes.go).

### Events

In the lifetime of a gRPC stream, an event for each message sent/received on
client and server spans SHOULD be created with the following attributes:

```
-> [time],
    "name" = "message",
    "message.type" = "SENT",
    "message.id" = id
    "message.compressed_size" = <compressed size in bytes>,
    "message.uncompressed_size" = <uncompressed size in bytes>
```

```
-> [time],
    "name" = "message",
    "message.type" = "RECEIVED",
    "message.id" = id
    "message.compressed_size" = <compressed size in bytes>,
    "message.uncompressed_size" = <uncompressed size in bytes>
```

The `message.id` MUST be calculated as two different counters starting from `1`
one for sent messages and one for received message. This way we guarantee that
the values will be consistent between different implementations. In case of
unary calls only one sent and one received message will be recorded for both
client and server spans.
