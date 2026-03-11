# Pprof

**Status**: [Development](../document-status.md)

<!-- toc -->

- [Compatibility](#compatibility)

<!-- tocstop -->

## Compatibility

Original [pprof](https://github.com/google/pprof/tree/main/proto) is compatible
with OpenTelemetry Profiles in that it can be transformed into OpenTelemetry Profiles
and back again into [pprof](https://github.com/google/pprof/tree/main/proto) without
data loss (convertibility but not wire compatibility).

To enable this compatibility through explicit conversion, OpenTelemetry provides a `pprof` [namespace](https://opentelemetry.io/docs/specs/semconv/general/profiles/#compatibility-with-pprof)
in [Semantic Conventions](https://opentelemetry.io/docs/specs/semconv).

