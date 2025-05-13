<!--- Hugo front matter used to generate the website version of this page:
linkTitle: Instrumentation Scope
--->

# Instrumentation Scope

**Status**: [Stable](../document-status.md)

A logical unit of software, with which the emitted telemetry can be
associated. It is typically the developer's choice to decide what denotes a
reasonable instrumentation scope. The most common approach is to use
the name and version of the [instrumentation library](../glossary.md#instrumentation-library),
with any additional identifying information as part of the scope's attributes.
Other software components can be used too to get name, version and additional attributes, e.g.
a module, a package, a class or a plugin.

The instrumentation scope is defined by the
(name,version,schema_url,attributes) tuple where version, schema_url, and
attributes are optional. This tuple MUST uniquely identify the logical unit of
software that emits the telemetry. A typical approach to ensure uniqueness is to
use the fully qualified name of the emitting software unit (e.g. fully qualified library
name or fully qualified class name).

The instrumentation scope MUST be used to obtain a
[Tracer, Meter, or Logger](../glossary.md#tracer-name--meter-name--logger-name).

The instrumentation scope's name MUST be specified to identify the `InstrumentationScope`
name. It SHOULD be set to the empty string as last fallback.

The instrumentation scope's optional Schema URL MUST identify the [Telemetry
Schema](../schemas/README.md) that the instrumentation's emitted
telemetry conforms to.

The instrumentation scope's optional attributes provide additional information about
the scope. For example for a scope that specifies an
instrumentation library an additional attribute may be recorded to denote the URL of the
repository URL the library's source code is stored.

## Examples

Here is a non comprehensive list of usage scenarios:

* Generic instrumentation library with its name, version and attributes containing
  additional library information.
* Database access instrumented with its own name and version (e.g. `db.system.name`).
  This can be leveraged by APIs abstracting access to different underlying databases,
  such as JDBC or SqlAlchemy.
* Client consuming or producing information, using its name, version and `id` to set
  `InstrumentationScope`.
* Internal application components emitting their own telemetry, relying on
  `InstrumentationScope` attributes to differentiate themselves in case multiple
  instances of the same type exist.
