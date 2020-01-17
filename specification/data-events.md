# Semantic conventions for events

Event types are identified by the event name. Library and application implementors
are free to define any event name that make sense with the exception of the
following reserved names.

## Reserved event names

| Event name  | Notes and examples                                                 |
| :---------- | :----------------------------------------------------------------- |
| `"message"` | Event with the details of a single message within a span.          |

## Message event attributes

Event `"name"` MUST be `"message"`.

Message events MUST be associated with a tracing span.

| Attribute name | Notes and examples                     | Required? |
| :------------- | :------------------------------------- | --------- |
| `message.type` | Either `"SENT"` or `"RECEIVED"`.       | Yes |
| `message.id`   | Incremented integer value within the parent span starting with `1`. | Yes |
| `message.compressed_size` | Compressed size in bytes. | No |
| `message.uncompressed_size` | Uncompressed size in bytes. | No |
| `message.content` | The body or main contents of the message. If binary, then message should be Base64 encoded. | No |

The `message.id` MUST be calculated as two different counters starting from `1`
one for sent messages and one for received message. This way we guarantee that
the values will be consistent between different implementations. In case of
unary calls only one sent and one received message will be recorded for both
client and server spans.

Most exporters will likely drop the `message.content` attribute if present.
However, logging-only exporters will likely want to log it as this information
is highly useful during the early stages of developing a new application.
