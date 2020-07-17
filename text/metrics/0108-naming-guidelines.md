# Metric instrument naming guidelines

## Purpose

Names and labels for metric instruments are primarily how humans interact with metric data -- users rely on these names to build dashboards and perform analysis. The names and hierarchical structure need to be understandable and discoverable during routine exploration -- and this becomes critical during incidents.

To ensure these goals and consistency in future metric naming standards, this outlines a meta-standard for these names.

## Guidelines

Metric names and labels exist within a single universe and a single hierarchy. Metric names and labels MUST be considered within the universe of all existing metric names. When defining new metric names and labels, consider the prior art of existing standard metrics and metrics from frameworks/libraries.

Associated metrics SHOULD be nested together in a hierarchy based on their usage. Define a top-level hierarchy for common metric categories: for OS metrics, like CPU and network; for app runtimes, like GC internals. Libraries and frameworks should nest their metrics into a hierarchy as well. This aids in discovery and adhoc comparison. This allows a user to find similar metrics given a certain metric.

The hierarchical structure of metrics defines the namespacing. Supporting OpenTelemetry artifacts define the metric structures and hierarchies for some categories of metrics, and these can assist decisions when creating future metrics.

Common labels SHOULD be consistently named. This aids in discoverability and disambiguates similar labels to metric names.

["As a rule of thumb, **aggregations** over all the dimensions of a given metric **SHOULD** be meaningful,"](https://prometheus.io/docs/practices/naming/#metric-names) as Prometheus recommends.

Semantic ambiguity SHOULD be avoided. Use prefixed metric names in cases where similar metrics have significantly different implementations across the breadth of all existing metrics. For example, every garbage collected runtime has slightly different strategies and measures. Using a single set of metric names for GC, not divided by the runtime, could create dissimilar comparisons and confusion for end users. (For example, prefer `runtime.java.gc*` over `runtime.gc.*`.) Measures of many operating system metrics are similar.

For conventional metrics or metrics that have their units included in OpenTelemetry metadata (eg `metric.WithUnit` in Go), SHOULD NOT include the units in the metric name. Units may be included when it provides additional meaning to the metric name. Metrics MUST, above all, be understandable and usable.
