# Semantic conventions for database client calls

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [Connection-level attributes](#connection-level-attributes)
  * [Notes and well-known identifiers for `db.system`](#notes-and-well-known-identifiers-for-dbsystem)
  * [Connection-level attributes for specific technologies](#connection-level-attributes-for-specific-technologies)
- [Call-level attributes](#call-level-attributes)
  * [Call-level attributes for specific technologies](#call-level-attributes-for-specific-technologies)
- [Examples](#examples)
  * [MySQL](#mysql)
  * [Redis](#redis)
  * [MongoDB](#mongodb)

<!-- tocstop -->

**Span kind:** MUST always be `CLIENT`.

The **span name** SHOULD be set to a low cardinality value representing the statement executed on the database.
It may be a stored procedure name (without arguments), SQL statement without variable arguments, operation name, etc.
When it's otherwise impossible to get any meaningful span name, `db.name` or the tech-specific database name MAY be used.

## Connection-level attributes

These attributes will usually be the same for all operations performed over the same database connection.
Some database systems may allow a connection to switch to a different `db.user`, for example, and other database systems may not even have the concept of a connection at all.

| Attribute name | Notes and examples                                           | Required? |
| :------------- | :----------------------------------------------------------- | --------- |
| `db.system`    | An identifier for the database management system (DBMS) product being used. See below for a [list of well-known identifiers](#notes-and-well-known-identifiers-for-dbsystem). | Yes       |
| `db.connection_string` | The connection string used to connect to the database. It is recommended to remove embedded credentials. | No       |
| `db.user`      | Username for accessing the database, e.g., `"readonly_user"` or `"reporting_user"` | No        |
| `net.peer.name` | Defined in the general [network attributes][]. | See below |
| `net.peer.ip`   | Defined in the general [network attributes][]. | See below |
| `net.peer.port` | Defined in the general [network attributes][]. | See below |
| `net.transport` | Defined in the general [network attributes][]. | See below |

At least one of `net.peer.name` or `net.peer.ip` from the [network attributes][] is required and `net.peer.port` is recommended.
If using a port other than the default port for this DBMS, `net.peer.port` is required.
Furthermore, it is strongly recommended to add the [`net.transport`][] attribute and follow its guidelines.
For in-process databases, `net.transport` MUST be set to `"inproc"`.

[network attributes]: span-general.md#general-network-connection-attributes
[`net.transport`]: span-general.md#nettransport-attribute

### Notes and well-known identifiers for `db.system`

This is a non-exhaustive list of well-known identifiers to be specified for `db.system`.

If a value defined in this list applies to the DBMS to which the request is sent, this value MUST be used.
If no value defined in this list is suitable, a custom value MUST be provided.
This custom value MUST be the name of the DBMS in lowercase and without a version number to stay consistent with existing identifiers.

It is encouraged to open a PR towards this specification to add missing values to the list, especially when instrumentations for those missing databases are written.
This allows multiple instrumentations for the same database to be aligned and eases analyzing for backends.

The value `other_sql` is intended as a fallback and MUST only be used if the DBMS is known to be SQL-compliant but the concrete product is not known to the instrumentation.
If the concrete DBMS is known to the instrumentation, its specific identifier MUST be used.

| Value for `db.system` | Product name              | Note                           |
| :-------------------- | :------------------------ | :----------------------------- |
| `"db2"`               | IBM Db2                   |                                |
| `"derby"`             | Apache Derby              |                                |
| `"hive"`              | Apache Hive               |                                |
| `"mariadb"`           | MariaDB                   |                                |
| `"mssql"`             | Microsoft SQL Server      |                                |
| `"mysql"`             | MySQL                     |                                |
| `"oracle"`            | Oracle Database           |                                |
| `"postgresql"`        | PostgreSQL                |                                |
| `"sqlite"`            | SQLite                    |                                |
| `"teradata"`          | Teradata                  |                                |
| `"other_sql"`         | Some other SQL Database   | Fallback only. See note above. |
| `"cassandra"`         | Cassandra                 |                                |
| `"cosmosdb"`          | Microsoft Azure Cosmos DB |                                |
| `"couchbase"`         | Couchbase                 |                                |
| `"couchdb"`           | CouchDB                   |                                |
| `"dynamodb"`          | Amazon DynamoDB           |                                |
| `"hbase"`             | HBase                     |                                |
| `"mongodb"`           | MongoDB                   |                                |
| `"neo4j"`             | Neo4j                     |                                |
| `"redis"`             | Redis                     |                                |

Back ends could, for example, use the provided identifier to determine the appropriate SQL dialect for parsing the `db.statement`.

When additional attributes are added that only apply to a specific DBMS, its identifier SHOULD be used as a namespace in the attribute key as for the attributes in the sections below.

### Connection-level attributes for specific technologies

| Technology | Attribute name | Notes and examples                                           | Required? |
| ---------- | :------------- | :----------------------------------------------------------- | --------- |
| Microsoft SQL Server | `db.mssql.instance_name` | The [instance name][] connecting to. This name is used to determine the port of a named instance. | See below. |
| JDBC Clients | `db.jdbc.driver_classname` | The fully-qualified class name of the [Java Database Connectivity (JDBC)][jdbc] driver used to connect, e.g., `"org.postgresql.Driver"` or `"com.microsoft.sqlserver.jdbc.SQLServerDriver"`. | No |

[instance name]: https://docs.microsoft.com/en-us/sql/connect/jdbc/building-the-connection-url?view=sql-server-ver15
[jdbc]: https://docs.oracle.com/javase/8/docs/technotes/guides/jdbc/

- Microsoft SQL Server:
  - If setting a `db.mssql.instance_name`, `net.peer.port` is no longer required (but still recommended if non-standard).

## Call-level attributes

These attributes may be different for each operation performed, even if the same connection is used for multiple operations.
Usually only one `db.name` will be used per connection though.

| Attribute name | Notes and examples                                           | Required? |
| :------------- | :----------------------------------------------------------- | --------- |
| `db.name`  | If no [tech-specific attribute](#call-level-attributes-for-specific-technologies) is defined in the list below, this attribute is used to report the name of the database being accessed. For commands that switch the database, this should be set to the target database (even if the command fails). | Yes (if applicable and no more specific attribute is defined) |
| `db.statement` | The database statement being executed. Note that the value may be sanitized to exclude sensitive information. E.g., for `db.system="other_sql"`, `"SELECT * FROM wuser_table"`; for `db.system="redis"`, `"SET mykey 'WuValue'"`. | Yes (if applicable)       |
| `db.operation` | The name of the operation being executed, e.g. the [MongoDB command name][] such as `findAndModify`. While it would semantically make sense to set this, e.g., to an SQL keyword like `SELECT` or `INSERT`, it is *not* recommended to attempt any client-side parsing of `db.statement` just to get this property (the back end can do that if required). | Yes, if `db.statement` is not applicable.       |

[MongoDB command name]: https://docs.mongodb.com/manual/reference/command/#database-operations

In some **SQL** databases, the database name to be used for `db.name` is called "schema name".

For **Redis**, the value provided for `db.statement` SHOULD correspond to the syntax of the Redis CLI.
If, for example, the [`HMSET` command][] is invoked, `"HMSET myhash field1 'Hello' field2 'World'"` would be a suitable value for `db.statement`.

[`HMSET` command]: https://redis.io/commands/hmset

In **CouchDB**, `db.operation` should be set to the HTTP method + the target REST route according to the API reference documentation.
For example, when retrieving a document, `db.operation` would be set to (literally, i.e., without replacing the placeholders with concrete values): [`GET /{db}/{docid}`][CouchDB get doc].

[CouchDB get doc]: http://docs.couchdb.org/en/stable/api/document/common.html#get--db-docid

### Call-level attributes for specific technologies

| Technology | Attribute name            | Notes and examples                                           | Required? |
| ---------- | :------------------------ | :----------------------------------------------------------- | --------- |
| Cassandra  | `db.cassandra.keyspace`   | The name of the keyspace being accessed. To be used instead of the generic `db.name` attribute. | Yes |
| HBase      | `db.hbase.namespace`      | The [HBase namespace][] being accessed. To be used instead of the generic `db.name` attribute. | Yes |
| Redis      | `db.redis.database_index` | The index of the database being accessed as used in the [`SELECT` command], provided as an integer. To be used instead of the generic `db.name` attribute. | Yes, if other than the default database (`0`) |
| MongoDB    | `db.mongodb.collection`   | The collection being accessed within the database stated in `db.name`. | Yes |

[HBase namespace]: https://hbase.apache.org/book.html#_namespace
[`SELECT` command]: https://redis.io/commands/select

## Examples

### MySQL

| Key | Value |
| :---------------------- | :----------------------------------------------------------- |
| Span name               | `"SELECT * FROM orders WHERE order_id = ?"` |
| `db.system`             | `"mysql"` |
| `db.connection_string`  | `"Server=shopdb.example.com;Database=ShopDb;Uid=billing_user;TableCache=true;UseCompression=True;MinimumPoolSize=10;MaximumPoolSize=50;"` |
| `db.user`               | `"billing_user"` |
| `net.peer.name`         | `"shopdb.example.com"` |
| `net.peer.ip`           | `"192.0.2.12"` |
| `net.peer.port`         | `3306` |
| `net.transport`         | `"IP.TCP"` |
| `db.name`               | `"ShopDb"` |
| `db.statement`          | `"SELECT * FROM orders WHERE order_id = 'o4711'"` |
| `db.operation`          | not set |

### Redis

In this example, Redis is connected using a unix domain socket and therefore the connection string and `net.peer.ip` are left out.
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
| `net.peer.ip`           | `"192.0.2.14"` |
| `net.peer.port`         | `27017` |
| `net.transport`         | `"IP.TCP"` |
| `db.name`               | `"shopDb"` |
| `db.statement`          | not set |
| `db.operation`          | `"findAndModify"` |
| `db.mongodb.collection` | `"products"` |
