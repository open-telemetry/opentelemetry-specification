# General

The conventions described in this section are http specific.

**Discaimer:** These are initial http labels but more may be added in the future.

## Summarizing http labels

### Justification

Http calls are generally fully described by Spans. By adding http labels
to metrics it allows for finely tuned aggregation on those metrics.

### Convention

Labels applied to these metric recordings should follow the http attribute semantic
conventions of the spans from which they are derived, see
[http common attributes](../../trace/semantic_conventions/http.md#common-attributes).
To avoid high cardinality the following attributes should not be included as labels
on http metrics:

`http.user_agent`

`http.request_content_length`

`http.request_content_length_uncompressed`

`http.response_content_length`

`http.response_content_length_uncompressed`



To avoid high cardinality the following attributes should be altered:

`http.url`: parameterized urls can lead to high cardinality which is why urls should
follow the same convention as
[http span names](../../trace/semantic_conventions/http.md#name).

`http.target`: Similar to `http.url`, parameterized targets can lead to high
cardinality which is why targets should follow the same convention as
[http span names](../../trace/semantic_conventions/http.md#name).