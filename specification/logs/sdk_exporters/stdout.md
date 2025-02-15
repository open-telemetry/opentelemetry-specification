<!--- Hugo front matter used to generate the website version of this page:
linkTitle: Stdout
--->

# Logs Exporter - Standard output

**Status**: [Stable](../../document-status.md)

"Standard output" LogRecord Exporter is a [LogRecord
Exporter](../sdk.md#logrecordexporter) which outputs the logs to stdout/console.

The exporter's output format is unspecified and can vary between
implementations. Documentation SHOULD warn users about this. The following
wording is recommended (modify as needed):

> This exporter is intended for debugging and learning purposes. It is not
> recommended for production use. The output format is not standardized and can
> change at any time.
>
> If a standardized format for exporting logs to stdout is desired, consider
> using the [File Exporter](../../protocol/file-exporter.md), if available.
> However, please note that the File Exporter specification is experimental.

[OpenTelemetry SDK](../../overview.md#sdk) authors MAY choose the best idiomatic
name for their language. For example, ConsoleExporter, StdoutExporter,
StreamExporter, etc.

If a language provides a mechanism to automatically configure a
[LogRecordProcessor](../sdk.md#logrecordprocessor) to pair with the associated
exporter (e.g., using the [`OTEL_LOGS_EXPORTER` environment
variable](../../configuration/sdk-environment-variables.md#exporter-selection)), by
default the standard output exporter SHOULD be paired with a [simple
processor](../sdk.md#simple-processor).
