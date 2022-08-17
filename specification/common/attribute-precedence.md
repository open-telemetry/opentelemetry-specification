# Attribute precedence on transformation to non-OTLP formats

**Status**: [Experimental](../document-status.md)

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [Overview](#overview)
- [Attribute hierarchy in OTLP messages](#attribute-hierarchy-in-otlp-messages)
- [Precedence per Signal](#precedence-per-signal)
  * [Traces](#traces)
  * [Metrics](#metrics)
  * [Logs](#logs)
  * [Span Links, Span Events and Metric Exemplars](#span-links-span-events-and-metric-exemplars)
- [Considerations](#considerations)
- [Example](#example)
- [Useful links](#useful-links)

<!-- tocstop -->

</details>

## Overview

This document provides supplementary guidelines for the attribute precedence
that exporters should follow when translating from the hierarchical OTLP format
to non-hierarchical formats.

A mapping is required when flattening out attributes from the structured OTLP
format, which has attributes at different levels (e.g., Resource attributes,
InstrumentationScope attributes, attributes on Spans/Metrics/Logs) to a
non-hierarchical representation (e.g., Prometheus/OpenMetrics labels).
In the case of OpenMetrics, the set of labels is flat and must have unique
labels only
(<https://github.com/OpenObservability/OpenMetrics/blob/main/specification/OpenMetrics.md#labelset>).
Since OpenTelemetry allows for different levels of attributes, it is possible
that the same attribute appears multiple times on different levels.

This document aims to provide guidance on how OpenTelemetry attributes can be
consistently mapped to flat sets.

## Attribute hierarchy in OTLP messages

Since the OTLP format is a hierarchical format, there is an inherent order in
the attributes.
In this document,
[Resource](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/resource/sdk.md)
attributes are considered to be at the top of the hierarchy, since they apply to
all collected telemetry.
Attributes on individual Spans/Metric data points/Logs are at the bottom of the
hierarchy, as they are most specialized and only apply to a subset of all data.

**A more specialized attribute that shares an attribute key with more general
attribute will take precedence and overwrite the more general attribute.**

When de-normalizing an OTLP message into a flat set of key-value pairs,
attributes that are present on the Resource and InstrumentationScope levels will
be attached to each Span/Metric data point/Log.

## Precedence per Signal

Below, the precedence for each of the signals is spelled out explicitly.
Only spans, metric data points and log records are considered.

`A > B` denotes that the attribute on `A` will overwrite the attribute on `B`
if the keys clash.

### Traces

```
Span.attributes > ScopeSpans.scope.attributes > ResourceSpans.resource.attributes
```

### Metrics

Metrics are different from Spans and LogRecords, as each Metric has a data field
which can contain one or more data points.
Each data point has a set of attributes, which need to be considered
independently.

```
Metric.data.data_points.attributes > ScopeMetrics.scope.attributes > ResourceMetrics.resource.attributes
```

### Logs

```
LogRecord.log_records.attributes > ScopeLogs.scope.attributes > ResourceLogs.resource.attributes
```

### Span Links, Span Events and Metric Exemplars

> Span Links, Span Events and Metric Exemplars need to be considered
> differently, as conflicting entries there can lead to problematic data loss.

Consider a `http.host` attribute on a Span Link, which identifies the host of a
linked Span.
Following the "more specialized overwrites more general" suggestion leads to
overwriting the `http.host` attribute of the Span, which is likely desired
information.
Transferring attributes on Span Links, Span Events and Metric Exemplars should
be done separately from the parent Span/Metric data point.
This is out of the scope of these guidelines.

## Considerations

Note that this precedence is a strong suggestion, not a requirement.
Code that transforms attributes should follow this mode of flattening, but may
diverge if they have a reason to do so.

## Example

The following is a theoretical YAML-like representation of an OTLP message which
has attributes with attribute names that clash on multiple levels.

```yaml
ResourceMetrics:
    resource:
        attributes:
            # key-value pairs (attributes) on the resource
            attribute1: resource-attribute-1
            attribute2: resource-attribute-2
            attribute3: resource-attribute-3
            service.name: my-service

    scope_metrics:
        scope:
            attributes:
                attribute1: scope-attribute-1
                attribute2: scope-attribute-2
                attribute4: scope-attribute-4
        
        metrics:
            # there can be multiple data entries here.
            data/0:
                data_points:
                    # each data can have multiple data points:
                    data_point/1:
                        attributes: 
                            # will overwrite scope and resource attribute
                            attribute1: data-point-1-attribute-1

                    data_point/2:
                        attributes:
                            # will overwrite 
                            attribute1: data-point-2-attribute-1
                            attribute4: data-point-2-attribute-4
```

The structure above contains two data points, thus there will be two data points
in the output.
Their attributes will be:

```yaml
# data point 1
service.name: my-service              # from the resource
attribute1: data-point-1-attribute-1  # overwrites attribute1 on resource & scope
attribute2: scope-attribute-2         # overwrites attribute2 on resource
attribute3: resource-attribute-3      # from the resource, not overwritten
attribute4: scope-attribute-4         # from the scope, not overwritten

# data point 2
service.name: my-service              # from the resource
attribute1: data-point-2-attribute-1  # overwrites attribute1 on resource & scope
attribute2: scope-attribute-2         # overwrites attribute2 on resource
attribute3: resource-attribute-3      # from the resource, not overwritten
attribute4: data-point-2-attribute-4  # overwrites attribute4 from the scope
```

## Useful links

* [Trace Proto](https://github.com/open-telemetry/opentelemetry-proto/blob/main/opentelemetry/proto/trace/v1/trace.proto)
* [Metrics Proto](https://github.com/open-telemetry/opentelemetry-proto/blob/main/opentelemetry/proto/metrics/v1/metrics.proto)
* [Logs Proto](https://github.com/open-telemetry/opentelemetry-proto/blob/main/opentelemetry/proto/logs/v1/logs.proto)
* [Resource Proto](https://github.com/open-telemetry/opentelemetry-proto/blob/main/opentelemetry/proto/resource/v1/resource.proto)
