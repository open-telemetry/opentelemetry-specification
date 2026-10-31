# Instrumentation Stability API

Introduce a `Stability` API parameter (`Stable`, `Development`) on instruments, spans, and log records, along with top-level SDK provider configuration (`minimum_stability`, defaulting to `Stable`), to make "stable by default" a reality for instrumentation libraries.

## Motivation

The [OpenTelemetry Graduation Project](https://github.com/open-telemetry/community/pull/3452) established "stable by default" as a cross-project goal so users can rely on OpenTelemetry without unexpected breaking changes. Making "stable by default" a reality for [Instrumentation Libraries](../specification/glossary.md#instrumentation-library) requires resolving a fundamental tension between [Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/) and [Telemetry Stability](../specification/telemetry-stability.md):

- Under [Telemetry Stability](../specification/telemetry-stability.md), a `Stable` (`1.x`) instrumentation library is prohibited from making breaking changes to any telemetry it emits by default without a major version bump.
- At the same time, [Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/) evolve incrementally: many domains are still in `development`, and even stabilized domains such as HTTP and Database contain a mix of `stable` and `development` signals.

Without an API and SDK mechanism for an instrumentation library to mark `development` telemetry so the SDK can suppress it by default, language ecosystems are forced into unsustainable workarounds (surveyed in the [Appendix](#appendix-ecosystem-survey-of-experimental-telemetry-gating)):

1. **Perpetual pre-`1.0` versions**: All contrib instrumentation packages in Go (`v0.72.0`), Python (`0.67b0`), JavaScript (`0.x`), Ruby (`0.x`), Rust (`0.x`), and Kotlin (`0.9.0`), along with ~98% of Java library instrumentations (`-alpha`), remain pre-stable because they emit `development` conventions.
2. **Inconsistent methods of enabling experimental telemetry**: Ecosystems that gate unstable telemetry rely on incompatible mechanisms—including library-specific environment variables and `internal` APIs in `.NET` (`OTEL_DOTNET_EXPERIMENTAL_*`) and Java (`otel.instrumentation.<name>.experimental-span-attributes`), or compile-time flags and static annotations in Rust (`#[cfg(feature = "semconv_experimental")]`) and Kotlin (`@IncubatingApi`) that fail in transitive dependency graphs and leave [Application Owners](../specification/glossary.md#application-owner) with no unified runtime control.
3. **Frequent major version churn**: If a `1.x` instrumentation library emits `development` semantic conventions by default (as in PHP `1.x` and Erlang/Elixir `1.x`–`3.x`), any subsequent rename, unit change, or removal in Semantic Conventions forces a major version bump of the instrumentation library or breaks stability guarantees.

This OTEP provides the technical design to make "stable by default" a reality for instrumentation. Determining whether `Development` telemetry is emitted—and how users configure it—is an SDK policy concern rather than a bespoke implementation inside every instrumentation package.

### Requirements

- **Signal-level granularity within a single instrumentation scope**: Instrumentation libraries must be able to mark individual metrics, spans, and log records as `Stable` or `Development` within the same `Tracer`, `Meter`, or `Logger`, because stabilized Semantic Convention domains (such as HTTP and Database) contain a mix of `stable` and `development` signals (for example, `http.server.request.duration` is `stable`, whereas `http.server.active_requests` and `http.server.request.body.size` are `development`).
- **Stable by default**: SDKs must emit `Stable` telemetry by default while suppressing `Development` telemetry unless explicitly enabled by the [Application Owner](../specification/glossary.md#application-owner).
- **Decoupled package and convention lifecycles**: Instrumentation libraries must be able to release `1.0` when their public programmatic API is stable, evolve or remove `Development` telemetry in minor releases as Semantic Conventions change, and graduate individual telemetry items from `Development` to `Stable` in minor releases without a major version bump.
- **Centralized SDK configuration**: Application Owners must have a consistent, SDK-level mechanism (programmatic and [Declarative Configuration](../specification/configuration/README.md)) to enable `Development` telemetry across all instrumentation libraries.
- **Orthogonality to value and importance controls**: Stability (`Development` vs. `Stable`) must remain independent from APIs that control telemetry volume, cost, or importance, such as log `Severity` levels or metric [`OptIn`](../specification/metrics/api.md#instrument-advisory-parameter-optin).

### Terminology

- **[`Stability` Maturity Levels](../specification/maturity-levels.md)**: This proposal introduces an API and SDK `Stability` enumeration ordered by maturity (`Development` < `Stable`). `Stability` describes the backward-compatibility guarantee of a signal's schema and is orthogonal to value or importance APIs such as log `Severity` levels or metric [`OptIn`](../specification/metrics/api.md#instrument-advisory-parameter-optin) (which control whether telemetry is emitted based on operational verbosity, cost, or cardinality). It has two initial values:
  - `Stable`: Telemetry covered by backward-compatibility guarantees; emitted by default when not disabled by other controls (such as metric `OptIn` or log `Severity` filtering).
  - `Development`: Experimental telemetry that MAY change or be removed in minor versions of a `1.x` instrumentation library; disabled by default when the SDK provider's `minimum_stability` is `Stable`.

## Proposal

### Instrumentation Examples

An instrumentation library passes `stability = Development` on individual instruments, spans, or log records that are based on `development` conventions, while leaving stable telemetry at the default `Stable`:

```go
// Development metric (disabled by default; enabled when minimum_stability is Development)
activeRequests, _ := meter.Int64UpDownCounter(
    "http.server.active_requests",
    metric.WithUnit("{request}"),
    metric.WithStability(otel.StabilityDevelopment),
)

// Development span (non-recording by default; recorded when minimum_stability is Development)
ctx, childSpan := tracer.Start(ctx, "spring.controller.exec",
    trace.WithStability(otel.StabilityDevelopment),
)
defer childSpan.End()
```

### Configuration Examples

By default, `TracerProvider`, `MeterProvider`, and `LoggerProvider` set `minimum_stability` to `Stable`. An [Application Owner](../specification/glossary.md#application-owner) can lower `minimum_stability` to `Development` across a provider programmatically or via [Declarative Configuration](../specification/configuration/README.md):

```yaml
file_format: "1.2"
tracer_provider:
  minimum_stability: development
  processors:
    - batch:
        exporter:
          otlp_http: {}
meter_provider:
  minimum_stability: development
  readers:
    - periodic:
        exporter:
          otlp_http: {}
logger_provider:
  minimum_stability: development
  processors:
    - batch:
        exporter:
          otlp_http: {}
```

In Metrics, an Application Owner can also keep `minimum_stability: stable` at the provider level and selectively enable a single `Development` instrument (or an `opt_in` attribute on a `Stable` instrument) using a [View](../specification/metrics/sdk.md#view):

```yaml
meter_provider:
  views:
    - selector:
        instrument_name: http.server.active_requests
      stream:
        enabled: true
```

### Migration Path for Instrumentation Libraries

1. **Pass stability levels based on convention maturity**: Instrumentation libraries pass `Stability` (`Stable` or `Development`) through the API based solely on the stability of the conventions each metric, span, or log record is based on.
2. **Stabilize the package when its public API is ready**: Once `Development` telemetry is marked via the API, the package is free to release `1.0.0` to indicate that its public programmatic API is stable, independent of whether all of its underlying Semantic Conventions have stabilized.
3. **Graduate individual telemetry items (both pre-`1.0` and `1.x`)**: Whenever a `Development` metric, span, or log record stabilizes in Semantic Conventions, the instrumentation updates its stability from `Development` to `Stable` (or removes the `Development` marker) in a minor release—whether the package is still `0.x` or already `1.x`.

## Internal details

### What the Specification WILL specify

#### `specification/telemetry-stability.md` and `specification/versioning-and-stability.md`

- A `Stable` (`1.x`) instrumentation library MAY modify, rename, or remove telemetry marked with `Stability = Development` without a major version bump.
- Telemetry emitted with `Stability = Stable` (the default when unspecified) by a `Stable` instrumentation library remains bound by all existing backward-compatibility rules in [Telemetry Stability](../specification/telemetry-stability.md).
- Graduating a piece of telemetry from `Development` to `Stable` (so that it becomes emitted by default) is a non-breaking additive change permitted in a minor version release of a `Stable` instrumentation library. Conversely, lowering the stability level of existing `Stable` telemetry to `Development` (which suppresses it by default) is a breaking change that requires a major version bump.

#### Signal APIs (`specification/trace/api.md`, `specification/metrics/api.md`, `specification/logs/api.md`)

- **Trace, Metrics, and Logs Operations**: `Span Creation` (`StartSpan`) and `Tracer.Enabled` in the Trace API, all synchronous and asynchronous `Instrument Creation` operations in the Metrics API (as an instrument advisory parameter), and `Emit a LogRecord` and `Logger.Enabled` in the Logs API SHOULD accept an optional `Stability` parameter (`Stable` or `Development`, defaulting to `Stable`).

#### Signal SDKs (`specification/trace/sdk.md`, `specification/metrics/sdk.md`, `specification/logs/sdk.md`)

- **Provider Configuration**: `TracerProvider`, `MeterProvider`, and `LoggerProvider` SHOULD support a `minimum_stability` configuration parameter of type `Stability` (defaulting to `Stable`).
- **Suppression and Enablement Across Signals**:
  - When a signal's `Stability` meets or exceeds the provider's `minimum_stability` (including `Development` telemetry when `minimum_stability` is `Development`), the SDK MUST process it according to normal pipeline rules.
  - When a signal's `Stability` is lower than the provider's `minimum_stability` (that is, `minimum_stability` is `Stable` and `Stability` is `Development`) and it is not explicitly enabled by a Metric `View`:
    - `Tracer.Enabled`, synchronous `Instrument.Enabled`, and `Logger.Enabled` MUST return `false`.
    - **Traces**: `StartSpan` MUST behave equivalently to a [No-op Tracer](../specification/trace/api.md#behavior-of-the-api-in-the-absence-of-an-installed-sdk)—returning a non-recording `Span` wrapping the `SpanContext` from the parent `Context` unchanged (preserving distributed trace continuity and `ParentBased` sampling for downstream calls), without generating a new `SpanId` or invoking the `Sampler` or any `SpanProcessor`.
    - **Metrics**: The SDK MUST apply the [Drop Aggregation](../specification/metrics/sdk.md#drop-aggregation).
    - **Logs**: `Emit` MUST drop the `LogRecord` before invoking any `LogRecordProcessor`.
- **Metric `OptIn` and `View` Interaction (`specification/metrics/sdk.md`)**:
  - An instrument is enabled when no `View` sets `enabled` if and only if its `OptIn` advisory parameter is `false` (or unset) **AND** its `Stability` meets or exceeds the `MeterProvider`'s `minimum_stability`.
  - If a matching `View` explicitly configures `enabled = true`, the SDK MUST enable the stream regardless of whether `OptIn` is `true` or `Stability` is `Development`. If a matching `View` configures `enabled = false`, the SDK MUST use the Drop Aggregation.

| Instrument `Stability` | Instrument `OptIn` | Default (`minimum_stability = Stable`) | Provider `minimum_stability = Development` | Matching View `enabled = true` |
| :--- | :--- | :--- | :--- | :--- |
| `Stable` | `false` | **Enabled** | **Enabled** | **Enabled** |
| `Stable` | `true` | **Disabled** (Drop) | **Disabled** (Drop) | **Enabled** |
| `Development` | `false` | **Disabled** (Drop) | **Enabled** | **Enabled** |
| `Development` | `true` | **Disabled** (Drop) | **Disabled** (Drop) | **Enabled** |

### What the Specification WILL NOT specify

- Language-specific method names, option builders, or internal SDK structures.
- Adding `minimum_stability` to `TracerConfig`, `MeterConfig`, or `LoggerConfig` in scope configurator functions.
- Wire-protocol (OTLP) fields for telemetry stability.

## Trade-offs and mitigations

- **Default Telemetry Changes When Instrumentation Adopts `Development` Markers**: When an existing pre-`1.0` instrumentation library marks unstable telemetry as `Development`, users who keep the default `minimum_stability: stable` stop receiving that unstable telemetry upon upgrading.
  - *Mitigation*: Where stable Semantic Conventions already exist for a domain, instrumentation libraries SHOULD upgrade directly to the `Stable` conventions rather than marking legacy or unstable telemetry as `Development`, avoiding the `Development` stage altogether. For telemetry whose conventions are still in `development`, contrib repositories SHOULD adopt the stability API across the entire repository in a coordinated pass (and document newly gated `Development` telemetry in release notes) so that opting in to experimental telemetry via `minimum_stability: development` is a one-time, consistent configuration change.

## Prior art and alternatives

### Prior Art

- **Metric Advisory Parameters [`OptIn`](../specification/metrics/api.md#instrument-advisory-parameter-optin) and [`Attributes`](../specification/metrics/api.md#instrument-advisory-parameter-attributes) ([Specification PR #3785](https://github.com/open-telemetry/opentelemetry-specification/pull/3785))**: Established the pattern of instrumentation passing metadata to the Metrics API while the SDK controls enablement and filtering via `MeterProvider` and `View`s.
- **OpenTelemetry Collector `metadata.yaml` and `featuregate`**: Collector components declare per-metric `stability` (`alpha`/`development`, `beta`, `stable`) and `enabled` defaults in `metadata.yaml`, and gate experimental features centrally via `featuregate` (`StageAlpha` disabled by default).
- **Per-Language Experimental Feature Flags**: As detailed in the [Appendix](#appendix-ecosystem-survey-of-experimental-telemetry-gating), several language repositories have built custom mechanisms to gate experimental telemetry—including Java's `internal/Experimental.setEmitExperimentalTelemetry`, `.NET`'s `OTEL_DOTNET_EXPERIMENTAL_*` environment variables, Go's runtime metrics opt-in environment variable, and `OTEL_SEMCONV_STABILITY_OPT_IN` in Python, JavaScript, and Ruby.

### Alternatives Considered

- **Standardizing per-instrumentation feature gates or `instrumentation.yaml` `semconv` blocks**: [Declarative Configuration `schema/instrumentation.yaml`](https://github.com/open-telemetry/opentelemetry-configuration/blob/main/schema/instrumentation.yaml) defines `general.<domain>.semconv.experimental` for eight hardcoded domains. Requiring every instrumentation package across 12 languages to depend on `ConfigProvider` and maintain manual `if/else` branching for every experimental metric, span, and attribute does not scale and leaves custom or non-core domains unhandled.
- **Decoupling package `1.0` stability from default-emitted telemetry stability ([OTEP #4813](https://github.com/open-telemetry/opentelemetry-specification/pull/4813))**: Allowing `1.0` instrumentation libraries to emit `Development` telemetry by default and break it in minor releases was rejected because breaking default-emitted telemetry in a minor upgrade breaks user dashboards and alerts.
- **Define an API to pass attribute stability**: Adding an API to mark individual attributes as `Development` (either when recording attributes or when creating a `Tracer`, `Meter`, or `Logger`) is unnecessary and would require SDKs to filter attribute keys on hot recording paths. [Weaver's stability policy](https://github.com/open-telemetry/opentelemetry-weaver-packages/blob/main/policies/check/stability/stability.rego) already enforces that a `stable` signal cannot reference a `development` attribute unless that attribute has `requirement_level: opt_in`. Consequently, `Stable` telemetry never emits `Development` attributes by default, and on `Development` signals the entire metric, span, or log record is already gated by the signal's stability.
- **Scope-level `stability` on `GetTracer`, `GetMeter`, and `GetLogger`**: Passing a single `stability` flag at scope creation makes graduating the first metric or span in an instrumentation package disruptive, as removing the scope-level flag forces the author to annotate every other call site in the package simultaneously. Per-instrument, per-span, and per-log-record `stability` makes graduating any individual signal a one-line change and maps directly to Weaver per-signal code generation.
- **Reusing `OptIn` (`bool`) instead of a separate `Stability` enum**: In Semantic Conventions, `requirement_level: opt_in` and `stability: development` are orthogonal—a metric can be both `Development` and `OptIn` (meaning it will remain `OptIn` even after it stabilizes). Conflating the two would cause `minimum_stability: development` to enable high-cardinality `OptIn` telemetry.

## Open questions

- Should an environment variable (such as `OTEL_MINIMUM_STABILITY=development`) also be specified alongside programmatic and Declarative Configuration for `minimum_stability`?

## Prototypes

- **Normative Specification (`opentelemetry-specification`)**: [main...dashpole:opentelemetry-specification:stable-by-default-instrumentation-spec](https://github.com/open-telemetry/opentelemetry-specification/compare/main...dashpole:opentelemetry-specification:stable-by-default-instrumentation-spec)
- **Go SDK (`opentelemetry-go`)**: [main...dashpole:opentelemetry-go:stable-by-default-instrumentation](https://github.com/open-telemetry/opentelemetry-go/compare/main...dashpole:opentelemetry-go:stable-by-default-instrumentation)
- **Go Contrib Instrumentation (`opentelemetry-go-contrib` — `otelhttp` and `runtime`)**: [main...dashpole:opentelemetry-go-contrib:stable-by-default-instrumentation](https://github.com/open-telemetry/opentelemetry-go-contrib/compare/main...dashpole:opentelemetry-go-contrib:stable-by-default-instrumentation)
- **Java SDK (`opentelemetry-java`)**: [main...dashpole:opentelemetry-java:stable-by-default-instrumentation](https://github.com/open-telemetry/opentelemetry-java/compare/main...dashpole:opentelemetry-java:stable-by-default-instrumentation)
- **Python SDK (`opentelemetry-python`)**: [main...dashpole:opentelemetry-python:stable-by-default-instrumentation](https://github.com/open-telemetry/opentelemetry-python/compare/main...dashpole:opentelemetry-python:stable-by-default-instrumentation)
- **JavaScript / TypeScript SDK (`opentelemetry-js`)**: [main...dashpole:opentelemetry-js:stable-by-default-instrumentation](https://github.com/open-telemetry/opentelemetry-js/compare/main...dashpole:opentelemetry-js:stable-by-default-instrumentation)
- **Declarative Configuration (`opentelemetry-configuration`)**: [main...dashpole:opentelemetry-configuration:stable-by-default-instrumentation](https://github.com/open-telemetry/opentelemetry-configuration/compare/main...dashpole:opentelemetry-configuration:stable-by-default-instrumentation)

## Future possibilities

- **Additional `Stability` enum values (such as `Deprecated`)**: Extending the `Stability` enum to include `Deprecated` so instrumentation libraries can mark deprecated telemetry and allow Application Owners to opt in or out of deprecated metrics, spans, and log records centrally in the SDK.
- **Weaver code generation**: Updating [Weaver](https://github.com/open-telemetry/weaver) templates so generated semantic convention helpers automatically pass `Stability` into the OpenTelemetry APIs.
- **Targeted span and log enablement**: Extending span and log configuration (or [Telemetry Policy](4738-telemetry-policy.md)) to selectively enable individual `Development` spans or log records by name or scope, analogous to Metric `View`s. Across contrib repositories today, individual by-name experimental toggles exist exclusively for metrics (which are already supported by Metric `View`s with `enabled: true`), while existing trace and log experimental flags in library instrumentations are coarse booleans, so per-span and per-log selectors can be added as a future enhancement without blocking instrumentation migration.

## Appendix: Ecosystem Survey of Experimental Telemetry Gating

*At the time of writing this OTEP, this reflects current support.*

| Ecosystem | Contrib `1.0+` Instrumentation | Current Experimental Telemetry Gating |
| :--- | :--- | :--- |
| **Go** | `0 / ~20` (`v0.72.0`) | Runtime metrics opt-in env var, `WithOptIn()`, `WithDefaultAttributes()` |
| **Java** | `4 / 200+` (~98% `-alpha`) | `internal/Experimental.setEmitExperimentalTelemetry`, `otel.instrumentation.<name>.experimental-span-attributes` |
| **Python** | `0 / 74` (`0.67b0`) | `OTEL_SEMCONV_STABILITY_OPT_IN` (`_semconv.py`), per-instrumentor `config` dict |
| **JS / TS** | `0 / 65+` (`0.x`) | `OTEL_SEMCONV_STABILITY_OPT_IN` (`semconvStability.ts`), vendored incubating constants |
| **.NET** | `6` stable (`1.20.x`), `~16` beta/alpha | Unstable telemetry stripped from `1.x` default path; `internal` options + `OTEL_DOTNET_EXPERIMENTAL_*` env vars |
| **Rust** | `0` (`0.x`) | Compile-time `#[cfg(feature = "semconv_experimental")]` (enabled unconditionally by contrib crates) |
| **C++** | `1` (`webserver 1.1`), others `0.x` | `semconv/incubating/` headers, `OPENTELEMETRY_ABI_VERSION_NO=2` |
| **Swift** | Bundled at `2.6.0` | Programmatic `HTTPSemanticConvention` enum (defaults to `.old`) |
| **Kotlin** | `0` (`0.9.0`) | `@ExperimentalApi` and `@IncubatingApi` compile-time warnings |
| **PHP** | `6` HTTP at `1.x`, DB at `0.x` | `SemConv\Incubating` + `@experimental` PHPDoc; `1.x` packages emit incubating attributes unconditionally |
| **Ruby** | `0 / 43` (`0.x`) | `OTEL_SEMCONV_STABILITY_OPT_IN` monkey-patch module swapping (`old`, `dup`, `stable`) |
| **Erlang / Elixir** | Mixed `1.x`–`3.x` and `0.x` | Separate `0.x` `opentelemetry_api_experimental` app; major version bumps on SemConv changes; `opt_in_attrs` map |
| **Collector** | Component `status.stability` | `metadata.yaml` per-metric `enabled` + `stability`, `resource_attributes`, `featuregate` (`StageAlpha` off by default) |
