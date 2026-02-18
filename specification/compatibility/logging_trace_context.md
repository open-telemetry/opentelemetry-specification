# Trace Context in non-OTLP Log Formats

**Status**: [Stable](../document-status.md)

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [Overview](#overview)
  * [Syslog RFC5424](#syslog-rfc5424)
  * [Plain Text Formats](#plain-text-formats)
  * [JSON Formats](#json-formats)
  * [Other Structured Formats](#other-structured-formats)

<!-- tocstop -->

</details>

## Overview

OTLP Logs Records have top level fields
representing [trace context](../logs/data-model.md#trace-context-fields). This
document defines how trace context should be recorded in non-OTLP Log Formats.
To summarize, the following field names should be used in legacy formats:

- "trace_id" for [TraceId](../logs/data-model.md#field-traceid), lowercase and hex-encoded.
- "span_id" for [SpanId](../logs/data-model.md#field-spanid), lowercase and hex-encoded.
- "trace_flags" for [trace flags](../logs/data-model.md#field-traceflags), formatted
  according to W3C traceflags format.

All 3 fields are optional (see the [data model](../logs/data-model.md) for details of
which combination of fields is considered valid).

### Syslog RFC5424

Trace ID, span ID and traceflags SHOULD be recorded via SD-ID "OpenTelemetry".

For example:

```
[opentelemetry trace_id="102981abcd2901" span_id="abcdef1010" trace_flags="01"]
```

### Plain Text Formats

The fields SHOULD be recorded according to the customary approach used for a
particular format (e.g. field:value format for LTSV). For example:

```
host:192.168.0.1<TAB>trace_id:102981abcd2901<TAB>span_id:abcdef1010<TAB>time:[01/Jan/2010:10:11:23 -0400]<TAB>req:GET /health HTTP/1.0<TAB>status:200
```

### JSON Formats

The fields SHOULD be recorded as top-level fields in the JSON structure. For example:

```json
{
  "timestamp":1581385157.14429,
  "body":"Incoming request",
  "trace_id":"102981abcd2901",
  "span_id":"abcdef1010"
}
```

### Other Structured Formats

The fields SHOULD be recorded as top-level structured attributes of the log
record as it is customary for the particular format.
