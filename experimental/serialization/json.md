# JSON File serialization

**Status**: [Experimental](../../specification/document-status.md)

## Table of Contents

- [Overview](#overview)
- [Requirements](#requirements)
  - [File storage requirements](#file-storage-requirements)
    - [JSON lines file](#json-lines-file)
    - [Streaming appending](#streaming-appending)
  - [Telemetry data requirements](#telemetry-data-requirements)
- [Examples](#examples)

## Overview

This document describes the serialization of OpenTelemetry data as JSON objects that can be stored in files.

## Requirements

### File storage requirements

#### JSON lines file

This file is a [JSON lines file](https://jsonlines.org/), and therefore follows those requirements:

* UTF-8 encoding
* Each line is a valid JSON value
* The line separator is `\n`
* The preferred file extension is `jsonl`.

#### Streaming appending

There is no guarantee that the data in the file is ordered.

There is no guarantee in particular that timestamps will be monotically increasing.

### Telemetry data requirements

This defines the first version of the serialization scheme.

The data must be encoded according to the format specified in the [OTLP/HTTP standard](../../specification/protocol/otlp.md#otlphttp).

Only top-level objects, `ExportTraceServiceRequest`, `ExportMetricsServiceRequest`, and `ExportLogsServiceRequest` are supported.

Files must contain exactly one type of data: traces, metrics, or logs.

## Examples

This is an example showing traces:

```json lines
{"resourceSpans":[{"resource":{"attributes":[{"key":"resource-attr","value":{"stringValue":"resource-attr-val-1"}}]},"instrumentationLibrarySpans":[{"instrumentationLibrary":{},"spans":[{"traceId":"","spanId":"","parentSpanId":"","name":"operationA","startTimeUnixNano":"1581452772000000321","endTimeUnixNano":"1581452773000000789","droppedAttributesCount":1,"events":[{"timeUnixNano":"1581452773000000123","name":"event-with-attr","attributes":[{"key":"span-event-attr","value":{"stringValue":"span-event-attr-val"}}],"droppedAttributesCount":2},{"timeUnixNano":"1581452773000000123","name":"event","droppedAttributesCount":2}],"droppedEventsCount":1,"status":{"deprecatedCode":"DEPRECATED_STATUS_CODE_UNKNOWN_ERROR","message":"status-cancelled","code":"STATUS_CODE_ERROR"}},{"traceId":"","spanId":"","parentSpanId":"","name":"operationB","startTimeUnixNano":"1581452772000000321","endTimeUnixNano":"1581452773000000789","links":[{"traceId":"","spanId":"","attributes":[{"key":"span-link-attr","value":{"stringValue":"span-link-attr-val"}}],"droppedAttributesCount":4},{"traceId":"","spanId":"","droppedAttributesCount":1}],"droppedLinksCount":3,"status":{}}]}]}]}
{"resourceSpans":[{"resource":{"attributes":[{"key":"resource-attr","value":{"stringValue":"resource-attr-val-1"}}]},"instrumentationLibrarySpans":[{"instrumentationLibrary":{},"spans":[{"traceId":"","spanId":"","parentSpanId":"","name":"operationA","startTimeUnixNano":"1581452772000000321","endTimeUnixNano":"1581452773000000789","droppedAttributesCount":1,"events":[{"timeUnixNano":"1581452773000000424","name":"event-with-attr","attributes":[{"key":"span-event-attr","value":{"stringValue":"span-event-attr-val"}}],"droppedAttributesCount":2},{"timeUnixNano":"1581452773000000424","name":"event","droppedAttributesCount":2}],"droppedEventsCount":1,"status":{"deprecatedCode":"DEPRECATED_STATUS_CODE_UNKNOWN_ERROR","message":"status-cancelled","code":"STATUS_CODE_ERROR"}},{"traceId":"","spanId":"","parentSpanId":"","name":"operationB","startTimeUnixNano":"1581452772000000343","endTimeUnixNano":"1581452773000001089","links":[{"traceId":"","spanId":"","attributes":[{"key":"span-link-attr","value":{"stringValue":"span-link-attr-val"}}],"droppedAttributesCount":3},{"traceId":"","spanId":"","droppedAttributesCount":4}],"droppedLinksCount":2,"status":{}}]}]}]}
{"resourceSpans":[{"resource":{"attributes":[{"key":"resource-attr","value":{"stringValue":"resource-attr-val-1"}}]},"instrumentationLibrarySpans":[{"instrumentationLibrary":{},"spans":[{"traceId":"","spanId":"","parentSpanId":"","name":"operationA","startTimeUnixNano":"1581452772000000321","endTimeUnixNano":"1581452773000000789","droppedAttributesCount":1,"events":[{"timeUnixNano":"1581452773000000826","name":"event-with-attr","attributes":[{"key":"span-event-attr","value":{"stringValue":"span-event-attr-val"}}],"droppedAttributesCount":2},{"timeUnixNano":"1581452773000000826","name":"event","droppedAttributesCount":2}],"droppedEventsCount":1,"status":{"deprecatedCode":"DEPRECATED_STATUS_CODE_UNKNOWN_ERROR","message":"status-cancelled","code":"STATUS_CODE_ERROR"}},{"traceId":"","spanId":"","parentSpanId":"","name":"operationB","startTimeUnixNano":"1581452772000200521","endTimeUnixNano":"1581452773000004789","links":[{"traceId":"","spanId":"","attributes":[{"key":"span-link-attr","value":{"stringValue":"span-link-attr-val"}}],"droppedAttributesCount":5},{"traceId":"","spanId":"","droppedAttributesCount":2}],"droppedLinksCount":3,"status":{}}]}]}]}
{"resourceSpans":[{"resource":{"attributes":[{"key":"resource-attr","value":{"stringValue":"resource-attr-val-1"}}]},"instrumentationLibrarySpans":[{"instrumentationLibrary":{},"spans":[{"traceId":"","spanId":"","parentSpanId":"","name":"operationA","startTimeUnixNano":"1581452772000000321","endTimeUnixNano":"1581452773000000789","droppedAttributesCount":1,"events":[{"timeUnixNano":"1581452773000010925","name":"event-with-attr","attributes":[{"key":"span-event-attr","value":{"stringValue":"span-event-attr-val"}}],"droppedAttributesCount":2},{"timeUnixNano":"1581452773000010925","name":"event","droppedAttributesCount":2}],"droppedEventsCount":1,"status":{"deprecatedCode":"DEPRECATED_STATUS_CODE_UNKNOWN_ERROR","message":"status-cancelled","code":"STATUS_CODE_ERROR"}},{"traceId":"","spanId":"","parentSpanId":"","name":"operationB","startTimeUnixNano":"1581452772000011821","endTimeUnixNano":"1581452772000012924","links":[{"traceId":"","spanId":"","attributes":[{"key":"span-link-attr","value":{"stringValue":"span-link-attr-val"}}],"droppedAttributesCount":2},{"traceId":"","spanId":"","droppedAttributesCount":2}],"droppedLinksCount":5,"status":{}}]}]}]}
```

This is an example showing metrics:

```json lines
{"resourceMetrics":[{"resource":{"attributes":[{"key":"resource-attr","value":{"stringValue":"resource-attr-val-1"}}]},"instrumentationLibraryMetrics":[{"instrumentationLibrary":{},"metrics":[{"name":"counter-int","unit":"1","sum":{"dataPoints":[{"attributes":[{"key":"label-1","value":{"stringValue":"label-value-1"}}],"startTimeUnixNano":"1581452773000000789","timeUnixNano":"1581452773000000789","asInt":"123"},{"attributes":[{"key":"label-2","value":{"stringValue":"label-value-2"}}],"startTimeUnixNano":"1581452772000000321","timeUnixNano":"1581452773000000789","asInt":"456"}],"aggregationTemporality":"AGGREGATION_TEMPORALITY_CUMULATIVE","isMonotonic":true}},{"name":"counter-int","unit":"1","sum":{"dataPoints":[{"attributes":[{"key":"label-1","value":{"stringValue":"label-value-1"}}],"startTimeUnixNano":"1581452772000000321","timeUnixNano":"1581452773000000789","asInt":"123"},{"attributes":[{"key":"label-2","value":{"stringValue":"label-value-2"}}],"startTimeUnixNano":"1581452772000000321","timeUnixNano":"1581452773000000789","asInt":"456"}],"aggregationTemporality":"AGGREGATION_TEMPORALITY_CUMULATIVE","isMonotonic":true}}]}]}]}
{"resourceMetrics":[{"resource":{"attributes":[{"key":"resource-attr","value":{"stringValue":"resource-attr-val-1"}}]},"instrumentationLibraryMetrics":[{"instrumentationLibrary":{},"metrics":[{"name":"counter-int","unit":"1","sum":{"dataPoints":[{"attributes":[{"key":"label-1","value":{"stringValue":"label-value-1"}}],"startTimeUnixNano":"1581452773000001459","timeUnixNano":"1581452773000001459","asInt":"120"},{"attributes":[{"key":"label-2","value":{"stringValue":"label-value-2"}}],"startTimeUnixNano":"1581452773000001459","timeUnixNano":"1581452773000001459","asInt":"456"}],"aggregationTemporality":"AGGREGATION_TEMPORALITY_CUMULATIVE","isMonotonic":true}},{"name":"counter-int","unit":"1","sum":{"dataPoints":[{"attributes":[{"key":"label-1","value":{"stringValue":"label-value-1"}}],"startTimeUnixNano":"1581452773000001459","timeUnixNano":"1581452773000001459","asInt":"123"},{"attributes":[{"key":"label-2","value":{"stringValue":"label-value-2"}}],"startTimeUnixNano":"1581452773000001459","timeUnixNano":"1581452773000001459","asInt":"456"}],"aggregationTemporality":"AGGREGATION_TEMPORALITY_CUMULATIVE","isMonotonic":true}}]}]}]}
{"resourceMetrics":[{"resource":{"attributes":[{"key":"resource-attr","value":{"stringValue":"resource-attr-val-1"}}]},"instrumentationLibraryMetrics":[{"instrumentationLibrary":{},"metrics":[{"name":"counter-int","unit":"1","sum":{"dataPoints":[{"attributes":[{"key":"label-1","value":{"stringValue":"label-value-1"}}],"startTimeUnixNano":"1581452773000002346","timeUnixNano":"1581452773000002346","asInt":"121"},{"attributes":[{"key":"label-2","value":{"stringValue":"label-value-2"}}],"startTimeUnixNano":"1581452773000002346","timeUnixNano":"1581452773000002346","asInt":"456"}],"aggregationTemporality":"AGGREGATION_TEMPORALITY_CUMULATIVE","isMonotonic":true}},{"name":"counter-int","unit":"1","sum":{"dataPoints":[{"attributes":[{"key":"label-1","value":{"stringValue":"label-value-1"}}],"startTimeUnixNano":"1581452773000002346","timeUnixNano":"1581452773000002346","asInt":"123"},{"attributes":[{"key":"label-2","value":{"stringValue":"label-value-2"}}],"startTimeUnixNano":"1581452772000000321","timeUnixNano":"1581452773000000789","asInt":"456"}],"aggregationTemporality":"AGGREGATION_TEMPORALITY_CUMULATIVE","isMonotonic":true}}]}]}]}
{"resourceMetrics":[{"resource":{"attributes":[{"key":"resource-attr","value":{"stringValue":"resource-attr-val-1"}}]},"instrumentationLibraryMetrics":[{"instrumentationLibrary":{},"metrics":[{"name":"counter-int","unit":"1","sum":{"dataPoints":[{"attributes":[{"key":"label-1","value":{"stringValue":"label-value-1"}}],"startTimeUnixNano":"1581452773000007891","timeUnixNano":"1581452773000007891","asInt":"125"},{"attributes":[{"key":"label-2","value":{"stringValue":"label-value-2"}}],"startTimeUnixNano":"1581452772000000321","timeUnixNano":"1581452773000007891","asInt":"456"}],"aggregationTemporality":"AGGREGATION_TEMPORALITY_CUMULATIVE","isMonotonic":true}},{"name":"counter-int","unit":"1","sum":{"dataPoints":[{"attributes":[{"key":"label-1","value":{"stringValue":"label-value-1"}}],"startTimeUnixNano":"1581452773000007891","timeUnixNano":"1581452773000007891","asInt":"123"},{"attributes":[{"key":"label-2","value":{"stringValue":"label-value-2"}}],"startTimeUnixNano":"1581452772000000321","timeUnixNano":"1581452773000007891","asInt":"456"}],"aggregationTemporality":"AGGREGATION_TEMPORALITY_CUMULATIVE","isMonotonic":true}}]}]}]}
```

This is an example showing logs:

```json lines
{"resourceLogs":[{"resource":{"attributes":[{"key":"resource-attr","value":{"stringValue":"resource-attr-val-1"}}]},"instrumentationLibraryLogs":[{"instrumentationLibrary":{},"logs":[{"timeUnixNano":"1581452773000000789","severityNumber":"SEVERITY_NUMBER_INFO","severityText":"Info","name":"logA","body":{"stringValue":"This is a log message"},"attributes":[{"key":"app","value":{"stringValue":"server"}},{"key":"instance_num","value":{"intValue":"1"}}],"droppedAttributesCount":1,"traceId":"08040201000000000000000000000000","spanId":"0102040800000000"},{"timeUnixNano":"1581452773000000789","severityNumber":"SEVERITY_NUMBER_INFO","severityText":"Info","name":"logB","body":{"stringValue":"something happened"},"attributes":[{"key":"customer","value":{"stringValue":"acme"}},{"key":"env","value":{"stringValue":"dev"}}],"droppedAttributesCount":1,"traceId":"","spanId":""}]}]}]}
{"resourceLogs":[{"resource":{"attributes":[{"key":"resource-attr","value":{"stringValue":"resource-attr-val-1"}}]},"instrumentationLibraryLogs":[{"instrumentationLibrary":{},"logs":[{"timeUnixNano":"1581452773000001233","severityNumber":"SEVERITY_NUMBER_INFO","severityText":"Info","name":"logA","body":{"stringValue":"This is a log message"},"attributes":[{"key":"app","value":{"stringValue":"server"}},{"key":"instance_num","value":{"intValue":"1"}}],"droppedAttributesCount":1,"traceId":"08040201000000000000000000000000","spanId":"0102040800000000"},{"timeUnixNano":"1581452773000000789","severityNumber":"SEVERITY_NUMBER_INFO","severityText":"Info","name":"logB","body":{"stringValue":"something happened"},"attributes":[{"key":"customer","value":{"stringValue":"acme"}},{"key":"env","value":{"stringValue":"dev"}}],"droppedAttributesCount":1,"traceId":"","spanId":""}]}]}]}
{"resourceLogs":[{"resource":{"attributes":[{"key":"resource-attr","value":{"stringValue":"resource-attr-val-1"}}]},"instrumentationLibraryLogs":[{"instrumentationLibrary":{},"logs":[{"timeUnixNano":"1581452773000005443","severityNumber":"SEVERITY_NUMBER_INFO","severityText":"Info","name":"logA","body":{"stringValue":"This is a log message"},"attributes":[{"key":"app","value":{"stringValue":"server"}},{"key":"instance_num","value":{"intValue":"1"}}],"droppedAttributesCount":1,"traceId":"08040201000000000000000000000000","spanId":"0102040800000000"},{"timeUnixNano":"1581452773000000789","severityNumber":"SEVERITY_NUMBER_INFO","severityText":"Info","name":"logB","body":{"stringValue":"something happened"},"attributes":[{"key":"customer","value":{"stringValue":"acme"}},{"key":"env","value":{"stringValue":"dev"}}],"droppedAttributesCount":1,"traceId":"","spanId":""}]}]}]}
{"resourceLogs":[{"resource":{"attributes":[{"key":"resource-attr","value":{"stringValue":"resource-attr-val-1"}}]},"instrumentationLibraryLogs":[{"instrumentationLibrary":{},"logs":[{"timeUnixNano":"1581452773000009875","severityNumber":"SEVERITY_NUMBER_INFO","severityText":"Info","name":"logA","body":{"stringValue":"This is a log message"},"attributes":[{"key":"app","value":{"stringValue":"server"}},{"key":"instance_num","value":{"intValue":"1"}}],"droppedAttributesCount":1,"traceId":"08040201000000000000000000000000","spanId":"0102040800000000"},{"timeUnixNano":"1581452773000000789","severityNumber":"SEVERITY_NUMBER_INFO","severityText":"Info","name":"logB","body":{"stringValue":"something happened"},"attributes":[{"key":"customer","value":{"stringValue":"acme"}},{"key":"env","value":{"stringValue":"dev"}}],"droppedAttributesCount":1,"traceId":"","spanId":""}]}]}]}
```
