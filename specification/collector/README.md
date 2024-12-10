<!--- Hugo front matter used to generate the website version of this page:
path_base_for_github_subdir:
  from: tmp/otel/specification/collector/_index.md
  to: collector/README.md
--->

# OpenTelemetry Collector

The goal of this document is for users to be able to easily switch between
OpenTelemetry Collector Distros while also ensuring that components produced by
the OpenTelemetry Collector SIG are able to work with any vendor who claims
support for an OpenTelemetry Collector.

- An OpenTelemetry Collector _MUST_ accept an [OpenTelemetry Collector configuration
  file](#opentelemetry-collector-configuration-file).
- An OpenTelemetry Collector _MUST_ be able to include additional compatible
  [Collector components](#opentelemetry-collector-components) that
  the user wishes to include.

## OpenTelemetry Collector configuration file

An OpenTelemetry Collector configuration file is defined as YAML and _MUST_ support
the following [minimum structure](https://pkg.go.dev/go.opentelemetry.io/collector/otelcol#Config):

```yaml
receivers:
processors:
exporters:
connectors:
extensions:
service:
```

## OpenTelemetry Collector components

For a library to be considered an OpenTelemetry Collector component, it _MUST_
implement a [Component interface](https://pkg.go.dev/go.opentelemetry.io/collector/component#Component)
defined by the OpenTelemetry Collector SIG.

Components require a unique identfier as a `type` string to be included in an OpenTelemetry
Collector. It is possible that multiple components use the same identifier, in which
case the two components cannot be used simultaneously in a single OpenTelemetry Collector. In
order to resolve this, the clashing components must use a different identifier.

### Compatibility requirements

A component is defined as compatible with an OpenTelemetry Collector when its dependencies are
source- and version-compatible with the Component interfaces of that Collector.

For example, a Collector derived from version tag v0.100.0 of the [OpenTelemetry Collector](https://github.com/open-telemetry/opentelemetry-collector) _MUST_ support all components that
are version-compatible with the Golang Component API defined in the `github.com/open-telemetry/opentelemetry-collector/component` module found in that repository for that version tag.

## OpenTelemetry Collector Distribution

An OpenTelemetry Collector Distribution (Distro) is a compiled instance
of an OpenTelemetry Collector with a specific set of components and features. A
Distribution _SHOULD_ provide users with tools and/or documentation for adding
their own components to the Distribution.
