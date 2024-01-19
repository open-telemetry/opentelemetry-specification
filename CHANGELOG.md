# Changelog

Please update changelog as part of any significant pull request. Place short
description of your change into "Unreleased" section. As part of release process
content of "Unreleased" section content will generate release notes for the
release.

## Unreleased

### Context

### Traces

### Metrics

- Add name suggestion for option to apply resource attributes as metric attributes in Prometheus exporter.
  ([#3837](https://github.com/open-telemetry/opentelemetry-specification/pull/3837))

### Logs

### Events

### Resource

### OpenTelemetry Protocol

### Compatibility

### SDK Configuration

### Common

### Supplementary Guidelines

## v1.32.0 (2024-04-11)

### Context

- No changes.

### Traces

- Remove the Jaeger Exporter.
  ([#3964](https://github.com/open-telemetry/opentelemetry-specification/pull/3964))

### Metrics

- Clarify that exemplar reservoir default may change in a minor version.
  ([#3943](https://github.com/open-telemetry/opentelemetry-specification/pull/3943))
- Add option to disable target info metric to Prometheus exporters.
  ([#3872](https://github.com/open-telemetry/opentelemetry-specification/pull/3872))
- Add synchronous gauge entry to sum monotonic table.
  ([#3977](https://github.com/open-telemetry/opentelemetry-specification/pull/3977))

### Logs

- Refine description of Instrumentation Scope.
  ([#3855](https://github.com/open-telemetry/opentelemetry-specification/pull/3855))
- Clarify that `ReadableLogRecord` and `ReadWriteLogRecord` can be represented using a single type.
  ([#3898](https://github.com/open-telemetry/opentelemetry-specification/pull/3898))
- Fix what can be modified via `ReadWriteLogRecord`.
  ([#3907](https://github.com/open-telemetry/opentelemetry-specification/pull/3907))

### Events

- No changes.

### Resource

- No changes.

### OpenTelemetry Protocol

- No changes.

### Compatibility

- Prometheus compatibility: Clarify naming of the target info metric, and differences between various Prometheus formats.
  ([#3871](https://github.com/open-telemetry/opentelemetry-specification/pull/3871))
- Prometheus compatibility: Clarify that the service triplet is required to be unique by semantic conventions.
  ([#3945](https://github.com/open-telemetry/opentelemetry-specification/pull/3945))
- Prometheus: represent Prometheus Info, StateSet and Unknown-typed metrics in OTLP.
  ([#3868](https://github.com/open-telemetry/opentelemetry-specification/pull/3868))
- Update and reorganize the prometheus sdk exporter specification.
  ([#3872](https://github.com/open-telemetry/opentelemetry-specification/pull/3872))

### SDK Configuration

- Define OTEL_EXPERIMENTAL_CONFIG_FILE to ignore other env vars, add env var substitution default syntax.
  ([#3948](https://github.com/open-telemetry/opentelemetry-specification/pull/3948))
- Clarify environment variable substitution is not recursive
  ([#3913](https://github.com/open-telemetry/opentelemetry-specification/pull/3913))
- Allow `env:` prefix in environment variable substitution syntax.
  ([#3974](https://github.com/open-telemetry/opentelemetry-specification/pull/3974))
- Add simple scope configuration to Tracer, Meter, Logger (experimental).
  ([#3877](https://github.com/open-telemetry/opentelemetry-specification/pull/3877))

### Common

- No changes.

### Supplementary Guidelines

- No changes.

## v1.31.0 (2024-03-13)

### Context

- Specify allowed characters for Baggage keys and values.
  ([#3801](https://github.com/open-telemetry/opentelemetry-specification/pull/3801))

### Traces

- Mark the AddLink() operation as stable.
  ([#3887](https://github.com/open-telemetry/opentelemetry-specification/pull/3887))

### Metrics

- Formalize the interaction between cardinality limit and overflow attribute.
  ([#3912](https://github.com/open-telemetry/opentelemetry-specification/pull/3912))

### Logs

- Fix: remove `name` from LogRecord example in the File Exporter example.
  ([#3886](https://github.com/open-telemetry/opentelemetry-specification/pull/3886))
- Remove implementation detail from Logs Bridge API.
  ([#3884](https://github.com/open-telemetry/opentelemetry-specification/pull/3884))
- Clarify that logs attributes are a superset of standard attributes.
  ([#3852](https://github.com/open-telemetry/opentelemetry-specification/pull/3852))
- Add support for empty values.
  ([#3853](https://github.com/open-telemetry/opentelemetry-specification/pull/3853))
- Mark standard output log record exporter as stable.
  ([#3922](https://github.com/open-telemetry/opentelemetry-specification/pull/3922))

### Events

- Add Provider to the Event API.
  ([#3878](https://github.com/open-telemetry/opentelemetry-specification/pull/3878))

### Resource

- No changes.

### OpenTelemetry Protocol

- No changes.

### Compatibility

- No changes.

### SDK Configuration

- No changes.

### Common

- Prohibit attribute value from evolving to contain complex types.
  ([#3858](https://github.com/open-telemetry/opentelemetry-specification/pull/3858))
- Tighten stability requirements for well-known attribute values.
  ([#3879](https://github.com/open-telemetry/opentelemetry-specification/pull/3879))

### Supplementary Guidelines

- No changes.

## v1.30.0 (2024-02-15)

### Context

- No changes.

### Traces

- No changes.

### Metrics

- Clarify metric view measurement processing.
  ([#3842](https://github.com/open-telemetry/opentelemetry-specification/pull/3842))
- Expose `ExemplarReservoir` as configuration parameter for views.
  Remove `ExemplarFilter` as an interface, now it is only configuration
  parameter.
  ([#3820](https://github.com/open-telemetry/opentelemetry-specification/pull/3820))

### Logs

- Fix `Resource` field type in Logs Data Model.
  ([#3826](https://github.com/open-telemetry/opentelemetry-specification/pull/3826))
- Remove confusing description from `Body` field in Logs Data Model to make it clear the Bridge API must support a structured body.
  ([#3827](https://github.com/open-telemetry/opentelemetry-specification/pull/3827))
- Deconstruct number scalar type to double and signed integer.
  ([#3854](https://github.com/open-telemetry/opentelemetry-specification/pull/3854))
- Remove use of Object-Oriented term `class` in log signal.
  ([#3882](https://github.com/open-telemetry/opentelemetry-specification/pull/3882))

### Resource

- No changes.

### OpenTelemetry Protocol

- Use `TracesData`, `MetricsData` and `LogsData` proto messages for file exporter.
  ([#3809](https://github.com/open-telemetry/opentelemetry-specification/pull/3809))

### Compatibility

- No changes.

### SDK Configuration

- Add file configuration section to spec compliance matrix.
  ([#3804](https://github.com/open-telemetry/opentelemetry-specification/pull/3804))
- Define mechanism for SDK extension components.
  ([#3802](https://github.com/open-telemetry/opentelemetry-specification/pull/3802))

### Common

- No changes.

### Supplementary Guidelines

- No changes.

## v1.29.0 (2024-01-10)

### Context & Baggage

- Align definition of Baggage with W3C Specification.
  ([#3800](https://github.com/open-telemetry/opentelemetry-specification/pull/3800))

### Traces

- Update OpenTelemetry to Zipkin Transformation to handle attributes from older semantic conventions in a backwards compatible way.
  ([#3794](https://github.com/open-telemetry/opentelemetry-specification/pull/3794))

### Metrics

- Define experimental MetricFilter as a mechanism to filter collected metrics by the MetricReader
  ([#3566](https://github.com/open-telemetry/opentelemetry-specification/pull/3566))
- Add optional configuration for Prometheus exporters to optionally remove unit and type suffixes.
  ([#3777](https://github.com/open-telemetry/opentelemetry-specification/pull/3777))
- Add optional configuration for Prometheus exporters to optionally drop `otel_scope_info` metric.
  ([#3796](https://github.com/open-telemetry/opentelemetry-specification/pull/3796))

### Logs

### Resource

### OpenTelemetry Protocol

### Compatibility

### SDK Configuration

- Define file configuration file format and env var substitution
  ([#3744](https://github.com/open-telemetry/opentelemetry-specification/pull/3744))

### Common

- Clarify that attribute keys are case-sensitive.
  ([#3784](https://github.com/open-telemetry/opentelemetry-specification/pull/3784))

### Supplementary Guidelines

## v1.28.0 (2023-12-07)

### Context

- No changes.

### Traces

- Stabilize how exceptions are recorded using the Trace SDK.
  ([#3769](https://github.com/open-telemetry/opentelemetry-specification/pull/3769))
- Add definition for standard output span exporter.
  ([#3740](https://github.com/open-telemetry/opentelemetry-specification/pull/3740))

### Metrics

- Add optional configuration for Prometheus exporters to promote resource attributes to metric attributes
  ([#3761](https://github.com/open-telemetry/opentelemetry-specification/pull/3761))
- Clarifications and flexibility in Exemplar speicification.
  ([#3760](https://github.com/open-telemetry/opentelemetry-specification/pull/3760))

### Logs

- Add definition for standard output log record exporter.
  ([#3741](https://github.com/open-telemetry/opentelemetry-specification/pull/3741))
- BREAKING: Change `event.name` definition to include `namespace` and removed `event.domain` from log event attributes.
  ([#3749](https://github.com/open-telemetry/opentelemetry-specification/pull/3749))
- BREAKING: Refine the arguments of the emit Event API. Instead of accepting
  a `LogRecord`, the individual arguments are enumerated along with the
  implementation requirements on how those arguments map to `LogRecord`.
  ([#3772](https://github.com/open-telemetry/opentelemetry-specification/pull/3772))

### Resource

- No changes.

### OpenTelemetry Protocol

- Clarify HTTP endpoint configuration option handling.
  ([#3739](https://github.com/open-telemetry/opentelemetry-specification/pull/3739))

### Compatibility

- No changes.

### SDK Configuration

- Add `console` as an exporter type that is supported via environment variable configuration.
  ([#3742](https://github.com/open-telemetry/opentelemetry-specification/pull/3742))

### Common

- No changes.

### Supplementary Guidelines

- No changes.

## v1.27.0 (2023-11-08)

### Context

- No changes.

### Traces

- Add a new AddLink() operation to Span (experimental).
  ([#3678](https://github.com/open-telemetry/opentelemetry-specification/pull/3678))

### Metrics

- No changes.

### Logs

- No changes.

### Resource

- No changes.

### OpenTelemetry Protocol

- New exporter implementations do not need to support
  `OTEL_EXPORTER_OTLP_SPAN_INSECURE` and `OTEL_EXPORTER_OTLP_METRIC_INSECURE`.
  ([#3719](https://github.com/open-telemetry/opentelemetry-specification/pull/3719))

### Compatibility

- No changes.

### SDK Configuration

- Define file configuration parse and create operations.
  ([#3437](https://github.com/open-telemetry/opentelemetry-specification/pull/3437))
- Add environment variable implementation guidelines.
  ([#3738](https://github.com/open-telemetry/opentelemetry-specification/pull/3738))

### Common

- Rename/replace `(client|server).socket.(address|port)` attributes with `network.(peer|local).(address|port)`.
  ([#3713](https://github.com/open-telemetry/opentelemetry-specification/pull/3713))

### Supplementary Guidelines

- No changes.

## v1.26.0 (2023-10-10)

### Context

- No changes.

### Traces

- `ParentBased` sampler is a decorator (not a composite).
  ([#3706](https://github.com/open-telemetry/opentelemetry-specification/pull/3706))

### Metrics

- Consistently use "advisory parameters" instead of "advice parameters".
  ([#3693](https://github.com/open-telemetry/opentelemetry-specification/pull/3693))
- Stabilize `ExplicitBucketBoundaries` instrument advisory parameter.
  ([#3694](https://github.com/open-telemetry/opentelemetry-specification/pull/3694))

### Logs

- Update two apache access logs mappings.
  ([#3712](https://github.com/open-telemetry/opentelemetry-specification/pull/3712))

### Resource

- No changes.

### OpenTelemetry Protocol

- No changes.

### Compatibility

- Prometheus exporters omit empty resources and scopes without attributes.
  ([#3660](https://github.com/open-telemetry/opentelemetry-specification/pull/3660))

### SDK Configuration

- Fix description of OTEL_ATTRIBUTE_COUNT_LIMIT
  ([#3714](https://github.com/open-telemetry/opentelemetry-specification/pull/3714))

### Common

- Add upgrading and version management documentation
  ([#3695](https://github.com/open-telemetry/opentelemetry-specification/pull/3695))

### Supplementary Guidelines

- No changes.

## v1.25.0 (2023-09-13)

### Context

- No changes.

### Traces

- No changes.

### Metrics

- Increase metric name maximum length from 63 to 255 characters.
  ([#3648](https://github.com/open-telemetry/opentelemetry-specification/pull/3648))
- MetricReader.Collect ignores Resource from MetricProducer.Produce.
  ([#3636](https://github.com/open-telemetry/opentelemetry-specification/pull/3636))
- Attribute sets not observed during async callbacks are not exported.
  ([#3242](https://github.com/open-telemetry/opentelemetry-specification/pull/3242))
- Promote MetricProducer specification to feature-freeze.
  ([#3655](https://github.com/open-telemetry/opentelemetry-specification/pull/3655))
- Add synchronous gauge instrument, clarify temporality selection influence on
  metric point persistence.
  ([#3540](https://github.com/open-telemetry/opentelemetry-specification/pull/3540))
- Clarify that advice is non-identifying.
  ([#3661](https://github.com/open-telemetry/opentelemetry-specification/pull/3661))
- Define the default size of the `SimpleFixedSizeExemplarReservoir` to be `1`.
  ([#3670](https://github.com/open-telemetry/opentelemetry-specification/pull/3670))
- Rename "advice" to "advisory parameters".
  ([#3662](https://github.com/open-telemetry/opentelemetry-specification/pull/3662))
- Clarify the minimal implementation of a `View`'s `attribute_keys` is an allow-list.
  ([#3680](https://github.com/open-telemetry/opentelemetry-specification/pull/3680))
- Add "/" to valid characters for instrument names
  ([#3684](https://github.com/open-telemetry/opentelemetry-specification/pull/3684))
- Stabilize the `MetricProducer`.
  ([#3685](https://github.com/open-telemetry/opentelemetry-specification/pull/3685))

### Logs

- Update GCP data model to use `TraceFlags` instead of
  `gcp.trace_sampled`. ([#3629](https://github.com/open-telemetry/opentelemetry-specification/pull/3629))

### Resource

- No changes.

### OpenTelemetry Protocol

- Fix and clarify definition of "transient error" in the OTLP exporter specification.
  ([#3653](https://github.com/open-telemetry/opentelemetry-specification/pull/3653))

### Compatibility

- OpenTracing Shim: Allow invalid but sampled SpanContext to be returned.
  ([#3471](https://github.com/open-telemetry/opentelemetry-specification/pull/3471))
- Prometheus: Allow changing metric names by default when translating from Prometheus to OpenTelemetry.
  ([#3679](https://github.com/open-telemetry/opentelemetry-specification/pull/3679))

### SDK Configuration

- No changes.

### Common

- No changes.

### Supplemenatary Guidelines

- No changes.

## v1.24.0 (2023-08-10)

### Context

- No changes.

### Traces

- No changes.

### Metrics

- Specify how to handle instrument name conflicts.
  ([#3626](https://github.com/open-telemetry/opentelemetry-specification/pull/3626))
- Add experimental metric attributes advice API.
  ([#3546](https://github.com/open-telemetry/opentelemetry-specification/pull/3546))
- Revise the exemplar default reservoirs.
  ([#3627](https://github.com/open-telemetry/opentelemetry-specification/pull/3627))
- Mark the default aggregation cardinality Experimental in MetricReader.
  ([#3619](https://github.com/open-telemetry/opentelemetry-specification/pull/3619))
- Mark Metric No-Op API as stable.
  ([#3642](https://github.com/open-telemetry/opentelemetry-specification/pull/3642))
- MetricProducers are provided as config to MetricReaders instead of through a RegisterProducer operation.
  ([#3613](https://github.com/open-telemetry/opentelemetry-specification/pull/3613))
- Refine `MetricProvider.ForceFlush` and define `ForceFlush` for periodic exporting MetricReader.
  ([#3563](https://github.com/open-telemetry/opentelemetry-specification/pull/3563))

### Logs

- Clarify how log appender use Scope name and attributes.
  ([#3583](https://github.com/open-telemetry/opentelemetry-specification/pull/3583))
- Mark No-Op Logs Bridge API as stable.
  ([#3642](https://github.com/open-telemetry/opentelemetry-specification/pull/3642))

### Resource

- No changes.

### Compatibility

- Prometheus exporters SHOULD provide configuration to disable the addition of `_total` suffixes.
  ([#3590](https://github.com/open-telemetry/opentelemetry-specification/pull/3590))

### SDK Configuration

- No changes.

### Common

- No changes.

### Supplemenatary Guidelines

- No changes.

## v1.23.0 (2023-07-12)

### Context

- No changes.

### Traces

- Refine SDK TracerProvider configuration section.
  ([#3559](https://github.com/open-telemetry/opentelemetry-specification/pull/3559))
- Make SDK Tracer Creation more normative.
  ([#3529](https://github.com/open-telemetry/opentelemetry-specification/pull/3529))

### Metrics

- Refine SDK MeterProvider configuration section.
  ([#3522](https://github.com/open-telemetry/opentelemetry-specification/pull/3522))
- Clarify metric view requirements and recommendations.
  ([#3524](https://github.com/open-telemetry/opentelemetry-specification/pull/3524))
- Change the view name to be the view's stream configuration name.
  ([#3524](https://github.com/open-telemetry/opentelemetry-specification/pull/3524))
- Make SDK Meter Creation more normative.
  ([#3529](https://github.com/open-telemetry/opentelemetry-specification/pull/3529))
- Clarify duplicate instrument registration scope to be a MeterProvider.
  ([#3538](https://github.com/open-telemetry/opentelemetry-specification/pull/3538))
- Clarify identical instrument definition for SDK.
  ([#3585](https://github.com/open-telemetry/opentelemetry-specification/pull/3585))

### Logs

- Refine SDK LoggerProvider configuration section.
  ([#3559](https://github.com/open-telemetry/opentelemetry-specification/pull/3559))
- Make SDK Logger Creation more normative.
  ([#3529](https://github.com/open-telemetry/opentelemetry-specification/pull/3529))

### Resource

- No changes.

### Compatibility

- NOTICE: Remove the Jaeger Exporter
  ([#3567](https://github.com/open-telemetry/opentelemetry-specification/pull/3567))
- Prometheus: Do not add `_total` suffix if the metric already ends in `_total`.
  ([#3581](https://github.com/open-telemetry/opentelemetry-specification/pull/3581))
- Prometheus type and unit suffixes are not trimmed by default.
  ([#3580](https://github.com/open-telemetry/opentelemetry-specification/pull/3580))

### SDK Configuration

- Extract Exemplar section and mark it as Experimental.
  ([#3533](https://github.com/open-telemetry/opentelemetry-specification/pull/3533))

### Common

- No changes.

### Supplemenatary Guidelines

- No changes.

## v1.22.0 (2023-06-09)

### Context

- No changes.

### Traces

- No changes.

### Metrics

- Make recommendation to reserve aggregator normative.
  ([#3526](https://github.com/open-telemetry/opentelemetry-specification/pull/3526))

### Logs

- No changes.

### Resource

- No changes.

### Compatibility

- No changes.

### OpenTelemetry Protocol

- Move OTLP specification to github.com/open-telemetry/opentelemetry-proto.
  ([#3454](https://github.com/open-telemetry/opentelemetry-specification/pull/3454))

### SDK Configuration

- No changes.

### Telemetry Schemas

- No changes.

### Common

- Explain why custom attributes are not recommended to be placed in OTel
  namespaces.
  ([#3507](https://github.com/open-telemetry/opentelemetry-specification/pull/3507))

### Supplemenatary Guidelines

- No changes.

## v1.21.0 (2023-05-09)

### Context

- No changes.

### Traces

- No changes.

### Metrics

- Add experimental histogram advice API.
  ([#3216](https://github.com/open-telemetry/opentelemetry-specification/pull/3216))
- Recommended non-prefixed units for metric instrument semantic conventions.
  ([#3312](https://github.com/open-telemetry/opentelemetry-specification/pull/3312))
- Recommended cardinality limits to protect metrics pipelines against
  excessive data production from a single instrument.
  ([#2960](https://github.com/open-telemetry/opentelemetry-specification/pull/2960))
- Specify second unit (`s`) and advice bucket boundaries of `[]`
  for `process.runtime.jvm.gc.duration`.
  ([#3458](https://github.com/open-telemetry/opentelemetry-specification/pull/3458))
- Add links to the JMX APIs that are the JVM runtime metric sources.
  ([#3463](https://github.com/open-telemetry/opentelemetry-specification/pull/3463))

### Logs

- Clarify parameters for emitting a log record.
  ([#3345](https://github.com/open-telemetry/opentelemetry-specification/pull/3354))
- Drop logger include_trace_context parameter.
  ([#3397](https://github.com/open-telemetry/opentelemetry-specification/pull/3397))
- Clarify how ObservedTimestamp field is set if unspecified
  ([#3385](https://github.com/open-telemetry/opentelemetry-specification/pull/3385))
- Mark logs bridge API / SDK as stable.
  ([#3376](https://github.com/open-telemetry/opentelemetry-specification/pull/3376))
- Mark LogRecord Environment Variables as stable.
  ([#3449](https://github.com/open-telemetry/opentelemetry-specification/pull/3449))

### Resource

### Semantic Conventions

- The Semantic Conventions have moved to a separate repository
  [github.com/open-telemetry/semantic-conventions](https://github.com/open-telemetry/semantic-conventions).
  There will be no future semantic conventions release from this repository.
  ([#3489](https://github.com/open-telemetry/opentelemetry-specification/pull/3489))

### Compatibility

- Mark OpenCensus compatibility spec as stable
  ([#3425](https://github.com/open-telemetry/opentelemetry-specification/pull/3425))

### OpenTelemetry Protocol

- No changes.

### SDK Configuration

- Lay initial groundwork for file configuration
  ([#3360](https://github.com/open-telemetry/opentelemetry-specification/pull/3360))
- Move file configuration schema to `opentelemetry-configuration`.
  ([#3412](https://github.com/open-telemetry/opentelemetry-specification/pull/3412))
- Move `sdk-configuration.md` and `sdk-environment-variables.md`
  to `/specification/configuration/`.
  ([#3434](https://github.com/open-telemetry/opentelemetry-specification/pull/3434))

### Telemetry Schemas

- No changes.

### Common

- Add log entries to specification README.md contents.
  ([#3435](https://github.com/open-telemetry/opentelemetry-specification/pull/3435))

### Supplemenatary Guidelines

- Add guidance to use service-supported propagation formats as default for AWS SDK client calls.
  ([#3212](https://github.com/open-telemetry/opentelemetry-specification/pull/3212))

## v1.20.0 (2023-04-07)

### Context

- No changes.

### Traces

- Clarify required parent information in ReadableSpan. Technically a relaxation,
  but previously it was easy to overlook certain properties were required.
  [#3257](https://github.com/open-telemetry/opentelemetry-specification/pull/3257)
- Remove underspecified and unused Span decorator from Trace SDK.
  ([#3363](https://github.com/open-telemetry/opentelemetry-specification/pull/3363))

### Metrics

- Clarify that units should use UCUM case sensitive variant.
  ([#3306](https://github.com/open-telemetry/opentelemetry-specification/pull/3306))
- Remove No-Op instrument and Meter creation requirements.
  ([#3322](https://github.com/open-telemetry/opentelemetry-specification/pull/3322))
- Fixed attributes requirement level in semantic conventions for hardware metrics
  ([#3258](https://github.com/open-telemetry/opentelemetry-specification/pull/3258))

### Logs

- Update log readme "request context" to "trace context".
  ([#3332](https://github.com/open-telemetry/opentelemetry-specification/pull/3332))
- Remove log readme document status.
  ([#3334](https://github.com/open-telemetry/opentelemetry-specification/pull/3334))
- Break out compatibility document on recording trace context in non-OTLP Log Format
  ([#3331](https://github.com/open-telemetry/opentelemetry-specification/pull/3331))
- Ensure Logs Bridge API doesn't contain SDK implementation details
  ([#3275](https://github.com/open-telemetry/opentelemetry-specification/pull/3275))
- Add Log Bridge API artifact naming guidance
  ([#3346](https://github.com/open-telemetry/opentelemetry-specification/pull/3346))
- Add log appender / bridge to glossary.
  ([#3335](https://github.com/open-telemetry/opentelemetry-specification/pull/3335))

### Resource

- No changes.

### Semantic Conventions

- Clarify that attribute requirement levels apply to the instrumentation library
  ([#3289](https://github.com/open-telemetry/opentelemetry-specification/pull/3289))
- Fix grammatical number of metric units.
  ([#3298](https://github.com/open-telemetry/opentelemetry-specification/pull/3298))
- Rename `net.app.protocol.(name|version)` to `net.protocol.(name|version)`
  ([#3272](https://github.com/open-telemetry/opentelemetry-specification/pull/3272))
- Replace `http.flavor` with `net.protocol.(name|version)`
  ([#3272](https://github.com/open-telemetry/opentelemetry-specification/pull/3272))
- Metric requirement levels are now stable
  ([#3271](https://github.com/open-telemetry/opentelemetry-specification/pull/3271))
- BREAKING: remove `messaging.destination.kind` and `messaging.source.kind`.
  ([#3214](https://github.com/open-telemetry/opentelemetry-specification/pull/3214),
  [#3348](https://github.com/open-telemetry/opentelemetry-specification/pull/3348))
- Define attributes collected for `cosmosdb` by Cosmos DB SDK
  ([#3097](https://github.com/open-telemetry/opentelemetry-specification/pull/3097))
- Clarify stability requirements of semantic conventions
  ([#3225](https://github.com/open-telemetry/opentelemetry-specification/pull/3225))
- BREAKING: Change span statuses for gRPC server spans.
  ([#3333](https://github.com/open-telemetry/opentelemetry-specification/pull/3333))
- Stabilize key components of `service.*` and `telemetry.sdk.*` resource
  semantic conventions.
  ([#3202](https://github.com/open-telemetry/opentelemetry-specification/pull/3202))
- Fixed attributes requirement level in semantic conventions for hardware metrics
  ([#3258](https://github.com/open-telemetry/opentelemetry-specification/pull/3258))
- Added AWS S3 semantic conventions.
  ([#3251](https://github.com/open-telemetry/opentelemetry-specification/pull/3251))
- Fix units in the Kafka metric semantic conventions.
  ([#3300](https://github.com/open-telemetry/opentelemetry-specification/pull/3300))
- Add Trino to Database specific conventions
  ([#3347](https://github.com/open-telemetry/opentelemetry-specification/pull/3347))
- Change `db.statement` to only be collected if there is sanitization.
  ([#3127](https://github.com/open-telemetry/opentelemetry-specification/pull/3127))
- BREAKING: Remove `http.status_code` attribute from the
  `http.server.active_requests` metric.
  ([#3366](https://github.com/open-telemetry/opentelemetry-specification/pull/3366))
- Mark attribute requirement levels as stable
  ([#3368](https://github.com/open-telemetry/opentelemetry-specification/pull/3368))

### Compatibility

- No changes.

### OpenTelemetry Protocol

- Declare OTLP stable.
  ([#3274](https://github.com/open-telemetry/opentelemetry-specification/pull/3274))

### SDK Configuration

- No changes.

### Telemetry Schemas

- No changes.

### Common

- No changes.

## v1.19.0 (2023-03-06)

### Context

- No changes.

### Traces

- No changes.

### Metrics

- Add unit to View's Instrument selection criteria.
  ([#3184](https://github.com/open-telemetry/opentelemetry-specification/pull/3184))
- Add metric requirement levels "Required", "Recommended", and "Opt-In".
  ([#3237](https://github.com/open-telemetry/opentelemetry-specification/pull/3237))

### Logs

- Rename Logs API to Logs Bridge API to prevent confusion.
  ([#3197](https://github.com/open-telemetry/opentelemetry-specification/pull/3197))
- Move event language from log README to event-api.
  ([#3252](https://github.com/open-telemetry/opentelemetry-specification/pull/3252))

### Resource

- Clarify how to collect `host.id` for non-containerized systems.
  ([#3173](https://github.com/open-telemetry/opentelemetry-specification/pull/3173))

### Semantic Conventions

- Move X-Ray Env Variable propagation to span link instead of parent for AWS Lambda.
  ([#3166](https://github.com/open-telemetry/opentelemetry-specification/pull/3166))
- Add heroku resource semantic conventions.
  [#3075](https://github.com/open-telemetry/opentelemetry-specification/pull/3075)
- BREAKING: Rename faas.execution to faas.invocation_id
  ([#3209](https://github.com/open-telemetry/opentelemetry-specification/pull/3209))
- BREAKING: Change faas.max_memory units to Bytes instead of MB
  ([#3209](https://github.com/open-telemetry/opentelemetry-specification/pull/3209))
- BREAKING: Expand scope of faas.id to cloud.resource_id
  ([#3188](https://github.com/open-telemetry/opentelemetry-specification/pull/3188))
- Add Connect RPC specific conventions
  ([#3116](https://github.com/open-telemetry/opentelemetry-specification/pull/3116))
- Rename JVM metric attribute value from `nonheap` to `non_heap`
  ([#3250](https://github.com/open-telemetry/opentelemetry-specification/pull/3250))
- Mark the attribute naming guidelines in the specification as stable.
  ([#3220](https://github.com/open-telemetry/opentelemetry-specification/pull/3220))
- Mark telemetry schema readme stable.
  ([#3221](https://github.com/open-telemetry/opentelemetry-specification/pull/3221))
- Remove mention of `net.transport` from HTTP semantic conventions
  ([#3244](https://github.com/open-telemetry/opentelemetry-specification/pull/3244))
- Clarifies that if an HTTP client request is explicitly made to an IP address,
  e.g. `http://x.x.x.x:8080`, then `net.peer.name` SHOULD be the IP address `x.x.x.x`
  ([#3276](https://github.com/open-telemetry/opentelemetry-specification/pull/3276))
- Mark `net.sock.host.port` as conditionally required.
  ([#3246](https://github.com/open-telemetry/opentelemetry-specification/pull/3246))
- Rename Optional attribute requirement level to Opt-In.
  ([#3228](https://github.com/open-telemetry/opentelemetry-specification/pull/3228))
- Rename `http.user_agent` to `user_agent.original`.
  ([#3190](https://github.com/open-telemetry/opentelemetry-specification/pull/3190))
- Expand the declaration of `pool.name`.
  ([#3050](https://github.com/open-telemetry/opentelemetry-specification/pull/3050))

### Compatibility

- Update Zipkin remoteEndpoint preferences.
  ([#3087](https://github.com/open-telemetry/opentelemetry-specification/pull/3087))

### OpenTelemetry Protocol

- Declare OTLP/JSON Stable.
  ([#2930](https://github.com/open-telemetry/opentelemetry-specification/pull/2930))

### SDK Configuration

- No changes.

### Telemetry Schemas

- No changes.

### Common

- No changes.

## v1.18.0 (2023-02-09)

### Context

- No changes.

### Traces

- Clarify guidance regarding excessive logging when attributes are dropped
  or truncated.
  ([#3151](https://github.com/open-telemetry/opentelemetry-specification/pull/3151))

### Metrics

- No changes.

### Logs

- Define BatchLogRecordProcessor default configuration values.
  ([#3002](https://github.com/open-telemetry/opentelemetry-specification/pull/3002))
- Clarify guidance regarding excessive logging when attributes are dropped
  or truncated.
  ([#3151](https://github.com/open-telemetry/opentelemetry-specification/pull/3151))

### Resource

- No changes.

### Semantic Conventions

- Add Cloud Spanner and Microsoft SQL Server Compact to db.system semantic conventions
  ([#3105](https://github.com/open-telemetry/opentelemetry-specification/pull/3105)).
- Enable semantic convention tooling for metrics in spec
  ([#3119](https://github.com/open-telemetry/opentelemetry-specification/pull/3119))
- Rename google openshift platform attribute from `google_cloud_openshift` to `gcp_openshift`
  to match the existing `cloud.provider` prefix.
  ([#3095](https://github.com/open-telemetry/opentelemetry-specification/pull/3095))
- Changes http server span names from `{http.route}` to `{http.method} {http.route}`
  (when route is available), and from `HTTP {http.method}` to `{http.method}` (when
  route is not available).
  Changes http client span names from `HTTP {http.method}` to `{http.method}`.
  ([#3165](https://github.com/open-telemetry/opentelemetry-specification/pull/3165))
- Mark `http.server.duration` and `http.client.duration` metrics as required, and mark
  all other HTTP metrics as optional.
  [#3158](https://github.com/open-telemetry/opentelemetry-specification/pull/3158)
- Add `net.host.port` to `http.server.active_requests` metrics attributes.
  [#3158](https://github.com/open-telemetry/opentelemetry-specification/pull/3158)
- `http.route` SHOULD contain the "application root" if there is one.
  ([#3164](https://github.com/open-telemetry/opentelemetry-specification/pull/3164))

### Compatibility

- Add condition with sum and count for Prometheus summaries
  ([3059](https://github.com/open-telemetry/opentelemetry-specification/pull/3059)).
- Clarify prometheus unit conversions
  ([#3066](https://github.com/open-telemetry/opentelemetry-specification/pull/3066)).
- Define conversion mapping from OTel Exponential Histograms to Prometheus Native
  Histograms.
  ([#3079](https://github.com/open-telemetry/opentelemetry-specification/pull/3079))
- Fix Prometheus histogram metric suffixes. Bucket series end in `_bucket`
  ([#3018](https://github.com/open-telemetry/opentelemetry-specification/pull/3018)).

### OpenTelemetry Protocol

- No changes.

### SDK Configuration

- Add log-specific attribute limit configuration and clarify that general
  attribute limit configuration also apply to log records
  ([#2861](https://github.com/open-telemetry/opentelemetry-specification/pull/2861)).

### Telemetry Schemas

- No changes.

### Common

- No changes.

## v1.17.0 (2023-01-17)

### Context

- No changes.

### Traces

- Clarify that the BatchSpanProcessor should export batches when the queue reaches the batch size
  ([#3024](https://github.com/open-telemetry/opentelemetry-specification/pull/3024))
- Deprecate jaeger exporter, scheduled for spec removal in July 2023.
  [#2858](https://github.com/open-telemetry/opentelemetry-specification/pull/2858)

### Metrics

- Rename built-in ExemplarFilters to AlwaysOn, AlwaysOff and TraceBased.
  ([#2919](https://github.com/open-telemetry/opentelemetry-specification/pull/2919))
- Add `MaxScale` config option to Exponential Bucket Histogram Aggregation.
  ([#3017](https://github.com/open-telemetry/opentelemetry-specification/pull/3017))
- Rename exponential bucket histogram aggregation to base 2 exponential histogram
  aggregation. Rename "OTEL_EXPORTER_OTLP_METRICS_DEFAULT_HISTOGRAM_AGGREGATION"
  value from "exponential_bucket_histogram" to
  "base2_exponential_bucket_histogram". Mark exponential histogram data model and
  base2 exponential histogram aggregation as stable.
  ([#3041](https://github.com/open-telemetry/opentelemetry-specification/pull/3041))

### Logs

- Clarify usage of log body for structured logs
  ([#3023](https://github.com/open-telemetry/opentelemetry-specification/pull/3023))
- Move appendices from Data Model to new Data Model Appendix document
  ([#3207](https://github.com/open-telemetry/opentelemetry-specification/pull/3207))

### Resource

- No changes.

### Semantic Conventions

- Clarify common HTTP attributes apply to both clients and servers
  ([#3044](https://github.com/open-telemetry/opentelemetry-specification/pull/3044))
- Add `code.lineno` source code attribute
  ([#3029](https://github.com/open-telemetry/opentelemetry-specification/pull/3029))
- Add ClickHouse to db.system semantic conventions
  ([#3011](https://github.com/open-telemetry/opentelemetry-specification/pull/3011))
- Refactor messaging attributes and per-message attributes in batching scenarios.
  ([#2957](https://github.com/open-telemetry/opentelemetry-specification/pull/2957)).
  BREAKING: rename `messaging.consumer_id` to `messaging.consumer.id`,
  `messaging.destination` to `messaging.destination.name`,
  `messaging.temp_destination` to `messaging.destination.temporary`,
  `messaging.destination_kind` to `messaging.destination.kind`,
  `messaging.message_id` to `messaging.message.id`,
  `messaging.protocol` to `net.app.protocol.name`,
  `messaging.protocol_version`, `net.app.protocol.version`,
  `messaging.conversation_id` to `messaging.message.conversation_id`,
  `messaging.message_payload_size_bytes` to `messaging.message.payload_size_bytes`,
  `messaging.message_payload_compressed_size_bytes` to `messaging.message.payload_compressed_size_bytes`,
  `messaging.rabbitmq.routing_key`: `messaging.rabbitmq.destination.routing_key`,
  `messaging.kafka.message_key` to `messaging.kafka.message.key`,
  `messaging.kafka.consumer_group` to `messaging.kafka.consumer.group`,
  `messaging.kafka.partition` to `messaging.kafka.destination.partition`,
  `messaging.kafka.tombstone` to `messaging.kafka.message.tombstone`,
  `messaging.rocketmq.message_type` to `messaging.rocketmq.message.type`,
  `messaging.rocketmq.message_tag` to `messaging.rocketmq.message.tag`,
  `messaging.rocketmq.message_keys` to `messaging.rocketmq.message.keys`;
  Removed `messaging.url`;
  Renamed `send` operation to `publish`;
  Split `destination` and `source` namespaces and clarify per-message attributes in batching scenarios.

### Compatibility

- Add Tracer.Close() to the OpenTracing Shim layer.
- Add OpenCensus migration guide and add BinaryPropagation as an option to gRPC
  instrumentation for OpenCensus compatibility
  ([#3015](https://github.com/open-telemetry/opentelemetry-specification/pull/3015)).

### OpenTelemetry Protocol

- Add table for OTLP/HTTP response code and client retry recommendation
  ([#3028](https://github.com/open-telemetry/opentelemetry-specification/pull/3028))
- Remove spaces from example exporter User-Agent header to conform to RFC7231 & RFC7230.
  [#3052](https://github.com/open-telemetry/opentelemetry-specification/pull/3052)

### SDK Configuration

- Rename knowns values for "OTEL_METRICS_EXEMPLAR_FILTER" to "always_on",
  "always_off" and "trace_based".
  ([#2919](https://github.com/open-telemetry/opentelemetry-specification/pull/2919))

### Telemetry Schemas

- No changes.

### Common

- No changes.

## v1.16.0 (2022-12-08)

### Context

- No changes.

### Traces

- No changes.

### Metrics

- Define Experimental MetricProducer as a third-party provider of metric data to MetricReaders.
  ([#2951](https://github.com/open-telemetry/opentelemetry-specification/pull/2951))
- Add OTLP exporter temporality preference named "LowMemory" which
  configures Synchronous Counter and Histogram instruments to use
  Delta aggregation temporality, which allows them to shed memory
  following a cardinality explosion, thus use less memory.
  ([#2961](https://github.com/open-telemetry/opentelemetry-specification/pull/2961))

### Logs

- Clarification on what an Event is, and what the event.domain and event.name attributes represent
  ([#2848](https://github.com/open-telemetry/opentelemetry-specification/pull/2848))
- Move `event.domain` from InstrumentationScope attributes to LogRecord
  attributes.
  ([#2940](https://github.com/open-telemetry/opentelemetry-specification/pull/2940))
- Split out Event API from Log API
  ([#2941](https://github.com/open-telemetry/opentelemetry-specification/pull/2941))
- Clarify data modification in `LogRecordProcessor`.
  ([#2969](https://github.com/open-telemetry/opentelemetry-specification/pull/2969))
- Make sure it is very clear we are not building a Logging API.
  ([#2966](https://github.com/open-telemetry/opentelemetry-specification/pull/2966))

### Resource

- Extend Cloud Platform Enum with OpenShift entry for all supported cloud providers.
  ([#2985](https://github.com/open-telemetry/opentelemetry-specification/pull/2985))

### Semantic Conventions

- Add `process.runtime.jvm.gc.duration` metric to semantic conventions.
  ([#2903](https://github.com/open-telemetry/opentelemetry-specification/pull/2903))
- Make http.status_code metric attribute an int.
  ([#2943](https://github.com/open-telemetry/opentelemetry-specification/pull/2943))
- Add IBM Cloud as a cloud provider.
  ([#2965](https://github.com/open-telemetry/opentelemetry-specification/pull/2965))
- Add semantic conventions for Feature Flags
  ([#2529](https://github.com/open-telemetry/opentelemetry-specification/pull/2529))
- Rename `rpc.request.metadata.<key>` and `rpc.response.metadata.<key>` to
  `rpc.grpc.request.metadata.<key>` and `rpc.grpc.response.metadata.<key>`
  ([#2981](https://github.com/open-telemetry/opentelemetry-specification/pull/2981))
- List the machine-id as potential source for a unique host.id
  ([#2978](https://github.com/open-telemetry/opentelemetry-specification/pull/2978))
- Add `messaging.kafka.message.offset` attribute.
  ([#2982](https://github.com/open-telemetry/opentelemetry-specification/pull/2982))
- Update hardware metrics to use `direction` as per general semantic conventions
  ([#2942](https://github.com/open-telemetry/opentelemetry-specification/pull/2942))

### Compatibility

- Add OpenCensus metric bridge specification.
  ([#2979](https://github.com/open-telemetry/opentelemetry-specification/pull/2979))

### OpenTelemetry Protocol

- No changes.

### SDK Configuration

- Specify handling of invalid numeric environment variables
  ([#2963](https://github.com/open-telemetry/opentelemetry-specification/pull/2963))

### Telemetry Schemas

- No changes.

### Common

- No changes.

## v1.15.0 (2022-11-09)

### Context

- No changes.

### Traces

- Rename `http.retry_count` to `http.resend_count` and clarify its meaning.
  ([#2743](https://github.com/open-telemetry/opentelemetry-specification/pull/2743))

### Metrics

- Handle duplicate description comments during Prometheus conversion.
  ([#2890](https://github.com/open-telemetry/opentelemetry-specification/pull/2890))
- Allow to configure min/max recording in the exponential histogram aggregation.
  ([#2904](https://github.com/open-telemetry/opentelemetry-specification/pull/2904))
- Add table of instrument additive property
  ([#2906](https://github.com/open-telemetry/opentelemetry-specification/pull/2906))

### Logs

- Add `Context` as argument to `LogRecordProcessor#onEmit`.
  ([#2927](https://github.com/open-telemetry/opentelemetry-specification/pull/2927))

### Resource

- No changes.

### Semantic Conventions

- Change to messaging.kafka.max.lag from UpDownCounter to Gauge (and rename it)
  ([#2837](https://github.com/open-telemetry/opentelemetry-specification/pull/2837))
- Add daemon attribute to jvm threads metric
  ([#2828](https://github.com/open-telemetry/opentelemetry-specification/pull/2828))
- Add gRPC request and response metadata semantic conventions
  ([#2874](https://github.com/open-telemetry/opentelemetry-specification/pull/2874))
- Add `process.paging.faults` metric to semantic conventions
  ([#2827](https://github.com/open-telemetry/opentelemetry-specification/pull/2827))
- Define semantic conventions yaml for non-otlp conventions
  ([#2850](https://github.com/open-telemetry/opentelemetry-specification/pull/2850))
- Add more semantic convetion attributes of Apache RocketMQ
  ([#2881](https://github.com/open-telemetry/opentelemetry-specification/pull/2881))
- Add `process.runtime.jvm.memory.usage_after_last_gc` metric to semantic conventions.
  ([#2901](https://github.com/open-telemetry/opentelemetry-specification/pull/2901))

### Compatibility

- Specify how Prometheus exporters and receivers handle instrumentation scope.
  ([#2703](https://github.com/open-telemetry/opentelemetry-specification/pull/2703)).

### OpenTelemetry Protocol

- Clarify that lowerCamelCase field names MUST be used for OTLP/JSON
  ([#2829](https://github.com/open-telemetry/opentelemetry-specification/pull/2829))

### SDK Configuration

- No changes.

### Telemetry Schemas

- No changes.

### Common

- Clarify that Scope is defined at build time
  ([#2878](https://github.com/open-telemetry/opentelemetry-specification/pull/2878))

## v1.14.0 (2022-10-04)

### Context

- No changes.

### Traces

- No changes.

### Metrics

- Changed the default buckets for Explicit Bucket Histogram to better match the
  official Prometheus clients.
  ([#2770](https://github.com/open-telemetry/opentelemetry-specification/pull/2770)).
- Fix OpenMetrics valid label keys, and specify prometheus conversion for metric name.
  ([#2788](https://github.com/open-telemetry/opentelemetry-specification/pull/2788))

### Logs

- Add environment variables for configuring the `BatchLogRecordProcessor`.
  ([#2785](https://github.com/open-telemetry/opentelemetry-specification/pull/2785))
- Fix inconsistencies in log README
  ([#2800](https://github.com/open-telemetry/opentelemetry-specification/pull/2800)).

### Resource

- Add `browser.mobile` and `browser.language` resource attributes
  ([#2761](https://github.com/open-telemetry/opentelemetry-specification/pull/2761))

### Semantic Conventions

- Add `process.context_switches`, and `process.open_file_descriptors`, to the
  metrics semantic conventions
  ([#2706](https://github.com/open-telemetry/opentelemetry-specification/pull/2706))
- Add exceptions to the logs semantic conventions
  ([#2819](https://github.com/open-telemetry/opentelemetry-specification/pull/2819))
- Make context propagation requirements explicit for messaging semantic conventions
  ([#2750](https://github.com/open-telemetry/opentelemetry-specification/pull/2750)).
- Update http metrics to use `http.route` instead of `http.target` for servers,
  drop `http.url` for clients
  ([#2818](https://github.com/open-telemetry/opentelemetry-specification/pull/2818)).

### Compatibility

- No changes.

### OpenTelemetry Protocol

- Add user agent to OTLP exporter specification
  ([#2684](https://github.com/open-telemetry/opentelemetry-specification/pull/2684))
- Prohibit usage of enum value name strings in OTLP/JSON
  ([#2758](https://github.com/open-telemetry/opentelemetry-specification/pull/2758))
- Clarify that unknown fields must be ignored when receiving OTLP/JSON
  ([#2816](https://github.com/open-telemetry/opentelemetry-specification/pull/2816))
- Add OTLP exporter user agent to the spec compliance matrix
  ([#2842](https://github.com/open-telemetry/opentelemetry-specification/pull/2842)).

### SDK Configuration

- Add the OTEL_SDK_DISABLED environment variable to the SDK configuration.
  ([2679](https://github.com/open-telemetry/opentelemetry-specification/pull/2679))
- Add the definition of a Boolean environment variable
  ([#2755](https://github.com/open-telemetry/opentelemetry-specification/pull/2755)).

### Telemetry Schemas

- No changes.

### Common

- No changes.

## v1.13.0 (2022-09-19)

### Context

- No changes.

### Traces

- Clarify the return of `Export(batch)` in the Batch Span Processor and exporter concurrency
  ([#2452](https://github.com/open-telemetry/opentelemetry-specification/pull/2452))
- Clarify that Context should not be mutable when setting a span
  ([#2637](https://github.com/open-telemetry/opentelemetry-specification/pull/2637))
- Clarify that `ForceFlush` is a required method on `SpanExporter` interface
  ([#2654](https://github.com/open-telemetry/opentelemetry-specification/pull/2654))

### Metrics

- Add experimental `OTEL_EXPORTER_OTLP_DEFAULT_HISTOGRAM_AGGREGATION` variable for
  configuring default histogram aggregation of OTLP metric exporter
  ([#2619](https://github.com/open-telemetry/opentelemetry-specification/pull/2619))
- Clarify async instrument callback identity
  ([#2538](https://github.com/open-telemetry/opentelemetry-specification/pull/2538))
- Prometheus export: Only monotonic sum are counters (with `_total`)
  ([#2644](https://github.com/open-telemetry/opentelemetry-specification/pull/2644))
- [OM/OTLP] Use `_created` for StartTimeUnixNano and vice-versa
  ([#2645](https://github.com/open-telemetry/opentelemetry-specification/pull/2645))
- Prometheus compatibility: use target_info metric instead of "target" info MF
  ([#2701](https://github.com/open-telemetry/opentelemetry-specification/pull/2701))
- Add optional Zero Threshold for Exponential Histograms to the metrics data model
  ([#2665](https://github.com/open-telemetry/opentelemetry-specification/pull/2665))
- Change the inclusivity of exponential histogram bounds
  ([#2633](https://github.com/open-telemetry/opentelemetry-specification/pull/2633))
- Add `process.threads` host metric semantic convention.
  ([#2705](https://github.com/open-telemetry/opentelemetry-specification/pull/2705)).

### Logs

- Update log SDK to allow log processors to mutate log records
  ([#2681](https://github.com/open-telemetry/opentelemetry-specification/pull/2681)).
- Add experimental Events and Logs API specification
  ([#2676](https://github.com/open-telemetry/opentelemetry-specification/pull/2676))
- Align log SDK and API component naming
  ([#2768](https://github.com/open-telemetry/opentelemetry-specification/pull/2768)).
- Add the signal-specific OTEL_EXPORTER_OTLP_LOGS_* environment variables
  ([#2782](https://github.com/open-telemetry/opentelemetry-specification/pull/2782)).

### Resource

- Update the version of the W3C Baggage specification used for `OTEL_RESOURCE_ATTRIBUTES`
  ([#2670](https://github.com/open-telemetry/opentelemetry-specification/pull/2670))

### Semantic Conventions

- Add `net.app.protocol.*` attributes
  ([#2602](https://github.com/open-telemetry/opentelemetry-specification/pull/2602))
- Add network metrics to process semantic conventions
  ([#2556](https://github.com/open-telemetry/opentelemetry-specification/pull/2556))
- Adopt attribute requirement levels in semantic conventions
  ([#2594](https://github.com/open-telemetry/opentelemetry-specification/pull/2594))
- Add semantic conventions for GraphQL
  ([#2456](https://github.com/open-telemetry/opentelemetry-specification/pull/2456))
- Change `cloudevents.event_spec_version` and `cloudevents.event_type` level from `required` to `recommended`
  ([#2618](https://github.com/open-telemetry/opentelemetry-specification/pull/2618))
- Change `faas.document.time` and `faas.time` level from `required` to `recommended`
  ([#2627](https://github.com/open-telemetry/opentelemetry-specification/pull/2627))
- Add `rpc.grpc.status_code` to RPC metric semantic conventions
  ([#2604](https://github.com/open-telemetry/opentelemetry-specification/pull/2604))
- Add `http.*.*.size` metric semantic conventions for tracking size of requests
  / responses for http servers / clients
  ([#2588](https://github.com/open-telemetry/opentelemetry-specification/pull/2588))
- BREAKING: rename `net.peer.ip` to `net.sock.peer.addr`, `net.host.ip` to `net.sock.host.addr`,
  `net.peer.name` to `net.sock.peer.name` for socket-level instrumentation.
  Define socket-level attributes and clarify logical peer and host attributes meaning
  ([#2594](https://github.com/open-telemetry/opentelemetry-specification/pull/2594))
- Add semantic conventions for JVM buffer pool usage
  ([#2650](https://github.com/open-telemetry/opentelemetry-specification/pull/2650))
- Improve the definition of `state` attribute for metric `system.network.connections`
  ([#2663](https://github.com/open-telemetry/opentelemetry-specification/pull/2663))
- Add `process.parent_pid` attribute for use in reporting parent process id (PID)
  ([#2691](https://github.com/open-telemetry/opentelemetry-specification/pull/2691))
- Add OpenSearch to db.system semantic conventions
  ([#2718](https://github.com/open-telemetry/opentelemetry-specification/pull/2718))
- Clarify when "count" is used instead of pluralization
  ([#2613](https://github.com/open-telemetry/opentelemetry-specification/pull/2613))
- Add the convention 'type' to the YAML definitions for all existing semantic conventions
  ([#2693](https://github.com/open-telemetry/opentelemetry-specification/pull/2693))
- Remove alternative attribute sets from HTTP semantic conventions
  ([#2469](https://github.com/open-telemetry/opentelemetry-specification/pull/2469))

### Compatibility

- No changes.

### OpenTelemetry Protocol

- Add support for partial success in an OTLP export response
  ([#2696](https://github.com/open-telemetry/opentelemetry-specification/pull/2696))

### SDK Configuration

- Mark `OTEL_METRIC_EXPORT_INTERVAL`, `OTEL_METRIC_EXPORT_TIMEOUT`
  environment variables as Stable
  ([#2658](https://github.com/open-telemetry/opentelemetry-specification/pull/2658))

### Telemetry Schemas

- Introduce "split" metric schema transformation
  ([#2653](https://github.com/open-telemetry/opentelemetry-specification/pull/2653))

### Common

- Introduce Instrumentation Scope Attributes
  ([#2579](https://github.com/open-telemetry/opentelemetry-specification/pull/2579))
  - Define Instrumentation Scope Attributes as non identifiers
    ([#2789](https://github.com/open-telemetry/opentelemetry-specification/pull/2789))

## v1.12.0 (2022-06-10)

### Context

- No changes.

### Traces

- No changes.

### Metrics

- Clarify that API support for multi-instrument callbacks is permitted.
  ([#2263](https://github.com/open-telemetry/opentelemetry-specification/pull/2263)).
- Clarify SDK behavior when view conflicts are present
  ([#2462](https://github.com/open-telemetry/opentelemetry-specification/pull/2462)).
- Clarify MetricReader.Collect result
  ([#2495](https://github.com/open-telemetry/opentelemetry-specification/pull/2495)).
- Specify optional support for an Exponential Histogram Aggregation.
  ([#2252](https://github.com/open-telemetry/opentelemetry-specification/pull/2252))
- Update Prometheus Sums for handling delta counter case
  ([#2570](https://github.com/open-telemetry/opentelemetry-specification/pull/2570)).
- Supplementary guidance for metrics additive property
  ([#2571](https://github.com/open-telemetry/opentelemetry-specification/pull/2571)).

### Logs

- OTLP Logs are now Stable
  ([#2565](https://github.com/open-telemetry/opentelemetry-specification/pull/2565))

### Resource

- No changes.

### Semantic Conventions

- Add semantic conventions for JVM CPU metrics
  ([#2292](https://github.com/open-telemetry/opentelemetry-specification/pull/2292))
- Add details for FaaS conventions for Azure Functions and allow FaaS/Cloud
  resources as span attributes on incoming FaaS spans
  ([#2502](https://github.com/open-telemetry/opentelemetry-specification/pull/2502))
- Define attribute requirement levels
  ([#2522](https://github.com/open-telemetry/opentelemetry-specification/pull/2522))
- Initial addition of Kafka metrics
  ([#2485](https://github.com/open-telemetry/opentelemetry-specification/pull/2485)).
- Add semantic conventions for Kafka consumer metrics
  ([#2536](https://github.com/open-telemetry/opentelemetry-specification/pull/2536))
- Add database connection pool metrics semantic conventions
  ([#2273](https://github.com/open-telemetry/opentelemetry-specification/pull/2273)).
- Specify how to obtain a Ruby thread's id
  ([#2508](https://github.com/open-telemetry/opentelemetry-specification/pull/2508)).
- Refactor jvm classes semantic conventions
  ([#2550](https://github.com/open-telemetry/opentelemetry-specification/pull/2550)).
- Add browser.* attributes
  ([#2353](https://github.com/open-telemetry/opentelemetry-specification/pull/2353)).
- Change JVM runtime metric `process.runtime.jvm.memory.max`
  to `process.runtime.jvm.memory.limit`
  ([#2605](https://github.com/open-telemetry/opentelemetry-specification/pull/2605)).
- Add semantic conventions for hardware metrics
  ([#2518](https://github.com/open-telemetry/opentelemetry-specification/pull/2518)).

### Compatibility

- No changes.

### OpenTelemetry Protocol

- No changes.

### SDK Configuration

- No changes.

### Telemetry Schemas

- No changes.

### Common

- Move non-otlp.md to common directory
  ([#2587](https://github.com/open-telemetry/opentelemetry-specification/pull/2587)).

## v1.11.0 (2022-05-04)

### Context

- No changes.

### Traces

- No changes.

### Metrics

- Clarify that API support for multi-instrument callbacks is permitted.
  ([#2263](https://github.com/open-telemetry/opentelemetry-specification/pull/2263)).
- Drop histogram aggregation, default to explicit bucket histogram
  ([#2429](https://github.com/open-telemetry/opentelemetry-specification/pull/2429))
- Clarify SDK behavior when view conflicts are present
  ([#2462](https://github.com/open-telemetry/opentelemetry-specification/pull/2462)).
- Add support for exemplars on OpenMetrics counters
  ([#2483](https://github.com/open-telemetry/opentelemetry-specification/pull/2483))
- Clarify MetricReader.Collect result
  ([#2495](https://github.com/open-telemetry/opentelemetry-specification/pull/2495)).
- Add database connection pool metrics semantic conventions
  ([#2273](https://github.com/open-telemetry/opentelemetry-specification/pull/2273)).

### Logs

- Update `com.google.*` to `gcp.*` in logs data model
  ([#2514](https://github.com/open-telemetry/opentelemetry-specification/pull/2514)).

### Resource

- No changes.

### Semantic Conventions

- Note added that `net.peer.name` SHOULD NOT be set if capturing it would require an
  extra reverse DNS lookup. And moved `net.peer.name` from common http attributes to
  just client http attributes.
  ([#2446](https://github.com/open-telemetry/opentelemetry-specification/pull/2446))
- Add `net.host.name` and `net.host.ip` conventions for rpc server spans.
  ([#2447](https://github.com/open-telemetry/opentelemetry-specification/pull/2447))
- Allow all metric conventions to be either synchronous or asynchronous.
  ([#2458](https://github.com/open-telemetry/opentelemetry-specification/pull/2458)
- Update JVM metrics with JMX Gatherer values
  ([#2478](https://github.com/open-telemetry/opentelemetry-specification/pull/2478))
- Add HTTP/3
  ([#2507](https://github.com/open-telemetry/opentelemetry-specification/pull/2507))
- Map SunOS to solaris for os.type resource attribute
  ([#2509](https://github.com/open-telemetry/opentelemetry-specification/pull/2509))

### Compatibility

- No changes.

### OpenTelemetry Protocol

- Clarify gRPC insecure option ([#2476](https://github.com/open-telemetry/opentelemetry-specification/pull/2476))
- Specify that OTLP/gRPC clients should retry on `RESOURCE_EXHAUSTED` code only if the server signals backpressure to indicate a possible recovery.
  ([#2480](https://github.com/open-telemetry/opentelemetry-specification/pull/2480))

### SDK Configuration

- No changes.

### Telemetry Schemas

- No changes.

### Common

- Define semantic conventions and instrumentation stability.
  ([#2180](https://github.com/open-telemetry/opentelemetry-specification/pull/2180))
- Loosen requirement for a major version bump
  ([#2510](https://github.com/open-telemetry/opentelemetry-specification/pull/2510)).

## v1.10.0 (2022-04-01)

### Context

- No changes.

### Traces

- Introduce the concept of Instrumentation Scope to replace/extend Instrumentation
  Library. The Tracer is now associated with Instrumentation Scope
  ([#2276](https://github.com/open-telemetry/opentelemetry-specification/pull/2276)).
- Add `OTEL_EXPORTER_JAEGER_PROTOCOL` environment variable to select the protocol
  used by the Jaeger exporter.
  ([#2341](https://github.com/open-telemetry/opentelemetry-specification/pull/2341))
- Add documentation REQUIREMENT for adding attributes at span creation.
  ([#2383](https://github.com/open-telemetry/opentelemetry-specification/pull/2383)).

### Metrics

- Initial Prometheus <-> OTLP datamodel specification
  ([#2266](https://github.com/open-telemetry/opentelemetry-specification/pull/2266))
- Introduce the concept of Instrumentation Scope to replace/extend Instrumentation
  Library. The Meter is now associated with Instrumentation Scope
  ([#2276](https://github.com/open-telemetry/opentelemetry-specification/pull/2276)).
- Specify the behavior of duplicate instrumentation registration in the API, specify
  duplicate conflicts in the data model, specify how the SDK is meant to report and
  assist the user when these conflicts arise.
  ([#2317](https://github.com/open-telemetry/opentelemetry-specification/pull/2317)).
- Clarify that expectations for user callback behavior are documentation REQUIREMENTs.
  ([#2361](https://github.com/open-telemetry/opentelemetry-specification/pull/2361)).
- Specify how to handle prometheus exemplar timestamp and attributes
  ([#2376](https://github.com/open-telemetry/opentelemetry-specification/pull/2376))
- Clarify that the periodic metric reader is the default metric reader to be
  paired with push metric exporters (OTLP, stdout, in-memory)
  ([#2379](https://github.com/open-telemetry/opentelemetry-specification/pull/2379)).
- Convert OpenMetrics Info and StateSet metrics to non-monotonic sums
  ([#2380](https://github.com/open-telemetry/opentelemetry-specification/pull/2380))
- Clarify that MetricReader has one-to-one mapping to MeterProvider.
  ([#2406](https://github.com/open-telemetry/opentelemetry-specification/pull/2406)).
- For prometheus metrics without sums, leave the sum unset
  ([#2413](https://github.com/open-telemetry/opentelemetry-specification/pull/2413))
- Specify default configuration for a periodic metric reader that is associated with
  the stdout metric exporter.
  ([#2415](https://github.com/open-telemetry/opentelemetry-specification/pull/2415)).
- Clarify the manner in which aggregation and temporality preferences
  are encoded via MetricReader parameters "on the basis of instrument
  kind".  Rename the environment variable
  `OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE` used to set the
  preference to be used when auto-configuring an OTLP Exporter,
  defaults to CUMULATIVE, with DELTA an option that makes Counter,
  Asynchronous Counter, and Histogram instruments choose Delta
  temporality by default.
  ([#2404](https://github.com/open-telemetry/opentelemetry-specification/pull/2404)).
- Clarify that instruments are enabled by default, even when Views are configured.
  Require support for the match-all View expression having `name=*` to support
  disabling instruments by default.
  ([#2417](https://github.com/open-telemetry/opentelemetry-specification/pull/2417)).
- Mark Metrics SDK spec as Mixed, with most components moving to Stable, while
  Exemplar remaining Feature-freeze.
  ([#2304](https://github.com/open-telemetry/opentelemetry-specification/pull/2304))
- Clarify how metric metadata and type suffixes are handled
  ([#2440](https://github.com/open-telemetry/opentelemetry-specification/pull/2440))

### Logs

- Add draft logging library SDK specification
  ([#2328](https://github.com/open-telemetry/opentelemetry-specification/pull/2328))
- Add InstrumentationScope/Logger Name to log data model
  ([#2359](https://github.com/open-telemetry/opentelemetry-specification/pull/2359))
- Remove `flush` method on LogEmitter
  ([#2405](https://github.com/open-telemetry/opentelemetry-specification/pull/2405))
- Declare Log Data Model Stable
  ([#2387](https://github.com/open-telemetry/opentelemetry-specification/pull/2387))

### Resource

- No changes.

### Semantic Conventions

- Define span structure for HTTP retries and redirects.
  ([#2078](https://github.com/open-telemetry/opentelemetry-specification/pull/2078))
- Changed `rpc.system` to an enum (allowing custom values), and changed the
  `rpc.system` value for .NET WCF from `wcf` to `dotnet_wcf`.
  ([#2377](https://github.com/open-telemetry/opentelemetry-specification/pull/2377))
- Define JavaScript runtime semantic conventions.
  ([#2290](https://github.com/open-telemetry/opentelemetry-specification/pull/2290))
- Add semantic conventions for [CloudEvents](https://cloudevents.io).
  ([#1978](https://github.com/open-telemetry/opentelemetry-specification/pull/1978))
- Add `process.cpu.utilization` metric.
  ([#2436](https://github.com/open-telemetry/opentelemetry-specification/pull/2436))
- Add `rpc.system` value for Apache Dubbo.
  ([#2453](https://github.com/open-telemetry/opentelemetry-specification/pull/2453))

### Compatibility

- Mark the OpenTracing compatibility section as stable.
  ([#2327](https://github.com/open-telemetry/opentelemetry-specification/pull/2327))

### OpenTelemetry Protocol

- Add experimental JSON serialization format
  ([#2235](https://github.com/open-telemetry/opentelemetry-specification/pull/2235))
- Parameters for private key and its chain added
  ([#2370](https://github.com/open-telemetry/opentelemetry-specification/pull/2370))

### SDK Configuration

- No changes.

### Telemetry Schemas

- No changes.

### Common

- Describe how to convert non-string primitives for protocols which only support strings
  ([#2343](https://github.com/open-telemetry/opentelemetry-specification/pull/2343))
- Add "Mapping Arbitrary Data to OTLP AnyValue" document.
  ([#2385](https://github.com/open-telemetry/opentelemetry-specification/pull/2385))

## v1.9.0 (2022-02-10)

### Context

- No changes.

### Traces

- Clarify `StartSpan` returning the parent as a non-recording Span when no SDK
  is in use.
  ([#2121](https://github.com/open-telemetry/opentelemetry-specification/pull/2121))
- Align Jaeger remote sampler endpoint with OTLP endpoint.
  ([#2246](https://github.com/open-telemetry/opentelemetry-specification/pull/2246))
- Add JaegerRemoteSampler spec.
  ([#2222](https://github.com/open-telemetry/opentelemetry-specification/pull/2222))
- Add support for probability sampling in the OpenTelemetry `tracestate` entry and
  add optional specification for consistent probability sampling.
  ([#2047](https://github.com/open-telemetry/opentelemetry-specification/pull/2047))
- Change description and default value of `OTEL_EXPORTER_JAEGER_ENDPOINT` environment
  variable to point to the correct HTTP port and correct description of
  `OTEL_TRACES_EXPORTER`.
  ([#2333](https://github.com/open-telemetry/opentelemetry-specification/pull/2333))

### Metrics

- Rename None aggregation to Drop.
  ([#2101](https://github.com/open-telemetry/opentelemetry-specification/pull/2101))
- Add details to the Prometheus Exporter requirements.
  ([#2124](https://github.com/open-telemetry/opentelemetry-specification/pull/2124))
- Consolidate the aggregation/aggregator term.
  ([#2153](https://github.com/open-telemetry/opentelemetry-specification/pull/2153))
- Remove the concept of supported temporality, keep preferred.
  ([#2154](https://github.com/open-telemetry/opentelemetry-specification/pull/2154))
- Rename extra dimensions to extra attributes.
  ([#2162](https://github.com/open-telemetry/opentelemetry-specification/pull/2162))
- Mark In-memory, OTLP and Stdout exporter specs as Stable.
  ([#2175](https://github.com/open-telemetry/opentelemetry-specification/pull/2175))
- Remove usage of baggage in View from initial SDK specification.
  ([#2215](https://github.com/open-telemetry/opentelemetry-specification/pull/2215))
- Add to the supplemental guidelines for metric SDK authors text about implementing
  attribute-removal Views for asynchronous instruments.
  ([#2208](https://github.com/open-telemetry/opentelemetry-specification/pull/2208))
- Clarify integer count instrument units.
  ([#2210](https://github.com/open-telemetry/opentelemetry-specification/pull/2210))
- Use UCUM units in Metrics Semantic Conventions.
  ([#2199](https://github.com/open-telemetry/opentelemetry-specification/pull/2199))
- Add semantic conventions for process metrics.
  [#2032](https://github.com/open-telemetry/opentelemetry-specification/pull/2061)
- Changed default Prometheus Exporter host from `0.0.0.0` to `localhost`.
  ([#2282](https://github.com/open-telemetry/opentelemetry-specification/pull/2282))
- Clarified wildcard and predicate support in metrics SDK View API.
  ([#2325](https://github.com/open-telemetry/opentelemetry-specification/pull/2325))
- Changed the Exemplar wording, exemplar should be turned off by default.
  ([#2414](https://github.com/open-telemetry/opentelemetry-specification/pull/2414))

### Logs

- Fix attributes names in Google Cloud Logging mapping.
  ([#2093](https://github.com/open-telemetry/opentelemetry-specification/pull/2093))
- Add OTEL_LOGS_EXPORTER environment variable.
  ([#2196](https://github.com/open-telemetry/opentelemetry-specification/pull/2196))
- Added ObservedTimestamp to the Log Data Model.
  ([#2184](https://github.com/open-telemetry/opentelemetry-specification/pull/2184))
- Change mapping for log_name of Google Cloud Logging.
  ([#2092](https://github.com/open-telemetry/opentelemetry-specification/pull/2092))
- Drop Log name.
  field ([#2271](https://github.com/open-telemetry/opentelemetry-specification/pull/2271))

### Resource

- No changes.

### Semantic Conventions

- Align runtime metric and resource namespaces
  ([#2112](https://github.com/open-telemetry/opentelemetry-specification/pull/2112))
- Prohibit usage of retired names in semantic conventions.
  ([#2191](https://github.com/open-telemetry/opentelemetry-specification/pull/2191))
- Add `device.manufacturer` to describe mobile device manufacturers.
  ([2100](https://github.com/open-telemetry/opentelemetry-specification/pull/2100))
- Change golang namespace to 'go', rather than 'gc'
  ([#2262](https://github.com/open-telemetry/opentelemetry-specification/pull/2262))
- Add JVM memory runtime semantic
  conventions. ([#2272](https://github.com/open-telemetry/opentelemetry-specification/pull/2272))
- Add opentracing.ref_type semantic convention.
  ([#2297](https://github.com/open-telemetry/opentelemetry-specification/pull/2297))

### Compatibility

- Simplify Baggage handling in the OpenTracing Shim layer.
  ([#2194](https://github.com/open-telemetry/opentelemetry-specification/pull/2194))
- State that ONLY error mapping can happen in the OpenTracing Shim layer.
  ([#2148](https://github.com/open-telemetry/opentelemetry-specification/pull/2148))
- Define the instrumentation library name for the OpenTracing Shim.
  ([#2227](https://github.com/open-telemetry/opentelemetry-specification/pull/2227))
- Add a Start Span section to the OpenTracing Shim.
  ([#2228](https://github.com/open-telemetry/opentelemetry-specification/pull/2228))

### OpenTelemetry Protocol

- Rename `OTEL_EXPORTER_OTLP_SPAN_INSECURE` to `OTEL_EXPORTER_OTLP_TRACES_INSECURE` and
  `OTEL_EXPORTER_OTLP_METRIC_INSECURE` to `OTEL_EXPORTER_OTLP_METRICS_INSECURE`
  so they match the naming of all other OTLP environment variables.
  ([#2240](https://github.com/open-telemetry/opentelemetry-specification/pull/2240))

### SDK Configuration

- No changes.

### Telemetry Schemas

- No changes.

## v1.8.0 (2021-11-12)

### Context

- Add a section for OTel specific values in TraceState.
  ([#1852](https://github.com/open-telemetry/opentelemetry-specification/pull/1852))
- Add `none` as a possible value for `OTEL_PROPAGATORS` to disable context
  propagation.
  ([#2052](https://github.com/open-telemetry/opentelemetry-specification/pull/2052))

### Traces

- No changes.

### Metrics

- Add optional min / max fields to histogram data model.
  ([#1915](https://github.com/open-telemetry/opentelemetry-specification/pull/1915),
  [#1983](https://github.com/open-telemetry/opentelemetry-specification/pull/1983))
- Add exponential histogram to the metrics data model.
  ([#1935](https://github.com/open-telemetry/opentelemetry-specification/pull/1935))
- Add clarifications on how to handle numerical limits.
  ([#2007](https://github.com/open-telemetry/opentelemetry-specification/pull/2007))
- Add environment variables for Periodic exporting MetricReader.
  ([#2038](https://github.com/open-telemetry/opentelemetry-specification/pull/2038))
- Specify that the SDK must support exporters to access meter information.
  ([#2040](https://github.com/open-telemetry/opentelemetry-specification/pull/2040))
- Add clarifications on how to determine aggregation temporality.
  ([#2013](https://github.com/open-telemetry/opentelemetry-specification/pull/2013),
  [#2032](https://github.com/open-telemetry/opentelemetry-specification/pull/2032))
- Mark Metrics API spec as Stable.
  ([#2104](https://github.com/open-telemetry/opentelemetry-specification/pull/2104))
- Clarify, fix and expand documentation sections:
  ([#1966](https://github.com/open-telemetry/opentelemetry-specification/pull/1966)),
  ([#1981](https://github.com/open-telemetry/opentelemetry-specification/pull/1981)),
  ([#1995](https://github.com/open-telemetry/opentelemetry-specification/pull/1995)),
  ([#2002](https://github.com/open-telemetry/opentelemetry-specification/pull/2002)),
  ([#2010](https://github.com/open-telemetry/opentelemetry-specification/pull/2010))

### Logs

- Fix Syslog severity number mapping in the example.
  ([#2091](https://github.com/open-telemetry/opentelemetry-specification/pull/2091))
- Add log.* attributes.
  ([#2022](https://github.com/open-telemetry/opentelemetry-specification/pull/2022))

### Resource

- No changes.

### Semantic Conventions

- Add `k8s.container.restart_count` Resource attribute.
  ([#1945](https://github.com/open-telemetry/opentelemetry-specification/pull/1945))
- Add "IBM z/Architecture" (`s390x`) to `host.arch`
  ([#2055](https://github.com/open-telemetry/opentelemetry-specification/pull/2055))
- BREAKING: Remove db.cassandra.keyspace and db.hbase.namespace, and clarify db.name
  ([#1973](https://github.com/open-telemetry/opentelemetry-specification/pull/1973))
- Add AWS App Runner as a cloud platform
  ([#2004](https://github.com/open-telemetry/opentelemetry-specification/pull/2004))
- Add Tencent Cloud as a cloud provider.
  ([#2006](https://github.com/open-telemetry/opentelemetry-specification/pull/2006))
- Don't set Span.Status for 4xx http status codes for SERVER spans.
  ([#1998](https://github.com/open-telemetry/opentelemetry-specification/pull/1998))
- Add attributes for Apache RocketMQ.
  ([#1904](https://github.com/open-telemetry/opentelemetry-specification/pull/1904))
- Define http tracing attributes provided at span creation time
  ([#1916](https://github.com/open-telemetry/opentelemetry-specification/pull/1916))
- Change meaning and discourage use of `faas.trigger` for FaaS clients (outgoing).
  ([#1921](https://github.com/open-telemetry/opentelemetry-specification/pull/1921))
- Clarify difference between container.name and k8s.container.name
  ([#1980](https://github.com/open-telemetry/opentelemetry-specification/pull/1980))

### Compatibility

- No changes.

### OpenTelemetry Protocol

- Clarify default for OTLP endpoint should, not must, be https
  ([#1997](https://github.com/open-telemetry/opentelemetry-specification/pull/1997))
- Specify the behavior of the OTLP endpoint variables for OTLP/HTTP more strictly
  ([#1975](https://github.com/open-telemetry/opentelemetry-specification/pull/1975),
  [#1985](https://github.com/open-telemetry/opentelemetry-specification/pull/1985))
- Make OTLP/HTTP the recommended default transport ([#1969](https://github.com/open-telemetry/opentelemetry-specification/pull/1969))

### SDK Configuration

- Unset and empty environment variables are equivalent.
  ([#2045](https://github.com/open-telemetry/opentelemetry-specification/pull/2045))

### Telemetry Schemas

Added telemetry schemas documents to the specification ([#2008](https://github.com/open-telemetry/opentelemetry-specification/pull/2008))

## v1.7.0 (2021-09-30)

### Context

- No changes.

### Traces

- Prefer global user defined limits over model-specific default values.
  ([#1893](https://github.com/open-telemetry/opentelemetry-specification/pull/1893))
- Generalize the "message" event to apply to all RPC systems not just gRPC
  ([#1914](https://github.com/open-telemetry/opentelemetry-specification/pull/1914))

### Metrics

- Added Experimental Metrics SDK specification.
  ([#1673](https://github.com/open-telemetry/opentelemetry-specification/pull/1673),
  [#1730](https://github.com/open-telemetry/opentelemetry-specification/pull/1730),
  [#1840](https://github.com/open-telemetry/opentelemetry-specification/pull/1840),
  [#1842](https://github.com/open-telemetry/opentelemetry-specification/pull/1842),
  [#1864](https://github.com/open-telemetry/opentelemetry-specification/pull/1864),
  [#1828](https://github.com/open-telemetry/opentelemetry-specification/pull/1828),
  [#1888](https://github.com/open-telemetry/opentelemetry-specification/pull/1888),
  [#1912](https://github.com/open-telemetry/opentelemetry-specification/pull/1912),
  [#1913](https://github.com/open-telemetry/opentelemetry-specification/pull/1913),
  [#1938](https://github.com/open-telemetry/opentelemetry-specification/pull/1938),
  [#1958](https://github.com/open-telemetry/opentelemetry-specification/pull/1958))
- Add FaaS metrics semantic conventions ([#1736](https://github.com/open-telemetry/opentelemetry-specification/pull/1736))
- Update env variable values to match other env variables
  ([#1965](https://github.com/open-telemetry/opentelemetry-specification/pull/1965))

### Logs

- No changes.

### Resource

- Exempt Resource from attribute limits.
  ([#1892](https://github.com/open-telemetry/opentelemetry-specification/pull/1892))

### Semantic Conventions

- BREAKING: Change enum member IDs to lowercase without spaces, not starting with numbers.
  Change values of `net.host.connection.subtype` to match.
  ([#1863](https://github.com/open-telemetry/opentelemetry-specification/pull/1863))
- Lambda instrumentations should check if X-Ray parent context is valid
  ([#1867](https://github.com/open-telemetry/opentelemetry-specification/pull/1867))
- Update YAML definitions for events
  ([#1843](https://github.com/open-telemetry/opentelemetry-specification/pull/1843)):
  - Mark exception as semconv type "event".
  - Add YAML definitions for grpc events.
- Add `messaging.consumer_id` to differentiate between message consumers.
  ([#1810](https://github.com/open-telemetry/opentelemetry-specification/pull/1810))
- Clarifications for `http.client_ip` and `http.host`.
  ([#1890](https://github.com/open-telemetry/opentelemetry-specification/pull/1890))
- Add HTTP request and response headers semantic conventions.
  ([#1898](https://github.com/open-telemetry/opentelemetry-specification/pull/1898))

### Compatibility

- No changes.

### OpenTelemetry Protocol

- Add environment variables for configuring the OTLP exporter protocol (`grpc`, `http/protobuf`, `http/json`) ([#1880](https://github.com/open-telemetry/opentelemetry-specification/pull/1880))
- Allow implementations to use their own default for OTLP compression, with `none` denotating no compression
  ([#1923](https://github.com/open-telemetry/opentelemetry-specification/pull/1923))
- Clarify OTLP server components MUST support none/gzip compression
  ([#1955](https://github.com/open-telemetry/opentelemetry-specification/pull/1955))
- Change OTLP/HTTP port from 4317 to 4318 ([#1970](https://github.com/open-telemetry/opentelemetry-specification/pull/1970))

### SDK Configuration

- Change default value for OTEL_EXPORTER_JAEGER_AGENT_PORT to 6831.
  ([#1812](https://github.com/open-telemetry/opentelemetry-specification/pull/1812))
- See also the changes for OTLP configuration listed under "OpenTelemetry Protocol" above.

## v1.6.0 (2021-08-06)

### Context

- No changes.

### Traces

- Add generalized attribute count and attribute value length limits and relevant
  environment variables.
  ([#1130](https://github.com/open-telemetry/opentelemetry-specification/pull/1130))
- Adding environment variables for event and link attribute limits. ([#1751](https://github.com/open-telemetry/opentelemetry-specification/pull/1751))
- Adding SDK configuration for Jaeger remote sampler ([#1791](https://github.com/open-telemetry/opentelemetry-specification/pull/1791))

### Metrics

- Metrics API specification Feature-freeze.
  ([#1833](https://github.com/open-telemetry/opentelemetry-specification/pull/1833))
- Remove MetricProcessor from the SDK spec (for now)
  ([#1840](https://github.com/open-telemetry/opentelemetry-specification/pull/1840))

### Logs

- No changes.

### Resource

- No changes.

### Semantic Conventions

- Add mobile-related network state: `net.host.connection.type`, `net.host.connection.subtype` & `net.host.carrier.*` [#1647](https://github.com/open-telemetry/opentelemetry-specification/issues/1647)
- Adding alibaba cloud as a cloud provider.
  ([#1831](https://github.com/open-telemetry/opentelemetry-specification/pull/1831))

### Compatibility

- No changes.

### OpenTelemetry Protocol

- Allow for OTLP/gRPC exporters to handle endpoint configuration without a scheme while still requiring them to support an endpoint configuration that includes a scheme of `http` or `https`. Reintroduce the insecure configuration option for OTLP/gRPC exporters. ([#1729](https://github.com/open-telemetry/opentelemetry-specification/pull/1729))
- Adding requirement to implement at least one of two transports: `grpc` or `http/protobuf`.
  ([#1790](https://github.com/open-telemetry/opentelemetry-specification/pull/1790/files))

### SDK Configuration

- No changes.

## v1.5.0 (2021-07-08)

### Context

- No changes.

### Traces

- Adding environment variables for event and link attribute limits.
  ([#1751](https://github.com/open-telemetry/opentelemetry-specification/pull/1751))
- Clarify some details about span kind and the meanings of the values.
  ([#1738](https://github.com/open-telemetry/opentelemetry-specification/pull/1738))
- Clarify meaning of the Certificate File option.
  ([#1803](https://github.com/open-telemetry/opentelemetry-specification/pull/1803))
- Adding environment variables for event and link attribute limits. ([#1751](https://github.com/open-telemetry/opentelemetry-specification/pull/1751))

### Metrics

- Clarify the limit on the instrument unit.
  ([#1762](https://github.com/open-telemetry/opentelemetry-specification/pull/1762))

### Logs

- Declare OTLP Logs Beta. ([#1741](https://github.com/open-telemetry/opentelemetry-specification/pull/1741))

### Resource

- No changes.

### Semantic Conventions

- Clean up FaaS semantic conventions, add `aws.lambda.invoked_arn`.
  ([#1781](https://github.com/open-telemetry/opentelemetry-specification/pull/1781))
- Remove `rpc.jsonrpc.method`, clarify that `rpc.method` should be used instead.
  ([#1748](https://github.com/open-telemetry/opentelemetry-specification/pull/1748))

### Compatibility

- No changes.

### OpenTelemetry Protocol

- No changes.

### SDK Configuration

- Allow selecting multiple exporters via `OTEL_TRACES_EXPORTER` and `OTEL_METRICS_EXPORTER`
  by using a comma-separated list. ([#1758](https://github.com/open-telemetry/opentelemetry-specification/pull/1758))

## v1.4.0 (2021-06-07)

### Context

- No changes.

### Traces

- Add schema_url support to `Tracer`. ([#1666](https://github.com/open-telemetry/opentelemetry-specification/pull/1666))
- Add Dropped Links Count to non-otlp exporters section ([#1697](https://github.com/open-telemetry/opentelemetry-specification/pull/1697))
- Add note about reporting dropped counts for attributes, events, links. ([#1699](https://github.com/open-telemetry/opentelemetry-specification/pull/1699))

### Metrics

- Add schema_url support to `Meter`. ([#1666](https://github.com/open-telemetry/opentelemetry-specification/pull/1666))
- Adds detail about when to use `StartTimeUnixNano` and handling of unknown start-time resets. ([#1646](https://github.com/open-telemetry/opentelemetry-specification/pull/1646))
- Expand `Gauge` metric description in the data model ([#1661](https://github.com/open-telemetry/opentelemetry-specification/pull/1661))
- Expand `Histogram` metric description in the data model ([#1664](https://github.com/open-telemetry/opentelemetry-specification/pull/1664))
- Added Experimental Metrics API specification.
  ([#1401](https://github.com/open-telemetry/opentelemetry-specification/pull/1401),
  [#1557](https://github.com/open-telemetry/opentelemetry-specification/pull/1557),
  [#1578](https://github.com/open-telemetry/opentelemetry-specification/pull/1578),
  [#1590](https://github.com/open-telemetry/opentelemetry-specification/pull/1590),
  [#1594](https://github.com/open-telemetry/opentelemetry-specification/pull/1594),
  [#1617](https://github.com/open-telemetry/opentelemetry-specification/pull/1617),
  [#1645](https://github.com/open-telemetry/opentelemetry-specification/pull/1645),
  [#1657](https://github.com/open-telemetry/opentelemetry-specification/pull/1657),
  [#1665](https://github.com/open-telemetry/opentelemetry-specification/pull/1665),
  [#1672](https://github.com/open-telemetry/opentelemetry-specification/pull/1672),
  [#1674](https://github.com/open-telemetry/opentelemetry-specification/pull/1674),
  [#1675](https://github.com/open-telemetry/opentelemetry-specification/pull/1675),
  [#1703](https://github.com/open-telemetry/opentelemetry-specification/pull/1703),
  [#1704](https://github.com/open-telemetry/opentelemetry-specification/pull/1704),
  [#1731](https://github.com/open-telemetry/opentelemetry-specification/pull/1731),
  [#1733](https://github.com/open-telemetry/opentelemetry-specification/pull/1733))
- Mark relevant portions of Metrics Data Model stable ([#1728](https://github.com/open-telemetry/opentelemetry-specification/pull/1728))

### Logs

- No changes.

### Resource

- Add schema_url support to `Resource`. ([#1692](https://github.com/open-telemetry/opentelemetry-specification/pull/1692))
- Clarify result of Resource merging and ResourceDetector aggregation in case of error. ([#1726](https://github.com/open-telemetry/opentelemetry-specification/pull/1726))

### Semantic Conventions

- Add JSON RPC specific conventions ([#1643](https://github.com/open-telemetry/opentelemetry-specification/pull/1643)).
- Add Memcached to Database specific conventions ([#1689](https://github.com/open-telemetry/opentelemetry-specification/pull/1689)).
- Add semantic convention attributes for the host device and added OS name and version ([#1596](https://github.com/open-telemetry/opentelemetry-specification/pull/1596)).
- Add CockroachDB to Database specific conventions ([#1725](https://github.com/open-telemetry/opentelemetry-specification/pull/1725)).

### Compatibility

- No changes.

### OpenTelemetry Protocol

- No changes.

### SDK Configuration

- Add `OTEL_SERVICE_NAME` environment variable. ([#1677](https://github.com/open-telemetry/opentelemetry-specification/pull/1677))

## v1.3.0 (2021-05-05)

### Context

- No changes.

### Traces

- `Get Tracer` should use an empty string if the specified `name` is null. ([#1654](https://github.com/open-telemetry/opentelemetry-specification/pull/1654))
- Clarify how to record dropped attribute count in non-OTLP formats. ([#1662](https://github.com/open-telemetry/opentelemetry-specification/pull/1662))

### Metrics

- Expand description of Event Model and Instruments. ([#1614](https://github.com/open-telemetry/opentelemetry-specification/pull/1614))
- Flesh out metric identity and single-write principle. ([#1574](https://github.com/open-telemetry/opentelemetry-specification/pull/1574))
- Expand `Sum` metric description in the data model and delta-to-cumulative handling. ([#1618](https://github.com/open-telemetry/opentelemetry-specification/pull/1618))
- Remove the "Func" name, use "Asynchronous" and "Observable". ([#1645](https://github.com/open-telemetry/opentelemetry-specification/pull/1645))
- Add details to UpDownCounter API. ([#1665](https://github.com/open-telemetry/opentelemetry-specification/pull/1665))
- Add details to Histogram API. ([#1657](https://github.com/open-telemetry/opentelemetry-specification/pull/1657))

### Logs

- Clarify "key/value pair list" vs "map" in Log Data Model. ([#1604](https://github.com/open-telemetry/opentelemetry-specification/pull/1604))

### Semantic Conventions

- Fix the inconsistent formatting of semantic convention enums. ([#1598](https://github.com/open-telemetry/opentelemetry-specification/pull/1598/))
- Add details for filling resource for AWS Lambda. ([#1610](https://github.com/open-telemetry/opentelemetry-specification/pull/1610))
- Add already specified `messaging.rabbitmq.routing_key` span attribute key to the respective YAML file. ([#1651](https://github.com/open-telemetry/opentelemetry-specification/pull/1651))
- Clarify usage of "otel." attribute namespace. ([#1640](https://github.com/open-telemetry/opentelemetry-specification/pull/1640))
- Add possibility to disable `db.statement` via instrumentation configuration. ([#1659](https://github.com/open-telemetry/opentelemetry-specification/pull/1659))

### Compatibility

- No changes.

### OpenTelemetry Protocol

- Fix incorrect table of transient errors. ([#1642](https://github.com/open-telemetry/opentelemetry-specification/pull/1642))
- Clarify that 64 bit integer numbers are decimal strings in OTLP/JSON. ([#1637](https://github.com/open-telemetry/opentelemetry-specification/pull/1637))

### SDK Configuration

- Add `OTEL_EXPORTER_JAEGER_TIMEOUT` environment variable. ([#1612](https://github.com/open-telemetry/opentelemetry-specification/pull/1612))
- Add `OTEL_EXPORTER_ZIPKIN_TIMEOUT` environment variable. ([#1636](https://github.com/open-telemetry/opentelemetry-specification/pull/1636))

## v1.2.0 (2021-04-14)

### Context

- Clarify composite `TextMapPropagator` method required and optional arguments. ([#1541](https://github.com/open-telemetry/opentelemetry-specification/pull/1541))
- Clarify B3 requirements and configuration. ([#1570](https://github.com/open-telemetry/opentelemetry-specification/pull/1570))

### Traces

- Add `ForceFlush` to `Span Exporter` interface ([#1467](https://github.com/open-telemetry/opentelemetry-specification/pull/1467))
- Clarify the description for the `TraceIdRatioBased` sampler needs to include the sampler's sampling ratio. ([#1536](https://github.com/open-telemetry/opentelemetry-specification/pull/1536))
- Define the fallback tracer name for invalid values.
  ([#1534](https://github.com/open-telemetry/opentelemetry-specification/pull/1534))
- Clarify non-blocking requirement from span API End. ([#1555](https://github.com/open-telemetry/opentelemetry-specification/pull/1555))
- Remove the Included Propagators section from trace API specification that was a duplicate of the Propagators Distribution of the context specification. ([#1556](https://github.com/open-telemetry/opentelemetry-specification/pull/1556))
- Remove the Baggage API propagator notes that conflict with the API Propagators Operations section and fix [#1526](https://github.com/open-telemetry/opentelemetry-specification/issues/1526). ([#1575](https://github.com/open-telemetry/opentelemetry-specification/pull/1575))

### Metrics

- Adds new metric data model specification ([#1512](https://github.com/open-telemetry/opentelemetry-specification/pull/1512))

### Semantic Conventions

- Add semantic conventions for AWS SDK operations and DynamoDB ([#1422](https://github.com/open-telemetry/opentelemetry-specification/pull/1422))
- Add details for filling semantic conventions for AWS Lambda ([#1442](https://github.com/open-telemetry/opentelemetry-specification/pull/1442))
- Update semantic conventions to distinguish between int and double ([#1550](https://github.com/open-telemetry/opentelemetry-specification/pull/1550))
- Add semantic convention for AWS ECS task revision ([#1581](https://github.com/open-telemetry/opentelemetry-specification/pull/1581))

### Compatibility

- Add initial OpenTracing compatibility section.
  ([#1101](https://github.com/open-telemetry/opentelemetry-specification/pull/1101))

## v1.1.0 (2021-03-11)

### Traces

- Implementations can ignore links with invalid SpanContext([#1492](https://github.com/open-telemetry/opentelemetry-specification/pull/1492))
- Add `none` as a possible value for OTEL_TRACES_EXPORTER to disable export
  ([#1439](https://github.com/open-telemetry/opentelemetry-specification/pull/1439))
- Add [`ForceFlush`](/specification/trace/sdk.md#forceflush) to SDK's `TracerProvider` ([#1452](https://github.com/open-telemetry/opentelemetry-specification/pull/1452))

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
