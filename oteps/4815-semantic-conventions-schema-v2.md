# Semantic Convention Schema v2

<!-- toc -->

- [Motivation](#motivation)
- [Details](#details)
  - [Resolved schema](#resolved-schema)
  - [Do we need to talk about importing and decentralization in details?](#do-we-need-to-talk-about-importing-and-decentralization-in-details)
  - [Differentiating between stable and not stable schemas](#differentiating-between-stable-and-not-stable-schemas)
- [Trade-offs and mitigations](#trade-offs-and-mitigations)
  - [Schema Transformation](#schema-transformation)
  - [Documentation and code generation](#documentation-and-code-generation)
- [Prior art and alternatives](#prior-art-and-alternatives)
- [Open questions](#open-questions)
  - [Schema processing evolution](#schema-processing-evolution)
- [Prototypes](#prototypes)
- [Future possibilities](#future-possibilities)

<!-- tocstop -->

In this OTEP, we propose a new telemetry schema format that supports multiple convention registries
and provides full access to metadata.

It's built upon and is aligned with [OTEP 0243 - Introducing Application Telemetry Schema in OpenTelemetry - Vision and Roadmap](/oteps/0243-app-telemetry-schema-vision-roadmap.md)

## Motivation

Semantic Conventions describe telemetry schema. Conventions hosted by OpenTelemetry describe
common concepts like HTTP and telemetry produced by different OTel instrumentations.

OTel collector and language-specific instrumentations should be able to publish their
own conventions that are only applicable within their ecosystem, and should
have means to communicate the schema they use with [Schema URL](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.52.0/specification/schemas/README.md#schema-url).

Instrumentations that are not hosted by OTel should be able to document and publish
their own conventions that may take a dependency on the OTel ones.

Consumers of telemetry should be able to access the full schema to validate, upgrade,
refine, or sanitize the telemetry. The fully resolved schema, discoverable using
Schema URL, serves as an additional channel for metadata about telemetry. This approach
does not increase telemetry volume and associated costs.

Examples:

- Given a telemetry signal, consumer should be able to find the full definition
  of the corresponding telemetry item. This enables quite a few use cases:
  - UX hints and AI-assistants (explain what this metric measures or what this attribute means)
  - validation (does the telemetry item comply with the schema)
  - cost-saving (drop all non-essential metrics)
  - sanitization (based on annotations in the schema, redact potentially sensitive data)
- Document company/service-specific conventions taking OTel ones as a dependency
  and make their schemas accessible to consumers.
  See [OTEP 0243](/oteps/0243-app-telemetry-schema-vision-roadmap.md) for the details

[Telemetry Schema](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.52.0/specification/schemas/README.md)
has built the foundation for these scenarios, but does not fully support them -
it's designed around schema transformations and describes diff between schema
versions such as attribute or metric renames. While it can work under the assumption
that there is a single registry (OpenTelemetry Semantic Conventions), it needs
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

The `resolved_schema_url` MUST be a valid URL that returns YAML file with the [*resolved* schema](#resolved-schema).
The service hosting Schema URL MUST support gzip compression that caller MAY control with `Content-Encoding`.

The manifest format will evolve. For example, we may start publishing diffs againts
previous version(s) and corresponding URL will be added as the new property with a
minor version bump. Consumers will decide to download parts they actually use.

All artifacts for a given release MUST be immutable. Consumers SHOULD make best efforts
to cache manifests and resolved schemas or any parts of them used on the hot path.

The manifest schema and REST API to obtain it using Schema URL will be formally
documented for public, unauthenticated access.

See [Differentiating between stable and not stable schemas](#differentiating-between-stable-and-not-stable-schemas)
for details on the `-dev` suffix.

### Resolved schema

The [*source* schema](https://github.com/open-telemetry/weaver/blob/main/schemas/semconv-syntax.v2.md)
used to write semantic conventions is not the same as *resolved* schema.

For example, a metric could be defined in the following way in the *source* schema:

```yaml
# source schema
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

Attributes are defined separately from metrics and are referenced,
optimizing reusability and consistency. Defaults or inherited properties are
omitted.

The *resolved* schema is a single file produced from a set of source schemas. It contains resolved
signal definitions and refinements. It is optimized for
distribution and in-memory representation.

*Resolved* schema for this metric would look like:

```yaml
# resolved schema
file_format: 2.0.0  # this could be versioned independently of manifest format
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

Resolved schema is formally documented as [JSON schema](https://github.com/lmolkova/weaver/blob/c61cfd13b8f4f1694b451862ea7345868978819e/schemas/semconv.resolved-schema.v2.json), see [overview](https://github.com/lmolkova/weaver/blob/c61cfd13b8f4f1694b451862ea7345868978819e/schemas/semconv-schemas.md#resolved-schema).

Volume data point: resolved schema for [OTel Semantic Conventions v1.38.0](https://github.com/open-telemetry/semantic-conventions/releases/tag/v1.38.0)
is estimated around 1.2MB uncompressed and around 200KB compressed.

### Differentiating between stable and not stable schemas

Currently, Schema URL includes semantic convention version, but does not include
indication of stability.

In addition to the version, we will leverage [SemVer pre-release](https://semver.org/#spec-item-9)
syntax to communicate the stability of the conventions and telemetry.

OpenTelemetry Semantic Conventions will publish two versions with each release:

- stable (e.g. `https://opentelemetry.io/schemas/1.39.0`) which will include only
  a stable subset of semantic conventions
- development (e.g. `https://opentelemetry.io/schemas/1.39.0-dev`) which will
  include all semantic conventions defined in the registry regardless of their
  stability

Manifest file MUST include actual stability level.

OpenTelemetry instrumentation SHOULD provide a Schema URL depending on which version
of conventions they follow.

For example, when HTTP instrumentation supports experimental features available
on top of HTTP conventions, and user enabled these experimental features, instrumentation
should specify a `-dev` Schema URL.

### Do we need to talk about importing and decentralization in details?

TODO

## Trade-offs and mitigations

> [!NOTE]
>
> We will stop publishing current schema [file format 1.1.0](/specification/schemas/file_format_v1.1.0.md)
> which has [Development](/specification/document-status.md) status
>
> This is a breaking change for:
>
> - schema transformation (collector `schemaprocessor`)
> - documentation and code generation scripts

Consumers that download content of Schema URL today will start receiving new
file format that they won't recognize and won't be able to perform their scenarios.

The only user of existing schema files we are aware of is [schemaprocessor](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/processor/schemaprocessor), which was partially implemented ~1 year ago to do schema transformations,
but has not been included in OTel collector distribution.

### Schema Transformation

Schema transformations (diffs) will not be published due to:

- limited adoption and functionality not covering many existing upgrade cases
- ability to generate them on demand
- lack of test infrastructure around tranformations and known

While it's possible to publish old schema side-by-side with a new one, it would mean
using a different URL format (such as `https://opentelemetry.io/schemas/v2/1.42.0`)
which would be confusing. More importantly, we believe it's not justified taking into
account actual usage.

In order to perform schema transformations, schema processor and other possible consumers
are encouraged to use [`weaver registry diff`](https://github.com/open-telemetry/weaver/blob/main/docs/usage.md#registry-diff)
to pre-generate at start time (or generate lazily at runtime) the list of diffs
for versions they want to support such as vN -> vTarget, vN+1 -> vTarget, etc:

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
registry:
  attribute_changes:
  - name: system.memory.linux.slab.state
    type: added
  - new_name: rpc.response.status_code
    note: Replaced by `rpc.response.status_code`.
    old_name: rpc.connect_rpc.error_code
    type: renamed
...
```

Diff schema is formally documented as JSON schema, see [overview](https://github.com/lmolkova/weaver/blob/c61cfd13b8f4f1694b451862ea7345868978819e/schemas/semconv-schemas.md#diff-schema)
and [full schema](https://github.com/lmolkova/weaver/blob/c61cfd13b8f4f1694b451862ea7345868978819e/schemas/semconv.diff.v2.json).

<details>

<summary>It's relatively cheap to calculate the diff between two arbitrary (supported by weaver)
versions.</summary>

Assuming data is already available locally, it takes ~100ms and ~500ms on two different
machines I tried. It currently includes time to unpack, read, validate, and
resolve source schema, and can be optimized further by leveraging resolved schema.
</details>

### Documentation and code generation

Weaver supports Schema V2 as opt-in feature and will default to old schema format
until a majority of OTel code-generation scripts use it.

Migration will involve minor changes in Jinja2 templates and weaver config files.
Migration steps and recipes will be documented. There should be no impact on the
generated documentation or artifacts affecting end users.

## Prior art and alternatives

See [Telemetry Schema](https://github.com/open-telemetry/opentelemetry-specification/blob/v1.52.0/specification/schemas/README.md)
for the current state of the art.

## Open questions

### Schema processing evolution

Based on the previous discussions in the community ([weaver/450](https://github.com/open-telemetry/weaver/issues/450),
[repo:open-telemetry/opentelemetry-specification schema transformation](https://github.com/search?q=repo%3Aopen-telemetry%2Fopentelemetry-specification+schema+transformation&type=issues)) we've identified
that the need for transformations is not limited to renames. Applying certain
transformations in isolation may produce otherwise invalid
telemetry items (e.g. renaming existing attribute but not adding new required attribute).
Transformations need to support upgrades and downgrades.
So while transformations are extremely useful, they could be extremely complicated.

The existing story around schema transformations didn't go through extensive development
and feedback cycle and we don't have confidence that weaver diff schema is sufficient
for the future transformation needs. It's also not clear if schema transformation
would still be necessary once the core set of semantic conventions is stabilized.

Weaver diff should evolve along with schema transformation adoption and eventually
may be included in the published artifacts.

## Prototypes

[Semantic conventions](https://github.com/open-telemetry/semantic-conventions/pull/2469)
in a release preparation step would:

- resolve schema
- generate manifest
- publish SemConv artifact as a GitHub release asset (and potentially on opentelemetry.io)
- TODO: stable and not stable publishing

TODO: do we need collector prototype for schema transformation?
TODO: do we need imports/decentralized example

## Future possibilities

1. Schema transformation may be applicable between different convention registries.
   For example, between ECS and OTel or between [OTel gRPC and native gRPC conventions](https://github.com/open-telemetry/semantic-conventions/pull/3229)

2. We've been serving OTel schemas on opentelemetry.io and are proposing to start
   serving artifacts from GitHub assets. If we see significantly higher demand,
   we'd need to consider other distribution options that would support scale or
   reliability needs.
