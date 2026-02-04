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

- Instrumentation should be able to stabilize independently of semantic conventions. Battle-tested instrumentation libraries should not be blocked from reaching stable status solely because the semantic conventions they emit are still evolving.

- Performance characteristics should be known. Users should be able to understand the overhead implications of OpenTelemetry before deploying to production, and maintainers should be able to detect regressions between releases.

- Security commitments should be documented. Users should be able to evaluate OpenTelemetry's security posture, including CVE response timelines and dependency management practices.

## Success Criteria

This initiative succeeds when official OpenTelemetry distributions—Collector distributions, the Java agent, and similar—enable only stable components by default. Users should be able to enable experimental features through a consistent, well-documented mechanism. Each component's stability status should be clearly documented and discoverable. Instrumentation libraries should be able to declare API stability independently from telemetry output stability. Performance benchmarks should exist for stable components, with published baseline characteristics. Security policies and CVE response commitments should be documented and followed.

## Workstreams

Achieving these goals requires coordinated effort across multiple areas. Each workstream below represents a body of work that may require its own detailed OTEP, tooling, or process changes. The current recommendations are just that -- it's probable that separate projects may need to be created to focus on these specific workstreams.

### Workstream 1: Experimental Feature Opt-In

There is no consistent mechanism across OpenTelemetry for users to opt into experimental features. The Collector uses feature gates, some SDKs use environment variables like `OTEL_SEMCONV_STABILITY_OPT_IN`, and others have ad-hoc approaches. This workstream should define a consistent pattern for experimental feature opt-in that works across SDKs, the Collector, and instrumentation libraries.

The work is complete when we have a documented mechanism for enabling experimental features—whether through environment variables, configuration, or programmatic API—along with clear guidance on what "experimental" means and what users are opting into. Experimental features should be disabled by default with clear logging when enabled. Where possible, the design should align with existing patterns like Collector feature gates and `OTEL_SEMCONV_STABILITY_OPT_IN`.

The Configuration SIG is the natural owner for this work.

### Workstream 2: Federated Schema and Stability

Instrumentation libraries are blocked from stabilization because they depend on experimental semantic conventions, even when the instrumentation code itself is mature. There is also no standard way to declare which semantic conventions an instrumentation uses or to report schema URLs consistently.

This workstream should enable instrumentation stability to be assessed independently from semantic convention stability, with clear mechanisms for communicating telemetry stability to users. Instrumentation libraries should be able to declare API stability separately from telemetry output stability. Schema URLs should be populated consistently across instrumentations, enabling downstream tooling. Migration pathways should be documented when instrumentation stabilizes before its semantic conventions. Breaking changes to telemetry output should be treated as breaking changes, requiring major version bumps.

The Semantic Conventions SIG and Weaver maintainers are the natural owners. Related work includes the [OTEP on federated semantic conventions](https://github.com/open-telemetry/opentelemetry-specification/pull/4815).

### Workstream 3: Distribution and Component Definitions

The term "component" means different things in different contexts—a Collector receiver is quite different from an SDK plugin or an instrumentation library. There is no clear definition of what criteria a component must meet to be included in an official distribution, or what "official distribution" even means.

This workstream needs to define what a component is, what an official distribution is, and what criteria govern inclusion in distributions. The definitions need to work across the Collector, SDKs, and instrumentation. We need governance around official OpenTelemetry distributions, criteria for including components in those distributions—stability requirements, documentation, testing—and a process for promoting components from contrib/community to official distributions.

The GC and Technical Committee should own this work.

### Workstream 4: Production Readiness Criteria

Users cannot easily assess whether a component is ready for production use. Stability status alone does not convey documentation quality, performance characteristics, or operational readiness.

This workstream should define what "production-ready" means for OpenTelemetry components. The goal is visibility, not gatekeeping. Documented guidance should cover what production-ready components typically include: getting started documentation, configuration reference, troubleshooting guides, migration guides, performance visibility through benchmarks and published overhead characteristics, tested integration points and known limitations, and operational features like health checks, graceful degradation, and clear error messages.

This guidance should be aspirational rather than a set of blocking requirements. Components can be stable without meeting every criterion. Requiring extensive benchmarks and documentation for every component would worsen the "stuck on pre-release" problem, not improve it. The goal is to help maintainers understand what production users need without creating barriers to stabilization.

The End User SIG and Communications SIG should own this work.

### Workstream 5: Performance Benchmarking

Users report unexpected performance overhead with OpenTelemetry, sometimes discovering issues only at scale. Maintainers lack consistent tooling to detect performance regressions.

This workstream should establish patterns and tooling for performance benchmarking that give users visibility into overhead and maintainers ability to detect regressions. We need guidance on benchmark approaches—microbenchmarks, integration benchmarks, memory profiling—along with recommended tooling or frameworks that maintainers can adopt, examples of effective benchmark suites from existing projects, and historical tracking patterns to detect regressions over time.

Benchmarks will take various forms depending on the component, and the specific approach should be left to maintainers. That said, stable components should have some published benchmark suite that runs consistently.

Per-language SIGs should own this work with coordination from the TC.

### Workstream 6: Security Standards

Users evaluating OpenTelemetry for production need confidence in security practices, but commitments around CVE response timelines, dependency updates, and supply chain security are not well documented.

This workstream should document OpenTelemetry's security commitments and establish consistent practices across projects: published CVE response timeline commitments, documented dependency update and hygiene practices, supply chain security practices including signing, provenance, and SBOM, and security policies that are consistent across OpenTelemetry projects.

The Security SIG, GC, and TC should own this work.

## Impact

### On Existing Distributions

Distributions that currently enable experimental components by default will need to audit their component list and develop a migration plan. To avoid breaking existing users, implementations may provide a transitional period with deprecation warnings before changing defaults. The specifics of this transition are left to individual distributions and the workstreams above.

### On Instrumentation Libraries

Instrumentation library maintainers will benefit from the ability to declare API stability independently from telemetry stability. They will need to clearly document which semantic conventions they use and provide migration guidance when conventions change.

### On Users

Users will experience a more predictable default installation. Those who depend on experimental features will need to explicitly opt in, which may require configuration changes during the transition period.

## Trade-offs

Disabling experimental features by default means users may get less functionality out of the box, potentially worsening the "batteries not included" perception. The mitigation is to accelerate stabilization of high-value components, provide clear and discoverable instructions for enabling experimental features, and ensure the stable subset provides genuine value for common use cases.

Defining workstreams and requiring cross-SIG coordination may slow progress compared to individual SIGs acting independently. However, each workstream can proceed independently once acceptance criteria are agreed. This OTEP provides alignment on goals without requiring lockstep execution.

Decoupling instrumentation stability from semantic convention stability may confuse users who see "stable" instrumentation emitting "experimental" semantic conventions. Clear documentation explaining the two dimensions of stability and tooling that surfaces this information consistently should address this. The alternative—keeping useful instrumentation in pre-release indefinitely—causes more confusion.

Expanding what "production-ready" means to include documentation, benchmarks, and security could make it harder for components to stabilize, worsening the "stuck on pre-release" problem. This is why production readiness criteria should be guidance rather than gatekeeping. Components can be stable without meeting every criterion.

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
