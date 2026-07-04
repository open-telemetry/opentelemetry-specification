<!--- Hugo front matter used to generate the website version of this page:
linkTitle: Instrumentation Supplementary Guidelines
--->

# Instrumentation Supplementary Guidelines

Note: this document is NOT a spec, it is provided as non-normative guidance for
[Instrumentation Authors](glossary.md#instrumentation-author); it does NOT add
any extra requirements to the existing specifications.

This covers both maintainers of a separate
[Instrumentation Library](glossary.md#instrumentation-library) that instruments
code it does not own (e.g. a database client or web framework) and maintainers
adding [native](glossary.md#natively-instrumented) OpenTelemetry instrumentation
to their own library. Except where noted, it applies to both. See
[Instrumentation Libraries](overview.md#instrumentation-libraries) for the
instrumentation-vs-instrumented distinction and package naming.

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [Dependencies](#dependencies)
- [Instrumentation Scope](#instrumentation-scope)
- [Acquiring Tracers, Meters, and Loggers](#acquiring-tracers-meters-and-loggers)
- [Semantic Conventions](#semantic-conventions)
- [Context Propagation](#context-propagation)
- [Robustness](#robustness)
- [Configuration](#configuration)
- [Stability and Versioning](#stability-and-versioning)
- [Testing](#testing)

<!-- tocstop -->

</details>

## Dependencies

The specification already requires instrumentation to depend only on the
OpenTelemetry API, not the SDK (see [Overview](overview.md#sdk)).

Depending only on the API lets a library ship instrumentation without forcing
its consumers to adopt OpenTelemetry: with no SDK installed, the
[minimal implementation](library-guidelines.md#api-and-minimal-implementation)
built into the API generates no telemetry.

Instrumentation can additionally depend on the OpenTelemetry
[Semantic Conventions](semantic-conventions.md) package where one is published
for the language.

## Instrumentation Scope

Telemetry emitted by an instrumentation library is associated with an
[Instrumentation Scope](common/instrumentation-scope.md) whose `name` and
optional `version` and `schema_url` identify the instrumentation that produced
it.

* The scope `name` should identify the **instrumentation** library, not the
  instrumented library, and should uniquely identify it, typically a fully
  qualified package or module name. For example, an HTTP client instrumentation
  uses the instrumentation package name (such as
  `io.opentelemetry.instrumentation.okhttp`), not the HTTP client it instruments.
* The scope `version` should be the version of the instrumentation library.
* When the instrumentation targets a particular version of the OpenTelemetry
  Semantic Conventions, it should set the scope `schema_url` to the
  corresponding [Telemetry Schema](schemas/README.md) URL.
* The scope name and version are part of the emitted telemetry's identity.
  Changing the scope `name` is a user-visible change and is best treated as a
  breaking change (see [Stability and Versioning](#stability-and-versioning)).

## Acquiring Tracers, Meters, and Loggers

An instrumentation library obtains a `Tracer`, `Meter`, or `Logger` from the
corresponding provider.

* Instrumentation should accept a `TracerProvider`, `MeterProvider`, and/or
  `LoggerProvider`, **not** an already-obtained `Tracer`, `Meter`, or `Logger`.
  Accepting the provider lets the instrumentation set the
  [Instrumentation Scope](#instrumentation-scope) (name, version, schema URL,
  attributes) itself, which it cannot do if it is handed an instance created
  with someone else's scope.
* When the application does not supply a provider explicitly, instrumentation
  can fall back to the [global provider](trace/api.md#tracerprovider) exposed by
  the API, where the language provides one. This "accept an explicit provider,
  otherwise fall back to the global" pattern is the common default.
* As common practice, instrumentation obtains the `Tracer`/`Meter`/`Logger` once
  (for example at construction time) and reuses it, rather than obtaining a new
  one per operation. The API guarantees that a `Tracer` picks up later
  configuration changes, so caching it is safe.

## Semantic Conventions

Instrumentation should follow the applicable
[OpenTelemetry Semantic Conventions](https://github.com/open-telemetry/semantic-conventions)
for the telemetry it emits: span names, attributes, metric names and units,
and log record fields. Consistent conventions let users and observability tools
interpret telemetry without learning each library's specifics.

* Semantic conventions assign each attribute a
  [requirement level](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/general/attribute-requirement-level.md)
  (Required, Conditionally Required, Recommended, or Opt-In). Instrumentation
  should populate Required, Conditionally Required, and Recommended attributes by
  default, and should provide a mechanism for users to opt in to Opt-In
  attributes, which are omitted by default because they can be expensive,
  high-cardinality, or sensitive. Instrumentation can also let users opt out of
  Recommended attributes they do not need.
* Where no stable semantic convention exists for a domain, instrumentation can
  define its own attributes, and should namespace them to avoid collisions and
  migrate to the OpenTelemetry convention once one stabilizes.

For signal-specific guidance, see the metrics
[Guidelines for instrumentation library authors](metrics/supplementary-guidelines.md#guidelines-for-instrumentation-library-authors)
on choosing the correct instrument.

## Context Propagation

Instrumentation participates in [Context](context/README.md) propagation so
that spans, metrics exemplars, and logs correlate correctly.

* In process, instrumentation sets the span it creates as the
  [active span](trace/api.md#context-interaction) for the duration of the
  operation, so that nested instrumentation and logs correlate with it.
* For a library that performs **outbound** inter-process calls over a protocol
  that is not already instrumented, the instrumentation should **inject** the
  propagation context into the outgoing request using the configured
  [propagators](context/api-propagators.md).
* For a library that **receives** inbound inter-process requests, the
  instrumentation should **extract** the propagation context from the incoming
  request and use it as the parent for the spans it creates.
* Instrumentation should use the propagators supplied by the application rather
  than hardcoding a specific propagation format.
* Context propagation is independent of whether the instrumentation records a
  span. A span can be [non-recording](trace/api.md#isrecording) or sampled out,
  or a no-op `Tracer` can be in use, yet a valid context can still flow through
  the service. Instrumentation should continue to inject and extract context in
  these cases so that a service in the middle of a trace does not break
  propagation for upstream and downstream participants.
* If instrumentation exposes a switch to turn off its own span generation (see
  [Configuration](#configuration)), that switch should not, by itself, also
  disable context propagation. Instrumentation can expose a separate switch for
  users who need to control propagation independently.

## Robustness

Instrumentation code should never let its own failures propagate into, or change
the behavior of, the instrumented library. Errors within instrumentation are
best handled internally, consistent with
[Error Handling Principles](error-handling.md).

## Configuration

* Instrumentation should expose configuration through the idiomatic mechanism
  for the language (for example, an options object or builder).
* Configuration surfaces should be minimal and have sensible defaults, so that
  instrumentation produces useful telemetry conforming to the semantic
  conventions without requiring configuration.
* Instrumentation should not expose configuration for concerns the SDK already
  owns (such as sampling, batching, resource detection, or exporter selection);
  these are configured by the [Application Owner](glossary.md#application-owner)
  on the SDK.

## Stability and Versioning

* Instrumentation packages should version independently of the OpenTelemetry API
  and SDK, and should follow the project's
  [Versioning and Stability](versioning-and-stability.md) guidance.
* The telemetry an instrumentation emits (instrumentation scope name, span
  names, attributes, metric names, and units) is part of its observable
  contract, which users build dashboards, alerts, and queries on. A change to
  this contract, including one that results from adopting a newer version of the
  semantic conventions, is a breaking change for the instrumentation. Where the
  conventions define a migration path, follow it and communicate the change
  clearly.
* Instrumentation that emits telemetry based on experimental (not-yet-stable)
  semantic conventions should make that clear to users. Where a stable
  convention also exists, prefer emitting it by default and gating the
  experimental output behind opt-in, so the default output stays stable.
* If no stable semantic convention exists for the instrumented domain, the
  instrumentation's own output cannot yet be stable. Keeping the library pre-1.0
  (a `0.x` version) signals to users that its telemetry may still change.

## Testing

Instrumentation authors are encouraged to test the telemetry their
instrumentation emits using OpenTelemetry's in-memory exporter, asserting on the
spans, metrics, and logs produced (including scope name and version, span and
metric names, attributes, status, and propagated context) without requiring a
full backend.

Beyond asserting on individual signals, instrumentation authors can add a CI
check that the emitted telemetry conforms to the
[Semantic Conventions](#semantic-conventions). For example, OpenTelemetry
[Weaver](https://github.com/open-telemetry/weaver)'s live-check can compare
telemetry against a semantic-convention registry and produce a compliance
report.
