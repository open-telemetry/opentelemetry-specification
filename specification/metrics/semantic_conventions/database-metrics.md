# General

**Status**: [Experimental](../../document-status.md)

The conventions described in this section are specific to SQL and NoSQL clients.

**Disclaimer:** These are initial database client metric instruments and attributes but more may be added in the future.

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [Metric Instruments](#metric-instruments)
  * [Connection pools](#connection-pools)

<!-- tocstop -->

## Metric Instruments

The following metric instruments MUST be used to describe database client operations. They MUST be of the specified type
and units.

### Connection pools

Below is a table of database client connection pool metric instruments that MUST be used by connection pool
instrumentations:

| Name                    | Instrument                 | Unit         | Unit ([UCUM](README.md#instrument-units)) | Description |
|-------------------------|----------------------------|--------------|-------------------------------------------|-------------|
| `db.connections.total`  | Asynchronous UpDownCounter | connections  | `{connections}`                           | The total number of open connections.
| `db.connections.active` | Asynchronous UpDownCounter | connections  | `{connections}`                           | The number of open connections that are currently in use.
| `db.connections.idle`   | Asynchronous UpDownCounter | connections  | `{connections}`                           | The number of open connections that are currently idle.

Instrumentation libraries for database server connection pools that collect data for the following data MUST use the
following metric instruments. Otherwise, if the instrumentation library does not collect this data, these instruments
MUST NOT be used.

| Name                             | Instrument                 | Unit         | Unit ([UCUM](README.md#instrument-units)) | Description |
|----------------------------------|----------------------------|--------------|-------------------------------------------|-------------|
| `db.connections.idle.max`        | Asynchronous UpDownCounter | connections  | `{connections}`                           | The maximum number of idle open connections allowed.
| `db.connections.idle.min`        | Asynchronous UpDownCounter | connections  | `{connections}`                           | The minimum number of idle open connections allowed.
| `db.connections.max`             | Asynchronous UpDownCounter | connections  | `{connections}`                           | The maximum number of open connections allowed.
| `db.connections.pending_threads` | Asynchronous UpDownCounter | threads      | `{threads}`                               | The number of threads that are currently waiting for an open connection.
| `db.connections.timeouts`        | Counter                    | timeouts     | `{timeouts}`                              | The number of connection timeouts that have happened since the application start.
| `db.connections.time`            | Histogram                  | milliseconds | `ms`                                      | The time it took to apply an operation described by the `operation` attribute.

Below is a table of the attributes that MUST be included on connection pool metric events:

| Name        | Type   | Description                                                                  | Examples       | Required |
|-------------|--------|------------------------------------------------------------------------------|----------------|----------|
| `pool.name` | string | The name of the connection pool; unique within the instrumented application. | `myDataSource` | Yes      |

The `db.connections.time` metric events MUST include the following attribute:

| Name        | Type   | Description                                                                                   | Examples       | Required |
|-------------|--------|-----------------------------------------------------------------------------------------------|----------------|----------|
| `operation` | string | The type of operation applied to a connection. Valid values include: `create`, `use`, `wait`. | `create` | Yes      |
