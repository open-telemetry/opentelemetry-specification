# Log Correlation

Log correlation is a feature that inserts information about the current span into log entries
created by existing logging frameworks.  The feature can be used to add more context to log entries,
filter log entries by trace ID, or find log entries associated with a specific trace or span.

The design of a log correlation implementation depends heavily on the details of the particular
logging framework that it supports.  Therefore, this document only covers the aspects of log
correlation that could be shared across log correlation implementations for multiple languages and
logging frameworks.  It doesn't cover how to hook into the logging framework.

## Identifying the span to associate with a log entry

A log correlation implementation should look up tracing data from the span that is current at the
point of the log statement.  See
[Span.md#how-span-interacts-with-context](Span.md#how-span-interacts-with-context) for the
definition of the current span.

## Tracing data to include in log entries

A log correlation implementation should make the following pieces of tracing data from the current
span context available in each log entry:

### Trace ID

The trace ID of the current span. See [SpanContext](../overview.md#spancontext).

### Span ID

The span ID of the current span. See [SpanContext](../overview.md#spancontext).

### Sampling Decision

The sampling bit of the current span, as a boolean.  See
[SpanContext](../overview.md#spancontext).

TODO(sebright): Include "samplingScore" once that field is added to the SpanContext.

TODO(sebright): Add a section on fields from the Tracestate. Users should be able to add
vendor-specific fields from the Tracestate to logs, using a callback mechanism.

TODO(sebright): Consider adding parent span ID, to allow recreating the trace structure from logs.

## String format for tracing data

The logging framework may require the pieces of tracing data to be converted to strings.  In that
case, the log correlation implementation should format the trace ID and span ID as lowercase base 16
and format the sampling decision as "true" or "false".

## Key names for tracing data

Some logging frameworks allow the insertion of arbitrary key-value pairs into log entries.  When
a log correlation implementation inserts tracing data by that method, the key names should be
"traceId", "spanId", and "traceSampled" by default.  The log correlation implementation may allow
the user to override the key names.
