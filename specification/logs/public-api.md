# Public Logs API

**Status**: [Development](../document-status.md), except where otherwise specified

<details>
<summary>Table of Contents</summary>

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [Logger](#logger)
  * [Logger operations](#logger-operations)
- [References](#references)

<!-- tocstop -->

</details>

<b>Note: this document is a work in progress as we move towards defining a user-facing Logs API. Unlike the current [Logs Bridge API](./bridge-api.md), this new API is intended to be called by both application developers and logging
library authors to build
[log appenders](./supplementary-guidelines.md#how-to-create-a-log4j-log-appender),
which use this API to bridge between existing logging libraries and the
OpenTelemetry log data model.</b>

## Logger

The `Logger` is responsible for emitting `LogRecord`s.

### Logger operations

The full set of operations that a `Logger` will provide is not yet defined. The
intent is that is will provide the capabalities needed to emit a `LogRecord` as is currently provided by

* [Logs Bridge API](./bridge-api.md)
* [Events API](./event-api.md)

## References

- [OTEP0265 Event Basics](https://github.com/open-telemetry/oteps/blob/main/text/0265-event-vision.md#api)
