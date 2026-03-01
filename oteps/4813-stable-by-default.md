# Stable by Default: Improving OpenTelemetry's Default User Experience

This OTEP defines goals and acceptance criteria for making OpenTelemetry production-ready by default. It identifies workstreams requiring dedicated effort and coordination across SIGs, each of which may spawn follow-up OTEPs with detailed designs.

## Motivation

OpenTelemetry has grown into a massive ecosystem supporting four telemetry signals across dozen programming languages. This growth has come with complexity that creates real barriers to production adoption.

Community feedback consistently identifies several pain points. Experimental features break production deployments—users report configuration breaking between minor versions, silent failures in telemetry pipelines, and unexpected performance regressions that only appear at scale. As one practitioner noted: "The silent failure policy of OTEL makes flames shoot out of the top of my head."

Semantic convention changes destroy existing dashboards. When conventions change, users must update instrumentation across their entire infrastructure while simultaneously updating dashboards, alerts, and downstream tooling. Organizations report significant resistance from developers asked to coordinate these changes.

Many instrumentation libraries are stuck on pre-release because they depend on experimental semantic conventions, even when the instrumentation API surface itself is mature and battle-tested. The "batteries not included" philosophy means users must assemble many components before achieving basic functionality. Documentation assumes expertise, and newcomers describe the experience as "overwhelming" with "no discoverability." Auto-instrumentation can add significant resource consumption that only becomes apparent at scale, with reports of "four times the CPU usage" compared to simpler alternatives. Users evaluating OpenTelemetry for production deployment need confidence in CVE response timelines, dependency hygiene, and supply chain security—areas where commitments are not well documented.

These all stem from the same problem: OpenTelemetry's default configuration prioritizes feature completeness over production readiness. This OTEP establishes the goals and workstreams needed to address this.

## Goals

This OTEP aims to achieve six outcomes:

- Users should be able to trust default installations. Someone who installs an OpenTelemetry SDK, agent, or Collector distribution without additional configuration should receive production-ready functionality that will not break between minor versions.

- Experimental features should be clearly marked and require explicit opt-in. Users who want cutting-edge functionality can access it, but they must take deliberate action that signals they understand the stability trade-offs.

- Stability information should be visible and consistent. Users should be able to easily determine the stability status of any component before adopting it, and this information should be presented consistently across all OpenTelemetry projects.

- Instrumentation should be able to stabilize based on production readiness. The bar for a stable instrumentation library should be whether the instrumentation code itself is production-ready, not whether the semantic conventions it depends on have been finalized. However, once an instrumentation library stabilizes, any breaking change to its telemetry output must be treated as a breaking change requiring a major version bump.

- Performance characteristics should be known. Users should be able to understand the overhead implications of OpenTelemetry before deploying to production, and maintainers should be able to detect regressions between releases.

- Security commitments should be documented. Users should be able to evaluate OpenTelemetry's security posture, including CVE response timelines and dependency management practices.

## Success Criteria

This initiative succeeds when official OpenTelemetry distributions—Collector distributions, the Java agent, and similar—enable only stable components by default. Users should be able to enable experimental features through a consistent, well-documented mechanism. Each component's stability status should be clearly documented and discoverable. Instrumentation libraries should be able to reach stable status based on the production readiness of their code, even if the semantic conventions they depend on are still evolving. Once stable, any breaking change to telemetry output requires a major version bump. Performance benchmarks should exist for stable components, with published baseline characteristics. Security policies and CVE response commitments should be documented and followed.

## Workstreams

Achieving these goals requires coordinated effort across multiple areas. Each workstream below represents a body of work that may require its own detailed OTEP, tooling, or process changes. The current recommendations are just that -- it's probable that separate projects may need to be created to focus on these specific workstreams.

### Workstream 1: Experimental Feature Opt-In

There is no consistent mechanism across OpenTelemetry for users to opt into experimental features. The Collector uses feature gates, some SDKs use environment variables like `OTEL_SEMCONV_STABILITY_OPT_IN`, and others have ad-hoc approaches. Users have no reliable way to know what they are opting into or what the stability implications are.

This workstream should result in a consistent pattern for experimental feature opt-in that works across SDKs, the Collector, and instrumentation libraries.

The Configuration SIG is the natural owner for this work.

### Workstream 2: Federated Schema and Stability

Instrumentation libraries are blocked from stabilization because they depend on experimental semantic conventions, even when the instrumentation code itself is mature and battle-tested. There is also no consistent mechanism to declare which semantic conventions an instrumentation uses or to report schema URLs consistently.

This workstream should establish a path for instrumentation libraries to stabilize based on the production readiness of their code, rather than requiring all upstream semantic conventions to be stable first. Once stable, instrumentation libraries own the stability of their full output—any breaking change to emitted telemetry must be treated as a breaking change requiring a major version bump, regardless of whether the change originates from updated semantic conventions or from the instrumentation itself. The workstream should also address how instrumentation communicates its semantic convention dependencies to users and downstream tooling, and how migration works when conventions evolve after instrumentation has stabilized.

The Semantic Conventions SIG and Weaver maintainers are the natural owners. Related work includes the [OTEP on federated semantic conventions](https://github.com/open-telemetry/opentelemetry-specification/pull/4815).

### Workstream 3: Distribution and Component Definitions

The term "component" means different things in different contexts—a Collector receiver is quite different from an SDK plugin or an instrumentation library. There is no clear definition of what criteria a component must meet to be included in an official distribution, or what "official distribution" even means.

This workstream needs to define what a component is, what an official distribution is, and what criteria govern inclusion in distributions. The definitions need to work across the Collector, SDKs, and instrumentation.

The GC and Technical Committee should own this work.

### Workstream 4: Production Readiness Criteria

Users cannot easily assess whether a component is ready for production use. Stability status alone does not convey documentation quality, performance characteristics, or operational readiness.

This workstream should define what "production-ready" means for OpenTelemetry components. The goal is visibility, not gatekeeping — helping maintainers understand what production users need without creating barriers to stabilization.

The End User SIG and Communications SIG should own this work.

### Workstream 5: Performance Benchmarking

Users report unexpected performance overhead with OpenTelemetry, sometimes discovering issues only at scale. Maintainers lack consistent tooling to detect performance regressions.

This workstream should address how users understand performance overhead and how maintainers detect regressions. Benchmarks will take different forms depending on the component.

Each implementation SIG should own this work with coordination from the TC.

### Workstream 6: Security Standards

Users evaluating OpenTelemetry for production need confidence in security practices, but commitments around CVE response timelines, dependency updates, and supply chain security are not well documented.

This workstream should result in documented, consistent security commitments across OpenTelemetry projects.

The Security SIG, GC, and TC should own this work.

## Impact

### On Existing Distributions

Distributions that currently enable experimental components by default will need to audit their component list and develop a migration plan. To avoid breaking existing users, implementations may provide a transitional period with deprecation warnings before changing defaults. The specifics of this transition are left to individual distributions and the workstreams above.

### On Instrumentation Libraries

Instrumentation library maintainers will be able to stabilize based on the production readiness of their code, without waiting for all upstream semantic conventions to stabilize. Once stable, they own the stability of their telemetry output—any breaking change to emitted telemetry requires a major version bump. They will need to clearly document which semantic conventions they use and provide migration guidance when conventions evolve.

### On Users

Users will experience a more predictable default installation. Those who depend on experimental features will need to explicitly opt in, which may require configuration changes during the transition period.

## Trade-offs

Disabling experimental features by default means users get less functionality out of the box, which could worsen the "batteries not included" perception. The workstreams above will need to account for this.

Defining workstreams and requiring cross-SIG coordination may slow progress compared to individual SIGs acting independently. However, each workstream can proceed independently once acceptance criteria are agreed. This OTEP provides alignment on goals without requiring lockstep execution.

Allowing instrumentation to stabilize before its upstream semantic conventions may confuse users who see "stable" instrumentation emitting telemetry based on "experimental" semantic conventions. However, this does not mean telemetry output is free to change without consequence—once stable, the instrumentation library commits to the telemetry it emits, and any breaking change requires a major version bump. How to communicate this to users is something the workstreams will need to sort out. The alternative — keeping production-ready instrumentation in pre-release indefinitely — is worse.

Expanding what "production-ready" means could make it harder for components to stabilize, worsening the "stuck on pre-release" problem. The workstreams should avoid creating new barriers to stabilization.

## Prior Art

OTEP 0143 on Versioning and Stability established the foundation for stability guarantees in OpenTelemetry clients. This OTEP extends those concepts to distributions and instrumentation.

OTEP 0232 on Maturity Levels defined maturity levels: Development, Alpha, Beta, RC, Stable, and Deprecated. This OTEP builds on these levels by specifying how they should affect default behavior. Workstreams should use these maturity levels consistently rather than inventing new terminology.

OTEP 0227 on Separate Semantic Conventions moved semantic conventions to a separate repository with independent versioning. This OTEP leverages that separation to enable independent stability assessments.

OTEP 0152 on Telemetry Schemas defined schema URLs and transformation mechanisms for semantic convention evolution. Workstream 2 builds on this foundation.

The OpenTelemetry Collector's `metadata.yaml` and feature gates provide established patterns for component metadata and experimental feature opt-in that workstreams should consider.

Kubernetes uses [feature gates](https://kubernetes.io/docs/reference/command-line-tools-reference/feature-gates/) with alpha/beta/stable progression, where beta features are typically enabled by default. Workstreams should consider whether OpenTelemetry should follow a similar pattern.

## Alternatives Considered

An earlier version of this OTEP attempted to specify detailed requirements for stability criteria, metadata schemas, and opt-in mechanisms. Community feedback indicated this approach was too prescriptive and should be broken into manageable workstreams that can be tackled independently with their own detailed designs.

We also considered keeping current defaults but improving documentation about stability. This does not address the core problem: users hit production issues with experimental features they did not realize they were using. Documentation alone is insufficient.

We considered requiring semantic conventions to be stable before instrumentation can stabilize. This blocks useful, mature instrumentation indefinitely and does not match how users evaluate stability.

## Open Questions

Who will own each workstream? Should ownership be assigned before this OTEP is approved, or can workstreams proceed as volunteers emerge?

Can workstreams proceed in parallel, or do some depend on others? For example, does "Distribution and Component Definitions" need to complete before "Experimental Feature Opt-In" can finalize its design?

Should the default be "stable only" or "beta and above"? The Collector and Kubernetes enable beta features by default. Is that the right model for OpenTelemetry broadly?

Which distributions are considered "official" and subject to these requirements? Just the Collector distributions and Java agent? What about language-specific SDK packages?

How do we ensure workstream outcomes are adopted across the federated OpenTelemetry project? What enforcement mechanisms exist beyond social pressure?

How will we measure whether this initiative is successful? User surveys? Reduced support burden? Faster adoption?

## Future Possibilities

Once the workstreams defined in this OTEP complete, several additional improvements become possible. Users could specify minimum stability thresholds—for example, "only enable beta or above components"—through configuration files or environment variables. Tooling could automatically assess and surface stability information such as documentation completeness, benchmark availability, and test coverage to help users and maintainers. Mechanisms for coordinating stability status across language implementations would ensure users have consistent expectations regardless of language choice. Decoupling instrumentation stability from semantic conventions enables domain experts outside core OpenTelemetry to develop and stabilize conventions for their domains.
