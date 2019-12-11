# Semantic conventions for asynchronous messaging spans

For call publishing a message to the bus, the `SpanKind` MUST be `Producer`.
For call retrieving a message from the bus, the `SpanKind` MUST be `Consumer`.

## Common Attributes

| Attribute name | Notes and examples                                           | Required? |
| :------------- | :----------------------------------------------------------- | --------- |
| `component`    | Denotes the type of the span and needs to be `"bus"`. | Yes |
| `message_bus.destination` | An address at which messages can be exchanged. E.g. A Kafka record has an associated "topic name" that can be extracted by the instrumented producer or consumer and stored using this tag. | Yes |
| `message_bus.type` | The brand of message bus or client API library such as `"kafka"`, `"rabbitmq"` or `"jms"`. | Yes |
| `message_bus.protocol` | The transport protocol such as `"AMQP"` or `"MQTT"`. | No |
| `message_bus.user` | Username for accessing bus. E.g., `"tibuser1"` or `"consumer_user"`. | No |
| `message_bus.url` | Connection substring such as `"tibjmsnaming://localhost:7222"` or `"https://queue.amazonaws.com/80398EXAMPLE/MyQueue"`. | No |

Additionally at least one of `net.peer.name` or `net.peer.ip` from the [network attributes][] is required and `net.peer.port` is recommended.

[network attributes]: data-span-general.md#general-network-connection-attributes
