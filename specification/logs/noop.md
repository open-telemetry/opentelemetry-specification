<!--- Hugo front matter used to generate the website version of this page:
linkTitle: noop
--->

# Logs Bridge API No-Op Implementation

**Status**: [Experimental](../document-status.md)

<details>
<summary> Table of Contents </summary>

<!-- toc -->

- [LoggerProvider](#loggerprovider)
  * [Logger Creation](#logger-creation)
- [Logger](#logger)
  * [Emit LogRecord](#emit-logrecord)

<!-- tocstop -->

</details>

Users of OpenTelemetry need a way to disable the API from actually
performing any operations. The No-Op OpenTelemetry API implementation
(henceforth referred to as the No-Op) provides users with this
functionally. It implements the [OpenTelemetry Logs Bridge API](./bridge-api.md)
so that no telemetry is produced and computation resources are minimized.

All language implementations of OpenTelemetry MUST provide a No-Op.

The [Logs Bridge API](./bridge-api.md) defines classes with various operations.
All No-Op classes MUST NOT hold configuration or operational state. All No-op
operations MUST accept all defined parameters, MUST NOT validate any arguments
received, and MUST NOT return any non-empty error or log any message.

## LoggerProvider

The No-Op MUST allow the creation of multiple `LoggerProviders`s.

Since all `LoggerProviders`s hold the same empty state, a No-Op MAY
provide the same `LoggerProvider` instances to all creation requests.

### Logger Creation

New `Logger` instances are always created with a [LoggerProvider](./bridge-api.md#loggerprovider).
Therefore, `LoggerProvider` MUST allow for the creation of `Logger`s.
All `Logger`s created MUST be an instance of the [No-Op Logger](#logger).

Since all `Logger`s will hold the same empty state, a `LoggerProvider` MAY
return the same `Logger` instances to all creation requests.

## Logger

### Emit LogRecord

The No-Op `Logger` MUST allow
for [emitting LogRecords](./bridge-api.md#emit-a-logrecord).
