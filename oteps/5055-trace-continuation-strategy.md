# Trace Continuation Strategy

Introduce an SDK component that decides whether an extracted or active trace
context is continued, restarted with a link, or restarted without a link.
The component is similar to the sampler in lifecycle and configurability, but it
answers a different question: which trace context, if any, is used for
continuation across a boundary?

## Motivation

OpenTelemetry currently defaults to continuing remote parent context when
extracting and starting server spans. This behavior works well inside a single
trust domain, but it is insufficient for the trace-continuation subset of common
boundary scenarios discussed in issue #1633.

Issue #1633 also asks for destination-aware baggage and header suppression. This
OTEP does not address that broader propagation-filtering scope. It standardizes
only how trace context is continued, restarted with a link, restarted without a
link, or omitted from trace-context injection.

When context is continued unchanged across trust boundaries, users report the
following problems:

- Multiple organizations share a trace ID even though they cannot share full
  trace data.
- Internal trace context can be propagated to external systems where it exposes
  correlation or sampling information that belongs to a different trust domain.
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

The decider returns a structured result with separate trace-context and baggage
decisions. The trace-context decision includes a continuation strategy and
separate `TraceState` decisions. Initially, only preservation is supported for
the `TraceState` and baggage decisions; their separation allows future controls
without adding combinations to the continuation strategy enum.

The ingress trace-context decision selects one of three continuation strategies:

1. **CONTINUE**: use the candidate `SpanContext` as the parent according to
   existing parentage rules. This applies only when there is exactly one parent
   candidate.
2. **RESTART_WITH_LINKS**: do not use the candidate `SpanContext` as a parent.
   Start a new trace and add a link to that context when creating the
   restarted root span.
3. **RESTART_WITHOUT_LINKS**: do not use the candidate `SpanContext` as a parent
   and do not preserve it as a link.

This proposal evaluates a single candidate from the selected parent `Context`.
The plural strategy names leave room for future support for multiple incoming
contexts, such as a batch of messages. Evaluating those contexts as a group,
including deciding which to preserve as links, is outside the scope of this
proposal. Caller-supplied links remain subject to the existing span creation
behavior and are not candidates for the decider.

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

For ingress, the Trace Continuation Decider runs after the existing span creation
API has selected a parent `Context` and before the SDK finalizes parentage for a
new span. For egress, it runs when instrumentation requests a context for
injection, immediately before propagating across an outgoing boundary.

For ingress, the lifecycle is:

1. Instrumentation receives a request and invokes propagators to extract remote
   context according to existing behavior.
2. Span start logic selects the parent `Context` using the existing span creation
   API.
3. If the selected parent `Context` contains a valid remote span context,
   instrumentation and the SDK assemble a trace continuation input containing
   that candidate and available request metadata.
4. The decider returns an `IngressResult` whose trace strategy is `CONTINUE`,
   `RESTART_WITH_LINKS`, or `RESTART_WITHOUT_LINKS`.
5. Span start logic applies the decision before sampling.
6. The sampler evaluates the span with the final parentage context.

For egress, the lifecycle is:

1. Instrumentation prepares an outgoing request and identifies the current active
   context or other propagation candidate.
2. Instrumentation calls `Tracer.ApplyEgressContinuation` with the propagation
   candidate, span kind, and available destination attributes.
3. The SDK invokes its configured decider and returns a `Context` representing
   the selected egress propagation action.
4. Instrumentation passes that `Context` explicitly to propagation injection.
5. Injection logic observes the action before writing propagation headers.

This proposal intentionally separates propagation parsing from continuation
policy. Language implementations MAY integrate the mechanics differently, but the
observable behavior SHOULD match this lifecycle.

### Interfaces and ownership

The Trace Continuation Decider is an SDK extension point. Applications configure
it on the `TracerProvider`, either programmatically or through declarative
configuration. Each SDK `Tracer` MUST use the decider configured on the provider
that created it, including when instrumentation uses an explicitly supplied
provider rather than the global provider. Instrumentation does not obtain or
invoke the decider directly.

The following language-neutral signatures describe the SDK interface. Names and
parameter grouping are illustrative; language implementations can use idiomatic
equivalents.

```text
TraceContinuationDecider.ShouldContinue(IngressInput) -> IngressResult
TraceContinuationDecider.ShouldInject(EgressInput) -> EgressResult
TraceContinuationDecider.GetDescription() -> String
```

`IngressInput` contains the selected parent `Context`, its valid remote candidate
`SpanContext`, the span kind, the attributes available at span start, and any
caller-supplied links. `IngressResult` contains independent trace-context and
baggage decisions, plus optional diagnostics, as described in
[Decision result](#decision-result).
Caller-supplied links are preserved when the SDK applies the result.

The SDK invokes `ShouldContinue` during `StartSpan`, after parent selection and
before trace ID selection and sampling. It applies the result to parentage and
automatic links before invoking the sampler. The conditions for invoking the
decider are defined in [Parent context selection](#parent-context-selection).
Instrumentation uses the existing span creation API for ingress; no additional
ingress operation is required.

`EgressInput` contains the selected propagation `Context`, the span kind when
known, and available destination attributes. `ShouldInject` returns an
`EgressResult` whose trace-context decision selects `INJECT_TRACE_CONTEXT` or
`SUPPRESS_TRACE_CONTEXT`, independently of its baggage decision. The SDK invokes
it from `Tracer.ApplyEgressContinuation`, independently of span creation or
activation.
The invoked method determines the direction: `ShouldContinue` evaluates ingress
rules and `ShouldInject` evaluates egress rules. `GetDescription` returns a
human-readable description for diagnostics.

Instrumentation accesses egress policy through an operation on the tracing API,
with a signature equivalent to:

```text
Tracer.ApplyEgressContinuation(Context?, SpanKind?, Attributes?) -> Context
```

Instrumentation SHOULD call this operation immediately before injecting context
for each outgoing boundary. If the context argument is omitted, the operation
MUST select the current active `Context`. A supplied `Context`, including an
empty one, MUST be used as supplied. The operation MUST return a context that
injection can use to observe the selected egress action, without changing the
current active context, the input context, or the active span's parentage or
recording state.

For example, instrumentation using an explicitly supplied provider performs the
following operations:

```text
tracer = provider.GetTracer(instrumentationScope)
injectionContext = tracer.ApplyEgressContinuation(context, kind, attributes)
propagator.Inject(carrier, injectionContext)
```

Language implementations MAY expose this operation as a context manager or
another scoped helper, provided instrumentation can pass the returned context
explicitly to injection. When no SDK is installed, the API implementation MUST
return the selected context unchanged. Propagators consume the returned context;
they do not locate the provider or invoke the decider.

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

Both ingress and egress results MUST be structured values with separate
trace-context and baggage decisions. They MUST NOT encode combinations of trace
continuation, `TraceState`, and baggage behavior in a single enum.

The initial result types have fields equivalent to the following. Names and
parameter grouping are illustrative; omitted preservation decisions default to
`PRESERVE`.

```text
IngressResult {
    trace: IngressTraceDecision
    baggage: BaggageDecision = { action: PRESERVE }
    diagnostics: optional implementation-specific diagnostics
}

IngressTraceDecision {
    strategy: CONTINUE | RESTART_WITH_LINKS | RESTART_WITHOUT_LINKS
    parent_tracestate: TraceStateDecision = { action: PRESERVE }
    link_tracestate: TraceStateDecision = { action: PRESERVE }
    link_attributes: optional attributes for the automatic continuation link
}

EgressResult {
    trace: EgressTraceDecision
    baggage: BaggageDecision = { action: PRESERVE }
    diagnostics: optional implementation-specific diagnostics
}

EgressTraceDecision {
    action: INJECT_TRACE_CONTEXT | SUPPRESS_TRACE_CONTEXT
    tracestate: TraceStateDecision = { action: PRESERVE }
}

TraceStateDecision {
    action: PRESERVE
}

BaggageDecision {
    action: PRESERVE
}
```

`TraceStateDecision` and `BaggageDecision` are separate structured decision types.
Their only action in this version is `PRESERVE`. Future actions can carry their
own parameters, such as entry selectors or key-value updates, without changing
the trace relationship strategy. Deciders in this version MUST return
`PRESERVE` for these decisions, either explicitly or through their defaults.

For `TraceStateDecision`, `PRESERVE` means no additional transformation by the
decider. `parent_tracestate` applies when continuing the candidate as parent;
`link_tracestate` applies when creating the automatic continuation link. Neither
decision retains a candidate that the strategy otherwise drops or introduces
parentage under a restart strategy. Egress `tracestate` applies only when trace
context is injected. Existing inheritance, sampling, and propagation behavior
continues to apply, as described in
[Interaction with tracestate](#interaction-with-tracestate).

For `BaggageDecision`, `PRESERVE` means the SDK leaves baggage behavior unchanged,
independently of whether trace context is continued, linked, dropped, or
suppressed for injection. It does not attach a new application context or merge
baggage from other contexts.

The link attributes are useful for recording why a causal relationship was
preserved without parentage. For example, an implementation might record that the
link represents an external audience, public endpoint, partner boundary, or
policy rule. Exact attribute names are left open by this OTEP.

#### Decision space for future extensions

The following inventory identifies the independent controls the result model
needs to accommodate. It distinguishes the initial behavior from future
operations; it does not enable the deferred operations or add configuration for
them.

| Input and decision | Controls | Initial scope |
| --- | --- | --- |
| Single incoming trace context | Continue as parent, restart with a link, or restart without a link | All three strategies |
| Parent or automatic-link `TraceState` | Preserve, clear, or filter/add entries independently of the trace relationship | Preserve only |
| Single incoming baggage | Keep all entries, select entries, or drop all entries independently of trace context | Preserve existing baggage behavior |
| Multiple incoming trace contexts | Retain contexts as links or drop them | Batch evaluation deferred |
| Multiple incoming `TraceState` values | Preserve or transform the state on each retained link; potentially merge state in a later design | Batch evaluation and merging deferred |
| Multiple incoming baggage values | Merge all sources, selected sources or entries, or drop all | Batch evaluation and merging deferred |
| Outgoing trace context | Inject or suppress | Both actions |
| Outgoing `TraceState` | Preserve, clear, or filter/add entries when trace context is injected | Preserve only |
| Outgoing baggage | Keep all entries, select entries, or drop all independently of trace injection | Preserve existing baggage behavior |

For example, a future result could continue parentage while clearing its
`TraceState` and selecting baggage entries, or preserve an incoming context as a
link while dropping baggage. These are independent decisions rather than new
continuation strategies. For multiple candidates, `CONTINUE` is not applicable;
the future result model needs to identify which candidates are retained as links
and associate `TraceState` decisions with those candidates. Caller-supplied links
remain outside the initial policy scope.

The output structure alone does not implement these extensions. Future baggage
filtering needs an ingress operation that evaluates baggage-only input and makes
the resulting context available to application code; changing a context inside
`StartSpan` alone is insufficient. Batch evaluation additionally needs candidate
contexts carrying baggage, distinct from ambient context and explicit links, and
deterministic merge rules for duplicate baggage keys. `TraceState` merging needs
its own semantics and is not implied by baggage merging. These input, lifecycle,
and configuration changes remain future work.

### Conceptual request flows

Normal continuation:

- Extract remote context.
- Select a parent `Context` containing the remote span context.
- Assemble trace continuation input from the selected remote span context and
  request metadata.
- The result's trace strategy is `CONTINUE`.
- Start span as a child of the remote parent.
- Sampler runs with the continued parentage.

Boundary restart with link:

- Extract remote context.
- Select a parent `Context` containing the remote span context.
- Assemble trace continuation input from the selected remote span context and
  trusted boundary metadata.
- The result's trace strategy is `RESTART_WITH_LINKS`.
- Start a new root span.
- Add one link to the selected remote span context, including any link attributes
  returned by the decider.
- Sampler runs for the new root span.

Boundary restart without link:

- Extract remote context.
- Select a parent `Context` containing the remote span context.
- Assemble trace continuation input from the selected remote span context and
  trusted boundary metadata.
- The result's trace strategy is `RESTART_WITHOUT_LINKS`.
- Start a new root span with no parent and no automatic link to the incoming
  remote span context.
- Sampler runs for the new root span.

Egress suppression:

- An outgoing request is prepared with an active in-process context.
- Instrumentation provides the span attributes.
- The result's trace decision selects an egress propagation action such as
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
- rules are matched in order, and evaluation stops at the first applicable
  matching rule,
- each rule can contain multiple match conditions and all conditions in a rule
  MUST match,
- each rule MUST declare a direction,
- a rule is applicable only when its strategy or egress action can be applied to
  the input,
- if no optional conditions are specified, the rule matches all inputs for its
  declared direction for which it is applicable,
- if a rule's conditions do not match, or its strategy or egress action is not
  applicable, evaluation continues with the next rule,
- if no applicable rule matches, the decider falls back to its default behavior.

For example, `CONTINUE` requires exactly one parent candidate. If support for
multiple incoming contexts is added, an ingress rule selecting `CONTINUE` would
be skipped for multiple candidates, even if all its explicit conditions match.
Evaluation would continue with subsequent rules rather than choosing one of the
candidates arbitrarily. Multi-context evaluation itself remains outside the
scope of this proposal.

The default behavior SHOULD preserve existing OpenTelemetry behavior. For
ingress, the default strategy SHOULD be `CONTINUE`. For egress, the default
propagation action SHOULD be `INJECT_TRACE_CONTEXT`. Deployments that enforce
security or tenant boundaries SHOULD be able to configure allowlist-style
policies where continuation is permitted only for known trusted inputs and all
other candidates restart or are dropped.

Rules SHOULD distinguish match inputs from rule outputs:

- `direction` MUST be a first-class rule field with values equivalent to
  `ingress` and `egress`.
- `span_kind` SHOULD be a first-class rule condition when span kind is known.
- `attributes` SHOULD match span, request, route, destination, transport, or
  other trusted metadata provided by instrumentation. Direction SHOULD NOT be
  represented as a synthetic attribute.
- Ingress rules SHOULD produce a trace continuation `strategy`.
- Egress rules SHOULD produce an `egress_action`.
- `link_attributes` SHOULD only apply when the selected ingress strategy is
  `RESTART_WITH_LINKS`.

The configured strategy or egress action populates the trace decision in the
structured result. The `TraceState` and baggage decisions default to `PRESERVE`;
this version introduces no configuration fields for their future actions. One
matching rule produces the whole result; fields are not accumulated from later
rules. The fallback produces the same structured result with the configured
default trace strategy or egress action and preservation for the other decisions.

For operator convenience, implementations MAY accept `strategy` on an egress
rule and map `CONTINUE` to `INJECT_TRACE_CONTEXT` and restart strategies to
`SUPPRESS_TRACE_CONTEXT`, but the canonical configuration model SHOULD expose
egress propagation actions explicitly.

Illustrative configuration shape using placeholder extension names:

```yaml
tracer_provider:
  trace_continuation_decider/development:
    rule_based/development:
      default_ingress_strategy: restart_with_links
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
          strategy: restart_with_links
          link_attributes:
            otel.trace_continuation.reason: external_webhook
        - direction: egress
          span_kind: client
          conditions:
            attributes:
              server.address: api.third-party.example
          egress_action: suppress_trace_context
```

[PR for the configuration](https://github.com/open-telemetry/opentelemetry-configuration/pull/688).

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

When trace continuation is evaluated for a valid remote span context in the
selected parent `Context`:

1. Extraction logic MUST parse incoming remote context according to existing
   propagator behavior.
2. Decider evaluation MUST be deterministic for a given input and configuration.
3. If multiple configured rules match and are applicable to the input,
   implementations SHOULD use first-match wins rule order. A rule whose strategy
   is not applicable MUST be skipped so evaluation can continue with the next
   rule.
4. If no applicable configured rule matches, implementations SHOULD preserve
   existing continuation behavior unless configured otherwise.

When the selected strategy is `CONTINUE`:

1. The candidate remote context MUST be eligible for parentage according to
   existing parentage rules.
2. Any pending-link value associated with that candidate MUST NOT be left behind.

When the selected strategy is `RESTART_WITH_LINKS`:

1. Span start logic MUST NOT use the candidate remote context as the active
   parent.
2. Span start logic SHOULD add exactly one automatic link to the candidate remote
   context.
3. If the decider returns link attributes, implementations SHOULD attach them to
   the automatic link.

When the selected strategy is `RESTART_WITHOUT_LINKS`:

1. Span start logic MUST NOT use the candidate remote context as the active
   parent.
2. Span start logic MUST NOT create an automatic link for that candidate.

### Parent context selection

Trace continuation is evaluated against the parent `Context` selected by the
existing span creation API.
Before invoking the Trace Continuation Decider, span start logic MUST first select
the parent `Context` using existing API behavior: use the caller-provided
`Context` when one is supplied, otherwise use the current active `Context`.
If the selected parent `Context` contains no valid span context, or represents an
explicit root request, the span is started as a root and the decider is not
invoked.
If the selected parent `Context` contains a valid local span context, existing
local parentage behavior is preserved and the decider is not invoked.
If the selected parent `Context` contains a valid remote span context, that remote
span context is the trace continuation candidate. The decider MUST evaluate it:
- `CONTINUE` uses the remote span context as the parent.
- `RESTART_WITH_LINKS` starts a new root span and adds one automatic link to the
    remote span context.
- `RESTART_WITHOUT_LINKS` starts a new root span without an automatic link.
The API does not distinguish an extracted remote context from any other
caller-provided remote parent context. Therefore, a caller-provided remote parent
is subject to the decider unless a language defines an explicit separate API for
forcing remote parentage.

### Link consumption

If the implementation stores a pending link before span start, that value is a
one-shot hint for the restarted root span. Child spans MUST NOT inherit a pending
link that was intended only for the restarted root span.

If user code supplied explicit links at span start, implementations MUST preserve
those links when adding the automatic continuation link.

### Required egress behavior

When trace continuation is evaluated for egress:

1. Injection logic MUST preserve existing propagator behavior when the result's
   trace decision selects `INJECT_TRACE_CONTEXT`.
2. If the selected action is `SUPPRESS_TRACE_CONTEXT`, injection logic MUST NOT
   propagate the suppressed trace context as the active parent context for that
   destination.
3. Egress decisions MUST be direction-aware so an ingress rule does not
   accidentally suppress unrelated outgoing propagation, or vice versa.

Egress is about propagation, not span parentage. The trace decision within the
structured egress result therefore selects an explicit propagation action rather
than a parentage restart strategy. The initial egress trace actions are:

1. `INJECT_TRACE_CONTEXT`: preserve existing trace context injection behavior.
2. `SUPPRESS_TRACE_CONTEXT`: do not inject the selected trace context for this
   outgoing boundary.

`SUPPRESS_TRACE_CONTEXT` intentionally preserves all other configured
propagation behavior. It does not suppress baggage, non-trace propagation
formats, or arbitrary application headers; destination-aware filtering for those
values is future work outside this OTEP.

Rule-based configuration MAY use the same strategy names as ingress for
operator convenience. If so, implementations SHOULD map `CONTINUE` to
`INJECT_TRACE_CONTEXT` and map restart strategies to `SUPPRESS_TRACE_CONTEXT`.
Language implementations MAY represent the selected egress action using context
state or another mechanism associated with the returned injection context, but
injection MUST observe the selected action before writing propagation headers.
The action MUST NOT depend on whether the span was created and activated in one
operation or through separate operations. Each call to
`Tracer.ApplyEgressContinuation` MUST evaluate the selected propagation context
for that boundary. If an inner operation selects `INJECT_TRACE_CONTEXT`, a
suppression hint in its input context MUST NOT override that decision. The input
context and any outer operation's injection context MUST remain unchanged.

### Interaction with samplers

For ingress, the Trace Continuation Decider runs before the sampler observes the
span's final parentage. This ordering is important because parent-based samplers
and attribute-based samplers need to evaluate the span that will actually be
created.

The decider MUST NOT make recording or sampling decisions. A sampler does not
need to understand why parentage was continued or restarted. Implementations
MAY expose decider diagnostics as span attributes or metrics, but those
observability details are not part of the sampling decision.

### Interaction with tracestate

`TraceState` is part of the candidate `SpanContext`. The separate `TraceState`
decisions initially support only `PRESERVE`, so continuation uses the following
behavior:

- `CONTINUE`: the candidate remains the parent, including its `TraceState`.
  The sampler receives that parent context, and existing `TraceState` inheritance
  and sampling behavior applies.
- `RESTART_WITH_LINKS`: the candidate is not the parent. When the automatic link
  is added, its `SpanContext` includes the candidate's `TraceState`. The new root
  does not inherit that `TraceState` as parent state.
- `RESTART_WITHOUT_LINKS`: the candidate's `TraceState` is neither inherited as
  parent state nor preserved through an automatic link. Caller-supplied links,
  including their `TraceState`, remain unchanged.

For either restart strategy, the sampler receives a root parentage context.
Existing root-span sampling behavior determines the new span's `TraceState`,
which is not necessarily empty. A sampler can inspect supplied links according
to the existing sampling API; preserving `TraceState` on a link does not make
that link a parent or cause automatic inheritance.

For W3C Trace Context egress, `INJECT_TRACE_CONTEXT` preserves existing injection
behavior for both `traceparent` and `tracestate`. `SUPPRESS_TRACE_CONTEXT` omits
injection of both headers for the selected context, without modifying the active
span's `TraceState`.

Independent `TraceState` controls, such as continuing parentage while clearing
`TraceState`, filtering or adding individual entries, or removing `TraceState`
from an automatic link, are reserved for future extensions to
`TraceStateDecision`. Their behavior and configuration are outside the initial
scope. This does not change existing sampler, propagator, or exporter
capabilities.

### Interaction with baggage

The result includes a separate `BaggageDecision` with `PRESERVE` as its only
initial action. Baggage filtering and merging remain outside the initial scope.

Baggage filtering is related operationally because the same boundaries often need
both trace restart and baggage suppression. However, combining both in the first
version would make the new SDK component decide parentage, linking, context
injection, and baggage filtering at once. That risks obscuring the core trace
continuation behavior.

The proposed first version standardizes trace continuation decisions and SDK
consumption semantics. Destination-aware baggage suppression, propagation-format
filtering, and arbitrary header filtering are treated as future work, such as:

- a follow-up OTEP using the same decision input and rule vocabulary,
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

- If both a current in-process span and a remote span context exist, existing
  parent `Context` selection rules determine which one is selected. A caller can
  ask to evaluate the remote span context by supplying it as the parent
  `Context`; that caller-provided remote parent is still subject to the decider.
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

For `/webhooks/{partner}` the trace strategy is `RESTART_WITH_LINKS`. The SDK starts
a new internal root span and links to the partner-provided context. Internal child
spans follow the new trace. The partner context is visible as causal information
without becoming the default parent.

For `/internal/*` the trace strategy is `CONTINUE`, so internal service-to-service
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

For internal destinations the trace action is `INJECT_TRACE_CONTEXT`, and
injectors preserve normal trace context propagation. For the external SaaS
destination the trace action is `SUPPRESS_TRACE_CONTEXT`, and injection omits the
internal trace context for that outgoing request. The baggage decision remains
`PRESERVE` for both destinations.

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
  `RESTART_WITH_LINKS`.
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
- Encourage diagnostics such as counts of `continue`, `restart_with_links`, and
  `restart_without_links` decisions.

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

4. How are filtering and merging added to the baggage decision in a follow-up,
   including the ingress context lifecycle and batch conflict resolution?

5. Which semantic convention attributes are RECOMMENDED as common decision
   inputs?

6. How does declarative configuration represent allowlist defaults without
   breaking existing continue-by-default behavior?

## Prototypes

- Python prototype at https://github.com/open-telemetry/opentelemetry-python/pull/5394

Prototype scenarios should cover:

- continue vs restart behavior during ingress span creation,
- first-match-wins rule evaluation,
- structured ingress and egress results with independent trace and baggage fields,
- preservation defaults for parent, link, and egress `TraceState` decisions,
- unchanged baggage for every trace strategy and egress action,
- restart with and without preserved causal links,
- link attributes returned by the decider,
- correct link consumption during root span creation,
- prevention of accidental link inheritance by child spans,
- sampler ordering after continuation decision,
- parent and automatic-link `TraceState` handling for each continuation strategy,
- egress suppression or restart behavior,
- egress policy using an explicitly supplied provider,
- unchanged egress context when no SDK is installed,
- egress injection after separate span creation and activation,
- nested egress operations with independent injection decisions,
- allowlist-style configuration for trusted boundaries.

## Future possibilities

- Integration with OpAMP or telemetry policy for centrally managed boundary
  policy updates.
- A follow-up baggage filtering proposal that reuses the same direction-aware
  rule vocabulary.
- External policy service integration, such as an authorization service or
  remote-sampler-like service returning trace continuation decisions.
