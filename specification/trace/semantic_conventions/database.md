# Semantic conventions for database client calls

**Status**: [Experimental](../../document-status.md)

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [Connection-level attributes](#connection-level-attributes)
  * [Notes and well-known identifiers for `db.system`](#notes-and-well-known-identifiers-for-dbsystem)
  * [Connection-level attributes for specific technologies](#connection-level-attributes-for-specific-technologies)
- [Call-level attributes](#call-level-attributes)
  * [Call-level attributes for specific technologies](#call-level-attributes-for-specific-technologies)
    + [Cassandra](#cassandra)
- [Examples](#examples)
  * [MySQL](#mysql)
  * [Redis](#redis)
  * [MongoDB](#mongodb)

<!-- tocstop -->

**Span kind:** MUST always be `CLIENT`.

The **span name** SHOULD be set to a low cardinality value representing the statement executed on the database.
It MAY be a stored procedure name (without arguments), DB statement without variable arguments, operation name, etc.
Since SQL statements may have very high cardinality even without arguments, SQL spans SHOULD be named the
following way, unless the statement is known to be of low cardinality:
`<db.operation> <db.name>.<db.sql.table>`, provided that `db.operation` and `db.sql.table` are available.
If `db.sql.table` is not available due to its semantics, the span SHOULD be named `<db.operation> <db.name>`.
It is not recommended to attempt any client-side parsing of `db.statement` just to get these properties,
they should only be used if the library being instrumented already provides them.
When it's otherwise impossible to get any meaningful span name, `db.name` or the tech-specific database name MAY be used.

## Connection-level attributes

These attributes will usually be the same for all operations performed over the same database connection.
Some database systems may allow a connection to switch to a different `db.user`, for example, and other database systems may not even have the concept of a connection at all.

<!-- semconv db(tag=connection-level) -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `db.system` | string | An identifier for the database management system (DBMS) product being used. See below for a list of well-known identifiers. | `other_sql` | Required |
| `db.connection_string` | string | The connection string used to connect to the database. It is recommended to remove embedded credentials. | `Server=(localdb)\v11.0;Integrated Security=true;` | Recommended |
| `db.user` | string | Username for accessing the database. | `readonly_user`; `reporting_user` | Recommended |
| [`net.peer.name`](span-general.md) | string | Name of the database host. [1] | `example.com` | Conditionally Required: See alternative attributes below. |
| [`net.peer.port`](span-general.md) | int | Logical remote port number | `80`; `8080`; `443` | Conditionally Required: [2] |
| [`net.sock.family`](span-general.md) | string | Protocol [address family](https://man7.org/linux/man-pages/man7/address_families.7.html) which is used for communication. | `inet6`; `bluetooth` | Conditionally Required: [3] |
| [`net.sock.peer.addr`](span-general.md) | string | Remote socket peer address: IPv4 or IPv6 for internet protocols, path for local communication, [etc](https://man7.org/linux/man-pages/man7/address_families.7.html). | `127.0.0.1`; `/tmp/mysql.sock` | See below |
| [`net.sock.peer.port`](span-general.md) | int | Remote socket peer port. | `16456` | Recommended: [4] |
| [`net.transport`](span-general.md) | string | Transport protocol used. See note below. | `ip_tcp` | Conditionally Required: [5] |

**[1]:** `net.peer.name` SHOULD NOT be set if capturing it would require an extra DNS lookup.

**[2]:** If using a port other than the default port for this DBMS and if `net.peer.name` is set.

**[3]:** If different than `inet` and if any of `net.sock.peer.addr` or `net.sock.host.addr` are set. Consumers of telemetry SHOULD expect to receive IPv6 address in `net.sock.peer.addr` without `net.sock.family` coming from instrumentations that follow previous versions of this document.

**[4]:** If defined for the address family and if different than `net.peer.port` and if `net.sock.peer.addr` is set.

**[5]:** If database type is in-process (`"inproc"`), recommended for other database types.

**Additional attribute requirements:** At least one of the following sets of attributes is required:

* [`net.peer.name`](span-general.md)
* [`net.sock.peer.addr`](span-general.md)

`db.system` has the following list of well-known values. If one of them applies, then the respective value MUST be used, otherwise a custom value MAY be used.

| Value  | Description |
|---|---|
| `other_sql` | Some other SQL database. Fallback only. See notes. |
| `mssql` | Microsoft SQL Server |
| `mysql` | MySQL |
| `oracle` | Oracle Database |
| `db2` | IBM Db2 |
| `postgresql` | PostgreSQL |
| `redshift` | Amazon Redshift |
| `hive` | Apache Hive |
| `cloudscape` | Cloudscape |
| `hsqldb` | HyperSQL DataBase |
| `progress` | Progress Database |
| `maxdb` | SAP MaxDB |
| `hanadb` | SAP HANA |
| `ingres` | Ingres |
| `firstsql` | FirstSQL |
| `edb` | EnterpriseDB |
| `cache` | InterSystems Caché |
| `adabas` | Adabas (Adaptable Database System) |
| `firebird` | Firebird |
| `derby` | Apache Derby |
| `filemaker` | FileMaker |
| `informix` | Informix |
| `instantdb` | InstantDB |
| `interbase` | InterBase |
| `mariadb` | MariaDB |
| `netezza` | Netezza |
| `pervasive` | Pervasive PSQL |
| `pointbase` | PointBase |
| `sqlite` | SQLite |
| `sybase` | Sybase |
| `teradata` | Teradata |
| `vertica` | Vertica |
| `h2` | H2 |
| `coldfusion` | ColdFusion IMQ |
| `cassandra` | Apache Cassandra |
| `hbase` | Apache HBase |
| `mongodb` | MongoDB |
| `redis` | Redis |
| `couchbase` | Couchbase |
| `couchdb` | CouchDB |
| `cosmosdb` | Microsoft Azure Cosmos DB |
| `dynamodb` | Amazon DynamoDB |
| `neo4j` | Neo4j |
| `geode` | Apache Geode |
| `elasticsearch` | Elasticsearch |
| `memcached` | Memcached |
| `cockroachdb` | CockroachDB |
<!-- endsemconv -->

### Notes and well-known identifiers for `db.system`

The list above is a non-exhaustive list of well-known identifiers to be specified for `db.system`.

If a value defined in this list applies to the DBMS to which the request is sent, this value MUST be used.
If no value defined in this list is suitable, a custom value MUST be provided.
This custom value MUST be the name of the DBMS in lowercase and without a version number to stay consistent with existing identifiers.

It is encouraged to open a PR towards this specification to add missing values to the list, especially when instrumentations for those missing databases are written.
This allows multiple instrumentations for the same database to be aligned and eases analyzing for backends.

The value `other_sql` is intended as a fallback and MUST only be used if the DBMS is known to be SQL-compliant but the concrete product is not known to the instrumentation.
If the concrete DBMS is known to the instrumentation, its specific identifier MUST be used.

Back ends could, for example, use the provided identifier to determine the appropriate SQL dialect for parsing the `db.statement`.

When additional attributes are added that only apply to a specific DBMS, its identifier SHOULD be used as a namespace in the attribute key as for the attributes in the sections below.

### Connection-level attributes for specific technologies

<!-- semconv db.mssql(tag=connection-level-tech-specific,remove_constraints) -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `db.jdbc.driver_classname` | string | The fully-qualified class name of the [Java Database Connectivity (JDBC)](https://docs.oracle.com/javase/8/docs/technotes/guides/jdbc/) driver used to connect. | `org.postgresql.Driver`; `com.microsoft.sqlserver.jdbc.SQLServerDriver` | Recommended |
| `db.mssql.instance_name` | string | The Microsoft SQL Server [instance name](https://docs.microsoft.com/en-us/sql/connect/jdbc/building-the-connection-url?view=sql-server-ver15) connecting to. This name is used to determine the port of a named instance. [1] | `MSSQLSERVER` | Recommended |

**[1]:** If setting a `db.mssql.instance_name`, `net.peer.port` is no longer required (but still recommended if non-standard).
<!-- endsemconv -->

## Call-level attributes

These attributes may be different for each operation performed, even if the same connection is used for multiple operations.
Usually only one `db.name` will be used per connection though.

<!-- semconv db(tag=call-level,remove_constraints) -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `db.name` | string | This attribute is used to report the name of the database being accessed. For commands that switch the database, this should be set to the target database (even if the command fails). [1] | `customers`; `main` | Conditionally Required: If applicable. |
| `db.statement` | string | The database statement being executed. [2] | `SELECT * FROM wuser_table`; `SET mykey "WuValue"` | Conditionally Required: [3] |
| `db.operation` | string | The name of the operation being executed, e.g. the [MongoDB command name](https://docs.mongodb.com/manual/reference/command/#database-operations) such as `findAndModify`, or the SQL keyword. [4] | `findAndModify`; `HMSET`; `SELECT` | Conditionally Required: If `db.statement` is not applicable. |

**[1]:** In some SQL databases, the database name to be used is called "schema name". In case there are multiple layers that could be considered for database name (e.g. Oracle instance name and schema name), the database name to be used is the more specific layer (e.g. Oracle schema name).

**[2]:** The value may be sanitized to exclude sensitive information.

**[3]:** If applicable and not explicitly disabled via instrumentation configuration.

**[4]:** When setting this to an SQL keyword, it is not recommended to attempt any client-side parsing of `db.statement` just to get this property, but it should be set if the operation name is provided by the library being instrumented. If the SQL statement has an ambiguous operation, or performs more than one operation, this value may be omitted.
<!-- endsemconv -->

For **Redis**, the value provided for `db.statement` SHOULD correspond to the syntax of the Redis CLI.
If, for example, the [`HMSET` command][] is invoked, `"HMSET myhash field1 'Hello' field2 'World'"` would be a suitable value for `db.statement`.

[`HMSET` command]: https://redis.io/commands/hmset

In **CouchDB**, `db.operation` should be set to the HTTP method + the target REST route according to the API reference documentation.
For example, when retrieving a document, `db.operation` would be set to (literally, i.e., without replacing the placeholders with concrete values): [`GET /{db}/{docid}`][CouchDB get doc].

In **Cassandra**, `db.name` SHOULD be set to the keyspace name.

In **HBase**, `db.name` SHOULD be set to the HBase namespace.

[CouchDB get doc]: http://docs.couchdb.org/en/stable/api/document/common.html#get--db-docid

### Call-level attributes for specific technologies

<!-- semconv db.tech(tag=call-level-tech-specific) -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `db.redis.database_index` | int | The index of the database being accessed as used in the [`SELECT` command](https://redis.io/commands/select), provided as an integer. To be used instead of the generic `db.name` attribute. | `0`; `1`; `15` | Conditionally Required: If other than the default database (`0`). |
| `db.mongodb.collection` | string | The collection being accessed within the database stated in `db.name`. | `customers`; `products` | Required |
| `db.sql.table` | string | The name of the primary table that the operation is acting upon, including the database name (if applicable). [1] | `public.users`; `customers` | Recommended |

**[1]:** It is not recommended to attempt any client-side parsing of `db.statement` just to get this property, but it should be set if it is provided by the library being instrumented. If the operation is acting upon an anonymous table, or more than one table, this value MUST NOT be set.
<!-- endsemconv -->

#### Cassandra

Separated for clarity.

<!-- semconv db.tech(tag=call-level-tech-specific-cassandra) -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `db.cassandra.page_size` | int | The fetch size used for paging, i.e. how many rows will be returned at once. | `5000` | Recommended |
| `db.cassandra.consistency_level` | string | The consistency level of the query. Based on consistency values from [CQL](https://docs.datastax.com/en/cassandra-oss/3.0/cassandra/dml/dmlConfigConsistency.html). | `all` | Recommended |
| `db.cassandra.table` | string | The name of the primary table that the operation is acting upon, including the keyspace name (if applicable). [1] | `mytable` | Recommended |
| `db.cassandra.idempotence` | boolean | Whether or not the query is idempotent. |  | Recommended |
| `db.cassandra.speculative_execution_count` | int | The number of times a query was speculatively executed. Not set or `0` if the query was not executed speculatively. | `0`; `2` | Recommended |
| `db.cassandra.coordinator.id` | string | The ID of the coordinating node for a query. | `be13faa2-8574-4d71-926d-27f16cf8a7af` | Recommended |
| `db.cassandra.coordinator.dc` | string | The data center of the coordinating node for a query. | `us-west-2` | Recommended |

**[1]:** This mirrors the db.sql.table attribute but references cassandra rather than sql. It is not recommended to attempt any client-side parsing of `db.statement` just to get this property, but it should be set if it is provided by the library being instrumented. If the operation is acting upon an anonymous table, or more than one table, this value MUST NOT be set.
<!-- endsemconv -->

## Examples

### MySQL

| Key | Value |
| :---------------------- | :----------------------------------------------------------- |
| Span name               | `"SELECT ShopDb.orders"` |
| `db.system`             | `"mysql"` |
| `db.connection_string`  | `"Server=shopdb.example.com;Database=ShopDb;Uid=billing_user;TableCache=true;UseCompression=True;MinimumPoolSize=10;MaximumPoolSize=50;"` |
| `db.user`               | `"billing_user"` |
| `net.peer.name`         | `"shopdb.example.com"` |
| `net.sock.peer.addr`    | `"192.0.2.12"` |
| `net.peer.port`         | `3306` |
| `net.transport`         | `"IP.TCP"` |
| `db.name`               | `"ShopDb"` |
| `db.statement`          | `"SELECT * FROM orders WHERE order_id = 'o4711'"` |
| `db.operation`          | `"SELECT"` |
| `db.sql.table`          | `"orders"` |

### Redis

In this example, Redis is connected using a unix domain socket and therefore the connection string and `net.sock.peer.addr` are left out.
Furthermore, `db.name` is not specified as there is no database name in Redis and `db.redis.database_index` is set instead.

| Key | Value |
| :------------------------ | :-------------------------------------------- |
| Span name                 | `"HMSET myhash"` |
| `db.system`               | `"redis"` |
| `db.connection_string`    | not set |
| `db.user`                 | not set |
| `net.peer.name`           | `"/tmp/redis.sock"` |
| `net.transport`           | `"Unix"` |
| `db.name`                 | not set |
| `db.statement`            | `"HMSET myhash field1 'Hello' field2 'World"` |
| `db.operation`            | not set |
| `db.redis.database_index` | `15` |

### MongoDB

| Key | Value |
| :---------------------- | :----------------------------------------------------------- |
| Span name               | `"products.findAndModify"` |
| `db.system`             | `"mongodb"` |
| `db.connection_string`  | not set |
| `db.user`               | `"the_user"` |
| `net.peer.name`         | `"mongodb0.example.com"` |
| `net.sock.peer.addr`    | `"192.0.2.14"` |
| `net.peer.port`         | `27017` |
| `net.transport`         | `"IP.TCP"` |
| `db.name`               | `"shopDb"` |
| `db.statement`          | not set |
| `db.operation`          | `"findAndModify"` |
| `db.mongodb.collection` | `"products"` |
