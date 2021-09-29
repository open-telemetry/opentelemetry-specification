# MongoDB

**Status**: [Experimental](../../document-status.md)

## Requirements

`db.system` MUST be set to `mongodb`.
`db.operation` MUST be set to the [MongoDB command name](https://docs.mongodb.com/manual/reference/command/#database-operations), such as `findAndModify`.

## Attributes

<!-- semconv db.mongodb(tag=call-level-tech-specific) -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `db.mongodb.collection` | string | The collection being accessed within the database stated in `db.name`. | `customers`; `products` | Yes |
<!-- endsemconv -->

## Example

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
