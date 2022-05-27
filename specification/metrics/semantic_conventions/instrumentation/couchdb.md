# Instrumenting Couchdb

**Status**: [Experimental](../../../document-status.md)

This document defines how to apply semantic conventions when instrumenting Couchdb.

<!-- toc -->

- [couchdb Metrics](#couchdb-metrics)

<!-- tocstop -->

## Couchdb Metrics

**Description:** General Couchdb metrics.

| Name                                | Instrument    | Value type | Unit       | Unit ([UCUM](../README.md#instrument-units)) | Description                         | Attribute Key | Attribute Values |
|-------------------------------------| ------------- | ---------- | ---------- | -------------------------------------------- | ----------------------------------- | ------------- | ---------------- |
| db.couchdb.average.request.time     | Gauge         | Double     | average    | `{average}`  | The average duration of a served request. | | |
| db.couchdb.httpd.bulk.request.count | UpDownCounter | Int64      | count      | `{count} ` |The number of bulk requests. | | |
| db.couchdb.httpd.request.count      | Counter       | Int64      | size       | `{count}` | The number of HTTP requests by method. | `http.method` | `COPY`, `DELETE`, `GET`, `HEAD`, `OPTIONS`, `POST`, `PUT` |
| db.couchdb.httpd.response.count     | Counter       | Int64      | count      | `{count}` | The number of connections. | ` http.status_code` | An HTTP status code. |
| db.couchdb.httpd.view.count         | Counter       | Int64      | count      | `{count}` | The number of views read. | `view` | `temporary_view_reads`, `view_reads` | 
| db.couchdb.database.open            | UpDownCounter | Int64      | open       | `{open}`  | The number of open databases. | | |
| db.couchdb.file.descriptor.open     | UpDownCounter | Int64      | count      | `{count}` | The number of open file descriptors. | | |
| db.couchdb.database.operation.count | Counter       | Int64      | count      | `{count}` | The number of database operations. | `operation` | `writes`, `reads` | 
