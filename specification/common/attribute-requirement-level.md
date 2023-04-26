# Attribute Requirement Levels for Semantic Conventions

**Status**: [Stable](../document-status.md)

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [Required](#required)
- [Conditionally Required](#conditionally-required)
- [Recommended](#recommended)
- [Opt-In](#opt-in)
- [Performance suggestions](#performance-suggestions)

<!-- tocstop -->

</details>

_This section applies to Log, Metric, Resource, and Span, and describes requirement levels for attributes defined in semantic conventions._

Attribute requirement levels apply to the [instrumentation library](../glossary.md#instrumentation-library).

The following attribute requirement levels are specified:

- [Required](#required)
- [Conditionally Required](#conditionally-required)
- [Recommended](#recommended)
- [Opt-In](#opt-in)

The requirement level for an attribute is specified by semantic conventions depending on attribute availability across instrumented entities, performance, security, and other factors. When specifying requirement levels, a semantic convention MUST take into account signal-specific requirements.

For example, Metric attributes that may have high cardinality can only be defined with `Opt-In` level.

A semantic convention that refers to an attribute from another semantic convention MAY modify the requirement level within its own scope. Otherwise, requirement level from the referred semantic convention applies.

For example, [Database semantic convention](../trace/semantic_conventions/database.md) references `network.transport` attribute defined in [General attributes](../trace/semantic_conventions/span-general.md) with `Conditionally Required` level on it.

## Required

All instrumentations MUST populate the attribute. A semantic convention defining a Required attribute expects an absolute majority of instrumentation libraries and applications are able to efficiently retrieve and populate it, and can additionally meet requirements for cardinality, security, and any others specific to the signal defined by the convention. `http.request.method` is an example of a Required attribute.

_Note: Consumers of telemetry can detect if a telemetry item follows a specific semantic convention by checking for the presence of a `Required` attribute defined by such convention. For example, the presence of the `db.system` attribute on a span can be used as an indication that the span follows database semantics._

## Conditionally Required

All instrumentations MUST populate the attribute when the given condition is satisfied. The semantic convention of a `Conditionally Required` attribute MUST clarify the condition under which the attribute is to be populated.

`http.route` is an example of a conditionally required attribute that is populated when the instrumented HTTP framework provides route information for the instrumented request. Some low-level HTTP server implementations do not support routing and corresponding instrumentations can't populate the attribute.

When a `Conditionally Required` attribute's condition is not satisfied, and there is no requirement to populate the attribute, semantic conventions MAY provide special instructions on how to handle it. If no instructions are given and if instrumentation can populate the attribute, instrumentation SHOULD use the `Opt-In` requirement level on the attribute.

For example, `server.address` is `Conditionally Required` by the [Database convention](../trace/semantic_conventions/database.md) when available. When `server.socket.address` is available instead, instrumentation can do a DNS lookup, cache and populate `server.address`, but only if the user explicitly enables the instrumentation to do so, considering the performance issues that DNS lookups introduce.

## Recommended

Instrumentations SHOULD add the attribute by default if it's readily available and can be [efficiently populated](#performance-suggestions). Instrumentations MAY offer a configuration option to disable Recommended attributes.

Instrumentations that decide not to populate `Recommended` attributes due to [performance](#performance-suggestions), security, privacy, or other consideration by default, SHOULD allow for users to
opt-in to emit them as defined for the `Opt-In` requirement level (if the attributes are logically applicable).

## Opt-In

Instrumentations SHOULD populate the attribute if and only if the user configures the instrumentation to do so. Instrumentation that doesn't support configuration MUST NOT populate `Opt-In` attributes.

This attribute requirement level is recommended for attributes that are particularly expensive to retrieve or might pose a security or privacy risk. These should therefore only be enabled explicitly by a user making an informed decision.

## Performance suggestions

Here are several examples of expensive operations to be avoided by default:

- DNS lookups to populate `server.address` when only an IP address is available to the instrumentation. Caching lookup results does not solve the issue for all possible cases and should be avoided by default too.
- forcing an `http.route` calculation before the HTTP framework calculates it
- reading response stream to find `http.response.body.size` when `Content-Length` header is not available
