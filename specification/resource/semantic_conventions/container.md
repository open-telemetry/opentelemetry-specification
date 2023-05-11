# Container

**Status**: [Experimental](../../document-status.md)

**NOTICE** Semantic Conventions are moving to a
[new location](http://github.com/open-telemetry/semantic-conventions).

No changes to this document are allowed.

**type:** `container`

**Description:** A container instance.

<!-- semconv container -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `container.name` | string | Container name used by container runtime. | `opentelemetry-autoconf` | Recommended |
| `container.id` | string | Container ID. Usually a UUID, as for example used to [identify Docker containers](https://docs.docker.com/engine/reference/run/#container-identification). The UUID might be abbreviated. | `a3bf90e006b2` | Recommended |
| `container.runtime` | string | The container runtime managing this container. | `docker`; `containerd`; `rkt` | Recommended |
| `container.image.name` | string | Name of the image the container was built on. | `gcr.io/opentelemetry/operator` | Recommended |
| `container.image.tag` | string | Container image tag. | `0.1` | Recommended |
<!-- endsemconv -->
