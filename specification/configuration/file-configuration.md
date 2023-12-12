<!--- Hugo front matter used to generate the website version of this page:
linkTitle: File
--->

# File Configuration

**Status**: [Experimental](../document-status.md)

<!-- toc -->

- [Overview](#overview)
- [Configuration Model](#configuration-model)
  * [Stability Definition](#stability-definition)
- [Configuration file](#configuration-file)
  * [YAML file format](#yaml-file-format)
  * [Environment variable substitution](#environment-variable-substitution)
- [SDK Configuration](#sdk-configuration)
  * [In-Memory Configuration Model](#in-memory-configuration-model)
  * [Operations](#operations)
    + [Parse](#parse)
    + [Create](#create)
- [References](#references)

<!-- tocstop -->

## Overview

File configuration provides a mechanism for configuring OpenTelemetry which is
more expressive and full-featured than
the [environment variable](sdk-environment-variables.md) based scheme, and
language agnostic in a way not possible
with [programmatic configuration](sdk-configuration.md#programmatic).

File configuration defines a [Configuration Model](#configuration-model),
which can be expressed in a [configuration file](#configuration-file).
Configuration files can be validated against the Configuration Schema, and
interpreted to produce configured OpenTelemetry components.

## Configuration Model

The configuration model is defined
in [opentelemetry-configuration](https://github.com/open-telemetry/opentelemetry-configuration)
using the [JSON Schema](https://json-schema.org/).

### Stability Definition

TODO: define stability guarantees and backwards compatibility

## Configuration file

A configuration file is a serialized file-based representation of
the [Configuration Model](#configuration-model).

Configuration files SHOULD use one the following serialization formats:

### YAML file format

[YAML](https://yaml.org/spec/1.2.2/) configuration files SHOULD follow YAML spec
revision >= 1.2.

YAML configuration files MUST use file extensions `.yaml` or `.yml`.

TODO: define JSON file format once prototypes are available

### Environment variable substitution

Configuration files support environment variables substitution for references
which match the following regular expression:

```regexp
\$\{(?<ENV_NAME>[a-zA-Z_][a-zA-Z0-9_]*)}
```

The `ENV_NAME` MUST start with an alphabetic or `_` character, and is followed
by 0 or more alphanumeric or `_` characters.

For example, `${API_KEY}` is valid, while `${1API_KEY}` and `${API_$KEY}` are
invalid.

Environment variable substitution MUST only apply to scalar values. Mapping keys
are not candidates for substitution.

If a referenced environment variable is not defined, it MUST be replaced with an
empty value.

Node types MUST be interpreted after environment variable substitution takes
place. This ensures the environment string representation of boolean, integer,
or floating point fields can be properly converted to expected types.

For example, consider the following environment variables,
and [YAML](#yaml-file-format) configuration file:

```shell
export STRING_VALUE="value"
export BOOl_VALUE="true"
export INT_VALUE="1"
export FLOAT_VALUE="1.1"
```

```yaml
string_key: ${STRING_VALUE}                           # Valid reference to STRING_VALUE
other_string_key: "${STRING_VALUE}"                   # Valid reference to STRING_VALUE inside double quotes
another_string_key: "${BOOl_VALUE}"                   # Valid reference to BOOl_VALUE inside double quotes
bool_key: ${BOOl_VALUE}                               # Valid reference to BOOl_VALUE
int_key: ${INT_VALUE}                                 # Valid reference to INT_VALUE
float_key: ${FLOAT_VALUE}                             # Valid reference to FLOAT_VALUE
combo_string_key: foo ${STRING_VALUE} ${FLOAT_VALUE}  # Valid reference to STRING_VALUE and FLOAT_VALUE
undefined_key: ${UNDEFINED_KEY}                       # Invalid reference, UNDEFINED_KEY is not defined and is replaced with ""
${STRING_VALUE}: value                                # Invalid reference, substitution is not valid in mapping keys and reference is ignored
```

Environment variable substitution results in the following YAML:

```yaml
string_key: value                # Interpreted as type string, tag URI tag:yaml.org,2002:str
other_string_key: "value"        # Interpreted as type string, tag URI tag:yaml.org,2002:str
another_string_key: "true"       # Interpreted as type string, tag URI tag:yaml.org,2002:str
bool_key: true                   # Interpreted as type bool, tag URI tag:yaml.org,2002:bool
int_key: 1                       # Interpreted as type int, tag URI tag:yaml.org,2002:int
float_key: 1.1                   # Interpreted as type float, tag URI tag:yaml.org,2002:float
combo_string_key: foo value 1.1  # Interpreted as type string, tag URI tag:yaml.org,2002:str
undefined_key:                   # Interpreted as type null, tag URI tag:yaml.org,2002:null
${STRING_VALUE}: value           # Interpreted as type string, tag URI tag:yaml.org,2002:str
```

## SDK Configuration

SDK configuration defines the interfaces and operations that SDKs are expected
to expose to enable file based configuration.

### In-Memory Configuration Model

SDKs SHOULD provide an in-memory representation of
the [Configuration Model](#configuration-model). In general, SDKs are encouraged
to provide this in-memory representation in a manner that is idiomatic for their
language. If an SDK needs to expose a class or interface, the
name `Configuration` is RECOMMENDED.

### Operations

SDK implementations of configuration MUST provide the following operations.

Note: Because these operations are stateless pure functions, they are not
defined as part of any type, class, interface, etc. SDKs may organize them in
whatever manner is idiomatic for the language.

TODO: Add operation to update SDK components with new configuration for usage
with OpAmp

#### Parse

Parse and validate a [configuration file](#configuration-file).

Parse MUST perform [environment variable substitution](#environment-variable-substitution).

Parse MUST interpret null as equivalent to unset.

**Parameters:**

* `file`: The [configuration file](#configuration-file) to parse. This MAY be a
  file path, or language specific file data structure, or a stream of a file's content.
* `file_format`: The file format of the `file` (e.g. [yaml](#yaml-file-format)).
  Implementations MAY accept a `file_format` parameter, or infer it from
  the `file` extension, or include file format specific overloads of `parse`,
  e.g. `parseYaml(file)`. If `parse` accepts `file_format`, the API SHOULD be
  structured so a user is obligated to provide it.

**Returns:** [configuration model](#in-memory-configuration-model)

This SHOULD return an error if:

* The `file` doesn't exist or is invalid
* The parsed `file` content does not conform to
  the [configuration model](#configuration-model) schema.

#### Create

Interpret [configuration model](#in-memory-configuration-model) and return SDK components.

If a field is null or unset and a default value is defined, Create MUST ensure
the SDK component is configured with the default value. If a field is null or
unset and no default value is defined, Create SHOULD return an error. For
example, if configuring
the [span batching processor](../trace/sdk.md#batching-processor) and
the `scheduleDelayMillis` field is null or unset, the component is configured
with the default value of `5000`. However, if the `exporter` field is null or
unset, Create fails fast since there is no default value for `exporter`.

**Parameters:**

* `configuration` - The configuration model.

**Returns:** Top level SDK components:

* `TracerProvider`
* `MeterProvider`
* `LoggerProvider`
* `Propagators`

The multiple responses MAY be returned using a tuple, or some other data
structure encapsulating the components.

This SHOULD return an error if it encounters an error in `configuration` (i.e.
fail fast) in accordance with
initialization [error handling principles](../error-handling.md#basic-error-handling-principles).

TODO: define behavior if some portion of configuration model is not supported

## References

* Configuration
  proposal ([OTEP #225](https://github.com/open-telemetry/oteps/pull/225))
