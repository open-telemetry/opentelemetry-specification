# SQL

**Status**: [Experimental](../../document-status.md)

## Requirements

**Span name:** SQL statements may have very high cardinality even without arguments.
Unless the statement is known to be of low cardinality, SQL spans SHOULD be named `<db.operation> <db.name>.<db.sql.table>`.
If `db.sql.table` is ambiguous or unavailable, the span SHOULD be named `<db.operation> <db.name>`.
If `db.operation` is ambiguous or unavailable, the span SHOULD be named `<db.name>.<db.sql.table>`.

`db.operation` SHOULD be set to the SQL keyword. If the SQL statement has an ambiguous operation, or performs more than one operation, this value may be omitted.

It is not recommended to attempt any client-side parsing of `db.statement` to derive the values for `db.sql.table` or `db.operation`. These attributes should only be included if the library being instrumented already provides them.

## Attributes

<!-- semconv db.tech(tag=call-level-tech-specific) -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `db.sql.table` | string | The name of the primary table that the operation is acting upon, including the schema name (if applicable). [1] | `public.users`; `customers` | Recommended if available. |

**[1]:** It is not recommended to attempt any client-side parsing of `db.statement` just to get this property, but it should be set if it is provided by the library being instrumented. If the operation is acting upon an anonymous table, or more than one table, this value MUST NOT be set.
<!-- endsemconv -->