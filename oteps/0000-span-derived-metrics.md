# Span-derived metrics

Define a standard, semantic-convention-aligned shape for metrics derived from
spans, so every span-to-metrics component (SDK processor, Collector connector,
eBPF agent, backend) produces and consumes the same data.

Tracking issue:
[semantic-conventions#4240](https://github.com/open-telemetry/semantic-conventions/issues/4240).

## Motivation

Turning spans into RED (rate, errors, duration) metrics is one of the most
common things people do with OpenTelemetry traces. It powers service
dashboards, SLOs, and APM views, and it works even for code that has no metric
instrumentation at all.

Yet the output has **no specification**. The Collector
[`spanmetrics` connector](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/connector/spanmetricsconnector)
set the de-facto shape, and that shape is defined only by its README and
configuration. As a result:

- **Producers disagree.** The connector, OpenTelemetry eBPF Instrumentation
  (OBI), Grafana Tempo, and vendor SDK-side generators differ in metric names
  (`traces.span.metrics.calls` vs `traces_spanmetrics_calls_total`), enum
  values (`SPAN_KIND_SERVER` vs `SERVER`; `STATUS_CODE_ERROR` vs `ERROR`),
  duration units (`ms` vs `s`), bucket boundaries, and where `service.name`
  lives.
- **Consumers hardcode one producer.** Jaeger SPM queries
  `status_code="STATUS_CODE_ERROR"` and assumes `ms`. Moving the connector to
  `s` or to `otel.status_code` breaks it, which is why those fixes have sat
  behind feature gates for several releases.
- **The shape doesn't follow semantic conventions.** It uses attributes outside
  the registry, a pluralized namespace, a unit-less counter, no `error.type`,
  and two metrics where semantic conventions use one histogram.
- **Shared behavior is undefined.** Which spans count? What do sampled spans
  mean for counts? How do two generators avoid counting the same span twice?
  Each implementation answers differently. Some answers are invisible in the
  output: the connector always scales counts by the
  [OTEP 235](./trace/0235-sampling-threshold-in-trace-state.md) adjusted count.
- **Cardinality.** The only standard grouping key is the span name, which
  explodes when instrumentation doesn't follow span-naming rules. The
  [Span Type OTEP](./5233-span-type.md) gives a low-cardinality alternative,
  but span metrics have no defined way to use it.

The tracking issue lists each of these gaps with links to the relevant
semantic conventions, specification sections, and implementation sources.

A specification lets backends build on one shape, lets generators be checked
for conformance (for example with Weaver live-check), and lets the connector
make its pending fixes without breaking consumers one at a time.

This needs an OTEP rather than only a semantic conventions change because it
adds attributes to the reserved `otel.*` namespace, which
[must be approved as part of the OpenTelemetry specification](https://opentelemetry.io/docs/specs/semconv/general/naming/#otel-namespace),
and because it defines behavior across components: which spans are measured,
how sampling is handled, and how double counting is avoided.

## Explanation

A **span-metrics generator** is any component that observes ended spans and
records metrics from them. For each ended span it records **one measurement**
on a single histogram, `otel.span.duration`.

### Example

```text
Span (resource: service.name=checkout, service.namespace=shop, ...)
  name:   GET /orders/{id}
  kind:   SERVER
  type:   http.server.request
  status: ERROR
  start → end: 231 ms
  attributes:
    http.request.method=GET
    http.route=/orders/{id}
    http.response.status_code=500
    error.type=500
    url.scheme=https
    user.id=8812                 ← not copied (not part of the convention)

              │  span-metrics generator
              ▼

Metric: otel.span.duration   (Histogram, unit "s")
  resource:  service.name=checkout, service.namespace=shop, ...   ← same as span
  scope:     <generator name/version>, schema_url=<semconv version>
  data point attributes:
    otel.span.name=GET /orders/{id}
    otel.span.kind=SERVER
    otel.span.type=http.server.request
    otel.status_code=ERROR
    error.type=500
    http.request.method=GET
    http.route=/orders/{id}
    http.response.status_code=500
    url.scheme=https
  recorded value: 0.231   (weight 1)
```

### What users get

| Question | How to answer it |
| --- | --- |
| Throughput | Rate of the histogram **count** |
| Error rate | Count where `error.type` is present ÷ total count (or `otel.status_code="ERROR"`) |
| Latency | Histogram quantiles / buckets |
| Per operation | Group by `otel.span.name`, or by `otel.span.type` + domain attributes (for example `http.route`) for low cardinality |
| Per service | Group by resource `service.name` |

This is the same pattern semantic conventions already use for
[`http.server.request.duration`](https://opentelemetry.io/docs/specs/semconv/http/http-metrics/#metric-httpserverrequestduration)
and similar metrics: one duration histogram, with throughput and errors derived
from it, as recommended by
[recording errors on metrics](https://opentelemetry.io/docs/specs/semconv/general/recording-errors/#recording-errors-on-metrics).

### Metric

| Name | Instrument | Unit | Description |
| --- | --- | --- | --- |
| `otel.span.duration` | Histogram | `s` | Duration of ended spans, computed from span start and end timestamps. |

Generators SHOULD use the
[`ExplicitBucketBoundaries`](../specification/metrics/api.md#instrument-advisory-parameters)
advice `[0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1, 2.5, 5, 7.5, 10]`
(the semantic conventions standard for HTTP, RPC, and messaging durations).
They MAY use exponential histograms instead.

### Data point attributes

| Attribute | Type | Requirement level | Notes |
| --- | --- | --- | --- |
| `otel.span.name` | string | Required | The span name, unchanged. **New.** |
| `otel.span.kind` | enum: `SERVER`, `CLIENT`, `PRODUCER`, `CONSUMER`, `INTERNAL` | Required | [SpanKind](../specification/trace/api.md#spankind) API names, not protobuf names. **New.** |
| [`otel.status_code`](https://opentelemetry.io/docs/specs/semconv/registry/attributes/otel/#otel-status-code) | enum: `OK`, `ERROR` | Conditionally Required: if span status is not `UNSET` | Existing, stable. MUST NOT be set when status is `UNSET`. |
| [`error.type`](https://opentelemetry.io/docs/specs/semconv/registry/attributes/error/#error-type) | string | Conditionally Required: if the operation failed | Existing, stable. Copied from the span. If the span status is `ERROR` and the span has no `error.type`, set `_OTHER`. Not set on success. |
| `otel.span.type` | string | Conditionally Required: if the span has a type | From the [Span Type OTEP](./5233-span-type.md). **New.** |
| Domain attributes | — | See below | Reused from existing conventions. |

### Domain attributes

When a span follows a semantic convention that defines an operation-duration
metric, the generator copies the **attributes defined on that metric** from the
span, keeping their requirement levels. Required and Conditionally Required
attributes are copied when present on the span. Recommended attributes SHOULD
be copied when present. Opt-In attributes are copied only when the user enables
them.

| Span (identified by `otel.span.type`, or by kind + marker attribute until span type is widely adopted) | Attribute set comes from |
| --- | --- |
| HTTP server | [`http.server.request.duration`](https://opentelemetry.io/docs/specs/semconv/http/http-metrics/#metric-httpserverrequestduration) |
| HTTP client | [`http.client.request.duration`](https://opentelemetry.io/docs/specs/semconv/http/http-metrics/#metric-httpclientrequestduration) |
| RPC server / client | [`rpc.server.call.duration`](https://opentelemetry.io/docs/specs/semconv/rpc/rpc-metrics/#metric-rpcservercallduration) / [`rpc.client.call.duration`](https://opentelemetry.io/docs/specs/semconv/rpc/rpc-metrics/#metric-rpcclientcallduration) |
| Database client | [`db.client.operation.duration`](https://opentelemetry.io/docs/specs/semconv/db/database-metrics/#metric-dbclientoperationduration) |
| Messaging client / process | [`messaging.client.operation.duration`](https://opentelemetry.io/docs/specs/semconv/messaging/messaging-metrics/#metric-messagingclientoperationduration) / [`messaging.process.duration`](https://opentelemetry.io/docs/specs/semconv/messaging/messaging-metrics/#metric-messagingprocessduration) |
| GenAI client | `gen_ai.client.operation.duration` ([semantic-conventions-genai](https://github.com/open-telemetry/semantic-conventions-genai)) |
| FaaS server | [`faas.invoke_duration`](https://opentelemetry.io/docs/specs/semconv/faas/faas-metrics/#metric-faasinvoke_duration) |

This reuses vetted, low-cardinality attribute sets instead of inventing a new
list. When semantic conventions add a convention with a duration metric, span
metrics pick it up automatically. Users MAY configure extra attributes. Those
are outside the convention and SHOULD be documented by the generator.

### Span attribute for avoiding double counting

| Attribute (on **spans**) | Type | Requirement level | Notes |
| --- | --- | --- | --- |
| `otel.span.metrics.skip` | boolean | Opt-In | `true` means span metrics for this span were already recorded by an upstream generator. **New.** |

## Internal details

### Which spans are measured

1. Each ended span is measured **exactly once** across the whole pipeline.
2. A generator MUST NOT measure a span with `otel.span.metrics.skip=true`.
3. A generator that measures a span AND exports that span onward SHOULD set
   `otel.span.metrics.skip=true` on it, so later generators skip it. SDK-side
   generators need to set it while the span is still writable (for example on
   start, or in an [`OnEnding`](../specification/trace/sdk.md#onending) hook
   where available).
4. All span kinds are measured, `INTERNAL` included. Because a `SERVER` span
   and its `INTERNAL` children cover the same work, **adding up across
   `otel.span.kind` is not meaningful**. Consumers SHOULD filter or group by
   kind. Generators MAY offer a kind filter.
5. Spans missing required resource identity (for example no `service.name`)
   are still measured. The connector's current behavior of silently dropping
   them is not conformant.

### Duration

`duration = (end_time − start_time)` in seconds, as a double. If
`end_time < start_time`, the generator MUST record `0`. The span is still
counted.

### Sampling

There are two kinds of generator, and they MUST count differently:

```text
  ┌──────────────────────────── SDK ───────────────────────────┐
  │ span ends ──► generator (sees ALL spans, via AlwaysRecord) │──► weight = 1 always
  └──────────────────────────┬─────────────────────────────────┘
                             │ only sampled spans exported
                             ▼
  ┌──────────────────────── Collector ─────────────────────────┐
  │ generator (sees SAMPLED spans) ──► weight = adjusted count │
  └────────────────────────────────────────────────────────────┘
```

- **Pre-sampling generators** see spans regardless of the sampling decision,
  for example a span processor used with the
  [AlwaysRecord](../specification/trace/sdk.md#alwaysrecord) sampler. They
  MUST record each span with weight 1, even if the span's `tracestate` carries
  an OTEP 235 threshold. Otherwise they would extrapolate data that is already
  complete.
- **Post-sampling generators** see only sampled spans. When a span carries a
  valid [OTEP 235](../specification/trace/tracestate-probability-sampling.md)
  threshold (`ot=th:…`), they SHOULD record it with weight = adjusted count
  (1/p), for both the count and the bucket. Otherwise weight is 1.
- A generator MAY add the Opt-In data point attribute `otel.span.count_method`
  = `counted` | `extrapolated`, so consumers can tell exact data from
  estimates.

### Resource and scope

- The metric's Resource MUST be the span's Resource, unchanged.
- Resource attributes (including `service.name`) SHOULD NOT be copied onto data
  points. Exporters for formats without resources handle promotion (for
  example Prometheus `target_info` / `job`).
- Instrumentation scope: the generator's own name and version. `schema_url`
  SHOULD be the semantic conventions version the generator implements.

### Single writer

Two generator instances receiving spans for the same resource (for example
load-balanced collectors) would write the same series. Generators MUST ensure
the [single-writer](../specification/metrics/data-model.md#single-writer)
property, either by routing spans so that one instance owns each resource, or
by adding an identifying attribute. The standard way to do the latter is an
open question (see below). A random UUID on every data point, as the connector
does today with `collector.instance.id`, multiplies series by the number of
instances and is NOT RECOMMENDED by default.

### Temporality

Not prescribed. It follows the exporter's temporality preference, as for any
other metric. Generators MUST set `AggregationTemporality` and start timestamps
correctly.

### Legacy semantic conventions versions on spans

Spans can use older semantic conventions attribute names (for example
`http.method`). Generators SHOULD copy the deprecated equivalents defined in
the registry (`deprecated: renamed_to`) unchanged. They MUST NOT rename or
translate values. Schema transformation is a separate concern.

### Migration from the current de-facto shape

| Current (connector) | Proposed |
| --- | --- |
| `traces.span.metrics.duration` (`ms` default) | `otel.span.duration` (`s`) |
| `traces.span.metrics.calls` | Histogram count (see open question on the counter) |
| `span.name` | `otel.span.name` |
| `span.kind` = `SPAN_KIND_SERVER` | `otel.span.kind` = `SERVER` |
| `status.code` = `STATUS_CODE_ERROR` / `STATUS_CODE_UNSET` | `otel.status_code` = `ERROR` / *(absent)* |
| *(none)* | `error.type` |
| `service.name` on data point | Resource only |
| `collector.instance.id` | See single-writer open question |
| `span.instrumentation.scope.name/version` | `otel.scope.name/version` (only if a user opts in) |
| `sampling.method` | `otel.span.count_method` |
| OBI `span.metrics.skip` | `otel.span.metrics.skip` (generators SHOULD also honor the old key during migration) |

The old names would be registered in semantic conventions as **deprecated,
`renamed_to`** the new ones, so Weaver live-check and schema tooling understand
both. Generators SHOULD offer a dual-emit period behind a flag, as OBI already
does for its legacy names.

### Error modes and corner cases

| Case | Behavior |
| --- | --- |
| Span name is high-cardinality (`GET /orders/8812`) | Recorded as-is. Generators MAY apply a [cardinality limit](../specification/metrics/sdk.md#cardinality-limits) (overflow series uses `otel.metric.overflow=true`) and MAY offer name sanitization. Users can group by `otel.span.type` + domain attributes instead. |
| Span status `ERROR` but no `error.type` | `error.type=_OTHER` |
| `error.type` set but status `UNSET` | Copy `error.type`; omit `otel.status_code`. Consumers relying on `error.type` still see the failure. |
| Span has a type but no matching duration-metric convention | Base attributes only |
| Same app also emits native `http.server.request.duration` | Different metric name, so no collision. Backends choose which to show. Span metrics remain the fallback for operations without metric instrumentation. |
| Span arrives at two generators (for example SDK + Collector) | The first sets `otel.span.metrics.skip`; the second skips it. |

## Trade-offs and mitigations

- **Breaking for current consumers** (Jaeger SPM, dashboards on
  `traces_span_metrics_*`). *Mitigation:* deprecated aliases, dual-emit period,
  and a migration table. Several of these changes (`s` unit,
  `otel.status_code`) are already planned behind connector feature gates. This
  OTEP gives them a target to land on.
- **More series from domain attributes.** *Mitigation:* we reuse attribute
  sets that semantic conventions already vetted as low-cardinality for
  metrics. Opt-In attributes stay Opt-In.
- **Histogram-only is heavier** for backends that store each bucket as a
  series. *Mitigation:* exponential histograms; an optional counter (open
  question).
- **New `otel.*` attributes** need specification approval. That's why this is
  an OTEP.
- **Span type adoption will take years.** *Mitigation:* span name and kind +
  marker-attribute detection work today; `otel.span.type` is used when
  present.

## Prior art and alternatives

### Prior art

- Collector
  [`spanmetrics` connector](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/connector/spanmetricsconnector),
  the de-facto shape, plus its OTEP 235 extrapolation
  ([collector-contrib#45557](https://github.com/open-telemetry/opentelemetry-collector-contrib/pull/45557)).
- OBI's Weaver definition of the same shape
  ([`schemas/obi/groups/spanmetrics/`](https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/tree/main/schemas/obi/groups/spanmetrics))
  and its `span.metrics.skip` hint. Grafana's k8s-monitoring Helm chart already
  filters spans with `span.metrics.skip` before the connector.
- Grafana Tempo metrics-generator (`traces_spanmetrics_*`).
- SDK-side generation:
  [opentelemetry-java-contrib#802](https://github.com/open-telemetry/opentelemetry-java-contrib/pull/802);
  the [AlwaysRecord](../specification/trace/sdk.md#alwaysrecord) sampler
  ([spec#4698](https://github.com/open-telemetry/opentelemetry-specification/issues/4698),
  [spec#5283](https://github.com/open-telemetry/opentelemetry-specification/pull/5283)),
  whose stated purpose is accurate span-to-metrics processing.
- Semantic conventions' own operation-duration metrics and
  [recording errors](https://opentelemetry.io/docs/specs/semconv/general/recording-errors/)
  guidance, which this proposal follows.

### Alternatives considered

1. **Just document the current connector shape as-is.** Rejected. It would
   make permanent a pluralized, configurable namespace, protobuf enum values, a
   unit-less counter, `ms` durations, and attributes outside the registry. All
   of these conflict with existing semantic conventions rules.
2. **Emit the domain metrics themselves** (for example
   `http.server.request.duration`) from spans. Rejected as the default. It
   collides with natively instrumented metrics (same name, so double counting
   and single-writer violations), and span scope can differ from what the
   metric definition measures. It could be a future opt-in mode keyed on span
   type.
3. **Group only by span type, drop span name.** Rejected for now. Span type
   isn't populated yet, and span name is what users recognize.
4. **Separate counters for calls and errors.** Rejected. Semantic conventions
   recommend one metric with `error.type` over separate success/failure
   metrics, and the histogram count already gives throughput.

## Open questions

1. **Namespace:** `otel.span.*` (reserved for OpenTelemetry concepts, needs
   specification approval) vs `span.*` (no approval needed, but unreserved and
   may collide). This proposal uses `otel.span.*`.
2. **Counter:** keep an Opt-In counter (for example `otel.span.calls`, unit
   `{call}`) for backends where histograms are expensive and for backward
   compatibility? Or rely on histogram count only?
3. **Single writer:** what is the standard identifying attribute when routing
   isn't possible (`otel.component.name`? `service.instance.id` of the
   generator?), and should it go on the Resource or on data points?
4. **Buckets:** the semantic conventions standard `[0.005 … 10]` vs the
   connector's `[0.002 … 15]` (which keeps 2–4 ms resolution and a tail above
   10 s). Or recommend exponential histograms by default?
5. **`otel.span.count_method`:** is a per-data-point attribute the right
   signal, or should extrapolation be signalled at scope level?
6. **`otel.span.metrics.skip` vs OBI's `span.metrics.skip`:** adopt OBI's key
   as-is (no migration for OBI) or move it into `otel.*`?
7. **Entry vs nested spans:** should `otel.span.parent.origin`
   (`none`/`local`/`remote`, already in the registry) be an Opt-In data point
   attribute, so users can select service entry points without filtering by
   kind?
8. **Span events metric** (`traces.span.metrics.events` in the connector): in
   scope, or left as a generator extension?

## Prototypes

- Collector `spanmetrics` connector: most pieces already exist behind feature
  gates (`useSecondAsDefaultMetricsUnit`, `useOtelPrefix`,
  `excludeResourceMetrics`, `enable_metrics_sampling_method`).
- CloudWatch Plugin for OpenTelemetry: an SDK-side generator, for example the
  open source [Go implementation](https://github.com/aws-observability/cloudwatch-plugin-otel-go).
  It already uses `s`, keeps `service.name` on the Resource only, copies
  semantic conventions domain attributes, and implements a skip-style
  double-counting handshake with a downstream generator. A reference prototype
  of the shape proposed here is planned.
- OBI: emits the de-facto shape and defines it in Weaver.

## Future possibilities

- **Span-type-driven generation:** once `otel.span.type` is widespread,
  generators can choose the attribute set by type alone, and an opt-in mode
  could emit the domain metric directly.
- **Self-time histogram** (span duration minus child time;
  [collector-contrib#50029](https://github.com/open-telemetry/opentelemetry-collector-contrib/issues/50029)).
- **Service graph / dependency edge metrics** derived from CLIENT↔SERVER span
  pairs
  ([collector-contrib#26648](https://github.com/open-telemetry/opentelemetry-collector-contrib/issues/26648)),
  on the same attribute model.
- A specified **SDK span-metrics processor** component, so SDKs can ship
  conformant generation without the Collector.
- **Weaver live-check** conformance tests for any span-metrics generator.
