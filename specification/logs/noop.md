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

## LoggerProvider

The No-Op MUST allow the creation of multiple `LoggerProviders`s.

The `LoggerProviders`s created by the No-Op needs to hold as small a memory
footprint as possible. Therefore, all `LoggerProviders`s created MUST NOT
hold configuration or operational state.

Since all `LoggerProviders`s hold the same empty state, a No-Op MAY
provide the same `LoggerProvider` instances to all creation requests.

The No-Op is used by OpenTelemetry users to disable OpenTelemetry
computation overhead and eliminate OpenTelemetry related output. For
this reason, the `LoggerProvider` MUST NOT return a non-empty error or log
any message for any operations it performs.

All operations a `LoggerProvider` provides MUST be safe to be run
concurrently.

### Logger Creation

[New Logger instances are always created with a LoggerProvider](./bridge-api.md#loggerprovider).
Therefore, `LoggerProvider` MUST allow for the creation of `Logger`s.
All `Logger`s created MUST be an instance of the [No-Op Logger](#logger).

Since all `Logger`s will hold the same empty state, a `LoggerProvider` MAY
return the same `Logger` instances to all creation requests.

[The API specifies multiple parameters](./bridge-api.md#loggerprovider) that
need to be accepted by the creation operation. The `LoggerProvider` MUST
accept these parameters. However, the `LoggerProvider` MUST NOT validate
any argument it receives.

## Logger

A `Logger` is always created by a `LoggerProvider`. The No-Op MUST NOT provide
a way for a user to create a `Logger` other than by a No-Op `LoggerProvider`.

The `Logger`s created by the No-Op need to hold as small a memory
footprint as possible. Therefore, all `Logger`s created MUST NOT hold
configuration or operational state.

The `Logger` MUST NOT return a non-empty error or log any message for any
operations it performs.

All operations a `Logger` provides MUST be safe to be run concurrently.

### Emit LogRecord

The No-Op `Logger` MUST allow
for [emitting LogRecords](./bridge-api.md#emit-logrecord).

[The API specifies multiple parameters](./bridge-api.md#emit-logrecord) that
need to be accepted by `emit`. The `Logger` MUST accept these parameters.
However, the `Logger` MUST NOT validate any argument it receives.
