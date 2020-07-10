# Changelog

Please update changelog as part of any significant pull request. Place short
description of your change into "Unreleased" section. As part of release
process content of "Unreleased" section content will generate release notes for
the release.

## Unreleased

- Add semantic convention for NGINX custom HTTP 499 status code.

## v0.6.0 (07-01-2020)

New:

- Add span attribute to indicate cold starts of Function as a Service executions ([#650](https://github.com/open-telemetry/opentelemetry-specification/pull/650))
- Add conventions for naming of exporter packages ([#629](https://github.com/open-telemetry/opentelemetry-specification/pull/629))
- Add semantic conventions for container id ([#673](https://github.com/open-telemetry/opentelemetry-specification/pull/673))
- Add semantic conventions for HTTP content length ([#641](https://github.com/open-telemetry/opentelemetry-specification/pull/641))
- Add semantic conventions for process resource ([#635](https://github.com/open-telemetry/opentelemetry-specification/pull/635))
- Add peer.service to provide a user-configured name for a remote service ([#652](https://github.com/open-telemetry/opentelemetry-specification/pull/652))

Updates:
- Improve root Span description ([#645](https://github.com/open-telemetry/opentelemetry-specification/pull/645))
- Extend semantic conventions for RPC and allow non-gRPC calls ([#604](https://github.com/open-telemetry/opentelemetry-specification/pull/604))
- Revise and extend semantic conventions for databases ([#575](https://github.com/open-telemetry/opentelemetry-specification/pull/575))
- Clarify Tracer vs TracerProvider in tracing API and SDK spec. ([#619](https://github.com/open-telemetry/opentelemetry-specification/pull/619))
  Most importantly:
  * Configuration should be stored not per Tracer but in the TracerProvider.
  * Active spans are not per Tracer.
- Do not set any value in Context upon failed extraction ([#671](https://github.com/open-telemetry/opentelemetry-specification/pull/671))
- Clarify semantic conventions around span start and end time ([#592](https://github.com/open-telemetry/opentelemetry-specification/pull/592))

## v0.5.0 (06-02-2020)

- Define Log Data Model.
- Remove SpanId from Sampler input.
- Clarify what it will mean for a vendor to "support OpenTelemetry".
- Clarify Tracers should reference an InstrumentationLibrary rather than a Resource.
- Replace ALWAYS_PARENT sampler with a composite ParentOrElse sampler.
- Incorporate old content on metrics calling conventions, label sets.
- Update api-metrics-user.md and api-metrics-meter.md with the latest metrics API.
- Normalize Instrumentation term for instrumentations.
- Change w3c correlation context to custom header.

## v0.4.0 (05-12-2020)

- [OTEP-83](https://github.com/open-telemetry/oteps/blob/master/text/0083-component.md) Introduce the notion of InstrumentationLibrary.
- [OTEP-88](https://github.com/open-telemetry/oteps/blob/master/text/metrics/0088-metric-instrument-optional-refinements.md) Metrics API instrument foundation.
- [OTEP-91](https://github.com/open-telemetry/oteps/blob/master/text/logs/0091-logs-vocabulary.md) Logs vocabulary.
- [OTEP-92](https://github.com/open-telemetry/oteps/blob/master/text/logs/0092-logs-vision.md) Logs Vision.
- [OTEP-90](https://github.com/open-telemetry/oteps/blob/master/text/metrics/0090-remove-labelset-from-metrics-api.md) Remove LabelSet from the metrics API.
- [OTEP-98](https://github.com/open-telemetry/oteps/blob/master/text/metrics/0098-metric-instruments-explained.md) Explain the metric instruments.
- [OTEP-99](https://github.com/open-telemetry/oteps/blob/master/text/0099-otlp-http.md) OTLP/HTTP: HTTP Transport Extension for OTLP.
- Define handling of null and empty attribute values.
- Rename Setter.put to Setter.set
- Add glossary for typically misused terms.
- Clarify that resources are immutable.
- Clarify that SpanContext.IsRemote is false on remote children.
- Move specifications into sub-directories per signal.
- Remove references to obsolete `peer.*` attributes.
- Span semantic conventions for for messaging systems.
- Span semantic conventions for function as a service.
- Remove the handling of retries from trace exporters.
- Remove Metrics' default keys.
- Add some clarifying language to the semantics of metric instrument naming.
- Allow injectors and extractors to be separate interfaces.
- Add an explanation on why Context Restore operation is needed.
- Document special Zipkin conversion cases.

## v0.3.0 (02-21-2020)

- [OTEP-0059](https://github.com/open-telemetry/oteps/blob/master/text/trace/0059-otlp-trace-data-format.md) Add OTLP Trace Data Format specification.
- [OTEP-0066](https://github.com/open-telemetry/oteps/blob/master/text/0066-separate-context-propagation.md) Separate Layer for Context Propagation.
- [OTEP-0070](https://github.com/open-telemetry/oteps/blob/master/text/metrics/0070-metric-bound-instrument.md) Rename metric instrument "Handles" to "Bound Instruments".
- [OTEP-0072](https://github.com/open-telemetry/oteps/blob/master/text/metrics/0072-metric-observer.md) Metric Observer instrument specification (refinement).
- [OTEP-0080](https://github.com/open-telemetry/oteps/blob/master/text/metrics/0080-remove-metric-gauge.md) Remove the Metric Gauge instrument, recommend use of other instruments.
- Update 0003-measure-metric-type to match current Specification.
- Update 0009-metric-handles to match current Specification.
- Clarify named tracers and meters.
- Remove SamplingHint from the Sampling OTEP (OTEP-0006).
- Remove component attribute.
- Allow non-string Resource label values.
- Allow array values for attributes.
- Add service version to Resource attributes.
- Add general, general identity, network and VM image attribute conventions.
- Add a section on transformation to Zipkin Spans.
- Add a section on SDK default configuration.
- Enhance semantic conventions for HTTP/RPC.
- Provide guidelines for low-cardinality span names.
- SDK Tracer: Replace TracerFactory with TracerProvider.
- Update Resource to be in the SDK.

## v0.2.0 (10-22-2019)

- [OTEP-0001](https://github.com/open-telemetry/oteps/blob/master/text/0001-telemetry-without-manual-instrumentation.md) Added Auto-Instrumentation.
- [OTEP-0002](https://github.com/open-telemetry/oteps/blob/master/text/trace/0002-remove-spandata.md): Removed SpanData interface in favor of Span Start and End options.
- [OTEP-0003](https://github.com/open-telemetry/oteps/blob/master/text/metrics/0003-measure-metric-type.md) Consolidatesd pre-aggregated and raw metrics APIs.
- [OTEP-0008](https://github.com/open-telemetry/oteps/blob/master/text/metrics/0008-metric-observer.md) Added Metrics Observers API.
- [OTEP-0009](https://github.com/open-telemetry/oteps/blob/master/text/metrics/0009-metric-handles.md) Added Metrics Handle API.
- [OTEP-0010](https://github.com/open-telemetry/oteps/blob/master/text/metrics/0010-cumulative-to-counter.md) Rename "Cumulative" to "Counter" in the Metrics API.
- [OTEP-006](https://github.com/open-telemetry/oteps/blob/master/text/trace/0006-sampling.md) Moved sampling from the API tp the SDK.
- [OTEP-0007](https://github.com/open-telemetry/oteps/blob/master/text/0007-no-out-of-band-reporting.md) Moved support for out-of-band telemetry from the API to the SDK.
- [OTEP-0016](https://github.com/open-telemetry/oteps/blob/master/text/0016-named-tracers.md) Added named providers for Tracers and Meters.
- Added design goals and requirements for a telemetry data exchange protocol.
- Added a Span Processor interface for intercepting span start and end invocations.
- Added a Span Exporter interface for processing batches of spans.
- Replaced DistributedContext.GetIterator with GetEntries.
- Added clarifications and adjustments to improve cross-language applicability.
- Added a specification for SDK configuration.

## v0.1.0 (06-21-2019)

- Added API proposal for the converged OpenTracing/OpenCensus project is complete.
