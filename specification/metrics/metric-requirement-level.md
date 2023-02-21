# Metric Requirement Levels for Semantic Conventions

**Status**: [Experimental](../document-status.md)

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

All instrumentations MUST emit the metric. A semantic convention defining a Required metric expects that an absolute majority of instrumentation libraries and applications are able to efficiently emit it. `http.server.duration` is an example of a Required metric.

## Recommended

Instrumentations SHOULD emit the metric by default if it's readily available and can be efficiently emitted. Instrumentations MAY offer a configuration option to disable Recommended metrics.

Instrumentations that decide not to emit `Recommended` metrics due to performance, security, privacy, or other consideration by default, SHOULD use the `Opt-In` requirement level on them if the metrics are logically applicable.

## Opt-In

Instrumentations SHOULD emit the metric if and only if the user configures the instrumentation to do so. Instrumentation that doesn't support configuration MUST NOT emit `Opt-In` metrics.
