<!--- Hugo front matter used to generate the website version of this page:
linkTitle: Prometheus and OpenMetrics
aliases:
  - /docs/reference/specification/compatibility/openmetrics
  - /docs/specs/otel/compatibility/openmetrics
--->

# Prometheus and OpenMetrics Compatibility

**Status**: [Mixed](../document-status.md)

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [Differences between Prometheus formats](#differences-between-prometheus-formats)
- [Prometheus Metric points to OTLP](#prometheus-metric-points-to-otlp)
  * [Metric Metadata](#metric-metadata)
  * [Timestamps](#timestamps)
  * [Counters](#counters)
  * [Gauges](#gauges)
  * [Info](#info)
  * [StateSet](#stateset)
  * [Unknown-typed](#unknown-typed)
  * [Histograms](#histograms)
  * [Native Histograms](#native-histograms)
  * [Summaries](#summaries)
  * [Dropped Types](#dropped-types)
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
  * [Exemplar Conversion](#exemplar-conversion)
  * [Resource Attributes](#resource-attributes-1)

<!-- tocstop -->

</details>

## Differences between Prometheus formats

This document covers OpenTelemetry compatibility with various Prometheus-related formats, including:

Formats used for Scraping metrics (pull):

* [Prometheus text exposition format](https://github.com/prometheus/docs/blob/main/docs/instrumenting/exposition_formats.md)
* [Prometheus protobuf format](https://github.com/prometheus/client_model/blob/01ca24cafc7877ed5ce091083068cde086b7c3dc/io/prometheus/client/metrics.proto)
* [OpenMetrics text format](https://github.com/prometheus/OpenMetrics/blob/1386544931307dff279688f332890c31b6c5de36/specification/OpenMetrics.md#text-format)
* (Not yet supported by Prometheus) [OpenMetrics protobuf format](https://github.com/prometheus/OpenMetrics/blob/1386544931307dff279688f332890c31b6c5de36/specification/OpenMetrics.md#protobuf-format)

Formats used for Pushing metrics:

* [Prometheus Remote Write format](https://github.com/prometheus/prometheus/blob/main/prompb/remote.proto)

The document below uses "Prometheus" to refer to the union of all of these
formats, even though support for particular features may be missing from the
specific format. To avoid duplicating the specification for each format, this
document will include requirements which may not be feasible to implement in
all Prometheus formats. The following features are not consistently supported
at the time of writing:

* Exemplars are not currently supported in the Prometheus text exposition format.
  * Exemplars MUST be dropped if they are not supported.
* Info and StateSet-typed metrics are not currently supported by the Prometheus text exposition format or Prometheus protobuf format.
  * If the specification below requires producing a Prometheus Info-typed metric, a Prometheus Gauge with an additional `_info` name suffix MUST be produced if Info-typed metrics are not supported.
  * If the specification below requires producing a Prometheus StateSet-typed metric, a Prometheus Gauge MUST be produced instead if StateSet-typed metrics are not supported.
* Exponential (Native) Histograms are not currently supported in the Prometheus text exposition format or the OpenMetrics text or proto formats.
  * Exponential (Native) Histograms SHOULD be dropped if they are not supported, or MAY be converted to fixed-bucket histograms.

## Prometheus Metric points to OTLP

**Status**: [Development](../document-status.md)

### Metric Metadata

**Status**: [Stable](../document-status.md)

The [Prometheus Metric Name](https://prometheus.io/docs/instrumenting/exposition_formats/#comments-help-text-and-type-information)
MUST be added as the Name of the OTLP metric. The name SHOULD NOT be altered.

[Prometheus UNIT metadata](https://github.com/prometheus/OpenMetrics/blob/v1.0.0/specification/OpenMetrics.md#metricfamily),
if present, MUST be converted to the unit of the OTLP metric. The unit MUST
be translated from words to the UCUM abbreviation if it is in the following set
of commonly-used units:

| Prometheus Unit | UCUM Abbreviation |
| :--- | :--- |
| `days` | `d` |
| `hours` | `h` |
| `minutes` | `min` |
| `seconds` | `s` |
| `milliseconds` | `ms` |
| `microseconds` | `us` |
| `nanoseconds` | `ns` |
| `bytes` | `By` |
| `kibibytes` | `KiBy` |
| `mebibytes` | `MiBy` |
| `gibibytes` | `GiBy` |
| `tebibytes` | `TiBy` |
| `kilobytes` | `kBy` |
| `megabytes` | `MBy` |
| `gigabytes` | `GBy` |
| `terabytes` | `TBy` |
| `meters` | `m` |
| `volts` | `V` |
| `amperes` | `A` |
| `joules` | `J` |
| `watts` | `W` |
| `grams` | `g` |
| `celsius` | `Cel` |
| `hertz` | `Hz` |
| `percent` | `%` |

[Prometheus HELP metadata](https://prometheus.io/docs/instrumenting/exposition_formats/#comments-help-text-and-type-information),
if present, MUST be added as the description of the OTLP metric.

[Prometheus TYPE metadata](https://prometheus.io/docs/instrumenting/exposition_formats/#comments-help-text-and-type-information),
if present, MUST be used to determine the OTLP data type, and dictates
type-specific conversion rules listed below. Metric families without type
metadata follow rules for [unknown-typed](#unknown-typed) metrics below.
The TYPE metadata MUST also be added to the OTLP [metric.metadata][metricMetadata]
under the `prometheus.type` key (e.g. `prometheus.type="unknown"`).

### Timestamps

**Status**: [Stable](../document-status.md)

If present, the Prometheus Metric Sample's Start timestamp (also referred to as the Created timestamp) MUST be converted to the Start timestamp of the OTLP data point. If no start timestamp is present, the start time of the OTLP data point SHOULD be left unset.

If present, the Prometheus Metric Sample's Timestamp MUST be converted to the Timestamp of the OTLP data point. For metrics scraped from a Prometheus endpoint without an explicit timestamp, the timestamp of the OTLP data point MUST be set to the time of the scrape.

### Counters

**Status**: [Stable](../document-status.md)

A [Prometheus Counter](https://prometheus.io/docs/instrumenting/exposition_formats/#basic-info) MUST be converted to an OTLP Sum with `is_monotonic` equal to `true`.

Exemplars on the Prometheus Counter Sample MUST be converted to OpenTelemetry
Exemplars on the OpenTelemetry Sum data point following the rules in
[Exemplars](#exemplars).

### Gauges

**Status**: [Stable](../document-status.md)

A [Prometheus Gauge](https://prometheus.io/docs/instrumenting/exposition_formats/#basic-info) MUST be converted to an OTLP Gauge.

### Info

**Status**: [Development](../document-status.md)

A [Prometheus Info](https://github.com/prometheus/OpenMetrics/blob/v1.0.0/specification/OpenMetrics.md#info) metric MUST be converted to an OTLP Non-Monotonic Sum unless it is the `target` info metric, which is used to populate [resource attributes](#resource-attributes). A Prometheus Info metric can be thought of as a special-case of the Prometheus Gauge metric which has a value of 1, and whose labels generally stays constant over the life of the process. It is converted to a OTLP Non-Monotonic Sum, rather than an OTLP Gauge, because the value of 1 is intended to be viewed as a count, which should be summed together when aggregating away labels.

### StateSet

**Status**: [Development](../document-status.md)

A [Prometheus StateSet](https://github.com/prometheus/OpenMetrics/blob/v1.0.0/specification/OpenMetrics.md#stateset) metric MUST be converted to an OTLP Non-Monotonic Sum. A Prometheus StateSet metric can be thought of as a special-case of the Prometheus Gauge which has a 0 or 1 value, and has one metric point for every possible state. It is converted to an OTLP Non-Monotonic Sum, rather than an OTLP Gauge, because the value of 1 is intended to be viewed as a count, which should be summed together when aggregating away labels.

### Unknown-typed

**Status**: [Development](../document-status.md)

A [Prometheus Unknown](https://prometheus.io/docs/instrumenting/exposition_formats/#basic-info) MUST be converted to an OTLP Gauge.

### Histograms

**Status**: [Stable](../document-status.md)

A [Prometheus Histogram](https://github.com/prometheus/OpenMetrics/blob/v1.0.0/specification/OpenMetrics.md#histogram) MUST be converted to an [OTLP Histogram](https://opentelemetry.io/docs/specs/otel/metrics/data-model/#histogram).

Prometheus bucket boundaries become OTLP explicit bounds, except the +Inf boundary which is dropped. The sample values associated with the Prometheus bucket boundaries become OTLP bucket counts, including the value associated with the +Inf boundary. The Prometheus Histogram Count becomes the OTLP Histogram Count and Prometheus Histogram Sum becomes OTLP Histogram Sum.

In the text format, Prometheus histograms buckets, count and sum are sent as separate samples and they MUST be merged together when forming an OTLP Histogram. Samples with a `_bucket` suffix will have an `le` label denoting the bucket boundary, whose value is the total count of observations less than the bucket boundary. The count of the OpenTelemetry bucket is computed as the difference between the bucket and the next-lowest bucket, if it exists. Lines with `_count` and `_sum` suffixes are used to determine the histogram's count and sum.

* If `_count` is not present, the metric MUST be dropped.
* If `_sum` is not present, the histogram's sum MUST be unset.

Exemplars on the Prometheus Histogram Sample MUST be converted to OpenTelemetry
Exemplars on the OpenTelemetry Histogram data point following the rules in
[Exemplars](#exemplars).

### Native Histograms

**Status**: [Stable](../document-status.md)

A [Prometheus Native Histogram](https://prometheus.io/docs/specs/native_histograms/)
with standard (exponential) schema (i.e. schemas -4 to 8) and which are
of the integer and counter [flavor](https://prometheus.io/docs/specs/native_histograms/#flavors)
MUST be converted to an OTLP Exponential Histogram as follows:

- If the Native Histogram `ResetHint` (or `CounterResetHint`) indicates gauge
  type, the native histogram is dropped. Otherwise this field is ignored.
- `Schema` is converted to the Exponential Histogram `Scale`.
- The `NoRecordedValue` flag is set to `true` if the `Sum` is equal to the
  [Stale NaN value](https://github.com/prometheus/prometheus/blob/main/model/value/value.go).
  Otherwise,
  - `Count` is made equal to the sum of all valid bucket counts by adding up
    - the `ZeroCount`,
    - the bucket counts from the sparse bucket layout described below, except
      for overflow buckets.
  - `Sum` is converted to the Exponential Histogram `Sum`. Note that the `Sum`
    may be `NaN` in case the Native Histogram observed the value `NaN` or both
    `-Inf` and `+Inf`. The `Sum` may also be `-Inf` or `+Inf`.
- `Timestamp` is converted to the Exponential Histogram `TimeUnixNano` after
  converting milliseconds to nanoseconds.
- `ZeroCount` is converted directly to the Exponential Histogram `ZeroCount`.
- `ZeroThreshold`, is converted to the Exponential Histogram `ZeroThreshold`.
- The [sparse bucket layout](https://prometheus.io/docs/specs/native_histograms/#buckets)
  represented by `PositiveSpans` and `PositiveDeltas` is converted to the
  Exponential Histogram dense layout represented by `Positive` bucket counts and
  `Offset`.

  - The `PositiveDeltas` are delta encoded bucket counts, where the first value
    is an absolute bucket count and each subsequent value is a delta to the
    previous value.
  - The Exponential Histogram `Positive` `Offset` is set to the first
    `PositiveSpan`'s `Offset` minus 1 (`PositiveSpans[0].Offset-1`) if there
    are spans, otherwise left at 0. The minus one is because Prometheus Native
    histogram buckets are indexed by their upper boundary while Exponential
    Histograms are indexed by their lower boundary.
  - The `PositiveSpans` encode the index into the `Positive` bucket counts for
    each value in the `PositiveDeltas`. The index starts from 0 for the first
    span, for subsequent spans the span's `Offset` is added to the previous
    index. The span's `Length` indicates the number of continuous indexes to
    use.
  - The Native Histogram may contain overflow buckets. If converted to
    an Exponential Histogram bucket, the overflow bucket would map to values
    outside the IEEE float range. Overflow buckets MUST be dropped and not
    counted in the overall `Count`.

- The `NegativeSpans` and `NegativeDeltas` are converted the same way as the
  positive buckets.
- `Min` and `Max` are not set.
- `StartTimeUnixNano` is set to the `Start Timestamp` timestamp, if available.
- `AggregationTemporality` is set to `cumulative`.

A Native histogram with custom buckets (NHCB) schema (i.e. schema -53) and which
are of the integer and counter [flavor](https://prometheus.io/docs/specs/native_histograms/#flavors)
MUST be converted to an OTLP Histogram as follows:

- If the Native Histogram `ResetHint` (or `CounterResetHint`) indicates gauge
  type, the native histogram is dropped. Otherwise this field is ignored.
- The `NoRecordedValue` flag is set to `true` if the `Sum` is equal to the
  [Stale NaN value](https://github.com/prometheus/prometheus/blob/main/model/value/value.go).
  Otherwise,
  - `Count` is converted to Histogram `Count`. Note that the `Count`
    is equal to the sum of all bucket counts.
  - `Sum` is converted to the Histogram `Sum`. Note that the `Sum`
    may be `NaN` in case the Native Histogram observed the value `NaN` or both
    `-Inf` and `+Inf`. The `Sum` may also be `-Inf` or `+Inf`.
- `Timestamp` is converted to the Histogram `TimeUnixNano` after
  converting milliseconds to nanoseconds.
- `Min` and `Max` are not set.
- [`CustomValues`](https://prometheus.io/docs/specs/native_histograms/#custom-values)
  is converted to bucket boundaries. The `+Inf` bucket is implicit, therefore
  `N` `CustomValues` represent `N+1` Histogram bucket counts.
- The [sparse bucket layout](https://prometheus.io/docs/specs/native_histograms/#buckets)
  represented by `PositiveSpans` and `PositiveDeltas` is converted to
  Histogram bucket counts.

  - The `PositiveDeltas` are delta encoded bucket counts, where the first value
    is an absolute bucket count and each subsequent value is a delta to the
    previous value.
  - The `PositiveSpans` encode the index into the bucket counts for each value
    in the `PositiveDeltas`. The index starts from the `Offset` in the first
    span and for subsequent spans the span's `Offset` is added to the previous
    index. The span's `Length` indicates the number of continuous indexes to
    use.

- `StartTimeUnixNano` is set to the `Start Timestamp`, if available.
- `AggregationTemporality` is set to `cumulative`.

Native histograms of the float or gauge flavors MUST be dropped.

Native Histograms with `Schema` outside of the range [-4, 8] and not equal to
-53 MUST be dropped.

Exemplars on the Prometheus Native Histogram Sample MUST be converted to
OpenTelemetry Exemplars on the OpenTelemetry Exponential Histogram data point
following the rules in [Exemplars](#exemplars).

### Summaries

**Status**: [Stable](../document-status.md)

[Prometheus Summary](https://prometheus.io/docs/instrumenting/exposition_formats/#basic-info) MUST be converted to an [OTLP Summary](https://opentelemetry.io/docs/specs/otel/metrics/data-model/#summary-legacy).

Prometheus Summary Quantiles become OTLP Summary Quantiles. Prometheus Summary Count becomes OTLP Summary Count and Prometheus Summary Sum becomes OTLP Summary Sum.

In the text format, samples without suffixes have the `quantile` label to identify the quantile points of the Prometheus Summary. Extra samples with the same metric name but with the suffixes `_count` and `_sum` are used to identify the Prometheus Summary Count and Sum respectively.

In text formats where Prometheus Summaries are represented by multiple samples, samples with same [metric family](https://github.com/prometheus/OpenMetrics/blob/main/specification/OpenMetrics.md#metricfamily) name MUST be merged together into a single OTLP Summary.

* If `_count` is not present, the metric MUST be dropped.
* If `_sum` is not present, the summary's sum MUST be [set to zero.](https://github.com/open-telemetry/opentelemetry-proto/blob/d8729d40f629dba12694b44c4c32c1eab109b00a/opentelemetry/proto/metrics/v1/metrics.proto#L601)

### Dropped Types

**Status**: [Stable](../document-status.md)

The following Prometheus types MUST be dropped:

* [Prometheus GaugeHistogram](https://github.com/prometheus/OpenMetrics/blob/v1.0.0/specification/OpenMetrics.md#gaugehistogram)
* [Prometheus Native GaugeHistogram](https://prometheus.io/docs/specs/native_histograms/#gauge-histograms-vs-counter-histograms)

### Exemplars

**Status**: [Stable](../document-status.md)

[Prometheus Exemplars](https://github.com/prometheus/OpenMetrics/blob/v1.0.0/specification/OpenMetrics.md#exemplars)
MUST be converted to OpenTelemetry Exemplars as follows:

* If present, the timestamp MUST be used as the OpenTelemetry exemplar's
  timestamp.
* If present, and if the values are valid Trace and Span IDs, the `trace_id` and
  `span_id` labels MUST be converted to the OpenTelemetry Exemplar's Trace ID and
  Span ID, respectively.
* All labels other than `trace_id` and `span_id` MUST be added to the OpenTelemetry
  exemplar as filtered attributes.

### Instrumentation Scope

**Status**: [Stable](../document-status.md)

Labels with `otel_scope_` prefix MUST be dropped from all metric points
and used as the Instrumentation Scope name (`otel_scope_name`),
version (`otel_scope_version`), schema URL (`otel_scope_schema_url`),
attributes (`otel_scope_[attribute]`).

```
# TYPE http_server_duration counter
http_server_duration{otel_scope_name="go.opentelemetry.io.contrib.instrumentation.net.http.otelhttp",otel_scope_schema_url="https://opentelemetry.io/schemas/1.31.0",otel_scope_version="v0.24.0",otel_scope_library_mascot="gopher"...} 1
```

becomes:

```yaml
# within a resource_metrics
scope_metrics:
  scope:
    name: go.opentelemetry.io.contrib.instrumentation.net.http.otelhttp
    version: v0.24.0
    attributes:
      library_mascot: gopher
  schema_url: https://opentelemetry.io/schemas/1.31.0 
  metrics:
  - name: http_server_duration
    data:
      sum:
        data_points:
        - value: 1
```

Metrics which do not have any label with `otel_scope_` prefix
MUST be assigned an instrumentation scope identifying the entity performing
the translation from Prometheus to OpenTelemetry (e.g. the collector's
Prometheus receiver).

### Resource Attributes

**Status**: [Development](../document-status.md)

When scraping a Prometheus endpoint, resource attributes MUST be added to the
scraped metrics to distinguish them from metrics from other Prometheus
endpoints. In particular, `service.name` and `service.instance.id`, are needed
to ensure Prometheus exporters can disambiguate metrics using
[`job` and `instance` labels](https://prometheus.io/docs/concepts/jobs_instances/)
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
[target](https://github.com/prometheus/OpenMetrics/blob/v1.0.0/specification/OpenMetrics.md#supporting-target-metadata-in-both-push-based-and-pull-based-systems)
 info metric is used to supply additional resource attributes. If present,
the `target` info metric MUST be dropped from the batch of metrics, and all labels from
the `target` info metric MUST be converted to resource attributes
attached to all other metrics which are part of the scrape. By default, label
keys and values MUST NOT be altered (such as replacing `_` with `.` characters
in keys).

## OTLP Metric points to Prometheus

### Metric Metadata

**Status**: [Stable](../document-status.md)

Prometheus Pull exporters for OpenTelemetry metric data MUST NOT allow duplicate
UNIT, HELP, or TYPE comments for the same metric name to be returned in a single
scrape of the Prometheus endpoint. Exporters MUST drop entire metrics to prevent
conflicting TYPE comments, but SHOULD NOT drop metric points as a result of
conflicting UNIT or HELP comments. Instead, all but one of the conflicting UNIT
and HELP comments (but not metric points) SHOULD be dropped. If dropping a
comment or metric points, the exporter SHOULD warn the user through error
logging. Note that SDKs are required to [warn the user over duplicate instrument
registration, indicative of the same problem](https://opentelemetry.io/docs/specs/otel/metrics/sdk/#duplicate-instrument-registration).

The Name of an OTLP metric MUST be added as the
[Prometheus Metric Name](https://prometheus.io/docs/instrumenting/exposition_formats/#comments-help-text-and-type-information).
Prometheus naming conventions encourage metric names to match the regular
expression: `[a-zA-Z_:]([a-zA-Z0-9_:])*`. Discouraged characters in the metric
name SHOULD be replaced with the `_` character by default, aiming for
compatibility with Prometheus conventions. Multiple consecutive `_` characters
SHOULD be replaced with a single `_` character.

The Unit of an OTLP metric point MUST be converted from the UCUM unit to the
equivalent unit word in Prometheus if it is included in the
table in [Metric Metadata above](#metric-metadata).

Portions of the Unit within brackets (e.g. {packet}) MUST be dropped.

Units defined as rates over time (e.g. "m/s") MUST be converted to words (e.g.
"meters_per_second").

The resulting unit SHOULD be added to the metric as
[UNIT metadata](https://github.com/prometheus/OpenMetrics/blob/v1.0.0/specification/OpenMetrics.md#metricfamily).
A suffix to the metric name SHOULD be added unless the metric name already ends with the
unit (before type-specific suffixes). The
unit suffix comes before any type-specific suffixes.

The description of an OTLP metrics point MUST be added as
[HELP metadata](https://prometheus.io/docs/instrumenting/exposition_formats/#comments-help-text-and-type-information).

The data point type of an OTLP metric MUST be added as
[TYPE metadata](https://prometheus.io/docs/instrumenting/exposition_formats/#comments-help-text-and-type-information).
It also dictates type-specific conversion rules listed below.

### Instrumentation Scope

**Status**: [Stable](../document-status.md)

Prometheus exporters MUST by default add
the scope name as the `otel_scope_name` label,
the scope version as the `otel_scope_version` label,
the scope schema URL as the `otel_scope_schema_url` label,
the scope attributes as labels with `otel_scope_` prefix and following the rules
described in the [`Metric Attributes`](#metric-attributes) section below,
on all metric points, based on the scope the original data point was nested in.
Scope attributes that, after adding the `otel_scope_` prefix and applying the
label-name conversion described in [`Metric Attributes`](#metric-attributes),
would conflict with `otel_scope_name`, `otel_scope_version`, or
`otel_scope_schema_url` MUST be dropped.

### Gauges

**Status**: [Stable](../document-status.md)

An [OpenTelemetry Gauge](../metrics/data-model.md#gauge) MUST be converted following 
a hint present in [metric.metadata][metricMetadata]:
- If the `prometheus.type` key is absent, or its value is equal to `gauge`, the datapoint MUST be transformed to a Prometheus Gauge.
- If the `prometheus.type` key has value equal to `unkown`, the datapoint MUST be transformed to a Prometheus Unknown.
- If the `prometheus.type` key has value equal to `info`, the datapoint SHOULD be transformed to a Prometheus Info.
- If the `prometheus.type` key has value equal to `stateset`, the datapoint SHOULD be transformed to a Prometheus Stateset.

Exemplars on OpenTelemetry Gauges SHOULD be dropped.

### Sums

**Status**: [Stable](../document-status.md)

An [OpenTelemetry Sum](../metrics/data-model.md#sums) MUST be converted following the rules below:

- If the aggregation temporality is cumulative and the sum is monotonic, it MUST be converted to a Prometheus Counter.
- If the aggregation temporality is cumulative and the sum is non-monotonic, it should follow the same rules as described for [OpenTelemetry Gauge](#gauges-1)
- If the aggregation temporality is delta and the sum is monotonic, it MAY be converted to a cumulative temporality and become a Prometheus Counter. The following behaviors are expected:
  - The new data point type must be the same as the accumulated data point type.
  - The new data point's start time must match the time of the accumulated data point. If not, see [detecting alignment issues](../metrics/data-model.md#sums-detecting-alignment-issues).

If the metric name for monotonic Sum metric points does not end in a suffix of `_total` a suffix of `_total` SHOULD be added by default, otherwise the name MUST remain unchanged.

Monotonic Sum metric points with `StartTimeUnixNano` SHOULD transform `StartTimeUnixNano` into Prometheus `StartTime`, following the appropriate format used by each Prometheus protocol. 

If Sum is converted to a Prometheus Counter, then `Exemplars` MUST be converted
as described in the [Exemplar Conversion](#exemplar-conversion) section.
Otherwise, `Exemplars` SHOULD be dropped. If the Prometheus protocol only
supports a single exemplar on the Counter sample, the latest exemplar SHOULD be
converted. This matches the behavior of Prometheus client libraries, which is to keep the
latest exemplar for counter instruments.

### Histograms

**Status**: [Development](../document-status.md)

An [OpenTelemetry Histogram](../metrics/data-model.md#histogram) with a cumulative aggregation temporality MUST be converted to a Prometheus metric family with the following metrics:

- A single `{name}_count` metric denoting the count field of the histogram. All attributes of the histogram point are converted to Prometheus labels.
- `{name}_sum` metric denoting the sum field of the histogram, reported only if the sum is positive and monotonic. The sum is positive and monotonic when all buckets are positive. All attributes of the histogram point are converted to Prometheus labels.
- A series of `{name}_bucket` metric points that contain all attributes of the histogram point recorded as labels.  Additionally, a label, denoted as `le` is added denoting the bucket boundary. The label's value is the stringified floating point value of bucket boundaries, ordered from lowest to highest. The value of each point is the sum of the count of all histogram buckets up to the boundary reported in the `le` label.  The final bucket metric MUST have an `+Inf` threshold.
- Histograms with `StartTimeUnixNano` set should export the `{name}_created` metric as well.

`Exemplars` are converted as described in the [Exemplar Conversion](#exemplar-conversion) section.
If the Prometheus protocol only supports a single exemplar per-bucket, the latest
exemplar that falls into each bucket SHOULD be converted.

OpenTelemetry Histograms with Delta aggregation temporality SHOULD be aggregated into a Cumulative aggregation temporality and follow the logic above, or MUST be dropped.

### Exponential Histograms

**Status**: [Development](../document-status.md)

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
- `Exemplars` are converted as described in the [Exemplar Conversion](#exemplar-conversion) section.

[OpenTelemetry Exponential Histogram](../metrics/data-model.md#exponentialhistogram)
metrics with the delta aggregation temporality are dropped.

### Summaries

**Status**: [Development](../document-status.md)

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

Exemplars on OpenTelemetry Summaries SHOULD be dropped.

### Metric Attributes

**Status**: [Stable](../document-status.md)

OpenTelemetry Metric Attributes MUST be converted to
[Prometheus labels](https://prometheus.io/docs/concepts/data_model/#metric-names-and-labels).
String Attribute values are converted directly to Metric Attributes, and
non-string Attribute values MUST be converted to string attributes following
the [attribute specification](../common/README.md#anyvalue-representation-for-non-otlp-protocols). Prometheus
naming conventions encourage metric names to match the following regular expression:
`[a-zA-Z_]([a-zA-Z0-9_])*`. Discouraged characters SHOULD be replaced with the
`_` character. Multiple consecutive `_` characters SHOULD be replaced with a
single `_` character. This conversion, or other labels (e.g. `otel_scope_name`)
added by this specification, may cause different OpenTelemetry keys to map to
the same Prometheus key. In such cases, the values MUST be concatenated together,
separated by `;`, and ordered by the lexicographical order of the original keys.

### Exemplar Conversion

**Status**: [Stable](../document-status.md)

When an exemplar is converted per the metric-type-specific sections above,
the [OpenTelemetry Exemplar](../metrics/data-model.md#exemplars) MUST be converted
to a Prometheus exemplar if the Prometheus (push or pull) protocol being used
supports them, as follows:

* If present, the OpenTelemetry Exemplar's Trace ID and Span ID MUST be added as
  Exemplar labels using the `trace_id` and `span_id` keys, respectively. These
  labels MUST take precedence over labels from `filtered_attributes` in cases
  where there is a key collision.
* Timestamps MUST be added as timestamps on the Prometheus exemplar.
* `filtered_attributes` MUST be added as labels on the Prometheus exemplar,
  unless they would exceed the Prometheus protocol's exemplar limits. For
  example, OpenMetrics 1.0 imposes a
  [128 character limit](https://github.com/prometheus/OpenMetrics/blob/v1.0.0/specification/OpenMetrics.md#exemplars).

### Resource Attributes

**Status**: [Development](../document-status.md)

In Prometheus exporters, an OpenTelemetry Resource SHOULD be converted to
a [`target` info metric](https://github.com/prometheus/OpenMetrics/blob/v1.0.0/specification/OpenMetrics.md#supporting-target-metadata-in-both-push-based-and-pull-based-systems)
if the resource is not [empty](../resource/sdk.md#the-empty-resource).
The Resource attributes MAY be copied to labels of exported metric families
if required by the exporter configuration, or MUST be dropped. The `target`
info metric MUST be an info-typed
metric whose labels MUST include the resource attributes, and MUST NOT include
any other labels.

In the Collector's Prometheus exporters, it is
possible for metrics from multiple targets to be sent together, so targets must
be disambiguated from one another. However, the Prometheus exposition format
and [remote-write](https://github.com/Prometheus/Prometheus/blob/main/prompb/remote.proto)
formats do not include a notion of resource, and expect metric labels to
distinguish scraped targets. By convention, [`job` and `instance`](https://prometheus.io/docs/concepts/jobs_instances/)
labels distinguish targets and are expected to be present on metrics exposed on
a Prometheus pull exporter (a ["federated"](https://prometheus.io/docs/prometheus/latest/federation/)
Prometheus endpoint) or pushed via Prometheus remote-write. In OpenTelemetry
semantic conventions, the `service.name`, `service.namespace`, and
`service.instance.id` triplet is
[required to be unique](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/resource/README.md#service),
which makes them good candidates to use to construct `job` and `instance`. In
the collector Prometheus exporters, the `service.name` and `service.namespace`
attributes MUST be combined as `<service.namespace>/<service.name>`, or
`<service.name>` if namespace is empty, to form the `job` metric label.  The
`service.instance.id` attribute, if present, MUST be converted to the
`instance` label; otherwise, `instance` should be added with an empty value.
Other resource attributes SHOULD be converted to a
[target](https://github.com/prometheus/OpenMetrics/blob/v1.0.0/specification/OpenMetrics.md#supporting-target-metadata-in-both-push-based-and-pull-based-systems)
info metric, or MUST be dropped. The `target` metric is an info-typed metric
whose labels MUST include the resource attributes, and MUST NOT include any
other labels other than `job` and `instance`.  There MUST be at most one
`target` info metric exported for each unique combination of `job` and `instance`.

If info-typed metric families are not yet supported by the language Prometheus client library, a gauge-typed metric family named `target_info` with a constant value of 1 MUST be used instead.

To convert OTLP resource attributes to Prometheus labels, string Attribute values are converted directly to labels, and non-string Attribute values MUST be converted to string attributes following the [attribute specification](../common/README.md#attribute).

[metricMetadata]: https://github.com/open-telemetry/opentelemetry-proto/blob/c451441d7b73f702d1647574c730daf7786f188c/opentelemetry/proto/metrics/v1/metrics.proto#L199
