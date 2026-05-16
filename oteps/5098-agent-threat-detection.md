# Agent threat detection semantic conventions

Introduce an `agent.threat.detection.*` attribute namespace for recording the outcome of runtime threat-detection evaluations on AI agent spans, in a ruleset-agnostic and vendor-neutral way.

## Motivation

AI agent runtimes already emit spans for operations such as `invoke_agent`, `execute_tool`, and model calls under the `gen_ai.*` semantic conventions. Around those operations, a growing set of runtime security layers evaluates each step: guardrails, tool-call inspectors, MCP-aware proxies, embedded scanners, and policy engines. When one of those layers fires on a span, there is currently no agreed convention for recording which rule matched, which ruleset issued it, how severe the finding is, or what the enforcing layer did.

Today, vendors write ad-hoc attributes such as `guardrail.rule`, `security.flag`, or proprietary `vendor.x.*` keys. Dashboards, alerting pipelines, and SIEM ingestion break across products. Operators cannot answer basic cross-vendor questions like "how many high-severity blocks fired on `execute_tool` spans this week, across all detection layers?". The gap was raised on [semantic-conventions-genai#132](https://github.com/open-telemetry/semantic-conventions-genai/issues/132), where maintainers and adjacent agentic-observability authors suggested escalating to an OTEP and recommended an `agent.*` rather than `gen_ai.*` namespace because detection layers are agent-aware but not always GenAI-API-aware. Related issues [#94](https://github.com/open-telemetry/semantic-conventions-genai/issues/94) (agent workflow grouping), [#95](https://github.com/open-telemetry/semantic-conventions-genai/issues/95) (MCP tool approval), and [#89](https://github.com/open-telemetry/semantic-conventions-genai/issues/89) (agent failure repair) all touch the same surface area: agent-runtime decisions need a stable schema, and the detection slice of that surface is well-scoped enough to standardize first.

This proposal does not standardize any ruleset. It standardizes how any ruleset, open or proprietary, reports its evaluations on an agent span.

## Explanation

A detection layer that evaluates an agent operation sets a small group of attributes on the span (or on a span event, depending on whether the evaluation is the operation itself or a side observation). The shape is the same in both cases.

```
span.name = execute_tool
gen_ai.operation.name = execute_tool
gen_ai.tool.name = read_url

agent.threat.detection.rule_id = "ATR-2026-00081"
agent.threat.detection.ruleset = "atr@v2.1.3"
agent.threat.detection.severity = "high"
agent.threat.detection.action = "block"
agent.threat.detection.correlation_id = "9c7e0a2f"   # optional, opaque
```

A backend can now answer:

* How many spans with `gen_ai.operation.name = execute_tool` were blocked by any detection layer in the last 24 hours?
* Which `rule_id` values fire most often under which `ruleset`?
* What is the severity distribution of detections, sliced by tenant or by agent framework?

Because the attributes live in the `agent.threat.detection.*` namespace and not under `gen_ai.*`, they are composable with the existing GenAI conventions without overlap, and they can also be applied to non-GenAI agent operations (for example MCP server spans that do not invoke an LLM at all).

## Internal details

### Attributes

| Attribute | Type | Requirement | Description |
| --- | --- | --- | --- |
| `agent.threat.detection.rule_id` | string | Conditionally required when a rule matched | Stable identifier of the matched rule, scoped by `ruleset`. Example: `ATR-2026-00081`, `guardrail-pii-7`. |
| `agent.threat.detection.ruleset` | string | Conditionally required when `rule_id` is set | Namespace plus version of the ruleset. Example: `atr@v2.1.3`, `vendor-x@2026.04`. |
| `agent.threat.detection.severity` | string enum | Conditionally required when `rule_id` is set | One of `low`, `medium`, `high`, `critical`. Aligned with common security severity scales. |
| `agent.threat.detection.action` | string enum | Required when a detection layer evaluated the operation | One of `allow`, `block`, `warn`, `ask`. Records the enforcing decision. `ask` covers human-in-the-loop approval flows (see issue #95). |
| `agent.threat.detection.correlation_id` | string | Optional | Opaque identifier connecting this detection to an upstream evaluation, a related repair span, or a SIEM ticket. Treated as opaque by OpenTelemetry. |

Cardinality is bounded by ruleset size, which is operationally small for production rulesets (today on the order of 10^2 to 10^3). The `correlation_id` is opaque and is not intended for high-cardinality joins inside a tracing backend.

### Where the attributes are set

Two patterns are valid:

1. **On the existing operation span.** A guardrail wrapped around `execute_tool` sets the attributes directly on the `execute_tool` span. This is the common case when the detection layer is in-process and the operation does not duplicate.
2. **On a span event or a dedicated detection span.** When the detection is asynchronous (for example, an out-of-band scanner that re-reads a tool output) or when multiple rules fire on one operation, each detection is a span event under the operation span, or a child span with the same attributes plus `correlation_id` linking to the parent operation.

Both shapes use the same attribute names. Backends do not need separate ingestion paths.

### Interaction with existing conventions

* No overlap with `gen_ai.*`. A `gen_ai.operation.name = execute_tool` span keeps all its existing attributes; the threat detection attributes are additive.
* No overlap with `error.*`. A detection is not an exception. A blocked operation may or may not also set `error.type`, at the discretion of the framework.
* Composes with `gen_ai.group.*` from issue #94 if that proposal is accepted: detections inside a grouped iteration retain their group attributes.
* Composes with the repair conventions sketched in issue #89: `correlation_id` is the natural join key from a detection span to a downstream `gen_ai.repair.*` span.

### Error modes

* A ruleset that mutates rule IDs between versions can confuse aggregation. The `ruleset` attribute carrying an explicit version (`atr@v2.1.3`) is the mitigation.
* A detection layer that reports `action = block` but does not actually block (for example, a shadow-mode evaluator) misleads operators. The recommendation is that `action` reflects the enforcing decision actually applied; shadow-mode evaluations should use `action = allow` and rely on `rule_id` plus `severity` to communicate findings.

## Trade-offs and mitigations

* **Namespace placement.** The original issue proposed `gen_ai.threat.detection.*`. Reviewer feedback on issue #132 pointed out that some detection layers are agent-aware but not strictly GenAI-API-aware (for example, MCP firewalls that intercept tool calls before any LLM is involved). The proposed `agent.*` top-level is a small expansion of the conventional namespace surface but is the more accurate home. Mitigation: scope `agent.*` strictly to attributes that apply to agent operations regardless of GenAI API surface.
* **Action enum granularity.** Four values cover the common cases (allow, block, warn, ask). A finer-grained enum (for example, `redacted`, `rewritten`) would be more expressive but risks fragmentation across vendors. Mitigation: keep the enum minimal and let `rule_id` plus rule documentation carry the finer-grained semantics.
* **Ruleset coupling.** Standardizing the attribute shape does not standardize the rulesets themselves. Different rulesets may produce inconsistent severities or overlapping rule IDs. Mitigation: `ruleset` is required alongside `rule_id`; operators decide how to weigh different sources.

## Prior art and alternatives

* **Ad-hoc vendor attributes.** Today, products emit attributes such as `guardrail.rule`, `security.policy.id`, or `vendor.x.detection.*`. These are not interoperable.
* **`error.*` repurposing.** A detection could be expressed as an error. This loses severity, conflates failures with policy decisions, and breaks dashboards that already treat `error.*` as exceptions.
* **CloudEvents extension.** A separate event schema could carry the same fields. Putting them on the operation span keeps the join with `gen_ai.*` natural and avoids a second pipeline.
* **`gen_ai.threat.*` namespace.** Discussed in issue #132. Rejected by reviewer feedback because it implies a GenAI API boundary that the detection layer does not always sit behind.

## Open questions

* Should `severity` align directly with CVSS qualitative bands, or remain abstract? Aligning would help SIEM integration; staying abstract leaves room for non-CVE-style rulesets.
* Should `action = warn` and `action = ask` be separate, or merged? They model different operator intents (passive warning vs. active human approval) and the working argument is to keep them separate to support issue #95.
* Is `correlation_id` better expressed as a span link rather than a string attribute?

## Prototypes

* Agent Threat Rules (ATR), an MIT-licensed open ruleset at [Agent-Threat-Rule/agent-threat-rules](https://github.com/Agent-Threat-Rule/agent-threat-rules), already issues stable `rule_id` values under the `ATR-YYYY-NNNNN` scheme and ships a CLI scanner. It can populate these attributes today; any other ruleset (proprietary or open) can do the same.
* Production deployments referenced in issue #132 include rule packs shipped into [microsoft/agent-governance-toolkit#908](https://github.com/microsoft/agent-governance-toolkit/pull/908), [cisco-ai-defense/skill-scanner#79](https://github.com/cisco-ai-defense/skill-scanner/pull/79), the [MISP taxonomy #323](https://github.com/MISP/misp-taxonomies/pull/323), and the OWASP regression harness [#74](https://github.com/OWASP/Agent-Security-Regression-Harness/pull/74). These are listed as evidence that detection layers with stable rule IDs are already operating in the field; the OTEP does not depend on any of them and works equally well for a vendor whose rule IDs are entirely internal.

## Future possibilities

* A companion convention for `agent.policy.*` covering policy-engine decisions that are not framed as threat detection (for example, rate limits or quota enforcement).
* Alignment with the `gen_ai.repair.*` direction in issue #89 so that a detection on one span and its remediation on another span are joinable through `correlation_id`.
* A small registry of well-known `ruleset` values, similar to the existing OTel registry of known instrumentation libraries, to help backends render names consistently without requiring those rulesets to be part of the OpenTelemetry project.
