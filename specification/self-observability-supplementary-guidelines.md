# Self-Observability Supplementary Guidelines

Note: this document is NOT a spec, it is provided to support the
[Self-Observability](self-observability.md) specification, it does NOT add any
extra requirements to the existing specifications.

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [Scope of signals and lifecycle ordering](#scope-of-signals-and-lifecycle-ordering)
- [Obtaining the Meter / Logger for self-observability](#obtaining-the-meter--logger-for-self-observability)
- [Avoiding telemetry-induced-telemetry loops](#avoiding-telemetry-induced-telemetry-loops)
- [Treat self-observability like any other SDK feature for stability](#treat-self-observability-like-any-other-sdk-feature-for-stability)

<!-- tocstop -->

</details>

## Scope of signals and lifecycle ordering

SDK self-observability is currently expressed primarily as metrics, defined in
the [SDK self-observability metrics semantic conventions][semconv-sdk-metrics].
The design is not inherently metrics-only. Events or spans describing SDK
internals may be added by future semantic conventions, so SDK implementers
should not assume the surface will remain metric-shaped.

[semconv-sdk-metrics]: https://opentelemetry.io/docs/specs/semconv/otel/sdk-metrics/

Once more than one signal is involved, lifecycle ordering becomes a problem. The
recording providers (`MeterProvider`, `LoggerProvider`, and potentially
`TracerProvider`) are constructed and shut down independently, so the second one
to be constructed cannot accept telemetry produced during the setup of the first.
Similarly, once a provider is shut down it can no longer accept telemetry
produced while the others are still tearing down.

For example, during startup:

* If `MeterProvider` is constructed first, self-observability *events* produced
  during its setup cannot yet flow through `LoggerProvider`, since
  `LoggerProvider` does not yet exist.
* If `LoggerProvider` is constructed first, self-observability *metrics*
  produced during its setup cannot yet flow through `MeterProvider`.

No ordering avoids this entirely — whichever provider comes up "second" loses
the window before it exists, and whichever is shut down "first" loses the window
after it is gone. Self-observability telemetry at the edges of the SDK lifecycle
is therefore inherently best-effort; the strategy for handling it is left to the
SDK.

For self-observability events specifically, if the SDK already emits
diagnostics through a non-OpenTelemetry path — the language's native logging
facility, a commonly-used ecosystem logging library (e.g., Tokio's `tracing`
crate in Rust), or in the simplest case direct writes to stdout/stderr — that
path is a natural fit for events emitted before `LoggerProvider` is installed
or after it has been shut down. It is typically available throughout the
process lifetime and has few external dependencies that can fail.

## Obtaining the Meter / Logger for self-observability

An SDK has two broadly different ways to acquire the `Meter` / `Logger` it
uses to emit self-observability telemetry:

* From the global provider (e.g., `GlobalMeterProvider.Get(...)`).
  Self-observability data then flows through the same pipeline as the rest of
  the user's telemetry. This is the simplest to ship and requires no additional
  configuration. The trade-off is that the user cannot easily route SDK
  self-observability separately, and the [telemetry-induced-telemetry
  concern](#avoiding-telemetry-induced-telemetry-loops) becomes more relevant
  since the SDK is emitting into its own pipeline.
* From a `MeterProvider` / `LoggerProvider` supplied explicitly by the user
  (typically via a dedicated configuration option). This makes the
  [separate pipeline](#avoiding-telemetry-induced-telemetry-loops) pattern
  viable and lets operators send SDK self-observability to a different
  backend or apply different retention/sampling. The trade-off is an
  additional configuration surface, and a fallback decision when no
  provider is supplied (e.g., fall back to global, or emit nothing).

Both choices are valid and depend on the SDK's audience and how strongly it
wants to enable separate routing.

These two approaches can also be combined: an SDK can accept an explicit
`MeterProvider` / `LoggerProvider` and fall back to the global when none is
supplied. This is a common pattern in instrumentation libraries and gives
operators the option to route SDK self-observability separately without
forcing additional configuration on users who do not need it.

## Avoiding telemetry-induced-telemetry loops

When the SDK emits self-observability data through its own telemetry pipeline,
the data it emits can in turn be processed by that same pipeline, creating a
feedback loop. This is primarily a concern for events and traces: each event or
span the SDK produces while handling an event or span can itself cause more events
or spans to be produced, leading to unbounded recursion. Metrics are less
affected in practice.

Patterns SDKs can use to prevent such loops:

* Use a dedicated `LoggerProvider` (or `TracerProvider`) for self-observability
  that is isolated from the user's pipeline, so self-observability telemetry
  does not feed back into it.
* Use the OpenTelemetry `Context` to carry a flag marking code as running inside
  the SDK's own pipeline, and skip self-observability recording when the flag is
  set. There is no standardized spec for this today (tracked in
  [open-telemetry/opentelemetry-specification#530](https://github.com/open-telemetry/opentelemetry-specification/issues/530));
  in the meantime, several SDKs implement it independently:
  * .NET:
    [`SuppressInstrumentationScope`](https://github.com/open-telemetry/opentelemetry-dotnet/blob/core-1.15.3/src/OpenTelemetry/SuppressInstrumentationScope.cs#L12)
  * Rust:
    [`Context::enter_telemetry_suppressed_scope`](https://github.com/open-telemetry/opentelemetry-rust/blob/opentelemetry-0.32.0/opentelemetry/src/context.rs#L410)
  * Python:
    [`_SUPPRESS_INSTRUMENTATION_KEY`](https://github.com/open-telemetry/opentelemetry-python/blob/v1.42.1/opentelemetry-api/src/opentelemetry/context/__init__.py#L152)
  * Java:
    [`InstrumentationUtil.suppressInstrumentation`](https://github.com/open-telemetry/opentelemetry-java/blob/v1.63.0/api/all/src/main/java/io/opentelemetry/api/impl/InstrumentationUtil.java#L23-L24)

## Treat self-observability like any other SDK feature for stability

SDK self-observability is an SDK feature and is subject to the SDK's normal
[stability guarantees](versioning-and-stability.md) — no weaker, no different.

This has three consequences:

1. Any in-development or experimental metric, attribute, or semantic must be
   opt-in.
2. When part of the surface is stable and part is experimental, only the stable
   part should be on by default; the experimental part stays opt-in.
3. Self-observability is not exempt from these rules on the grounds that it is
   "just diagnostic data" — SDK feature stability rules apply uniformly, and a
   breaking change is a breaking change.

How the opt-in is exposed is left to each SDK. Examples from existing SDKs:

* An environment variable using the SDK's experimental-feature naming convention
  (e.g., OpenTelemetry Go's `OTEL_GO_X_OBSERVABILITY`).
* A build-time feature flag (e.g., an experimental Cargo feature in
  OpenTelemetry Rust).
