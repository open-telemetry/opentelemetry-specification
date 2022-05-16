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
| postgresql.blocks_read                      | UpDownCounter | Int64      | 1 | `{1}` | The number of blocks read. | | |
| postgresql.commits                          | UpDownCounter | Int64      | 1 | `{1}` | The number of commits. | | |
| postgresql.db_size                          | Counter       | Int64      | bytes | `{By}` | The database disk usage. | | |
| postgresql.backends                         | Counter       | Int64      | 1 | `{1}` | The number of backends. | | |
| postgresql.rows                             | Counter       | Int64      | 1 | `{1}` | The number of rows in the database.  | | |
| postgresql.operations                       | UpDownCounter | Int64      | 1 | `{1}` | The number of db row operations.  | | |
| postgresql.rollbacks                        | UpDownCounter | Int64      | 1 | `{1}` | The number of rollbacks. | | |