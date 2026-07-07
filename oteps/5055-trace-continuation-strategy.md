# Trace Continuation Strategy

Introduce an SDK component that decides whether an extracted or active trace
context is continued, restarted with a link, or restarted without a link.
The component is similar to the sampler in lifecycle and configurability, but it
answers a different question: which trace context, if any, is used for
continuation across a boundary?

## Motivation

OpenTelemetry currently defaults to continuing remote parent context when
extracting and starting server spans. This behavior works well inside a single
trust domain, but it is insufficient for common boundary scenarios discussed in
issue #1633.

When context is continued unchanged across trust boundaries, users report the
following problems:

- Multiple organizations share a trace ID even though they cannot share full
  trace data.
- Callee services inherit upstream sampling decisions that can be unsafe or
  undesirable for local policies.
- Baggage can be propagated to external systems where it can expose sensitive or
  internal information.
- Automatic instrumentation lacks a standard way to apply boundary behavior
  consistently without manual per-call code.

These scenarios are common in practice, for example:

- third-party API calls,
- webhooks,
- synthetic monitoring and edge traffic,
- mixed internal/external API gateway usage,
- local sidecars/proxies where trace headers can cause functional side effects,
- SaaS products that need both an internal trace and a customer-facing trace.

The important commonality is that the decision is rarely based only on the
incoming propagation headers. A boundary can be identified by route, host,
destination, transport, authorization state, tenant, audience, deployment
metadata, or instrumentation-specific attributes. Propagators parse wire context,
but they do not reliably have access to those trusted inputs.

Users need a standard strategy to preserve causal relationships without always
continuing parentage across boundaries. A restart-based approach provides that
strategy by letting implementations either preserve correlation through links or
drop remote trace continuity entirely when policy requires it.

Standardizing this behavior in OpenTelemetry gives:

- safer default building blocks for boundary-aware instrumentation,
- a shared cross-language contract between propagation and tracing components,
- better interoperability for zero-code and library instrumentation,
- one SDK-level policy mechanism instead of many instrumentation-specific
  callbacks.

## Explanation

This proposal defines a policy-driven trace continuation model for trust and
propagation boundaries. Existing propagators continue to parse and inject trace
context. A new SDK component, provisionally called the **Trace Continuation
Decider**, evaluates richer boundary inputs and chooses how trace context is
used.

The decider produces one of three trace continuation strategies:

1. **CONTINUE**: use the candidate `SpanContext` as the parent according to
   existing parentage rules.
2. **RESTART_WITH_LINK**: do not use the candidate `SpanContext` as a parent.
   Start a new trace and add a link to the candidate context when creating the
   restarted root span.
3. **RESTART_WITHOUT_LINK**: do not use the candidate `SpanContext` as a parent
   and do not preserve it as a link.

The decider is similar to a sampler because it is an SDK component that evaluates
a structured input and returns a structured decision. It is not a sampler because
it does not decide whether a span is recorded or sampled. It decides which trace
context, if any, is eligible for parentage or linking.

### Why not decide in propagators?

A propagator can see a carrier and the values encoded in that carrier. It cannot
reliably know whether an HTTP request matched an external webhook route, whether
the remote caller was authenticated as a tenant, whether an outgoing request is
headed to a third-party SaaS provider, or whether the current process is inside a
company perimeter.

Some of these values can appear in headers, but they are not equivalent to a
trusted policy input. In particular, client-provided `tracestate` is not a secure
basis for enforcing a trust boundary. A policy that depends only on trace headers
is useful for some operational routing cases, but it is too narrow for security,
tenancy, and SaaS audience boundaries.

Moving the decision into the SDK lets instrumentation supply trusted or derived
metadata before the decision is made, while preserving the existing W3C Trace
Context and Baggage wire formats.

### Component lifecycle

The Trace Continuation Decider runs after propagation has produced a candidate
context and before the SDK finalizes parentage for a new span or propagates
context across an outgoing boundary.

For ingress, the lifecycle is:

1. Instrumentation receives a request and invokes propagators to extract a remote
   context candidate.
2. Instrumentation and the SDK assemble a trace continuation input containing the
   candidate context and available request metadata.
3. The decider returns `CONTINUE`, `RESTART_WITH_LINK`, or
   `RESTART_WITHOUT_LINK`.
4. Span start logic applies the decision before sampling.
5. The sampler evaluates the span with the final parentage context.

For egress, the lifecycle is:

1. Instrumentation prepares an outgoing request and identifies the current active
   context or other propagation candidate.
2. Instrumentation and the SDK assemble a trace continuation input containing the
   destination metadata and active context candidate.
3. The decider returns an egress propagation action.
4. Injection logic applies that decision before writing propagation headers.

This proposal intentionally separates propagation parsing from continuation
policy. Language implementations MAY integrate the mechanics differently, but the
observable behavior SHOULD match this lifecycle.

### Decision input

The decider input SHOULD be a structured value with fields equivalent to:

- the `Context`,
- direction: `ingress` or `egress`,
- span kind,
- span attributes: including route, host, path, method, destination, transport, or peer metadata provided by
  instrumentation,

Authorization, tenant, audience, or perimeter hints when provided by trusted application or instrumentation
code can be passed in the `Context` or as span attributes.

Not every implementation or instrumentation can provide every field. The decider
contract is defined around inputs that can be absent and deterministic behavior
when inputs are absent.

### Decision result

The ingress decider result SHOULD contain:

- a trace continuation strategy,
- OPTIONAL link attributes to attach when the strategy is `RESTART_WITH_LINK`,
- OPTIONAL diagnostic attributes or reason codes for implementation-specific
  observability,
- OPTIONAL baggage or propagation actions if baggage control remains in scope.

The link attributes are useful for recording why a causal relationship was
preserved without parentage. For example, an implementation might record that the
link represents an external audience, public endpoint, partner boundary, or
policy rule. Exact attribute names are left open by this OTEP.

### Conceptual request flows

Normal continuation:

- Extract remote context.
- Assemble trace continuation input from the remote context and request metadata.
- Decider returns `CONTINUE`.
- Start span as a child of the remote parent.
- Sampler runs with the continued parentage.

Boundary restart with link:

- Extract remote context.
- Assemble trace continuation input from the remote context and trusted boundary
  metadata.
- Decider returns `RESTART_WITH_LINK`.
- Start a new root span.
- Add one link to the extracted remote context, including any link attributes
  returned by the decider.
- Sampler runs for the new root span.

Boundary restart without link:

- Extract remote context.
- Assemble trace continuation input from the remote context and trusted boundary
  metadata.
- Decider returns `RESTART_WITHOUT_LINK`.
- Start a new root span with no parent and no automatic link to the incoming
  context.
- Sampler runs for the new root span.

Egress suppression:

- An outgoing request is prepared with an active in-process context.
- Instrumentation provides the span attributes.
- Decider returns an egress propagation action such as
  `SUPPRESS_TRACE_CONTEXT`.
- Injection omits the suppressed trace context while preserving other configured
  propagation behavior.

### Audience framing

Some SaaS products need to reason about more than one audience. A request can
arrive with a customer trace context, while the service also needs an internal
trace for its own operations. In that case, the customer context is useful causal
information, but it does not necessarily become the default parent for the
internal trace.

This proposal treats the default OpenTelemetry context as the current audience's
trace context. A decider can restart the default trace while preserving the
incoming audience context as a link, or can discontinue it entirely. Future work
can define more explicit multi-audience context handling, but that is not part of
the initial continuation strategy.

### Configuration model

The canonical configuration schema for this component SHOULD be defined in
`opentelemetry-configuration`.

Configuration SHOULD follow the same structural conventions used by
`ExperimentalComposableRuleBasedSampler` and
`ExperimentalComposableRuleBasedSamplerRule`:

- a trace continuation decider configuration object contains a `rules` array,
- rules are matched in order,
- each rule can contain multiple match conditions and all conditions in a rule
  MUST match,
- if no conditions are specified, the rule matches all inputs that reach it,
- if no rule matches, the decider falls back to its default behavior.

The default behavior SHOULD preserve existing OpenTelemetry behavior. For
ingress, the default strategy SHOULD be `CONTINUE`. For egress, the default
propagation action SHOULD be `INJECT_TRACE_CONTEXT`. Deployments that enforce
security or tenant boundaries SHOULD be able to configure allowlist-style
policies where continuation is permitted only for known trusted inputs and all
other candidates restart or are dropped.

Rules SHOULD distinguish match inputs from rule outputs:

- `direction` SHOULD be a first-class rule condition with values equivalent to
  `ingress` and `egress`.
- `span_kind` SHOULD be a first-class rule condition when span kind is known.
- `attributes` SHOULD match span, request, route, destination, transport, or
  other trusted metadata provided by instrumentation. Direction SHOULD NOT be
  represented as a synthetic attribute.
- Ingress rules SHOULD produce a trace continuation `strategy`.
- Egress rules SHOULD produce an `egress_action`.
- `link_attributes` SHOULD only apply when the selected ingress strategy is
  `RESTART_WITH_LINK`.

For operator convenience, implementations MAY accept `strategy` on an egress
rule and map `CONTINUE` to `INJECT_TRACE_CONTEXT` and restart strategies to
`SUPPRESS_TRACE_CONTEXT`, but the canonical configuration model SHOULD expose
egress propagation actions explicitly.

Illustrative configuration shape using placeholder extension names:

```yaml
tracer_provider:
  trace_continuation_decider:
    rule_based/development:
      default_ingress_strategy: restart_with_link
      default_egress_action: inject_trace_context
      rules:
        - direction: ingress
          span_kind: server
          conditions:
            attributes:
              http.route: /internal/*
              net.host.name: internal.example.com
          strategy: continue
        - direction: ingress
          span_kind: server
          conditions:
            attributes:
              http.route: /webhooks/*
          strategy: restart_with_link
          link_attributes:
            otel.trace_continuation.reason: external_webhook
        - direction: egress
          span_kind: client
          conditions:
            attributes:
              server.address: api.third-party.example
          egress_action: suppress_trace_context
```

The exact schema shape remains to be standardized. The important requirements are
that the model supports ordered rules, reusable condition objects, direction-aware
matching, separate ingress and egress outputs, and conservative allowlist
deployment patterns.

## Internal details

### Behavioral contract

This proposal introduces a cross-component behavioral contract between
instrumentation, propagation, tracing, and sampling:

- Propagators parse or inject trace context but do not make the final boundary
  policy decision.
- Instrumentation SHOULD provide relevant request, route, destination, and
  trusted application metadata when available.
- The SDK invokes the Trace Continuation Decider before final parentage is chosen
  for a span.
- The SDK invokes the sampler after trace continuation has established the span's
  parentage or root status.
- Restart-with-link uses existing span links to preserve causal relationship
  without parentage.

Language implementations MAY store either a `Link` or enough information to
construct one later, but MUST preserve the semantic contract across decider,
propagator, and tracer components.

### Required ingress behavior

When trace continuation is evaluated for an extracted remote context:

1. Extraction logic MUST parse incoming remote context according to existing
   propagator behavior.
2. Decider evaluation MUST be deterministic for a given input and configuration.
3. If multiple configured rules match, implementations SHOULD use first-match
   wins rule order.
4. If no configured rule matches, implementations SHOULD preserve existing
   continuation behavior unless configured otherwise.

When the selected strategy is `CONTINUE`:

1. The candidate remote context MUST be eligible for parentage according to
   existing parentage rules.
2. Any pending-link value associated with that candidate MUST NOT be left behind.

When the selected strategy is `RESTART_WITH_LINK`:

1. Span start logic MUST NOT use the candidate remote context as the active
   parent.
2. Span start logic MUST create a new root span unless an explicit in-process
   parent override takes precedence.
3. Span start logic SHOULD add exactly one automatic link to the candidate remote
   context.
4. If the decider returns link attributes, implementations SHOULD attach them to
   the automatic link.

When the selected strategy is `RESTART_WITHOUT_LINK`:

1. Span start logic MUST NOT use the candidate remote context as the active
   parent.
2. Span start logic MUST NOT create an automatic link for that candidate.

### Parentage precedence

To avoid ambiguous behavior, span start logic MUST use the following parentage
order:

1. Explicit API parent override, if provided by the caller.
2. Active in-process span context.
3. Extracted remote parent context under the `CONTINUE` strategy.
4. Root span if none apply.

A candidate selected for `RESTART_WITH_LINK` or `RESTART_WITHOUT_LINK` MUST NOT
be used as a parent in this order.

### Link consumption

If the implementation stores a pending link before span start, that value is a
one-shot hint for the restarted root span. Child spans MUST NOT inherit a pending
link that was intended only for the restarted root span.

If user code supplied explicit links at span start, implementations MUST preserve
those links when adding the automatic continuation link.

### Required egress behavior

When trace continuation is evaluated for egress:

1. Injection logic MUST preserve existing propagator behavior when the decider
   returns `INJECT_TRACE_CONTEXT`.
2. If the selected action is `SUPPRESS_TRACE_CONTEXT`, injection logic MUST NOT
   propagate the suppressed trace context as the active parent context for that
   destination.
3. Egress decisions MUST be direction-aware so an ingress rule does not
   accidentally suppress unrelated outgoing propagation, or vice versa.

Egress is about propagation, not span parentage. The egress result SHOULD
therefore be represented as an explicit propagation action rather than a
parentage restart strategy. The initial egress actions are:

1. `INJECT_TRACE_CONTEXT`: preserve existing trace context injection behavior.
2. `SUPPRESS_TRACE_CONTEXT`: do not inject the selected trace context for this
   outgoing boundary.

Rule-based configuration MAY use the same strategy names as ingress for
operator convenience. If so, implementations SHOULD map `CONTINUE` to
`INJECT_TRACE_CONTEXT` and map restart strategies to `SUPPRESS_TRACE_CONTEXT`.
Language implementations MAY represent the selected egress action using context
state, span state, an SDK propagation hook, or another mechanism, but injection
MUST observe the selected action before writing propagation headers.

### Interaction with samplers

The Trace Continuation Decider runs before the sampler observes the span's final
parentage. This ordering is important because parent-based samplers and
attribute-based samplers need to evaluate the span that will actually be created.

The decider MUST NOT make recording or sampling decisions. A sampler does not
need to understand why parentage was continued or restarted. Implementations
MAY expose decider diagnostics as span attributes or metrics, but those
observability details are not part of the sampling decision.

### Interaction with baggage

This OTEP keeps baggage filtering out of the initial normative scope.

Baggage filtering is related operationally because the same boundaries often need
both trace restart and baggage suppression. However, combining both in the first
version would make the new SDK component decide parentage, linking, context
injection, and baggage filtering at once. That risks obscuring the core trace
continuation behavior.

The proposed first version standardizes trace continuation decisions and SDK
consumption semantics. Baggage filtering is treated as one of:

- a follow-up OTEP using the same decision input and rule vocabulary,
- an OPTIONAL extension point on the decider result,
- a separate rule-based baggage propagator or processor if the SIG prefers to
  keep baggage behavior near propagation.

Any future baggage design needs to cover both ingress and egress and support
allowlist-style deployment for sensitive boundaries.

### Error modes and handling

- Invalid extracted remote context: ignore it and keep existing behavior.
- No matching rule: default to `CONTINUE` unless configuration explicitly chooses
  a different default.
- Missing trusted metadata: evaluate deterministically using the inputs that are
  available.
- Missing or invalid pending-link value at span start: start a new root span
  without an automatically added link.
- Duplicate or conflicting pending-link candidates: implementation SHOULD keep a
  single deterministic candidate and create at most one automatic link by
  default.

### Corner cases

- If both a current in-process span and a restartable remote candidate exist,
  current in-process span parentage rules win unless the caller explicitly asks
  to evaluate the remote candidate as the parent.
- If explicit links are provided at span start, the automatic continuation link
  is additive rather than replacing user-supplied links.
- If sampling flags or `tracestate` arrive in the remote context, they MUST NOT
  force parentage continuation under a restart strategy.
- Trace restart-with-link does not require baggage propagation.
- Egress suppression of trace context does not imply suppression of all other
  propagation formats unless separately configured.

## Examples

### Public webhook endpoint

A service exposes `/webhooks/{partner}` to external systems and `/internal/*` to
internal callers. Both routes can carry W3C Trace Context. The external webhook
route is authenticated, but the incoming trace belongs to the partner audience,
not the service's internal trace.

For `/webhooks/{partner}` the decider returns `RESTART_WITH_LINK`. The SDK starts
a new internal root span and links to the partner-provided context. Internal child
spans follow the new trace. The partner context is visible as causal information
without becoming the default parent.

For `/internal/*` the decider returns `CONTINUE`, so internal service-to-service
calls preserve the existing trace ID and parent chain.

### SaaS internal and customer traces

A SaaS service receives a request made on behalf of a customer. The customer
wants to trace the call through the SaaS boundary, while the SaaS operator needs a
separate internal trace for authorization, fanout, database calls, and background
work.

The decider uses trusted authorization or tenant metadata supplied by the
application or instrumentation. It starts a new internal trace and links to the
incoming customer context. The internal trace can be sampled, retained, and
shared according to the SaaS operator's policy without requiring the customer
trace ID to become the internal trace ID.

### Egress to third-party SaaS

A service calls both internal dependencies and an external SaaS API. The active
in-process span is valid for internal calls, but the operator does not want to
propagate internal trace context to the external provider.

For internal destinations the decider returns `CONTINUE`, and injectors preserve
normal trace context propagation. For the external SaaS destination the decider
returns a restart or suppression decision, and injection omits the internal trace
context for that outgoing request.

## Trade-offs and mitigations

### Trade-off: A new SDK component adds surface area

Adding a component increases SDK complexity and configuration surface.

Mitigation:

- Reuse sampler-style configuration and rule semantics where possible.
- Keep the first version focused on trace continuation only.
- Avoid requiring every language to expose identical helper classes.

### Trade-off: Trace tree continuity is broken at boundaries

Restarting at a boundary creates a new root span, so parent/child continuity is no
longer represented as a single tree in one trace.

Mitigation:

- Preserve causal relationship using a span link when policy selects
  `RESTART_WITH_LINK`.
- Allow link attributes to describe the boundary or audience relationship.
- Document backend query patterns that use links.

### Trade-off: Instrumentation metadata availability varies

Some instrumentations can provide route, host, destination, and auth metadata;
others cannot.

Mitigation:

- Define inputs that can be absent and deterministic behavior when inputs are
  absent.
- Let simple deployments use carrier-only or resource-only rules.
- Encourage instrumentations to provide standard semantic convention attributes
  before invoking the decider when practical.

### Trade-off: Policy misconfiguration can over-fragment traces

If restart rules are too broad, users can unintentionally restart too many
requests and reduce end-to-end trace readability.

Mitigation:

- Preserve `CONTINUE` as the compatibility default.
- Support allowlist defaults for deployments that need strict trust boundaries.
- Encourage diagnostics such as counts of `continue`, `restart_with_link`, and
  `restart_without_link` decisions.

### Trade-off: Relationship to baggage controls can be confusing

Users often want both trace restart and baggage suppression or filtering.

Mitigation:

- Keep baggage out of the initial normative scope.
- Require any future baggage work to cover both ingress and egress.
- Reuse the same rule vocabulary if baggage filtering becomes a follow-up.

### Trade-off: Security expectations can be overstated

Restarting trace parentage reduces correlation continuity but does not by itself
eliminate all metadata exposure risks.

Mitigation:

- Explicitly state that this proposal is not a full data-loss-prevention
  mechanism.
- Do not treat untrusted trace headers as sufficient trust-boundary inputs.
- Recommend combining continuation policy with authorization, network controls,
  and baggage governance where needed.

## Prior art and alternatives

### Prior art

The closest existing OpenTelemetry prior art is in `opentelemetry-go-contrib`
`otelhttp` via
[`WithPublicEndpointFn`](https://github.com/open-telemetry/opentelemetry-go-contrib/blob/instrumentation/net/http/otelhttp/v0.65.0/instrumentation/net/http/otelhttp/config.go#L99),
as used in
[handler logic](https://github.com/open-telemetry/opentelemetry-go-contrib/blob/dbf7b0a8a37a70ea1848bfdee02ff6c68b0fa9d6/instrumentation/net/http/otelhttp/handler.go#L103).
In that model, user-supplied logic decides when to start a new trace and link to
the extracted remote context.

The `opentelemetry-python` [prototype for the earlier version of this OTEP](https://github.com/open-telemetry/opentelemetry-python/pull/5134) implements:

- a `RuleBasedTraceContextTextMapPropagator`,
- three explicit trace strategies: `CONTINUE`, `RESTART_WITH_LINK`, and
  `RESTART_WITHOUT_LINK`,
- ordered first-match rule evaluation over `tracestate`,
- context helpers for storing and consuming a pending link,
- SDK logic that appends the pending link to restarted root spans without
  leaking it to child spans,
- a separate `RuleBasedW3CBaggagePropagator` with ordered `KEEP`/`DROP`
  semantics for selective baggage suppression.

That prototype demonstrates the restart/link behavior, but its policy placement
is too limited for the broader boundary cases described in this OTEP.

The `opentelemetry-configuration` repository provides configuration prior art for
rule-driven behavior. In particular, `ExperimentalComposableRuleBasedSampler`
demonstrates:

- a top-level plugin object,
- an ordered `rules` array,
- per-rule case sensitive match conditions with AND semantics,
- a match-all rule represented by omitting conditions,
- shared helper object shapes for exact-value and pattern-based matching.

### Alternatives considered

1. Keep the status quo, always continuing by default everywhere.
   - Rejected as insufficient for security, privacy, tenancy, and
     policy-controlled boundary scenarios described by users.

2. Implement restart behavior only in individual instrumentations.
   - Rejected as too inconsistent. Existing instrumentation hooks are useful
     prior art, but they do not provide a cross-language SDK contract or shared
     declarative configuration model.

3. Use rule-based propagators as the primary policy mechanism.
   - Rejected for this alternate direction. Propagators are a reasonable place to
     parse carriers, but they only see wire-format inputs. Trust-boundary policy
     often needs route, host, destination, authorization, audience, or deployment
     metadata that is unavailable or untrusted at propagation time.

4. Extend the sampler directly.
   - Attractive because samplers already have lifecycle similarities, rule
     engines, and access to useful attributes. Rejected as the initial proposal
     because sampling and trace continuation are separate decisions. Combining
     them risks confusing parentage with recording and sampling semantics.

5. Add a new SDK component adjacent to the sampler.
   - Preferred. It keeps trace continuation semantics separate from sampling
     while reusing sampler-style inputs, configuration patterns, and lifecycle
     placement.

6. Use an external authorization or remote-sampler-like service.
   - Promising future direction, especially for centrally managed policy. Not
     needed for the first version because the specification still needs a local
     SDK contract for decision inputs, outputs, ordering, and link behavior.

7. Modify W3C Trace Context semantics or header formats.
   - Rejected for this OTEP scope. This proposal standardizes OpenTelemetry SDK
     behavior while remaining compatible with current propagation formats.

## Open questions

1. What final name fits the component? Options include
   `TraceContinuationDecider` and `TraceContinuationPolicy`.

2. Is `SUPPRESS_TRACE_CONTEXT` the right name for the egress action, or should
   the action be named `DROP_TRACE_CONTEXT`, `DROP_PROPAGATION`, or something
   else?

3. Which link attributes, if any, are standardized for restart-with-link
   relationships?

4. Is baggage filtering a follow-up OTEP, an OPTIONAL result field on this
   component, or a separate propagation feature?

5. Which semantic convention attributes are RECOMMENDED as common decision
   inputs?

6. How does declarative configuration represent allowlist defaults without
   breaking existing continue-by-default behavior?

7. For egress, where is the continuation decision stored so injection can observe
   it across different instrumentation patterns? Outgoing instrumentation often
   creates a client or producer span, makes that span current, and later invokes
   propagation injection. In many languages these steps are not a single SDK
   operation: span creation, scope activation, and injection can be performed by
   different helper APIs or different layers of instrumentation. If the SDK
   stores egress suppression only in one activation path, other valid activation
   paths can miss the decision and accidentally propagate the suppressed trace
   context. Possible designs include an API-level context marker, API-visible
   span state, a propagation-time SDK hook, or a dedicated egress continuation
   API that instrumentation calls before injection.

## Prototypes

- Python prototype at https://github.com/open-telemetry/opentelemetry-python/pull/5394

Prototype scenarios should cover:

- continue vs restart behavior during ingress span creation,
- first-match-wins rule evaluation,
- restart with and without preserved causal links,
- link attributes returned by the decider,
- correct link consumption during root span creation,
- prevention of accidental link inheritance by child spans,
- sampler ordering after continuation decision,
- egress suppression or restart behavior,
- allowlist-style configuration for trusted boundaries.

## Future possibilities

- Integration with OpAMP or telemetry policy for centrally managed boundary
  policy updates.
- A follow-up baggage filtering proposal that reuses the same direction-aware
  rule vocabulary.
- External policy service integration, such as an authorization service or
  remote-sampler-like service returning trace continuation decisions.
