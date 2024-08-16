# Configuration Data Model

**Status**: [Development](../document-status.md)

<!-- toc -->

- [Overview](#overview)
  * [Stability definition](#stability-definition)
  * [File-based configuration model](#file-based-configuration-model)
    + [YAML file format](#yaml-file-format)
    + [Environment variable substitution](#environment-variable-substitution)

<!-- tocstop -->

## Overview

The OpenTelemetry configuration data model is part of
the [declarative configuration interface](./README.md#declarative-configuration).

The data model defines data structures which allow users to specify an intended
configuration of OpenTelemetry SDK components and instrumentation.

The data model is defined
in [opentelemetry-configuration](https://github.com/open-telemetry/opentelemetry-configuration)
using [JSON Schema](https://json-schema.org/).

The data model itself is an abstraction with multiple built-in representations:

* [File-based configuration model](#file-based-configuration-model)
* [SDK in-memory configuration model](./sdk.md#in-memory-configuration-model)

### Stability definition

TODO: define stability guarantees and backwards compatibility

### File-based configuration model

A configuration file is a serialized file-based representation of
the configuration data model.

Configuration files SHOULD use one the following serialization formats:

* [YAML file format](#yaml-file-format)

#### YAML file format

[YAML](https://yaml.org/spec/1.2.2/) configuration files SHOULD follow YAML spec
revision >= 1.2.

YAML configuration files SHOULD be parsed using [v1.2 YAML core schema](https://yaml.org/spec/1.2.2/#103-core-schema).

YAML configuration files MUST use file extensions `.yaml` or `.yml`.

#### Environment variable substitution

Configuration files support environment variables substitution for references
which match the following PCRE2 regular expression:

```regexp
\$\{(?:env:)?(?<ENV_NAME>[a-zA-Z_][a-zA-Z0-9_]*)(:-(?<DEFAULT_VALUE>[^\n]*))?\}
```

The `ENV_NAME` MUST start with an alphabetic or `_` character, and is followed
by 0 or more alphanumeric or `_` characters.

For example, `${API_KEY}` and `${env:API_KEY}` are valid, while `${1API_KEY}`
and `${API_$KEY}` are invalid.

Environment variable substitution MUST only apply to scalar values. Mapping keys
are not candidates for substitution.

The `DEFAULT_VALUE` is an optional fallback value which is substituted
if `ENV_NAME` is null, empty, or undefined. `DEFAULT_VALUE` consists of 0 or
more non line break characters (i.e. any character except `\n`). If a referenced
environment variable is not defined and does not have a `DEFAULT_VALUE`, it MUST
be replaced with an empty value.

When parsing a configuration file that contains a reference not matching
the references regular expression but does match the following PCRE2
regular expression, the parser MUST return an empty result (no partial
results are allowed) and an error describing the parse failure to the user.

```regexp
\$\{(?<INVALID_IDENTIFIER>[^}]+)\}
```

Node types MUST be interpreted after environment variable substitution takes
place. This ensures the environment string representation of boolean, integer,
or floating point fields can be properly converted to expected types.

It MUST NOT be possible to inject YAML structures by environment variables. For
example, see references to `INVALID_MAP_VALUE` environment variable below.

It MUST NOT be possible to inject environment variable by environment variables.
For example, see references to `DO_NOT_REPLACE_ME` environment variable below.

For example, consider the following environment variables,
and [YAML](#yaml-file-format) configuration file:

```shell
export STRING_VALUE="value"
export BOOL_VALUE="true"
export INT_VALUE="1"
export FLOAT_VALUE="1.1"
export HEX_VALUE="0xdeadbeef"                         # A valid integer value written in hexadecimal
export INVALID_MAP_VALUE="value\nkey:value"           # An invalid attempt to inject a map key into the YAML
export DO_NOT_REPLACE_ME="Never use this value"       # An unused environment variable
export REPLACE_ME='${DO_NOT_REPLACE_ME}'              # A valid replacement text, used verbatim, not replaced with "Never use this value"
```

```yaml
string_key: ${STRING_VALUE}                           # Valid reference to STRING_VALUE
env_string_key: ${env:STRING_VALUE}                   # Valid reference to STRING_VALUE
other_string_key: "${STRING_VALUE}"                   # Valid reference to STRING_VALUE inside double quotes
another_string_key: "${BOOL_VALUE}"                   # Valid reference to BOOL_VALUE inside double quotes
string_key_with_quoted_hex_value: "${HEX_VALUE}"      # Valid reference to HEX_VALUE inside double quotes
yet_another_string_key: ${INVALID_MAP_VALUE}          # Valid reference to INVALID_MAP_VALUE, but YAML structure from INVALID_MAP_VALUE MUST NOT be injected
bool_key: ${BOOL_VALUE}                               # Valid reference to BOOL_VALUE
int_key: ${INT_VALUE}                                 # Valid reference to INT_VALUE
int_key_with_unquoted_hex_value: ${HEX_VALUE}         # Valid reference to HEX_VALUE without quotes
float_key: ${FLOAT_VALUE}                             # Valid reference to FLOAT_VALUE
combo_string_key: foo ${STRING_VALUE} ${FLOAT_VALUE}  # Valid reference to STRING_VALUE and FLOAT_VALUE
string_key_with_default: ${UNDEFINED_KEY:-fallback}   # UNDEFINED_KEY is not defined but a default value is included
undefined_key: ${UNDEFINED_KEY}                       # Invalid reference, UNDEFINED_KEY is not defined and is replaced with ""
${STRING_VALUE}: value                                # Invalid reference, substitution is not valid in mapping keys and reference is ignored
recursive_key: ${REPLACE_ME}                          # Valid reference to REPLACE_ME
# invalid_identifier_key: ${STRING_VALUE:?error}      # If uncommented, this is an invalid identifier, it would fail to parse
```

Environment variable substitution results in the following YAML:

```yaml
string_key: value                              # Interpreted as type string, tag URI tag:yaml.org,2002:str
env_string_key: value                          # Interpreted as type string, tag URI tag:yaml.org,2002:str
other_string_key: "value"                      # Interpreted as type string, tag URI tag:yaml.org,2002:str
another_string_key: "true"                     # Interpreted as type string, tag URI tag:yaml.org,2002:str
string_key_with_quoted_hex_value: "0xdeadbeef" # Interpreted as type string, tag URI tag:yaml.org,2002:str
yet_another_string_key: "value\nkey:value"     # Interpreted as type string, tag URI tag:yaml.org,2002:str
bool_key: true                                 # Interpreted as type bool, tag URI tag:yaml.org,2002:bool
int_key: 1                                     # Interpreted as type int, tag URI tag:yaml.org,2002:int
int_key_with_unquoted_hex_value: 3735928559    # Interpreted as type int, tag URI tag:yaml.org,2002:int
float_key: 1.1                                 # Interpreted as type float, tag URI tag:yaml.org,2002:float
combo_string_key: foo value 1.1                # Interpreted as type string, tag URI tag:yaml.org,2002:str
string_key_with_default: fallback              # Interpreted as type string, tag URI tag:yaml.org,2002:str
undefined_key:                                 # Interpreted as type null, tag URI tag:yaml.org,2002:null
${STRING_VALUE}: value                         # Interpreted as type string, tag URI tag:yaml.org,2002:str
recursive_key: ${DO_NOT_REPLACE_ME}            # Interpreted as type string, tag URI tag:yaml.org,2002:str
```
