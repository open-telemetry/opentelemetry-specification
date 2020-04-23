# Semantic conventions for database client calls

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [Connection-level attributes](#connection-level-attributes)
- [Call-level attributes](#call-level-attributes)

<!-- tocstop -->

For database client calls the `SpanKind` MUST be `Client`.

The _span name_ should be set to a low cardinality value representing the statement executed on the database.
It may be a stored procedure name (without arguments), SQL statement without variable arguments, operation name, etc.
When it's impossible to get any meaningful representation of the span name, it can be populated using the same value as `db.name` or the tech-specific database name.

## Connection-level attributes

These attributes will usually be the same for all operations performed over the same database connection.
Some database systems may allow a connection to switch to a different `db.user`, for example, and other database systems may not even have the concept of a connection at all.

| Attribute name | Notes and examples                                           | Required? |
| :------------- | :----------------------------------------------------------- | --------- |
| `db.type`      | Database type. For any SQL database, `"sql"`. For others, the lower-case database category, e.g., `"cassandra"`, `"hbase"`, `"mongodb"`, or `"redis"`. | Yes       |
| `db.dbms`      | An identifier for the DBMS (database management system) product. E.g., `"mssql"`, `"mysql"`, `"oracle"`, `"db2"`, `"postgresql"`. | No, but recommended for `db.type="sql"` |
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

While `db.dbms` is optional, it is strongly recommended to set it if `db.type="sql"`.
For other `db.type`s, it is still recommended but less important since there is usually only one significant implementation per type.

Note: Future version of this semantic convention could provide a list of well-known values for `db.type` and `db.dbms` to allow back ends to analyze the data further.
Back ends could, for example, use the value of `db.dbms` to determine the appropriate SQL dialect for parsing the `db.statement`.

[network attributes]: span-general.md#general-network-connection-attributes
[`net.transport`]: span-general.md#nettransport-attribute

### Connection-level attributes for specific technologies

| Technology | Attribute name | Notes and examples                                           | Required? |
| ---------- | :------------- | :----------------------------------------------------------- | --------- |
| Microsoft SQL Server | `db.mssql.instance_name` | The [instance name][] connecting to. This name is used to determine the port of a named instance. | See below. |
| JDBC Clients | `db.jdbc.driver_classname` | The fully-qualified class name of the JDBC driver used to connect, e.g., `"org.postgresql.Driver"` or `"com.microsoft.sqlserver.jdbc.SQLServerDriver"`. | No |

[instance name]: https://docs.microsoft.com/en-us/sql/connect/jdbc/building-the-connection-url?view=sql-server-ver15

- Microsoft SQL Server:
  - If setting a `db.mssql.instance_name`, `net.peer.port` is no longer required (but still recommended if non-standard).

## Call-level attributes

These attributes may be different for each operation performed, even if the same connection is used for multiple operations.
Usually only one `db.name` will be used per connection though.

| Attribute name | Notes and examples                                           | Required? |
| :------------- | :----------------------------------------------------------- | --------- |
| `db.name`  | If no tech-specific attribute is defined below, this attribute is used to report the name of the database being accessed. For commands that switch the database, this should be set to the target database (even if the command fails). | Yes (if applicable and no more specific attribute is defined) |
| `db.statement` | A database statement for the given database type. Note that the value may be sanitized to exclude sensitive information. E.g., for `db.type="sql"`, `"SELECT * FROM wuser_table"`; for `db.type="redis"`, `"SET mykey 'WuValue'"`. | Yes (if applicable)       |
| `db.operation` | The type of operation that is executed, e.g. the [MongoDB command name][] such as `findAndModify`. While it would semantically make sense to set this, e.g., to an SQL keyword like `SELECT` or `INSERT`, it is *not* recommended to attempt any client-side parsing of `db.statement` just to get this property (the back end can do that if required). | Yes, if `db.statement` is not applicable.       |

[MongoDB command name]: https://docs.mongodb.com/manual/reference/command/#database-operations

### Call-level attributes for specific technologies

| Technology | Attribute name | Notes and examples                                           | Required? |
| ---------- | :------------- | :----------------------------------------------------------- | --------- |
| Cassandra | `db.cassandra.keyspace` | The name of the keyspace being accessed. To be used instead of the general `db.name` attribute. | Yes |
| HBase | `db.hbase.namespace` | The [HBase namespace][hbase ns] being accessed. To be used instead of the general `db.name` attribute. | Yes |
| MongoDB | `db.mongodb.collection` | The collection being accessed within the database stated in `db.name`. | Yes |

[hbase ns]: https://hbase.apache.org/book.html#_namespace

In some **SQL** databases, the database name to be used for `db.name` is called "schema name".

**Redis** does not have a database name to use for `db.name`.

In **CouchDB**, `db.operation` should be set to the HTTP method + the target REST route according to the API reference documentation.
For example, when retrieving a document, `db.operation` would be set to (literally, i.e., without replacing the placeholders with concrete values): [`GET /{db}/{docid}`][CouchDB get doc].

[CouchDB get doc]: http://docs.couchdb.org/en/stable/api/document/common.html#get--db-docid
