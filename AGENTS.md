# AGENTS.md

## Purpose and Scope

This repository contains the OpenTelemetry specification. Agent work should
protect specification consistency, interoperability, stability, clear normative
language, and OpenTelemetry project values.

Treat this file as a concise routing guide for the whole repository. If details
differ, follow the canonical repository documents linked here, especially
[CONTRIBUTING.md], [Specification Principles],
[Notation Conventions and Compliance], and [Document Statuses].

## Baseline Editing Guidance

- Specification content is written in Markdown and should render correctly on
  GitHub. Prefer line breaks at 80 characters.
- Use the project name "OpenTelemetry" and acronym "OTel" as described in
  [Project Naming].
- Keep changes focused, vendor-neutral, and implementable across languages.
- Prefer specification text that describes what must interoperate, not how each
  language or implementation must be built.
- Preserve existing headings, anchors, status markers, reference links, and
  table-of-contents markers unless the change explicitly requires updating
  them.

## Review Priorities

- Check specification changes against related sections and documents. Flag
  conflicts with existing requirements, terminology, data model behavior, or
  compliance matrix entries.
- Evaluate changes against the canonical [Specification Principles]:
  Be User Driven, Be General, Be Stable, Be Consistent, and Be Simple.
- Evaluate changes against OpenTelemetry [Mission and Values]:
  Telemetry should be easy, Telemetry should be universal,
  Telemetry should be vendor-neutral, Telemetry should be loosely-coupled,
  Telemetry should be built-in, Compatibility, Stability, Resilience, and
  Performance.
- For non-trivial changes, check for an accepted issue or OTEP covered by the
  [OTEP process], required prototypes, whether [CHANGELOG.md] or compliance
  matrix entries need updates, and declarative configuration schema impact.

## Process Checks

- New features at Development maturity require a prototype in a spec-bound
  implementation with SIG maintainer support.
- Stabilization requires prototypes in multiple languages. Three languages is
  typical, with coverage across typed object-oriented, dynamically typed, and
  structural ecosystems when relevant.
- Protocol changes should be prototyped on both the client and server sides.
- If SDK component configuration is added or changed, check for a corresponding
  proposed change to the [declarative configuration schema][config schema].
- If compliance matrix source YAML changes, update the generated matrix and do
  not require a changelog entry for that matrix-only update.

## Normative Language and Status

- For `specification/`, treat `MUST`, `MUST NOT`, `REQUIRED`, `SHOULD`,
  `SHOULD NOT`, `RECOMMENDED`, `NOT RECOMMENDED`, `MAY`, and `OPTIONAL` as
  BCP 14 terms only when they appear in all capitals.
- Recommend uppercase BCP 14 keywords only for implementation requirements
  needed for interoperability or to avoid harm.
- Treat lowercase modal wording such as "must", "should", and "may" as
  suspect in specification prose. For non-normative text, suggest neutral
  wording such as "can", "typically", or direct phrasing. Do not mechanically
  rewrite quotations or external standard language.
- For notes, examples, operational guidance, and supplementary guidance, flag
  wording that reads like a hidden requirement.
- If a change adds, removes, or tightens normative requirements, verify the
  affected document or section status. Status is commonly marked with a
  `**Status**: ...` line or bold inline marker. No explicit status is
  equivalent to Alpha; `Mixed` means individual sections can have different
  statuses.
- Flag changes that exceed the affected maturity level unless the PR explains
  an approved stability exception. Stable and Release Candidate content should
  avoid breaking changes except under special circumstances.

## Validation Commands

- Install dependencies with `npm install` after installing the latest LTS
  release of Node.js.
- Run all checks with `make check`.
- Run focused checks with `make language-analysis`, `make markdownlint`, or
  `make markdown-link-check`. Link checking requires Docker and can take a long
  time.
- Run `make fix` for textlint autofixes.
- Run `make markdown-toc` after changing Markdown files with table-of-contents
  markers.
- If compliance matrix source YAML changes, run `make compliance-matrix`.

[CHANGELOG.md]: CHANGELOG.md
[CONTRIBUTING.md]: CONTRIBUTING.md
[Document Statuses]: specification/document-status.md
[config schema]: https://github.com/open-telemetry/opentelemetry-configuration
[Mission and Values]: specification/specification-principles.md
[Notation Conventions and Compliance]: specification/README.md
[OTEP process]: oteps/README.md
[Project Naming]: specification/README.md
[Specification Principles]: specification/specification-principles.md
