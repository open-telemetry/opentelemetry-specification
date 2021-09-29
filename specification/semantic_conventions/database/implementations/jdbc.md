# JDMC

**Status**: [Experimental](../../../document-status.md)

## Requirements

`db.system` MUST be set to `jdmc`.

## Attributes

<!-- semconv db.jdbc(tag=connection-level-tech-specific,remove_constraints) -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `db.jdbc.driver_classname` | string | The fully-qualified class name of the [Java Database Connectivity (JDBC)](https://docs.oracle.com/javase/8/docs/technotes/guides/jdbc/) driver used to connect. | `org.postgresql.Driver`; `com.microsoft.sqlserver.jdbc.SQLServerDriver` | No |
<!-- endsemconv -->