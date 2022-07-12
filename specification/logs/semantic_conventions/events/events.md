# Event

**Status**: [Experimental](../../../document-status.md)

**type:** `event`

**Description**: All events are described by these attributes.

<!-- semconv browser -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `event.name` | string | The event name that uniquely identifies the type of the event within the domain. | `exception`; `interaction` | Required |
| `event.domain | string | Identifies the group of related events. Each event within a domain MUST have a unique value for the event.name attribute. | `browser`; `mobile` | Recommended |
| `event.data` | any | Some events/domains may choose to send event attributes as an object or serialized string. | `Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36` | Optional |
<!-- endsemconv -->
