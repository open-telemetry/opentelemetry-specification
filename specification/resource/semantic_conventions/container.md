# Container

**type:** `container`

**Description:** A container instance.

| Attribute  | Description  | Example  |
|---|---|---|
| container.name | Container name. | `opentelemetry-autoconf` |
| container.id | Container id. Usually a UUID, as for example used to [identify Docker containers][]. The UUID might be abbreviated. | `a3bf90e006b2` |
| container.image.name | Name of the image the container was built on. | `gcr.io/opentelemetry/operator` |
| container.image.tag | Container image tag. | `0.1` |

[identify Docker containers]: https://docs.docker.com/engine/reference/run/#container-identification
