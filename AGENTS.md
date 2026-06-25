# AGENTS.md

This repository contains the OpenTelemetry specification. This file is a short
routing guide for agents.

Canonical requirements and project guidance live in the repository documents.
If details differ, follow the canonical repository documents linked here,
especially [Contributing guidelines] and [Specification Principles].

## Contributing

- Follow [Contributing guidelines].

## Review Focus

- Ensure the change adheres to the OpenTelemetry Values and review against the
  [Specification Principles].
- Check if the changes are focused, vendor-neutral, and implementable across
  languages.
- Check related specification sections for conflicts in requirements,
  terminology, or data model behavior.
- For feature, behavior, or stability changes, check whether the pull request
  links to an issue or OTEP and includes prototype links.
- For SDK component configuration changes, check whether a corresponding
  proposed change exists in the [declarative configuration schema].
- In `specification/`, treat `MUST`, `MUST NOT`, `REQUIRED`, `SHOULD`,
  `SHOULD NOT`, `RECOMMENDED`, `NOT RECOMMENDED`, `MAY`, and `OPTIONAL` as
  BCP 14 terms only when they appear in all capitals.
- Flag lowercase modal wording such as "must", "should", and "may" in
  specification prose when it reads like an implementation requirement. For
  non-normative text, suggest neutral wording or explicit non-normative
  framing instead of hidden requirements.
- Verify the affected document or section [status] when a change adds, removes,
  or tightens requirements. Status is commonly marked with a `**Status**: ...`
  line or bold inline marker.
- Flag possible stability or breaking-change impact for human review,
  especially in Stable and Release Candidate content.

[Contributing guidelines]: CONTRIBUTING.md
[Specification Principles]: specification/specification-principles.md
[declarative configuration schema]: https://github.com/open-telemetry/opentelemetry-configuration

[status]: specification/document-status.md
