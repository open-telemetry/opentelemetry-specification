# Semantic Conventions for Log Media

**Status**: [Experimental](../../document-status.md)

This document describes attributes for log media in OpenTelemetry. Log media are mechanisms by which logs are transmitted. Types of media include files, streams, network protocols, and os-specific logging services such as journald and Windows Event Log.

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [Log Media](#log-media)
  * [Log File](#log-file)
  * [I/O Stream](#io-stream)

<!-- tocstop -->

</details>

## Log Media

**Note:** The OpenTelemetry specification defines a [Resource](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/resource/sdk.md#resource-sdk) as `an immutable representation of the entity producing telemetry`.
The following attributes do not describe entities that produce telemetry. Rather, they describe mechanisms of log transmission.
As such, these should be recorded as Log Record attributes when applicable. They should not be recorded as Resource attributes.

### Log File

**Description:** A file to which log was emitted.

| Name                            | Notes and examples                                                                       |
| ------------------------------- | ---------------------------------------------------------------------------------------- |
| `log.file.name`          | The basename of the file. Example: `audit.log`                                           |
| `log.file.path`          | The full path to the file. Example: `/var/log/mysql/audit.log`                           |
| `log.file.name_resolved` | The basename of the file, with symlinks resolved. Example: `uuid.log`                    |
| `log.file.path_resolved` | The full path to the file, with symlinks resolved. Example: `/var/lib/docker/uuid.log`   |

### I/O Stream

**Description:** The I/O stream to which the log was emitted.

| Name                            | Notes and examples                                                                       |
| ------------------------------- | ---------------------------------------------------------------------------------------- |
| `log.iostream`        | The stream associated with the log. SHOULD be one of: `stdout`, `stderr` |
