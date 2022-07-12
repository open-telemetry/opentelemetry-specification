# Navigation

**Status**: [Experimental](../../../../document-status.md)

**type:** `navigation`

**Description**: Represents a browser navigation event.

<!-- semconv browser -->
| Attribute  | Type | Value  | Requirement Level |
|---|---|---|---|---|
| `event.name` | string | `navigation` | Required |
| `event.domain | string | `browser` | Required |
<!-- endsemconv -->

Additional attributes are mapped from the (Navigation Timing API)[https://www.w3.org/TR/navigation-timing-2/#sec-PerformanceNavigationTiming].

This list is not exhaustive and is listed as an example. All numeric and string values thar are provided by the Navigation Timing API SHOULD be included.


| Attribute  | Type | Example  | Requirement Level |
|---|---|---|---|---|
| `unloadEventStart` | numeric | 0 | Optional |
| `unloadEventEnd` | numeric | 0 | Optional |
| `domInteractive` | numeric | 0 | Optional |
| `domContentLoadedEventStart` | numeric | 0 | Optional |
| `domContentLoadedEventStart` | numeric | 0 | Optional |
| `domComplete` | numeric | 0 | Optional |
| `loadEventStart` | numeric | 0 | Optional |
| `loadEventEnd` | numeric | 0 | Optional |
| `type` | string | `navigate`; `reload`; `back_forward` | Optional |
| `redirectCount` | numeric | 0 | Optional |
