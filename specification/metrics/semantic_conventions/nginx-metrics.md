**Status**: [Experimental](../../../document-status.md)

This document defines how to apply semantic conventions when instrumenting NGINX.

<!-- toc -->

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- tocstop -->

## NGINX Metrics

**Description:** NGINX stub status module metrics.

| Name                        | Instrument    | Value type | Unit        | Unit ([UCUM](README.md#instrument-units)) | Description    | Attribute Key | Attribute Values |
| --------------------------- | ------------- | ---------- | ----------- | ----------------------------------------- | -------------- | ------------- | ---------------- |
| nginx.requests              | Counter       | Int64      | requests    | `{requests}`                              | The total number of requests made to the server since it started. | | |
| nginx.connections_accepted  | Counter       | Int64      | connections | `{connections}`                           | The total number of accepted client connections.   | | |
| nginx.connections_handled   | Counter       | Int64      | connections | `{connections}`                           | The total number of handled connections. Generally, the parameter value is the same as nginx.connections.accepted unless some resource limits have been reached (for example, the worker.connections limit) | | |
| nginx.connections_current   | UpDownCounter | Int64      | connections | `{connections}`                           | The current number of nginx.connections by state. | `state` | `active`, `reading`, `writing`, `waiting` |

