# Separate Semantic Conventions

Move Semantic Conventions outside of the main Specifications and version them
separately.

## Motivation

We need to allow semantic conventions to evolve mostly independent of the
overall OpenTelemetry specification. Today, any breaking change in a semantic
convention would require bumping the version number of the entirety of the
OpenTelemetry specification.

## Explanation

A new GitHub repository called `semantic-conventions` would be created in the
OpenTelemetry organization.

This would *initially* have the following structure:

- Boilerplate files, e.g. `README.md`, `LICENSE`, `CODEOWNERS`, `CONTRIBUTING.md`
- `Makefile` that allows automatic generation of documentation from model.
- `semantic_conventions/` The set of YAML files that exist in
  `{specification}/semantic_conventions` today.
- `docs/` A new directory that contains human readable documentation for how to
  create instrumentation compliant with semantic conventions.
  - `resource/` - Contents of `{specification}/resource/semantic_conventions`
  - `trace/` - Contents of `{specification}/trace/semantic_conventions`
  - `metrics/` - Contents of `{specification}/metrics/semantic_conventions`
  - `logs/`- Contents of `{specification}/logs/semantic_conventions`
  - `schemas/` - A new location for [Telemetry Schemas](https://github.com/open-telemetry/semantic-conventions/tree/main/schemas)
    to live. This directory will be hosted at
    `https://opentelemetry.io/schemas/`

Existing semantic conventions in the specification would be marked as
moved, with documentation denoting the move, but preserving previous contents.

Additionally, if the semantic conventions eventually move to domain-specific
directory structure (e.g. `docs/{domain}/README.md`, with trace, metrics, events
in the same file), then this can be refactored in the new repository, preserving
git history.

There will also be the following exceptions in the specification:

- Semantic conventions used to implement API/SDK details will be fully specified in the `opentelemetry-specification` repo
  and will not be allowed to change in the Semantic Convention directory.
  - Error/Exception handling will remain in the specification.
  - SDK configuration interaction w/ semantic convention will remain in the
    specification. Specifically `service.name`.
- The specification may elevate some semantic conventions as necessary for
  compatibility requirements, e.g. `service.instance.id` and
  [Prometheus Compatibility](../specification/compatibility/prometheus_and_openmetrics.md).

These exceptions exist because:

- Stable portions of the specification already rely on these conventions.
- These conventions are required to implement an SDK today.

As such, the Specification should define the absolute minimum of reserved or
required attribute names and their interaction with the SDK.

## Internal details

The following process would be used to ensure semantic conventions are
seamlessly moved to their new location. This process lists steps in order:

- A moratorium will be placed on Semantic Convention PRs to the specification
  repository. (Caveat that PRs related to this proposal would be allowed).
- Interactions between Semantic Conventions and the Specification will be
  extracted such that the Specification can place requirements on Semantic
  Conventions and *normative* specification language will remain in the
  core specification directories.
- A new repository `open-telemetry/semantic-conventions` will be constructed with
  the proposed format and necessary `Makefile` / tooling.
  - The new repository would be created by using `git filter-branch` to preserve
    all existing semantic convention history. *This means all existing
    semantic conventions will be in the new repository*.
  - GitHub Actions, `Makefile` tooling and contributing / readmes would be
    updated for the separate repository.
  - **Note: At this point, the new location for semantic conventions should
      be adoptable/usable.**
- Semantic conventions in the Specification will be marked as moved with
  links to the new location.
  - The semconv YAML files in the specification repository *will be deleted*.
  - All semconv markdown files will be updated such that:
    - They no longer generate from YAML files.
    - They include a header denoting deprecation and move to the new repository.
- Instrumentation authors will update their code generation to pull from the new
  semconv repository instead of the specification repository.

## Trade-offs and mitigations

This proposal has a few drawbacks:

- The semantic conventions will no longer be easily referenceable form the specification.
  - This is actually a benefit. We can ensure isolation of convention from
    specification and require the Specification to use firm language for
    attributes it requires, like `service.name`.
  - We will provide links from existing location to the new location.
- Semantic Convention version will no longer match the specification version.
  - Instrumentation authors will need to consume a separate semantic-convention
    bundle from Specification bundle. What used to be ONE upgrade effort will
    now be split into two (hopefully smaller) efforts.
  - We expect changes from Semantic Conventions and Specification to be
    orthogonal, so this should not add significant wall-clock time.
- Existing PRs against semantic conventions will need to be regenerated.

Initially this repository would have the following ownership:

- Approvers
  - [Christian Neumüller](https://github.com/Oberon00), Dynatrace
  - [James Moessis](https://github.com/jamesmoessis), Atlassian
  - [Joao Grassi](https://github.com/joaopgrassi), Dynatrace
  - [Johannes Tax](https://github.com/pyohannes), Microsoft
  - [Liudmila Molkova](https://github.com/lmolkova), Microsoft
  - [Sean Marcinak](https://github.com/MovieStoreGuy), Atlassian
  - [Ted Young](https://github.com/tedsuo), Lightstep
- Approvers (HTTP Only)
  - [Trask Stalnaker](https://github.com/trask)
- Approvers (SchemaUrl Files)
  - [Tigran Najaryan](https://github.com/tigrannajaryan)
- Maintainers
  - [Josh Suereth](https://github.com/jsuereth)
  - [Armin Ruech](https://github.com/arminru)
  - [Reiley Yang](https://github.com/reyang)

That is, Maintenance would initially continue to fall on (a subset of) the
Technical Committee. Approvers would start with existing semconv approvers in
addition to targeted at HTTP semantic convention stability approvers and
expand rapidly as we build momentum on semantic conventions.

## Prior art and alternatives

When we evaluate equivalent communities and efforts we see the following:

- `OpenTracing` - had specification and [semantics](https://github.com/opentracing/specification/blob/master/semantic_conventions.md)
  merged.
- `OpenCensus` - had specification and semantics merged. However, OpenCensus
  merged with OpenTelemetry prior to mass adoption or stable release of its
  specification.
- `Elastic Common Schema` - the schema is its own project / document.
- `Prometheus` - Prometheus does not define rigid guidelines for telemetry, like
  semantic conventions, instead relying on naming conventions and
  standardization through mass adoption.

## Open questions

This OTEP doesn't address the full needs of tooling and codegen that will be
needed for the community to shift to a separate semantic convention directory.
This will require each SIG that uses autogenerated semantic conventions to
adapt to the new location.

The first version of the new location for semantic conventions may not follow
the latest of the specification. There is reasoning to desire a `2.0` but the
details will be discussed in the new repository location upon execution of this
OTEP.

## Future possibilities

This OTEP paves way for the following desirable features:

- Semantic Conventions can decide to bump major version numbers to accommodate
  new signals or hard-to-resolve new domains without breaking the Specification
  version number.
- Semantic Conventions can have dedicated maintainers and approvers.
- Semantic Conventions can restructure to better enable subject matter experts
  (SMEs) to have approver/CODEOWNER status on relevant directories.
- Semantic Conventions can adopt semantic versioning for itself, helping clearly
  denote breaking changes to users.

There is a desire to move semantic conventions to domain-specific directories
instead of signal-specific. This can occur after the separation of the repository
and will be proposed and discussed separately from this OTEP.

For example:

- `docs/`
  - `signals/` - Conventions for metrics, traces + logs
    - `http/`
    - `db/`
    - `messaging/`
    - `client/`
  - `resource/` - We still need resource-specific semantic conventions
