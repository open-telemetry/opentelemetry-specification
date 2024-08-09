<!--- Hugo front matter used to generate the website version of this page:
linkTitle: OTLP Stdout
--->

# Span Exporter - OTLP Standard output

**Status**: [Development](../document-status.md)

"OTLP Standard output" Exporter is an OTLP exporter which outputs to
stdout/console in OTLP JSON format, as defined in the
[file exporter](../protocol/file-exporter.md).

The exporter MUST provide the same configuration options as the OTLP
Exporter, except for the all the network related options.

If a language provides a mechanism to automatically configure a
Span, Traces, or Metrics processor to pair with the associated
exporter (e.g., using the [`OTEL_TRACES_EXPORTER` environment
variable](../configuration/sdk-environment-variables.md#exporter-selection)), by
default the standard output exporter SHOULD be paired with a batching
processor.

## Programmatic configuration

| Requirement | Name                       | Description                                                                                            | Default |
|-------------|----------------------------|--------------------------------------------------------------------------------------------------------|---------|
| MUST        | output stream (or similar) | Configure output stream. This SHOULD include the possibility to configure the output stream to a file. | stdout  |
