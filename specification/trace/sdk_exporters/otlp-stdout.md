<!--- Hugo front matter used to generate the website version of this page:
linkTitle: OTLP Stdout
--->

# Span Exporter - OTLP Standard output

**Status**: [Development](../../document-status.md)

"OTLP Standard output" Span Exporter is a [Span
Exporter](../sdk.md#span-exporter) which outputs the spans to
stdout/console in OTLP JSON format.

The exporter SHOULD provide the same configuration options as the OTLP
Exporter, except for the all the network related options.

If a language provides a mechanism to automatically configure a
[Span processor](../sdk.md#span-processor) to pair with the associated
exporter (e.g., using the [`OTEL_TRACES_EXPORTER` environment
variable](../../configuration/sdk-environment-variables.md#exporter-selection)), by
default the standard output exporter SHOULD be paired with a [batching
processor](../sdk.md#batching-processor).
                                                  
When using programmatically, the exporter SHOULD provide a way to configure the
output stream, defaulting to `stdout`.
