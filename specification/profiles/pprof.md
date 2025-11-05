# Pprof

**Status**: [Development](../document-status.md)

<!-- toc -->

- [Compatibility](#compatibility)

<!-- tocstop -->

## Compatibility

Original [pprof](https://github.com/google/pprof/tree/main/proto) is forward
compatible with OpenTelemetry Profiles in a sense that it can be transformed into
OpenTelemetry Profiles and again into [pprof](https://github.com/google/pprof/tree/main/proto)
without data loss.

For this compatibility OpenTelemetry also provides a `pprof` namespace in
Semantic Conventions.
