<!--- Hugo front matter used to generate the website version of this page:
linkTitle: Stdout
--->

# Span Exporter - Standard output

**Status**: [Stable](../../document-status.md)

"Standard output" Span Exporter is a [Span
Exporter](../sdk.md#span-exporter) which outputs the spans to
stdout/console.

[OpenTelemetry SDK](../../overview.md#sdk) authors MAY choose the best idiomatic
name for their language. For example, ConsoleExporter, StdoutExporter,
StreamExporter, LoggingExporter etc.

If a language provides a mechanism to automatically configure a
[Span processor](../sdk.md#span-processor) to pair with the associated
exporter (e.g., using the [`OTEL_TRACES_EXPORTER` environment
variable](../../configuration/sdk-environment-variables.md#exporter-selection)), by
default the standard output exporter SHOULD be paired with a [simple
processor](../sdk.md#simple-processor).
