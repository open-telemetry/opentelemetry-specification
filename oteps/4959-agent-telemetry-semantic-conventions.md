# 0000-agent-telemetry-semantic-conventions.md

# Agent Telemetry Semantic Conventions

**Status:** proposed  
**Author:** Jesse Williams  
**Date:** 2026-03-17  

---

## Motivation

AI agent systems present observability requirements that general-purpose distributed tracing specifications do not address. The OpenTelemetry base specification defines spans, traces, metrics, and logs. The OTel GenAI Semantic Conventions define attributes for LLM calls. Neither covers what happens at the agent level.

Current gaps include:

- No standard representation for agent reasoning cycles, tool invocations, or multi-agent handoffs
- No canonical schema for human-in-the-loop interactions and the audit trail they require
- No standard for capturing retrieval quality signals in RAG pipelines
- No common model for session-scoped memory and its lineage across runs
- No consistent span hierarchy for graph-based agent frameworks such as LangGraph and Microsoft Agent Framework

Without a shared standard, every observability platform (Langfuse, LangSmith, Arize Phoenix) defines its own schema. Every agent framework (LangGraph, Microsoft Agent Framework, AutoGen, Semantic Kernel) emits incompatible telemetry shapes. Enterprises running multiple frameworks and multiple observability backends are forced to maintain bespoke translation layers.

This proposal defines Agent Telemetry Semantic Conventions (ATSC) — a vendor-neutral semantic layer that sits above OTel GenAI Semantic Conventions in the same way that GenAI SemConv sits above the OTel base specification.

Every ATSC span is a valid OTel span. Any OTLP-compatible receiver ingests ATSC telemetry without custom plugins.

---

## Explanation

### Position in the OTel Stack

```
┌─────────────────────────────────────────────────┐
│   Agent Telemetry Semantic Conventions (ATSC)   │
│   Agent span kinds, domain objects, span events  │
├─────────────────────────────────────────────────┤
│      OTel GenAI Semantic Conventions             │
│      gen_ai.* attributes, LLM-call conventions   │
├─────────────────────────────────────────────────┤
│      OTel Base Specification                     │
│      Spans, traces, metrics, logs, OTLP          │
└─────────────────────────────────────────────────┘
```

ATSC does not replace OTel GenAI Semantic Conventions. LLM call attributes (`gen_ai.*`) continue to apply on `llm.*` spans. ATSC adds the agent-specific semantic layer above them.

### Span Kind Taxonomy

ATSC defines 21 span kinds covering the full agent operation surface:

| Span Kind | OTel SpanKind | Description |
|---|---|---|
| `agent.invoke` | INTERNAL | Root span for a complete agent run. |
| `agent.turn` | INTERNAL | One reasoning/response cycle within an agent run. |
| `agent.step` | INTERNAL | A discrete step within a turn, e.g. a graph node execution. |
| `agent.handoff` | CLIENT | Control transferred to another agent. |
| `llm.chat` | CLIENT | A chat completion call to a language model. |
| `llm.completion` | CLIENT | A text completion call to a language model. |
| `llm.embed` | CLIENT | An embedding generation call. |
| `tool.call` | CLIENT | Invocation of a function or API tool. |
| `tool.mcp` | CLIENT | Invocation of a tool via Model Context Protocol. |
| `retrieval.query` | CLIENT | A query against an external knowledge store. |
| `retrieval.fetch` | CLIENT | Direct document fetch from a retrieval store. |
| `memory.read` | INTERNAL | Read from an agent-managed memory store. |
| `memory.write` | INTERNAL | Write to an agent-managed memory store. |
| `human.input` | SERVER | Awaiting input from a human participant. |
| `human.review` | INTERNAL | Agent output submitted for human review. |
| `human.override` | INTERNAL | Human modified or overrode agent output. |
| `guardrail.check` | INTERNAL | A guardrail evaluated as a discrete operation. |
| `evaluation.run` | INTERNAL | An evaluation or scoring operation. |
| `infra.cache` | CLIENT | A cache read or write operation. |
| `infra.queue` | PRODUCER/CONSUMER | A message queue interaction. |
| `error` | INTERNAL | An error span capturing a failure with full context. |

### Domain Objects

ATSC defines 14 domain objects as structured fields on spans. Each object groups related attributes by concern:

| Domain Object | Applicable Span Kinds | Key Fields |
|---|---|---|
| `resource` | All | service.name (MUST), service.version, deployment.environment |
| `run` | All | id (MUST), kind (MUST), name, attempt |
| `session` | All | id, kind, state, participant, context |
| `caller` | agent.*, llm.*, tool.* | type, id, name, framework, version |
| `executor` | tool.*, retrieval.* | type, id, name, framework, version |
| `model` | llm.* | provider, name, input_tokens, output_tokens, total_tokens, cost_usd |
| `tool` | tool.* | name, type, version, target, success |
| `retrieval` | retrieval.* | store, query, results, performance |
| `memory` | memory.* | store, operation, result, content |
| `handoff` | agent.handoff | pattern, reason, target, context_transfer, outcome |
| `human` | human.* | trigger, assignment, context, response, audit |
| `guardrail` | guardrail.check | name, policy, triggered, action, score, categories |
| `evaluation` | evaluation.run | name, score, label, passed, threshold, evaluator |
| `error` | error, any | type, message, stacktrace, code, retryable |

### Conformance Model

ATSC defines three conformance tiers:

**Core Conformant** — 12 MUST fields present and valid on every emitted span:
`spec_version`, `event_id`, `trace_id`, `span_id`, `span_kind`, `timestamp`, `start_time`, `end_time`, `status`, `resource.service.name`, `run.id`, `run.kind`

**Standard Conformant** — Core plus applicable SHOULD fields for the span kind. For example, `model` fields on `llm.*` spans, `tool` fields on `tool.*` spans.

**Full Conformant** — Standard plus MAY fields where technically feasible, with redaction rules documented for all sensitive fields. Suitable for regulated industries and fine-tuning pipelines.

### Span Events

ATSC defines 40+ span events for point-in-time occurrences within spans, organized by namespace:

- Lifecycle events: `agent.started`, `agent.stopped`, `agent.paused`, `agent.resumed`
- Reasoning events: `thought`, `plan.created`, `plan.updated`, `decision`
- Model events: `stream.first_token`, `token.limit.warning`, `content.filtered`, `retry.attempt`
- Tool events: `tool.selected`, `tool.input.validated`, `tool.rate_limited`
- Memory events: `memory.hit`, `memory.miss`, `memory.evicted`
- Retrieval events: `retrieval.reranked`, `retrieval.threshold.miss`
- Guardrail events: `guardrail.triggered`, `guardrail.bypassed`
- Human events: `human.notified`, `human.escalated`
- Graph events: `node.entered`, `node.exited`, `edge.traversed`, `state.updated`
- Evaluation events: `score.recorded`, `threshold.failed`
- Error events: `exception`, `timeout`, `rate_limit`, `context.overflow`

### Privacy and Redaction

ATSC defines a redaction guidance table for sensitive fields. Implementations MUST NOT emit PII in `session.participant.*` or `human.context.*` fields without explicit redaction. Scrubbing is the responsibility of the telemetry generator — ATSC does not define a redaction pipeline.

### Extension Namespaces

ATSC defines a namespace convention for framework-specific and vendor-specific extensions:

| Namespace | Use |
|---|---|
| `agent_framework.*` | Microsoft Agent Framework |
| `semantic_kernel.*` | Semantic Kernel (legacy) |
| `langgraph.*` | LangGraph |
| `aspire.*` | .NET Aspire |
| `x.*` | Custom extensions |

---

## Known Limitations (v0.1.0)

The following are known gaps in the current draft, tracked for v0.2.0:

- **Completed spans only.** ATSC requires complete spans with both `start_time` and `end_time`. There is no buffering model. Assembling start/end events into complete spans is the responsibility of the implementor.
- **No explicit retry span linking.** Retry relationships are currently implicit through `parent_span_id`. An explicit `links[]` convention for retry chains is planned.
- **No agent self-correction span kind.** There is no dedicated span kind or span event for an agent observing and revising its own output.
- **Safety and compliance fields are limited.** Refusal tracking, content policy violation codes, and safety classifier identification are not covered in v0.1.0.

---

## Trade-offs and Mitigations

**Verbosity.** Full conformance produces verbose spans. The three-tier conformance model mitigates this — Core conformance requires only 12 fields, giving implementors a low-friction entry point.

**Overlap with OTel GenAI SemConv.** `gen_ai.*` attributes apply on `llm.*` spans. ATSC does not duplicate these — it adds agent-level context above them. The relationship is additive, not conflicting.

**Framework diversity.** Agent frameworks differ significantly in their execution models. The span kind taxonomy is intentionally abstract enough to accommodate graph-based frameworks (LangGraph), orchestrator-agent patterns (Microsoft Agent Framework), and hand-rolled agents. Framework-specific detail belongs in extension namespaces.

**Completed spans only.** This is a real constraint for streaming and long-running agents. Buffering is an implementation concern and intentionally out of scope for v0.1.0.

---

## Prior Art and Alternatives

**OTel GenAI Semantic Conventions** — covers LLM calls via `gen_ai.*` attributes. Does not address agent-level operations, multi-agent patterns, HITL, or retrieval. ATSC builds on top of this work.

**Langfuse trace schema** — proprietary, platform-specific. Not interoperable across observability backends. ATSC defines the layer that Langfuse and similar platforms could emit to.

**LangSmith trace schema** — proprietary, LangChain-specific. Same interoperability problem.

**OpenTracing baggage** — predecessor to OTel. No agent-specific semantics.

**OpenInference** — Arize's open schema for LLM observability. Focused on LLM and retrieval, does not address multi-agent patterns, HITL, or session-scoped memory lineage.

---

## Open Questions

1. Should `agent.correction` (self-correction loop) be a span kind or a span event? Span kind gives it its own latency and result. Span event is lighter weight.
2. Should the buffering problem be addressed in v0.2.0 via a span streaming convention, or left to implementors indefinitely?
3. Should `run.kind` values be extended to include `pipeline` and `workflow` as distinct from `agent`?
4. Is the three-tier conformance model the right abstraction, or should conformance be binary (valid/invalid against the schema)?
5. How should ATSC interact with the OTel Collector's transform processor for span enrichment and redaction?

---

## References

- ATSC draft specification: https://github.com/agent-telemetry-spec/atsc/blob/main/SPEC.md
- ATSC JSON Schema: https://agent-telemetry-spec.github.io/atsc/schemas/v0.1.0/agent-telemetry-event.json
- OTel GenAI Semantic Conventions: https://opentelemetry.io/docs/specs/semconv/gen-ai/
