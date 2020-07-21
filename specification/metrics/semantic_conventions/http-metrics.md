# General

The conventions described in this section are http specific.

**Discaimer:** These are initial http labels but more may be added in the future.

## Summarizing http labels

### Justification

Http calls are generally fully described by Spans. By adding http labels
to metrics it allows for finely tuned aggregation on those metrics.

### Convention

### Labels

Labels applied to these metric recordings should follow the http attribute semantic
conventions of the spans from which they are derived, see
[http common attributes](../../trace/semantic_conventions/http.md#common-attributes).

#### Included labels

Below is a table of the attributes that **should** be included as labels
and whether they should be on server, client, or both http metrics:

| Attribute name    | Span kind| Notes |
|-------------------|----------|-------|
| `http.method`     | Both     ||
| `http.host`       | Both     ||
| `http.scheme`     | Both     ||
| `http.status_code`| Both     ||
| `http.status_text`| Both     ||
| `http.flavor`     | Both     ||
| `net.peer.name`   | Client   | see [http client attributes](../../trace/semantic_conventions/http.md#http-client) for details on when to use this over `http.host` and `net.peer.ip`|
| `net.peer.port`   | Client   |see [http client attributes](../../trace/semantic_conventions/http.md#http-client) for details on when to use this over `http.host`|
| `net.peer.ip`     | Client   |see [http client attributes](../../trace/semantic_conventions/http.md#http-client) for details on when to use this over `http.host`|
| `http.server_name`| Server   ||
| `http.route`      | Server   ||

#### Altered labels

To avoid high cardinality the following attributes should be altered:

| Attribute name    | Span kind| Alteration | Notes|
|-------------------|----------|------------|------|
|`http.url`         | Both     | Parameterized urls should follow the same convention as [http span names](../../trace/semantic_conventions/http.md#name)| See [http server semantic conventions](../../trace/semantic_conventions/http.md#http-server-semantic-conventions) for details on when to use alternate attributes on server http metrics|
|`http.target`      | Both     | Parameterized targets should follow the same convention as [http span names](../../trace/semantic_conventions/http.md#name)||

 #### Excluded labels

 To avoid high cardinality some attributes **should not** be included as labels
 on http metrics. Below is a list of them:

    http.user_agent
    http.request_content_length
    http.request_content_length_uncompressed
    http.response_content_length
    http.response_content_length_uncompressed
    http.client_ip
