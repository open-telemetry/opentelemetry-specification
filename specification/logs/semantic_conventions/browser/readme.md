# Browser events semantic conventions

All browser events MUST have the `event.domain` attribute set to `browser`.

| Event name | Description |
|---|---|
| [`pageview`](./pageview.md) | Represents a page impression event. |
| [`useraction`](./useraction.md) | Represents an interaction event like click, scroll, etc. |
| [`fetchtiming`](./fetchtiming.md) | Represents the fetchtiming  event that has page fetch timing details. |
| [`exception`](./exception.md) | Represents the exception event.|