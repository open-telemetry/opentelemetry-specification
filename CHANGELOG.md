# Changelog

Please update changelog as part of any significant pull request. Place short
description of your change into "Unreleased" section. As part of release
process content of "Unreleased" section content will generate release notes for
the release.

## Unreleased

## v0.2.0 (10-22-2019)
### Specification Changes
- Added a new Metrics API for creating measurements, and a new Meter API for capturing them.
- Removed SpanData interface in favor of Span Start and End options.
- Added a TracerFactory interface for labeling spans library 
- Added design goals and requirements for a telemetry data exchange protocol.
- Added a Span Processor interface for intercepting span start and end invocations.
- Added a Span Exporter interface for processing batches of spans.
- Replace DistributedContext.GetIterator with GetEntries.
- Clarifications and adjustments to improve cross-language applicability.

### Related OTEPS
- [Telemetry Without Manual Instrumentation](https://github.com/open-telemetry/oteps/blob/master/text/0001-telemetry-without-manual-instrumentation.md)
- [Remove SpanData](https://github.com/open-telemetry/oteps/blob/master/text/0002-remove-spandata.md)
- [Consolidate pre-aggregated and raw metrics APIs](https://github.com/open-telemetry/oteps/blob/master/text/0003-measure-metric-type.md)
- [Sampling API](https://github.com/open-telemetry/oteps/blob/master/text/0006-sampling.md)
- [Remove support to report out-of-band telemetry](https://github.com/open-telemetry/oteps/blob/master/text/0007-no-out-of-band-reporting.md)
- [Metrics Observers API](https://github.com/open-telemetry/oteps/blob/master/text/0008-metric-observer.md)
- [Metric Handle API](https://github.com/open-telemetry/oteps/blob/master/text/0009-metric-handles.md)
- [Rename "Cumulative" to "Counter"](https://github.com/open-telemetry/oteps/blob/master/text/0010-cumulative-to-counter.md)
- [Named Tracers and Meters](https://github.com/open-telemetry/oteps/blob/master/text/0016-named-tracers.md)

## v0.1.0 (06-21-2019)

### Specification Changes
- Added API proposal for the converged OpenTracing/OpenCensus project is complete.
