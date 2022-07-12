# Navigation

**Status**: [Experimental](../../../../document-status.md)

**type:** `resource`

**Description**: Represents a resource observed by the browser.

<!-- semconv browser -->
| Attribute  | Type | Value  | Requirement Level |
|---|---|---|---|---|
| `event.name` | string | `resource` | Required |
| `event.domain | string | `browser` | Required |
<!-- endsemconv -->

Additional attributes are mapped from the (Resource Timing API)[https://www.w3.org/TR/resource-timing-2/#sec-performanceresourcetiming].

This list is not exhaustive and is listed as an example. All numeric and string values thar are provided by the Resource Timing API SHOULD be included.

| Attribute  | Type | Example  | Requirement Level |
|---|---|---|---|---|
| `redirectStart` | numeric | 0 | Optional |
| `redirectEnd` | numeric | 0 | Optional |
| `fetchStart` | numeric | 0 | Optional |
| `domainLookupStart` | numeric | 0 | Optional |
| `domainLookupEnd` | numeric | 0 | Optional |
| `connectStart` | numeric | 0 | Optional |
| `connectEnd` | numeric | 0 | Optional |
| `secureConnectionStart` | numeric | 0 | Optional |
| `requestStart` | numeric | 0 | Optional |
| `responseStart` | numeric | 0 | Optional |
| `responseEnd` | numeric | 0 | Optional |
| `transferSize` | numeric | 0 | Optional |
| `encodedBodySize` | numeric | 0 | Optional |
| `decodedBodySize` | numeric | 0 | Optional |
