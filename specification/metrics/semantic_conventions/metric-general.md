# General

The conventions described in this section are generic; they are not specific to a
particular operation.

## Summarizing timed operations

### Justification

Timed operations are generally fully described by Spans. Because these Spans may be
sampled, aggregating information about them downstream is subject to inaccuracies.
Computing count, duration, and error rate from _all_ Spans (including `sampled=true` and
`sampled=false`) results in more accurate aggregates.

### Convention

Spans representing operations whose times should be aggregated should be summarized by
a single [`ValueRecorder`](../api.md#valuerecorder) recording duration. The instrument
name should be prefixed with the Span category and kind.

The resulting name should be `{category}.{span.kind}.duration`.
See [examples](#examples) below.

If a `duration` instrument is being created for a Span's category and kind, the duration
of all _recorded_ Spans **in milliseconds** should be recorded on to the `duration`
instrument.  The duration should be recorded onto this instrument regardless of whether
the Span is sampled.

#### Status

The `duration` instrument must include a `status` label. The value of this label must be
one of the valid Span [`StatusCanonicalCode`s](../api.md#statuscanonicalcode).

#### Labels

Labels applied to these metrics should follow the attribute semantic conventions of the
spans from which they are derived.

Care should be taken when adding labels to the duration instruments in order to avoid
excessive cardinality.

For example, adding `http.status_code` as a label to the instrument whose duration
represents HTTP client latency would be reasonable, but `http.response_code` would not.

### Examples

A simple HTTP service would create the `ValueRecorder`:

* `http.server.duration`

If this service also calls out to other HTTP services, it would create the
additional `ValueRecorder`:

* `http.client.duration`

If this service also queries one or more databases, it would create the
additional `ValueRecorder`:

* `db.client.duration`
