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
- [Specifications](#specifications)

<!-- tocstop -->

</details>

## Overview

A Resource is an immutable representation of the entity producing telemetry.
Within OpenTelemetry, all signals are associated with a Resource, enabling
contextual correlation of data from the same source.  For example, if I see
a high latency in a span I need to check the metrics for the same entity that
produced that Span during the time when the latency was observed.

## Specifications

- [Data Model](./data-model.md)
- [Resource SDK](./sdk.md)
