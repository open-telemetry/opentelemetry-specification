# Compatibility Considerations for SQL Server

**Status**: [Development](../../specification/document-status.md)

This document highlights compatibility considerations for OpenTelemetry instrumentations when interacting with SQL Server.

## Context Propagation

### SET CONTEXT_INFO

Instrumentations MAY make use of [SET CONTEXT_INFO](https://learn.microsoft.com/en-us/sql/t-sql/statements/set-context-info-transact-sql?view=sql-server-ver16) to add text format of [`traceparent`](https://www.w3.org/TR/trace-context/#traceparent-header) before executing a query. This is an opt-in behavior that should be explicitly enabled by the user.

`SET CONTEXT_INFO` must be executed on the same physical connection as the SQL statement (or reuse its transaction).

Note that `SET CONTEXT_INFO` requires binary input according to its syntax: `SET CONTEXT_INFO { binary_str | @binary_var }` and has a maximum size of 128 bytes.

Example:

For a query `SELECT * FROM songs` where `traceparent` is `00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01`:

Run the following command on the same physical connection as the SQL statement:

```sql
-- The binary conversion may be done by the application or the driver.
DECLARE @BinVar varbinary(55);
SET @BinVar = CAST('00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01' AS varbinary(55));
SET CONTEXT_INFO @BinVar; 
```

Then run the query:

```sql
SELECT * FROM songs;
```