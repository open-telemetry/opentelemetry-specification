# JSON serialization

## Table of Contents

- [Overview](#overview)
- [Requirements](#requirements)
  - [Telemetry data requirements](#telemetry-data-requirements)
    - [Versioning](#versioning)
    - [Resource level](#resource-level)
    - [JSON encoding](#json-encoding)
  - [File storage requirements](#file-storage-requirements)
    - [UTF-8 preamble](#utf-8-preamble)
    - [File extension](#file-extension)
    - [Separation between objects](#separation-between-objects)
    - [Sequential append](#sequential-append)
    - [Compression](#compression)
- [Example](#example)

## Overview

This document describes the serialization of OpenTelemetry data as JSON objects, and their serialization to files.

## Requirements

### Telemetry data requirements

#### Versioning

Each object serialized to JSON should be identified with a version tagging the version of the serializer.

The deserializer must support and maintain compatibility with versions explicitly supported by this specification.

The version is serialized as a string under the key "v" of the JSON document.

#### Resource level

The JSON serialization operates at the level of `ResourceSpans`, `ResourceMetrics` and `ResourceLogs`.

There is no support for serializing objects at a lower level.

Resources are serialized under the key "rs", "rm" and "rl" respectively for `ResourceSpans`, `ResourceMetrics` and `ResourceLogs`.

#### JSON encoding

The data should be encoded according to the format specified in the [OTLP/HTTP standard](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/protocol/otlp.md#otlphttp).

### File storage requirements

#### UTF-8 preamble

The file must contain a byte order mark (BOM) of 3 bytes indicating that the file is encoded as UTF-8.

#### File extension

The file should use the `json` file extension.

#### Separation between objects

Each object should be serialized to JSON and stored to the file separated by a newline `\n` character.

#### Sequential append

Data is appended sequentially to the file, irrespective of the type of data or timestamp.

#### Compression

The file may be stored as uncompressed. Implementors are free to compress the file using gzip or tar compression algorithm as they see fit.

## Example

```json lines
{"v":"1.0.0.alpha","rs":{"resourceSpans":[{"resource":{"attributes":[{"key":"resource-attr","value":{"stringValue":"resource-attr-val-1"}}]},"instrumentationLibrarySpans":[{"instrumentationLibrary":{},"spans":[{"traceId":"","spanId":"","parentSpanId":"","name":"operationA","startTimeUnixNano":"1581452772000000321","endTimeUnixNano":"1581452773000000789","droppedAttributesCount":1,"events":[{"timeUnixNano":"1581452773000000123","name":"event-with-attr","attributes":[{"key":"span-event-attr","value":{"stringValue":"span-event-attr-val"}}],"droppedAttributesCount":2},{"timeUnixNano":"1581452773000000123","name":"event","droppedAttributesCount":2}],"droppedEventsCount":1,"status":{"deprecatedCode":"DEPRECATED_STATUS_CODE_UNKNOWN_ERROR","message":"status-cancelled","code":"STATUS_CODE_ERROR"}},{"traceId":"","spanId":"","parentSpanId":"","name":"operationB","startTimeUnixNano":"1581452772000000321","endTimeUnixNano":"1581452773000000789","links":[{"traceId":"","spanId":"","attributes":[{"key":"span-link-attr","value":{"stringValue":"span-link-attr-val"}}],"droppedAttributesCount":4},{"traceId":"","spanId":"","droppedAttributesCount":4}],"droppedLinksCount":3,"status":{}}]}]}]}}
{"v":"1.0.0.alpha","rm":{"resourceMetrics":[{"resource":{"attributes":[{"key":"resource-attr","value":{"stringValue":"resource-attr-val-1"}}]},"instrumentationLibraryMetrics":[{"instrumentationLibrary":{},"metrics":[{"name":"counter-int","unit":"1","sum":{"dataPoints":[{"attributes":[{"key":"label-1","value":{"stringValue":"label-value-1"}}],"startTimeUnixNano":"1581452772000000321","timeUnixNano":"1581452773000000789","asInt":"123"},{"attributes":[{"key":"label-2","value":{"stringValue":"label-value-2"}}],"startTimeUnixNano":"1581452772000000321","timeUnixNano":"1581452773000000789","asInt":"456"}],"aggregationTemporality":"AGGREGATION_TEMPORALITY_CUMULATIVE","isMonotonic":true}},{"name":"counter-int","unit":"1","sum":{"dataPoints":[{"attributes":[{"key":"label-1","value":{"stringValue":"label-value-1"}}],"startTimeUnixNano":"1581452772000000321","timeUnixNano":"1581452773000000789","asInt":"123"},{"attributes":[{"key":"label-2","value":{"stringValue":"label-value-2"}}],"startTimeUnixNano":"1581452772000000321","timeUnixNano":"1581452773000000789","asInt":"456"}],"aggregationTemporality":"AGGREGATION_TEMPORALITY_CUMULATIVE","isMonotonic":true}}]}]}]}}
{"v":"1.0.0.alpha","rl":{"resourceLogs":[{"resource":{"attributes":[{"key":"resource-attr","value":{"stringValue":"resource-attr-val-1"}}]},"instrumentationLibraryLogs":[{"instrumentationLibrary":{},"logs":[{"timeUnixNano":"1581452773000000789","severityNumber":"SEVERITY_NUMBER_INFO","severityText":"Info","name":"logA","body":{"stringValue":"This is a log message"},"attributes":[{"key":"app","value":{"stringValue":"server"}},{"key":"instance_num","value":{"intValue":"1"}}],"droppedAttributesCount":1,"traceId":"08040201000000000000000000000000","spanId":"0102040800000000"},{"timeUnixNano":"1581452773000000789","severityNumber":"SEVERITY_NUMBER_INFO","severityText":"Info","name":"logB","body":{"stringValue":"something happened"},"attributes":[{"key":"customer","value":{"stringValue":"acme"}},{"key":"env","value":{"stringValue":"dev"}}],"droppedAttributesCount":1,"traceId":"","spanId":""}]}]}]}}
```
