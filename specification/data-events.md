# Semantic conventions for events

Event types are identified by the event name. Library and application implementors
are free to define any event name that make sense with the exception of the
following reserved names.

## Reserved event names

| Event name  | Notes and examples                                                 |
| :---------- | :----------------------------------------------------------------- |
| `"message"` | Event with the details of a single message within a span.          |

## Message event attributes

Each message sent/received within a span should be recorded as an event. In the
case of synchronous RPC calls there will be one sent and one received event per
span. In case of a stream span such as a gRPC stream, WebSocket or HTTP
server-sent events, there could be multiple messages with each message recorded
as an individual event.

Event `"name"` MUST be `"message"`.

Message events MUST be associated with a tracing span.

| Attribute name | Notes and examples                     | Required? |
| :------------- | :------------------------------------- | --------- |
| `message.type` | Either `"SENT"` or `"RECEIVED"`.       | Yes |
| `message.id`   | Incremented integer value within the parent span starting with `1`. | Yes |
| `message.compressed_size` | Compressed size in bytes. | No |
| `message.uncompressed_size` | Uncompressed size in bytes. | No |
| `message.content` | The body or main contents of the message. If binary, then message should be Base64 encoded. | No |

The `message.id` MUST be calculated as two different counters starting from `1`,
the first for sent messages and the second for received messages. This way we
guarantee that the values will be consistent between different implementations.
In protocols where the message id is included as a header in the message, the
received message id should be that sent be the server instead of its own
incremented value.

Most exporters will likely drop the `message.content` attribute if present.
However, logging-only exporters will likely want to log it as this information
is highly useful during the early stages of developing a new application.
