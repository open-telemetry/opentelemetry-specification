# Semantic conventions for database client calls

For database client call the `SpanKind` MUST be `Client`.

Span `name` should be set to low cardinality value representing the statement
executed on the database. It may be stored procedure name (without argument), sql
statement without variable arguments, etc. When it's impossible to get any
meaningful representation of the span `name`, it can be populated using the same
value as `db.instance`.

Note, Redis, Cassandra, HBase and other storage systems may reuse the same
attribute names.

| Attribute name | Notes and examples                                           | Required? |
| :------------- | :----------------------------------------------------------- | --------- |
| `component`    | Database driver name or database name (when known) `"JDBI"`, `"jdbc"`, `"odbc"`, `"postgreSQL"`. | Yes       |
| `db.type`      | Database type. For any SQL database, `"sql"`. For others, the lower-case database category, e.g. `"cassandra"`, `"hbase"`, or `"redis"`. | Yes       |
| `db.instance`  | Database instance name. E.g., In java, if the jdbc.url=`"jdbc:mysql://db.example.com:3306/customers"`, the instance name is `"customers"`. | Yes       |
| `db.statement` | A database statement for the given database type. Note, that the value may be sanitized to exclude sensitive information. E.g., for `db.type="sql"`, `"SELECT * FROM wuser_table"`; for `db.type="redis"`, `"SET mykey 'WuValue'"`. | Yes       |
| `db.user`      | Username for accessing database. E.g., `"readonly_user"` or `"reporting_user"` | No        |

For database client calls, peer information can be populated and interpreted as
follows:

| Attribute name  | Notes and examples                                           | Required |
| :-------------- | :----------------------------------------------------------- | -------- |
| `peer.address`  | JDBC substring like `"mysql://db.example.com:3306"`          | Yes      |
| `peer.hostname` | Remote hostname. `"db.example.com"`                          | Yes      |
| `peer.ipv4`     | Remote IPv4 address as a `.`-separated tuple. E.g., `"127.0.0.1"` | No       |
| `peer.ipv6`     | Remote IPv6 address as a string of colon-separated 4-char hex tuples. E.g., `"2001:0db8:85a3:0000:0000:8a2e:0370:7334"` | No       |
| `peer.port`     | Remote port. E.g., `80` (integer)                            | No       |
| `peer.service`  | Remote service name. Can be database friendly name or `"db.instance"` | No       |