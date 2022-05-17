# Instrumenting Postgres

**Status**: [Experimental](../../../document-status.md)

This document defines how to apply semantic conventions when instrumenting Postgres.

<!-- toc -->

- [Postgres Metrics](#postgres-metrics)

<!-- tocstop -->

## Postgres Metrics

**Description:** General Postgres metrics.

| Name                                        | Instrument    | Value type | Unit       | Unit ([UCUM](../README.md#instrument-units)) | Description                         | Attribute Key | Attribute Values                                                                                   |
|---------------------------------------------| ------------- | ---------- | ------     | -------------------------------------------- | --------------                      | ------------- | -------------------------------------------------------------------------------------------------- |
| db.postgresql.blocks_read                   | Counter       | Int64      | blocks     | `{blocks}`                                   | The number of blocks read.          | `database`    |  The name of the database.                                                                         |
|                                             |               |            |            |                                              |                                     | `table`       |  The schema name followed by the table name                                                        |
|                                             |               |            |            |                                              |                                     | `source`      | `heap_read`, `heap_hit`, `idx_read`, `idx_hit`, `toast_read`, `toast_hit`, `tidx_read`, `tidx_hit` |             
| db.postgresql.commits                       | Counter       | Int64      | commits    | `{commits}`                                  | The number of commits.              | `database`    |  The name of the database.                                                                         |
| db.postgresql.db_size                       | UpDownCounter | Int64      | bytes      | `{by}`                                       | The database disk usage.            | `database`    |  The name of the database.                                                                         |
| db.postgresql.backends                      | UpDownCounter | Int64      | backends   | `{backends}`                                 | The number of backends.             | `database`    |  The name of the database.                                                                         |
| db.postgresql.rows                          | UpDownCounter | Int64      | rows       | `{rows}`                                     | The number of rows in the database. | `database`    |  The name of the database.                                                                         |
|                                             |               |            |            |                                              |                                     | `table`       |  The schema name followed by the table name                                                        |
|                                             |               |            |            |                                              |                                     | `state`       |  `dead`, `live`                                                                                    |
| db.postgresql.operations                    | Counter       | Int64      | operations | `{operations}`                               | The number of db row operations.    | `database`    |  The name of the database.                                                                         |
|                                             |               |            |            |                                              |                                     | `table`       |  The schema name followed by the table name                                                        |
|                                             |               |            |            |                                              |                                     | `source`      | `ins`, `upd`, `del`, `hot_upd`                                                                     |
| db.postgresql.rollbacks                     | Counter       | Int64      | rollbacks  | `{rollbacks}`                                | The number of rollbacks.            | `database`    |  The name of the database.                                                                         |