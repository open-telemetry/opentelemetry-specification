# General

The conventions described in this section are http specific. Http calls are generally fully described by Spans. By adding http labels
to metric events it allows for finely tuned filtering.

**Discaimer:** These are initial http metric instruments and labels but more may be added in the future.

### Metric Instruments

Below is a table of the metric instruments that MUST be used for http spans. They MUST be of the specified
type and units.

| Name                                | Span kind       | Type          | Units         | Description |
|-------------------------------------|-----------------|---------------|---------------|-------------|
| `http.{span.kind}.request.duration` | Client & Server | ValueRecorder | milliseconds  | measure a request duration |

### Labels

In order to make metric events as filterable as span events, http attributes
of spans should have a corresponding label on the metric event. See [http common attributes](../../trace/semantic_conventions/http.md#common-attributes)
for a list of attributes that should have corresponding labels. Due to cardinality issues some attributes MUST NOT have corresponding labels.
Below describes the details for specific attributes.

#### Included labels

Below is a table of the attributes that SHOULD be included as labels
and whether they should be on server, client, or both types of http metric events:

| Attribute name    | Span kind           | Required | Notes |
|-------------------|---------------------|----------|-------|
| `http.method`     | Client & Server     | Yes      ||
| `http.host`       | Client & Server     | see [http client attributes](../../trace/semantic_conventions/http.md#http-client) ||
| `http.scheme`     | Client & Server     | No       ||
| `http.status_code`| Client & Server     | No       ||
| `http.status_text`| Client & Server     | No       ||
| `http.flavor`     | Client & Server     | No       ||
| `net.peer.name`   | Client              | see [http client attributes](../../trace/semantic_conventions/http.md#http-client) | see [http client attributes](../../trace/semantic_conventions/http.md#http-client) for details on when to use this over `http.host` and `net.peer.ip`|
| `net.peer.port`   | Client              | see [http client attributes](../../trace/semantic_conventions/http.md#http-client) |see [http client attributes](../../trace/semantic_conventions/http.md#http-client) for details on when to use this over `http.host`|
| `net.peer.ip`     | Client              | see [http client attributes](../../trace/semantic_conventions/http.md#http-client) |see [http client attributes](../../trace/semantic_conventions/http.md#http-client) for details on when to use this over `http.host`|
| `http.server_name`| Server              | see [http server attributes](../../trace/semantic_conventions/http.md#http-server-semantic-conventions) ||
| `http.route`      | Server              | No       ||

#### Altered labels

To avoid high cardinality the following span attributes SHOULD be altered when added as labels to http metric events:

| Attribute name    | Span kind           | Required | Alteration | Notes|
|-------------------|---------------------|----------|------------|------|
|`http.url`         | Client & Server     | see [http client attributes](../../trace/semantic_conventions/http.md#http-client) | Parameterized urls should follow the same convention as [http span names](../../trace/semantic_conventions/http.md#name)| See [http server semantic conventions](../../trace/semantic_conventions/http.md#http-server-semantic-conventions) for details on when to use alternate attributes on server http metrics|
|`http.target`      | Client & Server     | see [http client attributes](../../trace/semantic_conventions/http.md#http-client) | Parameterized targets should follow the same convention as [http span names](../../trace/semantic_conventions/http.md#name)||

 #### Excluded labels

 To avoid high cardinality some http attributes that are on spans SHOULD NOT     be included as labels
 on http metric events. Below is a list of them:

* `http.user_agent`
* `http.request_content_length`
* `http.request_content_length_uncompressed`
* `http.response_content_length`
* `http.response_content_length_uncompressed`
* `http.client_ip`
* `{any attribute that captures duration}`
