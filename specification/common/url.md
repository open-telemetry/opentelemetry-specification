# Semantic conventions for URL

**Status**: [Experimental](../document-status.md)

This document defines semantic conventions that describe URL and its components.

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [Attributes](#attributes)
- [Sensitive information](#sensitive-information)

<!-- tocstop -->

</details>

## Attributes

<!-- semconv url -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `url.scheme` | string | The [URI scheme](https://www.rfc-editor.org/rfc/rfc3986#section-3.1) component identifying the used protocol. | `https`; `ftp`; `telnet` | Recommended |
| `url.full` | string | Absolute URL describing a network resource according to [RFC3986](https://www.rfc-editor.org/rfc/rfc3986) [1] | `https://www.foo.bar/search?q=OpenTelemetry#SemConv`; `//localhost` | Recommended |
| `url.path` | string | The [URI path](https://www.rfc-editor.org/rfc/rfc3986#section-3.3) component [2] | `/search` | Recommended |
| `url.query` | string | The [URI query](https://www.rfc-editor.org/rfc/rfc3986#section-3.4) component [3] | `q=OpenTelemetry` | Recommended |
| `url.fragment` | string | The [URI fragment](https://www.rfc-editor.org/rfc/rfc3986#section-3.5) component | `SemConv` | Recommended |

**[1]:** For network calls, URL usually has `scheme://host[:port][path][?query][#fragment]` format, where the fragment is not transmitted over HTTP, but if it is known, it should be included nevertheless.
`url.full` MUST NOT contain credentials passed via URL in form of `https://username:password@www.example.com/`. In such case username and password should be redacted and attribute's value should be `https://REDACTED:REDACTED@www.example.com/`.
`url.full` SHOULD capture the absolute URL when it is available (or can be reconstructed) and SHOULD NOT be validated or modified except for sanitizing purposes.

**[2]:** When missing, the value is assumed to be `/`

**[3]:** Sensitive content provided in query string SHOULD be scrubbed when instrumentations can identify it.
<!-- endsemconv -->

## Sensitive information

Capturing URL and its components MAY impose security risk. User and password information, when they are provided in [User Information](https://datatracker.ietf.org/doc/html/rfc3986#section-3.2.1) subcomponent, MUST NOT be recorded.

Instrumentations that are aware of specific sensitive query string parameters MUST scrub their values before capturing `url.query` attribute. For example, native instrumentation of a client library that passes credentials or user location in URL, must scrub corresponding properties.

_Note: Applications and telemetry consumers should scrub sensitive information from URL attributes on collected telemetry. In systems unable to identify sensitive information, certain attribute values may be redacted entirely._
