<!--- Hugo front matter used to generate the website version of this page:
linkTitle: Instrumentation Scope
--->

# Instrumentation Scope

**Status**: [Stable](../document-status.md)

A logical unit of the application or one if its components, with which the emitted telemetry can be
associated. It is typically the developer's choice to decide what denotes a
reasonable instrumentation scope. The most common approach is to use the
[instrumentation library](../glossary.md#instrumentation-library) as the scope,
however other scopes are also common, e.g. a module, a package, a class or
a plugin name can be chosen as the instrumentation scope.

The instrumentation scope is defined by the
(name,version,schema_url,attributes) tuple where version, schema_url, and
attributes are optional. This tuple MUST uniquely identify the logical unit of the
code that emits the telemetry. A typical approach to ensure uniqueness is to
use the fully qualified name of the emitting code (e.g. fully qualified library
name or fully qualified class name).

The instrumentation scope MUST be used to obtain a
[Tracer, Meter, or Logger](../glossary.md#tracer-name--meter-name--logger-name).

The instrumentation scope's optional Schema URL identifies the [Telemetry
Schema](../schemas/README.md) that the instrumentation's emitted
telemetry conforms to.

The instrumentation scope's optional attributes provide additional information about
the scope. For example for a scope that specifies an
instrumentation library an additional attribute may be recorded to denote the URL of the
repository URL the library's source code is stored.
