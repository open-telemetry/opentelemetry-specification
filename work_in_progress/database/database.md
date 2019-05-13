# Databases client spans

Calls to databases should be tracked as client spans.

Span `name` should be set to low cardinality value representing the statement
executed on database. It may be stored procedure name (without argument), sql
statement without variable arguments, etc. When it's impossible to get any
meaningful representation of the span `name`, it can be populated using the same
value as `db.instance`.

**TODO: we might need have separate specs for other database types like Redis
and such.**

Note, Redis, Cassandra, HBase and other storage systems may reuse the same
attribute names.

**TODO: Agree to use `type` instead of `component`?**

| Attribute name | Notes and examples |
|:---------------|:-------------------|
| `type`         | Database driver name or database name (when known) `JDBI`, `jdbc`, `odbc`, `postgreSQL`. |
| `db.type`      | Database type. For any SQL database, `"sql"`. For others, the lower-case database category, e.g. `"cassandra"`, `"hbase"`, or `"redis"`. |
| `db.instance`  | Database instance name. E.g., In java, if the jdbc.url=`"jdbc:mysql://127.0.0.1:3306/customers"`, the instance name is `"customers"`. |
| `db.statement` | A database statement for the given database type. E.g., for `db.type="sql"`, `"SELECT * FROM wuser_table"`; for `db.type="redis"`, `"SET mykey 'WuValue'"`. |
| `db.user`      | Username for accessing database. E.g., `"readonly_user"` or `"reporting_user"` |

For database client calls, peer information SHOULD be collected.

| Attribute name  | Notes and examples |
|:----------------|:-------------------|
| `peer.address`  | JDBC substring like `"mysql://prod-db:3306"` |
| `peer.hostname` | Remote hostname. `localhost` |
| `peer.ipv4`     | Remote IPv4 address as a `.`-separated tuple. E.g., `"127.0.0.1"` |
| `peer.ipv6`     | Remote IPv6 address as a string of colon-separated 4-char hex tuples. E.g., `"2001:0db8:85a3:0000:0000:8a2e:0370:7334"` |
| `peer.port`     | Remote port. E.g., `80` (integer) |
| `peer.service`  | Remote service name. Can be database friendly name or `db.instance` |
