# Copilot instructions for OpenTelemetry specification

This repository contains the OpenTelemetry specification. Prefer reviews that
protect specification consistency, clear normative language, stability,
interoperability, and OpenTelemetry project values.

## Review priorities

- Check specification changes against related sections and documents. Flag
  conflicts with existing requirements, terminology, data model behavior, or
  compliance matrix entries.
- Evaluate changes against the canonical
  [Specification Principles](../specification/specification-principles.md):
  Be User Driven, Be General, Be Stable, Be Consistent, and Be Simple.
- Evaluate changes against OpenTelemetry
  [Mission and Values](../specification/specification-principles.md):
  Telemetry should be easy, Telemetry should be universal,
  Telemetry should be vendor-neutral, Telemetry should be loosely-coupled,
  Telemetry should be built-in, Compatibility, Stability, Resilience, and
  Performance.
- Prefer precise comments that cite the conflicting file, section, or existing
  rule. Avoid comments for issues already covered by automation.

## Normative language

- For `specification/`, treat `MUST`, `MUST NOT`, `REQUIRED`, `SHOULD`,
  `SHOULD NOT`, `RECOMMENDED`, `NOT RECOMMENDED`, `MAY`, and `OPTIONAL` as
  BCP 14 terms only when they appear in all capitals.
- Recommend uppercase BCP 14 keywords only for implementation requirements.
- For non-normative text, flag lowercase modal wording such as "must",
  "should", and "may". Suggest neutral descriptive wording such as "can",
  "typically", or direct phrasing.
- If a change adds, removes, or tightens normative requirements, verify that the
  affected document or section is marked `**Status**: [Development]` (per
  [document status](../specification/document-status.md)); otherwise, flag it
  unless the PR explains an approved stability exception.
- For notes, examples, operational guidance, and supplementary guidance, flag
  wording that reads like a hidden requirement.

## Specification process and validation

- For non-trivial changes, check for an accepted issue or OTEP link, required
  prototypes, changelog impact, compliance matrix impact, and declarative
  configuration schema impact.
- Prefer focused diffs that stay implementable across languages and avoid
  unnecessary implementation details.
