# Attribute limits for resources, instrumentation scopes, and metrics

Define the research, design, stability, and rollout gates for considering
attribute limits on resources, instrumentation scopes, and metric data points.
This planning OTEP does not approve SDK limit behavior or a change to defaults.

## Motivation

The [common attribute limits](../specification/common/README.md#attribute-limits)
define a default count limit of 128, a default value length limit of infinity,
and a default value depth limit of 64. The specification says resource
attributes [SHOULD be exempt](../specification/common/README.md#exempt-entities)
and metric attributes are exempt. It does not explicitly exempt
instrumentation scope attributes or clearly define where their limits are
enforced. SDKs may therefore have different behavior for scopes. There is no
uniform way to bound all three collections. An unexpectedly large collection
or value can increase SDK memory use and downstream processing cost.

The [OTLP message size limits](https://github.com/open-telemetry/opentelemetry-proto/pull/782)
provide a separate transport safeguard. They do not bound the attributes held
by an SDK before export or identify which attributes can be safely removed.

Introducing limits for these collections without a transition could change
resource identity, instrumentation scope identity, and metric time series
identity. The
[discussion in #4911](https://github.com/open-telemetry/opentelemetry-specification/issues/4911#issuecomment-5669985533)
raises this concern, particularly for metrics. We need to establish the
behavior and assess user impact before changing defaults.

## Explanation

The intended first phase is to offer explicit, independent opt-in controls
for resource, instrumentation scope, and metric attribute count, value length,
and value depth. No new limits would take effect solely because an SDK is
upgraded. Scope behavior must first be inventoried so the opt-in phase does
not inadvertently remove a limit an SDK already applies. Existing span,
span event, span link, and log record limits are outside this plan.

This OTEP approves a process, not the controls or their semantics. Separate
regular issues under #4911 will track and resolve each domain's enforcement
point, identity handling, and configuration. Their agreed outcomes will be
added to this OTEP for review before normative specification changes are
proposed. This reuses the same OTEP rather than opening another one.

The common limit values are candidate defaults for a later phase, rather than
new defaults established by this OTEP. In particular, the default value
length limit of infinity does not provide a finite bound on value size. The
proposal is about giving users control over these collections and deciding
whether to apply the existing common defaults to them. A guarantee that all
telemetry fields have finite bounds is outside this proposal.

Applying new defaults to conforming implementations changes specified
behavior; it is not a fix for SDK nonconformance. A default change can alter
exported telemetry and must be treated as compatibility-impacting. This OTEP
does not authorize a default change or waive existing stability guarantees.

## Internal details

### Configuration and enforcement

The design issues must define programmatic and applicable SDK configuration
controls, with a corresponding proposal to the
[declarative configuration schema](https://github.com/open-telemetry/opentelemetry-configuration).
They must distinguish an unset limit, zero where permitted, a finite limit,
and an explicit unlimited setting. Opting in to one dimension must not
accidentally activate other limit dimensions. The designs must also settle
precedence between domain-specific controls and existing `OTEL_ATTRIBUTE_*`
settings, including the distinction between an absent setting and a default
value.

The design issues must choose enforcement points and define diagnostics
that cannot grow without bound. They must address repeated attributes and
collections shared by providers or instruments. For resources, they must
reconcile stable `Create` and `Merge` behavior, immutable resources created
before provider configuration, required SDK-provided attributes, detector
merges, and entity identifying attributes. In a resource without Entities,
[all attributes determine identity](../specification/resource/sdk.md#entities);
preserving only a subset cannot satisfy a finite count limit without changing
identity. Rejection or another explicit outcome needs review, including any
new runtime error during initialization.

Scope attributes also participate in scope identity. The scope design issue
must define whether an oversized scope is rejected or handled in
another identity-safe way, and how this affects obtaining tracers, meters,
and loggers. None of these outcomes is approved by this OTEP.

Metric attributes identify a time series. Dropping an attribute or truncating
a value can merge distinct series. The metric design issue must compare
routing an over-limit measurement to
[`otel.metric.overflow`](../specification/metrics/sdk.md#overflow-attribute)
with other explicit outcomes. Reusing that series would conflict with the
current guarantee that cardinality overflow does not occur below the
cardinality limit, so the normative rule would need reconciliation. A count
limit of zero also conflicts with the overflow marker's single attribute.
The design must cover filtering by each View, multiple Views, synchronous and
asynchronous instruments, and exemplar attributes. Prototypes should include
a measurement over the raw limit that falls below it after View filtering.
The outcome must not silently merge distinct ordinary series or count a
measurement twice; any proposed measurement loss needs explicit review.

### Versioning and stability policy

Before deciding on any default change, propose amendments to both the
[client versioning and stability specification](../specification/versioning-and-stability.md)
and the [telemetry stability specification](../specification/telemetry-stability.md),
or conclude that the new limits must remain opt-in.
The current SDK stability section protects public interfaces, constructors,
configuration objects, and environment variables. The telemetry stability
rules prohibit changes to output from stable fixed-schema instrumentations
and, during the schema transformation moratorium, stable schema-file driven
instrumentations. A new SDK default that changes their output would conflict
with those rules. The client versioning policy also needs to classify the
release impact of an SDK default change. The semantic convention stability
section protects resource, scope, and metric attribute keys; some
SDK-provided `service.*` resource attributes must never change. These rules
must be reconciled before limits can remove or alter attributes by default.
Any allowed design must preserve the required resource attributes.

The policy work should explicitly determine:

- whether a default limit that drops, truncates, or reroutes telemetry is a
  breaking change even when the SDK API and ABI remain compatible;
- how changed constructor and configuration behavior, including possible new
  runtime errors, fits the SDK's existing compatibility guarantees;
- which release version, if any, can carry such a change for stable signals,
  and how this interacts with each language's versioning policy;
- whether an exception to the prohibition on changing stable instrumentation
  output can be justified for fixed-schema producers and schema-file driven
  producers, including during the transformation moratorium;
- what compatibility option, notice period, and migration documentation are
  required; and
- whether this class of default change is permitted at all. If the answer is
  no, the new limits remain opt-in.

Long lead time and low measured impact are inputs to that decision. They do
not, on their own, override the stability specification. A separate
specification PR must establish the policy before a PR changing defaults is
considered.

### Execution plan

1. **Track and measure impact.** Create separate tracking issues for
   resource, scope, and metric attributes under
   [#4911](https://github.com/open-telemetry/opentelemetry-specification/issues/4911).
   Use each issue to record alternatives, decisions, prototype links, and
   acceptance criteria as the work progresses.
   Inventory language SDK behavior and configuration support. Collect
   implementation tests, representative workload measurements, and user
   reports for attribute counts and value sizes, especially cases exceeding
   the candidate defaults. Record which attributes affect identity. Do not
   collect application attribute values in project telemetry.
2. **Clarify stability policy.** Open a tracking issue and propose amendments
   to both versioning and telemetry stability for SDK default changes that
   alter exported telemetry. Review them with the Specification SIG, Technical
   Committee, and affected language SIGs. Resolve the release classification,
   stable telemetry, and required resource attribute questions before deciding
   on defaults.
3. **Design and prototype opt-in limits.** Resolve the resource, scope, and
   metric design questions in their linked issues. Prototype difficult paths in
   three language styles: typed object-oriented, dynamically typed, and
   structural. Include resource creation and merging, scope creation, metric
   Views and exemplars, and zero or low limits. Resolve conflicts with stable
   Resource and Metrics SDK requirements before approving behavior.
4. **Approve and specify behavior.** For each domain, once its design issue
   records an agreed resolution and its open questions are settled, update
   this OTEP with that domain's proposed behavior and prototype links for
   review. Issue acceptance alone does not approve a solution. After that
   amendment is approved, make focused specification and companion
   declarative configuration schema PRs that link the issue and prototypes.
   Add implementation tracking issues after the specification changes merge.
   Each domain can proceed independently while preserving existing SDK
   default behavior in this phase.
5. **Review default behavior separately.** After opt-in releases have been
   used in practice, present the impact data and proposed behavior to the
   Specification SIG and affected language SIGs. Apply the approved stability
   policy and decide separately for each domain and limit dimension whether a
   default should change. If the policy does not allow it, the impact cannot
   be justified, or an identity-safe rule is missing, keep that limit opt-in.
6. **Communicate before any default change.** If approved, publish a migration
   guide, release notes, and an OpenTelemetry blog post explaining affected
   telemetry, diagnostics, configuration, and the way to retain the previous
   behavior. Announce the planned change with substantial lead time, targeting
   6–12 months before it takes effect, and solicit feedback. Coordinate
   release timing with language SDK maintainers and follow each language's
   stability policy.
7. **Roll out and monitor.** Land the approved default change through separate
   spec and implementation PRs. Verify conformance and monitor reports of
   missing resource or scope identity and changed metric series. Revisit the
   default if the observed impact differs materially from the assessment.

## Trade-offs and mitigations

- An opt-in period delays protection for users who do not configure limits.
  It gives SDKs and users time to test behavior before defaults change.
- Separate domain controls add configuration surface. They allow identity
  rules and rollout timing to differ where necessary.
- A count limit alone does not bound total payload size; the current default
  value length is infinite. Users who need a finite value size must configure
  a finite length limit. Limits for other fields, such as log record bodies
  and span names, require separate work.
- Any default change can remove or alter telemetry. A measured rollout,
  explicit compatibility option, and advance notice reduce surprises but
  cannot guarantee that no user is affected.

## Prior art and alternatives

The common attribute limits already apply to several record types, and the
Metrics SDK has a [cardinality overflow mechanism](../specification/metrics/sdk.md#cardinality-limits).
Neither directly defines safe behavior for these three collections.

Applying the count limit of 128 immediately everywhere would be simpler to
specify but risks changing identities without warning. Keeping the resource
and metric exemptions while leaving scope behavior unclear prevents a
consistent way to bound them. OTLP message size limits and downstream
receiver limits protect a different stage of the pipeline and cannot replace
SDK attribute limits.

## Open questions

- Which identity-preserving behavior should each domain use when its count,
  length, or depth limit is exceeded? Should resource or scope creation fail?
- Can the existing metric overflow series represent attribute limit violations
  without confusing them with cardinality overflow, and what should happen to
  exemplars?
- How should general limit settings interact with domain-specific opt-in
  settings and a future explicit unlimited setting?
- What evidence would justify changing each default, and should those
  decisions differ across the three domains?
- What versioning and telemetry stability rules should govern SDK defaults
  that change exported telemetry without changing a public interface?

## Prototypes

None yet. This planning OTEP does not approve an SDK feature. The design
issues and the later behavior amendment to this OTEP must link to working
prototypes before the behavior is approved.

## Future possibilities

The impact study can inform separate proposals for finite default value
lengths, attribute keys, and other unbounded telemetry fields identified in
[#4911](https://github.com/open-telemetry/opentelemetry-specification/issues/4911).
