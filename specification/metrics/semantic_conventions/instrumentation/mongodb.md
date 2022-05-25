# Instrumenting Mongodb

**Status**: [Experimental](../../../document-status.md)

This document defines how to apply semantic conventions when instrumenting MongoDB.

<!-- toc -->

- [mongodb Metrics](#mongodb-metrics)

<!-- tocstop -->

## Mongodb Metrics

**Description:** General mongodb metrics.

| Name                                | Instrument    | Value type | Unit       | Unit ([UCUM](../README.md#instrument-units)) | Description                         | Attribute Key | Attribute Values |
|-------------------------------------| ------------- | ---------- | ---------- | -------------------------------------------- | ----------------------------------- | ------------- | ---------------- |
| db.mongodb.cache.operation.count    | UpDownCounter | Int64      | count      | `{count}`  | The number of cache operations of the instance. | `type` | `hit`, `miss`, `misc`            |
| db.mongodb.collection.count         | UpDownCounter | Int64      | pages      | `{pages} ` | The number of collections. | `database` | The name of a database. |
| db.mongodb.data.size                | Counter       | Int64      | size       | `{size  }` | The size of the collection. Data compression does not affect this value. | `database` | The name of a database. |
| db.mongodb.connection.count         | Counter       | Int64      | count      | `{count}` | The number of connections. | `database` | The name of a database. |
|                                     |               |            |            |           |                            | `connection_type` | `active`, `available`, `current` |
| db.mongodb.extent.count             | UpDownCounter | Int64      | count      | `{count}`  | The number of extents. | `database` | The name of a database. | 
| db.mongodb.global_lock.time         | UpDownCounter | Int64      | usage      | `{usage}`  | The time the global lock has been held. | | |
| db.mongodb.index.count              | Counter       | Int64      | count      | `{count}` | The number of indexes. | `database` | The name of a database. |
| db.mongodb.index.size               | Counter       | Int64      | size       | `{size}` | Sum of the space allocated to all indexes in the database, including free index space. | `database` | The name of a database. | 
| db.mongodb.memory.usage             | Counter       | Int64      | usage      | `usage` | The amount of memory used. | `database` | The name of a database. |
|                                     |               |            |            |         |                            | `memory_type` | `resident`, `virtual` |
| db.mongodb.object.count             | Counter       | Int64      | object     | `{object}` | The number of objects. | `database` | The name of a database. |
| db.mongodb.operation.count          | Counter       | Int64      | operation  | `{operation}` | The number of operations executed. | `operation` | `insert`, `query`, `update`,`delete`,`getmore`,`command` |
| db.mongodb.storage.size             | Counter       | Int64      | size       | `{size}` | The total amount of storage allocated to this collection. | `database` | The name of a database. | 
