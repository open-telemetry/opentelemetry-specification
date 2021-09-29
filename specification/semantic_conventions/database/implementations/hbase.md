# HBase

**Status**: [Experimental](../../../document-status.md)

## Requirements

`db.system` MUST be set to `hbase`.

## Attributes

<!-- semconv db.hbase(tag=call-level-tech-specific) -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `db.hbase.namespace` | string | The [HBase namespace](https://hbase.apache.org/book.html#_namespace) being accessed. To be used instead of the generic `db.name` attribute. | `default` | Yes |
<!-- endsemconv -->