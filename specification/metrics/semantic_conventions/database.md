# Semantic Conventions for Database Metrics

This document contains semantic conventions for database client metrics in
OpenTelemetry. When instrumenting database clients, also consider the 
[general metric semantic conventions](README.md#general-metric-semantic-conventions).

## Common

The following labels SHOULD be applied to all database metric instruments.

| Label Name             | Description  | Example  | Required |
|------------------------|--------------|----------|----------|
| `db.system`            | An identifier for the database management system (DBMS) product being used. [1] | `other_sql` | Yes |
| `db.connection_string` | The connection string used to connect to the database. It is recommended to remove embedded credentials. | `Server=(localdb)\v11.0;Integrated Security=true;` | No |
| `db.user`              | Username for accessing the database. | `readonly_user`<br>`reporting_user` | No |
| `net.transport`        | Transport protocol used. See note below. See [general network connection attributes](../../trace/semantic_conventions/span-general.md#general-network-connection-attributes). | `IP.TCP`<br>`Unix` | Conditional [2] |
| `net.peer.ip`          | Remote address of the peer (dotted decimal for IPv4 or [RFC5952](https://tools.ietf.org/html/rfc5952) for IPv6) | `127.0.0.1` | No |
| `net.peer.port`        | Remote port number. | `80`<br>`8080`<br>`443` | No |
| `net.peer.name`        | Remote hostname or similar, see note below. | `example.com` | No |


**[1]:** See the [database trace semantic conventions](../../trace/semantic_conventions/database.md#connection-level-attributes)
for the list of well-known database system values.

**[2]:** Recommended in general, required for in-process databases (`"inproc"`).

## Call-level Metric Instruments

The following metric instruments SHOULD be iterated for every database operation.

| Name                 | Instrument    | Units        | Description |
|----------------------|---------------|--------------|-------------|
| `db.client.duration` | ValueRecorder | milliseconds | The duration of the database operation. |

Database operations SHOULD include execution of queries, including DDL, DML,
DCL, and TCL SQL statements (and the corresponding operations in non-SQL
databases), as well as connect operations.

### Labels

In addition to the [common](#common) labels, the following labels SHOULD be
applied to all database call-level metric instruments.

| Label Name       | Type   | Description  | Example  | Required |
|------------------|--------|--------------|----------|----------|
| `db.name`        | string | If no [tech-specific label](#call-level-labels-for-specific-technologies) is defined, this attribute is used to report the name of the database being accessed. For commands that switch the database, this should be set to the target database (even if the command fails). [1] | `customers`<br>`main` | Required if applicable. |
| `db.operation`   | string | The name of the operation being executed, e.g. the [MongoDB command name](https://docs.mongodb.com/manual/reference/command/#database-operations) such as `findAndModify`. [4][5] | `findAndModify`<br>`HMSET`<br>`SELECT`<br>`CONNECT` | Required if applicable. |
| `db.table`       | string | The name of the primary table, collection, segment, etc... that the operation is acting upon. | `user_table` | Required if applicable. |
| `exception.type` | string | The type of the exception (its fully-qualified class name, if applicable). The dynamic type of the exception should be preferred over the static type in languages that support it. | `java.sql.SQLException`<br/>`psycopg2.OperationalError` | Required if applicable. |

**[1]:** In some SQL databases, the database name to be used is called "schema name".

**[4]:** For SQL operations, this should be set to the SQL keyword (example: `SELECT` or `INSERT`).

**[5]:** To reduce cardinality, the value for `db.operation` should have parameters
removed or substituted. The resulting value should be a low-cardinality value
represeting the statement or operation being executed on the database. It may be
a stored procedure name (without arguments), operation name, etc.

### Call-level labels for specific technologies

| Label Name                | Description  | Example  | Required |
|---------------------------|--------------|----------|----------|
| `db.cassandra.keyspace`   | The name of the keyspace being accessed. To be used instead of the generic `db.name` attribute. | `mykeyspace` | Yes |
| `db.hbase.namespace`      | The [HBase namespace](https://hbase.apache.org/book.html#_namespace) being accessed. To be used instead of the generic `db.name` attribute. | `default` | Yes |
| `db.redis.database_index` | The index of the database being accessed as used in the [`SELECT` command](https://redis.io/commands/select), provided as an integer. To be used instead of the generic `db.name` label. | `0`<br>`1`<br>`15` | Conditional [1] |
| `db.mongodb.collection`   | The collection being accessed within the database stated in `db.name`. | `customers`<br>`products` | Yes |

**[1]:** Required, if other than the default database (`0`).

## Connection Pooling Metric Instruments

Otherwise, the following metric instruments SHOULD be collected. They SHOULD
have all [common](#common) labels applied to them.

| Name                      | Instrument    | Units        | Description |
|---------------------------|---------------|--------------|-------------|
| `db.connection_pool.limit` | ValueObserver | {connections} | The total number of database connections available in the connection pool. |
| `db.connection_pool.usage` | ValueObserver | {connections} | The number of database connections _in use_. |

If the following detailed information is available, instrumentation MAY collect
the following metric instruments. They SHOULD have all [common](#common) labels
applied to them.

| Name                      | Instrument | Units         | Description |
|---------------------------|------------|---------------|-------------|
| `db.connections.new`      | Counter	 | {connections} | The number of new connections created. |
| `db.connections.taken`    | Counter	 | {connections} | The number of connections taken from the connection pool. |
| `db.connections.returned` | Counter	 | {connections} | The number of connections returned to the connection pool. |
| `db.connections.reused`   | Counter	 | {connections} | The number of connections reused. |
| `db.connections.closed`   | Counter    | {connections} | The number of connections closed. |
