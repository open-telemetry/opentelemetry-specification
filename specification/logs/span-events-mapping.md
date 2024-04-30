# Span Event to Events Mapping

**Status**: [Experimental](../document-status.md)

<details>
<summary>Table of Contents</summary>

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

<!-- tocstop -->

</details>

[Span Events](../trace/api.md#add-events) represent an event attached to a span and has a different structure than [Events](./event-api.md).

Applications or telemetry consumers MAY transform Span Events to Events inside their span processing pipeline using the mappings defined in the document.

Event API properties:

<!- TODO add link to semantic conventions once https://github.com/open-telemetry/semantic-conventions/pull/954 is merged -->

- `Name` SHOULD match the Span Event name
- `Timestamp` SHOULD match Span Event timestamp
- `Context` SHOULD match the context of the span the Span Event is attached to.
- `SeverityNumber` - no mapping, not set. <!-- TODO define mapping in the semconv -->
- `Payload` SHOULD be set to the object deserialized from JSON string provided in the Span Event `event.data` attribute (if any). If deserialization fails with an error, the original string value of the `event.data` attribute SHOULD be used.
- `Attributes` SHOULD match Span Event attributes except those that were used to populate other event properties (`event.data`).

The `EventLogger` used to report mapped Events SHOULD have the same instrumentation scope properties as the
Span the original Span Event is attached to.