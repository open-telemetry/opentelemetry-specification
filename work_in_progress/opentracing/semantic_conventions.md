# Semantic Conventions

The [OpenTracing Specification](https://github.com/opentracing/specification/blob/master/specification.md) describes the overarching language-neutral data model and API guidelines for OpenTracing. That data model includes the related concepts of **Span Tags** and **(structured) Log Fields**; though these terms are defined in the specification, there is no guidance there about standard Span tags or logging keys.

Those semantic conventions are described by this document. The document is divided into two sections: first, tables listing all standard Span tags and logging keys; then guidance about how to combine these to model certain important semantic concepts.

### Versioning

Changes to this file affect the OpenTracing specification version. Additions should bump the minor version, and backwards-incompatible changes (or perhaps very large additions) should bump the major version.

## Standard Span tags and log fields

### Span tags table

Span tags apply to **the entire Span**; as such, they apply to the entire timerange of the Span, not a particular moment with a particular timestamp: those sorts of events are best modelled as Span log fields (per the table in the next subsection of this document).

> Work in progress! Please note, that the list below only contains attributes that aren't contained in the [OpenTelemetry main spec](../../specification/data-semantic-conventions.md) (yet):

| Span tag name | Type | Notes and examples |
|:--------------|:-----|:-------------------|
| `message_bus.destination` | string | An address at which messages can be exchanged. E.g. A Kafka record has an associated `"topic name"` that can be extracted by the instrumented producer or consumer and stored using this tag. |
| `peer.address` | string | Remote "address", suitable for use in a networking client library. This may be a `"ip:port"`, a bare `"hostname"`, a FQDN or various connection strings |
| `peer.hostname` | string | Remote hostname. E.g., `"opentracing.io"`, `"internal.dns.name"` |
| `peer.ipv4` | string | Remote IPv4 address as a `.`-separated tuple. E.g., `"127.0.0.1"` |
| `peer.ipv6` | string | Remote IPv6 address as a string of colon-separated 4-char hex tuples. E.g., `"2001:0db8:85a3:0000:0000:8a2e:0370:7334"` |
| `peer.port` | integer | Remote port. E.g., `80` |
| `peer.service` | string | Remote service name (for some unspecified definition of `"service"`). E.g., `"elasticsearch"`, `"a_custom_microservice"`, `"memcache"` |
| `sampling.priority` | integer | If greater than 0, a hint to the Tracer to do its best to capture the trace. If 0, a hint to the trace to not-capture the trace. If absent, the Tracer should use its default sampling mechanism. |

### Log fields table

Every Span log has a specific timestamp (which must fall between the start and finish timestamps of the Span, inclusive) and one or more **fields**. What follows are the standard fields.

| Span log field name | Type    | Notes and examples |
|:--------------------|:--------|:-------------------|
| `error.kind` | string | The type or "kind" of an error (only for `event="error"` logs). E.g., `"Exception"`, `"OSError"` |
| `error.object` | object | For languages that support such a thing (e.g., Java, Python), the actual Throwable/Exception/Error object instance itself. E.g., A `java.lang.UnsupportedOperationException` instance, a python `exceptions.NameError` instance |
| `event` | string | A stable identifier for some notable moment in the lifetime of a Span. For instance, a mutex lock acquisition or release or the sorts of lifetime events in a browser page load described in the [Performance.timing](https://developer.mozilla.org/en-US/docs/Web/API/PerformanceTiming) specification. E.g., from [Zipkin](https://zipkin.io/pages/instrumenting.html#core-data-structures), `"cs"`, `"sr"`, `"ss"`, or `"cr"`. Or, more generally, `"initialized"` or `"timed out"`. For errors, `"error"` |
| `message` | string | A concise, human-readable, one-line message explaining the event. E.g., `"Could not connect to backend"`, `"Cache invalidation succeeded"` |
| `stack` | string | A stack trace in platform-conventional format; may or may not pertain to an error. E.g., `"File \"example.py\", line 7, in \<module\>\ncaller()\nFile \"example.py\", line 5, in caller\ncallee()\nFile \"example.py\", line 2, in callee\nraise Exception(\"Yikes\")\n"` |

## Modelling special circumstances

### RPCs

The following Span tags combine to model RPCs:

- `span.kind`: either `"client"` or `"server"`. It is important to provide this tag **at Span start time**, as it may affect internal ID generation.
- `peer.address`, `peer.hostname`, `peer.ipv4`, `peer.ipv6`, `peer.port`, `peer.service`: optional tags that describe the RPC peer (often in ways it cannot assess internally)

### Message Bus

A message bus is asynchronous, and therefore the relationship type used to link a Consumer Span and a Producer Span would be **Follows From** (see [References between Spans](https://github.com/opentracing/specification/blob/master/specification.md#references-between-spans) for more information on relationship types).

The following Span tags combine to model message bus based communications:

- `message_bus.destination`: as described in the table above
- `span.kind`: either `"producer"` or `"consumer"`. It is important to provide this tag **at Span start time**, as it may affect internal ID generation.
- `peer.address`, `peer.hostname`, `peer.ipv4`, `peer.ipv6`, `peer.port`, `peer.service`: optional tags that describe the message bus broker (often in ways it cannot assess internally)

### Captured errors

Errors may be described by OpenTracing in different ways, largely depending on the language. Some of these descriptive fields are specific to errors; others are not (e.g., the `event` or `message` fields).

For languages where an error object encapsulates a stack trace and type information, log the following fields:

- event=`"error"`
- error.object=`<error object instance>`

For other languages, or when above is not feasible:

- event=`"error"`
- message=`"..."`
- stack=`"..."` (optional)
- error.kind=`"..."` (optional)

This scheme allows Tracer implementations to extract what information they need from the actual error object when it's available.
