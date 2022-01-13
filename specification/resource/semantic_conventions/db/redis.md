# Redis

**Status**: [Experimental](../../document-status.md)

**type:** `db.redis`

**Description:** A redis instance

<!-- semconv redis -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `db.redis.instance` | string | Reported name of the Redis instance. This can be in the form `{host}:{port}` or any other name provided manually while configuring the instrumentation and defaults to the `endpoint` value provided in the configuration. | `localhost:6379`; `product_info_redis` | No |
<!-- endsemconv -->