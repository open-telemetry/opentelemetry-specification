# Process Context: Sharing Registered Instrumentations with External Readers

Extend the [Process Context](./profiles/4719-process-ctx.md) mechanism to publish the list of registered
instrumentation libraries running inside an OpenTelemetry SDK, so external readers can coordinate with in-process
instrumentation.

The list is published as a semantic-convention attribute inside the existing `ProcessContext.attributes` collection.
No change to the process context protocol is required.

## Motivation

[OTEP 4719: Process Context](./profiles/4719-process-ctx.md) introduced a mechanism for OpenTelemetry SDKs to publish
process-level resource attributes via a memory-mapped region readable by external processes. This OTEP extends that
mechanism to also publish the list of **registered instrumentation libraries** active in the process.

The primary motivating consumer is [OpenTelemetry eBPF Instrumentation (OBI)](https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation).
OBI can detect if an application is already instrumented based on
heuristics [specified in OBI devdocs](https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/blob/e2f806535af8505d09b074a78153c52170e40683/devdocs/exclude-otel-instrumented-services.md),
but this comes with 2 big known limitations.

1. Duplicate telemetry may be emitted at the beginning of the process lifecycle before OBI can detect if the service is
   instrumented.
2. OBI instrumentation disabling works as "all or nothing", so if OBI detects any telemetry exported by the service, it
   disables all of its instrumentation modules, even those that do not overlap with the SDK's instrumentation libraries
   (e.g., if the SDK has HTTP instrumentation but not Kafka, OBI disables both HTTP and Kafka modules,
   even though it can add this telemetry and not have duplication).

With this change OBI can read the list of registered instrumentation libraries from the process context as soon as
it starts up, and disable only the overlapping modules, allowing it to add non-overlapping telemetry without
duplication.

Other external readers (e.g., eBPF profiler, monitoring agents) can also use this information for richer context about
the process, or to coordinate their own instrumentation with the SDK's.

## Explanation

When an instrumentation library activates inside an OpenTelemetry SDK, the component responsible for activating it
(the SDK itself, an automatic instrumentation agent, an instrumentor base class, or the contrib package's own
initialization — whichever is appropriate for the language) calls a new SDK API:

```text
process_context.register_instrumentation(scope)
```

The SDK records the registration in a process-global registry and publishes (or republishes) the process context
mapping per the [Process Context Publication / Updating Protocols](./profiles/4719-process-ctx.md#publication-protocol).
If no mapping has been created yet — for example because the SDK has not yet (or will never) publish a resource — the
first `register_instrumentation` call creates the mapping with an empty `Resource` and the registration under the
`otel.instrumentations` attribute. This ensures instrumentation libraries are visible to external readers even when no
resource is ever published by the SDK.

The registered instrumentations appear as a single entry in the `ProcessContext.attributes` collection already defined
by OTEP 4719, keyed `otel.instrumentations`. Its value is an array of maps, one map per registered instrumentation
library:

```text
ProcessContext {
  resource:   { service.name=..., service.instance.id=..., ... }   # already in 4719
  attributes: [                                                    # already in 4719
    otel.instrumentations = [
      { otel.scope.name: "opentelemetry-instrumentation-redis", otel.scope.version: "1.2.0" },
      { otel.scope.name: "opentelemetry-instrumentation-jdbc",  otel.scope.version: "2.5.0" },
      ...
    ]
  ]
}
```

The keys inside each map are the existing OpenTelemetry
[scope attributes](https://opentelemetry.io/docs/specs/semconv/registry/attributes/otel/#otel-scope-name)
(`otel.scope.name`, `otel.scope.version`, `otel.scope.schema_url`), so readers that already know how to interpret an
instrumentation scope need no new vocabulary.

### Manual instrumentations are not registered

Only instrumentation libraries call `register_instrumentation`. User application code that calls
`tracer.start_span()` directly is **not** registered and does not appear in the published list. The list is, by
construction, the set of instrumentation libraries active in the process.

### Decoupled from tracer/meter/logger acquisition

`register_instrumentation` is a separate API call from `getTracer()`/`getMeter()`/`getLogger()`. A library typically
calls both — `register_instrumentation` to declare itself, and the relevant `get*()` methods to acquire handles. The
registry is not derived from observed `get*()` calls.

## Internal details

This OTEP does not change the process context protocol. `ProcessContext.attributes` is already a collection of
`KeyValue`, and an OpenTelemetry [`AnyValue`](../specification/common/README.md#anyvalue) may be an array of
`map<string, AnyValue>`, so the payload is expressible with the message exactly as OTEP 4719 specifies it. Readers that
do not understand the key skip it, as they would any other unknown attribute.

### Semantic conventions

The schema of the payload is defined in the semantic conventions rather than in the protocol. This OTEP proposes a
registry group in the `otel` namespace:

```yaml
groups:
  - id: registry.otel.instrumentations
    type: attribute_group
    display_name: OTel Instrumentation Attributes
    brief: Attributes describing the instrumentation libraries registered in a process.
    attributes:
      - id: otel.instrumentations
        type: any
        stability: development
        annotations:
          type:
            json_schema: model/otel/otel-instrumentations.json
        brief: >
          The set of instrumentation libraries registered in the process.
        note: |
          The value is an array of maps, one map per registered instrumentation library,
          as defined by the referenced JSON schema.

          The array is unordered. Readers MUST NOT rely on the position of an entry.
        examples:
          - [
              { "otel.scope.name": "opentelemetry-instrumentation-redis", "otel.scope.version": "1.2.0" },
              { "otel.scope.name": "opentelemetry-instrumentation-jdbc", "otel.scope.version": "2.5.0" },
            ]
```

The semantic conventions have no structured attribute type: an attribute's `type` may be a primitive, an array of
primitives, a `template[...]`, an `enum`, or `any`. Structured values are therefore declared as `type: any` with the
shape given by an accompanying JSON schema, the convention established by the GenAI conventions for
`gen_ai.input.messages`, `gen_ai.output.messages`, `gen_ai.tool.definitions` and others. The pairing is enforced rather
than conventional — a registry policy rejects any attribute declared `type: any` that does not carry a
`annotations.type.json_schema` reference — so the schema below is a required companion to the group above, not
documentation.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "description": "The set of instrumentation libraries registered in the process.",
  "type": "array",
  "items": {
    "type": "object",
    "description": "A single registered instrumentation library.",
    "properties": {
      "otel.scope.name": {
        "type": "string",
        "description": "The name of the instrumentation scope (InstrumentationScope.name in OTLP)."
      },
      "otel.scope.version": {
        "type": "string",
        "description": "The version of the instrumentation scope (InstrumentationScope.version in OTLP)."
      },
      "otel.scope.schema_url": {
        "type": "string",
        "description": "The schema URL of the instrumentation scope."
      }
    },
    "required": ["otel.scope.name"],
    "additionalProperties": true
  }
}
```

`additionalProperties` is left open so that keys added by later revisions, or by a publisher that implements more than
this OTEP, do not invalidate the payload. Readers MUST ignore keys they do not understand.

The resulting requirement levels are:

| Key                     | Type   | Requirement level | Notes                                                      |
|-------------------------|--------|-------------------|------------------------------------------------------------|
| `otel.scope.name`       | string | Required          | `InstrumentationScope.name`; already a stable attribute    |
| `otel.scope.version`    | string | Recommended       | `InstrumentationScope.version`; already a stable attribute |
| `otel.scope.schema_url` | string | Opt-In            | `InstrumentationScope.schema_url`                          |

Reusing `otel.scope.*` as the map keys means the identity of a published instrumentation is expressed with the same
vocabulary as the corresponding OTLP `InstrumentationScope`, including `schema_url`, which is a sibling field of
`InstrumentationScope` in OTLP and therefore not otherwise expressible.

One map per instrumentation is preferred over index-suffixed keys or parallel arrays of names and versions: it keeps
each instrumentation's fields together so entries cannot drift out of alignment, and a new per-instrumentation field is
a new key in the map rather than another top-level attribute that must be kept consistent with the others.

Instrumentation scope `attributes` are deliberately not part of this convention in v1; see "Privacy and security" and
"Future possibilities".

### Registration API contract

SDKs that implement this OTEP MUST expose an API roughly equivalent to:

```text
process_context.register_instrumentation(scope: InstrumentationScope)
```

The API MUST satisfy:

1. **Idempotency.** Two registrations with the same `(scope.name, scope.version, scope.schema_url)` tuple are
   equivalent to one. Subsequent calls have no observable effect on the published payload. Registrations that differ in
   any element of the tuple are distinct entries in the published array.

2. **Self-sufficient publication.** `register_instrumentation` MUST be sufficient on its own to publish the process
   context. If no mapping exists yet, the first `register_instrumentation` call MUST create the memory mapping per the
   [OTEP 4719 Publication Protocol](./profiles/4719-process-ctx.md#publication-protocol), with an empty `Resource`
   message and the registered scope in the `otel.instrumentations` attribute. Any subsequent resource publication by
   the SDK updates the resource portion of the existing mapping; subsequent registrations are appended to the existing
   `otel.instrumentations` value.

   Symmetrically, when the SDK publishes a resource per OTEP 4719, it MUST include whatever registrations have already
   accumulated in the process-global registry, regardless of whether they arrived before or after the resource.

   This guarantees that instrumentation libraries loaded in processes where the SDK never publishes a resource
   (e.g., a library bundles instrumentation but the user does not configure resource attributes) are still visible
   to external readers.

3. **Eventually-consistent publication.** Each registration marks the process context dirty. The SDK MAY coalesce
   multiple registrations and republish the payload via
   the [OTEP 4719 Updating Protocol](./profiles/4719-process-ctx.md#updating-protocol). A staleness window of up to a
   few seconds between registration and publication is acceptable.

4. **No deregistration.** Once registered, a scope remains in the registry for the lifetime of the process. The registry
   is monotonically growing. The whole context is dropped only when the SDK shuts down (per OTEP 4719) or the process
   exits.

5. **Single attribute.** The SDK MUST publish at most one `otel.instrumentations` entry in
   `ProcessContext.attributes`, per the uniqueness requirement OTEP 4719 places on that collection. When the registry is
   empty, the SDK SHOULD omit the attribute rather than publish an empty array.

### When and by whom the API is called (non-normative)

The OTEP does not prescribe *when* or *by whom* `register_instrumentation` is called — that is a per-language SIG
decision driven by the language's idioms for activating instrumentation libraries. In most languages, an
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

### The payload schema is not enforced by the protocol

Because the value is an `any`-typed attribute rather than a dedicated message, protobuf does not validate the shape of
each entry. A publisher can emit a map missing `otel.scope.name`, or a value that is not an array at all, and the
protocol will not reject it.

**Mitigation:** the shape is still declared machine-readably, as a JSON schema carried by the attribute definition, so
a publisher can be validated against it in tests and a reader can validate what it receives. What is lost relative to a
dedicated protobuf message is enforcement at deserialization time, not the schema itself. The cost is further bounded by
the fact that both the publisher (an OpenTelemetry SDK) and the consumer are OpenTelemetry components, and the required
part of the schema is a single key. Readers MUST tolerate malformed entries by skipping them rather than rejecting the
whole payload.

### External Readers must maintain a language→library mapping

The published `otel.scope.name` is library-specific (e.g., `io.opentelemetry.netty-4.1`,
`opentelemetry-instrumentation-redis`, `go.opentelemetry.io/contrib/instrumentation/net/http/otelhttp`). OBI's modules
are language-agnostic and capability-named (HTTP-server, Redis, Kafka, etc.). To dedupe, OBI must maintain a translation
table mapping known scope names to its own modules.

**Mitigation:** OBI (the motivating consumer) already maintains language-specific knowledge to function. The translation
table is one more piece of that. Future evolution (see "Future possibilities") may introduce a `covered_namespaces` key
that lets instrumentations self-declare semconv coverage in a language-agnostic way, reducing OBI's table to a one-line
rule. v1 ships without this dependency.

### Privacy and security

Beyond the existing OTEP 4719 threat model, this OTEP exposes the names and versions of instrumentation libraries, which
could be used for stack fingerprinting.

**Mitigations:**

- Instrumentation scope `attributes` are not published by this OTEP. Should a future revision add them, they MUST be
  invariant for the lifetime of the scope and MUST NOT contain user data, request-specific data, or secrets.
- Exporter endpoints, propagator configuration, sampler configuration, and other potentially-sensitive SDK state are
  explicitly **out of scope** for this OTEP. They may be revisited in future work with appropriate controls.

## Open questions

- **Namespace and attribute name.** This OTEP proposes `otel.instrumentations`, reusing the `otel` namespace that
  already holds `otel.scope.*`. A dedicated `instrumentation` namespace (e.g. `instrumentation.libraries`) was also
  suggested. This is a naming decision for the semantic conventions maintainers and does not affect the payload shape.

- **Where the convention lives.** The attribute is only ever published over process context, never over OTLP. It may
  belong in the general semantic conventions registry alongside `otel.scope.*`, or in a process-context-specific area
  of the registry.

- **How the structure is declared.** `type: any` plus a JSON schema is what the semantic conventions offer today, and
  the GenAI conventions have already established it. A first-class complex type for attributes is being designed
  ([weaver#892](https://github.com/open-telemetry/weaver/issues/892)); the model already expresses structured values
  natively as `map[]` with declared `fields`, but only for event bodies. If a native declaration lands before this OTEP
  is implemented, the attribute should adopt it and the JSON schema should be dropped. The published payload is
  unaffected either way.

- **Attribute versus dedicated schema-free field.** This OTEP publishes the array through `ProcessContext.attributes`,
  so the protocol is untouched. A dedicated `ProcessContext` field typed
  `repeated opentelemetry.proto.common.v1.KeyValueList`, with the semantic conventions still defining the keys, was
  also suggested. That variant makes the payload easier to locate for a reader that does not scan attributes, at the
  cost of a protocol revision that this OTEP otherwise avoids. The per-entry schema is identical either way, so this
  can be settled independently of the rest of the proposal.

- **Publishing scope attributes.** `InstrumentationScope.attributes` are omitted in v1. If a consumer use case appears,
  they can be added as a nested `otel.scope.attributes` map key, subject to the invariance constraint in
  "Privacy and security".

## Future possibilities

The per-instrumentation map is intentionally minimal in v1. Because it is a map, each item below is a new key with a
requirement level, not a protocol change. Each could be a follow-up in its own right:

- **Signal types per scope** (`otel.scope.signals`, e.g. `["traces", "metrics"]`). Lets consumers reason about which
  signals each scope produces. Deferred because reliable self-declaration by library authors is required for this.

- **Covered semantic-convention namespaces** (`otel.scope.covered_namespaces`, e.g. `["http.client"`, `"db.redis"`,
  `"messaging.kafka"]`). Lets instrumentations self-declare which top-level semconv namespaces they emit attributes in.
  This would eliminate OBI's need for per-language scope-name mapping tables — OBI could match its own modules to
  namespaces directly. Deferred for the same reason as signal types.

- **Per-instrumentation language.** `telemetry.sdk.language` on the resource covers the common case, but a process can
  host instrumentation libraries written in more than one language
  (see [community#3483](https://github.com/open-telemetry/community/issues/3483)). A per-entry language key can be added
  when that case needs to be distinguished.

- **Sampler / sampling configuration.** Process-level sampler description and (where applicable) the W3C
  consistent-sampling threshold, enabling external readers to make sampling decisions consistent with the SDK. Deferred
  for simplicity.

- **Source enum (`AUTO_INSTRUMENTATION` / `MANUAL` / `UNKNOWN`).** Currently unnecessary because the registry is
  auto-only by construction. Becomes relevant only if a use case emerges for tracking manual instrumentation in the
  published list.
