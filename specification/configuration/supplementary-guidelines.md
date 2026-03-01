# Supplementary Guidelines

Note: this document is NOT a spec, it is provided to support the declarative config
[API](./api.md) and [SDK](./sdk.md) specifications, it does NOT add any extra
requirements to the existing specifications.

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [Configuration interface prioritization and `create`](#configuration-interface-prioritization-and-create)
- [Programmatic customization and `create`](#programmatic-customization-and-create)
- [Strict YAML parsing](#strict-yaml-parsing)

<!-- tocstop -->

</details>

## Configuration interface prioritization and `create`

With the [environment variable](./sdk-environment-variables.md) configuration
interface, the spec failed to answer the question of whether programmatic or
environment variable configuration took precedence. This led to differences in
implementations that were ultimately stabilized and difficult to resolve after
the fact.

With declarative config, we don't have ambiguity around configuration interface
precedence:

* [`parse`](./sdk.md#parse) is responsible for parsing config file contents and
  returning the corresponding in-memory data model. Along the way, it
  performs [environment variable substitution](./data-model.md#environment-variable-substitution).
* [`create`](./sdk.md#create) is responsible for interpreting an in-memory
  config data model and creating SDK components.

There is no precedence ambiguity with the environment variable configuration
interface: The language of `parse` and `create` is explicit about
responsibilities and makes no mention of merging environment variables outside
of environment variable substitution.
Furthermore, [OTEL_EXPERIMENTAL_CONFIG_FILE](./sdk-environment-variables.md#declarative-configuration)
explicitly states that the environment variable configuration scheme is ignored.

There is no precedence ambiguity with
the [programmatic configuration interface](./README.md#programmatic): `create`
consumes an in-memory config data model and creates SDK components. According to
the trace, metric, and log specs, SDKs MAY support updating the config, but
there is no conflict with declarative config which doesn't already exist.
However, the SDK handles programmatic config updates to SDK components which
originally programmatically configured applies here as well. If an SDK supports
it, all programmatic config updates are applied after `create` initializes SDK
components and therefore take precedence. The semantics of what programmatic
config updates are allowed and how they merge with existing SDK components are
out of scope for declarative config.

## Programmatic customization and `create`

While `create` does provide an optional mechanism for programmatic
customization, its use should be considered a code smell, to be addressed by
improving the declarative config data model.

For example, the fact that configuration of dynamic authentication for OTLP
exporters is not possible to express with declarative config should not
encourage the OpenTelemetry community to have better programmatic customization.
Instead, we should pursue adding authentication as an SDK plugin component and
modeling in declarative config.

## Strict YAML parsing

The practices described below are derived from the
[YAML 1.2 Core Schema](https://yaml.org/spec/1.2.2/#103-core-schema)
as specified in the [data model](./data-model.md#yaml-file-format) and common
security best practices for YAML processing.

Configuration file authors are encouraged to constrain themselves to the
Core Schema's minimal type system (strings, integers, floats, booleans, null)
to maximize portability across languages and avoid common YAML pitfalls such
as:

* Unintended type coercion (e.g., `NO` being parsed as boolean `false` instead
  of the string `"NO"` in YAML 1.1)
* Security vulnerabilities from language-specific object deserialization
  features that allow arbitrary code execution (e.g., Python's `!!python/object`
  tags, Ruby's `!ruby/object` tags)
* Unexpected behavior from complex YAML features like anchors and aliases in
  untrusted input

When an implementation's YAML library offers a "safe" or "strict" parser mode
(e.g., `yaml.safe_load()` in Python, safe mode in Ruby's Psych), using it is a
good way to enforce these constraints automatically.
