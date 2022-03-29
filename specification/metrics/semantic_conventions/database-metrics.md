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

| Name                          | Instrument                 | Unit        | Unit ([UCUM](README.md#instrument-units)) | Description                                                                               |
|-------------------------------|----------------------------|-------------|-------------------------------------------|-------------------------------------------------------------------------------------------|
| `db.client.connections.usage` | Asynchronous UpDownCounter | connections | `{connections}`                           | The number of connections that are currently in state described by the `state` attribute. |

All `db.client.connections.usage` measurements MUST include the following attribute:

| Name    | Type   | Description                                                                  | Examples | Required |
|---------|--------|------------------------------------------------------------------------------|----------|----------|
| `state` | string | The state of a connection in the pool. Valid values include: `idle`, `used`. | `idle`   | Yes      |

Instrumentation libraries for database client connection pools that collect data for the following data MUST use the
following metric instruments. Otherwise, if the instrumentation library does not collect this data, these instruments
MUST NOT be used.

| Name                                     | Instrument                 | Unit         | Unit ([UCUM](README.md#instrument-units)) | Description                                                                                                                                  |
|------------------------------------------|----------------------------|--------------|-------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------|
| `db.client.connections.idle.max`         | Asynchronous UpDownCounter | connections  | `{connections}`                           | The maximum number of idle open connections allowed.                                                                                         |
| `db.client.connections.idle.min`         | Asynchronous UpDownCounter | connections  | `{connections}`                           | The minimum number of idle open connections allowed.                                                                                         |
| `db.client.connections.max`              | Asynchronous UpDownCounter | connections  | `{connections}`                           | The maximum number of open connections allowed.                                                                                              |
| `db.client.connections.waiting_requests` | Asynchronous UpDownCounter | requests     | `{requests}`                              | The number of pending requests for an open connection, cumulative for the entire pool.                                                       |
| `db.client.connections.timeouts`         | Counter                    | timeouts     | `{timeouts}`                              | The number of connection timeouts that have occurred trying to obtain a connection from the pool. |
| `db.client.connections.time`             | Histogram                  | milliseconds | `ms`                                      | The time it took to apply an operation described by the `operation` attribute.                                                               |

All `db.client.connections.time` measurements MUST include the following attribute:

| Name        | Type   | Description                                                                                                                                                                                                                                | Examples | Required |
|-------------|--------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|----------|
| `operation` | string | The type of operation applied to a connection. Valid values include: `create` (time it took to create a new connection), `use` (time spent using a connection obtained from the pool), `wait` (time spent waiting for an open connection). | `create` | Yes      |

Below is a table of the attributes that MUST be included on all connection pool measurements:

| Name        | Type   | Description                                                                  | Examples       | Required |
|-------------|--------|------------------------------------------------------------------------------|----------------|----------|
| `pool.name` | string | The name of the connection pool; unique within the instrumented application. | `myDataSource` | Yes      |
