# Federated Semantic Convention Lifecycle

This OTEP defines the lifecycle, independent versioning, and consolidation path for federated semantic conventions in OpenTelemetry. It expands on the technical foundation provided by OTEP 4815 (Federated SemConv and Schema v2) and the stability goals of OTEP 4813 (Stable by Default).

## Motivation

As OpenTelemetry's semantic conventions expand, a monolithic registry and versioning scheme create friction:
1. **Slow Evolution**: Highly specialized or domain-specific conventions (e.g., JVM metrics, cloud-provider-specific resources) are often gated by the slower stabilization process of the core registry.
2. **Coupled Breaking Changes**: A major version bump in one sub-domain (e.g., a total overhaul of database conventions) should not force the entire OpenTelemetry ecosystem to adopt a major version bump.
3. **Instrumentation Stability**: Instrumentation libraries need a clear way to declare stability for their OTLP output by pinning to specific versions of the conventions they implement, regardless of whether those conventions are "core" or "federated".

We need a federated model where conventions can move at different speeds while still being part of a "cohesive whole" with obvious version conformance for end-users.

## Goals

1. **Independent Lifecycle**: Enable domain-specific semantic convention registries to have their own SemVer lifecycle.
2. **Instrumentation Pinning**: Allow instrumentation libraries to declare stability by pinning to specific federated registry versions.
3. **Platform Releases**: Provide a mechanism (Platform Releases) to bundle specific versions of federated registries into a "tested-together" cohesive set.
4. **Promotion Path**: Define a clear path for federated conventions to be consolidated into the core OpenTelemetry registry.

## Details

### 1. Federated Registry Lifecycle

Each federated registry (as defined in OTEP 4815) manages its own versioning independently.

**The JVM Metrics Example**:
The JVM Metrics registry (e.g., `opentelemetry.io/schemas/jvm`) identifies a need to overhaul its metric names to align with a new runtime standard. 

#### Registry Structure
A federated registry like `jvm-metrics` would contain a manifest, the convention definitions, and a policy enforcment github action.

For example:

**`manifest.yaml`**:
```yaml
schema_url: https://opentelemetry.io/schemas/jvm/2.0.0
description: Semantic Conventions for JVM Metrics
stability: stable

dependencies:
  - schema_url: https://opentelemetry.io/schemas/semconv/1.49.0
```

**`jvm.yaml`**:
```yaml
file_format: definition/2
metrics:
  - name: jvm.memory.used
    ...
```
#### Registry Requirements

- The registry MUST declare a dependency on core semantic conventions.
- The registry MUST use a dependabot or rennovate bot to keep dependencies up-to-date.
- The registry MUST enforce semantic convention policies via github workflow, e.g.

`.github/workflows/semconv-policy.yaml`:
```yaml
name: Semantic Convention Policy Check
...
jobs:
  weaver-check:
    runs-on: ubuntu-latest
    steps:
    - name: check out code
      uses: actions/checkout@... # v...
    - name: set up weaver
      uses: open-telemetry/weaver/.github/actions/setup-weaver@... # v...
    - name: verify template packages
      run: weaver registry check \
           -r {my_registry_dir} \
           -p https://github.com/open-telemetry/opentelemetry-weaver-packages.git[policies/check/naming_conventions] \
           -p https://github.com/open-telemetry/opentelemetry-weaver-packages.git[policies/check/stability] \
           -p https://github.com/open-telemetry/opentelemetry-weaver-packages.git[policies/check/naming]
```

#### Independent Versioning
- It releases `v2.0.0` of the `jvm` federated registry.
- This release is **completely independent** of the core `semconv` registry (which might still be at `v1.45.0`) and other registries like `http` or `messaging`.
- Users who want the new JVM metrics can opt-in by updating their instrumentation to point to the new `schema_url`. 
- Existing users of `v1.x.x` are unaffected and continue to see the old OTLP output.
- **Policy Enforcement**: The federated registry uses a `weaver.yaml` configuration to enforce official OpenTelemetry policies (e.g., naming conventions, stability rules) even while iterating independently.

### 2. Instrumentation Stability and OTLP Output

Instrumentation libraries "own" the stability of the OTLP they produce. To maintain this stability:

- **Pinning**: An instrumentation library MUST specify the `schema_url` of the federated registry version it targets in its `Scope` metadata, via `get {Meter|Tracer|Logger}` operations.
- **Breaking Changes**: If an instrumentation library adopts a new major version of a federated registry that results in breaking changes to its OTLP output, the library ITSELF must perform a major version bump. For example, if `opentelemetry-java-instrumentation` moves from `jvm/v1` to `jvm/v2`, it must release a new major version of its instrumentation package.
- **Stable by Default**: Following OTEP 4813, instrumentation can be marked as stable once its code and OTLP output are production-ready, this means marking any federated registry as stable, in tandem with the library.

### 3. Platform Releases (The Cohesive Whole)

To solve the "cohesive whole" problem and provide obvious version conformance, OpenTelemetry will periodically publish **Platform Releases**. 

A **Platform Release** is a manifest (using the schema format from OTEP 4815) that acts as a "BOM" (Bill of Materials). It does not contain new conventions itself but rather lists specific, tested-together versions of federated registries.

**Example Platform Release Manifest (`OpenTelemetry 2026.1`):**

```yaml
file_format: platform/1.0.0
name: OpenTelemetry Platform Release
version: 2026.1
registries:
  - schema_url: https://opentelemetry.io/schemas/semconv/1.42.0
  - schema_url: https://opentelemetry.io/schemas/jvm/2.1.0
  - schema_url: https://opentelemetry.io/schemas/http/1.15.0
```

- **Version Conformance**: A user can say "My application conforms to OpenTelemetry Platform Release 2026.1". This is a much simpler statement than listing 15 different federated registry versions.
- **Collector Support**: The OpenTelemetry Collector can use a Platform Release manifest to automatically load all necessary schemas and transformations for a specific release.

### 4. Promotion and Consolidation Path

Federated registries follow a standard path toward consolidation to ensure the core specification remains cohesive:

1. **Incubating**: Registry exists outside the core, managed by a specific SIG. It uses a unique namespace, both for schema_url (e.g., `opentelemetry.io/schemas/jvm`) and for signals/attributes (e.g. `jvm`).
2. **Maturity Progression**: The federated registry progresses through `development` -> `beta` -> `stable` according to its own usage and feedback.
3. **Criteria for Promotion**: To be merged into core `semconv`, a federated registry MUST:
    - Reach `stable` status, and remain backwards compatible for a full year.
    - Be available in at least two different stable instrumentation libraries (which may include multiple language implementation).
    - Have a formal review and approval from the Semantic Conventions SIG.
4. **Consolidation**: The promoted conventions are merged into the core `semconv` registry. 
    - A new version of core `semconv` is released (e.g., `v1.50.0`).
    - The old federated `schema_url` manifest is updated to simply re-export the new core `semconv` version. This ensures that existing OTLP data continues to work seamlessly with consumers of
      the previous registry.

## Success Criteria

- An instrumentation library can overhaul its OTLP output (major version bump) by adopting a new version of a federated registry without requiring a global OpenTelemetry semantic convention version bump.
- Users can use components of OpenTelemetry together, without conflicts in signal definitions or unexpected breaking changes (e.g. those not associated with clear version bumps).
- The core `semantic-conventions` registry remains focused and stable while innovation accelerates in federated registries.

## Open Questions

### 1. How do we prevent namespace collisions between federated registries?
The Semantic Conventions SIG maintains the root `opentelemetry.io/schemas/` namespace. Any new "official" federated registry (e.g., `/jvm`, `/http`) must be an approved OpenTelemetry project and will use tooling provided for federated semantic convention SIGs.

For third-party or experimental registries, authors are encouraged to use their own domains (e.g., `acme.com/schemas/`) to avoid collisions. The `weaver` tool will also validate that a registry does not redefine attributes or signals already present in its dependencies, so any opentelemetry registry MUST depend on the core `semantic-conventions` registry.

### 2. What happens if two instrumentation libraries depend on different, incompatible versions of the same federated registry?
This is a classic "diamond dependency" problem. OpenTelemetry's Schema v2 (OTEP 4815) handles this via the "latest version wins" resolution at the collector or consumer level, provided the changes are backward compatible. For breaking changes (major version bumps), the telemetry remains unambiguous because each library pins its specific `schema_url`. A consumer (e.g., the Collector) can process both signals independently using the metadata provided in the OTLP `Resource` or `Scope`. This is no worse than the same issue today, where we rely on storage to figure out these conflicts
and either resolve them or force our queries to be more sophisticated to do so. However, by tagging the data with `schema_url` we could allow storage-time migration and even provide transformation
scripts for major version changes.  See [Future Possibilites](#future-possibilities).

### 3. Does this make the Collector configuration more complex?
No. The Schema Transformation Processor has not stabilized, but even in its current iteration, it was designed to work against many possible URLs and versions.

### 4. Why would a federated registry ever want to "promote" to core?
Promotion to core provides the highest level of visibility, stability guarantees, and long-term maintenance by the Semantic Conventions SIG. It also allows other federated semantic convetion
registries to use/access its conventions in their own. However, registries that require rapid iteration or are highly niche may choose to remain federated indefinitely.

### 5. Is it a burden for instrumentation maintainers to "own" the stability of federated conventions?
This should not be an additional burden. Stability in OpenTelemetry requires the produced telemetry be unchanging. The only change is leveraging the same definition format and enforcement
tooling (`weaver`) to ensure that stability. We believe that once past initial setup, the overall maintainence burden for instrumetnation authors will be less.

### 6. Where is the documentation for all these registries?
The "Platform Release" manifest serves as the primary technical discovery mechanism. We also intend to expand the OpenTelemetry website to include a central "Registry of Registries" where users can browse all approved federated conventions, their stability status, and documentation.

### 7. Does this increase the implementation burden for SDKs and the Collector?
No. Engaging with `schema_url` and federated registries is optional. OpenTelemetry continues to work as-is for users who do not require automated schema transformation or validation. Existing observability ecosystems suffer from these same semantic fragmentation issues today, but they are typically only discovered at the storage or query layer. This proposal provides the metadata necessary to *address* these issues upstream, but it does not mandate that every SDK or Collector component must be schema-aware.

### 8. Won't this lead to "version fatigue" if instrumentation libraries have to major bump frequently to adopt federated registry changes?
No. Instrumentation libraries in OpenTelemetry are subject to the [specification's versioning and stability policies](/specification/versioning-and-stability.md). These policies strongly discourage frequent major version bumps and require minimum support periods (e.g., one year for contrib/instrumentation packages) for older major versions. This inherent bias towards stability ensures that instrumentation libraries do not adopt breaking changes from federated registries at a high cadence. Instead, maintainers will typically batch such changes or only adopt them when the value to users clearly outweighs the significant cost of a major release and the subsequent long-term support requirement.

### 9. Where will federated semantic convention registries reside?
It is not yet decided if federated registries should be:
- Embedded as sub-directories within the main `semantic-conventions` repository (sharing infrastructure but maintaining independent lifecycles).
- Hosted in their own dedicated GitHub repositories.
- Nested within the project that produces the telemetry (e.g., `opentelemetry-collector-contrib` hosting its own conventions, or a language-specific instrumentation repository).
- A combination of the above, depending on whether the registry is maintained by a core OpenTelemetry SIG or an external entity.

### 10. How will consumers handle query fragmentation across different registry versions?
If "Service A" is on `jvm/v1.0.0` and "Service B" is on `jvm/v2.0.0` (which has breaking changes), a consumer's dashboard for "JVM Heap" is effectively broken or requires complex `OR` logic in every query. 

This is a scenario that exists today in open source observability. As
`schema_url` becomes more widely adopted, we expect backends to support
automatic or semi-automatic (e.g agent-aided) transitions and translations to handle this problem.

### 11. How can a consumer discover the "Semantic Contract" of a service?
As a consumer (e.g., an SRE team), I need a way to know what telemetry a service *promises* to send without waiting for a packet to arrive. We
expect insturmentation libraries to publish the schema url they use, and
for documentation to be easily discoverable from this.

### 12. What is the impact on telemetry overhead and storage costs?
We may not be able to re-use `InstrumentationScope` in as many places
as we do today, due to needing finer-grained `schema_url` tracking. To
know if this is true, we need feedback from instrumentation SIGs on how
they are leveraging instrumentation scope today.

We do not expect significant change.

## Alternatives Considered

### Monolithic Registry with Namespaces
We could keep everything in one repo but using namespaces. This does not solve the coupled versioning problem (major bumps).

### Ad-hoc Federation
Allowing federation without a central "Platform Release" mechanism leads to "dependency hell" for users trying to understand if their components work together.

## Future Possibilities

### Automatic Schema Transformation

Tooling (like `weaver`) could automatically generate the necessary OTLP transformations when a user moves from a Platform Release `2026.1` to `2026.2`. We could also
leverage `weaver`'s MCP server to automatically generate OTLP transformation and configuration today as tooling to help with major version bumps needed in OpenTelemetry
instrumentation. This would rely on finer-grained SchemaURLs such that we can tie the transformation to signals generated by a specific library.


### Registry Discovery
A central "Registry of Registries" to discover available conventions, and to advertise conventions from non-opentelemtery sources, similar to the instrumentation registry on opentelemetry.io.
