# Span type

Introduce a `type` property on spans that identifies the semantic convention
definition a span follows, making spans identifiable the same way metrics,
events, and entities already are.

## Motivation

There is no reliable way to tell which semantic convention a span in a stream of
spans follows. This limits the ability to query, generate, transform, aggregate,
or visualize spans, and it blocks validation: it is not possible to map a span
received over OTLP to the semantic convention it should follow.

Weaver [live check], collector schema transformation, and backend-side
conformance checking all need to resolve an observed span to its definition
before they can say anything about it. Today they can only apply heuristics that
are wrong by construction for multi-span conventions.

Span-to-metrics pipelines have the same gap. They aggregate by span name today,
which regularly explodes in cardinality because span names are per-instance by
design, and they cannot tell which metric a span should contribute to without
convention-specific rules. Span type gives such pipelines a low-cardinality
dimension to group by, and a stable key to map a span onto a metric name.

Related issues:
[spec#4733](https://github.com/open-telemetry/opentelemetry-specification/issues/4733),
[semconv#2055](https://github.com/open-telemetry/semantic-conventions/issues/2055),
[spec#531](https://github.com/open-telemetry/opentelemetry-specification/issues/531),
[spec#1161](https://github.com/open-telemetry/opentelemetry-specification/issues/1161).

### Identity today

Historically the problem is solved by defining a required attribute per
convention area and using its presence as the signal that the span follows that
convention: `db.system.name`, `http.request.method`, `messaging.system`,
`rpc.system`, `gen_ai.provider.name`, `faas.trigger`,
`feature_flag.provider.name`, and so on.

This does not work:

- Every convention has to define and maintain such an attribute, and consumers
  have to know all of them up front.
- Conventions define more than one span each, so the marker attribute only
  narrows a span down to an area, not to a definition. Further disambiguation
  needs convention-specific heuristics, and in the general case is impossible.
- Third-party (non-OTel) conventions have no way to participate at all.
- Span kind does not narrow it down either. Deleting a message and creating a
  queue are both `CLIENT` messaging spans, but they are structurally different:
  different attributes, different span name rules, different error criteria.

The scale of the problem is not hypothetical. At the time of writing:

| Registry | Span definitions |
| --- | --- |
| [semantic-conventions](https://github.com/open-telemetry/semantic-conventions) | 64 |
| [semantic-conventions-genai](https://github.com/open-telemetry/semantic-conventions-genai) | 12 |

76 span definitions today, and both registries keep growing. A consumer that
wants to classify them has to reimplement, and keep in sync, the full heuristic
tree.

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
- GenAI uses `gen_ai.operation.name` for the same purpose, but there the mapping
  is not 1:1: `chat`, `generate_content`, and `text_completion` all describe the
  same `gen_ai.inference.client` span definition, and more values keep arriving
  (for example
  [semconv-genai#353](https://github.com/open-telemetry/semantic-conventions-genai/pull/353)
  adds `fetch_response`, which is a non-inference operation that must *not* be
  mapped onto the inference span).
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
| Event | event name (top-level `event_name` field) |
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

Span type is a string. Values are owned by whoever defines the
convention: OpenTelemetry semantic conventions, or a third party. Values SHOULD
follow `{area}.{kind}.{domain-specific-name}`, for example
`messaging.producer.send`, `gen_ai.client.inference`, `http.server.request`, so
that they do not collide, and so that a prefix can be used for coarse grouping by
area and by kind.

Spans without a type are valid and MUST be accepted. A missing type means "this
span does not follow a known definition", which is true for all existing spans.

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
identifiable for querying or validation, and that is fine: those spans do not set
a span type.

### Refinements keep the parent span identity

Semantic conventions specialize definitions for specific technologies through
refinements. A refinement **shares the span type of the definition it refines**.
It may:

- narrow requirement levels,
- add non-required attributes,
- add examples, notes, and better guidance on how to populate attributes,
- specify a more precise span name format,

but it MUST NOT change the identity in an incompatible way (for example,
downgrade required attributes, or change stability or span kind). A consumer that
only understands `messaging.producer.send` handles an SQS span correctly; a
consumer that also knows about SQS can use the extra attributes.

Span refinements are not identifiable over OTLP. We expect to solve this within
semantic conventions, without new OTLP properties, by pinning attribute values on
refinements so a refinement can be recognized from the span's attributes
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
- Span type is immutable after span creation. Like `SpanKind`, it determines what
  the span *is*; it cannot become something else halfway through.
- The API does not validate the value.

```diff
 class Tracer:
     def start_span(
         self,
         name: str,
         context: Context | None = None,
         kind: SpanKind = SpanKind.INTERNAL,
         attributes: Attributes = None,
         links: Links = None,
         start_time: int | None = None,
         record_exception: bool = True,
         set_status_on_exception: bool = True,
+        span_type: str | None = None,
     ) -> Span: ...
```

Instrumentations that follow a semantic convention SHOULD set the span type to
the type of the definition they implement.

```diff
 with tracer.start_as_current_span(
     f"chat {model}",
     kind=SpanKind.CLIENT,
+    span_type="gen_ai.client.inference",
     attributes={"gen_ai.operation.name": "chat"},
 ) as span:
     ...
```

### SDK

- Span type becomes a sampler input, next to name and `SpanKind`, so sampling
  rules can match on it without matching on attributes. It is added as an
  optional parameter, so existing `Sampler` implementations keep working
  unchanged.
- Span processors and exporters read it through
  [readable span](../specification/trace/sdk.md#additional-span-interfaces),
  which already covers everything the Span API defines. There is no setter.

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
+        span_type: str | None = None,
     ) -> SamplingResult: ...
```

```diff
 class ReadableSpan:
     @property
     def name(self) -> str: ...

     @property
     def kind(self) -> SpanKind: ...

+    # named `span_type` because `type` shadows a Python builtin;
+    # the property name is normative, the accessor name is per-language
+    @property
+    def span_type(self) -> str | None: ...
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

### Other updates

- Declarative configuration: sampler configuration that matches on span type.
- Downstream, the Collector (pdata, OTTL paths, schema processor) needs the new
  field plumbed through.
- Exporters for protocols that have no place for span type can map it to an
  attribute. If needed, we can define `otel.span.type` for that, so all such
  exporters use the same key.
- Existing instrumentations should be updated to populate it.

## Trade-offs and mitigations

- **Wire size.** One short, highly repetitive string per span. Where identity
  matters, it is already recorded today through marker attributes, which costs
  more (a key and a value, subject to attribute limits and processing). Where it
  does not matter, span type is not set and costs nothing.
- **Long migration.** SDKs, the Collector, and backends all need to add the field
  before it is useful end-to-end. Mitigation: the field is optional and additive,
  and the existing marker attributes stay in place, so nothing breaks in the
  meantime.

## Prior art and alternatives

### Attribute instead of a top-level field

Span type could be a regular attribute (for example `otel.span.type`). It needs
no protocol change and works with today's SDKs.

Rejected for the same reasons event name stopped being an attribute:

- It is metadata identifying the record, not data describing it.
- As an attribute it is subject to attribute limits and can be dropped or
  rewritten by processors that have no idea it is load-bearing.
- It is inconsistent with metric name, event name, and entity type.

There is direct precedent: `event.name` started as an attribute and was promoted
to a top-level field:
[spec#4320](https://github.com/open-telemetry/opentelemetry-specification/pull/4320),
[proto#600](https://github.com/open-telemetry/opentelemetry-proto/pull/600),
stabilized in [proto#643](https://github.com/open-telemetry/opentelemetry-proto/pull/643).
Spans have not shipped this yet; there is no reason to repeat the detour.

### Instrumentation scope attribute

Lowest data volume: put the identity on the scope
([semconv#2055](https://github.com/open-telemetry/semantic-conventions/issues/2055),
option 1). Rejected: a single instrumentation library emits many span types
(the messaging conventions alone define six), so this forces a tracer per span
type, and the identity is a property of the span, not of the code that created
it.

### Category only

[spec#1161](https://github.com/open-telemetry/opentelemetry-specification/issues/1161)
proposes a coarse `database` / `http` / `messaging` / `rpc` / `faas` category.
Too coarse for validation and codegen: it cannot distinguish
`messaging.producer.send` from `messaging.consumer.process`. A category can be
derived from the span type namespace later, and is out of scope here.

### Existing systems

Elastic APM has `span.type` and `span.subtype` and uses them for span icons and
breakdown charts.

[OpenInference](https://github.com/Arize-ai/openinference/blob/main/spec/semantic_conventions.md#span-kinds)
requires `openinference.span.kind` on every span (`LLM`, `CHAIN`, `RETRIEVER`,
`TOOL`, `AGENT`, ...) and its backends dispatch rendering and evaluation on it.
It is span type under another name, implemented as an attribute because that was
the only option available, and its naming collision with OTel `SpanKind` is a
good argument for OpenTelemetry defining this property itself rather than
leaving every ecosystem to invent it.

## Open questions

- **Identifying refinements.** Still in design, see
  [weaver#1643](https://github.com/open-telemetry/weaver/pull/1643). Whatever the
  mechanism turns out to be, it should not be mixed into span type in
  OTLP: one definition can have tens of refinements (in theory, every HTTP client
  library could be documented as a refinement of `http.client.request`, each with
  its own caveats worth documenting). Span type is needed regardless of how
  refinement identification is solved.

## Prototypes

To be added:

- One SDK prototype (creation-time parameter, readable span getter, sampler
  input) plus the corresponding proto change.
- A [live check run][weaver-pr] resolving spans to definitions by type instead of
  [hand-written heuristics][genai-rego].
- Weaver code generation producing span type constants and setting the type in
  generated instrumentation helpers
  TODO

[live check]: https://github.com/open-telemetry/weaver/blob/main/crates/weaver_live_check/README.md
[weaver-pr]: https://github.com/open-telemetry/weaver/pull/1648
[genai-rego]: https://github.com/open-telemetry/opentelemetry-python-genai/blob/main/policies/genai_span_validation.rego
