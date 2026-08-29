# Span type

Introduce a `type` property on spans that identifies the semantic convention
definition a span follows, making spans identifiable the same way metrics,
events, and entities already are.

## Motivation

There is no reliable way to tell which semantic convention a span in a stream of
spans follows. Consumers need to know the convention and invent a per-span
heuristic to recognize it, with no guarantee that such a heuristic exists, or
that a future update will not break it.

This limits the ability to query, generate, transform, aggregate, or visualize
spans, and it blocks validation: it is not possible to map a span received over
OTLP to the semantic convention that defines it.

Weaver [live check], collector schema transformation, and backend-side
conformance checking all need to resolve an observed span to its definition
before they can say anything about it. Today they can only apply heuristics that
are wrong by construction for multi-span conventions.

Span-to-metrics pipelines have the same gap. The collector
[spanmetrics connector] emits one generic duration and call-count metric for
every span, dimensioned by span name and kind, which regularly explodes in
cardinality when span names are not populated correctly. Span type would give
such pipelines a low-cardinality dimension to group by.

Related issues:
[spec#4733](https://github.com/open-telemetry/opentelemetry-specification/issues/4733),
[semconv#2055](https://github.com/open-telemetry/semantic-conventions/issues/2055),
[spec#531](https://github.com/open-telemetry/opentelemetry-specification/issues/531),
[spec#1161](https://github.com/open-telemetry/opentelemetry-specification/issues/1161).

### Identity today

Historically we tried to solve the problem by defining a required attribute per
convention area and using its presence as the signal that the span follows that
convention: `db.system.name`, `http.request.method`, `messaging.system`,
`rpc.system`, `gen_ai.provider.name`, `faas.trigger`,
`feature_flag.provider.name`, and so on.

This was never fully reliable, but it worked well enough while there was a single
semantic convention registry with a handful of spans in it. It no longer holds
up:

- Every convention has to define and maintain such an attribute, and consumers
  have to know all of them up front.
- Conventions define more than one span each, so the marker attribute narrows a
  span down to an area, not to a definition. Disambiguating further needs
  convention-specific heuristics, and in the general case is impossible.
- Third-party (non-OTel) conventions have no way to participate at all.
- The instrumentation scope `schema_url` does not narrow it down either: it
  identifies the registry and its version, and a registry defines many spans.
- Neither does span kind. Deleting a message and creating a queue are both
  `CLIENT` messaging spans, but they are structurally different: different
  attributes, different span name rules, different error criteria.

The scale of the problem is not hypothetical. At the time of writing:

| Registry | Span definitions |
| --- | --- |
| [semantic-conventions](https://github.com/open-telemetry/semantic-conventions) | 64 |
| [semantic-conventions-genai](https://github.com/open-telemetry/semantic-conventions-genai) | 12 |

76 span definitions today, and both registries keep growing. A consumer that
wants to classify them has to reimplement the full heuristic tree, and keep it in
sync.

### Conventions are already inventing span types, inconsistently

Because the need is real, individual conventions grow their own identity
attributes:

- Messaging defines
  [`messaging.operation.type`](https://github.com/open-telemetry/semantic-conventions/blob/main/docs/messaging/messaging-spans.md)
  (`create`, `send`, `receive`, `process`, `settle`) with the sole purpose of
  telling consumers which messaging span definition applies
  ([semconv#913](https://github.com/open-telemetry/semantic-conventions/pull/913),
  [semconv#1422](https://github.com/open-telemetry/semantic-conventions/pull/1422)).
  It is a span type wearing an attribute costume: it is not the operation the
  user called, it is the definition the span follows.
- GenAI uses `gen_ai.operation.name` for the same purpose, but the mapping is not
  1:1: `chat`, `generate_content`, and `text_completion` all describe the same
  `gen_ai.inference.client` span definition, and more values keep arriving (for
  example
  [semconv-genai#353](https://github.com/open-telemetry/semantic-conventions-genai/pull/353)
  adds `fetch_response`, which is a non-inference operation and is not an
  inference span).
- Outside OpenTelemetry, [OpenInference](https://github.com/Arize-ai/openinference/blob/main/spec/semantic_conventions.md#span-kinds)
  (Arize) requires an `openinference.span.kind` attribute on every span, with
  values `LLM`, `EMBEDDING`, `CHAIN`, `RETRIEVER`, `RERANKER`, `TOOL`, `AGENT`,
  `GUARDRAIL`, `EVALUATOR`, `PROMPT`. It is named after OTel's `SpanKind` but it
  is not a span kind at all. A convention had to shadow a core span property to
  get an identity, because OTLP does not offer one.

### Consistency across signals

Every other signal has an identifying, low-cardinality, definition-level
property:

| Signal | Identity |
| --- | --- |
| Metric | metric name |
| Log | top-level `event_name` field |
| Entity | entity type |
| Span | *(missing)* |

Span name is not a substitute: it is dynamic, per-instance (`GET /orders/{id}`),
and explicitly allowed to vary. `SpanKind` is not a substitute either: it is a
fixed six-value enum describing the relationship to a remote peer, orthogonal to
what the span represents.

## Explanation

A span gains a new top-level string property: **span type**. It identifies the
semantic convention definition the span follows.

```text
type: gen_ai.client.inference
name: chat gpt-4o-mini
kind: CLIENT
attributes: gen_ai.operation.name=chat, ...
```

Examples:

| type | name | kind |
| --- | --- | --- |
| `http.server.request` | `GET /orders/{id}` | `SERVER` |
| `db.client.call` | `SELECT orders` | `CLIENT` |
| `messaging.producer.send` | `send orders-queue` | `PRODUCER` |
| `messaging.consumer.process` | `process orders-queue` | `CONSUMER` |
| `gen_ai.client.inference` | `chat gpt-4o-mini` | `CLIENT` |
| `gen_ai.internal.execute_tool` | `execute_tool get_weather` | `INTERNAL` |

### Span type is an optional string

Values are owned by whoever defines the convention: OpenTelemetry semantic
conventions, or a third party. They SHOULD follow
`{area}.{kind}.{domain-specific-name}`, for example `messaging.producer.send`,
`gen_ai.client.inference`, `http.server.request`, so that they do not collide and
so that a prefix can be used for coarse grouping by area and kind.

Span types are unique within the scope of a Schema URL
(including the dependency tree), following the same
identity model as other semantic convention definitions.

Spans without a type are valid and MUST be accepted. A missing type means "this
span does not follow a known definition", which is true for all existing spans.

### Span type syntax

Span type values are restricted to a small character set, defined below using the
[Augmented Backus-Naur Form](https://datatracker.ietf.org/doc/html/rfc5234):

```abnf
span-type = ALPHA 0*254 ("_" / "." / "-" / "/" / ALPHA / DIGIT)

ALPHA = %x41-5A / %x61-7A; A-Z / a-z
DIGIT = %x30-39 ; 0-9
```

* Case-insensitive ASCII strings.
* The first character is alphabetic.
* Maximum length of 255 characters.

This is the same as the
[instrument name syntax](../specification/metrics/api.md#instrument-name-syntax).

### One span, one type

A span has exactly one type. There is no mixing of identities.

If an operation legitimately matches two definitions at the same time, for
example a serverless function invoked by an HTTP trigger, which is both a FaaS
invocation and an HTTP server request, the answer is to **define a new type for
it**, specifying:

- which attributes to take from each definition and how to populate them at this
  instrumentation point,
- a single span name rule,
- a single set of error status criteria.

This is deliberately the more expensive path. Not all spans need to be reliably
identifiable, and that is fine: those spans do not set a span type.

Carrying several types on one span is rejected in
[Multiple types per span](#alternative-1-multiple-types-per-span).

### Refinements keep the parent span identity

Semantic conventions specialize definitions for specific technologies through
refinements. A refinement **shares the span type of the definition it refines**.
It MAY:

- narrow requirement levels,
- add non-required attributes,
- add examples, notes, and better guidance on how to populate attributes,
- specify a more precise span name format,

but it MUST NOT change the identity in an incompatible way (for example,
downgrade required attributes, change stability or span kind). A consumer that
only understands `messaging.producer.send` handles an SQS span correctly; one
that also knows SQS can use the extra attributes.

Refinements are not identifiable over OTLP. We expect to solve that within
semantic conventions, without new OTLP properties, by pinning attribute values so
a refinement can be recognized from the span's attributes
([weaver#1643](https://github.com/open-telemetry/weaver/pull/1643)).

### This already matches the semantic conventions schema

The [semantic conventions schema v2](./4815-semantic-conventions-schema-v2.md)
already uses span type as the identity of a span definition, and already models
refinements as sharing it:

```yaml
# definition: the identity is `type`
spans:
  - type: messaging.producer.send
    kind: producer
    brief: Describes a producer sending one or more messages to a destination.
    attributes:
      - ref_group: messaging.attributes.common

# refinement: clarifies the definition, keeps its type
span_refinements:
  - id: aws.sqs.producer.send
    ref: messaging.producer.send # this is the span type
    brief: Describes a producer sending one or more messages to Amazon SQS.
    attributes:
      - refinement_discriminator: messaging.system # this is in design phase, does not exist today
        value: aws.sqs
```

## Implementation details

### Protocol

Add a `type` field to `Span`.

```protobuf
message Span {
  // name is the human-readable description of this specific operation.
  string name = 5;

  SpanKind kind = 6;

  // ...
  // type identifies the semantic convention definition this span follows,
  // for example "http.server.request" or "gen_ai.client.inference".
  // Unlike name, type is low-cardinality and stable across instances.
  // An empty value means the span does not follow a known definition or
  // the instrumentation does not yet populate it.
  string type = 17;  // this is new
}
```

### API

Span type is supplied at span creation, next to `SpanKind`:

- The span creation API accepts an optional span type. Default is unset. It is
  added as an optional parameter, so existing calls and existing `Tracer`
  implementations keep working unchanged.

  Backward compatibile ([Extending API/SDK abstractions](../specification/versioning-and-stability.md#extending-apisdk-abstractions))

- Span type is immutable after creation. Like `SpanKind`, it determines what the
  span *is*; it cannot become something else halfway through.
- The API SHOULD NOT validate the value, following the precedent set for
  [instrument names](../specification/metrics/api.md#instrument-name-syntax).

```diff
 class Tracer:
     def start_span(
         self,
         name: str,
         context: Context | None = None,
         kind: SpanKind = SpanKind.INTERNAL,
+        type: str | None = None,
         attributes: Attributes = None,
         links: Links = None,
         start_time: int | None = None,
         record_exception: bool = True,
         set_status_on_exception: bool = True,
     ) -> Span: ...
```

Instrumentations that follow a semantic convention SHOULD set the span type to
the type of the definition they implement.

```diff
 with tracer.start_as_current_span(
     f"chat {model}",
     kind=SpanKind.CLIENT,
+    type="gen_ai.client.inference",
     attributes={"gen_ai.operation.name": "chat"},
 ) as span:
     ...
```

### SDK

- Span type becomes a sampler input, next to name and `SpanKind`, so sampling
  rules can match on it without matching on attributes. `Sampler` is a stable
  plugin interface implemented by end users, so this addition follows
  [Extending API/SDK abstractions](../specification/versioning-and-stability.md#extending-apisdk-abstractions).

  How disruptive it is depends on how the language models the sampler inputs:
  - Languages that already pass a single sampling parameters object (such as
    [Go](https://github.com/open-telemetry/opentelemetry-go/blob/main/sdk/trace/sampling.go#L33)
    and
    [.NET](https://github.com/open-telemetry/opentelemetry-dotnet/blob/main/src/OpenTelemetry/Trace/Sampler/SamplingParameters.cs))
    add a new property to it. Existing samplers keep compiling and
    ignore the new property.

  - Languages that pass sampling parameters as individual arguments cannot extend 
    the existing method without breaking end-user implementations of it. 
    They introduce a new method (for example `ShouldSampleSpan`) with a default implementation that
    delegates to the existing one, so existing samplers keep working. 
    
    The new method SHOULD be shaped so that further inputs can be added without
    repeating this migration, either by taking a sampling parameters object or
    by using a language-specific extensible mechanism such as arbitrary keyword
    arguments (Python's **kwargs, Ruby's **opts).

- Span processors and exporters read span type through
  [readable span](../specification/trace/sdk.md#additional-span-interfaces),
  which already covers everything the Span API defines. There is no setter.

  Backward compatibility: a new property on the `ReadableSpan` - source and
  binary compatible.
- The `Tracer` SHOULD validate that the span type conforms to the
  [span type syntax](#span-type-syntax) and SHOULD emit an error if it does not,
  the same way a `Meter`
  [validates instrument names](../specification/metrics/sdk.md#instrument-name).

```diff
 class Sampler:
     def should_sample(
         self,
         parent_context: Context | None,
         trace_id: int,
         name: str,
         kind: SpanKind | None = None,
         attributes: Attributes = None,
         links: Sequence[Link] | None = None,
         trace_state: TraceState | None = None,
     ) -> SamplingResult: ...

+    # new method; existing samplers that only override should_sample keep
+    # working through the default implementation below
+    def should_sample_span(
+        self,
+        parent_context: Context | None,
+        trace_id: int,
+        name: str,
+        kind: SpanKind | None = None,
+        type: str | None = None,
+        attributes: Attributes = None,
+        links: Sequence[Link] | None = None,
+        trace_state: TraceState | None = None,
+        # scope: InstrumentationScope | None = None,   # see https://github.com/open-telemetry/opentelemetry-specification/issues/1588
+        # resource: Resource | None = None,            # same
+        **kwargs,  # extensibility point for the future needs, so we don't need to define new method name
+    ) -> SamplingResult:
+        # default: ignore the new inputs and fall back to should_sample
+        return self.should_sample(
+            parent_context, trace_id, name, kind, attributes, links, trace_state
+        )
```

> [!NOTE]
>
> Consider bundling this change in the spec and in the implementations together
> with [making InstrumentationScope and Resource available to samplers](https://github.com/open-telemetry/opentelemetry-specification/issues/1588)

```diff
 class ReadableSpan:
     @property
     def name(self) -> str: ...

     @property
     def kind(self) -> SpanKind: ...

+    # the property name is normative, the accessor name is per-language:
+    # languages where `type` is reserved pick their own spelling
+    @property
+    def type(self) -> str | None: ...
```

### Semantic conventions

- No model change is needed: `spans[].type` and `span_refinements[].ref` already
  carry the identity.
- Code generation can start emitting span type constants and setting the type in
  generated helpers.
- A policy can enforce that span types are unique across the resolved registry
  and namespaced consistently.
- Marker attributes such as `messaging.operation.type` can be retired once span
  type is broadly available.

### Declarative configuration

Sampling by span type is expressed through the existing rule-based sampler:
[`ExperimentalComposableRuleBasedSamplerRule`](https://github.com/open-telemetry/opentelemetry-configuration/blob/b20c9d6399c19a1b2e7bd16f18ff6f589d3317a6/schema/tracer_provider.yaml#L304), whose
match conditions are `attribute_values`, `attribute_patterns`, `span_kinds`,
and `parent`.

It gains one more condition:

```yaml
span_types:
  type: array
  minItems: 1
  items: { type: string }
  description: The span types to match exactly (any of).
  defaultBehavior: ignore
```

Prefix/wildcard matching is a natural follow-up that can be added in the future
and is out of scope.

Disabling spans by type, similarly to the existing [tracer scope-level config](../specification/trace/sdk.md#tracerconfig), is a future possibility and is not detailed here.

### Other updates

- [Telemetry stability](../specification/versioning-and-stability.md#telemetry-stability)
  lists the fields semantic conventions guarantee (span name, span kind,
  attribute keys, well-known attribute values). Span type needs to be added to
  that list: changing the type of an existing span definition is a breaking
  change.

- Built-in samplers that match on span name and kind need to accept span type as
  a match condition. Third-party samplers, such as the
  [Jaeger remote sampler](../specification/trace/sdk.md#jaegerremotesampler),
  can be updated if and when the protocols behind them support span type.

- [Mapping to non-OTLP formats](../specification/common/mapping-to-non-otlp.md)
  needs a rule for protocols that have no place for span type. They can map it
  to an `otel.span.type` attribute.

- Downstream, the Collector (pdata, OTTL paths, schema processor) needs the new
  field plumbed through.
- Existing instrumentations need to be updated to populate it.

## Trade-offs and mitigations

- **Wire size.** One short, highly repetitive string per span. Where identity
  matters, it is already recorded through marker attributes, which cost more (a
  key and a value, subject to attribute limits and processing). Where it does not
  matter, span type is unset and costs nothing.
- **Long migration.** SDKs, the Collector, and backends all need the field before
  it is useful end-to-end. Mitigation: it is optional and additive, and the
  existing marker attributes stay in place, so nothing breaks meanwhile.

## Alternatives

### Alternative 1: Multiple types per span

`type` could be a list of strings, so a span that matches two definitions carries
both, and no new type has to be defined for the overlap.

Rejected. A span definition is not just a bag of attributes. It defines:

- the span name,
- the span kind,
- the attributes, their requirement levels, and which are sampling relevant,
- what counts as an error, and what goes into the error description,
- **the scope**: what the duration measures, what nests under the span, and
  whether a failure means one attempt failed or all of them did.

Scope matters most. An alert on HTTP client latency measures one attempt. An
metric on an [AWS SDK operation](#aws-sdk-and-http-client) measures all attempts,
plus authentication, redirects, reading the response body, serialization, and
validation. **These are different numbers, often by a lot, and an SLI is measured
after all tries, not per request.**

Metrics have the same problem: most span definitions come with a matching
duration metric. Would a blended DB and HTTP instrumentation report both metrics,
or a third blended one? Which would users pick for dashboards and alerts?

A single value does not block anything. Blended operations can still be defined,
they just have to be explicit: which scope is traced, which attributes come from
which side, how the span name is built, and which duration metrics are reported.
Span type is also optional, so an application that does not care can set no type
at all.

The [span type syntax](#span-type-syntax) excludes `,`, keeping it available as a
list separator. If multiple types turn out to be necessary, a future change can
define comma-separated values without breaking any conforming span type.

[Appendix A](#appendix-a-overlapping-definitions-in-practice) walks through the
usual candidates: the AWS SDK, Elasticsearch, and a function invoked over HTTP.

### Alternative 2: Attribute instead of a top-level field

Span type could be a regular attribute (for example `otel.span.type`), needing no
protocol change and working with today's SDKs.

Rejected for the same reasons event name stopped being an attribute:

- It is metadata identifying the record, not data describing it.
- As an attribute it is subject to attribute limits and can be dropped or
  rewritten by processors that have no idea it is load-bearing.
- It is inconsistent with metric name, event name, and entity type.
- A top-level field makes routing, filtering, and indexing on it cheaper than
  scanning the attribute list.

There is direct precedent: `event.name` started as an attribute and was promoted
to a top-level field:
[spec#4320](https://github.com/open-telemetry/opentelemetry-specification/pull/4320),
[proto#600](https://github.com/open-telemetry/opentelemetry-proto/pull/600),
stabilized in [proto#643](https://github.com/open-telemetry/opentelemetry-proto/pull/643).
Spans have not shipped this yet; there is no reason to repeat the detour.

### Alternative 3: Instrumentation scope attribute

Lowest data volume: put the identity on the scope
([semconv#2055](https://github.com/open-telemetry/semantic-conventions/issues/2055),
option 1). Rejected: one instrumentation library emits many span types (the
messaging conventions alone define six), so this forces a tracer per span type,
and the identity belongs to the span, not to the code that created it.

### Alternative 4: Category only

[spec#1161](https://github.com/open-telemetry/opentelemetry-specification/issues/1161)
proposes a coarse `database` / `http` / `messaging` / `rpc` / `faas` category.
Too coarse for validation and codegen: it cannot distinguish
`messaging.producer.send` from `messaging.consumer.process`. A category can be
derived from the span type namespace later, and is out of scope here.

## Prior art

Elastic APM has `span.type` and `span.subtype` and uses them for span icons and
breakdown charts.

Dash0 defines [`dash0.span.type`][dash0-semconv] in its own semantic
conventions. It is a single string with coarse values (`http`, `db`, `rpc`,
`messaging`), assigned at ingestion time by rules over OpenTelemetry semantic
conventions.

[OpenInference](https://github.com/Arize-ai/openinference/blob/main/spec/semantic_conventions.md#span-kinds)
requires `openinference.span.kind` on every span (`LLM`, `CHAIN`, `RETRIEVER`,
`TOOL`, `AGENT`, ...) and its backends dispatch rendering and evaluation on it.
It is span type under another name, implemented as an attribute because that was
the only option available. Its naming collision with OTel `SpanKind` argues for
OpenTelemetry defining this property itself rather than leaving every ecosystem
to invent it.

## Open questions

- **Identifying refinements.** Still in design, see
  [weaver#1643](https://github.com/open-telemetry/weaver/pull/1643). Whatever the
  mechanism turns out to be, it SHOULD NOT be mixed into span type in OTLP: one
  definition can have tens of refinements (every HTTP client library could be
  documented as a refinement of `http.client.request`, each with its own
  caveats). Span type is needed regardless of how this is solved.
- **Out-of-process instrumentation.** eBPF probes and proxies or gateways see
  requests and responses on the wire. From their vantage point a database span
  has the same scope as an HTTP client span, which is quite different from a
  database span produced in-process over a client library API: it excludes
  connection acquisition, retries, deserialization errors and delays, and result
  iteration. Reusing
  `db.client.call` for both would put two different measurements under one type,
  so these instrumentation points likely need their own definitions for database,
  messaging, GenAI, and similar domains.

## Prototypes

- API/SDK prototype (creation-time parameter, readable span getter, sampler
  input) plus the corresponding proto change:
  - [Python](https://github.com/open-telemetry/opentelemetry-python/pull/5464)

- A [live check run][weaver-pr] resolving spans to definitions by type instead of
  [hand-written heuristics][genai-rego].

## Appendix A: overlapping definitions in practice

A few natural candidates for a blended identity. In all of them the two
definitions differ in span name, in the convention followed, and, most
importantly, in scope.

### AWS SDK and HTTP client

An AWS SDK span carries HTTP attributes, so it looks like a candidate for a
blended identity:

| | AWS SDK span | HTTP client span |
| --- | --- | --- |
| Span name | `{Service}.{Operation}`, for example `S3.GetObject` | `{method}`, for example `GET` |
| Scope | one AWS operation | one HTTP request |
| Failure means | the operation failed after all attempts | this request failed |

Scope is the important difference. One SDK call can produce several HTTP
requests: credential lookups, redirects, retries, and for parallel downloads,
several at once.

```text
CLIENT  S3.download                       |==================================|
CLIENT    GET credentials (200)            |==|
CLIENT    GET part 1 (200)                     |============|
CLIENT    GET part 2 (500)                     |=====|
CLIENT    GET part 2, retry (200)                    |==========|
CLIENT    GET part 3 (200)                     |==================|
```

There is no single HTTP request to attach a second identity to: some run in
parallel, some are retries of each other, and the credentials call does not go to
the same service at all. The [instrumentation in Java][aws-sdk-java] even has an
[option][aws-sdk-option] to record the error of each individual HTTP request as
an event on the SDK span, because the mapping is one to many.

AWS is just an example. The same applies to Azure and GCP SDKs.

### Elasticsearch and HTTP client

The [Elasticsearch REST client instrumentation in Java][es-java] sets almost
exactly the HTTP client attribute set, plus `db.system.name`. On attributes alone
it looks like an HTTP client span. It is not:

| | Elasticsearch span | HTTP client span |
| --- | --- | --- |
| Span name | the endpoint name, for example `search` | `{method}`, for example `POST` |
| Scope | one logical Elasticsearch request | one HTTP request to one node |
| Failure means | the request failed on every node tried | this request failed |

The Elasticsearch Java API client ships its own OpenTelemetry instrumentation and
keeps the layers apart on purpose. Per its [documentation][es-otel], it emits one
span per logical request and expects HTTP spans from auto-instrumentation to nest
underneath, which is what makes node round-robin and retries visible:

> In addition to the logical Elasticsearch client requests, spans will be
> captured for the physical HTTP requests emitted by the client.

### FaaS and HTTP server

This one is the good case for a merge. A function with an HTTP trigger and the
HTTP server request around it measure close enough to the same thing, and only
one needs to report, since HTTP server auto-instrumentation can be suppressed or
turned off inside the function app.

It still is not a union of two definitions. The Lambda conventions already spell
out how to reconcile them ([aws-lambda.md][faas-lambda]): where the span name and
`http.route` come from, that `faas.trigger` is `http`, and which HTTP attributes
come from the proxy request event. That is a new definition with its own rules,
not "set both". And it is not what instrumentations do.

The Java [`aws-lambda-events`][faas-java] span is not a valid HTTP server span:
the required `url.path` and `url.scheme` are missing, and `http.route` is not set
even though API Gateway provides it.

Assuming a blended span is the superset of both definitions does not survive
contact with what instrumentations actually emit.

[aws-sdk-java]: https://github.com/open-telemetry/opentelemetry-java-instrumentation/blob/main/docs/instrumentation-list.yaml
[aws-sdk-option]: https://github.com/open-telemetry/opentelemetry-java-instrumentation/blob/main/instrumentation/aws-sdk/aws-sdk-2.2/metadata.yaml
[dash0-semconv]: https://github.com/dash0hq/dash0-semantic-conventions/blob/main/model/registry/span-attributes.yaml
[es-java]: https://github.com/open-telemetry/opentelemetry-java-instrumentation/tree/main/instrumentation/elasticsearch
[es-otel]: https://www.elastic.co/docs/reference/elasticsearch/clients/java/setup/opentelemetry
[faas-lambda]: https://github.com/open-telemetry/semantic-conventions/blob/main/docs/faas/aws-lambda.md#api-gateway
[faas-java]: https://github.com/open-telemetry/opentelemetry-java-instrumentation/tree/main/instrumentation/aws-lambda/aws-lambda-events-2.2
[live check]: https://github.com/open-telemetry/weaver/blob/main/crates/weaver_live_check/README.md
[spanmetrics connector]: https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/connector/spanmetricsconnector
[weaver-pr]: https://github.com/open-telemetry/weaver/pull/1648
[genai-rego]: https://github.com/open-telemetry/opentelemetry-python-genai/blob/main/policies/genai_span_validation.rego
