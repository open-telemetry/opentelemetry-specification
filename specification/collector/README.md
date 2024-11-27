<!--- Hugo front matter used to generate the website version of this page:
path_base_for_github_subdir:
  from: tmp/otel/specification/baggage/_index.md
  to: baggage/README.md
--->

# OpenTelemetry Collector

The goal of this document is for users to be able to easily switch between
OpenTelemetry Collector Distros while also ensuring that components produced by
the OpenTelemetry Collector SIG is able to work with any vendor who claims
support for an OpenTelemetry Collector.

- An OpenTelemetry Collector _MUST_ accept an [OpenTelemetry Collector configuration
  file](#opentelemetry-collector-configuration-file).
- An OpenTelemetry Collector _MUST_ be able to be compiled with any and all
  additional [Collector components](#opentelemetry-collector-components) that
  the user wishes to include.

## OpenTelemetry Collector configuration file

## OpenTelemetry Collector components

For a library to be considered an OpenTelemetry Collector component, it _MUST_
implement the [Component interface](https://github.com/open-telemetry/opentelemetry-collector/blob/main/component/component.go)
defined in the [opentelemetry-collector repository](https://github.com/open-telemetry/opentelemetry-collector).
repository.

## OpenTelemetry Collector Distribution

An OpenTelemetry Collector Distribution (Distro) is a compiled instance
of an OpenTelemetry Collector with a specific set of components and features.
