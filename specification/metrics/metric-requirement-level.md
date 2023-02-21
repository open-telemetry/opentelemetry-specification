# Metric Requirement Levels for Semantic Conventions

**Status**: [Experimental](../document-status.md)

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [Required](#required)
- [Conditionally Required](#conditionally-required)
- [Recommended](#recommended)
- [Opt-In](#opt-in)

<!-- tocstop -->

</details>

The following metric requirement levels are specified:

- [Required](#required)
- [Conditionally Required](#conditionally-required)
- [Recommended](#recommended)
- [Optional](#optional)

## Required

All instrumentations MUST emit the metric. A semantic convention defining a Required metric expects that an absolute majority of instrumentation libraries and applications are able to efficiently emit it. `http.server.duration` is an example of a Required metric.

## Conditionally Required

All instrumentations MUST emit the metric when given condition is satisfied. Semantic convention of a `Conditionally Required` level of a metric MUST clarify the condition under which the metric is expected to be emitted.

When the condition on a `Conditionally Required` metric is not satisfied and there is no requirement to emit the metric, semantic conventions MAY provide special instructions on how to handle it. If no instructions are given and if instrumentation can emit the metric, instrumentation SHOULD use the `Opt-In` requirement level on the metric.

## Recommended

Instrumentations SHOULD emit the metric by default if it's readily available and can be efficiently emitted. Instrumentations MAY offer a configuration option to disable Recommended metrics.

Instrumentations that decide not to emit `Recommended` metrics due to performance, security, privacy, or other consideration by default, SHOULD use the `Opt-In` requirement level on them if the metrics are logically applicable.

## Opt-In

Instrumentations SHOULD emit the metric if and only if the user configures the instrumentation to do so. Instrumentation that doesn't support configuration MUST NOT emit `Opt-In` metrics.
