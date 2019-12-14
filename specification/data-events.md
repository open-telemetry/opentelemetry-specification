# Semantic conventions for events

Event types are identified by the event name. Library and application implementors
are free to define any event name that make sense with the exception of the
following reserved names.

## Reserved event names

| Event name  | Notes and examples                                                 |
| :---------- | :----------------------------------------------------------------- |
| `"message"` | Event with the details of a single message within a span.          |
| `"error"`   | Event with the details of one captured error, fault or exception.  |

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

Most exporters will likely drop the `message.content` attribute if present.
However, logging-only exporters will likely want to log it as this information
is highly useful during the early stages of developing a new application.

## Error event attributes

Event `"name"` MUST be `"error"`.

| Attribute name | Notes and examples                     | Required? |
| :------------- | :------------------------------------- | --------- |
| `error.kind`   | The type or "kind" of an error. E.g., `"Exception"`, `"OSError"` | Yes |
| `error.message` | A concise, human-readable, one-line message explaining the event. E.g., `"Could not connect to backend"`, `"Cache invalidation succeeded"` | Yes |
| `error.object` | For languages that support such a thing (e.g., Java, Python), the actual Throwable/Exception/Error object instance itself. E.g., A `java.lang.UnsupportedOperationException` instance, a python `exceptions.NameError` instance | No |
| `error.stack` | A stack trace in platform-conventional format; may or may not pertain to an error. E.g., `"File \"example.py\", line 7, in \<module\>\ncaller()\nFile \"example.py\", line 5, in caller\ncallee()\nFile \"example.py\", line 2, in callee\nraise Exception(\"Yikes\")\n"` | No |
