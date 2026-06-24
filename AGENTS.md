# AGENTS.md

## Purpose

This repository contains the OpenTelemetry specification. Agents should protect
specification consistency, clear normative language, stability,
interoperability, and OpenTelemetry project values.

Treat this file as a concise routing guide. When details differ, follow the
canonical repository documents linked here, especially [CONTRIBUTING.md],
[Specification Principles], [Notation Conventions and Compliance], and
[Document Statuses].

## Repository Guidance

- Specification content is written in Markdown and should render correctly on
  GitHub. Prefer line breaks at 80 characters.
- Use the project name "OpenTelemetry" and acronym "OTel" as described in
  [Project Naming].
- Keep changes focused and implementable across languages. Avoid unnecessary
  implementation details in specification text.

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
- For non-trivial changes, check for an accepted issue or OTEP link, required
  prototypes, changelog impact, compliance matrix impact, and declarative
  configuration schema impact.

## Contribution Process Checks

- New features at Development maturity require a prototype in a spec-bound
  implementation with SIG maintainer support. Stabilization requires prototypes
  in multiple languages; three is typical.
- If SDK component configuration is added or changed, check for a corresponding
  proposed change to the declarative configuration schema.
- Non-trivial pull requests should update the `Unreleased` section of
  [CHANGELOG.md] under the appropriate subsection.

## Normative Language and Status

- For `specification/`, treat `MUST`, `MUST NOT`, `REQUIRED`, `SHOULD`,
  `SHOULD NOT`, `RECOMMENDED`, `NOT RECOMMENDED`, `MAY`, and `OPTIONAL` as
  BCP 14 terms only when they appear in all capitals.
- Recommend uppercase BCP 14 keywords only for implementation requirements.
- For non-normative text, flag lowercase modal wording such as "must",
  "should", and "may". Suggest neutral descriptive wording such as "can",
  "typically", or direct phrasing.
- If a change adds, removes, or tightens normative requirements, verify the
  affected document or section status. Status is commonly marked with a
  `**Status**: [...]` line or bold inline marker, not a literal code span.
  Flag changes that exceed the maturity level unless the pull request explains
  an approved stability exception.
- For notes, examples, operational guidance, and supplementary guidance, flag
  wording that reads like a hidden requirement.

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
[Mission and Values]: specification/specification-principles.md
[Notation Conventions and Compliance]: specification/README.md
[Project Naming]: specification/README.md
[Specification Principles]: specification/specification-principles.md
