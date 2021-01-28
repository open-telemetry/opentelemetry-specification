# Semantic Conventions for Runtime Environment Metrics

**Status**: [Experimental](../../document-status.md)

This document includes semantic conventions for runtime environment level
metrics in OpenTelemetry. Also consider the [general
metric](README.md#general-metric-semantic-conventions), [system
metrics](system-metrics.md) and [OS Process metrics](process-metrics.md)
semantic conventions when instrumenting runtime environments.

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [Metric Instruments](#metric-instruments)
  * [Runtime Environment Specific Metrics - `runtime.{environment}.`](#runtime-environment-specific-metrics---runtimeenvironment)

<!-- tocstop -->

## Metric Instruments

Runtime environments vary widely in their terminology, implementation, and
relative values for a given metric. For example, Go and Python are both
garbage collected languages, but comparing heap usage between the Go and
CPython runtimes directly is not meaningful. For this reason, this document
does not propose any standard top-level runtime metric instruments. See [OTEP
108](https://github.com/open-telemetry/oteps/pull/108/files) for additional
discussion.

### Runtime Environment Specific Metrics - `runtime.{environment}.`

Metrics specific to a certain runtime environment should be prefixed with
`runtime.{environment}.` and follow the semantic conventions outlined in
[general metric semantic
conventions](README.md#general-metric-semantic-conventions). Authors of
runtime instrumentations are responsible for the choice of `{environment}` to
avoid ambiguity when interpreting a metric's name or values.

For example, some programming languages have multiple runtime environments
that vary significantly in their implementation, like [Python which has many
implementations](https://wiki.python.org/moin/PythonImplementations). For
such languages, consider using specific `{environment}` prefixes to avoid
ambiguity, like `runtime.cpython.` and `runtime.pypy.`.

There are other dimensions even within a given runtime environment to
consider, for example pthreads vs green thread implementations.
