# Telemetry Schema Evolution for Efficient Consumption

> This document is in progress; refer to PR TBD discussions for the latest updates.
> 
----
**Author(s)**: 
* [Bartek Płotka, Google](https://www.bwplotka.dev/)
* [Josh Suereth, Google](https://github.com/jsuereth)
* [Dinesh Gurumurthy, Datadog](https://github.com/dineshg13)
* [Laurent Quérel, F5](https://github.com/lquerel)
* <active co-authors/contributors welcome!>

**Related**: 
[Spec Issue #4427](https://github.com/open-telemetry/opentelemetry-specification/issues/4427), [Weaver Issue #612](https://github.com/open-telemetry/weaver/issues/612), [Weaver Issue #450](https://github.com/open-telemetry/weaver/issues/450), [OTEP-0152][otep-0152], [OTEP 0243](https://github.com/open-telemetry/opentelemetry-specification/blob/main/oteps/0243-app-telemetry-schema-vision-roadmap.md), [Prometheus Proposal][prom-proposal], [KubeConEU 2025 Talk][kubecon-talk]. 

> **TL;DR**: We propose the next evolution of the [Telemetry Schema (OTEP-0152)][otep-0152] that enables an **efficient** consumption of the Telemetry schema pieces for the emerging collection and backend use cases. As a case study, we demonstrate how those changes will effectively enable:
> 
> * Ingestion layers to handle schema changes on the fly e.g.:
>   * *OpenTelemetry Collector Schema Processor* with "versioned write" capability.
> * Backends to [ultimately handle schema changes][prom-proposal] on the query layer, e.g.: 
>   * *Prometheus* with [a PromQL "versioned read" capability][prom-prototype].
>   * *???* logging/tracing backend with "version read" capability to prove this OTEP? Help wanted!
> * "Traditionally schemaless" ecosystems to adopt telemetry "schematization" with all its benefits, e.g.:
>   * *[Prometheus metrics](https://github.com/prometheus/prometheus/issues/16428)* which historically were schemaless.

Before reading, we recommend familiarizing with [the attached glossary](#glossary) used in this document.

## Motivation

Long story short, it's challenging for the end-users to effectively **organize their observability data**, because the telemetry ecosystem is increasingly vast and rich.
 
To start solving this, OpenTelemetry community [established the telemetry semantic convention](https://opentelemetry.io/docs/specs/semconv/) to unify the telemetry pieces into "one representation". Accompanied [Telemetry Schema (OTEP-152) was specified to start the discussion on sustainability of that schema definitions (e.g. changes over time)](https://github.com/open-telemetry/opentelemetry-specification/blob/main/oteps/0152-telemetry-schemas.md#motivation). Specifically OTEP-152 defines [a public YAML Schema File with all the telemetry transformations between 1.0 and current version](https://github.com/open-telemetry/semantic-conventions/blob/main/schemas/1.32.0). To connect telemetry on the wire (or in storage) to their schema a [Schema URL](https://github.com/open-telemetry/opentelemetry-specification/blob/main/oteps/0152-telemetry-schemas.md#schema-url) "link" was defined, pointing to that [schema file](https://github.com/open-telemetry/semantic-conventions/blob/main/schemas/1.32.0). Finally, the [Weaver](https://github.com/open-telemetry/weaver) project was established to consolidate with various schema operations (e.g.: validation, generation of schema file, code, documentation).

While it has been proven to be a great start, the Telemetry Schema [has known limitations](#current-limitations), surfaced by the lack of the adopted, backend and tools that would consume and utilize the Telemetry Schema File and Schema URL. As a result, it's still hard for end-users to adopt and maintain OpenTelemetry schemas and enjoy many **incredible** benefits like generative instrumentation and documentation, consistency and stability of telemetry consumption, signal correlations and more.

This OTEP proposes the next evolution of Telemetry Schema, beyond a single YAML file, based on [the PromQL/Prometheus Schema Changes](#prometheus-case-study) prototype using OpenTelemetry Schema (showcased in the [KubeCon Talk][kubecon-talk], and other experiments.

### Current Limitations

Let's enumerate a few high level limitations we could improve to enable efficient schema artifacts consumption:

* The Schema File referenced by the Schema URL:
  * **No link to the Schema Definitions**. Schema File is only focused on transformations. It's not specified how to get from the Schema URL to the Schema Definition (OTEP-0152 [out-of-scope](https://github.com/open-telemetry/opentelemetry-specification/blob/main/oteps/0152-telemetry-schemas.md#what-is-out-of-scope)). This limits the ability for the ecosystem to experiment, innovate and extend schema tooling capabilities. We will always hit some limits of the generated artifacts we establish. Surfacing the raw definitions (source of truth) will mitigate this.
  * **Current transformation format is limited** (OTEP-0152 [out-of-scope](https://github.com/open-telemetry/opentelemetry-specification/blob/main/oteps/0152-telemetry-schemas.md#what-is-out-of-scope)). On the example of the metric signal, it has been proven that more than the metric name can be auto-transformed without loosing any semantic information e.g. changes like metric unit, value, attribute tags or even enum values (see [demo][prom-prototype]).
  * **Scalability limits**. There's a strong need to split this file into smaller artifacts to support large number of versions, changes, signals and attributes.
  * **Future compatibility**. There's no notion of the "latest" schema version, required for consumption layers to translate certain telemetry schema version to future variants.
* The Schema Definition:
  * **No official, versioned specification** for the schema definitions (schema definition seems to be internally described by the [weaver spec][weaver-schema-def]). The source of every schema transformation or any other artifact starts with the schema definition. Ideally we have that YAML format and semantics well-defined and versioned--if we want wider ecosystem to define their telemetry in similar fashion.
  * **No reliable "semantic identification"**. It's not trivial to represent and auto-generate rich, reliable and efficient transformations out of the schema definitions, without "semantic connection". The current schema syntax offers the [`deprecated` field with the `rename_to` field](https://github.com/open-telemetry/weaver/blob/main/schemas/semconv-syntax.md#:~:text=deprecated%20%3A%3A%3D%20renamed%20renamed_to%20%5Bnote%5D%0A%20%20%20%20%20%20%20%20%20%20%20%7C%20%20%20obsoleted%20%5Bnote%5D%0A%20%20%20%20%20%20%20%20%20%20%20%7C%20%20%20uncategorized%20%5Bnote%5D) which not only limits what transformations one could do (as mentioned above), but also connect elements by "name" which:
    * Creates too soft link between "semantically identical" telemetry definitions, causing consumption in-efficiencies. For example, connecting telemetry pieces name and schema URL with a certain definition and all backwards and forward "variants".
    * Prevents transformations that change e.g. metric attribute without changing metric name.
  
## Goals

In general, the goal is to **enable practical and efficient consumption of the key Telemetry Schema Artifacts**.

Consumption use cases in the current scope:

* **Link to Schema Definitions**: Ability to access the current _definitions_ instead of only transformations (e.g. for extensibility, rich generative tooling, GenAI tools, etc.)
* **Version Write**: Ability to version the telemetry access on write APIs (e.g. for schema "ABC" auto-translate all the related attributes to a known version 1.2.0).
* **Versioned Read**: Ability to version the telemetry access on read APIs (e.g. pin selected metric to a "ABC" schema and 1.2.0 version on PromQL, so backend can fetch previous and new versions and show as 1.2.0 version).
* (lower priority) **Aliasing**: Ability to have two "current" telemetry schema definitions of the same semantic information to support alternative naming conventions or preferences.

Practical and efficient quality means:

* It's practical to _connect_ the telemetry in the storage/OTLP with the related definition, version and schema artifacts (e.g. transformations).
* It's practical to _connect_ the changed telemetry definitions (across versions) to a single "semantic" information.
* It's practical to _find and apply_ the related transformations for each telemetry definition and version.
* Basic transformations are supported e.g. changes like metric name, unit, value, attribute tags, enum values.
* It's practical to ensure further schema evolution (e.g. new transformations) does not break certain backend capabilities?

## Out of Scope

* Handle transformations that can't be trivially auto-translated or complex transformations that join or split attributes (in theory possible in future). 
* Defining anything that does not have a practical implementation/consumption in the OSS.

## Proposal

> @bwplotka: This is a starting point. Feedback/contributions/changes/researches/prototypes welcome! There are many ways of solving this!_

Generally, we propose the following high level changes:

1. Schema Definition: Create an official specification for the Schema Definition files (starting with what is now used in [the SemConv/weaver][weaver-schema-def]).
2. Schema Definition Changes: Establish strict format for making schema changes while preserving the same "semantic" information. Notably, the Schema Definition `id` field format that enables **semantic identification** of the elements and new `deprecated` syntax.
3. Schema: Establish way for Schema URL to link to the specific version of the raw schema definitions.
4. Schema: Establish way for Schema URL to link to the **latest** schema artifacts and definitions.
5. Schema Changes: Establish the efficient transformation format (potentially per backend, potentially on-demand generated?)
6. Schema Changes: (Best effort) Establish new Schema ID URL format for the efficient lookup from telemetry representation to telemetry definition ID.
7. Schema Web Security: We need mechanisms for ensuring schema URL resources integrity and security (e.g. checksums, auth, caching, proxying practices)

Further sections explain all changes in details (TBD: Help wanted!):

### Official Schema Definition Specification

> @bwplotka: To be motivated, self-explanatory (: 
> Generally, we really need a way to agree on a single language for defining our telemetry pieces in. 
> In practice, while painful, we could do breaking changes to Schema File, transformation languages, etc, but it's critically important to not change definition format (and if we change, have migration process).
> This is because everything else could be generated from definitions, but definitions is designed to be created and carefully agree among humans.

### Schema Definition ID Format

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

### Schema URL allow reaching multiple Schema artifacts (definitions, latest, other pieces)

> @bwplotka: To be discussed but my idea was to expand URL to have a known URL paths for various Schema artifacts. In fact
> this generally could end up as a stable HTTP API which could be a great result out of this OTEP.
> 
> For example for the Schema API idea, given the "http[s]://server[:port]/path/<version>" Schema URL, consumers could assume `http[s]://server[:port]/path/` is the base URL to some "Schema API".
> 
> * `http[s]://server[:port]/path/<version (starting by number)>` returns Schema File for the compatibility.
> * `http[s]://server[:port]/path/v1/latest` for the latest schema version.
> * `http[s]://server[:port]/path/v1/.well-known` for [the API/resources sitemap](https://en.wikipedia.org/wiki/Well-known_URI).
> * `http[s]://server[:port]/path/v1/changes?filter=<signal or semantic ID>&format=<transformation format>` for the transformation and elements of the choice.
> * `http[s]://server[:port]/path/v1/definitions?filter=<...>&version=<version or latest>` for the Schema definitions.
> * etc..
>
> If we follow this API route, we need to establish process for HTTP codes etc, which would be quite helpful. 
> 
> The alternative is to keep the Schema URL to point to plain text-based resources with PATH parameters which is also possible e.g.
>
> * `http[s]://server[:port]/path/<version>` returns Schema File for the compatibility.
> * `http[s]://server[:port]/path/latest` for the latest schema version.
> * `http[s]://server[:port]/path/v1/.well-known` for [the API/resources sitemap](https://en.wikipedia.org/wiki/Well-known_URI).
> * `http[s]://server[:port]/path/v1/changes/<signal>/<transformation format>` for the transformation and elements of the choice.
> * `http[s]://server[:port]/path/v1/definitions?filter=<...>&version=<version or latest>` for the Schema definitions.
> * etc..
> 
> The generic file based URL is less extensible (e.g. dynamic parameters), robust and secure, but serving those pieces is dead simple.
> 
> Requires discussion to feel the group sentiment where to go here.

### Efficient Schema Changes/Transformation Format

> @bwplotka: To be discussed but my idea was to be able to publish multiple transformation languages, as I believe there is no single one that will
> work best for all use cases. For example for Prometheus PromQL layer, one pragmatic and efficient format would be something like this, grouped
> by the [semantic ID](#schema-definition-id-format):

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

> @bwplotka: This file could be auto-generated on demand by Prometheus or hosted in the Schema registry and referenced by e.g. Schema URL/API like `http[s]://server[:port]/path/changes?filter=type:metric&format=promql`
> Other formats e.g. the current OTEP-0152 one and OTTL could be a good idea to publish as well, given their own benefits.

### Schema ID URL Optimization

> @bwplotka: To be explained, but if we follow the [Semantic ID](#schema-definition-id-format) idea, we could establish something like Schema ID URL and attach that to our telemetry (instead or on top of the Schema URL).
> For example with the format like `http[s]://server[:port]/path#<semantic-ID`. The motivation is efficiency. For the consumers knowing the semantic ID offers reach capabilities to index the telemetry by schema and semantic ID. This information is the also incredible useful to
> [fast lookup the related transformations](#efficient-schema-changestransformation-format).
> 
> Without Schema ID URL, consumption layers would need to build mappings from telemetry names to ID/semantic ID as we did in Prometheus prototype ([ids.yaml](https://github.com/bwplotka/metric-rename-demo/blob/main/my-org/semconv/ids.yaml)).
> With SchemaID the PromQL "versioned-read" could look as follows:

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

### Security Considerations

All Schema pieces are designed to be stored and access from the remote sources.
 
> @bwplotka: TBD security considerations for this.

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

## Alternatives

### Alternative Transformation Formats/Languages

> TBD: Explore alternative formats, why not purely OTTL, any query language or anything else!

## Future Possibilities

### Advanced transformations

> TBD: Explain and discuss what could be added in future -- e.g. splitting or merging attributes could be possible.

## Open questions

1. What about "almost" semantically identical schema changes? For example, there might be a telemetry piece that was capturing latency of Go garbage collection doing X and Y. In the next Go version, runtime loose ability to track Y but enables Z, so producers have to switch to a telemetry piece that measures X and Z. In practice, the majority of users would NOT notice a difference, but technically this should be another telemetry piece and out of scope of this OTEP. Should we enable some process that allows "close enough semantic changes"?
2. Is it possible for Telemetry Schema spec to define a single transformation format that would work for **every** backend and translation logic? E.g. in Prometheus and PromQL you could handle some type changes (!) or advanced attribute changes like label splits/merges, but what if that's not possible for e.g. vendor? What if it's not possible for a certain version of backend? Should transformation formats be owned and maintained by each backend instead?
3. Feedback from the KubeCon talk audience: Does Schema URL version need to use semantic versioning? One perspective is that all changes are either breaking or non-breaking (e.g. description?).

## Glossary

* **Schema**: Generally it means the shape of your telemetry "attributes", e.g.: tracing span names, logging fields, metric name, type, unit, metric labels etc.
* **Schema Definition**: Place where you describe the shape of your telemetry, the source of truth.
* **Schema File**: As per OTEP-0152, the versioned, single file with schema changes transformations.
* **Schema URL**: As per OTEP-0152, the URL where the Schema File can be found, ideally provided by the telemetry pieces to reference their schema.
* **Schema Pieces/Artifacts**: Generally, all the resources related to telemetry schemas e.g. definitions, generated code, documentation, transformations etc.
* **Telemetry Attribute Identity**: Piece of information that allows to identify a unique telemetry attribute (e.g. metric, span or metric tag).
* **Telemetry Attribute Semantic Identity**: Piece of information that allows to identify a group of the telemetry attributes that represent the same semantic information (e.g. span that traces the stop-the-word event in the Go garbage collection).

[weaver-schema-def]: https://github.com/open-telemetry/weaver/blob/main/schemas/semconv-syntax.md
[prom-proposal]: https://docs.google.com/document/d/14y4wdZdRMC676qPLDqBQZfaCA6Dog_3ukzmjLOgAL-k/edit?tab=t.0#heading=h.2bo9sxs50as
[kubecon-talk]: https://www.youtube.com/watch?v=Rw4c7lmdyFs
[prom-prototype]: https://youtu.be/md2QBPkUoe0
[otep-0152]: https://github.com/open-telemetry/opentelemetry-specification/blob/main/oteps/0152-telemetry-schemas.md
