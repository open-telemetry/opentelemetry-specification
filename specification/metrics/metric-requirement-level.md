# Metric Requirement Levels for Semantic Conventions

**Status**: [Stable](../document-status.md)

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [Required](#required)
- [Recommended](#recommended)
- [Opt-In](#opt-in)

<!-- tocstop -->

</details>

The following metric requirement levels are specified:

- [Required](#required)
- [Recommended](#recommended)
- [Opt-In](#opt-in)

## Required

All instrumentations MUST emit the metric.
A semantic convention defining a Required metric expects that an absolute majority of instrumentation libraries and applications are able to efficiently emit it.

## Recommended

Instrumentations SHOULD emit the metric by default if it's readily available and can be efficiently emitted. Instrumentations MAY offer a configuration option to disable Recommended metrics.

Instrumentations that decide not to emit `Recommended` metrics due to performance, security, privacy, or other consideration by default, SHOULD allow for opting in to emitting them as defined for the `Opt-In` requirement level if the metrics are logically applicable.

## Opt-In

Instrumentations SHOULD emit the metric if and only if the user configures the instrumentation to do so.
Instrumentation that doesn't support configuration MUST NOT emit `Opt-In` metrics.

This attribute requirement level is recommended for metrics that are particularly expensive to retrieve or might pose a security or privacy risk. These should therefore only be enabled deliberately by a user making an informed decision.
