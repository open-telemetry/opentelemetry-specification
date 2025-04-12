<!--- Hugo front matter used to generate the website version of this page:
path_base_for_github_subdir:
  from: tmp/otel/specification/resource/_index.md
  to: resource/README.md
--->

# Resource

 <details>
 <summary>Table of Contents</summary>

<!-- toc -->

- [Overview](#overview)
  * [Identity](#identity)
  * [Navigation](#navigation)
  * [Telescoping](#telescoping)
- [Specifications](#specifications)

<!-- tocstop -->

</details>

## Overview

A Resource is a representation of the entity producing telemetry.
Within OpenTelemetry, all signals are associated with a Resource, enabling
contextual correlation of data from the same source.  For example, if I see
a high latency in a span I need to check the metrics for the same entity that
produced that Span during the time when the latency was observed.

Resource provides two important aspects for observability:

- It MUST identify an entity that is producing telemetry.
- It SHOULD allow users to determine where that entity resides within their infrastructure.

### Identity

Resource provides a natural way to understand "what" produced an effect and
evaluate other signals of that same source. This is done through attaching the
same set of identifying attributes on all telemetry produced in an
OpenTelemetry SDK.

Resource identity provides a natural pivot point for observability signals, a
key type of correlation in OpenTelemetry.

### Navigation

Implicit in the design of Resource and attributes is ensuring users are able to
navigate their infrastructure, tools, UIs, etc. to find the *same* entity that
telemetry is reporting against.  For example, in practice we could see Resource
including more than on entity, like:

- A process
- A container
- A kubernetes pod name
- A namespace
- A deployment

By including identifying attributes of each of these, we can help users navigate
through their `kubectl` or Kubernetes UIs to find the specific process
generating telemetry.   This is as important as being able to uniquely identify
one process from another.

> Aside: Observability signals SHOULD be actionable.  Knowing a process is
> struggling is not as useful as being able to scale up a deployment to take
> load off the struggling process.

If the only thing important to Resource was identity, we could simply use UUIDs.
However, this would rely on some other, easily accessible, system to provide
human-friendly understanding for these UUIDs. OpenTelemetry provides a model
where a full UUID-only solution could be chosen, but defaults to a *blended*
approach, where resource provides both Identity and Navigation.

This leads to the next concept: Telescoping identity to the needs of a system.

### Telescoping

Within OpenTelemetry, we want to give users the flexibility to decide what
information needs to be sent *with* observability signals and what information
can be later joined.  We call this "telescoping identity" where users can decide
how *small* or *large* the size of an OpenTelemetry resource will be on the wire
(and correspondingly, how large data points are when stored, depending on
storage solution).

For example, in the extreme, OpenTelemery could synthesize a UUID for every
system which produces telemetry.  All identifying attributes for Resource and
Entity could be sent via a side channel with known relationships to this UUID.
While this would optimise the runtime generation and sending of telemetry, it
comes at the cost of downstream storage systems needing to join data back
together either at ingestion time or query time. For high performance use cases,
e.g. alerting, these joins can be expensive.

In practice, users control Resource identity via the configuration of Resource
Detection within SDKs and the collector. Users wishing for minimal identity will
limit their resource detection just to a `service.instance.id`, for example.
Some users highly customize resource detection with many concepts being appended.

## Specifications

- [Data Model](./data-model.md)
- [Resource SDK](./sdk.md)
