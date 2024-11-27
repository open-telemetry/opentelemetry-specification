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

- An OpenTelemetry Collector _MUST_ accept a OpenTelemetry Collector Config file.
- An OpenTelemetry Collector _MUST_ be able to be compiled with any and all
  additional Collector plugins that the user wishes to include.
- A compiled instance of an OpenTelemetry Collector – with a specific set of
  plugins and features – is referred to as an OpenTelemetry Collector Distro.
