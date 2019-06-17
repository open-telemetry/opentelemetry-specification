# Performance and Blocking of OpenTelemetry API

This document defines common principles that will help designers create language libraries that are safe to use. 

## Key principles

Here are the key principles:

- **Library should not block end-user application.**
- **Library should not consume infinite memory resource.**

Tracer should not degrade the end-user application. So that it should not block the end-user application nor consume too much memory resource.

Especially, most telemetry exporters need to call API of servers to export traces. API call operations should be performed in asynchronous I/O or background thread to prevent blocking end-user applications.

See also [Concurrency and Thread-Safety](concurrency.md) if implementation supports concurrency.

### Trade-off between non-blocking and memory consumption

Any incomplete asynchronous I/O tasks or background tasks may consume memory to preserve its state. In such a case, there is a trade-off between dropping some tasks to prevent memory starvation and keeping all tasks to prevent information loss.

If there is such trade-off in language library, it should provide the following options to end-user:

- **Prevent blocking**: Dropping some information under overwhelming load and show warning log to inform when information loss starts and when recovered
  - Should be a default option
  - Should provide option to change threshold of the dropping
  - Better to provide metric that represents effective sampling ratio
- **Prevent information loss**: Preserve all information but possible to consume unlimited resource
  - Should be supported as an alternative option

## Documentation

If language specific implementation has any special characteristics that are not described in this document, such characteristics should be documented.
