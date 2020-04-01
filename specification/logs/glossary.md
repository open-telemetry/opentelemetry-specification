# Logs Glossary

These definitions are in addition to the [Glossary](../glossary.md)
that defines common OpenTelemetry concepts.

## Log Record

A recording of an event. Typically the record includes a timestamp indicating
when the event happened as well as other data that describes what happened,
where it happened, etc.

Also known as Log Entry.

## Log

Sometimes used to refer to a collection of Log Records. May be ambiguous, since
people also sometimes use `Log` to refer to a single `Log Record`, thus this
term should be used carefully and in the context where ambiguity is possible
additional qualifiers should be used (e.g. `Log Record`).

## Embedded Log

`Log Records` embedded inside a [Span](../api-tracing.md#span)
object, in the [Events](../api-tracing.md#add-events) list.

## Standalone Log

`Log Records` that are not embedded inside a `Span` and are recorded elsewhere.

## Log Attributes

Key/value pairs contained in a `Log Record`.

## Structured Logs

Logs that are recorded in a format which has a well-defined structure that allows
to differentiate between different elements of a Log Record (e.g. the Timestamp,
the Attributes, etc). The _Syslog protocol_ ([RFC 5425](https://tools.ietf.org/html/rfc5424)),
for example, defines a `structured-data` format.

## Flat File Logs

Logs recorded in text files, often one line per log record (although multiline
records are possible too). There is no common industry agreement whether
logs written to text files in more structured formats (e.g. JSON files)
are considered Flat File Logs or not. Where such distinction is important it is
recommended to call it out specifically.
