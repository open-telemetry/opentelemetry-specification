# Process Context: Sharing Registered Instrumentations with External Readers

Extend the [Process Context](./profiles/4719-process-ctx.md) mechanism to publish the list of registered
auto-instrumentation libraries running inside an OpenTelemetry SDK, so external readers can coordinate with in-process
instrumentation.

## Motivation

[OTEP 4719: Process Context](./profiles/4719-process-ctx.md) introduced a mechanism for OpenTelemetry SDKs to publish
process-level resource attributes via a memory-mapped region readable by external processes. This OTEP extends that
mechanism to also publish the list of **registered auto-instrumentation libraries** active in the process.

The primary motivating consumer is [OpenTelemetry eBPF Instrumentation (OBI)](https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation),
OBI can detect if an application is already instrumented based on
heuristics [specified in OBI devdocs](https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/blob/main/devdocs/exclude-otel-instrumented-services.md)
but this comes with 2 big known limitations.

1. Duplicate telemetry may be emitted at the beginning of the process lifecycle before OBI can detect if the service is
   instrumented.
2. OBI instrumentation disabling works as "all or nothing", so if OBI detects any telemetry exported by the service, it
   disables all of its instrumentation modules, even those that do not overlap with the SDK's auto-instrumentation (
   e.g., if the SDK has HTTP auto-instrumentation but not Kafka, OBI disables both HTTP and Kafka modules,
   even though it can add this telemetry and not have duplication).

With this change OBI can read the list of registered auto-instrumentation libraries from the process context as soon as
it starts up, and disable only the overlapping modules, allowing it to add non-overlapping telemetry without
duplication.

Other external readers (e.g., ebpf-profiler, monitoring agents) can also use this information for richer context about
the process, or to coordinate their own instrumentation with the SDK's.

## Explanation

When an auto-instrumentation library activates inside an OpenTelemetry SDK, the component responsible for activating it
(the SDK itself, an auto-instrumentation agent, an instrumentor base class, or the contrib package's own initialization
— whichever is appropriate for the language) calls a new SDK API:

```text
process_context.register_instrumentation(scope)
```

The SDK records the registration in a process-global registry and publishes (or republishes) the process context
mapping per the [Process Context Publication / Updating Protocols](./profiles/4719-process-ctx.md#publication-protocol).
If no mapping has been created yet — for example because the SDK has not yet (or will never) publish a resource — the
first `register_instrumentation` call creates the mapping with an empty `Resource` and the registration under
`instrumentations`. This ensures auto-instrumentation libraries are visible to external readers even when no resource is
ever published by the SDK.

The registered instrumentations appear as an additional field on the `ProcessContext` message:

```text
ProcessContext {
  resource:         { service.name=..., service.instance.id=..., ... }   # already in 4719
  attributes:       [ ... ]                                                # already in 4719
  instrumentations: [
    { scope: { name: "opentelemetry-instrumentation-redis", version: "1.2.0" } }
    { scope: { name: "opentelemetry-instrumentation-jdbc",  version: "2.5.0" } }
    ...
  ]
}
```

### Manual instrumentations are not registered

Only auto-instrumentation libraries call `register_instrumentation`. User application code that calls
`tracer.start_span()` directly is **not** registered and does not appear in the published list. The list is, by
construction, the set of auto-instrumentations active in the process.

### Decoupled from tracer/meter/logger acquisition

`register_instrumentation` is a separate API call from `getTracer()`/`getMeter()`/`getLogger()`. A library typically
calls both — `register_instrumentation` to declare itself, and the relevant `get*()` methods to acquire handles. The
registry is not derived from observed `get*()` calls.

## Internal details

### Proto change

This OTEP adds one field to the existing `ProcessContext` message defined in OTEP 4719. The header format and discovery
mechanism are unchanged.

```protobuf
syntax = "proto3";

package opentelemetry.proto.processcontext.v1development;

import "opentelemetry/proto/common/v1/common.proto";
import "opentelemetry/proto/resource/v1/resource.proto";

message ProcessContext {
  // Existing fields from OTEP 4719 (unchanged):
  opentelemetry.proto.resource.v1.Resource resource = 1;
  repeated opentelemetry.proto.common.v1.KeyValue attributes = 2;

  // NEW: List of auto-instrumentation libraries registered in this process.
  // [Optional] Empty list (or absent field) means no instrumentations have
  // been registered, or the SDK does not implement this mechanism.
  repeated InstrumentationRecord instrumentations = 3;
}

// Status: [Development]
message InstrumentationRecord {
  // The instrumentation scope identifying this auto-instrumentation library.
  // Uniqueness is determined by the tuple (name, version, schema_url).
  opentelemetry.proto.common.v1.InstrumentationScope scope = 1;

  // Future fields are reserved for additive evolution
  // (see "Future possibilities").
}
```

This change is **backwards compatible at the wire level**: so version headers remain `2`,

### Registration API contract

SDKs that implement this OTEP MUST expose an API roughly equivalent to:

```text
process_context.register_instrumentation(scope: InstrumentationScope)
```

The API MUST satisfy:

1. **Idempotency.** Two registrations with the same `(scope.name, scope.version, scope.schema_url)` tuple are equivalent
   to one. Subsequent calls have no observable effect on the published payload.

2. **Self-sufficient publication.** `register_instrumentation` MUST be sufficient on its own to publish the process
   context. If no mapping exists yet, the first `register_instrumentation` call MUST create the memory mapping per the
   [OTEP 4719 Publication Protocol](./profiles/4719-process-ctx.md#publication-protocol), with an empty `Resource`
   message and the registered scope under `instrumentations`. Any subsequent resource publication by the SDK updates the
   resource portion of the existing mapping; subsequent registrations append to the existing registry.

   Symmetrically, when the SDK publishes a resource per OTEP 4719, it MUST include whatever registrations have already
   accumulated in the process-global registry, regardless of whether they arrived before or after the resource.

   This guarantees that auto-instrumentation libraries loaded in processes where the SDK never publishes a resource
   (e.g., a library bundles auto-instrumentation but the user does not configure resource attributes) are still visible
   to external readers.

3. **Eventually-consistent publication.** Each registration marks the process context dirty. The SDK MAY coalesce
   multiple registrations and republish the payload via
   the [OTEP 4719 Updating Protocol](./profiles/4719-process-ctx.md#updating-protocol). A staleness window of up to a
   few seconds between registration and publication is acceptable.

4. **No deregistration.** Once registered, a scope remains in the registry for the lifetime of the process. The registry
   is monotonically growing. The whole context is dropped only when the SDK shuts down (per OTEP 4719) or the process
   exits.

### When and by whom the API is called (non-normative)

The OTEP does not prescribe *when* or *by whom* `register_instrumentation` is called — that is a per-language SIG
decision driven by the language's idioms for activating auto-instrumentation. In most languages, an
**activation orchestrator** (rather than each library) is the natural caller. Sketches:

- **JavaScript** — `NodeSDK.start()` iterates its `instrumentations: [...]` array and registers each. Individual
  libraries don't call the API.
- **Java agent** — the agent registers each instrumentation module as it loads it. Individual modules don't call the
  API.
- **Python** — `BaseInstrumentor.instrument()` (the shared base class for all `*Instrumentor` implementations) calls
  the API once on behalf of every instrumentor that activates. Individual instrumentor implementations don't call the
  API.
- **Go** — no central orchestrator; each contrib instrumentation package calls the API itself from `init()` or on
  first use. This is the only language where individual libraries need to opt in directly.
- **Rust** — the application or SDK setup code calls `register_instrumentation` explicitly for each enabled library,
  mirroring the explicit resource-publication pattern.

## Trade-offs and mitigations

### External Readers must maintain a language→library mapping

The published `InstrumentationScope.name` is library-specific (e.g., `io.opentelemetry.netty-4.1`,
`opentelemetry-instrumentation-redis`, `go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp`). OBI's modules
are language-agnostic and capability-named (HTTP-server, Redis, Kafka, etc.). To dedupe, OBI must maintain a translation
table mapping known scope names to its own modules.

**Mitigation:** OBI (the motivating consumer) already maintains language-specific knowledge to function. The translation table is one more piece
of that. Future evolution (see "Future possibilities") may introduce a `covered_namespaces` field that lets
instrumentations self-declare semconv coverage in a language-agnostic way, reducing OBI's table to a one-line rule. v1
ships without this dependency.

### Privacy and security

Beyond the existing OTEP 4719 threat model, this OTEP exposes:

- Names and versions of auto-instrumentation libraries (could be used for stack fingerprinting).
- Scope-level attributes set by the instrumentation library.

**Mitigations:**
- Instrumentation scope `attributes` published via process context MUST be invariant for the lifetime of the scope and
  MUST NOT contain user data, request-specific data, or secrets. SDKs MAY enforce this by rejecting registrations whose
  attributes change between calls.
- Exporter endpoints, propagator configuration, sampler configuration, and other potentially-sensitive SDK state are
  explicitly **out of scope** for this OTEP. They may be revisited in future work with appropriate controls.

## Future possibilities

The `InstrumentationRecord` message is intentionally minimal in v1, leaving room for additive evolution. Each item below
could be a follow-up OTEP in its own right:

- **Signal types per scope** (`repeated SignalType signal_types`). Lets consumers reason about which signals (
  TRACES/METRICS/LOGS/PROFILES) each scope produces. Deferred because reliable self-declaration by library authors is
  required for this.

- **Covered semantic-convention namespaces** (`repeated string covered_namespaces`). Lets instrumentations self-declare
  which top-level semconv namespaces they emit attributes in (e.g., `"http.client"`, `"db.redis"`, `"messaging.kafka"`).
  This would eliminate OBI's need for per-language scope-name mapping tables — OBI could match its own modules to
  namespaces directly. Deferred for the same reason as `signal_types`.

- **Sampler / sampling configuration.** Process-level sampler description and (where applicable) the W3C
  consistent-sampling threshold, enabling external readers to make sampling decisions consistent with the SDK. Deferred
  for simplicity.

- **Source enum (`AUTO_INSTRUMENTATION` / `MANUAL` / `UNKNOWN`).** Currently unnecessary because the registry is
  auto-only by construction. Becomes relevant only if a use case emerges for tracking manual instrumentation in the
  published list.