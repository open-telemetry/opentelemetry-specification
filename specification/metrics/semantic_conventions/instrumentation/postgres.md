# Instrumenting Postgres

**Status**: [Experimental](../../../document-status.md)

This document defines how to apply semantic conventions when instrumenting Postgres.

<!-- toc -->

- [Postgres Metrics](#postgres-metrics)

<!-- tocstop -->

## Postgres Metrics

**Description:** General Postgres metrics.

| Name                                        | Instrument    | Value type | Unit   | Unit ([UCUM](../README.md#instrument-units)) | Description    | Attribute Key | Attribute Values |
|---------------------------------------------| ------------- | ---------- | ------ | -------------------------------------------- | -------------- | ------------- | ---------------- |
| db.postgresql.blocks_read                   | Counter       | Int64      | blocks | `{blocks}`                                   | The number of blocks read. | | |
| db.postgresql.commits                       | Counter       | Int64      | commits      | `{commits}`                                        | The number of commits. | | |
| db.postgresql.db_size                       | UpDownCounter | Int64      | bytes  | `{by}`                                       | The database disk usage. | `state` | `in`, `out` |
| db.postgresql.backends                      | UpDownCounter | Int64      | backends      | `{backends}`                                        | The number of backends. | | |
| db.postgresql.rows                          | UpDownCounter | Int64      | rows   | `{rows}`                                     | The number of rows in the database.  | | |
| db.postgresql.operations                    | Counter       | Int64      | operations | `{operations}`                           | The number of db row operations.  | | |
| db.postgresql.rollbacks                     | Counter       | Int64      | rollbacks      | `{rollbacks}`                                        | The number of rollbacks. | | |