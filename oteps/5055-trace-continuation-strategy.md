# Trace Continuation Strategy

Make it possible to configure propagators behavior depending on rules.
Introduce a location in the context for forwarding of restarted traces as links
that is understood by the SDK.

## Motivation

OpenTelemetry currently defaults to continuing remote parent context when
extracting and starting server spans. This behavior works well inside a single
trust domain, but it is insufficient for common boundary scenarios discussed in
issue #1633.

When context is continued unchanged across trust boundaries, users report the
following problems:

- Multiple organizations share a trace ID even though they cannot share full
  trace data.
- Callee services inherit upstream sampling decisions that may be unsafe or
  undesirable for local policies.
- Baggage can be propagated to external systems where it may expose sensitive or
  internal information.
- Automatic instrumentation lacks a standard way to apply boundary behavior
  consistently without manual per-call code.

These scenarios are common in practice, for example:

- third-party API calls,
- webhooks,
- synthetic monitoring and edge traffic,
- mixed internal/external API gateway usage,
- local sidecars/proxies where trace headers can cause functional side effects.

Users need a standard strategy to preserve causal relationships without always
continuing parentage across boundaries. A restart-based approach provides that
strategy by letting implementations either preserve correlation through links or
drop remote trace continuity entirely when policy requires it.

Standardizing this behavior in OpenTelemetry gives:

- safer default building blocks for boundary-aware instrumentation,
- a shared cross-language contract between propagation and tracing components,
- better interoperability for zero-code and library instrumentation.

## Explanation

This proposal defines a policy-driven trace continuation model for trust and
propagation boundaries. Instead of a single hardcoded choice between "continue"
and "restart", extraction evaluates a trace continuation policy and records the
result in context for later span creation.

This proposal introduces two new rule-based propagators: one for W3C Trace
Context and one for W3C Baggage.

The rule-based W3C trace context propagator introduces three policies:

1. **CONTINUE**: extract the remote `SpanContext` and make it the current
   parent.
2. **RESTART_WITH_LINK**: extract the remote `SpanContext`, but do not use it as
   a parent. Instead, store it as a pending link for the next root span.
3. **RESTART_WITHOUT_LINK**: extract for evaluation purposes, but do not use the
   remote context as a parent and do not preserve it as a link.

The trace continuation rules are composed of:
- a predicate taking the `tracestate` header value
- a policy as described before

The rule-based W3C baggage propagator works as a filter for the baggage context.
It introduces two explicit outcomes:

1. **KEEP**: keep the baggage entry in the extracted baggage context.
2. **DROP**: suppress the baggage entry from the extracted baggage context.

The baggage filtering rules are composed of:
- a predicate taking the name and the value of a valid baggage entry
- a baggage outcome as described before

A predicate that drops baggage entries independently of key and value is
equivalent to dropping baggage as a whole.

Each propagator is independent of the other.

### Conceptual request flow for rule based W3C trace context propagator

Normal continuation:

- Extract remote context.
- Evaluate policy and obtain `CONTINUE`.
- Start span as child of remote parent.
- Continue same trace ID and parent chain.

Boundary restart with link:

- Extract remote context.
- Evaluate policy and obtain `RESTART_WITH_LINK`.
- Store the extracted remote context as a pending link.
- Start a new root span.
- Add one link to the stored remote context.

Boundary restart without link:

- Extract remote context.
- Evaluate policy and obtain `RESTART_WITHOUT_LINK`.
- Start a new root span with no parent and no link to the incoming context.

### Policy evaluation for rule based W3C trace context propagator

The `opentelemetry-python` prototype evaluates ordered rules over incoming
`tracestate`. The first matching rule wins, and if no rule matches the default
behavior is `CONTINUE`.

That prototype shape is useful because it:

- avoids wire-format changes,
- allows policy to be decided using metadata already carried with the trace,
- keeps policy enforcement inside propagation and tracing components rather than
  requiring every instrumentation to reimplement the logic.

This OTEP standardizes the behavior that results from policy evaluation. It does
not require every language to expose the exact same rule classes, but it should
be possible to express equivalent behavior.

### Policy evaluation for rule based W3C baggage propagator

The `opentelemetry-python` prototype evaluates ordered rules for each valid
incoming baggage entry. The first matching rule wins, and if no rule matches the
default behavior is `KEEP`.

That prototype shape is useful because it:

- lets baggage filtering be configured using the same ordered-rule mental model
  as trace continuation,
- allows selective suppression instead of requiring all-or-nothing baggage
  handling,
- preserves the existing baggage wire format and parser behavior.

### Configuration model

The canonical configuration schema for these propagators SHOULD be defined in
`opentelemetry-configuration`.

That configuration SHOULD follow the same structural conventions used by
`ExperimentalComposableRuleBasedSampler` and
`ExperimentalComposableRuleBasedSamplerRule`:

- a rule-based propagator configuration object contains a `rules` array,
- rules are matched in order,
- each rule can contain multiple match conditions and all conditions in a rule
  must match,
- if no conditions are specified, the rule matches all inputs that reach it,
- if no rule matches, the propagator falls back to its default behavior.

For these propagators, the default behaviors are:

- trace context: `CONTINUE`,
- baggage: `KEEP`.

For trace context configuration, the standardized schema SHOULD be based on
sampler-style condition objects rather than language-specific helper classes. In
particular, it SHOULD support structures equivalent to:

- `trace_state_values`, analogous to
  `ExperimentalComposableRuleBasedSamplerRuleAttributeValues`,
- `trace_state_patterns`, analogous to
  `ExperimentalComposableRuleBasedSamplerRuleAttributePatterns`.

For baggage configuration, the standardized schema SHOULD likewise support:

- `baggage_values`,
- `baggage_patterns`.

Pattern semantics SHOULD follow the same rules used by
`ExperimentalComposableRuleBasedSamplerRuleAttributePatterns`:

- matching is case-sensitive,
- exact string matches are supported,
- wildcard matching uses `?` for a single character and `*` for any number of
  characters including none,
- `excluded` is evaluated after `included`,
- if `included` is omitted, all values for the named key are considered
  included.

Using those conventions, the prototype's helper predicates map naturally into
the configuration model:

- `OnKeyPresence(key)` maps to a `*_patterns` condition with `key` specified and
  no `included` or `excluded` lists,
- `OnKeyValue(key, value)` maps to a `*_values` condition with a single value,
- `AlwaysPredicate()` maps to a rule with no match conditions.

Each trace-context rule SHOULD require a `policy` field. Each baggage rule
SHOULD require an `action` field. The exact extension names to be added to
`opentelemetry-configuration` remain to be standardized, but their schema shape
should mirror the sampler's rule-based model.

<!-- TODO: The configuration may not match exactly the python prototype regarding values -->

Illustrative configuration shape using placeholder extension names:

```yaml
propagator:
  composite:
    - tracecontext_rule_based/development:
        rules:
          - trace_state_values:
              key: ot.boundary
              values:
                - "public"
            policy: restart_with_link
          - trace_state_patterns:
              key: ot.synthetic
            policy: restart_without_link
    - baggage_rule_based/development:
        rules:
          - baggage_patterns:
              key: tenant.id
            action: drop
          - baggage_values:
              key: debug
              values:
                - "true"
            action: keep
```

## Internal details

### Behavioral contract for rule based W3C trace context propagator

This proposal introduces a cross-component behavioral contract between
propagation and tracing:

- **Pending-link context value**: a standard context semantic meaning "an
  extracted remote parent candidate that is eligible for linking but not for
  parentage."
- Language implementations MAY store either a `Link` or enough information to
  construct one later, but MUST preserve the semantic contract across propagator
  and tracer components.
- The pending-link value is a one-shot hint for the next restarted root span,
  not a new general-purpose parent channel.

### Required behavior for rule based W3C trace context propagator

When trace continuation policy is evaluated for an extracted remote context:

1. Extraction logic MUST parse incoming remote context according to existing
   propagator behavior.
2. Policy evaluation MUST be deterministic.
3. If multiple configured rules match, implementations SHOULD use a first-match
   wins rule order.
4. If no configured rule matches, implementations SHOULD preserve existing
   continuation behavior by defaulting to `CONTINUE`.

When the selected policy is `CONTINUE`:

1. The extracted remote context MUST become the current remote parent according
   to existing continuation behavior.
2. Any pending-link value associated with that extraction outcome MUST NOT be
   left behind.

When the selected policy is `RESTART_WITH_LINK`:

1. Extraction logic MUST NOT make the extracted remote context the active
   parent.
2. Extraction logic MUST store the extracted remote context as a pending-link
   value, or an equivalent link-only representation.

When the selected policy is `RESTART_WITHOUT_LINK`:

1. Extraction logic MUST NOT make the extracted remote context the active
   parent.
2. Extraction logic MUST NOT store a pending-link value for that extraction
   outcome.

When span start logic runs:

1. If a valid parent is available through the normal parentage rules, existing
   parentage behavior remains unchanged.
2. If no valid parent is available, span start logic MUST create a new root
   span.
3. If no valid parent is available and a valid pending-link value is present,
   span start logic SHOULD add exactly one link to the new root span.
4. If user code supplied explicit links at span start, implementations MUST
   preserve those links when adding the pending link.
5. Child spans MUST NOT inherit a pending link that was intended only for the
   restarted root span.

The `opentelemetry-python` prototype achieves the last requirement by clearing
the pending link when a span is installed into context. Other languages may use
different mechanics, but the observable behavior should be the same.

### Parentage precedence

To avoid ambiguous behavior, span start logic MUST use the following parentage
order:

1. Explicit API parent override (if provided by the caller).
2. Active in-process span context.
3. Extracted remote parent context under the `CONTINUE` policy.
4. Root span if none apply.

The pending-link value MUST NOT be used as a parent in this order.

### Rule model informed by the prototype

The `opentelemetry-python` prototype uses simple ordered predicates to make the
behavior concrete:

- `OnKeyPresence(key)`,
- `OnKeyValue(key, value)`,
- `AlwaysPredicate()`.

For trace continuation, those predicates are evaluated against `tracestate` and
yield one of the three policies.

For baggage filtering, those predicates are evaluated per valid baggage entry and
yield one of two baggage outcomes:

- `KEEP`,
- `DROP`.

This OTEP does not require those exact class names or constructor shapes, but it
does intentionally reflect the prototype's design choices:

- ordered evaluation,
- deterministic first-match behavior,
- default continuation when no rule matches,
- separate policy decisions for trace continuation and baggage propagation.

For standardized configuration, the equivalent behavior SHOULD be expressed
using the sampler-inspired schema described above, rather than requiring these
exact helper names to exist in every language API.

### Behavioral contract for rule based W3C baggage propagator

This proposal introduces a standardized baggage rule schema at the behavioral
level:

- baggage rules are evaluated independently for each valid extracted baggage
  entry,
- each baggage rule consists of a predicate and one baggage outcome,
- the standardized baggage outcomes are `KEEP` and `DROP`,
- language implementations MAY represent those outcomes internally using enums,
  booleans, or similar constructs, but their observable behavior MUST be
  equivalent to `KEEP` and `DROP`.

### Required behavior for rule based W3C baggage propagator

When baggage extraction logic is evaluated for an incoming baggage header:

1. Implementations MUST parse and validate baggage entries according to existing
   W3C baggage propagator behavior before applying rule evaluation.
2. Policy evaluation MUST be deterministic for each valid baggage entry.
3. If multiple configured rules match a baggage entry, implementations SHOULD
   use a first-match wins rule order.
4. If no configured rule matches a baggage entry, implementations SHOULD keep
   that entry by default.

When a baggage rule outcome is `KEEP`:

1. The baggage entry MUST be added to the extracted baggage context according to
   existing baggage extraction behavior.

When a baggage rule outcome is `DROP`:

1. The baggage entry MUST NOT be added to the extracted baggage context.

When baggage injection logic runs:

1. Injection behavior MUST remain unchanged by this proposal unless a future
   specification explicitly defines outbound baggage filtering semantics.
2. This proposal standardizes filtering during extraction only.

### Interaction with existing functionality

- Existing propagation formats are unchanged.
- Existing APIs can remain source-compatible if policy evaluation and
  pending-link handling are implemented internally by propagators,
  instrumentation, and SDK components.
- Configuration for these propagators SHOULD be integrated into
  `opentelemetry-configuration` using the same rule-oriented style already used
  by `ExperimentalComposableRuleBasedSampler`.
- Linking is already a supported tracing concept, so correlation across the
  boundary is represented without introducing a new data model primitive.
- Trace restart behavior and baggage filtering are related operationally, but
  they remain distinct controls.

### Baggage interaction

The `opentelemetry-python` prototype also adds a rule-based baggage propagator.
It evaluates ordered rules per baggage entry and can selectively suppress
entries during extraction while leaving injection behavior unchanged.

This is important because many real boundary scenarios want both:

- trace restart policy, and
- baggage filtering policy.

This OTEP standardizes the baggage rule schema at the behavioral level so that:

- implementations share the same ordered rule semantics,
- baggage outcomes are expressed consistently as `KEEP` and `DROP`,
- baggage filtering composes cleanly with trace continuation policy without
  coupling the two behaviors.

### Error modes and handling

- Invalid extracted remote context: ignore it and keep the pre-existing context
  unchanged.
- No matching rule: default to `CONTINUE`.
- Missing or invalid pending-link value at span start: start a new root span
  without an automatically added link.
- Duplicate or conflicting pending-link candidates: implementation SHOULD keep a
  single deterministic candidate and create at most one automatic link by
  default.

### Corner cases

- If both a current in-process span and a pending link exist, current in-process
  span parentage rules win and the pending link MUST NOT be inherited by child
  spans.
- If explicit links are provided at span start, the automatic pending link is
  additive rather than replacing user-supplied links.
- If sampling flags or `tracestate` arrive in the remote context, they MUST NOT
  force parentage continuation under a restart policy.
- If baggage handling is separately restricted at the boundary, this proposal
  remains compatible: trace restart-with-link does not require baggage
  propagation.

## Trade-offs and mitigations

### Trade-off: Trace tree continuity is broken at boundaries

Restarting at a boundary creates a new root span, so parent/child continuity is
no longer represented as a single tree in one trace.

Mitigation:

- Preserve causal relationship using a span link to the extracted remote
  context when policy selects `RESTART_WITH_LINK`.
- Document this as intentional behavior and provide guidance for backend query
  patterns that use links.

### Trade-off: Potential cross-language divergence

Without clear behavioral requirements, language implementations could differ in
how they store pending links, evaluate rules, handle unmatched policy cases, or
expose configuration schemas.

Mitigation:

- Define language-agnostic MUST/SHOULD behavior for extraction, parentage
  precedence, and link creation.
- Keep key material and public helper APIs language-specific, but keep semantic
  meaning standardized.
- Reuse `opentelemetry-configuration` rule-schema conventions instead of
  introducing a completely separate configuration model.
- Add conformance-style test scenarios as follow-up spec work.

### Trade-off: Policy misconfiguration can over-fragment traces

If restart rules are too broad, users may unintentionally restart too many
requests and reduce end-to-end trace readability.

Mitigation:

- Recommend conservative defaults that preserve current continuation unless
  restart is explicitly configured.
- Encourage implementations to expose diagnostics such as counts of `continue`,
  `restart_with_link`, and `restart_without_link` decisions.
- Encourage staged rollout and observation before enforcing broad restart rules.

### Trade-off: Relationship to baggage controls can be confusing

Users often want both trace restart and baggage suppression/filtering. If these
are not clearly separated, implementations may couple them inconsistently.

Mitigation:

- Specify that trace continuation policy and baggage policy are independent.
- Use the prototype as evidence that both can be rule-driven without sharing the
  same internal state.
- Standardize baggage rule behavior in this OTEP while keeping room for later
  work on shared configuration formats.

### Trade-off: Security expectations may be overstated

Restarting trace parentage reduces correlation continuity but does not by itself
eliminate all metadata exposure risks.

Mitigation:

- Explicitly state that this proposal is not a full data-loss-prevention
  mechanism.
- Recommend combining boundary restart policy with network controls and baggage
  governance where required.

## Prior art and alternatives

### Prior art

The closest existing OpenTelemetry prior art is in
`opentelemetry-go-contrib` `otelhttp` via
[`WithPublicEndpointFn`](https://github.com/open-telemetry/opentelemetry-go-contrib/blob/instrumentation/net/http/otelhttp/v0.65.0/instrumentation/net/http/otelhttp/config.go#L99),
as used in
[handler logic](https://github.com/open-telemetry/opentelemetry-go-contrib/blob/dbf7b0a8a37a70ea1848bfdee02ff6c68b0fa9d6/instrumentation/net/http/otelhttp/handler.go#L103).
In that model, user-supplied logic decides when to start a new trace and link
to the extracted remote context.

The `opentelemetry-python` prototype provides more direct prior art for this
OTEP. It implements:

- a `RuleBasedTraceContextTextMapPropagator`,
- three explicit trace policies: `CONTINUE`, `RESTART_WITH_LINK`, and
  `RESTART_WITHOUT_LINK`,
- ordered first-match rule evaluation over `tracestate`,
- context helpers for storing and consuming a pending link,
- SDK logic that appends the pending link to restarted root spans without
  leaking it to child spans,
- a separate `RuleBasedW3CBaggagePropagator` with ordered `KEEP`/`DROP`
  semantics for selective baggage suppression.

The `opentelemetry-configuration` repository provides the configuration prior
art for how rule-driven behavior should be expressed. In particular,
`ExperimentalComposableRuleBasedSampler` demonstrates a schema structure that is
well suited for these propagators:

- a top-level plugin object,
- an ordered `rules` array,
- per-rule match conditions with AND semantics,
- a match-all rule represented by omitting conditions,
- shared helper object shapes for exact-value and pattern-based matching.

### Alternatives considered

1. Keep the status quo (always continue by default everywhere).
   - Rejected as insufficient for security, privacy, and policy-controlled
     boundary scenarios described by users.

2. Implement restart behavior only in individual instrumentations.
   - Rejected as too inconsistent. The prototype shows that the behavior can be
     expressed once in propagation and tracing components instead of being
     reimplemented per framework or protocol.

3. Modify W3C Trace Context semantics or header format in this proposal.
   - Rejected for this OTEP scope. This proposal standardizes OpenTelemetry
     behavior while remaining compatible with current propagation formats.

4. Support only `RESTART_WITH_LINK` and not `RESTART_WITHOUT_LINK`.
   - Rejected because the prototype shows users sometimes want a hard restart
     with no causal link preserved at all.

5. Drop context without preserving causal relation as the only restart option.
   - Rejected as too limiting. `RESTART_WITH_LINK` preserves useful
     troubleshooting correlation while still breaking parentage.

## Open questions

1. Should `tracestate` be the primary standardized policy input, or should the
   model also directly cover route-based, destination-based, or environment-based
   policy inputs?

2. Should trace continuation and baggage filtering share a common standardized
   predicate vocabulary, or should implementations be free to expose equivalent
   language-specific helpers?

3. What exact extension names should be added to
   `opentelemetry-configuration` for the rule-based trace-context and baggage
   propagators?

## Prototypes

This proposal is backed by a prototype in `opentelemetry-python` that
demonstrates the full end-to-end behavior:

- prototype PR: [open-telemetry/opentelemetry-python#5134](https://github.com/open-telemetry/opentelemetry-python/pull/5134),

- extraction uses ordered rules over `tracestate` to select `CONTINUE`,
  `RESTART_WITH_LINK`, or `RESTART_WITHOUT_LINK`,
- `RESTART_WITH_LINK` stores a pending link in context instead of a parent,
- span activation clears the pending link so it is consumed only by the next
  restarted root span,
- root span creation preserves user-supplied links and appends the pending link,
- child spans do not inherit the pending link,
- baggage extraction can separately apply ordered keep/drop rules to baggage
  entries.

The prototype includes tests for:

- continue vs restart behavior during extraction,
- first-match-wins rule evaluation,
- restart with and without preserved causal links,
- correct link consumption during root span creation,
- prevention of accidental link inheritance by child spans,
- rule-based baggage suppression with ordered `KEEP`/`DROP` behavior.

## Future possibilities

- Promotion of the corresponding `opentelemetry-configuration` schema entries
  from experimental to stable once the behavior has interoperable
  implementations.
- Additional sampler-style condition objects for non-header policy inputs such as
  route, destination, or transport metadata.
