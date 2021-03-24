# Changelog

Please update changelog as part of any significant pull request. Place short
description of your change into "Unreleased" section. As part of release process
content of "Unreleased" section content will generate release notes for the
release.

## Unreleased

### Context

- Clarify composite `TextMapPropagator` method required and optional arguments. ([#1541](https://github.com/open-telemetry/opentelemetry-specification/pull/1541))
- Clarify B3 requirements and configuration. ([#1570](https://github.com/open-telemetry/opentelemetry-specification/pull/1570))

### Traces

- Add `ForceFlush` to `Span Exporter` interface ([#1467](https://github.com/open-telemetry/opentelemetry-specification/pull/1467))
- Clarify the description for the `TraceIdRatioBased` sampler needs to include the sampler's sampling ratio. ([#1536](https://github.com/open-telemetry/opentelemetry-specification/pull/1536))
- Define the fallback tracer name for invalid values.
  ([#1534](https://github.com/open-telemetry/opentelemetry-specification/pull/1534))
- Remove the Included Propagators section from trace API specification that was a duplicate of the Propagators Distribution of the context specification. ([#1556](https://github.com/open-telemetry/opentelemetry-specification/pull/1556))
- Remove the Baggage API propagator notes that conflict with the API Propagators Operations section and fix [#1526](https://github.com/open-telemetry/opentelemetry-specification/issues/1526). ([#1575](https://github.com/open-telemetry/opentelemetry-specification/pull/1575))

### Metrics

- Adds new metric data model specification ([#1512](https://github.com/open-telemetry/opentelemetry-specification/pull/1512))

### Logs

### Semantic Conventions

- Add details for filling semantic conventions for AWS Lambda ([#1442](https://github.com/open-telemetry/opentelemetry-specification/pull/1442))
- Update semantic conventions to distinguish between int and double ([#1550](https://github.com/open-telemetry/opentelemetry-specification/pull/1550))

### Compatibility

- Add initial OpenTracing compatibility section.
  ([#1101](https://github.com/open-telemetry/opentelemetry-specification/pull/1101))

## v1.1.0 (2021-03-11)

### Traces

- Implementations can ignore links with invalid SpanContext([#1492](https://github.com/open-telemetry/opentelemetry-specification/pull/1492))
- Add `none` as a possible value for OTEL_TRACES_EXPORTER to disable export
  ([#1439](https://github.com/open-telemetry/opentelemetry-specification/pull/1439))
- Add [`ForceFlush`](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/trace/sdk.md#forceflush) to SDK's `TracerProvider` ([#1452](https://github.com/open-telemetry/opentelemetry-specification/pull/1452))

### Metrics

- Add `none` as a possible value for OTEL_METRICS_EXPORTER to disable export
  ([#1439](https://github.com/open-telemetry/opentelemetry-specification/pull/1439))

### Logs

### Semantic Conventions

- Add `elasticsearch` to `db.system` semantic conventions ([#1463](https://github.com/open-telemetry/opentelemetry-specification/pull/1463))
- Add `arch` to `host` semantic conventions ([#1483](https://github.com/open-telemetry/opentelemetry-specification/pull/1483))
- Add `runtime` to `container` semantic conventions ([#1482](https://github.com/open-telemetry/opentelemetry-specification/pull/1482))
- Rename `gcp_gke` to `gcp_kubernetes_engine` to have consistency with other
Google products under `cloud.infrastructure_service` ([#1496](https://github.com/open-telemetry/opentelemetry-specification/pull/1496))
- `http.url` MUST NOT contain credentials ([#1502](https://github.com/open-telemetry/opentelemetry-specification/pull/1502))
- Add `aws.eks.cluster.arn` to EKS specific semantic conventions ([#1484](https://github.com/open-telemetry/opentelemetry-specification/pull/1484))
- Rename `zone` to `availability_zone` in `cloud` semantic conventions ([#1495](https://github.com/open-telemetry/opentelemetry-specification/pull/1495))
- Rename `cloud.infrastructure_service` to `cloud.platform` ([#1530](https://github.com/open-telemetry/opentelemetry-specification/pull/1530))
- Add section describing that libraries and the collector should autogenerate
the semantic convention keys. ([#1515](https://github.com/open-telemetry/opentelemetry-specification/pull/1515))

## v1.0.1 (2021-02-11)

- Fix rebase issue for span limit default values ([#1429](https://github.com/open-telemetry/opentelemetry-specification/pull/1429))

## v1.0.0 (2021-02-10)

New:

- Add `cloud.infrastructure_service` resource attribute
  ([#1112](https://github.com/open-telemetry/opentelemetry-specification/pull/1112))
- Add `SpanLimits` as a configuration for the TracerProvider([#1416](https://github.com/open-telemetry/opentelemetry-specification/pull/1416))

Updates:

- Add `http.server.active_requests` to count in-flight HTTP requests
  ([#1378](https://github.com/open-telemetry/opentelemetry-specification/pull/1378))
- Update default limit for span attributes, events, links to 128([#1419](https://github.com/open-telemetry/opentelemetry-specification/pull/1419))
- Update OT Trace propagator environment variable to match latest name([#1406](https://github.com/open-telemetry/opentelemetry-specification/pull/1406))
- Remove Metrics SDK specification to avoid confusion, clarify that Metrics API
  specification is not recommended for client implementation
  ([#1401](https://github.com/open-telemetry/opentelemetry-specification/pull/1401))
- Rename OTEL_TRACE_SAMPLER and OTEL_TRACE_SAMPLER_ARG env variables to OTEL_TRACES_SAMPLER and OTEL_TRACES_SAMPLER_ARG
  ([#1382](https://github.com/open-telemetry/opentelemetry-specification/pull/1382))
- Mark some entries in compliance matrix as optional([#1359](https://github.com/open-telemetry/opentelemetry-specification/pull/1359))
  SDKs are free to provide support at their discretion.
- Rename signal-specific variables for `OTLP_EXPORTER_*` to `OTLP_EXPORTER_TRACES_*` and `OTLP_EXPORTER_METRICS_*`([#1362](https://github.com/open-telemetry/opentelemetry-specification/pull/1362))
- Versioning and stability guarantees for OpenTelemetry clients([#1291](https://github.com/open-telemetry/opentelemetry-specification/pull/1291))
- Additional Cassandra semantic attributes
  ([#1217](https://github.com/open-telemetry/opentelemetry-specification/pull/1217))
- OTEL_EXPORTER environment variable replaced with OTEL_TRACES_EXPORTER and
  OTEL_METRICS_EXPORTER which each accept only a single value, not a list.
  ([#1318](https://github.com/open-telemetry/opentelemetry-specification/pull/1318))
- `process.runtime.description` resource convention: Add `java.vm.name`
  ([#1242](https://github.com/open-telemetry/opentelemetry-specification/pull/1242))
- Refine span name guideline for SQL database spans
  ([#1219](https://github.com/open-telemetry/opentelemetry-specification/pull/1219))
- Add RPC semantic conventions for metrics
  ([#1162](https://github.com/open-telemetry/opentelemetry-specification/pull/1162))
- Clarify `Description` usage on `Status` API
  ([#1257](https://github.com/open-telemetry/opentelemetry-specification/pull/1257))
- Add/Update `Status` + `error` mapping for Jaeger & Zipkin Exporters
  ([#1257](https://github.com/open-telemetry/opentelemetry-specification/pull/1257))
- Resource's service.name MUST have a default value, service.instance.id is not
  required.
  ([#1269](https://github.com/open-telemetry/opentelemetry-specification/pull/1269))
  - Clarified in [#1294](https://github.com/open-telemetry/opentelemetry-specification/pull/1294)
- Add requirement that the SDK allow custom generation of Trace IDs and Span IDs
  ([#1006](https://github.com/open-telemetry/opentelemetry-specification/pull/1006))
- Add default ratio when TraceIdRatioSampler is specified by environment variable but
  no ratio is.
  ([#1322](https://github.com/open-telemetry/opentelemetry-specification/pull/1322))
- Require schemed endpoints for OTLP exporters
  ([1234](https://github.com/open-telemetry/opentelemetry-specification/pull/1234))
- Resource SDK: Reverse (suggested) order of Resource.Merge parameters, remove
  special case for empty strings
  ([#1345](https://github.com/open-telemetry/opentelemetry-specification/pull/1345))
- Resource attributes: lowerecased the allowed values of the `aws.ecs.launchtype`
  attribute
  ([#1339](https://github.com/open-telemetry/opentelemetry-specification/pull/1339))
- Trace Exporters: Fix TODOs in Jaeger exporter spec
  ([#1374](https://github.com/open-telemetry/opentelemetry-specification/pull/1374))
- Clarify that Jaeger/Zipkin exporters must rely on the default Resource to
  get service.name if none was specified.
  ([#1386](https://github.com/open-telemetry/opentelemetry-specification/pull/1386))
- Modify OTLP/Zipkin Exporter format variables for 1.0 (allowing further specification post 1.0)
  ([#1358](https://github.com/open-telemetry/opentelemetry-specification/pull/1358))
- Add `k8s.node` semantic conventions ([#1390](https://github.com/open-telemetry/opentelemetry-specification/pull/1390))
- Clarify stability for both OTLP/HTTP and signals in OTLP.
  ([#1400](https://github.com/open-telemetry/opentelemetry-specification/pull/1400/files))

## v0.7.0 (11-18-2020)

New:

- Document service name mapping for Jaeger exporters
  ([1222](https://github.com/open-telemetry/opentelemetry-specification/pull/1222))
- Change default OTLP port number
  ([#1221](https://github.com/open-telemetry/opentelemetry-specification/pull/1221))
- Add performance benchmark specification
  ([#748](https://github.com/open-telemetry/opentelemetry-specification/pull/748))
- Enforce that the Baggage API must be fully functional, even without an installed SDK.
  ([#1103](https://github.com/open-telemetry/opentelemetry-specification/pull/1103))
- Rename "Canonical status code" to "Status code"
  ([#1081](https://github.com/open-telemetry/opentelemetry-specification/pull/1081))
- Add Metadata for Baggage entries, and clarify W3C Baggage Propagator implementation
  ([#1066](https://github.com/open-telemetry/opentelemetry-specification/pull/1066))
- Change Status to be consistent with Link and Event
  ([#1067](https://github.com/open-telemetry/opentelemetry-specification/pull/1067))
- Clarify env variables in otlp exporter
  ([#975](https://github.com/open-telemetry/opentelemetry-specification/pull/975))
- Add Prometheus exporter environment variables
  ([#1021](https://github.com/open-telemetry/opentelemetry-specification/pull/1021))
- Default propagators in un-configured API must be no-op
  ([#930](https://github.com/open-telemetry/opentelemetry-specification/pull/930))
- Define resource mapping for Jaeger exporters
  ([#891](https://github.com/open-telemetry/opentelemetry-specification/pull/891))
- Add resource semantic conventions for operating systems
  ([#693](https://github.com/open-telemetry/opentelemetry-specification/pull/693))
- Add semantic convention for source code attributes
  ([#901](https://github.com/open-telemetry/opentelemetry-specification/pull/901))
- Add semantic conventions for outgoing Function as a Service (FaaS) invocations
  ([#862](https://github.com/open-telemetry/opentelemetry-specification/pull/862))
- Add resource semantic convention for deployment environment
  ([#606](https://github.com/open-telemetry/opentelemetry-specification/pull/606/))
- Refine semantic conventions for messaging systems and add specific attributes for Kafka
  ([#1027](https://github.com/open-telemetry/opentelemetry-specification/pull/1027))
- Clarification of the behavior of the Trace API, re: context propagation, in
  the absence of an installed SDK
- Add API and semantic conventions for recording exceptions as Span Events
  ([#697](https://github.com/open-telemetry/opentelemetry-specification/pull/697))
  * API was extended to allow adding arbitrary event attributes ([#874](https://github.com/open-telemetry/opentelemetry-specification/pull/874))
  * `exception.escaped` semantic span event attribute was added
    ([#784](https://github.com/open-telemetry/opentelemetry-specification/pull/784),
    [#946](https://github.com/open-telemetry/opentelemetry-specification/pull/946))
- Allow samplers to modify tracestate
  ([#988](https://github.com/open-telemetry/opentelemetry-specification/pull/988/))
- Update the header name for otel baggage, and version date
  ([#981](https://github.com/open-telemetry/opentelemetry-specification/pull/981))
- Define PropagationOnly Span to simplify active Span logic in Context
  ([#994](https://github.com/open-telemetry/opentelemetry-specification/pull/994))
- Add limits to the number of attributes, events, and links in SDK Spans
  ([#942](https://github.com/open-telemetry/opentelemetry-specification/pull/942))
- Add Metric SDK specification (partial): covering terminology and Accumulator component
  ([#626](https://github.com/open-telemetry/opentelemetry-specification/pull/626))
- Clarify context interaction for trace module
  ([#1063](https://github.com/open-telemetry/opentelemetry-specification/pull/1063))
- Add `Shutdown` function to `*Provider` SDK
  ([#1074](https://github.com/open-telemetry/opentelemetry-specification/pull/1074))
- Add semantic conventions for system metrics
  ([#937](https://github.com/open-telemetry/opentelemetry-specification/pull/937))
- Add `db.sql.table` to semantic conventions, allow `db.operation` for SQL
  ([#1141](https://github.com/open-telemetry/opentelemetry-specification/pull/1141))
- Add OTEL_TRACE_SAMPLER env variable definition
  ([#1136](https://github.com/open-telemetry/opentelemetry-specification/pull/1136/))
- Add guidelines for OpenMetrics interoperability
  ([#1154](https://github.com/open-telemetry/opentelemetry-specification/pull/1154))
- Add OTEL_TRACE_SAMPLER_ARG env variable definition
  ([#1202](https://github.com/open-telemetry/opentelemetry-specification/pull/1202))

Updates:

- Clarify null SHOULD NOT be allowed even in arrays
  ([#1214](https://github.com/open-telemetry/opentelemetry-specification/pull/1214))
- Remove ordering SHOULD-requirement for attributes
  ([#1212](https://github.com/open-telemetry/opentelemetry-specification/pull/1212))
- Make `process.pid` optional, split `process.command_args` from `command_line`
  ([#1137](https://github.com/open-telemetry/opentelemetry-specification/pull/1137))
- Renamed `CorrelationContext` to `Baggage`:
  ([#857](https://github.com/open-telemetry/opentelemetry-specification/pull/857))
- Add semantic convention for NGINX custom HTTP 499 status code.
- Adapt semantic conventions for the span name of messaging systems
  ([#690](https://github.com/open-telemetry/opentelemetry-specification/pull/690))
- Remove lazy Event and Link API from Span interface
  ([#840](https://github.com/open-telemetry/opentelemetry-specification/pull/840))
  * SIGs are recommended to remove any existing implementation of the lazy APIs
    to avoid conflicts/breaking changes in case they will be reintroduced to the
    spec in future.
- Provide clear definitions for readable and read/write span interfaces in the
  SDK
  ([#669](https://github.com/open-telemetry/opentelemetry-specification/pull/669))
  * SpanProcessors must provide read/write access at least in OnStart.
- Specify how `Probability` sampler is used with `ParentOrElse` sampler.
- Clarify event timestamp origin and range
  ([#839](https://github.com/open-telemetry/opentelemetry-specification/pull/839))
- Clean up api-propagators.md, by extending documentation and removing redundant
  sections
  ([#577](https://github.com/open-telemetry/opentelemetry-specification/pull/577))
- Rename HTTPText propagator to TextMap
  ([#793](https://github.com/open-telemetry/opentelemetry-specification/pull/793))
- Rename ParentOrElse sampler to ParentBased and add multiple delegate samplers
  ([#610](https://github.com/open-telemetry/opentelemetry-specification/pull/610))
- Rename ProbabilitySampler to TraceIdRatioBasedSampler and add requirements
  ([#611](https://github.com/open-telemetry/opentelemetry-specification/pull/611))
- Version attributes no longer have a prefix such as semver:
  ([#873](https://github.com/open-telemetry/opentelemetry-specification/pull/873))
- Add semantic conventions for process runtime
  ([#882](https://github.com/open-telemetry/opentelemetry-specification/pull/882),
   [#1137](https://github.com/open-telemetry/opentelemetry-specification/pull/1137))
- Use hex encoding for trace id and span id fields in OTLP JSON encoding:
  ([#911](https://github.com/open-telemetry/opentelemetry-specification/pull/911))
- Explicitly specify the SpanContext APIs IsValid and IsRemote as required
  ([#914](https://github.com/open-telemetry/opentelemetry-specification/pull/914))
- A full `Context` is the only way to specify a parent of a `Span`.
  `SpanContext` or even `Span` are not allowed anymore.
  ([#875](https://github.com/open-telemetry/opentelemetry-specification/pull/875))
- Remove obsolete `http.status_text` from semantic conventions
  ([#972](https://github.com/open-telemetry/opentelemetry-specification/pull/972))
- Define `null` as an invalid value for attributes and declare attempts to set
  `null` as undefined behavior
  ([#992](https://github.com/open-telemetry/opentelemetry-specification/pull/992))
- SDK: Rename the `Decision` values for `SamplingResult`s to `DROP`, `RECORD_ONLY`
  and `RECORD_AND_SAMPLE` for consistency
  ([#938](https://github.com/open-telemetry/opentelemetry-specification/pull/938),
  [#956](https://github.com/open-telemetry/opentelemetry-specification/pull/956))
- Metrics API: Replace "Additive" with "Adding", "Non-Additive" with "Grouping"
  ([#983](https://github.com/open-telemetry/opentelemetry-specification/pull/983)
- Move active span interaction in the Trace API to a separate class
  ([#923](https://github.com/open-telemetry/opentelemetry-specification/pull/923))
- Metrics SDK: Specify LastValue default aggregation for ValueObserver
  ([#984](https://github.com/open-telemetry/opentelemetry-specification/pull/984)
- Metrics SDK: Specify TBD default aggregation for ValueRecorder
  ([#984](https://github.com/open-telemetry/opentelemetry-specification/pull/984)
- Trace SDK: Sampler.ShouldSample gets parent Context instead of SpanContext
  ([#881](https://github.com/open-telemetry/opentelemetry-specification/pull/881))
- SDK: Specify known values, as well as basic error handling for OTEL_PROPAGATORS.
  ([#962](https://github.com/open-telemetry/opentelemetry-specification/pull/962))
  ([#995](https://github.com/open-telemetry/opentelemetry-specification/pull/995))
- SDK: Specify when to generate new IDs with sampling
  ([#1225](https://github.com/open-telemetry/opentelemetry-specification/pull/1225))
- Remove custom header name for Baggage, use official header
  ([#993](https://github.com/open-telemetry/opentelemetry-specification/pull/993))
- Trace API: Clarifications for `Span.End`, e.g. IsRecording becomes false after End
  ([#1011](https://github.com/open-telemetry/opentelemetry-specification/pull/1011))
- Update semantic conventions for gRPC for new Span Status
  ([#1156](https://github.com/open-telemetry/opentelemetry-specification/pull/1156))

## v0.6.0 (2020-07-01)

New:

- Add span attribute to indicate cold starts of Function as a Service executions
  ([#650](https://github.com/open-telemetry/opentelemetry-specification/pull/650))
- Add conventions for naming of exporter packages
  ([#629](https://github.com/open-telemetry/opentelemetry-specification/pull/629))
- Add semantic conventions for container id
  ([#673](https://github.com/open-telemetry/opentelemetry-specification/pull/673))
- Add semantic conventions for HTTP content length
  ([#641](https://github.com/open-telemetry/opentelemetry-specification/pull/641))
- Add semantic conventions for process resource
  ([#635](https://github.com/open-telemetry/opentelemetry-specification/pull/635))
- Add peer.service to provide a user-configured name for a remote service
  ([#652](https://github.com/open-telemetry/opentelemetry-specification/pull/652))

Updates:

- Improve root Span description
  ([#645](https://github.com/open-telemetry/opentelemetry-specification/pull/645))
- Extend semantic conventions for RPC and allow non-gRPC calls
  ([#604](https://github.com/open-telemetry/opentelemetry-specification/pull/604))
- Revise and extend semantic conventions for databases
  ([#575](https://github.com/open-telemetry/opentelemetry-specification/pull/575))
- Clarify Tracer vs TracerProvider in tracing API and SDK spec.
  ([#619](https://github.com/open-telemetry/opentelemetry-specification/pull/619))
  Most importantly:
  * Configuration should be stored not per Tracer but in the TracerProvider.
  * Active spans are not per Tracer.
- Do not set any value in Context upon failed extraction
  ([#671](https://github.com/open-telemetry/opentelemetry-specification/pull/671))
- Clarify semantic conventions around span start and end time
  ([#592](https://github.com/open-telemetry/opentelemetry-specification/pull/592))

## v0.5.0 (06-02-2020)

- Define Log Data Model.
- Remove SpanId from Sampler input.
- Clarify what it will mean for a vendor to "support OpenTelemetry".
- Clarify Tracers should reference an InstrumentationLibrary rather than a
  Resource.
- Replace ALWAYS_PARENT sampler with a composite ParentOrElse sampler.
- Incorporate old content on metrics calling conventions, label sets.
- Update api-metrics-user.md and api-metrics-meter.md with the latest metrics
  API.
- Normalize Instrumentation term for instrumentations.
- Change w3c correlation context to custom header.

## v0.4.0 (2020-05-12)

- [OTEP-83](https://github.com/open-telemetry/oteps/blob/main/text/0083-component.md)
  Introduce the notion of InstrumentationLibrary.
- [OTEP-88](https://github.com/open-telemetry/oteps/blob/main/text/metrics/0088-metric-instrument-optional-refinements.md)
  Metrics API instrument foundation.
- [OTEP-91](https://github.com/open-telemetry/oteps/blob/main/text/logs/0091-logs-vocabulary.md)
  Logs vocabulary.
- [OTEP-92](https://github.com/open-telemetry/oteps/blob/main/text/logs/0092-logs-vision.md)
  Logs Vision.
- [OTEP-90](https://github.com/open-telemetry/oteps/blob/main/text/metrics/0090-remove-labelset-from-metrics-api.md)
  Remove LabelSet from the metrics API.
- [OTEP-98](https://github.com/open-telemetry/oteps/blob/main/text/metrics/0098-metric-instruments-explained.md)
  Explain the metric instruments.
- [OTEP-99](https://github.com/open-telemetry/oteps/blob/main/text/0099-otlp-http.md)
  OTLP/HTTP: HTTP Transport Extension for OTLP.
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

## v0.3.0 (2020-02-21)

- [OTEP-0059](https://github.com/open-telemetry/oteps/blob/main/text/trace/0059-otlp-trace-data-format.md)
  Add OTLP Trace Data Format specification.
- [OTEP-0066](https://github.com/open-telemetry/oteps/blob/main/text/0066-separate-context-propagation.md)
  Separate Layer for Context Propagation.
- [OTEP-0070](https://github.com/open-telemetry/oteps/blob/main/text/metrics/0070-metric-bound-instrument.md)
  Rename metric instrument "Handles" to "Bound Instruments".
- [OTEP-0072](https://github.com/open-telemetry/oteps/blob/main/text/metrics/0072-metric-observer.md)
  Metric Observer instrument specification (refinement).
- [OTEP-0080](https://github.com/open-telemetry/oteps/blob/main/text/metrics/0080-remove-metric-gauge.md)
  Remove the Metric Gauge instrument, recommend use of other instruments.
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

## v0.2.0 (2019-10-22)

- [OTEP-0001](https://github.com/open-telemetry/oteps/blob/main/text/0001-telemetry-without-manual-instrumentation.md)
  Added Auto-Instrumentation.
- [OTEP-0002](https://github.com/open-telemetry/oteps/blob/main/text/trace/0002-remove-spandata.md):
  Removed SpanData interface in favor of Span Start and End options.
- [OTEP-0003](https://github.com/open-telemetry/oteps/blob/main/text/metrics/0003-measure-metric-type.md)
  Consolidatesd pre-aggregated and raw metrics APIs.
- [OTEP-0008](https://github.com/open-telemetry/oteps/blob/main/text/metrics/0008-metric-observer.md)
  Added Metrics Observers API.
- [OTEP-0009](https://github.com/open-telemetry/oteps/blob/main/text/metrics/0009-metric-handles.md)
  Added Metrics Handle API.
- [OTEP-0010](https://github.com/open-telemetry/oteps/blob/main/text/metrics/0010-cumulative-to-counter.md)
  Rename "Cumulative" to "Counter" in the Metrics API.
- [OTEP-006](https://github.com/open-telemetry/oteps/blob/main/text/trace/0006-sampling.md)
  Moved sampling from the API tp the SDK.
- [OTEP-0007](https://github.com/open-telemetry/oteps/blob/main/text/0007-no-out-of-band-reporting.md)
  Moved support for out-of-band telemetry from the API to the SDK.
- [OTEP-0016](https://github.com/open-telemetry/oteps/blob/main/text/0016-named-tracers.md)
  Added named providers for Tracers and Meters.
- Added design goals and requirements for a telemetry data exchange protocol.
- Added a Span Processor interface for intercepting span start and end
  invocations.
- Added a Span Exporter interface for processing batches of spans.
- Replaced DistributedContext.GetIterator with GetEntries.
- Added clarifications and adjustments to improve cross-language applicability.
- Added a specification for SDK configuration.

## v0.1.0 (2019-06-21)

- Added API proposal for the converged OpenTracing/OpenCensus project is
  complete.
