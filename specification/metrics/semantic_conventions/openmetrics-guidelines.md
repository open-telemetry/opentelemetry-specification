# Guidance for Interoperating with OpenMetrics

**Status**: [Experimental](../../document-status.md)

**Note:** This document is work in progress and will be updated as the
OpenMetrics specification further develops.

## Overview

OpenTelemetry will need to interoperate with systems using the OpenMetrics or
Prometheus exposition format in two ways:

* OpenTelemetry may need to accept and propagate metrics expressed in
  the OpenMetrics exposition format, and export them to downstream systems
  (including OpenTelemetry Collector(s), zPages, vendor backends, etc...)
* OpenTelemetry may need to expose OpenTelemetry generated metrics in the
  OpenMetrics exposition format.

### OpenMetrics to OpenTelemetry

The OpenTelemetry collector implements a Prometheus receiver, which reads
metrics in the OpenMetrics exposition format. For more information, refer to the
[Prometheus Receiver Design Document](https://github.com/open-telemetry/opentelemetry-collector/blob/master/receiver/prometheusreceiver/DESIGN.md).

### OpenTelemetry to OpenMetrics

#### Name and Label Keys

Exposting OpenTelemetry metrics in the OpenMetrics format is primarily
problematic for metric and label naming; the OpenMetrics exposition format
expressly forbids some characters that are allowed in OpenTelemetry.

When converting OpenTelemetry metric events to the OpenMetrics exposition
format, the name field and all label keys MUST be sanitized by replacing
every character that is not a letter or a digit with an underscore.

Example pseudocode:

```ruby
def sanitize(name)
    return name.sub(/\W/, '_')
```

See also [Metric names and labels](https://prometheus.io/docs/concepts/data_model/#metric-names-and-labels)
in the Prometheus data model documentation.

OpenMetrics does not allow metric names to begin with a digit. OpenTelemetry's
[instrument naming requirements](../api.md#instrument-naming-requirements) also
require that the first character of a metric instrument is non-numeric.

If a metric event is generated in OpenTelemetry that does not conform to this
specification, the name of the resulting OpenMetrics metric MAY be prepended
with an underscore.
