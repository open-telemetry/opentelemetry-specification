# Telemetry Schema Evolution for Efficient Consumption

> This document is in progress; refer to PR TBD discussions for the latest updates.
> 
----
**Author(s)**: 
* [Bartek Płotka, Google](https://www.bwplotka.dev/)
* [Josh Suereth, Google](https://github.com/jsuereth)
* [Laurent Quérel, F5](https://github.com/lquerel)
* <active co-authors/contributors welcome!>

**Related**: 
[Spec Issue #4427](https://github.com/open-telemetry/opentelemetry-specification/issues/4427), [Weaver Issue #612](https://github.com/open-telemetry/weaver/issues/612), [Weaver Issue #450](https://github.com/open-telemetry/weaver/issues/450), [OTEP-0152][otep-0152], [OTEP 0243](https://github.com/open-telemetry/opentelemetry-specification/blob/main/oteps/0243-app-telemetry-schema-vision-roadmap.md), [Prometheus Proposal][prom-proposal], [KubeConEU 2025 Talk][kubecon-talk]. 

> **TL;DR**: We propose the next evolution of the [Telemetry Schema (OTEP-0152)][otep-0152] that enables an **efficient** consumption of the Telemetry schema pieces for the emerging collection and backend use case. As a case study, we show how those changes will practically:
> 
> * Enable ingestion to handle schema changes on write e.g.:
>  * for all telemetry in an OpenTelemetry Collector Schema Processor
> * Enable backends to [ultimately handle schema changes][prom-proposal] on a query layer, e.g.: 
>  * for metrics in Prometheus with [a powerful PromQL "versioned read" capability][prom-prototype].
>  * (Help wanted!): Anyone would like to use this evolution to try implementing "versioned read" on any logging/telemetry backend to prove this OTEP?
> * Enable ecosystems to adopt telemetry schematization with all its benefits, e.g.:
>  * [Prometheus metrics](https://github.com/prometheus/prometheus/issues/16428), which historically were schemaless.

## Motivation

Long story short, it's challenging for the end-users to effectively **organize their observability data**, because the telemetry ecosystem is increasingly vast and rich.
 
To start solving this, OpenTelemetry community [established the telemetry semantic convention](https://opentelemetry.io/docs/specs/semconv/) to unify the telemetry pieces into "one representation". Accompanied [Telemetry Schema (OTEP-152) was specified to start the discussion on sustainability of that schema definitions (e.g. changes over time)](https://github.com/open-telemetry/opentelemetry-specification/blob/main/oteps/0152-telemetry-schemas.md#motivation). Specifically OTEP-152 defines [a public YAML file with all the telemetry transformations between 1.0 and current version](https://github.com/open-telemetry/semantic-conventions/blob/main/schemas/1.32.0). To connect telemetry on the wire (or in storage) to their schema a [Schema URL](https://github.com/open-telemetry/opentelemetry-specification/blob/main/oteps/0152-telemetry-schemas.md#schema-url) "link" was defined, pointing to that [schema file](https://github.com/open-telemetry/semantic-conventions/blob/main/schemas/1.32.0). Finally, the [Weaver](https://github.com/open-telemetry/weaver) project was established to consolidate with various schema operations (e.g.: validation, generation of schema file, code, documentation).

While it has been proven to be a great start, the Telemetry Schema [has known limitations](#current-limitations), surfaced by the lack of the adopted, backend and tools that would use Telemetry Schema file and Schema URL. As a result, it's still hard for end-users to adopt and maintain OpenTelemetry schemas and enjoy many **incredible** benefits like generative instrumentation and documentation, consistency and stability of telemetry consumption, signal correlations and more.

This OTEP proposes the next evolution of Telemetry Schema, beyond a single YAML file, based on [the PromQL/Prometheus Schema Changes](#prometheus-case-study) prototype using OpenTelemetry Schema (showcased in the [KubeCon Talk][kubecon-talk].

### Current Limitations

Let's enumerate a few high level limitations we can improve to enable efficient schema artifacts consumption:

* Schema file pointed by Schema URL:
  * There is no link to the current definition (initially [out-of-scope](https://github.com/open-telemetry/opentelemetry-specification/blob/main/oteps/0152-telemetry-schemas.md#what-is-out-of-scope)). This limits the ability for the ecosystem to extend schema tooling capabilities in future (e.g. we can't predict what's efficient and needed for potential future consumption implementations).
  * Transformations are limited (initially [out-of-scope](https://github.com/open-telemetry/opentelemetry-specification/blob/main/oteps/0152-telemetry-schemas.md#what-is-out-of-scope)). Just scoping to metric signal, it has been proven that more than metric name can be auto-transformed without loosing any semantic information e.g. changes like metric name, unit, value, attribute tags, enum values (see [demo][prom-prototype]).
  * **Scalability limits**. We need to split this file into smaller artifacts to support large number of versions, changes, signals and attributes.
  * **Future compatibility**. There's no notion of the "latest" schema version, required for consumption layers to translate certain telemetry schema version to future variants.
* Schema definitions:
  * No official, versioned specification for the schema definitions (_bwplotka: Am I wrong here? I only see a [weaver spec][weaver-schema-def]_). The source of every schema transformation or any other artifact starts with the schema definition. Ideally we have that YAML format and semantics well-defined and versioned, if we want wider ecosystem to define their telemetry in similar files.
  * No reliable "semantic identification". As a result it's not trivial to auto-generate rich and reliable transformations out of the schema definition. The current schema syntax offers the [`deprecated` field with the `rename_to` field](https://github.com/open-telemetry/weaver/blob/main/schemas/semconv-syntax.md#:~:text=deprecated%20%3A%3A%3D%20renamed%20renamed_to%20%5Bnote%5D%0A%20%20%20%20%20%20%20%20%20%20%20%7C%20%20%20obsoleted%20%5Bnote%5D%0A%20%20%20%20%20%20%20%20%20%20%20%7C%20%20%20uncategorized%20%5Bnote%5D) which not only limits what transformations one could do (as mentioned above), but also connect elements by "name" which is:
    * Creates too soft link between "semantically identical" telemetry definitions, causing consumption in-efficiencies (e.g. connecting telemetry pieces name and schema URL with a certain definition and all backwards and forward "variants").
    * Prevents changes that change e.g. metric attribute without changing metric name.
  
## Goals

In general, the goal is to enable practical and efficient consumption of the key Telemetry Schema artifacts.

Consumption use cases in the current scope:
* **Current definitions**: Ability to access the current _definitions_ instead of only transformations (e.g. for extensibility, rich generative tooling, GenAI tools, etc.)
* **Version Write**: Ability to version the telemetry access on write APIs (e.g. for schema "ABC" auto-translate all the related attributes to a known version 1.2.0).
* **Versioned Read** Ability to version the telemetry access on read APIs (e.g. pin selected metric to a "ABC" schema and 1.2.0 version on PromQL, so backend can fetch previous and new versions and show as 1.2.0 version).
* **Aliasing**: Ability to have two "current" telemetry schema definitions of the same semantic information to support alternative naming conventions or preferences.

Practical and efficient means: 
  * It's practical to _connect_ telemetry in storage/OTLP with the related definition, version and schema artifacts (e.g. transformations).
  * It's practical to _connect_ telemetry definitions (across versions) to a single "semantic" information.
  * It's practical to _find and apply_ related transformations for each telemetry definition and version.
  * Basic transformations are supported e.g. changes like metric name, unit, value, attribute tags, enum values.
  * It's practical to ensure further schema evolution (e.g. new transformations) does not break certain backend capabilities?

## Out of Scope

* Supporting transformations that can't be trivially auto-translated (e.g. the majority of type changes) or complex transformations that join or split attributes (in theory possible in future) 
* Supporting anything that does not have a practical implementation/consumption in the OSS.

## Proposal

_@bwplotka: This section is in heavy WIP, feedback welcome! There are many ways of solving this._

Generally, we propose the following high level changes:

1. Schema Definition: Create an official specification for the Schema Definition files (starting with what is now used in [the SemConv/weaver][weaver-schema-def]).
2. Schema Definition: Establish strict format for making schema changes while preserving the same "semantic" information. Notably, the Schema Definition `id` field format that enables **semantic identification** of the elements and new `deprecated` syntax.
3. Schema: Establish way for Schema URL to link to the specific version of the raw schema definitions.
4. Schema: Establish way for Schema URL to link to the **latest** schema artifacts and definitions.
5. Schema: Establish the efficient transformation format (potentially per backend, potentially on-demand generated?)
6. Schema: (Best effort) Establish Schema ID URL format for the efficient lookup from telemetry representation to telemetry definition ID.

Further section explain the above changes in details (TBD diagrams, details etc)

### 1. Official Schema Definition

TBD, self explanatory (: 

### 2. Schema Definition ID Format

The `id` field in schema definition is loosely defined. In Weaver sometimes it has to be globally unique, sometimes not (e.g. when nested for metric attribute). It seemed this field was historically only used practically by humans, not automation.

We propose to establish a strict definition of the `id` format as follows:
* Top level group `id` field MUST use a short, globally unique set of characters matching `^(?P<semantic_id>[a-z_]+)(|.(?P<revision>\d+))$` regex.
* Nested `id` field MUST use a short, locally unique set of characters matching `^(?P<nested_id>[a-z_]+)$` regex.

This format allows:

* Reliable connection for elements that share exactly the same semantic ID.
* Reliable way for consumers to go from the element unique ID to its semantic ID.
* Deprecation schema as it is now, where even "semantically convertible" change is a new element in the definition (we could challenge that too?) 

As a result we will are able to reduce the amount of data to represent useful transformations per semantic ID. The revision is then "a location" in the forward/backward chain (See [The efficient schema change format](#5-efficient-schema-changestransformation-format)).

Practical example: https://github.com/bwplotka/metric-rename-demo/blob/79c0b560b9723967c427460daa92ec3de0a3853d/my-org/semconv/registry/my-app.yaml#L3

### 3. Schema URL current definition link

TBD

### 4. Schema URL latest link

TBD

### 5. Efficient Schema Changes/Transformation Format

TBD explain

```yaml
# Version of this file.
version: 1

# changelog contains all changes made to elements with the same semantic id
# sorted from the newest to the oldest.
metrics_changelog:
  my_app_latency:
  # my_app_latency vs my_app_latency.2
  - forward:
      metric_name: my_app_latency_seconds
      unit: "{second}"
      value_promql: "value{} / 1000"
    backward:
      metric_name: my_app_latency_milliseconds
      unit: "{millisecond}"
      value_promql: "value{} * 1000"

  my_app_custom_elements:
  # my_app_custom_elements.2 vs my_app_custom_elements.3
  - forward:
      attributes:
      - tag: "my_number"
    backward:
      attributes:
      - tag: "number"
    # my_app_custom_elements vs my_app_custom_elements.2
  - forward:
      metric_name: my_app_custom_changed_elements_total
      attributes:
      - tag: "number"
      - tag: "class"
        members:
        - value: "FIRST"
        - value: "SECOND"
        - value: "OTHER"
    backward:
      metric_name: my_app_custom_elements_total
      attributes:
      - tag: "integer"
      - tag: "category"
        members:
        - value: "first"
        - value: "second"
        - value: "other" 
```

### 6. Schema ID URL Optimization

TBD explain e.g. using PromQL example:

```
 # PromQL query with special schema_url selector; pinning query to a certain schema registry and a certain metric ID (semantic-id.2):
old_metric_name{__schema_url__="https://example.com/semconv#semantic-id.2"}

# Series in storage:
older_metric_name{__schema_url__="https://example.com/semconv#semantic-id.1", instance="A"} 1
old_metric_name{__schema_url__="https://example.com/semconv#semantic-id.2", instance="B"} 2
new_metric_name{__schema_url__="https://example.com/semconv#semantic-id.3", instance="C"} 3

# Series returned:
old_metric_name{instance="A"} 1
old_metric_name{instance="B"} 2
old_metric_name{instance="C"} 3
```


## Prometheus Case Study

For the full context, see [the KubeCon EU talk][kubecon-talk] that motivates why Prometheus
ecosystem needs schema and PromQL "versioned read" to automatically handle schema changes.
See [the prototype technical details](https://docs.google.com/document/d/14y4wdZdRMC676qPLDqBQZfaCA6Dog_3ukzmjLOgAL-k/edit?tab=t.f0p1e46oa2c).

Generally [Prometheus users are looking for ways to automate schema changes and schema migrations](https://docs.google.com/document/d/14y4wdZdRMC676qPLDqBQZfaCA6Dog_3ukzmjLOgAL-k/edit?tab=t.0#heading=h.1hb3zptlu59q). To achieve a [prototype][prom-prototype] and [proposal][prom-proposal] were created to:
* Allow and encourage subset of Prometheus metrics to be defined in OpenTelemetry schema (with Prometheus or OpenTelemetry naming).
* Implement PromQL versioned read that allows "pinning" queried metrics to a certain schema and version (generally to a certain metric ID):

Notably, PromQL syntax in prototype could work as follows:

``` 
# PromQL query with special schema_url selector; pinning query to a certain schema registry and a version,
old_metric_name{__schema_url__="https://example.com/semconv/1.1.0"}

# Series in storage:
older_metric_name{__schema_url__="https://example.com/semconv/1.0.0", instance="A"} 1
old_metric_name{__schema_url__="https://example.com/semconv/1.1.0", instance="B"} 2
new_metric_name{__schema_url__="https://example.com/semconv/1.2.0", instance="C"} 3

# Series returned:
old_metric_name{instance="A"} 1
old_metric_name{instance="B"} 2
old_metric_name{instance="C"} 3
```

However, more efficient evolution is proposed, that ties schema URL to true "element" ID with a certain format:

```
# PromQL query with special schema_url selector; pinning query to a certain schema registry and a certain metric ID (semantic-id.2):
old_metric_name{__schema_url__="https://example.com/semconv#semantic-id.2"}

# Series in storage:
older_metric_name{__schema_url__="https://example.com/semconv#semantic-id.1", instance="A"} 1
old_metric_name{__schema_url__="https://example.com/semconv#semantic-id.2", instance="B"} 2
new_metric_name{__schema_url__="https://example.com/semconv#semantic-id.3", instance="C"} 3

# Series returned:
old_metric_name{instance="A"} 1
old_metric_name{instance="B"} 2
old_metric_name{instance="C"} 3
```

## Trade-offs and mitigations

* TBD

## Prior art and alternatives

* TBD

## Open questions

* Is it possible for Telemetry Schema spec to define a single transformation format that would work for **every** backend and translation logic? E.g. in Prometheus and PromQL you could handle some type changes (!) or advanced attribute changes like label splits/merges, but what if that's not possible for e.g. vendor? What if it's not possible for a certain version of backend? Should transformation formats be owned and maintained by each backend instead?
* Feedback from the KubeCon talk audience: Does Schema URL version need to use semantic versioning? One perspective is that all changes are either breaking or non-breaking (e.g. description?).

## Future possibilities

* TBD


[weaver-schema-def]: https://github.com/open-telemetry/weaver/blob/main/schemas/semconv-syntax.md
[prom-proposal]: https://docs.google.com/document/d/14y4wdZdRMC676qPLDqBQZfaCA6Dog_3ukzmjLOgAL-k/edit?tab=t.0#heading=h.2bo9sxs50as
[kubecon-talk]: https://www.youtube.com/watch?v=Rw4c7lmdyFs
[prom-prototype]: https://youtu.be/md2QBPkUoe0
[otep-0152]: https://github.com/open-telemetry/opentelemetry-specification/blob/main/oteps/0152-telemetry-schemas.md
