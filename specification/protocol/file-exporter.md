<!--- Hugo front matter used to generate the website version of this page:
linkTitle: File Exporter
--->

# OpenTelemetry Protocol File Exporter

**Status**: [Development](../document-status.md)

This document provides a placeholder for specifying an OTLP exporter capable of
exporting to either a file or stdout.

Currently, it only describes the serialization of OpenTelemetry data to the OTLP JSON format.

## Table of Contents

- [Use Cases](#use-cases)
- [Exporter configuration](#exporter-configuration)
  - [Programmatic configuration](#programmatic-configuration)
- [JSON File serialization](#json-file-serialization)
  - [File storage requirements](#file-storage-requirements)
    - [JSON lines file](#json-lines-file)
    - [Streaming appending](#streaming-appending)
  - [Telemetry data requirements](#telemetry-data-requirements)
  - [Examples](#examples)

## Use Cases

Why do we need a file exporter - why not just use the OTLP exporter?

- *FaaS*: In a FaaS environment, the OTLP exporter may not be able to send data to a collector.
- *Consistent log scraping from pods*: In a Kubernetes environment, logs are often scraped from the stdout pod file.
  This exporter can be used to write logs to stdout - which makes it easier to integrate with existing log scraping tools.
  Existing solutions add metadata, such as the trace ID, to the log line,
  which needs manual configuration and is error-prone.
- *Reliability*: Some prefer writing logs to a file rather than sending data over the network for reliability reasons.

## Exporter configuration

The metric exporter MUST support the environment variables defined in the
[OTLP Exporter](../metrics/sdk_exporters/otlp.md#additional-environment-variable-configuration)
specification.

If a language provides a mechanism to automatically configure a
span or logs processor to pair with the associated
exporter (e.g., using the [`OTEL_TRACES_EXPORTER` environment
variable](../configuration/sdk-environment-variables.md#exporter-selection)), by
default the OpenTelemetry Protocol File Exporter SHOULD be paired with a batching
processor.

### Programmatic configuration

| Requirement | Name                       | Description                                                                                            | Default |
|-------------|----------------------------|--------------------------------------------------------------------------------------------------------|---------|
| MUST        | output stream (or similar) | Configure output stream. This SHOULD include the possibility to configure the output stream to a file. | stdout  |

## JSON File serialization

This document describes the serialization of OpenTelemetry data as JSON objects that can be stored in files.

### File storage requirements

#### JSON lines file

This file is a [JSON lines file](https://jsonlines.org), and therefore follows those requirements:

* UTF-8 encoding
* Each line is a valid JSON value
* The line separator is `\n`
* The preferred file extension is `jsonl`.

#### Streaming appending

There is no guarantee that the data in the file is ordered.

There is no guarantee in particular that timestamps will be monotonically increasing.

### Telemetry data requirements

This defines the first version of the serialization scheme.

The data must be encoded according to the format specified in the
[OTLP JSON Encoding](https://github.com/open-telemetry/opentelemetry-proto/blob/main/docs/specification.md#json-protobuf-encoding).

Only top-level objects, `TracesData`, `MetricsData`, and `LogsData` are supported.

Files must contain exactly one type of data: traces, metrics, or logs.

### Examples

This is an example showing traces:

```json lines
{"resourceSpans":[{"resource":{"attributes":[{"key":"resource-attr","value":{"stringValue":"resource-attr-val-1"}}]},"scopeSpans":[{"scope":{},"spans":[{"traceId":"","spanId":"","parentSpanId":"","name":"operationA","startTimeUnixNano":"1581452772000000321","endTimeUnixNano":"1581452773000000789","droppedAttributesCount":1,"events":[{"timeUnixNano":"1581452773000000123","name":"event-with-attr","attributes":[{"key":"span-event-attr","value":{"stringValue":"span-event-attr-val"}}],"droppedAttributesCount":2},{"timeUnixNano":"1581452773000000123","name":"event","droppedAttributesCount":2}],"droppedEventsCount":1,"status":{"message":"status-cancelled","code":2}},{"traceId":"","spanId":"","parentSpanId":"","name":"operationB","startTimeUnixNano":"1581452772000000321","endTimeUnixNano":"1581452773000000789","links":[{"traceId":"","spanId":"","attributes":[{"key":"span-link-attr","value":{"stringValue":"span-link-attr-val"}}],"droppedAttributesCount":4},{"traceId":"","spanId":"","droppedAttributesCount":1}],"droppedLinksCount":3,"status":{}}]}]}]}
{"resourceSpans":[{"resource":{"attributes":[{"key":"resource-attr","value":{"stringValue":"resource-attr-val-1"}}]},"scopeSpans":[{"scope":{},"spans":[{"traceId":"","spanId":"","parentSpanId":"","name":"operationA","startTimeUnixNano":"1581452772000000321","endTimeUnixNano":"1581452773000000789","droppedAttributesCount":1,"events":[{"timeUnixNano":"1581452773000000424","name":"event-with-attr","attributes":[{"key":"span-event-attr","value":{"stringValue":"span-event-attr-val"}}],"droppedAttributesCount":2},{"timeUnixNano":"1581452773000000424","name":"event","droppedAttributesCount":2}],"droppedEventsCount":1,"status":{"message":"status-cancelled","code":2}},{"traceId":"","spanId":"","parentSpanId":"","name":"operationB","startTimeUnixNano":"1581452772000000343","endTimeUnixNano":"1581452773000001089","links":[{"traceId":"","spanId":"","attributes":[{"key":"span-link-attr","value":{"stringValue":"span-link-attr-val"}}],"droppedAttributesCount":3},{"traceId":"","spanId":"","droppedAttributesCount":4}],"droppedLinksCount":2,"status":{}}]}]}]}
{"resourceSpans":[{"resource":{"attributes":[{"key":"resource-attr","value":{"stringValue":"resource-attr-val-1"}}]},"scopeSpans":[{"scope":{},"spans":[{"traceId":"","spanId":"","parentSpanId":"","name":"operationA","startTimeUnixNano":"1581452772000000321","endTimeUnixNano":"1581452773000000789","droppedAttributesCount":1,"events":[{"timeUnixNano":"1581452773000000826","name":"event-with-attr","attributes":[{"key":"span-event-attr","value":{"stringValue":"span-event-attr-val"}}],"droppedAttributesCount":2},{"timeUnixNano":"1581452773000000826","name":"event","droppedAttributesCount":2}],"droppedEventsCount":1,"status":{"message":"status-cancelled","code":2}},{"traceId":"","spanId":"","parentSpanId":"","name":"operationB","startTimeUnixNano":"1581452772000200521","endTimeUnixNano":"1581452773000004789","links":[{"traceId":"","spanId":"","attributes":[{"key":"span-link-attr","value":{"stringValue":"span-link-attr-val"}}],"droppedAttributesCount":5},{"traceId":"","spanId":"","droppedAttributesCount":2}],"droppedLinksCount":3,"status":{}}]}]}]}
{"resourceSpans":[{"resource":{"attributes":[{"key":"resource-attr","value":{"stringValue":"resource-attr-val-1"}}]},"scopeSpans":[{"scope":{},"spans":[{"traceId":"","spanId":"","parentSpanId":"","name":"operationA","startTimeUnixNano":"1581452772000000321","endTimeUnixNano":"1581452773000000789","droppedAttributesCount":1,"events":[{"timeUnixNano":"1581452773000010925","name":"event-with-attr","attributes":[{"key":"span-event-attr","value":{"stringValue":"span-event-attr-val"}}],"droppedAttributesCount":2},{"timeUnixNano":"1581452773000010925","name":"event","droppedAttributesCount":2}],"droppedEventsCount":1,"status":{"message":"status-cancelled","code":2}},{"traceId":"","spanId":"","parentSpanId":"","name":"operationB","startTimeUnixNano":"1581452772000011821","endTimeUnixNano":"1581452772000012924","links":[{"traceId":"","spanId":"","attributes":[{"key":"span-link-attr","value":{"stringValue":"span-link-attr-val"}}],"droppedAttributesCount":2},{"traceId":"","spanId":"","droppedAttributesCount":2}],"droppedLinksCount":5,"status":{}}]}]}]}
```

This is an example showing metrics:

```json lines
{"resourceMetrics":[{"resource":{"attributes":[{"key":"resource-attr","value":{"stringValue":"resource-attr-val-1"}}]},"scopeMetrics":[{"scope":{},"metrics":[{"name":"counter-int","unit":"1","sum":{"dataPoints":[{"attributes":[{"key":"label-1","value":{"stringValue":"label-value-1"}}],"startTimeUnixNano":"1581452773000000789","timeUnixNano":"1581452773000000789","asInt":"123"},{"attributes":[{"key":"label-2","value":{"stringValue":"label-value-2"}}],"startTimeUnixNano":"1581452772000000321","timeUnixNano":"1581452773000000789","asInt":"456"}],"aggregationTemporality":2,"isMonotonic":true}},{"name":"counter-int","unit":"1","sum":{"dataPoints":[{"attributes":[{"key":"label-1","value":{"stringValue":"label-value-1"}}],"startTimeUnixNano":"1581452772000000321","timeUnixNano":"1581452773000000789","asInt":"123"},{"attributes":[{"key":"label-2","value":{"stringValue":"label-value-2"}}],"startTimeUnixNano":"1581452772000000321","timeUnixNano":"1581452773000000789","asInt":"456"}],"aggregationTemporality":2,"isMonotonic":true}}]}]}]}
{"resourceMetrics":[{"resource":{"attributes":[{"key":"resource-attr","value":{"stringValue":"resource-attr-val-1"}}]},"scopeMetrics":[{"scope":{},"metrics":[{"name":"counter-int","unit":"1","sum":{"dataPoints":[{"attributes":[{"key":"label-1","value":{"stringValue":"label-value-1"}}],"startTimeUnixNano":"1581452773000001459","timeUnixNano":"1581452773000001459","asInt":"120"},{"attributes":[{"key":"label-2","value":{"stringValue":"label-value-2"}}],"startTimeUnixNano":"1581452773000001459","timeUnixNano":"1581452773000001459","asInt":"456"}],"aggregationTemporality":2,"isMonotonic":true}},{"name":"counter-int","unit":"1","sum":{"dataPoints":[{"attributes":[{"key":"label-1","value":{"stringValue":"label-value-1"}}],"startTimeUnixNano":"1581452773000001459","timeUnixNano":"1581452773000001459","asInt":"123"},{"attributes":[{"key":"label-2","value":{"stringValue":"label-value-2"}}],"startTimeUnixNano":"1581452773000001459","timeUnixNano":"1581452773000001459","asInt":"456"}],"aggregationTemporality":2,"isMonotonic":true}}]}]}]}
{"resourceMetrics":[{"resource":{"attributes":[{"key":"resource-attr","value":{"stringValue":"resource-attr-val-1"}}]},"scopeMetrics":[{"scope":{},"metrics":[{"name":"counter-int","unit":"1","sum":{"dataPoints":[{"attributes":[{"key":"label-1","value":{"stringValue":"label-value-1"}}],"startTimeUnixNano":"1581452773000002346","timeUnixNano":"1581452773000002346","asInt":"121"},{"attributes":[{"key":"label-2","value":{"stringValue":"label-value-2"}}],"startTimeUnixNano":"1581452773000002346","timeUnixNano":"1581452773000002346","asInt":"456"}],"aggregationTemporality":2,"isMonotonic":true}},{"name":"counter-int","unit":"1","sum":{"dataPoints":[{"attributes":[{"key":"label-1","value":{"stringValue":"label-value-1"}}],"startTimeUnixNano":"1581452773000002346","timeUnixNano":"1581452773000002346","asInt":"123"},{"attributes":[{"key":"label-2","value":{"stringValue":"label-value-2"}}],"startTimeUnixNano":"1581452772000000321","timeUnixNano":"1581452773000000789","asInt":"456"}],"aggregationTemporality":2,"isMonotonic":true}}]}]}]}
{"resourceMetrics":[{"resource":{"attributes":[{"key":"resource-attr","value":{"stringValue":"resource-attr-val-1"}}]},"scopeMetrics":[{"scope":{},"metrics":[{"name":"counter-int","unit":"1","sum":{"dataPoints":[{"attributes":[{"key":"label-1","value":{"stringValue":"label-value-1"}}],"startTimeUnixNano":"1581452773000007891","timeUnixNano":"1581452773000007891","asInt":"125"},{"attributes":[{"key":"label-2","value":{"stringValue":"label-value-2"}}],"startTimeUnixNano":"1581452772000000321","timeUnixNano":"1581452773000007891","asInt":"456"}],"aggregationTemporality":2,"isMonotonic":true}},{"name":"counter-int","unit":"1","sum":{"dataPoints":[{"attributes":[{"key":"label-1","value":{"stringValue":"label-value-1"}}],"startTimeUnixNano":"1581452773000007891","timeUnixNano":"1581452773000007891","asInt":"123"},{"attributes":[{"key":"label-2","value":{"stringValue":"label-value-2"}}],"startTimeUnixNano":"1581452772000000321","timeUnixNano":"1581452773000007891","asInt":"456"}],"aggregationTemporality":2,"isMonotonic":true}}]}]}]}
```

This is an example showing logs:

```json lines
{"resourceLogs":[{"resource":{"attributes":[{"key":"resource-attr","value":{"stringValue":"resource-attr-val-1"}}]},"scopeLogs":[{"scope":{},"logRecords":[{"timeUnixNano":"1581452773000000789","severityNumber":9,"severityText":"Info","body":{"stringValue":"This is a log message"},"attributes":[{"key":"app","value":{"stringValue":"server"}},{"key":"instance_num","value":{"intValue":"1"}}],"droppedAttributesCount":1,"traceId":"08040201000000000000000000000000","spanId":"0102040800000000"},{"timeUnixNano":"1581452773000000789","severityNumber":9,"severityText":"Info","body":{"stringValue":"something happened"},"attributes":[{"key":"customer","value":{"stringValue":"acme"}},{"key":"env","value":{"stringValue":"dev"}}],"droppedAttributesCount":1,"traceId":"","spanId":""}]}]}]}
{"resourceLogs":[{"resource":{"attributes":[{"key":"resource-attr","value":{"stringValue":"resource-attr-val-1"}}]},"scopeLogs":[{"scope":{},"logRecords":[{"timeUnixNano":"1581452773000001233","severityNumber":9,"severityText":"Info","body":{"stringValue":"This is a log message"},"attributes":[{"key":"app","value":{"stringValue":"server"}},{"key":"instance_num","value":{"intValue":"1"}}],"droppedAttributesCount":1,"traceId":"08040201000000000000000000000000","spanId":"0102040800000000"},{"timeUnixNano":"1581452773000000789","severityNumber":9,"severityText":"Info","body":{"stringValue":"something happened"},"attributes":[{"key":"customer","value":{"stringValue":"acme"}},{"key":"env","value":{"stringValue":"dev"}}],"droppedAttributesCount":1,"traceId":"","spanId":""}]}]}]}
{"resourceLogs":[{"resource":{"attributes":[{"key":"resource-attr","value":{"stringValue":"resource-attr-val-1"}}]},"scopeLogs":[{"scope":{},"logRecords":[{"timeUnixNano":"1581452773000005443","severityNumber":9,"severityText":"Info","body":{"stringValue":"This is a log message"},"attributes":[{"key":"app","value":{"stringValue":"server"}},{"key":"instance_num","value":{"intValue":"1"}}],"droppedAttributesCount":1,"traceId":"08040201000000000000000000000000","spanId":"0102040800000000"},{"timeUnixNano":"1581452773000000789","severityNumber":9,"severityText":"Info","body":{"stringValue":"something happened"},"attributes":[{"key":"customer","value":{"stringValue":"acme"}},{"key":"env","value":{"stringValue":"dev"}}],"droppedAttributesCount":1,"traceId":"","spanId":""}]}]}]}
{"resourceLogs":[{"resource":{"attributes":[{"key":"resource-attr","value":{"stringValue":"resource-attr-val-1"}}]},"scopeLogs":[{"scope":{},"logRecords":[{"timeUnixNano":"1581452773000009875","severityNumber":9,"severityText":"Info","body":{"stringValue":"This is a log message"},"attributes":[{"key":"app","value":{"stringValue":"server"}},{"key":"instance_num","value":{"intValue":"1"}}],"droppedAttributesCount":1,"traceId":"08040201000000000000000000000000","spanId":"0102040800000000"},{"timeUnixNano":"1581452773000000789","severityNumber":9,"severityText":"Info","body":{"stringValue":"something happened"},"attributes":[{"key":"customer","value":{"stringValue":"acme"}},{"key":"env","value":{"stringValue":"dev"}}],"droppedAttributesCount":1,"traceId":"","spanId":""}]}]}]}
```
