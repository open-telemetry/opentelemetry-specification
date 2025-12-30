# Stable by Default: Improving OpenTelemetry's Default User Experience

This OTEP proposes that OpenTelemetry distributions enable only stable components by default, decouple instrumentation stability from semantic convention stability, and establish expanded stability criteria that include documentation, performance benchmarks, and practical usability.

## Motivation

OpenTelemetry has grown into a massive ecosystem supporting four telemetry signals across more than a dozen programming languages. This growth has come with complexity that creates real barriers to production adoption. Community feedback consistently identifies several pain points:

**Experimental features break production deployments.** Users report configuration breaking between minor versions, silent failures in telemetry pipelines, and unexpected performance regressions that only appear at scale. As one practitioner noted: "The silent failure policy of OTEL makes flames shoot out of the top of my head."

**Semantic convention changes destroy existing dashboards.** When semantic conventions change, users must update instrumentation across their entire infrastructure while simultaneously updating dashboards, alerts, and downstream tooling. Organizations report significant resistance from developers asked to coordinate these changes.

**Instrumentation libraries are stuck on pre-release.** Many instrumentation libraries cannot reach stable status because they depend on experimental semantic conventions, even when the instrumentation API surface itself is mature and battle-tested.

**Defaults are not useful out of the box.** The "batteries not included" philosophy means users must assemble many components before achieving basic functionality. Documentation assumes expertise, and newcomers describe the experience as "overwhelming" with "no discoverability."

**Performance overhead surprises users.** Auto-instrumentation can add significant resource consumption that only becomes apparent at scale, with reports of "four times the CPU usage" compared to simpler alternatives.

These issues share a common root cause: OpenTelemetry's default configuration prioritizes feature completeness over production readiness. This OTEP addresses that by making stability the default.

## Explanation

### Principle: Stable by Default

All OpenTelemetry distributions SHOULD enable only stable components by default. Users who want experimental features MUST explicitly opt in through a consistent, well-documented mechanism.

This means:

1. **Default installations are production-ready.** A user who installs an OpenTelemetry SDK or agent without additional configuration receives only stable, tested functionality.

2. **Experimental features require explicit action.** Enabling experimental components requires configuration that clearly signals the user understands they are opting into potentially unstable behavior.

3. **No silent experimental dependencies.** Stable components MUST NOT silently depend on experimental components in a way that could break user deployments.

### Decoupling Instrumentation Stability from Semantic Convention Stability

An instrumentation library's stability status SHOULD be independent of the stability status of the semantic conventions it emits.

**Rationale:** Instrumentation libraries have two surfaces that can be evaluated independently:

1. **API surface** - The programmatic interface developers use (method signatures, configuration options, lifecycle hooks)
2. **Telemetry output** - The semantic conventions used in emitted spans, metrics, and logs

If an instrumentation library's API surface is stable, mature, and well-tested, blocking its stabilization on experimental semantic conventions harms users by:

- Keeping useful, production-ready code in a "pre-release" state indefinitely
- Preventing distributions from including battle-tested instrumentation by default
- Creating a false signal that the instrumentation is immature when only the conventions are evolving

**Migration pathway requirement:** When instrumentation libraries stabilize before their semantic conventions, they MUST document:

- Which semantic conventions are currently experimental
- How telemetry output may change when conventions stabilize
- Recommended approaches for handling convention migrations (e.g., dual-emission, schema transformations)

### Expanded Stability Criteria

The definition of "stable" SHOULD expand beyond API compatibility to include:

1. **Documentation completeness**
   - Getting started guide with working examples
   - Configuration reference with all options documented
   - Troubleshooting guide for common issues
   - Migration guide from previous versions

2. **Performance benchmarks**
   - A consistent benchmark suite that runs in CI
   - Published baseline overhead characteristics for typical scenarios
   - Historical tracking to detect regressions over time

   Note: The goal of benchmarking is **visibility, not gatekeeping**. We acknowledge that instrumentation adds overhead—we are not promising zero-cost observability. What we need is:
   - **Knowledge**: Users should be able to understand what overhead to expect in typical scenarios before deploying
   - **Tracking**: Maintainers should be able to detect performance regressions between releases
   - **Improvement path**: Contributors who care about performance should have benchmarks they can optimize against

   Benchmarks may take various forms depending on the component: microbenchmarks for hot paths, integration benchmarks for end-to-end scenarios, or memory profiling for allocation-heavy components. The specific approach is left to maintainers, but stable components SHOULD have *some* published benchmark suite that runs consistently.

3. **Tested integration points**
   - Verified compatibility with common frameworks and libraries
   - Example configurations for popular deployment patterns
   - Known limitations clearly documented

4. **Operational readiness**
   - Health check and diagnostic capabilities
   - Graceful degradation under resource pressure
   - Clear feedback mechanisms (no silent failures)

### Promoting Instrumentation to Distributions

Instrumentation libraries that meet stability criteria SHOULD be promoted into official distributions when:

1. The instrumentation API surface is stable
2. The instrumentation covers a widely-used framework or library
3. The instrumentation has demonstrated production usage
4. The semantic conventions used are either:
   - Stable, OR
   - Experimental but with a documented migration pathway

This enables distributions to provide useful functionality by default while maintaining clear communication about what stability guarantees apply to different aspects of the telemetry.

### Consistent Opt-In Mechanism

All OpenTelemetry implementations SHOULD provide a consistent mechanism for opting into experimental features:

1. **Environment variable:** `OTEL_EXPERIMENTAL_FEATURES_ENABLED=feature1,feature2` or `OTEL_EXPERIMENTAL_FEATURES_ENABLED=all`

2. **Programmatic configuration:** A clearly-named API for enabling experimental features at initialization time

3. **Configuration file:** A dedicated section for experimental feature flags

The mechanism SHOULD:
- Be consistent across all language implementations
- Produce clear log messages when experimental features are enabled
- Be discoverable through documentation and error messages

## Internal details

### Impact on Existing Distributions

Distributions that currently enable experimental components by default will need to:

1. Audit which components are experimental vs. stable
2. Move experimental components behind opt-in flags
3. Update documentation to explain how to enable experimental features
4. Communicate changes to users with appropriate migration guidance

**Rollout consideration:** To avoid breaking existing users, implementations MAY provide a transitional period where:
- A deprecation warning is emitted when experimental features are used without explicit opt-in
- The default behavior changes to stable-only in a subsequent release

### Impact on Instrumentation Libraries

Instrumentation library maintainers will need to:

1. Clearly document which semantic conventions they use and their stability status
2. Implement migration pathways for convention changes (e.g., dual-emission periods)
3. Meet expanded stability criteria before being included in default distributions

### Unified Component Metadata

OpenTelemetry currently has fragmented metadata approaches: semantic conventions use Weaver's YAML schema with stability fields, the Collector has `metadata.yaml` for components, and instrumentation libraries have no standardized format. This OTEP proposes a unified component metadata schema that works across all OpenTelemetry components.

Every OpenTelemetry component (instrumentation library, Collector component, SDK plugin) SHOULD include a `metadata.yaml` file with a consistent schema:

```yaml
# metadata.yaml - Unified OpenTelemetry Component Metadata
type: instrumentation  # instrumentation | receiver | processor | exporter | extension

status:
  # API/programmatic interface stability (method signatures, config options)
  api:
    stability: stable  # development | alpha | beta | release_candidate | stable

  # Telemetry output stability, per-signal
  telemetry:
    traces: stable
    metrics: beta
    logs: development

  # Overall component lifecycle
  class: maintained  # maintained | unmaintained | deprecated
  codeowners:
    - "@username"
    - "@org/team"

# Which semantic conventions this component emits
semantic_conventions:
  - http.client
  - http.server
  - url

# Target framework/library information
target:
  name: express
  versions: ">=4.0.0 <6.0.0"

# Where to find more information
documentation: https://opentelemetry.io/docs/instrumentation/js/libraries/express/
```

This unified schema:

1. **Extends the Collector's existing `metadata.yaml` pattern** rather than inventing something new
2. **Separates API stability from telemetry stability** - the core insight of this OTEP
3. **References semantic conventions by ID** - inherits stability from Weaver-managed semconv definitions rather than duplicating
4. **Links to documentation** - single source of truth for details about the component

#### Schema Alignment

The `status.telemetry` stability levels align with the existing semantic conventions schema (development, alpha, beta, release_candidate, stable) as defined in [Weaver](https://github.com/open-telemetry/weaver). The `status.class` field aligns with OTEP 0232's maturity levels.

#### Tooling Integration

This metadata enables:
- **Distribution builders** to automatically include only components meeting stability thresholds
- **Documentation generators** to surface stability information consistently
- **Registry** to display unified component information
- **CI/CD** to enforce stability policies and detect regressions
- **IDEs/editors** to warn when using experimental components without opt-in

### Error Modes

**Experimental feature without opt-in:** When code attempts to use an experimental feature without explicit opt-in, implementations SHOULD:
- Log a warning explaining how to enable the feature
- Either disable the feature or fail fast (language-specific decision)
- NOT silently enable the experimental behavior

**Semantic convention migration:** When semantic conventions change, instrumentation SHOULD:
- Support a dual-emission period where both old and new conventions are emitted
- Provide configuration to control emission behavior during migration
- Log clear messages about the migration status

## Trade-offs and mitigations

### Trade-off: Reduced default functionality

**Concern:** Users may get less functionality out of the box if experimental features are disabled by default.

**Mitigation:**
- Accelerate stabilization of high-value components
- Provide clear, single-command instructions for enabling experimental features
- Ensure the stable subset provides genuine value for common use cases

### Trade-off: Increased maintenance burden

**Concern:** Maintaining stability metadata, dual-emission, and opt-in mechanisms adds work for maintainers.

**Mitigation:**
- Provide shared tooling and libraries for common patterns
- Automate stability checks in CI/CD
- This burden is offset by reduced support load from users hitting stability issues

### Trade-off: Decoupling creates confusion

**Concern:** Users may be confused if instrumentation is "stable" but emits "experimental" semantic conventions.

**Mitigation:**
- Clear documentation explaining the two dimensions of stability
- Tooling that surfaces this information
- Consistent messaging across all OpenTelemetry materials

## Prior art and alternatives

### Prior Art

**OTEP 0143 (Versioning and Stability):** Established the foundation for stability guarantees in OpenTelemetry clients. This OTEP extends those concepts to distributions and instrumentation.

**OTEP 0232 (Maturity Levels):** Defined maturity levels (Development, Alpha, Beta, RC, Stable, Deprecated). This OTEP builds on these levels by specifying how they should affect default behavior.

**OTEP 0227 (Separate Semantic Conventions):** Moved semantic conventions to a separate repository with independent versioning. This OTEP leverages that separation to enable independent stability assessments.

**OTEP 0152 (Telemetry Schemas):** Defined schema URLs and transformation mechanisms for semantic convention evolution. This OTEP references schemas as a migration pathway mechanism.

**OTEP 0155 (External Modules):** Defined the Registry self-assessment form and component quality indicators. The unified metadata schema incorporates these concepts.

**Semantic Conventions YAML Schema (Weaver):** The [Weaver](https://github.com/open-telemetry/weaver) project defines a YAML schema for semantic conventions that includes `stability` (development, alpha, beta, release_candidate, stable), `deprecated`, and `requirement_level` fields. The unified metadata schema aligns with these stability levels.

**OpenTelemetry Collector `metadata.yaml`:** The Collector already requires [`metadata.yaml`](https://github.com/open-telemetry/opentelemetry-collector-contrib/blob/main/processor/resourcedetectionprocessor/internal/system/metadata.yaml) files for components, defining `status.stability` per-signal, `status.codeowners`, and resource attributes. The unified metadata schema extends this pattern to instrumentation libraries.

### Alternatives Considered

**Alternative 1: Status quo with better documentation**

Keep current defaults but improve documentation about stability. Rejected because documentation alone does not prevent users from hitting production issues with experimental features they didn't realize they were using.

**Alternative 2: Strict coupling of instrumentation and semantic convention stability**

Require semantic conventions to be stable before instrumentation can stabilize. Rejected because this blocks useful, mature instrumentation indefinitely and doesn't match how users evaluate stability.

**Alternative 3: Per-feature opt-out instead of opt-in**

Default to enabling everything, with opt-out for experimental features. Rejected because this still causes production issues for users who don't know to opt out, and the current pain points demonstrate this approach doesn't work.

## Open questions

1. **Transition timeline:** How long should the deprecation period be before changing defaults? Should this be coordinated across all language implementations?

2. **Granularity of opt-in:** Should opt-in be at the feature level, component level, or signal level? What's the right balance between simplicity and control?

3. **Semantic convention migration tooling:** What tooling should OpenTelemetry provide to help users migrate when semantic conventions change? Is schema-based transformation sufficient?

4. **Certification or compliance:** Should there be a formal process for certifying that a distribution meets "stable by default" requirements?

5. **Contrib vs. core promotion criteria:** What specific criteria determine when an instrumentation library should be promoted from contrib to core distributions?

6. **Unified metadata schema scope:** Should the unified `metadata.yaml` schema be defined in this OTEP, or should it be a separate OTEP? The Collector SIG and Semantic Conventions SIG already have metadata formats - how do we coordinate convergence?

7. **Metadata schema governance:** Who owns the unified metadata schema? Should it live in the specification repo, a dedicated schema repo, or be managed by Weaver?

8. **Backwards compatibility with existing Collector metadata:** The Collector's existing `metadata.yaml` format has existing tooling (mdatagen). How do we evolve toward a unified schema without breaking existing Collector component builds?

9. **Benchmark guidance:** Should OpenTelemetry provide recommended benchmark scenarios or tooling to help maintainers get started? How do we balance flexibility (let maintainers choose their approach) with comparability (users want to compare overhead across instrumentations)?

## Future possibilities

### Stability Selection in Configuration

Future work could enable users to specify minimum stability thresholds through configuration:

```yaml
# Example: only enable components at beta or higher
otel:
  minimum_stability: beta
```

### Federated Semantic Convention Development

This OTEP supports future work on federating semantic convention development to domain experts outside the core OpenTelemetry organization, as the decoupling reduces the blast radius of convention changes.

### Automated Stability Assessment

Tooling could automatically assess stability criteria (documentation completeness, performance benchmarks, test coverage) and surface this information to users and maintainers.

### Cross-Language Stability Coordination

Future work could establish mechanisms for coordinating stability status across language implementations, ensuring users have consistent expectations regardless of language choice.
