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

## OpenTelemetry Collector components

For a library to be considered an OpenTelemetry Collector component, it _MUST_
implement a [Component interface](https://pkg.go.dev/go.opentelemetry.io/collector/component#Component)
defined by the OpenTelemetry Collector SIG.

## OpenTelemetry Collector Distribution

An OpenTelemetry Collector Distribution (Distro) is a compiled instance
of an OpenTelemetry Collector with a specific set of components and features.
