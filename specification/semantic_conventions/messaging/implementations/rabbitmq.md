# RabbitMQ

**Status**: [Experimental](../../../document-status.md)

## Requirements

In RabbitMQ, the destination is defined by an _exchange_ and a _routing key_.
`messaging.destination` MUST be set to the name of the exchange. This will be an empty string if the default exchange is used.

## Attributes

<!-- semconv messaging.rabbitmq -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `messaging.rabbitmq.routing_key` | string | RabbitMQ message routing key. | `myKey` | Unless it is empty. |
<!-- endsemconv -->
