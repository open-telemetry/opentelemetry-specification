# zPages: general direction (#110)

Make zPages a standard OpenTelemetry component.

## Motivation

Self-introspection debug pages or zPages are in-process web pages that display collected data from the process they are attached to. They are used to provide in-process diagnostics without the need of any backend to examine traces or metrics. Various implementations of zPages are widely used in many environments. The standard extensible implementation of zPages in OpenTelemetry will benefit everybody.

## Explanation

This OTEP is a request to get a general approval for zPages development as an experimental feature [open-telemetry/opentelemetry-specification#62](https://github.com/open-telemetry/opentelemetry-specification/pull/632). See [opencensus.io/zpages](https://opencensus.io/zpages/) for the overview of zPages.

## Internal details

Implementation of zPages includes multiple components - data collection (sampling, filtering, configuration), storage and aggregation, and a framework to expose this data.

This is a request for a general direction approval. There are a few principles for the development:

1. zPages MUST NOT be hardcoded into OpenTelemetry SDK.
2. OpenTelemetry implementation of zPages MUST be split as two separate components - one for data, another for rendering. So that, for example, data providers could be also integrated into other rendering frameworks.
3. zPages SHOULD be built as a framework that provides a way to extend information exposed from the process. Ideally all the way to replace OpenTelemetry SDK with alternative source of information.

## Trade-offs and mitigations

We may discover that implementation of zPages as a vendor-specific or user-specific plugins may be preferable. Based on initial investigation, extensible standard implementation will benefit everybody.

## Prior art and alternatives

[opencensus.io/zpages](https://opencensus.io/zpages/)

## Open questions

N/A

## Future possibilities

N/A
