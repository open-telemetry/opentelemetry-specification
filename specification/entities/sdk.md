<!--- Hugo front matter used to generate the website version of this page:
linkTitle: SDK
--->

# Entities SDK

**Status**: [Development](../document-status.md)

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [Specifying entity information via an environment variable](#specifying-entity-information-via-an-environment-variable)
  * [Format Specification](#format-specification)
  * [Grammar](#grammar)
  * [Examples](#examples)
  * [Parsing Algorithm](#parsing-algorithm)
  * [Character Encoding](#character-encoding)
  * [Validation Requirements](#validation-requirements)
  * [Error Handling](#error-handling)
  * [Environment Variable Conflict Resolution](#environment-variable-conflict-resolution)
  * [Relationship to Programmatic Entity Configuration](#relationship-to-programmatic-entity-configuration)

<!-- tocstop -->

</details>

## Specifying entity information via an environment variable

The SDK MUST extract information from the `OTEL_ENTITIES` environment
variable and associate the defined entities with the resource.

The `OTEL_ENTITIES` environment variable contains a list of entities in a
compact format designed for human readability and concise representation.

### Format Specification

Each entity follows this structure:

```
type{id_key1=id_value1,id_key2=id_value2}[desc_key1=desc_value1,desc_key2=desc_value2]@schema_url
```

Where:

- `type` is the entity type (required, e.g., "service", "host", "container")
- `{...}` contains identifying attributes as comma-separated key=value pairs (required, at least one pair)
- `[...]` contains descriptive attributes as comma-separated key=value pairs (optional)
- `@schema_url` specifies the Schema URL for the entity (optional)

Multiple entities are separated by semicolons (`;`).

### Grammar

```
entities      := entity (";" entity)*
entity        := type id_attrs desc_attrs? schema_url?
type          := [a-zA-Z][a-zA-Z0-9._-]*
id_attrs      := "{" key_value_list "}"
desc_attrs    := "[" key_value_list "]"
schema_url    := "@" url_string
key_value_list := key_value ("," key_value)*
key_value     := key "=" value
key           := [a-zA-Z][a-zA-Z0-9._-]*
value         := [^{}[\]@;,=]*
url_string    := [^;]*
```

### Examples

```bash
# Single service entity
OTEL_ENTITIES="service{service.name=my-app,service.instance.id=instance-1}[service.version=1.0.0]"

# Multiple entities with schema URL
OTEL_ENTITIES="service{service.name=my-app,service.instance.id=instance-1}[service.version=1.0.0]@https://opentelemetry.io/schemas/1.21.0;host{host.id=host-123}[host.name=web-server-01]"

# Kubernetes pod entity
OTEL_ENTITIES="k8s.pod{k8s.pod.uid=pod-abc123}[k8s.pod.name=my-pod,k8s.pod.label.app=my-app]"

# Container with host (minimal descriptive attributes)
OTEL_ENTITIES="container{container.id=cont-456};host{host.id=host-789}[host.name=docker-host]"

# Minimal entity (only required fields)
OTEL_ENTITIES="service{service.name=minimal-app}"
```

### Parsing Algorithm

1. Split the input string by semicolons (`;`) to get individual entity definitions
2. For each entity definition:
   a. Extract the entity type (everything before the first `{`)
   b. Extract identifying attributes from `{...}` block
   c. Extract descriptive attributes from `[...]` block (if present)
   d. Extract schema URL from `@...` portion (if present)
3. Parse key-value lists using comma (`,`) as separator and equals (`=`) for assignment
4. Validate that each entity has a non-empty type and at least one identifying attribute
5. Create entity objects and associate them with the resource

### Character Encoding

All attribute values MUST be considered strings and characters outside the
`baggage-octet` range MUST be percent-encoded following the [W3C Baggage](https://www.w3.org/TR/baggage/#header-content) specification.

The reserved characters `{}[]@;,=` MUST be percent-encoded when used in attribute keys or values:

- `{` → `%7B`
- `}` → `%7D`
- `[` → `%5B`
- `]` → `%5D`
- `@` → `%40`
- `;` → `%3B`
- `,` → `%2C`
- `=` → `%3D`

### Validation Requirements

- Entity type MUST NOT be empty and MUST match the pattern `[a-zA-Z][a-zA-Z0-9._-]*`
- At least one identifying attribute MUST be present in the `{...}` block
- Attribute keys MUST NOT be empty and SHOULD follow OpenTelemetry semantic conventions
- Schema URL, if present, MUST be a valid URI
- Entity types SHOULD follow existing OpenTelemetry entity naming conventions (e.g., "service", "host", "container", "k8s.pod")

### Error Handling

The SDK SHOULD be resilient to malformed input and follow these error handling rules:

1. **Invalid syntax**: If the environment variable contains invalid syntax, the SDK SHOULD log a warning and ignore the malformed portions while processing valid parts
2. **Missing required fields**: If an entity is missing required fields (type or identifying attributes), the SDK SHOULD log a warning and skip that entity
3. **Empty entities list**: An empty `OTEL_ENTITIES` environment variable is valid and indicates no entities are defined
4. **Duplicate entities**: If multiple entities of the same type with identical identifying attributes are defined, the SDK SHOULD use the last occurrence and SHOULD log a warning
5. **Invalid characters**: If unencoded reserved characters are found in attribute keys or values, the SDK SHOULD log a warning and attempt to parse the value as-is
6. **Schema URL validation**: If a schema URL is present but invalid, the SDK SHOULD log a warning and ignore the URL while processing the entity
7. **Conflicting attributes between entities**: If two entities define the same identifying attribute key with different values, the SDK SHOULD log a warning and discard the conflicting entity, keeping the last valid definition
8. **Conflict with resource attributes**: If an entity attribute conflicts with a resource attribute, the SDK SHOULD log a warning and apply the conflict resolution rules defined below

### Environment Variable Conflict Resolution

When multiple environment variables define overlapping configuration, the following precedence order applies:

1. **Programmatic configuration**: Entities configured via SDK API take highest precedence
2. **OTEL_ENTITIES**: Entity definitions from this environment variable
3. **Other OTEL_* variables**: Specific environment variables like `OTEL_SERVICE_NAME`
4. **OTEL_RESOURCE_ATTRIBUTES**: Resource attributes that may conflict with entity attributes

**Example of conflict resolution:**

```bash
# These environment variables:
OTEL_SERVICE_NAME="old-service-name"
OTEL_RESOURCE_ATTRIBUTES="service.name=resource-service,host.name=resource-host,custom.attr=resource-value"
OTEL_ENTITIES="service{service.name=entity-service,service.instance.id=inst-1}[service.version=1.0.0];host{host.id=host-123}[host.name=entity-host]"

# Result in:
# - Service entity: service.name=entity-service (from OTEL_ENTITIES, overrides others)
# - Host entity: host.name=entity-host (from OTEL_ENTITIES, overrides OTEL_RESOURCE_ATTRIBUTES)
# - Resource: remaining attributes from OTEL_RESOURCE_ATTRIBUTES that don't conflict: custom.attr=resource-value
```
