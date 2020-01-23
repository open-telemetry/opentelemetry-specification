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
| `message.id`   | Unique identifier within a span and `message.type` for the individual message. Further specifications for common protocols are discussed below. | No |
| `message.compressed_size` | Compressed size in bytes. | No |
| `message.uncompressed_size` | Uncompressed size in bytes. | No |
| `message.content` | The body or main contents of the message. If binary, then message should be Base64 encoded. | No |

To conserve bandwith and/or storage, exporters MAY drop the `message.content`
attribute if present. Logging-only exporters bundled with default OpenTelemetry
SDKs SHOULD provide affordances for logging this information as it is highly
useful during the early stages of developing a new application.

### Representative message.id attribute values

#### gRPC

For [gRPC], `message.id` MUST be calculated as two different counters starting
from `1`, the first for sent messages and the second for received messages.
This way we guarantee that the values will be consistent between different
implementations. Server streaming, client streaming and bidirectional streaming
RPCs provided gRPC all guarantee message ordering so there should be no
discrepencies between the sender and receiver spans.

#### Server-Sent Events

For [Server-Sent Events] included in the HTML5 specification, `message.id` MUST
match the `id` field of an event if it does not contain U+0000 NULL. Otherwise,
the attribute should not be populated. This is equivalent to what gets populated
to the last event ID buffer of the `EventSource` object specified in the SSE
specification.

#### Java Message Service (JMS)

For JMS, `message.id` SHOULD be set to the value of the `JMSMessageID`field
exposed by [JMS Message]. This value uniquely identifies each message sent by
a provider.

[gRPC]: https://www.grpc.io/docs/guides/concepts/
[Server-Sent Events]: https://html.spec.whatwg.org/multipage/server-sent-events.html
[JMS Message]: https://docs.oracle.com/javaee/7/api/javax/jms/Message.html
