# Events semantic conventions

Events in OpenTelemetry are a subset of logs with specific set of semantic conventions.

Each events MUST follow the [`events.*`](./events.md) semantic conventions, and it must follow semantic conventions specific for the type of event 

Each event has a name (`event.name`) attribute, which uniquely identifies the type of the event. In addition 