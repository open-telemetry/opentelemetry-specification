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
entity        := type id_attrs desc_attrs? schema_url? | ""
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

# Empty strings are allowed (leading, trailing, and consecutive semicolons are ignored)
OTEL_ENTITIES=";service{service.name=app1};;host{host.id=host-123};"
```

### Parsing Algorithm

1. Split the input string by semicolons (`;`) to get individual entity definitions
2. For each entity definition:
   a. Skip if the entity definition is empty (allows consecutive semicolons and leading/trailing semicolons)
   b. Extract the entity type (everything before the first `{`)
   c. Extract identifying attributes from `{...}` block
   d. Extract descriptive attributes from `[...]` block (if present)
   e. Extract schema URL from `@...` portion (if present)
3. Parse key-value lists using comma (`,`) as separator and equals (`=`) for assignment
4. Validate that each entity has a non-empty type and at least one identifying attribute
5. Create entity objects and associate them with the resource

### Character Encoding

All attribute values MUST be considered strings and characters outside the
`baggage-octet` range MUST be percent-encoded following the [W3C Baggage](https://www.w3.org/TR/baggage/#header-content) specification.

The reserved characters `{}[]@;,=` MUST be percent-encoded when they appear literally in attribute values:

- `{` → `%7B`
- `}` → `%7D`
- `[` → `%5B`
- `]` → `%5D`
- `@` → `%40`
- `;` → `%3B`
- `,` → `%2C`
- `=` → `%3D`

**Example:**

```bash
# Entity with reserved characters in attribute values
OTEL_ENTITIES="service{service.name=my%2Capp,service.instance.id=inst-1}[config=key%3Dvalue%5Bprod%5D]"
# Resolves to: service.name="my,app", config="key=value[prod]"
```

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
4. **Empty entity strings**: Empty strings between semicolons (including leading and trailing semicolons) SHOULD be ignored during parsing
5. **Duplicate entities**: If multiple entities of the same type with identical identifying attributes are defined, the SDK SHOULD use the last occurrence and SHOULD log a warning
6. **Invalid characters**: If unencoded reserved characters are found in attribute keys or values, the SDK SHOULD log a warning and attempt to parse the value as-is
7. **Schema URL validation**: If a schema URL is present but invalid, the SDK SHOULD log a warning and ignore the URL while processing the entity
8. **Conflicting identifying attributes**: If two entities of the same type define different values for the same identifying attribute key, the SDK SHOULD treat them as separate entities. If this results in ambiguous entity identification, the SDK SHOULD log a warning and use the last valid definition
9. **Conflicting descriptive attributes**: If two entities define different values for the same descriptive attribute key, the SDK SHOULD use the value from the last entity definition and SHOULD log a warning. The conflicting attributes SHOULD NOT be recorded for entities other than the last one
10. **Conflict with resource attributes**: If an entity attribute conflicts with a resource attribute, the SDK SHOULD log a warning and apply the conflict resolution rules defined below

### Environment Variable Conflict Resolution

When multiple environment variables define overlapping configuration, the following precedence order applies (highest to lowest precedence):

1. **Programmatic configuration**: Entities configured via SDK API take highest precedence and override all environment variable configurations
2. **OTEL_ENTITIES**: Entity definitions from this environment variable override resource attributes and other OTEL_* environment variables for the same attribute keys
3. **OTEL_SERVICE_NAME**: Takes precedence over `service.name` in `OTEL_RESOURCE_ATTRIBUTES` but is overridden by `service.name` in `OTEL_ENTITIES`
4. **Other specific OTEL_* variables**: Individual environment variables (when they exist) take precedence over equivalent attributes in `OTEL_RESOURCE_ATTRIBUTES`
5. **OTEL_RESOURCE_ATTRIBUTES**: Lowest precedence for overlapping attribute keys

**Precedence rules within OTEL_ENTITIES:**
- When the same entity type appears multiple times with identical identifying attributes, the last occurrence takes precedence

**Example of conflict resolution:**

```bash
# These environment variables:
OTEL_SERVICE_NAME="old-service-name"
OTEL_RESOURCE_ATTRIBUTES="service.name=resource-service,host.name=resource-host,custom.attr=resource-value"
OTEL_ENTITIES="service{service.name=entity-service,service.instance.id=inst-1}[service.version=1.0.0];host{host.id=host-123}[host.name=entity-host]"

# Result in:
# - Service entity with identifying attributes: {service.name=entity-service, service.instance.id=inst-1} (from OTEL_ENTITIES, overrides others)
#   and descriptive attributes: {service.version=1.0.0}
# - Host entity with identifying attributes: {host.id=host-123}
#   and descriptive attributes: {host.name=entity-host} (from OTEL_ENTITIES, overrides OTEL_RESOURCE_ATTRIBUTES)
# - Resource: remaining attributes from OTEL_RESOURCE_ATTRIBUTES that don't conflict: {custom.attr=resource-value}
```
