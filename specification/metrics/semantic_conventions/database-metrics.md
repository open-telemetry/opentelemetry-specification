<!--- Hugo front matter used to generate the website version of this page:
linkTitle: Database
--->

# Semantic Conventions for Database Metrics

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
| `db.client.connections.usage` | UpDownCounter | connections | `{connections}`                           | The number of connections that are currently in state described by the `state` attribute. |

All `db.client.connections.usage` measurements MUST include the following attribute:

| Name    | Type   | Description                                                                  | Examples | Requirement Level |
|---------|--------|------------------------------------------------------------------------------|----------|-------------------|
| `state` | string | The state of a connection in the pool. Valid values include: `idle`, `used`. | `idle`   | Required          |

Instrumentation libraries for database client connection pools that collect data for the following data MUST use the
following metric instruments. Otherwise, if the instrumentation library does not collect this data, these instruments
MUST NOT be used.

| Name                                     | Instrument ([*](README.md#instrument-types)) | Unit         | Unit ([UCUM](README.md#instrument-units)) | Description                                                                                       |
|------------------------------------------|----------------------------------------------|--------------|-------------------------------------------|---------------------------------------------------------------------------------------------------|
| `db.client.connections.idle.max`         | UpDownCounter                                | connections  | `{connections}`                           | The maximum number of idle open connections allowed.                                              |
| `db.client.connections.idle.min`         | UpDownCounter                                | connections  | `{connections}`                           | The minimum number of idle open connections allowed.                                              |
| `db.client.connections.max`              | UpDownCounter                                | connections  | `{connections}`                           | The maximum number of open connections allowed.                                                   |
| `db.client.connections.pending_requests` | UpDownCounter                                | requests     | `{requests}`                              | The number of pending requests for an open connection, cumulative for the entire pool.            |
| `db.client.connections.timeouts`         | Counter                                      | timeouts     | `{timeouts}`                              | The number of connection timeouts that have occurred trying to obtain a connection from the pool. |
| `db.client.connections.create_time`      | Histogram                                    | milliseconds | `ms`                                      | The time it took to create a new connection.                                                      |
| `db.client.connections.wait_time`        | Histogram                                    | milliseconds | `ms`                                      | The time it took to obtain an open connection from the pool.                                      |
| `db.client.connections.use_time`         | Histogram                                    | milliseconds | `ms`                                      | The time between borrowing a connection and returning it to the pool.                             |

Below is a table of the attributes that MUST be included on all connection pool measurements:

| Name        | Type   | Description                                                                  | Examples       | Requirement Level |
|-------------|--------|------------------------------------------------------------------------------|----------------|-------------------|
| `pool.name` | string | The name of the connection pool; unique within the instrumented application. | `myDataSource` | Required          |
