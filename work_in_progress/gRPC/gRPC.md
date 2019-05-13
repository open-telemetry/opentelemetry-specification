# gRPC

This document explains tracing of gRPC requests with OpenConsensus.

## Spans

Implementations MUST create a span, when the gRPC call starts, for the client
and a span for the server.

Span `name` MUST be full gRPC method name formatted as:

```
$package.$service/$method
```

Examples of span names:

- `grpc.test.EchoService/Echo`

Outgoing requests should be a span `kind` of `CLIENT` and incoming requests
should be a span `kind` of `SERVER`.

## Propagation

Propagation is how `SpanContext` is transmitted on the wire in an gRPC request.

**TODO: review and close on binary protocol and metadata name**

The propagation MUST inject a `SpanContext` as a gRPC metadata `grpc-trace-bin`
and MUST extract a `SpanContext` from the gRPC metadata. Serialization format is
configurable. The default serialization format should be used is [W3C binary
trace context](https://w3c.github.io/trace-context-binary/).

## Attributes


**TODO: `type` is not implemented today in existing integrations. Need to track it**
**TODO: should we include `host`, `uri` or those should be reported as `peer`?**
**TODO: agree that `component` from OpenTracing is being replaced with `type` as
a better name.**

| Attribute name            | Description                    | Type   |Example value              |
|---------------------------|--------------------------------|--------|---------------------------|
| "type"                    | Type of the client/server span | string | `grpc`                    |

## Status

Implementations MUST set status which should be the same as the gRPC
client/server status. The mapping between gRPC canonical codes and OpenCensus
status codes can be found
[here](https://github.com/grpc/grpc-go/blob/master/codes/codes.go).

## Events

In the lifetime of a gRPC stream, the following events SHOULD be created:

- An event for each message sent/received on client and server spans.

[Message
event](../../contrib/src/main/java/opentelemetry/contrib/trace/MessageEvent.java)
should be used as a name of event.

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
