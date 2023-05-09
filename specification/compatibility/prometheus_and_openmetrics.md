# Prometheus and OpenMetrics Compatibility

**Status**: [Experimental](../document-status.md)

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [Prometheus Metric points to OTLP](#prometheus-metric-points-to-otlp)
  * [Metric Metadata](#metric-metadata)
  * [Counters](#counters)
  * [Gauges](#gauges)
  * [Info](#info)
  * [StateSet](#stateset)
  * [Unknown-typed](#unknown-typed)
  * [Histograms](#histograms)
  * [Summaries](#summaries)
  * [Dropped Types](#dropped-types)
  * [Start Time](#start-time)
  * [Exemplars](#exemplars)
  * [Instrumentation Scope](#instrumentation-scope)
  * [Resource Attributes](#resource-attributes)
- [OTLP Metric points to Prometheus](#otlp-metric-points-to-prometheus)
  * [Metric Metadata](#metric-metadata-1)
  * [Instrumentation Scope](#instrumentation-scope-1)
  * [Gauges](#gauges-1)
  * [Sums](#sums)
  * [Histograms](#histograms-1)
  * [Exponential Histograms](#exponential-histograms)
  * [Summaries](#summaries-1)
  * [Metric Attributes](#metric-attributes)
  * [Exemplars](#exemplars-1)
  * [Resource Attributes](#resource-attributes-1)

<!-- tocstop -->

</details>

This section denotes how to convert metrics scraped in the
[Prometheus exposition](https://github.com/Prometheus/docs/blob/main/content/docs/instrumenting/exposition_formats.md#exposition-formats)
or [OpenMetrics](https://openmetrics.io/) formats to the OpenTelemetry metric
data model and how to create Prometheus metrics from
OpenTelemetry metric data. Since OpenMetrics has a superset of Prometheus' types, "Prometheus" is taken to mean "Prometheus or OpenMetrics".  "OpenMetrics" refers to OpenMetrics-only concepts.

## Prometheus Metric points to OTLP

### Metric Metadata

The [OpenMetrics MetricFamily Name](https://github.com/OpenObservability/OpenMetrics/blob/main/specification/OpenMetrics.md#metricfamily)
MUST be added as the Name of the OTLP metric after the removal of unit and type
suffixes described below.

The [OpenMetrics UNIT metadata](https://github.com/OpenObservability/OpenMetrics/blob/main/specification/OpenMetrics.md#metricfamily),
if present, MUST be converted to the unit of the OTLP metric.  After trimming
type-specific suffixes, such as `_total` for counters, the unit MUST be trimmed
from the suffix as well, if the metric suffix matches the unit. The unit SHOULD
be translated from Prometheus conventions to OpenTelemetry conventions by:

* Converting from full words to abbreviations (e.g. "milliseconds" to "ms").
* Special case: Converting "ratio" to "1".
* Converting "foo_per_bar" to "foo/bar".

The [OpenMetrics HELP metadata](https://github.com/OpenObservability/OpenMetrics/blob/main/specification/OpenMetrics.md#metricfamily),
if present, MUST be added as the description of the OTLP metric.

The [OpenMetrics TYPE metadata](https://github.com/OpenObservability/OpenMetrics/blob/main/specification/OpenMetrics.md#metricfamily),
if present, MUST be used to determine the OTLP data type, and dictates
type-specific conversion rules listed below. Metric families without type
metadata follow rules for [unknown-typed](#unknown-typed) metrics below.

### Counters

A [Prometheus Counter](https://github.com/OpenObservability/OpenMetrics/blob/main/specification/OpenMetrics.md#counter) MUST be converted to an OTLP Sum with `is_monotonic` equal to `true`.  If the counter has a `_total` suffix, it MUST be removed.

### Gauges

A [Prometheus Gauge](https://github.com/OpenObservability/OpenMetrics/blob/main/specification/OpenMetrics.md#gauge) MUST be converted to an OTLP Gauge.

### Info

An [OpenMetrics Info](https://github.com/OpenObservability/OpenMetrics/blob/main/specification/OpenMetrics.md#info) metric MUST be converted to an OTLP Non-Monotonic Sum unless it is the target_info metric, which is used to populate [resource attributes](#resource-attributes). An OpenMetrics Info can be thought of as a special-case of the OpenMetrics Gauge which has a value of 1, and whose labels generally stays constant over the life of the process. It is converted to a Non-Monotonic Sum, rather than a Gauge, because the value of 1 is intended to be viewed as a count, which should be summed together when aggregating away labels.  If it has an `_info` suffix, the suffix MUST be removed from the metric name.

### StateSet

An [OpenMetrics StateSet](https://github.com/OpenObservability/OpenMetrics/blob/main/specification/OpenMetrics.md#stateset) metric MUST be converted to an OTLP Non-Monotonic Sum. An OpenMetrics StateSet can be thought of as a special-case of the OpenMetrics Gauge which has a 0 or 1 value, and has one metric point for every possible state. It is converted to a Non-Monotonic Sum, rather than a Gauge, because the value of 1 is intended to be viewed as a count, which should be summed together when aggregating away labels.

### Unknown-typed

A [Prometheus Unknown](https://github.com/OpenObservability/OpenMetrics/blob/main/specification/OpenMetrics.md#unknown) MUST be converted to an OTLP Gauge.

### Histograms

A [Prometheus Histogram](https://github.com/OpenObservability/OpenMetrics/blob/main/specification/OpenMetrics.md#histogram) MUST be converted to an OTLP Histogram.

Multiple Prometheus histogram metrics MUST be merged together into a single OTLP Histogram:

* The `le` label on the `_bucket`-suffixed metric is used to identify and order histogram bucket boundaries. Each Prometheus line produces one bucket count on the resulting histogram. Each value for the `le` label except `+Inf` produces one bucket boundary.
* Lines with `_count` and `_sum` suffixes are used to determine the histogram's count and sum.
* If `_count` is not present, the metric MUST be dropped.
* If `_sum` is not present, the histogram's sum MUST be unset.

### Summaries

[Prometheus Summary](https://github.com/OpenObservability/OpenMetrics/blob/main/specification/OpenMetrics.md#summary) MUST be converted to an OTLP Summary.

Multiple Prometheus metrics are merged together into a single OTLP Summary:

* The `quantile` label on non-suffixed metrics is used to identify quantile points in summary metrics. Each Prometheus line produces one quantile on the resulting summary.
* Lines with `_count` and `_sum` suffixes are used to determine the summary's count and sum.
* If `_count` is not present, the metric MUST be dropped.
* If `_sum` is not present, the summary's sum MUST be [set to zero.](https://github.com/open-telemetry/opentelemetry-proto/blob/d8729d40f629dba12694b44c4c32c1eab109b00a/opentelemetry/proto/metrics/v1/metrics.proto#L601)

### Dropped Types

The following Prometheus types MUST be dropped:

* [OpenMetrics GaugeHistogram](https://github.com/OpenObservability/OpenMetrics/blob/main/specification/OpenMetrics.md#gaugehistogram)

### Start Time

Prometheus Cumulative metrics can include the start time using the [`_created` metric](https://github.com/OpenObservability/OpenMetrics/blob/main/specification/OpenMetrics.md#counter-1) as specified in OpenMetrics. When converting Prometheus Counters to OTLP, conversion SHOULD use `_created` where available. When no `_created` metric is available, conversion MUST follow [Cumulative streams: handling unknown start time](../metrics/data-model.md#cumulative-streams-handling-unknown-start-time) by default. Conversion MAY offer configuration, disabled by default, which allows using the `process_start_time_seconds` metric to provide the start time. Using `process_start_time_seconds` is only correct when all counters on the target start after the process and are not reset while the process is running.

### Exemplars

[OpenMetrics Exemplars](https://github.com/OpenObservability/OpenMetrics/blob/main/specification/OpenMetrics.md#exemplars)
can be attached to Prometheus Histogram bucket metric points and counter metric
points. Exemplars on histogram buckets SHOULD be converted to exemplars on
OpenTelemetry histograms. Exemplars on counter metric points SHOULD be
converted to exemplars on OpenTelemetry sums. If present, the timestamp
MUST be added to the OpenTelemetry exemplar. The Trace ID and Span ID SHOULD be
retrieved from the `trace_id` and `span_id` label keys, respectively.  All
labels not used for the trace and span ids MUST be added to the OpenTelemetry
exemplar as attributes.

### Instrumentation Scope

Each `otel_scope_info` metric point present in a batch of metrics
SHOULD be dropped from the incoming scrape, and converted to an instrumentation
scope. The `otel_scope_name` and `otel_scope_version` labels, if present, MUST
be converted to the Name and Version of the Instrumentation Scope. Additional
labels MUST be added as scope attributes, with keys and values unaltered. Other
metrics in the batch which have `otel_scope_name` and `otel_scope_version`
labels that match an instrumentation scope MUST be placed within the matching
instrumentation scope, and MUST remove those labels. For example, the
OpenMetrics metrics:

```
# TYPE otel_scope_info info
otel_scope_info{otel_scope_name="go.opentelemetry.io.contrib.instrumentation.net.http.otelhttp",otel_scope_version="v0.24.0",library_mascot="bear"} 1
# TYPE http_server_duration counter
http_server_duration{otel_scope_name="go.opentelemetry.io.contrib.instrumentation.net.http.otelhttp",otel_scope_version="v0.24.0"...} 1
```

becomes:

```yaml
# within a resource_metrics
scope_metrics:
  scope:
    name: go.opentelemetry.io.contrib.instrumentation.net.http.otelhttp
    version: v0.24.0
    attributes:
      library_mascot: bear
  metrics:
  - name: http_server_duration
    data:
      sum:
        data_points:
        - value: 1
```

Metrics which are not found to be associated with an instrumentation scope MUST
all be placed within an empty instrumentation scope, and MUST not have any labels
removed.

### Resource Attributes

When scraping a Prometheus endpoint, resource attributes MUST be added to the
scraped metrics to distinguish them from metrics from other Prometheus
endpoints. In particular, `service.name` and `service.instance.id`, are needed
to ensure Prometheus exporters can disambiguate metrics using
[`job` and `instance` labels](https://prometheus.io/docs/concepts/jobs_instances/#jobs-and-instances)
as [described below](#resource-attributes-1).

The following attributes MUST be associated with scraped metrics as resource
attributes, and MUST NOT be added as metric attributes:

| OTLP Resource Attribute | Description |
| ----------------------- | ----------- |
| `service.name` | The configured name of the service that the target belongs to |
| `service.instance.id` | A unique identifier of the target.  By default, it should be the `<host>:<port>` of the scraped URL |

The following attributes SHOULD be associated with scraped metrics as resource
attributes, and MUST NOT be added as metric attributes:

| OTLP Resource Attribute | Description |
| ----------------------- | ----------- |
| `server.address` | The `<host>` portion of the target's URL that was scraped |
| `server.port` | The `<port>` portion of the target's URL that was scraped |
| `url.scheme` | `http` or `https` |

In addition to the attributes above, the
[target_info](https://github.com/OpenObservability/OpenMetrics/blob/main/specification/OpenMetrics.md#supporting-target-metadata-in-both-push-based-and-pull-based-systems)
metric is used to supply additional resource attributes. If present,
target_info MUST be dropped from the batch of metrics, and all labels from
the target_info metric MUST be converted to resource attributes
attached to all other metrics which are part of the scrape. By default, label
keys and values MUST NOT be altered (such as replacing `_` with `.` characters
in keys).

## OTLP Metric points to Prometheus

### Metric Metadata

Prometheus SDK exporters MUST NOT allow duplicate UNIT, HELP, or TYPE
comments for the same metric name to be returned in a single scrape of the
Prometheus endpoint. Exporters MUST drop entire metrics to prevent conflicting
TYPE comments, but SHOULD NOT drop metric points as a result of conflicting
UNIT or HELP comments. Instead, all but one of the conflicting UNIT and HELP
comments (but not metric points) SHOULD be dropped. If dropping a comment or
metric points, the exporter SHOULD warn the user through error logging.

The Name of an OTLP metric MUST be added as the
[OpenMetrics MetricFamily Name](https://github.com/OpenObservability/OpenMetrics/blob/main/specification/OpenMetrics.md#metricfamily),
with unit and type suffixes added as described below. The metric name is
required to match the regex: `[a-zA-Z_:]([a-zA-Z0-9_:])*`. Invalid characters
in the metric name MUST be replaced with the `_` character. Multiple
consecutive `_` characters MUST be replaced with a single `_` character.

The Unit of an OTLP metric point SHOULD be converted to the equivalent unit in Prometheus when possible.  This includes:

* Converting from abbreviations to full words (e.g. "ms" to "milliseconds").
* Dropping the portions of the Unit within brackets (e.g. {packets}). Brackets MUST NOT be included in the resulting unit. A "count of foo" is considered unitless in Prometheus.
* Special case: Converting "1" to "ratio".
* Converting "foo/bar" to "foo_per_bar".

The resulting unit SHOULD be added to the metric as
[OpenMetrics UNIT metadata](https://github.com/OpenObservability/OpenMetrics/blob/main/specification/OpenMetrics.md#metricfamily)
and as a suffix to the metric name unless the metric name already contains the
unit, or the unit MUST be omitted. The unit suffix comes before any
type-specific suffixes.

The description of an OTLP metrics point MUST be added as
[OpenMetrics HELP metadata](https://github.com/OpenObservability/OpenMetrics/blob/main/specification/OpenMetrics.md#metricfamily).

The data point type of an OTLP metric MUST be added as
[OpenMetrics TYPE metadata](https://github.com/OpenObservability/OpenMetrics/blob/main/specification/OpenMetrics.md#metricfamily).
It also dictates type-specific conversion rules listed below.

### Instrumentation Scope

Prometheus exporters SHOULD generate an [Info](https://github.com/OpenObservability/OpenMetrics/blob/main/specification/OpenMetrics.md#info)-typed
metric named `otel_scope_info`. If present, Instrumentation Scope
`name` and `version` MUST be added as `otel_scope_name` and
`otel_scope_version` labels. Scope attributes MUST also be added as labels
following the rules described in the [`Metric Attributes`](#metric-attributes)
section below.

Prometheus exporters MUST add the scope name as the `otel_scope_name` label and
the scope version as the `otel_scope_version` label on all metric points by
default, based on the scope the original data point was nested in.

Prometheus exporters SHOULD provide a configuration option to disable the
`otel_scope_info` metric and `otel_scope_` labels.

### Gauges

An [OpenTelemetry Gauge](../metrics/data-model.md#gauge) MUST be converted to a Prometheus Gauge.

### Sums

[OpenTelemetry Sums](../metrics/data-model.md#sums) follows this logic:

- If the aggregation temporality is cumulative and the sum is monotonic, it MUST be converted to a Prometheus Counter.
- If the aggregation temporality is cumulative and the sum is non-monotonic, it MUST be converted to a Prometheus Gauge.
- If the aggregation temporality is delta and the sum is monotonic, it SHOULD be converted to a cumulative temporality and become a Prometheus Counter. The following behaviors are expected:
  - The new data point type must be the same as the accumulated data point type.
  - The new data point's start time must match the time of the accumulated data point. If not, see [detecting alignment issues](../metrics/data-model.md#sums-detecting-alignment-issues).
- Otherwise, it MUST be dropped.

Monotonic Sum metric points MUST have `_total` added as a suffix to the metric name.
Monotonic Sum metric points with `StartTimeUnixNano` should export the `{name}_created` metric as well.

### Histograms

An [OpenTelemetry Histogram](../metrics/data-model.md#histogram) with a cumulative aggregation temporality MUST be converted to a Prometheus metric family with the following metrics:

- A single `{name}_count` metric denoting the count field of the histogram. All attributes of the histogram point are converted to Prometheus labels.
- `{name}_sum` metric denoting the sum field of the histogram, reported only if the sum is positive and monotonic. The sum is positive and monotonic when all buckets are positive. All attributes of the histogram point are converted to Prometheus labels.
- A series of `{name}_bucket` metric points that contain all attributes of the histogram point recorded as labels.  Additionally, a label, denoted as `le` is added denoting the bucket boundary. The label's value is the stringified floating point value of bucket boundaries, ordered from lowest to highest. The value of each point is the sum of the count of all histogram buckets up the the boundary reported in the `le` label. These points will include a single exemplar that falls within `le` label and no other `le` labelled point.  The final bucket metric MUST have an `+Inf` threshold.
- Histograms with `StartTimeUnixNano` set should export the `{name}_created` metric as well.

OpenTelemetry Histograms with Delta aggregation temporality SHOULD be aggregated into a Cumulative aggregation temporality and follow the logic above, or MUST be dropped.

### Exponential Histograms

An [OpenTelemetry Exponential Histogram](../metrics/data-model.md#exponentialhistogram) with
a cumulative aggregation temporality MUST be converted to a Prometheus Native
Histogram as follows:

- `Scale` is converted to the Native Histogram `Schema`. Currently,
  [valid values](https://github.com/prometheus/prometheus/commit/d9d51c565c622cdc7d626d3e7569652bc28abe15#diff-bdaf80ebc5fa26365f45db53435b960ce623ea6f86747fb8870ad1abc355f64fR76-R83)
  for `schema` are -4 <= n <= 8.
  If `Scale` is > 8 then Exponential Histogram data points SHOULD be downscaled
  to a scale accepted by Prometheus (in range [-4,8]). Any data point unable to
  be rescaled to an acceptable range MUST be dropped.
- `Count` is converted to Native Histogram `Count` if the `NoRecordedValue`
  flag is set to `false`, otherwise, Native Histogram `Count` is set to the
  Stale NaN value.
- `Sum` is converted to the Native Histogram `Sum` if `Sum` is set and the
  `NoRecordedValue` flag is set to `false`, otherwise, Native Histogram `Sum` is
  set to the Stale NaN value.
- `TimeUnixNano` is converted to the Native Histogram `Timestamp` after
  converting nanoseconds to milliseconds.
- `ZeroCount` is converted directly to the Native Histogram `ZeroCount`.
- `ZeroThreshold`, if set, is converted to the Native Histogram `ZeroThreshold`.
  Otherwise, it is set to the default value `1e-128`.
- The dense bucket layout represented by `Positive` bucket counts and `Offset` is
  converted to the Native Histogram sparse layout represented by `PositiveSpans`
  and `PositiveDeltas`. The same holds for the `Negative` bucket counts
  and `Offset`. Note that Prometheus Native Histograms buckets are indexed by
  upper boundary while Exponential Histograms are indexed by lower boundary, the
  result being that the Offset fields are different-by-one.
- `Min` and `Max` are not used.
- `StartTimeUnixNano` is not used.

[OpenTelemetry Exponential Histogram](../metrics/data-model.md#exponentialhistogram)
metrics with the delta aggregation temporality are dropped.

### Summaries

An [OpenTelemetry Summary](../metrics/data-model.md#summary-legacy) MUST be converted to a Prometheus metric family with the following metrics:

- A single `{name}_count` metric denoting the count field of the summary.
  All attributes of the summary point are converted to Prometheus labels.
- `{name}_sum` metric denoting the sum field of the summary, reported
  only if the sum is positive and monotonic. All attributes of the summary
  point are converted to Prometheus labels.
- A series of `{name}` metric points that contain all attributes of the
  summary point recorded as labels.  Additionally, a label, denoted as
  `quantile` is added denoting a reported quantile point, and having its value
  be the stringified floating point value of quantiles (between 0.0 and 1.0),
  starting from lowest to highest, and all being non-negative.  The value of
  each point is the computed value of the quantile point.
- Summaries with `StartTimeUnixNano` set should export the `{name}_created` metric as well.

### Metric Attributes

OpenTelemetry Metric Attributes MUST be converted to
[Prometheus labels](https://prometheus.io/docs/concepts/data_model/#metric-names-and-labels).
String Attribute values are converted directly to Metric Attributes, and
non-string Attribute values MUST be converted to string attributes following
the [attribute specification](../common/README.md#attribute).  Prometheus
metric label keys are required to match the following regex:
`[a-zA-Z_]([a-zA-Z0-9_])*`.  Metrics from OpenTelemetry with unsupported
Attribute names MUST replace invalid characters with the `_` character.
Multiple consecutive `_` characters MUST be replaced with a single `_`
character. This may cause ambiguity in scenarios where multiple similar-named
attributes share invalid characters at the same location.  In such unlikely
cases, if multiple key-value pairs are converted to have the same Prometheus
key, the values MUST be concatenated together, separated by `;`, and ordered by
the lexicographical order of the original keys.

### Exemplars

[Exemplars](../metrics/data-model.md#exemplars) on OpenTelemetry Histograms and Monotonic Sums SHOULD
be converted to OpenMetrics exemplars. Exemplars on other OpenTelemetry data
points MUST be dropped. For Prometheus push exporters, multiple exemplars are
able to be added to each bucket, so all exemplars SHOULD be converted. For
Prometheus pull endpoints, only a single exemplar is able to be added to each
bucket, so the largest exemplar from each bucket MUST be used, if attaching
exemplars. If no exemplars exist on a bucket, the highest exemplar from a lower
bucket MUST be used, even though it is a duplicate of another bucket's exemplar.
OpenMetrics Exemplars MUST use the `trace_id` and `span_id` keys for the trace
and span IDs, respectively. Timestamps MUST be added as timestamps on the
OpenMetrics exemplar, and `filtered_attributes` MUST be added as labels on the
OpenMetrics exemplar unless they would exceed the OpenMetrics
[limit on characters](https://github.com/OpenObservability/OpenMetrics/blob/main/specification/OpenMetrics.md#exemplars).

### Resource Attributes

In SDK Prometheus (pull) exporters, resource attributes SHOULD be converted to a single [`target_info` metric](https://github.com/OpenObservability/OpenMetrics/blob/main/specification/OpenMetrics.md#supporting-target-metadata-in-both-push-based-and-pull-based-systems); otherwise, they MUST be dropped, and MUST NOT be attached as labels to other metric families. The target_info metric MUST be an info-typed metric  whose labels MUST include the resource attributes, and MUST NOT include any other labels. There MUST be at most one target_info metric exposed on an SDK Prometheus endpoint.

In the Collector's Prometheus pull and push (remote-write) exporters, it is
possible for metrics from multiple targets to be sent together, so targets must
be disambiguated from one another. However, the Prometheus exposition format
and [remote-write](https://github.com/Prometheus/Prometheus/blob/main/prompb/remote.proto)
formats do not include a notion of resource, and expect metric labels to
distinguish scraped targets. By convention, [`job` and `instance`](https://prometheus.io/docs/concepts/jobs_instances/#jobs-and-instances)
labels distinguish targets and are expected to be present on metrics exposed on
a Prometheus pull exporter (a ["federated"](https://prometheus.io/docs/prometheus/latest/federation/)
Prometheus endpoint) or pushed via Prometheus remote-write. In OTLP, the
`service.name`, `service.namespace`, and `service.instance.id` triplet is
[required to be unique](../resource/semantic_conventions/README.md#service),
which makes them good candidates to use to construct `job` and `instance`. In
the collector Prometheus exporters, the `service.name` and `service.namespace`
attributes MUST be combined as `<service.namespace>/<service.name>`, or
`<service.name>` if namespace is empty, to form the `job` metric label.  The
`service.instance.id` attribute, if present, MUST be converted to the
`instance` label; otherwise, `instance` should be added with an empty value.
Other resource attributes SHOULD be converted to a
[target_info](https://github.com/OpenObservability/OpenMetrics/blob/main/specification/OpenMetrics.md#supporting-target-metadata-in-both-push-based-and-pull-based-systems)
metric, or MUST be dropped. The target_info metric is an info-typed metric
whose labels MUST include the resource attributes, and MUST NOT include any
other labels other than `job` and `instance`.  There MUST be at most one
target_info metric exported for each unique combination of `job` and `instance`.

If info-typed metric families are not yet supported by the language Prometheus client library, a gauge-typed metric family named target_info with a constant value of 1 MUST be used instead.

To convert OTLP resource attributes to Prometheus labels, string Attribute values are converted directly to labels, and non-string Attribute values MUST be converted to string attributes following the [attribute specification](../common/README.md#attribute).
