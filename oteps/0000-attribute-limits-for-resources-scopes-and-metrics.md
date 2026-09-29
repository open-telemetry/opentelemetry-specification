# Attribute limits for resources, instrumentation scopes, and metrics

Plan a staged path to configurable attribute limits for resources,
instrumentation scopes, and metric data points, with a separate decision on
whether to change their defaults.

## Motivation

The [common attribute limits](../specification/common/README.md#attribute-limits)
define a default count limit of 128, a default value length limit of infinity,
and a default value depth limit of 64. However, the specification
[exempts resource and metric attributes](../specification/common/README.md#exempt-entities).
It does not clearly say how limits apply to instrumentation scope attributes.
Consequently, the existing general limit configuration cannot reliably bound
these collections. An unexpectedly large collection or value can increase SDK
memory use and the cost of processing telemetry downstream.

The [OTLP message size limits](https://github.com/open-telemetry/opentelemetry-proto/pull/782)
provide a separate transport safeguard. They do not bound the attributes held
by an SDK before export or identify which attributes can be safely removed.

Removing the exemptions without a transition could change resource identity,
instrumentation scope identity, and metric time series identity. The
[discussion in #4911](https://github.com/open-telemetry/opentelemetry-specification/issues/4911#issuecomment-5669985533)
raises this concern, particularly for metrics. We need to establish the
behavior and assess user impact before changing defaults.

## Explanation

SDK users can opt in to limits on resource, instrumentation scope, and metric
attributes. Each collection has independently configurable count, value
length, and value depth limits. When a collection has no explicit limit
configuration, it retains its current behavior during the first rollout
phase. Existing span, span event, span link, and log record limits are
unaffected.

The common limit values are candidate defaults for a later phase, rather than
new defaults established by this OTEP. In particular, the default value
length limit of infinity does not provide a finite bound on value size. The
proposal is about giving users control over these collections and deciding
whether to apply the existing common defaults to them. A guarantee that all
telemetry fields have finite bounds is outside this proposal.

Changing the default can alter exported telemetry. Regardless of whether an
individual exemption is considered a bug, a default change is treated as a
compatibility-impacting behavior change and follows the
[client stability requirements](../specification/versioning-and-stability.md#sdk-stability).
It is not implied by accepting the opt-in phase.

## Internal details

### Configuration and enforcement

The specification will define explicit controls for resource,
instrumentation scope, and metric attribute limits. These controls should be
available programmatically and through the applicable SDK configuration
mechanisms. A domain-specific setting takes precedence over a general setting
when that domain participates in general limits. An unset domain-specific
setting preserves the current behavior in the opt-in phase; a way to
explicitly retain unlimited behavior will be needed before any default
change. Exact option names and the interaction with existing
`OTEL_ATTRIBUTE_*` settings belong in the integration PRs.

Enforcement must happen before the SDK retains or exports the affected
collection. The specification must define how an implementation reports a
limit violation without producing unbounded diagnostics. It must also define
the behavior for a zero limit, repeated attributes, and a collection that is
shared by multiple providers or instruments.

Resource and scope attributes can participate in identity, so silently
discarding an arbitrary attribute is unsafe. The specification work should
evaluate rejecting an oversized resource or scope, preserving identifying
attributes, and other deterministic behaviors. It must address resource
detectors and the case where an entity's identifying attributes would exceed
the limit. No behavior that silently changes identity is approved by this
OTEP.

Metric attributes identify a time series. Applying the ordinary attribute
count rule by dropping an attribute, or truncating a value, can merge distinct
series. The specification work should prototype routing an over-limit
measurement to the existing
[`otel.metric.overflow` series](../specification/metrics/sdk.md#overflow-attribute)
and compare that with rejecting the measurement or an alternative explicit
signal. The chosen behavior must specify interaction with Views, the existing
cardinality limit, synchronous and asynchronous instruments, and exemplars.
It must preserve the rule that a measurement is neither counted twice nor
silently assigned to a different ordinary series.

### Execution plan

1. **Track and measure impact.** Create separate tracking issues for
   resource, scope, and metric attributes under
   [#4911](https://github.com/open-telemetry/opentelemetry-specification/issues/4911).
   Inventory language SDK behavior and configuration support. Collect
   implementation tests, representative workload measurements, and user
   reports for attribute counts and value sizes, especially cases exceeding
   the candidate defaults. Record which attributes affect identity. Do not
   collect application attribute values in project telemetry.
2. **Specify and prototype opt-in limits.** Define configuration, enforcement,
   diagnostics, and identity-safe behavior for each domain in focused spec
   changes. Prototype the difficult paths in more than one language SDK,
   including resource detection, scope creation, metric overflow, and low
   limits. Add implementation tracking issues after the specification is
   integrated. Keep the default behavior unchanged in this phase.
3. **Review default behavior separately.** After opt-in releases have been
   used in practice, present the impact data and proposed behavior to the
   Specification SIG and affected language SIGs. Decide separately for each
   domain and limit dimension whether a default should change. If a default
   change cannot be justified or an identity-safe rule is missing, keep that
   limit opt-in.
4. **Communicate before any default change.** If approved, publish a migration
   guide, release notes, and an OpenTelemetry blog post explaining affected
   telemetry, diagnostics, configuration, and the way to retain the previous
   behavior. Announce the planned change with substantial lead time, targeting
   6–12 months before it takes effect, and solicit feedback. Coordinate
   release timing with language SDK maintainers and follow each language's
   stability policy.
5. **Roll out and monitor.** Land the approved default change through separate
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
specify but risks changing identities without warning. Permanently keeping
all three collections exempt leaves users without a standard way to bound
them. OTLP message size limits and downstream receiver limits protect a
different stage of the pipeline and cannot replace SDK attribute limits.

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

## Prototypes

None yet. Metric overflow and resource or scope identity behavior should be
prototyped before the corresponding specification changes are finalized.

## Future possibilities

The impact study can inform separate proposals for finite default value
lengths, attribute keys, and other unbounded telemetry fields identified in
[#4911](https://github.com/open-telemetry/opentelemetry-specification/issues/4911).
