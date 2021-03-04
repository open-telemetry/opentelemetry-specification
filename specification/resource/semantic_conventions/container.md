# Container

**Status**: [Experimental](../../document-status.md)

**type:** `container`

**Description:** A container instance.

<!-- semconv container -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `container.name` | string | Container name. | `opentelemetry-autoconf` | No |
| `container.id` | string | Container ID. Usually a UUID, as for example used to [identify Docker containers](https://docs.docker.com/engine/reference/run/#container-identification). The UUID might be abbreviated. | `a3bf90e006b2` | No |
| `container.runtime` | string | The container runtime managing this container. | `docker`; `containerd`; `rkt` | No |
| `container.image.name` | string | Name of the image the container was built on. | `gcr.io/opentelemetry/operator` | No |
| `container.image.tag` | string | Container image tag. | `0.1` | No |
<!-- endsemconv -->
