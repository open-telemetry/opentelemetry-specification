<!--- Hugo front matter used to generate the website version of this page:
linkTitle: Stdout
--->

# Logs Exporter - Standard output

**Status**: [Stable](../../document-status.md)

"Standard output" LogRecord Exporter is a [LogRecord
Exporter](../sdk.md#logrecordexporter) which outputs the logs to
stdout/console.

[OpenTelemetry SDK](../../overview.md#sdk) authors MAY choose the best idiomatic
name for their language. For example, ConsoleExporter, StdoutExporter,
StreamExporter, etc.

If a language provides a mechanism to automatically configure a
[LogRecordProcessor](../sdk.md#logrecordprocessor) to pair with the associated
exporter (e.g., using the [`OTEL_LOGS_EXPORTER` environment
variable](../../configuration/sdk-environment-variables.md#exporter-selection)), by
default the standard output exporter SHOULD be paired with a [simple
processor](../sdk.md#simple-processor).
