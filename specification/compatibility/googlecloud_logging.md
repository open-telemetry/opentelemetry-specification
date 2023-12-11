<!--- Hugo front matter used to generate the website version of this page:
linkTitle: Google Cloud Logging
--->

# Google Cloud Logging

**Status**: [Experimental](../document-status.md)

Google Cloud logging uses the [LogEntry](https://cloud.google.com/logging/docs/reference/v2/rest/v2/LogEntry) to
cary log information. In this section the JSON representation is used for mapping of the fields to OpenTelemetry fields
and attributes.

## Semantic Mapping

Some of the attributes can be moved to OpenTelemetry Semantic Conventions.

| Field       | Type      | Description                            | Maps to Unified Model Field    |
|-------------|-----------|----------------------------------------|--------------------------------|
| `insert_id` | `boolean` | A unique identifier for the log entry. | `Attributes["log.record.uid"]` |

## Severity Mapping

Mapping from [Google Cloud Log Severity](https://cloud.google.com/logging/docs/reference/v2/rest/v2/LogEntry#LogSeverity)
to the OpenTelemetry Severity Number

| CloudLog         | Severity Number  | CloudLog Description                                                                   |
|------------------|------------------|----------------------------------------------------------------------------------------|
| `DEFAULT`(0)     | `UNSPECIFIED`(0) | The log entry has no assigned severity level.                                          |
| `DEBUG`(100)     | `DEBUG`(5)       | Debug or trace information.                                                            |
| `INFO`(200)      | `INFO`(9)        | Routine information, such as ongoing status or performance.                            |
| `NOTICE`(300)    | `INFO2`(10)      | Normal but significant events, such as start up, shut down, or a configuration change. |
| `WARNING`(400)   | `WARN`(13)       | Warning events might cause problems.                                                   |
| `ERROR`(500)     | `ERROR`(17)      | Error events are likely to cause problems.                                             |
| `CRITICAL`(600)  | `FATAL`(21)      | Critical events cause more severe problems or outages.                                 |
| `ALERT`(700)     | `FATAL2`(22)     | A person must take an action immediately.                                              |
| `EMERGENCY`(800) | `FATAL4`(24)     | One or more systems are unusable.                                                      |

Mapping from OpenTelemetry Severity Number to a
[Google Cloud Log Severity](https://cloud.google.com/logging/docs/reference/v2/rest/v2/LogEntry#LogSeverity)

| Severity Number             | CloudLog         |
|-----------------------------|------------------|
| `UNSPECIFIED`(0)            | `DEFAULT`(0)     |
| `TRACE`(1) - `DEBUG4`(8)    | `DEBUG`(100)     |
| `INFO`(9)                   | `INFO`(200)      |
| `INFO2`(10) - `INFO4`(12)   | `NOTICE`(300)    |
| `WARN`(13) - `WARN4`(16)    | `WARNING`(400)   |
| `ERROR`(17) - `ERROR4`(20   | `ERROR`(500)     |
| `FATAL`(21)                 | `CRITICAL`(600)  |
| `FATAL2`(22) - `FATAL3`(23) | `ALERT`(700)     |
| `FATAL4`(24)                | `EMERGENCY`(800) |

## Miscellaneous

| Field              | Type                     | Description                                                                                                      | Maps to Unified Model Field                   |
|--------------------|--------------------------|------------------------------------------------------------------------------------------------------------------|-----------------------------------------------|
| `timestamp`        | `string`                 | The time the event described by the log entry occurred.                                                          | `Timestamp`                                   |
| `receiveTimestamp` | `string`                 | The time the log entry was received.                                                                             | `ObservedTimestamp`                           |
| `logName`          | `string`                 | The URL-encoded log ID suffix of the log_name field identifies which log stream this entry belongs to.           | `Attributes["gcp.log_name"]` (string)         |
| `jsonPayload`      | `google.protobuf.Struct` | The log entry payload, represented as a structure that is expressed as a JSON object.                            | `Body` (KVList)                               |
| `protoPayload`     | `google.protobuf.Any`    | The log entry payload, represented as a protocol buffer.                                                         | `Body` (KVList, key from JSON representation) |
| `textPayload`      | `string`                 | The log entry payload, represented as a Unicode string (UTF-8).                                                  | `Body` (string)                               |
| `trace`            | `string`                 | The trace associated with the log entry, if any.                                                                 | `TraceId`                                     |
| `spanId`           | `string`                 | The span ID within the trace associated with the log entry.                                                      | `SpanId`                                      |
| `traceSampled`     | `boolean`                | The sampling decision of the trace associated with the log entry.                                                | `TraceFlags.SAMPLED`                          |
| `labels`           | `map<string,string>`     | A set of user-defined (key, value) data that provides additional information about the log entry.                | `Attributes`                                  |
| `resource`         | `MonitoredResource`      | The monitored resource that produced this log entry.                                                             | `Resource["gcp.*"]`                           |
| `httpRequest`      | `HttpRequest`            | The HTTP request associated with the log entry, if any.                                                          | `Attributes["gcp.http_request"]` (KVList)     |
| `operation`        | `LogEntryOperation`      | Information about a operation associated with the log entry.                                                     | `Attributes["gcp.operation"]`  (KVList)       |
| `sourceLocation`   | `LogEntrySourceLocation` | Source code location information associated with the log entry.                                                  | `Attributes["gcp.source_location"]` (KVList)  |
| `split`            | `LogSplit`               | Information indicating this LogEntry is part of a sequence of multiple log entries split from a single LogEntry. | `Attributes["gcp.log_split"]`  (KVList)       |
