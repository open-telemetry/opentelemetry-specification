# Semantic Convention Schema v2

<!-- toc -->

- [Semantic Convention Schema v2](#semantic-convention-schema-v2)
  - [Motivation](#motivation)
  - [Details](#details)
    - [Semantic Conventions Schemas](#semantic-conventions-schemas)
    - [Differentiating between stable and not stable schemas](#differentiating-between-stable-and-not-stable-schemas)
    - [Building and publishing arbitrary semantic convention registries](#building-and-publishing-arbitrary-semantic-convention-registries)
  - [Trade-offs and mitigations](#trade-offs-and-mitigations)
    - [Schema Transformations](#schema-transformations)
      - [Migration option 1: upgrades based on resolved schema only](#migration-option-1-upgrades-based-on-resolved-schema-only)
      - [Migration option 2: generate diff on demand](#migration-option-2-generate-diff-on-demand)
    - [Documentation and code generation](#documentation-and-code-generation)
  - [Prior art and alternatives](#prior-art-and-alternatives)
  - [Open questions](#open-questions)
    - [Schema transformations evolution](#schema-transformations-evolution)
    - [Where should conventions belong?](#where-should-conventions-belong)
  - [Prototypes](#prototypes)
  - [Future possibilities](#future-possibilities)

<!-- tocstop -->

In this OTEP, we propose a new telemetry schema format that supports multiple convention registries
and provides full access to metadata.

It's built upon and is aligned with [OTEP 0243 - Introducing Application Telemetry Schema in OpenTelemetry - Vision and Roadmap](/oteps/0243-app-telemetry-schema-vision-roadmap.md)

## Motivation

Semantic Conventions describe the telemetry schema. Conventions hosted by OpenTelemetry describe
common concepts like HTTP, as well as telemetry produced by various OTel instrumentations.

OTel collector and language-specific instrumentations should be able to publish their
own conventions that are only applicable within their ecosystem. They should
also have a means to communicate the schema they use via [Schema URL](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.52.0/specification/schemas/README.md#schema-url).

Instrumentations that are not hosted by OTel should be able to document and publish
their own conventions that may take a dependency on the OTel ones.

Consumers of telemetry should be able to access the full schema to validate, upgrade,
refine, or sanitize the telemetry. The fully resolved schema, discoverable using
Schema URL, serves as an additional channel for metadata about telemetry. This approach
does not increase telemetry volume and associated costs.

Examples:

- Given a telemetry signal, a consumer should be able to find the full definition
  of the corresponding telemetry item. This enables several use cases:
  - UX hints and AI-assistants (explain what this metric measures or what this attribute means)
  - validation (does the telemetry item comply with the schema)
  - cost-saving (drop all non-essential metrics)
  - sanitization (based on annotations in the schema, redact potentially sensitive data)
- Document company/service-specific conventions taking OTel ones as a dependency
  and make their schemas accessible to consumers.
  See [OTEP 0243](/oteps/0243-app-telemetry-schema-vision-roadmap.md) for the details

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
file_format: 2.0.0
name: open-telemetry
description: OpenTelemetry Semantic Conventions
version: 1.39.0-dev
repository_url: https://github.com/open-telemetry/semantic-conventions
stability: development
resolved_schema_url: https://github.com/open-telemetry/semantic-conventions/archive/refs/tags/schema-v1.39.0-dev.yaml

# future
# diff_url: ...
# all_in_one_url: https://github.com/open-telemetry/semantic-conventions/archive/refs/tags/v1.39.0-dev.tar.gz
```

The manifest contains metadata about the semantic convention registry including its
version, stability, and `resolved_schema_url`.

The `resolved_schema_url` MUST be a valid URL that returns a YAML file with the [*resolved* schema](#semantic-conventions-schemas).
The service hosting Schema URL MUST support gzip compression that the caller MAY control with `Content-Encoding`.

The manifest format can evolve in a non-breaking manner. For example, we may start
publishing diffs against previous versions. The corresponding URL would be added
as a new property with a minor `file_format` version bump, without changing existing
features. Consumers can download only the parts they need, and we may provide
a single archive with all files for convenience.

All artifacts for a given release MUST be immutable. Consumers SHOULD make best efforts
to cache manifests and resolved schemas, or any parts of them, when used on the hot path.

The manifest schema and REST API to obtain it using Schema URL will be formally
documented for public, unauthenticated access.

See [Differentiating between stable and not stable schemas](#differentiating-between-stable-and-not-stable-schemas)
for details on the `-dev` suffix.

### Semantic Conventions Schemas

The [*definition* schema](https://github.com/open-telemetry/weaver/blob/main/schemas/semconv-syntax.v2.md)
used to write semantic conventions is not the same as the *resolved* schema.

For example, a metric could be defined in the following way in the *definition* schema:

```yaml
# definition schema
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

The *resolved* schema is a single file produced from a set of definitions. It contains
all attributes along with signal definitions and refinements. It is optimized for
distribution and in-memory representation.

*Resolved* schema for this metric looks like:

```yaml
# resolved schema
file_format: 2.0.0/resolved  # this could be versioned independently of manifest format
schema_url: https://opentelemetry.io/schemas/1.39.0
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

Resolved schema is formally documented as [JSON schema](https://github.com/lmolkova/weaver/blob/99af9dcc68cc271b9c719deec82a72e6fd5b4f40/schemas/semconv.resolved-schema.v2.json),
see [overview](https://github.com/lmolkova/weaver/blob/99af9dcc68cc271b9c719deec82a72e6fd5b4f40/schemas/semconv-schemas.md#resolved-schema).

Volume data point: resolved schema for [OTel Semantic Conventions v1.38.0](https://github.com/open-telemetry/semantic-conventions/releases/tag/v1.38.0)
is estimated around 1.2MB uncompressed and around 200KB compressed.

### Differentiating between stable and not stable schemas

Currently, Schema URL includes semantic convention version, but does not include
an indication of stability.

In addition to the version, we will leverage [SemVer pre-release](https://semver.org/#spec-item-9)
syntax to communicate the stability of the conventions and telemetry.

OpenTelemetry Semantic Conventions will publish two versions with each release:

- stable (e.g. `https://opentelemetry.io/schemas/1.39.0`) which will include only
  a stable subset of semantic conventions
- development (e.g. `https://opentelemetry.io/schemas/1.39.0-dev`) which will
  include all semantic conventions defined in the registry regardless of their
  stability.

The manifest file MUST include the actual stability level.

OpenTelemetry instrumentation SHOULD provide a Schema URL depending on the version
of conventions it follows.

For example, when HTTP instrumentation supports experimental features available
on top of HTTP conventions, and the user has enabled these experimental features, the instrumentation
SHOULD specify a `-dev` Schema URL.

### Building and publishing arbitrary semantic convention registries

TODO

## Trade-offs and mitigations

### Schema Transformations

> [!NOTE]
>
> We will stop publishing current schema [file format 1.1.0](/specification/schemas/file_format_v1.1.0.md)
> which has [Development](/specification/document-status.md) status
>
> This is a breaking change for components that do schema transformation (such
> as collector `schemaprocessor`)

Schema transformations (diffs) will **not** be published due to the following reasons:

- The resolved schema already includes information about deprecated (renamed) attributes
  and signals that can be used to apply rename transformations when upgrading versions.
- Ability to generate diffs on demand.
- Limited adoption and functionality not covering many existing transformation needs.
- Lack of test infrastructure around transformations, which resulted in several
  immutable schema files being incorrect (with no one complaining about it due to limited adoption).

While it's possible to publish the old schema in addition to the new manifest, it would mean
using a different URL format (such as `https://opentelemetry.io/schemas/v2/1.42.0` for
the new manifest), which would be confusing. More importantly, we believe it's not justified given
actual usage.

Consumers that download Schema URL content today will start receiving a new
file format that they won't recognize and won't be able to use for their scenarios.

The only user of existing schema files we are aware of is [schemaprocessor](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/processor/schemaprocessor),
which was partially implemented ~1 year ago for schema transformations
but has not been included in the OTel collector distribution.

The recommended update path for `schemaprocessor` is to add support for the new file format
while keeping support for file_format `1.1.0` to avoid breaking users.
This may involve two-step transformation when a version range is covered by both the old and the new
schema files.

#### Migration option 1: upgrades based on resolved schema only

OpenTelemetry Semantic Conventions don't allow removing attributes, metrics,
and other identifiable signals from the registry.

When an attribute or signal is no longer recommended, it gets deprecated. Backward compatibility checks enforce this policy.

Here's an example of deprecation in the resolved schema:

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

The schema version 1.N includes information on how to upgrade from v1.N-M to v1.N.
This approach is limited to one major version and covers upgrades only.

#### Migration option 2: generate diff on demand

To perform schema transformations, the schema processor and other possible consumers
are encouraged to use [`weaver registry diff`](https://github.com/open-telemetry/weaver/blob/main/docs/usage.md#registry-diff)
to generate diffs at startup (or lazily at runtime)
for versions they want to support, such as vN -> vTarget, vN+1 -> vTarget, etc.:

```bash
weaver registry diff \
  --registry ./schema-v1.38.0-dev \
  --baseline-registry ./schema-v1.28.0-dev \
  --diff-format yaml \
  --output diff_v1.28.0_v1.38.0 \
  --v2
```

It produces a diff file similar to:

```yaml
file_format: "2.0.0/diff"
schema_url: https://opentelemetry.io/schemas/1.39.0
registry:
  attribute_changes:
  - name: system.memory.linux.slab.state
    type: added
  - new_name: rpc.response.status_code
    old_name: rpc.connect_rpc.error_code
    type: renamed
...
```

The diff schema is formally documented as JSON schema; see the [overview](https://github.com/lmolkova/weaver/blob/99af9dcc68cc271b9c719deec82a72e6fd5b4f40/schemas/semconv-schemas.md#diff-schema)
and [full schema](https://github.com/lmolkova/weaver/blob/99af9dcc68cc271b9c719deec82a72e6fd5b4f40/schemas/semconv.diff.v2.json).

<details>

<summary>It's relatively cheap to calculate the diff between two arbitrary (supported by weaver)
versions.</summary>

Assuming data is already available locally, it takes ~100ms to run `weaver` directly
and ~1sec via `docker` on my relatively powerful MacBook Pro laptop.

It currently includes time to unpack, read, validate, and resolve source schema,
and can be optimized further by leveraging resolved schema.

</details>

It's also possible to publish a diff generation algorithm so that consumers can
generate transformation plans in memory without calling external tools such as `weaver`
or `docker`.

### Documentation and code generation

Current code and documentation generation tooling uses schema v1.
Weaver will continue supporting this format while the majority of OTel code-generation
scripts still use it.

In addition, weaver allows opting into Schema v2. Code and documentation
generation then receives [materialized resolved schema v2](https://github.com/lmolkova/weaver/blob/99af9dcc68cc271b9c719deec82a72e6fd5b4f40/schemas/semconv-schemas.md#materialized-resolved-schema).

Migration to v2 involves minor changes in Jinja2 templates and weaver config files.
Migration steps and recipes will be documented. There should be no impact on the
generated documentation or artifacts affecting end users.

## Prior art and alternatives

See [Telemetry Schema](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.53.0/specification/schemas/README.md)
for the current state of the art.

See the [Semantic Conventions YAML schema](https://github.com/open-telemetry/weaver/blob/main/schemas/semconv-syntax.md) for the
current (v1) definition schema and [Weaver docs](https://github.com/open-telemetry/weaver?tab=readme-ov-file#usage)
for usage details.

## Open questions

### Schema transformations evolution

During stabilization efforts, when we overhauled HTTP, database, and code conventions,
we introduced different types of changes. To name a few:

- Renamed attributes and metrics with or without behavior changes.
- Merged two attributes into one and split existing ones.
- Added or removed attributes to/from specific metrics and spans.
- Changed span name templates, error criteria, and made attributes opt-in due to
  cardinality or sensitivity.

Only simple renames without behavior changes could have been covered by the existing
schema transformation. We handled migration by supporting side-by-side new/old
conventions in the instrumentation code.

The community has identified the need for transformations beyond renames in several discussions:
[weaver/450](https://github.com/open-telemetry/weaver/issues/450) and
[repo:open-telemetry/opentelemetry-specification schema transformation](https://github.com/search?q=repo%3Aopen-telemetry%2Fopentelemetry-specification+schema+transformation&type=issues).

While we do many breaking changes in unstable conventions, we have not
made any breaking changes in stable ones. Given the high bar for breaking changes in stable
conventions, schema transformations are unlikely to be useful for minor version updates.

Schema transformations can provide huge value for major version upgrades or
when converting between convention registries (ECS <-> OTel or [OTel gRPC <-> native gRPC conventions](https://github.com/open-telemetry/semantic-conventions/pull/3229))
if we can formally describe a larger subset of changes and provide tooling to test them.

There are many design decisions to be made (e.g., a DSL to describe
transformations). We haven't gone through an extensive development and feedback cycle
and don't yet have confidence in how to solve this problem.

### Where should conventions belong?

Semantic convention maintainers have discussed rough criteria: conventions used by
multiple distinct instrumentations SHOULD be documented in the central
`semantic-conventions` repository (e.g., database drivers implemented across multiple
languages), while component-specific conventions (e.g., JMX metrics for the Kafka client)
SHOULD remain in their respective repositories.

This OTEP focuses on building the technical stack to support multiple registries;
defining strict criteria is not a goal.

## Prototypes

[Semantic conventions](https://github.com/open-telemetry/semantic-conventions/pull/2469)
in a release preparation step would:

- Resolve schema.
- Generate manifest.
- Publish SemConv artifact as a GitHub release asset (and potentially on opentelemetry.io).
- TODO: stable and not stable publishing.

TODO: imports/decentralized example
TODO: do we need collector prototype for schema transformation?

## Future possibilities

1. Return a list of all released semconv versions. E.g. `https://opentelemetry.io/schemas`
   would return a list of versions:

   ```json
   [
    "1.39.0",
    "1.39.0-dev",
    "1.38.0",
    //...
   ]
   ```

2. When releasing, publish `latest` version - `https://opentelemetry.io/schemas/latest/`.
   It should not be used by instrumentation/application code, but consumers can
   leverage it to learn about latest schema (version and content).

3. We've been serving OTel schemas on opentelemetry.io and are proposing to also
   serve artifacts from GitHub release assets. If we see significantly higher demand,
   we'd need to consider other distribution options to support scale or
   reliability needs.
