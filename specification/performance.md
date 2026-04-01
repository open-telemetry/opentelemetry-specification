# Performance and Blocking of OpenTelemetry API

This document defines common principles that will help designers create OpenTelemetry clients that are safe to use.

## Key principles

Here are the key principles:

- **Library should not block end user application by default.**
- **Library should not consume unbounded memory resource.**

Although there are inevitable overhead to achieve monitoring, API should not degrade the end user application as possible. So that it should not block the end user application nor consume too much memory resource.

See also [Concurrency and Thread-Safety](library-guidelines.md#concurrency-and-thread-safety) if the implementation supports concurrency.

### Trade-off between non-blocking and memory consumption

Incomplete asynchronous I/O tasks or background tasks may consume memory to preserve their state. In such a case, there is a trade-off between dropping some tasks to prevent memory starvation and keeping all tasks to prevent information loss.

If there is such trade-off in OpenTelemetry client, it should provide the following options to end user:

- **Prevent information loss**: Preserve all information but possible to consume many resources
- **Prevent blocking**: Dropping some information under overwhelming load and show warning log to inform when information loss starts and when recovered
  - Should provide option to change threshold of the dropping
  - Better to provide metric that represents effective sampling ratio
  - OpenTelemetry client might provide this option for Logging

### End user application should be aware of the size of logs

Logging could consume much memory by default if the end user application emits too many logs. This default behavior is intended to preserve logs rather than dropping it. To make resource usage bounded, the end user should consider reducing logs that are passed to the exporters.

Therefore, the OpenTelemetry client should provide a way to filter logs to capture by OpenTelemetry. End user applications may want to log so much into log file or stdout (or somewhere else) but not want to send all of the logs to OpenTelemetry exporters.

In a documentation of the OpenTelemetry client, it is a good idea to point out that too many logs consume many resources by default then guide how to filter logs.

### Shutdown and explicit flushing could block

The OpenTelemetry client could block the end user application when it shut down. On shutdown, it has to flush data to prevent information loss. The OpenTelemetry client should support user-configurable timeout if it blocks on shut down.

If the OpenTelemetry client supports an explicit flush operation, it could block also. But should support a configurable timeout.

## Documentation

If language specific implementation has special characteristics that are not described in this document, such characteristics should be documented.
