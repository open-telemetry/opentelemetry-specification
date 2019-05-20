# gRPC Trace

This document explains tracing of gRPC requests with OpenCensus.

## Spans

Implementations MUST create a span, when the gRPC call starts, for the client and a span for the 
server.

Span name is formatted as (also known as full gRPC method name):

* $package.$service/$method

Examples of span names:

* grpc.test.EchoService/Echo

Outgoing requests should be a span kind of CLIENT and
incoming requests should be a span kind of SERVER.

For backends that does not support Span.Kind, the exported span names can be prefixed with `Sent.`
(for CLIENT kind) and `Recv.` (for SERVER kind).

## Propagation

Propagation is how SpanContext is transmitted on the wire in an gRPC request.

The propagation MUST inject a SpanContext (as a gRPC metadata `grpc-trace-bin`) and MUST extract 
a SpanContext from the gRPC metadata. The serialization format is defined
[here](../encodings/BinaryEncoding.md).

## Status

Implementations MUST set status which should be the same as the gRPC client/server status. The 
mapping between gRPC canonical codes and OpenCensus status codes can be found
[here](https://github.com/grpc/grpc-go/blob/master/codes/codes.go).

## Message events

In the lifetime of a gRPC stream, the following message events SHOULD be created:

* A message event for each message sent/received on client and server spans.

```
-> [time], MessageEventTypeSent, MessageId, UncompressedByteSize, CompressedByteSize
```

```
-> [time], MessageEventTypeRecv, MessageId, UncompressedByteSize, CompressedByteSize
```

The `MessageId` must be calculated as two different counters starting from `1` one for sent 
messages and one for received message. This way we guarantee that the values will be consistent 
between different implementations. In case of unary calls only one sent and one received message 
will be recorded for both client and server spans.