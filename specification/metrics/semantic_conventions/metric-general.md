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

When creating duration metrics from Spans, the duration **in seconds** of all
_recorded_ Spans of a given category and kind should be aggregated together in a single
[`ValueRecorder`](../api.md#valuerecorder).

The instrument's name should be prefixed with a category and the Span's kind,
using the pattern `{category}.{span.kind}.duration`.

If the duration is derived from Spans that follow one of the common semantic-conventional
_areas_, the category should be the label prefix used in that semantic convention.

For example:

* `http.server.duration`
* `http.client.duration`
* `db.client.duration`

#### Labels

Labels applied to these metric recordings should follow the attribute semantic conventions
of the corresponding Span for the operation.

Care should be taken when adding labels to the duration instruments in order to avoid
excessive cardinality.

For example, adding `http.status_code` as a label to the instrument whose duration
represents HTTP client latency would be reasonable, but `http.response_content_length`
would not.
