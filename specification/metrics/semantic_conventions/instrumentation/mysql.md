# Instrumenting MYSQL

**Status**: [Experimental](../../../document-status.md)

This document defines how to apply semantic conventions when instrumenting Postgres.

<!-- toc -->

- [MYSQL Metrics](#mysql-metrics)

<!-- tocstop -->

## MYSQL Metrics

**Description:** General MYSQL metrics.

| Name                                | Instrument    | Value type | Unit       | Unit ([UCUM](../README.md#instrument-units)) | Description                         | Attribute Key | Attribute Values |
|-------------------------------------| ------------- | ---------- | ---------- | -------------------------------------------- | ----------------------------------- | ------------- | ---------------- |
| db.mysql.buffer_pool.pages          | UpDownCounter | Int64      | pages      | `{pages}`  | The number of pages in the InnoDB buffer pool. | `buffer_pool_pages` | `data`, `free`, `misc`            |
| db.mysql.buffer_pool.data_pages     | UpDownCounter | Int64      | pages      | `{pages} ` | The number of data pages in the InnoDB buffer pool. | `buffer_pool_data` | `dirty`, `clean`             |
| db.mysql.buffer_pool.page_flushes   | Counter       | Int64      | flushes    | `{flushes}` | The number of requests to flush pages from the InnoDB buffer pool. | |               |
| db.mysql.buffer_pool.operations     | Counter       | Int64      | operations | `{operations}` | The number of operations on the InnoDB buffer pool. | `buffer_pool_operations` | The buffer pool operations types. |
|                                     |               |            |            |              |                                                   |           | `read_ahead_rnd`, `read_ahead`, `read_ahead_evicted`, `read_requests`, `reads`, `wait_free`, `write_requests` |
| db.mysql.buffer_pool.limit          | UpDownCounter | Int64      | limit      | `{limit}`  | The configured size of the InnoDB buffer pool. | | 
| db.mysql.buffer_pool.usage          | UpDownCounter | Int64      | usage      | `{usage}`  | The number of bytes in the InnoDB buffer pool. | `buffer_pool_data` | `dirty`, `clean` |
| db.mysql.commands                   | Counter       | Int64      | commands   | `{commands}` | The number of times each type of command has been executed. | `command` | `execute`, `close`, `fetch`, `prepare`, `reset`, `send_long_data` |
| db.mysql.handlers                   | Counter       | Int64      | handlers   | `{handlers}` | The number of requests to various MySQL handlers. | `handler` | The handler types |
|                                     |               |            |            |              |                                                   |           | `ommit`, `delete`, `discover`, `external_lock`, `mrr_init`, `prepare`, `read_first`, `read_key`, `read_last`, `read_next`, `read_prev`, `read_rnd`, `read_rnd_next`, `rollback`, `savepoint`, `savepoint_rollback`, `update`, `write` |
| db.mysql.double_writes              | Counter       | Int64      | writes     | `writes` | The number of writes to the InnoDB doublewrite buffer. | `double_writes` | `pages_written`, `writes` |
| db.mysql.log_operations             | Counter       | Int64      | operations | `{operations}` | The number of InnoDB log operations. | `log_operations` | `waits`, `write_requests`, `writes` |
| db.mysql.operations                 | Counter       | Int64      | operations | `{operations}` | The number of InnoDB operations. | `operations` | `fsyncs`, `reads`, `writes` |
| db.mysql.page_operations            | Counter       | Int64      | operations | `{operations}` | The number of InnoDB page operations. | `page_operations` | `created`, `read`, `written` | 
| db.mysql.row_locks                  | Counter       | Int64      | locks      | `{locks}`      | The number of InnoDB row locks. | `row_locks` | `waits`, `time` |
| db.mysql.row_operations             | Counter       | Int64      | operations | `{operations}` | The number of InnoDB row operations. | `row_operations` | `deleted`, `inserted`, `read`, `updated` |
| db.mysql.locks                      | Counter       | int64      | locks      | `{locks}`      | The number of MySQL locks. | `locks` | `immediate`, `waited` |
| db.mysql.sorts                      | Counter       | Int64      | sorts      | `{sorts}`      | The number of MySQL sorts. | `sorts` | `merge_passes`, `range`, `rows`, `scan` |
| db.mysql.threads                    | UpDownCounter | Int64      | threads    | `{threads}`    | The state of MySQL threads. | `threads` | `cached`, `connected`, `created`, `running` |