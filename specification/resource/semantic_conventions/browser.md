# Browser

**Status**: [Experimental](../../document-status.md)

**type:** `browser`

**Description**: The web browser in which the application represented by the resource is running. The `browser.*` attributes MUST be used only for resources that represent applications running in a web browser (regardless of whether running on a mobile or desktop device).

All of these attributes can be provided by the user agent itself in the form of an HTTP header (e.g. Sec-CH-UA, Sec-CH-Platform, User-Agent). However, the headers could be removed by proxy servers, and are tied to calls from individual clients. In order to support batching through services like the Collector and to prevent loss of data (e.g. due to proxy servers removing headers), these attributes should be used when possible.

<!-- semconv browser -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `browser.brands` | string[] | Array of brand name and version separated by a space [1] | `[ Not A;Brand 99, Chromium 99, Chrome 99]` | Recommended |
| `browser.platform` | string | The platform on which the browser is running [2] | `Windows`; `macOS`; `Android` | Recommended |
| `browser.mobile` | boolean | A boolean that is true if the browser is running on a mobile device [3] |  | Recommended |
| `browser.language` | string | Preferred language of the user using the browser [4] | `en`; `en-US`; `fr`; `fr-FR` | Recommended |
| `browser.visitor_id` | string | An anonymous id for the visiting user. [5] | `123` | Recommended |
| `browser.session_id` | string | Identifier for the current browser session | `123` | Recommended |
| `browser.page_impression_id` | string | Unique id for the page impression, represented by a GUID [6] | `12627cc493-f310-47de-96bd-71410b7dec043` | Recommended |
| `browser.screen_width` | int | Screen width of the device/browser view port | `600` | Recommended |
| `browser.screen_height` | int | Screen height of the device/browser view port | `400` | Recommended |
| `browser.url` | string | Complete URL of the current active page including the URL fragment | `https://en.wikipedia.org/wiki/Main_Page#foo` | Recommended |
| `user_agent.original` | string | Full user-agent string provided by the browser [7] | `Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36` | Recommended |

**[1]:** This value is intended to be taken from the [UA client hints API](https://wicg.github.io/ua-client-hints/#interface) (`navigator.userAgentData.brands`).

**[2]:** This value is intended to be taken from the [UA client hints API](https://wicg.github.io/ua-client-hints/#interface) (`navigator.userAgentData.platform`). If unavailable, the legacy `navigator.platform` API SHOULD NOT be used instead and this attribute SHOULD be left unset in order for the values to be consistent.
The list of possible values is defined in the [W3C User-Agent Client Hints specification](https://wicg.github.io/ua-client-hints/#sec-ch-ua-platform). Note that some (but not all) of these values can overlap with values in the [`os.type` and `os.name` attributes](./os.md). However, for consistency, the values in the `browser.platform` attribute should capture the exact value that the user agent provides.

**[3]:** This value is intended to be taken from the [UA client hints API](https://wicg.github.io/ua-client-hints/#interface) (`navigator.userAgentData.mobile`). If unavailable, this attribute SHOULD be left unset.

**[4]:** This value is intended to be taken from the Navigator API `navigator.language`.

**[5]:** This will remain same in a given browser session, and will persist across page navigations in the same browser session.

**[6]:** As an example, Page.html will yield 4 impression ids if the page is refreshed 4 times in the same browser instance. For SPA apps, every URL change results in a new impression.

**[7]:** The user-agent value SHOULD be provided only from browsers that do not have a mechanism to retrieve brands and platform individually from the User-Agent Client Hints API. To retrieve the value, the legacy `navigator.userAgent` API can be used.
<!-- endsemconv -->
