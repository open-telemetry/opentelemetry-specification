# Semantic conventions for browser events

**Status**: [Experimental](../../../document-status.md)

<details>
<summary>Table of Contents</summary>
<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [Events](#events)
  * [PageView](#pageview)
  * [PageLoad](#pageload)
  * [PageNavigationTiming](#pagenavigationtiming)
  * [ResourceTiming](#resourcetiming)
  * [HTTP](#http)
  * [HttpRequestTiming](#httprequesttiming)
  * [Exception](#exception)
  * [UserAction](#useraction)
  * [WebVital](#webvital)

<!-- tocstop -->

</details>

This document describes the semantic conventions for browser events.

## Events

The events may be represented either as Span Events or Log Events.

All events have the following three high-level attributes. The event name is specified at the beginning of each section below. The payload of the event goes in an attribute called `event.data` of whose value is of type `map`. The contents of the `event.data` map for each event is listed in the sections below.

| Key  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `event.domain` | string | Fixed value: browser ||Required|
| `event.name` | string | Described in each section below||Required|
| `event.data` | map | A map of key/value pairs, with the keys for each event described in following sections||Recommended|

### PageView

**Event name**:  `page_view`.

| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `referrer` | string | Referring Page URI (`document.referrer`) whenever available. | `https://en.wikipedia.org/wiki/Main_Page` | Recommended |
| `type` | int | Browser page type | `0` | Required |
| `title` | string | Page title DOM property | `Shopping cart page` | Recommended |
| `url` [1] | string | Full HTTP request URL in the form `scheme://host[:port]/path?query[#fragment]`. Usually the fragment is not transmitted over HTTP, but if it is known, it should be included nevertheless. [2] | `https://en.wikipedia.org/wiki/Main_Page`; `https://en.wikipedia.org/wiki/Main_Page#foo` | Required |

**[1]:**  Alias for [`http.url`](../../../trace/semantic_conventions/http.md)
**[2]:** The URL fragment may be included for virtual pages

`type` MUST be one of the following:

| Value  | Description |
|---|---|
| `0` | physical_page |
| `1` | virtual_page |

<details>
<summary>Sample PageView Event</summary>

```json
    "log_record": {
        "timeUnixNano":"1581452773000000789",
        "attributes": [
        {
            "key": "event.domain",
            "value": {
            "stringValue": "browser"
            }
        },
        {
            "key": "event.name",
            "value": {
            "stringValue": "page_view"
            }
        },

        {
            "key": "event.data",
            "value": {
                "kvlistValue": [
                    {
                        "key": "type",
                        "value": {
                        "intValue": "0"
                        }
                    },
                    {
                        "key": "url",
                        "value": {
                        "stringValue": "https://www.guidgenerator.com/online-guid-generator.aspx"
                        }
                    },
                    {
                        "key": "referrer",
                        "value": {
                        "stringValue": "https://wwww.google.com"
                        }
                    },
                    {
                        "key": "title",
                        "value": {
                        "stringValue": "Free Online GUID Generator"
                        }
                    },
                ]
            }
        }
        ]
    }
```

</details>

### PageLoad

**Event name**:`page_load`.

| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `url` [1]| string | Full HTTP request URL in the form `scheme://host[:port]/path?query[#fragment]`. Usually the fragment is not transmitted over HTTP, but if it is known, it should be included nevertheless. [2] | `https://en.wikipedia.org/wiki/Main_Page`; `https://en.wikipedia.org/wiki/Main_Page#foo` | Required |

**[1]:** Alias for [`http.url`](../../../trace/semantic_conventions/http.md)
**[2]:** The URL fragment may be included for virtual pages

### PageNavigationTiming

**Event name**:`page_navigation_timing`

| Key  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| fetchStart | long | || Recommended |
| unloadEventStart | long | || Recommended |
| unloadEventEnd | long | || Recommended |
| domInteractive | long | || Recommended |
| domContentLoadedEventStart | long | || Recommended |
| domContentLoadedEventEnd | long | || Recommended |
| domComplete | long | || Recommended |
| loadEventStart | long | || Recommended |
| loadEventEnd | long | || Recommended |
| firstPaint | long | || Recommended |
| firstContentfulPaint | long | || Recommended |

### ResourceTiming

**Event name**:`resource_timing`

| Key  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
|fetchStart | long | || Recommended |
|domainLookupStart | long | || Recommended |
|domainLookupEnd | long | || Recommended |
|connectStart | long | || Recommended |
|secureConnectionStart | long | || Recommended |
|connectEnd | long | || Recommended |
|requestStart | long | || Recommended |
|responseStart | long | || Recommended |
|responseEnd | long | || Recommended |

### HTTP

**Event name**:`HTTP`

| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `request_type` | int | Request type | `0` | Required |
| `url` [1] | string | Full HTTP request URL in the form `scheme://host[:port]/path?query[#fragment]`. Usually the fragment is not transmitted over HTTP, but if it is known, it should be included nevertheless. [2] | `https://www.foo.bar/search?q=OpenTelemetry#SemConv` | Required |
| `method` [3] | string | HTTP request method. | `GET`; `POST`; `HEAD` | Required |
| `status_code` [4]| int | [HTTP response status code](https://tools.ietf.org/html/rfc7231#section-6). | `200` | Conditionally Required: If and only if one was received/sent. |
| `request_content_length` [5]| int | The size of the request payload body in bytes. This is the number of bytes transferred excluding headers and is often, but not always, present as the [Content-Length](https://www.rfc-editor.org/rfc/rfc9110.html#field.content-length) header. For requests using transport encoding, this should be the compressed size. | `3495` | Recommended |
| `response_content_length` [6] | int | The size of the response payload body in bytes. This is the number of bytes transferred excluding headers and is often, but not always, present as the [Content-Length](https://www.rfc-editor.org/rfc/rfc9110.html#field.content-length) header. For requests using transport encoding, this should be the compressed size. | `3495` | Recommended |
| `response_content_length_uncompressed` [7] | int | length of the response after it's uncompressed | `23421` | Recommended |
| `request.header.<key>` [8]| string[] | HTTP request headers, `<key>` being the normalized HTTP Header name (lowercase, with `-` characters replaced by `_`), the value being the header values. [9] | `http.request.header.content_type=["application/json"]`; `http.request.header.x_forwarded_for=["1.2.3.4", "1.2.3.5"]` | Optional |
| `response.header.<key>` [10]| string[] | HTTP response headers, `<key>` being the normalized HTTP Header name (lowercase, with `-` characters replaced by `_`), the value being the header values. [11] | `http.response.header.content_type=["application/json"]`; `http.response.header.my_custom_header=["abc", "def"]` | Optional |

**[1]:**  Alias for [`http.url`](../../../trace/semantic_conventions/http.md)
**[2]:** `url` MUST NOT contain credentials passed via URL in form of `https://username:password@www.example.com/`. In such case the attribute's value should be `https://www.example.com/`.
**[3]:** Alias for [`http.method`](../../../trace/semantic_conventions/http.md)
**[4]:**  Alias for [`http.status_code`](../../../trace/semantic_conventions/http.md)
**[5]:** Alias for [`http.request_content_length`](../../../trace/semantic_conventions/http.md)
**[6]:**  Alias for [`http.response_content_length`](../../../trace/semantic_conventions/http.md)
**[7]:** Alias for `http.response_content_length_uncompressed`
**[8]:** Alias for `http.request.header.<key>`
**[10]:**  Alias for `http.response.header.<key>`
**[9,11]:** Instrumentations SHOULD require an explicit configuration of which headers are to be captured. Including all request/response headers can be a security risk - explicit configuration helps avoid leaking sensitive information. The `User-Agent` header is already captured in the `browser.user_agent` resource attribute. Users MAY explicitly configure instrumentations to capture them even though it is not recommended.

`request_type` MUST be one of the following:

| Value  | Description |
|---|---|
| `0` | fetch |
| `1` | xhr |
| `2` | send_beacon |

### HttpRequestTiming

**Event name**:`http_request_timing`

| Key  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| open | long | || Recommended |
| send | long | || Recommended |
| domainLookupStart | long | || Recommended |
| domainLookupEnd | long | || Recommended |
| connectStart | long | || Recommended |
| secureConnectionStart | long | || Recommended |
| connectEnd | long | || Recommended |
| requestStart | long | || Recommended |
| responseStart | long | || Recommended |
| responseEnd | long | || Recommended |
| loaded | long | || Recommended |

### Exception

**Event name**:`exception`

| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `exception.file_name` | string | Name of the file that generated the error | `foo.js` | Recommended |
| `exception.line_number` | int | Line number where the error occurred |  | Recommended |
| `exception.column_number` | int | Column number where the error occurred |  | Recommended |
| `exception.message` | string | The exception message. | `Division by zero`; `Can't convert 'int' object to str implicitly` | Recommended |
| `exception.stacktrace` | string | A stacktrace as a string in the natural representation for the language runtime. The representation is to be determined and documented by each language SIG. | `Exception in thread "main" java.lang.RuntimeException: Test exception\n at com.example.GenerateTrace.methodB(GenerateTrace.java:13)\n at com.example.GenerateTrace.methodA(GenerateTrace.java:9)\n at com.example.GenerateTrace.main(GenerateTrace.java:5)` | Recommended |
| `exception.type` | string | The type of the exception (its fully-qualified class name, if applicable). The dynamic type of the exception should be preferred over the static type in languages that support it. | `java.net.ConnectException`; `OSError` | Recommended |

### UserAction

**Event name**:`user_action`

| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `element` | string | Target element tag name (obtained via `event.target.tagName`) | `button` | Recommended |
| `element_xpath` | string | Target element xpath | `//*[@id="testBtn"]` | Recommended |
| `user_action_type` | string | Type of interaction. See enum [here](https://github.com/microsoft/ApplicationInsights-JS/blob/941ec2e4dbd017b8450f2b17c60088ead1e6c428/extensions/applicationinsights-clickanalytics-js/src/Enums.ts) for potential values we could add support for. | `click` | Required |
| `click_coordinates` | string | Click coordinates captured as a string in the format {x}X{y}.  Eg. 345X23 | `345X23` | Recommended |
| `tags` | string[] | Grab data from data-otel-* attributes in tree | `[data-otel-asd="value" -> asd attr w/ "value"]` | Recommended |

`user_action_type` MUST be one of the following:

| Value  | Description |
|---|---|
| `click` | click |

### WebVital

**Event name**:`web_vital`

| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `name` | string | name of the web vital | `CLS` | Required |
| `value` | double | value of the web vital | `1.0`; `2.0` | Required |
| `delta` | double | The delta between the current value and the last-reported value | `0.2` | Required |
| `id` | string | A unique ID representing this particular metric instance | "v3-1677874579383-6381583661209" | Required |

`name` MUST be one of the following:

| Value  | Description |
|---|---|
| `CLS` | cls |
| `LCP` | lcp |
| `FID` | fid |
