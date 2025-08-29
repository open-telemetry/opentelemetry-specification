<!--- Hugo front matter used to generate the website version of this page:
path_base_for_github_subdir:
  from: tmp/otel/specification/entities/_index.md
  to: entities/README.md
--->

# Entities

 <details>
 <summary>Table of Contents</summary>

<!-- toc -->

- [Overview](#overview)
- [Specifications](#specifications)

<!-- tocstop -->

</details>

## Overview

Entity represents an object of interest associated with produced telemetry:
traces, metrics, logs, profiles etc.

Entities can be instantiated through two complementary approaches:

1. **Pull-based Model**: Entities discover themselves from the current environment by examining the runtime context, system properties, metadata services, and other available sources of entity information.

2. **Push-based Model**: Entities are explicitly provided from external sources, typically through environment variables or configuration. This approach allows entity information to be propagated across process boundaries. See [Entity Propagation](./entity-propagation.md) for more details.

## Specifications

- [Data Model](./data-model.md)
- [Entity Propagation](./entity-propagation.md) - Describes the push-based model for entity instantiation
