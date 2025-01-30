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

The `$` character is an escape sequence, such that `$$` in the input is
translated to a single `$` in the output. The resolved `$` from an escape
sequence MUST NOT be considered when matching input against the environment
variable substitution regular expression. For example, `$${API_KEY}` resolves
to `${API_KEY}`, and the value of the `API_KEY` environment variable is NOT
substituted. See table below for more examples. In practice, this implies that
parsers consume the input from left to right, iteratively identifying the next
escape sequence, and matching the content since the prior escape sequence
against the environment variable substitution regular expression.

For example, the pseudocode for processing input `$${FOO} ${BAR} $${BAZ}`
where `FOO=a, BAR=b, BAZ=c` would resemble:

* Identify escape sequence `$$` at index 0. Perform substitution
  against `input.substring(0, 0)=""` => `""` and append to output. Append `$`
  to output. Current output: `"$"`.
* Identify escape sequence `$$` at index 15. Perform substitution
  against `input.substring(0+2, 15)="{FOO} ${BAR} "` => `"{FOO} b "` and append
  to output. Append `$` to output. Current output: `"${FOO} b $"`.
* Reach end of input without escape sequence. Perform substitution
  against `input.substring(15+2, input.length)="{BAZ}"` => `"{BAZ}"` and append
  to output. Return output: `"${FOO} b ${BAZ}"`.

When parsing a configuration file that contains a reference not matching
the references regular expression but does match the following PCRE2
regular expression, the parser MUST return an empty result (no partial
results are allowed) and an error describing the parse failure to the user.

```regexp
\$\{(?<INVALID_IDENTIFIER>[^}]+)\}
```

Node types MUST be interpreted after environment variable substitution takes
place. This ensures the environment string representation of boolean, integer,
or floating point properties can be properly converted to expected types.

It MUST NOT be possible to inject YAML structures by environment variables. For
example, see references to `INVALID_MAP_VALUE` environment variable below.

It MUST NOT be possible to inject environment variable by environment variables.
For example, see references to `DO_NOT_REPLACE_ME` environment variable below.

The table below demonstrates environment variable substitution behavior for a
variety of inputs. Examples assume environment variables are set as follows:

```shell
export STRING_VALUE="value"
export BOOL_VALUE="true"
export INT_VALUE="1"
export FLOAT_VALUE="1.1"
export HEX_VALUE="0xdeadbeef"                         # A valid integer value (i.e. 3735928559) written in hexadecimal
export INVALID_MAP_VALUE="value\nkey:value"           # An invalid attempt to inject a map key into the YAML
export DO_NOT_REPLACE_ME="Never use this value"       # An unused environment variable
export REPLACE_ME='${DO_NOT_REPLACE_ME}'              # A valid replacement text, used verbatim, not replaced with "Never use this value"
export VALUE_WITH_ESCAPE='value$$'              # A valid replacement text, used verbatim, not replaced with "Never use this value"
```

| YAML - input                               | YAML - post substitution            | Resolved Tag URI          | Notes                                                                                                                                             |
|--------------------------------------------|-------------------------------------|---------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------|
| `key: ${STRING_VALUE}`                     | `key: value`                        | `tag:yaml.org,2002:str`   | YAML parser resolves to string                                                                                                                    |
| `key: ${BOOL_VALUE}`                       | `key: true`                         | `tag:yaml.org,2002:bool`  | YAML parser resolves to true                                                                                                                      |
| `key: ${INT_VALUE}`                        | `key: 1`                            | `tag:yaml.org,2002:int`   | YAML parser resolves to int                                                                                                                       |
| `key: ${FLOAT_VALUE}`                      | `key: 1.1`                          | `tag:yaml.org,2002:float` | YAML parser resolves to float                                                                                                                     |
| `key: ${HEX_VALUE}`                        | `key: 0xdeadbeef`                   | `tag:yaml.org,2002:int`   | YAML parser resolves to int `3735928559`                                                                                                          |
| `key: "${STRING_VALUE}"`                   | `key: "value"`                      | `tag:yaml.org,2002:str`   | Double quoted to force coercion to string `"value"`                                                                                               |
| `key: "${BOOL_VALUE}"`                     | `key: "true"`                       | `tag:yaml.org,2002:str`   | Double quoted to force coercion to string `"true"`                                                                                                |
| `key: "${INT_VALUE}"`                      | `key: "1"`                          | `tag:yaml.org,2002:str`   | Double quoted to force coercion to string `"1"`                                                                                                   |
| `key: "${FLOAT_VALUE}"`                    | `key: "1.1"`                        | `tag:yaml.org,2002:str`   | Double quoted to force coercion to string `"1.1"`                                                                                                 |
| `key: "${HEX_VALUE}"`                      | `key: "0xdeadbeef"`                 | `tag:yaml.org,2002:str`   | Double quoted to force coercion to string `"0xdeadbeef"`                                                                                          |
| `key: ${env:STRING_VALUE}`                 | `key: value`                        | `tag:yaml.org,2002:str`   | Alternative `env:` syntax                                                                                                                         |
| `key: ${INVALID_MAP_VALUE}`                | `key: value\nkey:value`             | `tag:yaml.org,2002:str`   | Map structure resolves to string and _not_ expanded                                                                                               |
| `key: foo ${STRING_VALUE} ${FLOAT_VALUE}`  | `key: foo value 1.1`                | `tag:yaml.org,2002:str`   | Multiple references are injected and resolved to string                                                                                           |
| `key: ${UNDEFINED_KEY}`                    | `key:`                              | `tag:yaml.org,2002:null`  | Undefined env var is replaced with `""` and resolves to null                                                                                      |
| `key: ${UNDEFINED_KEY:-fallback}`          | `key: fallback`                     | `tag:yaml.org,2002:str`   | Undefined env var results in substitution of default value `fallback`                                                                             |
| `${STRING_VALUE}: value`                   | `${STRING_VALUE}: value`            | `tag:yaml.org,2002:str`   | Usage of substitution syntax in keys is ignored                                                                                                   |
| `key: ${REPLACE_ME}`                       | `key: ${DO_NOT_REPLACE_ME}`         | `tag:yaml.org,2002:str`   | Value of env var `REPLACE_ME` is `${DO_NOT_REPLACE_ME}`, and is _not_ substituted recursively                                                     |
| `key: ${UNDEFINED_KEY:-${STRING_VALUE}}`   | `${STRING_VALUE}`                   | `tag:yaml.org,2002:str`   | Undefined env var results in substitution of default value `${STRING_VALUE}`, and is _not_ substituted recursively                                |
| `key: ${STRING_VALUE:?error}`              | n/a                                 | n/a                       | Invalid substitution reference produces parse error                                                                                               |
| `key: $${STRING_VALUE}`                    | `key: ${STRING_VALUE}`              | `tag:yaml.org,2002:str`   | `$$` escape sequence is replaced with `$`, `{STRING_VALUE}` does not match substitution syntax                                                    |
| `key: $$${STRING_VALUE}`                   | `key: $value`                       | `tag:yaml.org,2002:str`   | `$$` escape sequence is replaced with `$`, `${STRING_VALUE}` is replaced with `value`                                                             |
| `key: $$$${STRING_VALUE}`                  | `key: $${STRING_VALUE}`             | `tag:yaml.org,2002:str`   | `$$` escape sequence is replaced with `$`, `$$` escape sequence is replaced with `$`, `{STRING_VALUE}` does not match substitution syntax         |
| `key: $${STRING_VALUE:-fallback}`          | `${STRING_VALUE:-fallback}`         | `tag:yaml.org,2002:str`   | `$$` escape sequence is replaced with `$`, `{STRING_VALUE:-fallback}` does not match substitution syntax                                          |
| `key: $${STRING_VALUE:-${STRING_VALUE}}`   | `${STRING_VALUE:-value}`            | `tag:yaml.org,2002:str`   | `$$` escape sequence is replaced with `$`, leaving `{STRING_VALUE:-${STRING_VALUE}}`, `${STRING_VALUE}` is replaced with `value`                  |
| `key: ${UNDEFINED_KEY:-$${UNDEFINED_KEY}}` | `${STRING_VALUE:-${UNDEFINED_KEY}}` | `tag:yaml.org,2002:str`   | `$$` escape sequence is replaced with `$`, leaving `${UNDEFINED_KEY:-` before and `{UNDEFINED_KEY}}` after which do not match substitution syntax |
| `key: ${VALUE_WITH_ESCAPE}`                | `value$$`                           | `tag:yaml.org,2002:str`   | Value of env var `VALUE_WITH_ESCAPE` is `value$$`, which is substituted without escaping                                                          |
| `key: a $$ b`                              | `key: a $ b`                        | `tag:yaml.org,2002:str`   | `$$` escape sequence is replaced with `$`                                                                                                         |
| `key: a $ b`                               | `key: a $ b`                        | `tag:yaml.org,2002:str`   | No escape sequence, no substitution references, value is left unchanged                                                                           |
