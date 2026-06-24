# Copilot instructions for OpenTelemetry specification

This repository contains the OpenTelemetry specification. Prefer reviews that
protect specification consistency, clear normative language, stability,
interoperability, and OpenTelemetry project values.

## Review priorities

- Check specification changes against related sections and documents. Flag
  conflicts with existing requirements, terminology, data model behavior, or
  compliance matrix entries.
- Evaluate changes against the Specification Principles: user driven, general,
  stable, consistent, and simple.
- Evaluate changes against the OpenTelemetry mission and engineering values:
  portable telemetry, vendor neutrality, loose coupling, compatibility,
  stability, resilience, and performance.
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
  affected document or section is marked `Development`; otherwise, flag it
  unless the PR explains an approved stability exception.
- For notes, examples, operational guidance, and supplementary guidance, flag
  wording that reads like a hidden requirement.

## Specification process and validation

- For non-trivial changes, check for accepted issue or OTEP links, required
  prototypes, changelog impact, compliance matrix impact, and declarative
  configuration schema impact.
- Prefer focused diffs that stay implementable across languages and avoid
  unnecessary implementation details.
