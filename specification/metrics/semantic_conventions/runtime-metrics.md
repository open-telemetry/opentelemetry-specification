# Semantic Conventions for Runtime Metrics

This document describes instruments and labels for common runtime level
metrics in OpenTelemetry. Also consider the general [semantic conventions for
system metrics](system-metrics.md#semantic-conventions) when creating
instruments not explicitly defined in this document.

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [Metric Instruments](#metric-instruments)
  * [Runtime Metrics - `runtime.`](#runtime-metrics---runtime)
    + [Runtime Specific Metrics - `runtime.{environment}.`](#runtime-specific-metrics---runtimeenvironment)

<!-- tocstop -->

## Metric Instruments

### Runtime Metrics - `runtime.`

Runtime environments vary widely in their terminology, implementation, and
relative values for a given metric. For example, Go and Python are both
garbage collected languages, but comparing heap usage between the two
runtimes directly is not meaningful. For this reason, this document does not
propose any standard top-level runtime metric instruments. See [OTEP
108](https://github.com/open-telemetry/oteps/pull/108/files) for additional
discussion.

#### Runtime Specific Metrics - `runtime.{environment}.`

Runtime level metrics specific to a certain runtime environment should be
prefixed with `runtime.{environment}.` and follow the semantic conventions
outlined in [semantic conventions for system
metrics](system-metrics.md#semantic-conventions). For example, Go runtime
metrics use `runtime.go.` as a prefix.

Some programming languages have multiple runtime environments that vary
significantly in their implementation, for example [Python has many
implementations](https://wiki.python.org/moin/PythonImplementations). For
these languages, consider using specific `environment` prefixes to avoid
ambiguity, like `runtime.cpython.` and `runtime.pypy.`.
