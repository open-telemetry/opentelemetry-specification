# Metrics Semantic Conventions

**Status**: [Experimental](../../document-status.md)

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [General Guidelines](#general-guidelines)
  * [Units](#units)
  * [Pluralization](#pluralization)
- [General Metric Semantic Conventions](#general-metric-semantic-conventions)
  * [Instrument Naming](#instrument-naming)
  * [Instrument Units](#instrument-units)

<!-- tocstop -->

The following semantic conventions surrounding metrics are defined:

* [HTTP Metrics](http-metrics.md): Semantic conventions and instruments for HTTP metrics.
* [System Metrics](system-metrics.md): Semantic conventions and instruments for standard system metrics.
* [Process Metrics](process-metrics.md): Semantic conventions and instruments for standard process metrics.
* [Runtime Environment Metrics](runtime-environment-metrics.md): Semantic conventions and instruments for runtime environment metrics.

Apart from semantic conventions for metrics and
[traces](../../trace/semantic_conventions/README.md), OpenTelemetry also
defines the concept of overarching [Resources](../../resource/sdk.md) with
their own [Resource Semantic
Conventions](../../resource/semantic_conventions/README.md).

## General Guidelines

Metric names and labels exist within a single universe and a single
hierarchy. Metric names and labels MUST be considered within the universe of
all existing metric names. When defining new metric names and labels,
consider the prior art of existing standard metrics and metrics from
frameworks/libraries.

Associated metrics SHOULD be nested together in a hierarchy based on their
usage. Define a top-level hierarchy for common metric categories: for OS
metrics, like CPU and network; for app runtimes, like GC internals. Libraries
and frameworks should nest their metrics into a hierarchy as well. This aids
in discovery and adhoc comparison. This allows a user to find similar metrics
given a certain metric.

The hierarchical structure of metrics defines the namespacing. Supporting
OpenTelemetry artifacts define the metric structures and hierarchies for some
categories of metrics, and these can assist decisions when creating future
metrics.

Common labels SHOULD be consistently named. This aids in discoverability and
disambiguates similar labels to metric names.

["As a rule of thumb, **aggregations** over all the dimensions of a given
metric **SHOULD** be
meaningful,"](https://prometheus.io/docs/practices/naming/#metric-names) as
Prometheus recommends.

Semantic ambiguity SHOULD be avoided. Use prefixed metric names in cases
where similar metrics have significantly different implementations across the
breadth of all existing metrics. For example, every garbage collected runtime
has slightly different strategies and measures. Using a single set of metric
names for GC, not divided by the runtime, could create dissimilar comparisons
and confusion for end users. (For example, prefer `runtime.java.gc*` over
`runtime.gc.*`.) Measures of many operating system metrics are similarly
ambiguous.

### Units

Conventional metrics or metrics that have their units included in
OpenTelemetry metadata (e.g. `metric.WithUnit` in Go) SHOULD NOT include the
units in the metric name. Units may be included when it provides additional
meaning to the metric name. Metrics MUST, above all, be understandable and
usable.

When building components that interoperate between OpenTelemetry and a system
using the OpenMetrics exposition format, use the
[OpenMetrics Guidelines](./openmetrics-guidelines.md).

### Pluralization

Metric names SHOULD NOT be pluralized, unless the value being recorded
represents discrete instances of a
[countable quantity](https://en.wikipedia.org/wiki/Count_noun).
Generally, the name SHOULD be pluralized only if the unit of the metric in
question is a non-unit (like `{faults}` or `{operations}`).

Examples:

* `system.filesystem.utilization`, `http.server.duration`, and `system.cpu.time`
should not be pluralized, even if many data points are recorded.
* `system.paging.faults`, `system.disk.operations`, and `system.network.packets`
should be pluralized, even if only a single data point is recorded.

## General Metric Semantic Conventions

The following semantic conventions aim to keep naming consistent. They
provide guidelines for most of the cases in this specification and should be
followed for other instruments not explicitly defined in this document.

### Instrument Naming

- **limit** - an instrument that measures the constant, known total amount of
something should be called `entity.limit`. For example, `system.memory.limit`
for the total amount of memory on a system.

- **usage** - an instrument that measures an amount used out of a known total
(**limit**) amount should be called `entity.usage`. For example,
`system.memory.usage` with label `state = used | cached | free | ...` for the
amount of memory in a each state. Where appropriate, the sum of **usage**
over all label values SHOULD be equal to the **limit**.

  A measure of the amount of an unlimited resource consumed is differentiated
  from **usage**.

- **utilization** - an instrument that measures the *fraction* of **usage**
out of its **limit** should be called `entity.utilization`. For example,
`system.memory.utilization` for the fraction of memory in use. Utilization
values are in the range `[0, 1]`.

- **time** - an instrument that measures passage of time should be called
`entity.time`. For example, `system.cpu.time` with label `state = idle | user
| system | ...`. **time** measurements are not necessarily wall time and can
be less than or greater than the real wall time between measurements.

  **time** instruments are a special case of **usage** metrics, where the
  **limit** can usually be calculated as the sum of **time** over all label
  values. **utilization** for time instruments can be derived automatically
  using metric event timestamps. For example, `system.cpu.utilization` is
  defined as the difference in `system.cpu.time` measurements divided by the
  elapsed time.

- **io** - an instrument that measures bidirectional data flow should be
called `entity.io` and have labels for direction. For example,
`system.network.io`.

- Other instruments that do not fit the above descriptions may be named more
freely. For example, `system.paging.faults` and `system.network.packets`.
Units do not need to be specified in the names since they are included during
instrument creation, but can be added if there is ambiguity.

### Instrument Units

Units should follow the [UCUM](http://unitsofmeasure.org/ucum.html) (need
more clarification in
[#705](https://github.com/open-telemetry/opentelemetry-specification/issues/705)).

- Instruments for **utilization** metrics (that measure the fraction out of a
total) are dimensionless and SHOULD use the default unit `1` (the unity).
- Instruments that measure an integer count of something SHOULD use the
default unit `1` (the unity) and
[annotations](https://ucum.org/ucum.html#para-curly) with curly braces to
give additional meaning. For example `{packets}`, `{errors}`, `{faults}`,
etc.
