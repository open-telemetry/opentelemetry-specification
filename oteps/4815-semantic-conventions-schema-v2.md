# Semantic Convention Schema v2

<!-- START DOCTOC -->

- [Semantic Convention Schema v2](#semantic-convention-schema-v2)
  - [Motivation](#motivation)
  - [Details](#details)
    - [Difference with `file_format: 1.1.0`](#difference-with-file_format-110)
    - [Schema URL structure](#schema-url-structure)
      - [Differentiating between stable and not stable schemas](#differentiating-between-stable-and-not-stable-schemas)
      - [Listing available schema versions](#listing-available-schema-versions)
    - [Definition and resolved schemas](#definition-and-resolved-schemas)
      - [File format and versioning](#file-format-and-versioning)
    - [Building and publishing arbitrary semantic convention registries](#building-and-publishing-arbitrary-semantic-convention-registries)
      - [Creating a registry that depends on OpenTelemetry semantic conventions](#creating-a-registry-that-depends-on-opentelemetry-semantic-conventions)
    - [Dependency resolution mechanism](#dependency-resolution-mechanism)
  - [Trade-offs and mitigations](#trade-offs-and-mitigations)
    - [Schema Transformations](#schema-transformations)
      - [Migration option 1: upgrades based on resolved registry only](#migration-option-1-upgrades-based-on-resolved-registry-only)
      - [Migration option 2: generate diff on demand](#migration-option-2-generate-diff-on-demand)
      - [Migration option 3: publish diff in the future](#migration-option-3-publish-diff-in-the-future)
    - [Documentation and code generation](#documentation-and-code-generation)
  - [Prior art and alternatives](#prior-art-and-alternatives)
  - [Open questions](#open-questions)
    - [Schema transformations evolution](#schema-transformations-evolution)
    - [Where should conventions belong?](#where-should-conventions-belong)
    - [What's the granularity for Collector and instrumentation-specific conventions?](#whats-the-granularity-for-collector-and-instrumentation-specific-conventions)
  - [Prototypes](#prototypes)
  - [Future possibilities](#future-possibilities)

<!-- END DOCTOC -->

In this OTEP, we propose a new telemetry schema format that supports multiple convention registries
and provides full access to metadata.

It builds upon and is aligned with [OTEP 0243 - Introducing Application Telemetry Schema in OpenTelemetry - Vision and Roadmap](/oteps/0243-app-telemetry-schema-vision-roadmap.md).

## Motivation

Semantic Conventions describe the telemetry schema. Conventions hosted by OpenTelemetry describe
common concepts like HTTP, as well as telemetry produced by various OTel instrumentations.

OTel Collector and language-specific instrumentations should be able to publish their
own conventions that are only applicable within their ecosystem. They should
also have a means to communicate the schema they use via [Schema URL](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.54.0/specification/schemas/README.md#schema-url).

Instrumentations that are not hosted by OTel should be able to document and publish
their own conventions that may take a dependency on the OTel ones.

Consumers of telemetry should be able to access the full schema to validate, upgrade,
or sanitize the telemetry. The fully resolved registry, discoverable using
Schema URL, serves as an additional channel for metadata about telemetry. This approach
does not increase telemetry volume and associated costs.

Examples:

- Given a telemetry signal, a consumer should be able to find the full definition
  of the corresponding telemetry item. This enables several use cases:
  - UX hints and AI assistants (explain what this metric measures or what this attribute means)
  - validation (does the telemetry item comply with the schema)
  - cost-saving (drop all non-essential metrics)
  - sanitization (based on annotations in the schema, redact potentially sensitive data)
- Document company/service-specific conventions taking OTel ones as a dependency
  and make their schemas accessible to consumers.
  See [OTEP 0243](/oteps/0243-app-telemetry-schema-vision-roadmap.md) for details.

[Telemetry Schema](/specification/schemas/README.md)
has built the foundation for these scenarios, but does not fully support them.
It's designed around schema transformations and describes the differences between schema
versions, such as attribute or metric renames. While it works under the assumption
of a single registry (OpenTelemetry Semantic Conventions), it needs
an upgrade to support arbitrary convention registries.

## Details

When an HTTP GET is issued against a valid Schema URL, the service hosting that
Schema URL SHOULD return a valid *manifest* in response.

Here's an example of the *manifest*:

```yaml
file_format: manifest/2.0
# schema_url serves as the primary source of schema family and version
# schema family (everything before version) must be unique
schema_url: https://opentelemetry.io/schemas/semconv-dev/1.40.0-dev
# MAY point to a file under schema_url or to an arbitrary location.
resolved_registry_uri: https://opentelemetry.io/schemas/semconv-dev/1.40.0-dev/resolved.yaml

stability: development

# metadata
description: OpenTelemetry Semantic Conventions

# future
# diff_uri: ...
# all_in_one_uri: https://github.com/open-telemetry/semantic-conventions/archive/refs/tags/v1.40.0-dev.tar.gz
```

The manifest contains information about the semantic convention registry including:

- `schema_url` (required) - identifies the registry and its version. MUST follow
  [Schema URL format](/specification/schemas/README.md#schema-url). The part of
  the URL preceding the version is the *Schema Family*, as defined in the
  existing [Schema URL](/specification/schemas/README.md#schema-url) spec.
- `resolved_registry_uri` (required) - Points to a YAML file with the
  [*resolved* registry](#definition-and-resolved-schemas).
  MUST be a valid URL.
- `stability` (required) - Registry stability. MUST be one of the
  [Maturity levels](/specification/document-status.md#maturity-levels).

Other properties may be added in the future.

The service hosting the Schema URL MUST support gzip compression that the caller
MAY control with [`Accept-Encoding`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Accept-Encoding)
header (this is already supported by `opentelemetry.io`).

New properties MAY be added to the manifest with a minor `file_format` version
bump - for example, a URL pointing to diffs against previous versions, so
consumers can download only the parts they need. A future major version bump
follows [versioning and stability policies](/specification/versioning-and-stability.md).

See [File format and versioning](#file-format-and-versioning) for the rules that apply
to `manifest`, `resolved`, and `definition` format identifiers.

All artifacts for a given release MUST be immutable. Consumers SHOULD cache manifests
and resolved registries, or any parts of them, when used on the hot path.

The manifest schema and REST API to obtain it using Schema URL will be formally
documented for public, unauthenticated access.

See [Schema URL structure](#schema-url-structure) and
[Differentiating between stable and not stable schemas](#differentiating-between-stable-and-not-stable-schemas)
for details on the `schema_url` format and how the schema family encodes
maturity (e.g. `semconv-dev`).

### Difference with `file_format: 1.1.0`

Schema [file format 1.1.0](/specification/schemas/file_format_v1.1.0.md) included
`schema_url` and a `versions` section.

The `versions` section listed all previous versions and for each of them included
a list of transformations to be applied to upgrade `vX` to `vX + 1`.

This functionality is now covered by other means. See [Listing available schema versions](#listing-available-schema-versions)
and [Schema Transformations](#schema-transformations) for the details.

### Schema URL structure

The Schema URL pattern today does not provide per-registry or per-stability
differentiation - `opentelemetry.io/schemas/{version}`.

OTel components that want to publish their conventions SHOULD follow a new
pattern:

```text
opentelemetry.io/schemas/{component}[-{maturity}]/{version}[-{maturity}]
```

- `{component}` identifies the registry - for example, `semconv` for the
  central `semantic-conventions` repo, or `collector` for OTel Collector
  conventions.
- `{maturity}` (optional) selects a view of the registry at a given
  stability level. When omitted, the URL points to the stable view. Allowed
  suffixes correspond to the [maturity levels](/specification/document-status.md#maturity-levels)
  defined in this repository:

  | Maturity level    | Suffix    |
  | ----------------- | --------- |
  | Stable            | *(none)*  |
  | Release Candidate | `-rc`     |
  | Beta              | `-beta`   |
  | Alpha             | `-alpha`  |
  | Development       | `-dev`    |

  The suffix is part of the schema family. Mixing maturity-suffixed and
  unsuffixed versions under one schema family would break version ordering,
  which [dependency conflict resolution](#dependency-resolution-mechanism)
  relies on.

- `{version}` is the [Schema Version Number](/specification/schemas/README.md#schema-version-number)
  and follows SemVer 2.0, with a prerelease component when applicable.

A registry MAY publish multiple maturity-suffixed views of the same release.
Each view has a distinct schema family with its own listing SchemaURL and its
own manifest.

Examples:

- `opentelemetry.io/schemas/semconv/{version}` - stable conventions from the
  semantic-conventions repo
- `opentelemetry.io/schemas/semconv-dev/{version}-dev` - development conventions
  from the semantic-conventions repo
- `opentelemetry.io/schemas/collector/{version}` - stable conventions for the
  Collector and Collector Contrib
- `opentelemetry.io/schemas/java-instrumentation/{version}` - stable conventions for
  Java instrumentation

#### Differentiating between stable and not stable schemas

Currently, Schema URL includes the semantic convention version but does not include any
indication of stability.

OpenTelemetry Semantic Conventions will publish two schemas with each release:

- stable (e.g. `https://opentelemetry.io/schemas/semconv/1.40.0`) which includes
  only the stable subset of semantic conventions registry.
- development (e.g. `https://opentelemetry.io/schemas/semconv-dev/1.40.0-dev`) which
  includes all semantic conventions defined in the registry regardless of their
  stability.

Both registries are produced from the same release and share the same version
number. They have distinct schema families, each with its own listing endpoint
and its own manifest.

Additional intermediate maturity levels (`-rc`, `-beta`, `-alpha`) MAY be
published. A registry published at a given maturity SHOULD include all
conventions at that maturity or higher (e.g. an `-alpha` registry includes
alpha, beta, RC, and stable conventions). In practice, publishing intermediate
levels is impractical and usually unnecessary - the stable and
development pair is expected to cover most if not all use cases.

The manifest file MUST include the actual stability level.

OpenTelemetry instrumentation SHOULD provide a Schema URL that reflects the version
of conventions it follows.

For example, when HTTP instrumentation supports experimental features on top of
HTTP conventions and the user has enabled these experimental features, the
instrumentation SHOULD use a development Schema URL
(e.g. `https://opentelemetry.io/schemas/semconv-dev/1.40.0-dev`).

#### Listing available schema versions

The service hosting the Schema URL SHOULD also support listing available versions.

[Schema URL format](/specification/schemas/README.md#schema-url) is defined as `http[s]://server[:port]/path/<version>`,
so the service SHOULD return a list of available Schema URLs on `http[s]://server[:port]/path/`.

For example, `https://opentelemetry.io/schemas/semconv` would return

```yaml
- "https://opentelemetry.io/schemas/semconv/1.{N}.0",
- "https://opentelemetry.io/schemas/semconv/1.{N-1}.0",
- ...
```

The format and content type will be formally documented in a way that could support
paging in a non-breaking manner.

This requirement applies only to the full path above the version segment -
`https://opentelemetry.io/schemas/semconv` in this example. Listing at ancestor
path segments (e.g. `https://opentelemetry.io/schemas`) is out of scope of this
OTEP.

### Definition and resolved schemas

The [*definition* schema](https://github.com/open-telemetry/weaver/blob/main/schemas/semconv-syntax.v2.md)
used to write semantic conventions is not the same as the *resolved* registry.

For example, a metric could be defined in the following way in the *definition* schema:

```yaml
# definition schema
file_format: definition/2
attributes:
- key: my.operation.name
  type: string
  stability: development
  brief: My service operation name as defined in this Open API spec
  examples: ["get_object", "create_collection"]
...
metrics:
- name: my.client.operation.duration
  stability: stable
  instrument: histogram
  unit: s
  attributes:
    - ref: my.operation.name
    - ref_group: my.operation.server.attributes
    - ref: error.type
```

Attributes are defined separately from metrics and referenced by them.
This approach optimizes for reusability and consistency. Defaults and inherited properties are
omitted. Definitions can be spread across an arbitrary set of files.

The *resolved* registry is a single file produced from a set of definitions. It contains
all attributes along with signal definitions and refinements. It is optimized for
distribution and in-memory representation.

The *resolved* registry for this metric looks like:

```yaml
# resolved registry
file_format: resolved/2.0  # versioned independently of manifest format
schema_url: https://acme.com/schemas/1.0.0  # URL where the owning manifest is (or will be) published
attribute_catalog:
...
- key: my.operation.name
  type: string
  stability: development
  brief: My service operation name as defined in this Open API spec
  examples: ["get_object", "create_collection"]
...
registry:
  attributes:
  ...
  - 888   # this is the index of `server.address` in the attribute_catalog
  - 1042  # this is the index of `my.operation.name` in attribute_catalog
  ...
  metrics:
  - name: my.client.operation.duration
    instrument: histogram
    unit: s
    attributes:
      - base: 1042  # this is the index of `my.operation.name` in attributes list
        requirement_level: required
      - base: 888  # this is the index of `server.address` in the attributes list
        requirement_level: recommended
      ...
```

These examples are for illustration only - see the [JSON schema](https://github.com/open-telemetry/weaver/blob/main/schemas/semconv.resolved.v2.json)
for the full structure.

The resolved registry file is immutable once published for a given version.
The manifest and resolved registry are versioned together, and each release MUST use a unique `schema_url`.

If the resolved registry needs to change, a new version of both the manifest and the resolved registry MUST be released.

The resolved registry is formally documented as a [JSON schema](https://github.com/open-telemetry/weaver/blob/main/schemas/semconv.resolved.v2.json),
see [overview](https://github.com/open-telemetry/weaver/blob/main/schemas/semconv-schemas.md#resolved-schema).

As a data point on volume: the resolved registry for [OTel Semantic Conventions v1.38.0](https://github.com/open-telemetry/semantic-conventions/releases/tag/v1.38.0)
is approximately 1.2MB uncompressed and 200KB compressed.

#### File format and versioning

The file format follows the `{prefix}/<major>[.<minor>]` pattern.
The supported formats are:

- `definition/2`
- `definition/2.{minor}`
- `manifest/2.{minor}`
- `resolved/2.{minor}`

Patch versions are not part of the format identifier.

The same compatibility rules apply to all formats that include a minor version:

- **Newer minor version, same major**: backward compatible. New optional fields
  may be added within a major version. Consumers SHOULD continue to parse the
  file, ignore unknown fields, and SHOULD log a warning indicating that the
  file uses a newer minor version than the consumer supports.
- **Major version mismatch**: breaking change. Consumers MUST check the major
  version before parsing and MUST refuse to process files with an unsupported
  major version. Migration tooling and documentation will be provided for major
  version transitions.

The definition schema also accepts the major-only form `definition/2`, which
omits the minor version. This lets authors avoid bumping every definition file
each time weaver releases a new minor version. When parsing such files,
consumers (weaver) SHOULD ignore unknown fields and SHOULD log a warning if any
are encountered, since the file may use a newer minor version than the consumer
supports.

### Building and publishing arbitrary semantic convention registries

Any organization, project, or application MAY define its own semantic conventions, publish them as a
versioned registry, and expose them via Schema URL using the same manifest and resolved registry formats
described above.

Weaver will provide `weaver registry package --resolved-registry-uri <url>` to read, resolve, and produce publication
artifacts (manifest, resolved registry, and any future additions). The command consumes
a *definition* manifest and local semconv definitions, then outputs the resolved registry
and the publication manifest.

**Definitions:**

- semconv registry definition files (attributes, entities, signals)
- `manifest.yaml` (definition manifest, includes information about dependencies)

The *definition manifest* contains information about the registry that's available
at development time and is used to create the publication manifest.

Here's an example of a definition manifest:

```yaml
schema_url: https://acme.com/schemas/1.0.0
description: This registry contains semantic conventions for Acme Corp.
stability: stable
```

**Publication artifacts:**

- `manifest.yaml` (publication manifest, `file_format: manifest/2.0`). To be published at the Schema URL.
- `resolved-registry.yaml`. To be published at the URL specified in the manifest.

Here's an example of a publication manifest produced from the definition above:

```yaml
file_format: manifest/2.0
schema_url: https://acme.com/schemas/1.0.0
resolved_registry_uri: https://acme.com/schemas/1.0.0/resolved.yaml
stability: stable
description: This registry contains semantic conventions for Acme Corp.
```

`resolved_registry_uri` is set by `weaver registry package` based on a publication
location passed to it. It points to an arbitrary
location.

#### Creating a registry that depends on OpenTelemetry semantic conventions

OpenTelemetry Collector components, instrumentation libraries, and any other components
can define their own conventions and may take a dependency on OTel semantic conventions
and/or any other registry.

Here's an example of a definition manifest that includes a dependency on OTel conventions:

```yaml
name: activemq-jmx-instrumentation
description: This registry contains semantic conventions for ActiveMQ JMX instrumentation.
version: 1.0.0
repository_url: https://github.com/open-telemetry/opentelemetry-java-instrumentation/blob/main/instrumentation/jmx-metrics/library/activemq.md
stability: development
dependencies:
  # schema_url is expected to point to the publication manifest of the dependency.
  # It's a unique identifier containing schema family and version.
  - schema_url: https://opentelemetry.io/schemas/semconv-dev/1.39.0-dev
    # in some cases (when registry_path is provided) schema_url is ONLY used as
    # a unique identifier containing schema family and version.
    # The actual registry artifacts come from `registry_path` property.
    # This allows supporting v1 registries and simplifying local development.
    # `registry_path` may be a local folder or a link to the registry on GitHub
    registry_path: https://github.com/open-telemetry/semantic-conventions/archive/refs/tags/v1.39.0.zip[model]
```

This example is simplified - in practice, we would likely include all Java-instrumentation-
specific conventions in this registry and publish one Schema URL for all of them.

Here's how the definition might look:

```yaml
file_format: definition/2
# new attributes defined in this registry
attributes:
  - key: activemq.broker.name
    brief: The name of the ActiveMQ broker.
    ...
metrics:
  # based on https://github.com/open-telemetry/opentelemetry-java-instrumentation/blob/main/instrumentation/jmx-metrics/library/activemq.md
  - name: activemq.producer.count
    instrument: updowncounter
    stability: development
    brief: The number of producers attached to this destination
    unit: "{producer}"
    attributes:
      - ref: messaging.destination.name
      - ref: activemq.destination.type
      - ref: activemq.broker.name
imports:
  metrics:
    # this is not realistic, just an example of how to import existing metric
    - messaging.client.operation.duration
    # can also import by wildcard
    # - messaging.*

```

The *resolved* registry contains:

- everything defined in the registry
- definitions and refinements (from dependencies) for signals and attributes imported or referenced explicitly

Attributes and signals from dependencies that are not used by the registry are not
included by default.

Check out the [full example](https://github.com/open-telemetry/opentelemetry-weaver-examples/pull/33).

### Dependency resolution mechanism

Principles:

- **Latest version wins:** When a registry depends (transitively) on multiple versions
  of the same registry, only the latest version of that dependency is used during
  the resolution process.
  - If an object is referenced but only exists in an older version that was not selected,
    the resolution fails.
- **Only exact dependency versions are supported:** Version ranges are not supported at this time.
- **All signals and attributes are identifiable** via a specific property: metric name,
  event name, span type, entity type, or attribute key. Signal refinements have a unique ID.
- **Conflicts are not allowed:** If the resolution process discovers multiple attributes
  with the same key, or multiple signals or refinements with the same identity, the resolution fails.
  This rule applies within a single registry and across all its dependencies.
- **Source tracking:** Attributes and signal definitions, including their refinements,
  include provenance metadata that identifies the source registry and its version.
- **Extensibility:** The manifest format is designed to be
  extensible so that additional conflict-resolution hints can be added in the future in a non-breaking manner.

## Trade-offs and mitigations

### Schema Transformations

> [!NOTE]
>
> We will stop publishing current schema [file format 1.1.0](/specification/schemas/file_format_v1.1.0.md)
> which has [Development](/specification/document-status.md) status
>
> This is a breaking change for components that do schema transformation (such
> as Collector `schemaprocessor`)

Schema transformations (diffs) will **not** be published due to the following reasons:

- The resolved registry already includes information about deprecated (renamed) attributes
  and signals that can be used to apply rename transformations when upgrading versions.
- Ability to generate diffs on demand.
- Limited adoption and functionality not covering many existing transformation needs.
- Lack of test infrastructure around transformations, which resulted in several
  immutable schema files being incorrect (with no one complaining about it due to limited adoption).

While it's possible to publish the old schema in addition to the new manifest, it would mean
using a different URL format (such as `https://opentelemetry.io/schemas/v2/1.42.0` for
the new manifest), which would be confusing. More importantly, we believe it's not justified given
the limited actual usage.

Consumers that download Schema URL content today will start receiving a new
file format that they won't recognize and won't be able to use for their scenarios.

The only user of existing schema files we are aware of is [schemaprocessor](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/processor/schemaprocessor),
which was partially implemented about a year ago for schema transformations
but has not been included in the OTel Collector distribution.

The recommended update path for `schemaprocessor` is to add support for the new file format
while keeping support for file_format `1.1.0` to avoid breaking users.
This may involve two-step transformation when a version range is covered by both the old and the new
schema files.

Possible migration options are listed below.

We recommend starting with [Option 1: upgrades based on resolved registry](#migration-option-1-upgrades-based-on-resolved-registry-only).

For users or vendors that have implemented an approach similar to `schemaprocessor`
(that relies on the list of transformations), an alternative migration option
would be [Option 2: generate diff on demand](#migration-option-2-generate-diff-on-demand).

As schema transformations evolve and provide more capabilities, OpenTelemetry
could consider providing tooling and support for [Option 3: publish diff](#migration-option-3-publish-diff-in-the-future).

#### Migration option 1: upgrades based on resolved registry only

OpenTelemetry Semantic Conventions do not allow removing attributes, metrics,
and other identifiable signals from the registry.

When an attribute or signal is no longer recommended, it is deprecated. Backward compatibility checks enforce this policy.

Here's an example of deprecation in the resolved registry:

```yaml
attributes:
- key: http.method
  type: string
  stability: development
  deprecated:
    reason: renamed  # can also be `obsolete` or `uncategorized`
    renamed_to: http.request.method   # the replacement is validated to exist and not be deprecated.
    note: Replaced by `http.request.method`.
```

The schema version 1.N includes information about how to upgrade from v1.N-M to v1.N.
This approach is limited to one major version and covers upgrades only.

This option shares limitations with the existing schema transformation and
covers most of its capabilities. It can be used as a replacement, but in the future
[schema transformations may evolve](#schema-transformations-evolution) and this
approach won't be enough.

#### Migration option 2: generate diff on demand

To perform schema transformations, the schema processor and other possible consumers
are encouraged to use [`weaver registry diff`](https://github.com/open-telemetry/weaver/blob/main/docs/usage.md#weaver-registry-diff)
to generate diffs at startup (or lazily at runtime)
for the versions they want to support (e.g., vN → vTarget, vN+1 → vTarget):

```bash
weaver registry diff \
  --registry ./semconv-dev-1.38.0 \
  --baseline-registry ./semconv-dev-1.28.0 \
  --diff-format yaml \
  --output diff_v1.28.0_v1.38.0 \
  --v2
```

It produces a machine-readable summary of changes between versions similar to:

```yaml
schema_url: https://opentelemetry.io/schemas/semconv/1.39.0
registry:
  attribute_changes:
  - name: system.memory.linux.slab.state
    type: added
  - new_name: rpc.response.status_code
    old_name: rpc.connect_rpc.error_code
    type: renamed
...
```

The diff schema is formally documented as a JSON schema; see [overview](https://github.com/open-telemetry/weaver/blob/main/schemas/semconv-schemas.md#diff-schema)
and [full schema](https://github.com/open-telemetry/weaver/blob/main/schemas/semconv.diff.v2.json).

<details>

<summary>Calculating the diff between two arbitrary versions (supported by Weaver)
is relatively inexpensive.</summary>

Assuming data is already available locally, it takes approximately 100ms to run `weaver` directly
and approximately 1 second via `docker` on a modern laptop.

This currently includes time to unpack, read, validate, and resolve the source schema,
and can be optimized further by leveraging the resolved registry.

</details>

#### Migration option 3: publish diff in the future

In the future, based on the feedback and demand, we can return to publishing diffs.

At that point, we could update `weaver registry package` to allow diff-generation:

```bash
weaver registry package --include-diff --resolved-registry-uri <url>
```

and consider extending the publication manifest file format to include
a `diff_uri` field.

This can be done in a non-breaking manner.

### Documentation and code generation

Current code and documentation generation tooling uses schema v1.
Weaver will continue to support this format while the majority of OTel code-generation
scripts still use it.

In addition, Weaver allows opting into schema v2. Code and documentation
generation then receives [materialized resolved schema v2](https://github.com/open-telemetry/weaver/blob/main/schemas/semconv-schemas.md#materialized-resolved-schema).

Migration to v2 involves minor changes to Jinja2 templates and Weaver config files.
Migration steps and recipes will be documented. There should be no impact on the
generated documentation or artifacts affecting end users.

## Prior art and alternatives

See [Telemetry Schema](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.54.0/specification/schemas/README.md)
for the current state of the art.

See the [Semantic Conventions YAML schema](https://github.com/open-telemetry/weaver/blob/main/schemas/semconv-syntax.md) for the
current (v1) definition schema and [Weaver docs](https://github.com/open-telemetry/weaver?tab=readme-ov-file#usage)
for usage details.

## Open questions

### Schema transformations evolution

During stabilization efforts, when we overhauled HTTP, database, and code conventions,
we introduced different types of changes, including:

- Renamed attributes and metrics with or without behavior changes.
- Merged two attributes into one and split existing ones.
- Added or removed attributes to/from specific metrics and spans.
- Changed span name templates, error criteria, and made attributes opt-in due to
  high cardinality or sensitivity concerns.

Only simple renames without behavior changes could have been covered by the existing
schema transformation. We handled migration by supporting both new and old
conventions side-by-side in the instrumentation code.

The community has identified the need for transformations beyond renames in several discussions:
[weaver/450](https://github.com/open-telemetry/weaver/issues/450) and
[repo:open-telemetry/opentelemetry-specification schema transformation](https://github.com/search?q=repo%3Aopen-telemetry%2Fopentelemetry-specification+schema+transformation&type=issues).

> [!NOTE]
>
> While we make many breaking changes in unstable conventions, we have not
> made any breaking changes in stable ones. Given the high bar for breaking
> changes in stable conventions, schema transformations are unlikely to be useful
> for minor version updates.
>
> Schema transformations can provide huge value for major version upgrades or
> when converting between convention registries (ECS <-> OTel or
> [OTel gRPC <-> native gRPC conventions](https://github.com/open-telemetry/semantic-conventions/pull/3229)).

There are many design decisions to be made and gaps to be covered:

- Which DSL should be used to describe transformations (OTTL, SEL, invent one, etc.).
- How to describe upgrades and downgrades to arbitrary versions.
- Tooling that validates transformations against semantic conventions and telemetry.

We haven't gone through an extensive development and feedback cycle
and don't yet have confidence in how to solve these problems.

### Where should conventions belong?

Semantic convention maintainers have discussed general criteria: conventions used by
multiple distinct instrumentations SHOULD be documented in the central
`semantic-conventions` repository (e.g., database drivers implemented across multiple
languages), while component-specific conventions (e.g., JMX metrics for the Kafka client)
SHOULD remain in their respective repositories.

This OTEP focuses on building the technical stack to support multiple registries;
defining strict criteria is not a goal.

### What's the granularity for Collector and instrumentation-specific conventions?

Should we publish conventions for each individual instrumentation library or
OTel Collector component?

We recommend publishing conventions per distribution rather than per
component, but 1st-party instrumentations MAY publish conventions for their library only.

This OTEP does not intend to provide strict guidance.

## Prototypes

[Semantic conventions](https://github.com/open-telemetry/semantic-conventions/pull/2469)
in a release preparation step would:

- Resolve schema.
- Generate manifest.
- TODOs:
  - Generate stable and development versions.
  - Publish SemConv artifact as a GitHub release asset (and potentially on opentelemetry.io).

[Decentralized conventions example](https://github.com/open-telemetry/opentelemetry-weaver-examples/pull/33).
Generating [OTel Collector transformprocessor config to run schema transformations](https://github.com/open-telemetry/opentelemetry-weaver-examples/pull/36).

## Future possibilities

1. When releasing, publish a `latest` version under each schema family -
   for example `https://opentelemetry.io/schemas/semconv/latest` and
   `https://opentelemetry.io/schemas/semconv-dev/latest`.
   It should not be used by instrumentation/application code, but consumers can
   leverage it to learn about the latest schema (version and content).

2. We've been serving OTel schemas on opentelemetry.io and are proposing to also
   serve artifacts from GitHub release assets. If we see significantly higher demand,
   we'd need to consider other distribution options to support scale or
   reliability needs.
