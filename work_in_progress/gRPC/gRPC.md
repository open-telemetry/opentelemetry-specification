# gRPC

## Propagation

Propagation is how `SpanContext` is transmitted on the wire in an gRPC request.

**TODO: review and close on binary protocol and metadata name**

The propagation MUST inject a `SpanContext` as a gRPC metadata `grpc-trace-bin`
and MUST extract a `SpanContext` from the gRPC metadata. Serialization format is
configurable. The default serialization format should be used is [W3C binary
trace context](https://w3c.github.io/trace-context-binary/).
