# zPages

## Table of Contents

- [Overview](#overview)
  - [Types of zPages](#types-of-zpages)
    - [Tracez](#tracez)
    - [TraceConfigz](#traceconfigz)
    - [RPCz](#rpcz)
    - [Statsz](#statsz)
- [Design and Implementation](#design-and-implementation)
  - [Tracez](#tracez-details)
    - [TraceConfigz](#traceconfigz-details)
  - [RPCz](#rpcz-details)
  - [Statsz](#statsz-details)
  - [Shared zPages Components](#shared-zpages-components)
    - [Wrapper](#wrapper)
    - [HTTP Server](#http-server)
- [Future possibilities / Exploration](#future-possibilities)
  - [Shared Static Files](#shared-static-files)
  - [Out-process Implementation](#out-process)

## Overview

zPages are an in-process alternative to external exporters. When included, they collect and aggregate tracing and metrics information in the background; this data is served on web pages when requested.

The idea of "zPages" originates from one of OpenTelemetry's predecessors, [OpenCensus](https://opencensus.io/). You can read more about zPages from the OpenCensus docs [here](https://opencensus.io/zpages) or the OTEP [here](https://github.com/open-telemetry/oteps/blob/main/text/0110-z-pages.md). OpenCensus has different zPage implementations in [Java](https://opencensus.io/zpages/java/), [Go](https://opencensus.io/zpages/go/), and [Node](https://opencensus.io/zpages/node/) and there has been similar internal solutions developed at companies like Uber. Within OpenTelemetry, zPages are available in Go and Rust. The OTel Collector also has [an implementation](https://github.com/open-telemetry/opentelemetry-collector/tree/master/extension/zpagesextension) of zPages.

zPages are uniquely useful in a couple of different ways. One is that they're more lightweight and quicker compared to installing external tracing systems like Jaeger and Zipkin, yet they still share useful ways to debug and gain insight into instrumented applications; these uses depend on the type of zPage, which is detailed below. For high throughput applications, zPages can also analyze more telemetry with the limited set of supported scenarios than external exporters; this is because zPages are in-memory while external exporters are typically configured to send a subset of telemetry for reach analysis to save costs.

## Types of zPages

### Tracez

Tracez shows information on tracing, including aggregation counts for latency, running, and errors for spans grouped by name. Latency spans are spans that complete successfully without errors, and are bucketed according to their end time. Running spans are incomplete spans, which should become latency or error spans at some point. Error spans are ones that complete with an error, which is encoded with a [non-Ok status](../../specification/trace/api.md#set-status). In addition to these counts, Tracez also keeps a set number of samples for each of these error, running, and latency (including within each duration bucket) buckets within each span name to allow users to look closer at span fields. This is particularly useful compared to external exporters that would otherwise likely sample them out.

This zPage is also useful for debugging latency issues (slow parts of applications), deadlocks and instrumentation problems (running spans that don't end), and errors (where errors happen and what types). They're also good for spotting patterns by showing which latency speeds are typical for operations with a given span name.

### TraceConfigz

TraceConfigz allows the user to control how spans are sampled for both zPages and external backends.

For example, the sampling probability can be increased, decreased, or customized in other ways (i.e. depending on span parentage). Number of kept attributes, annotations, events, and links can also be adjusted. This would be useful for users that want to more accurately capture span insights or allow scaling better for exceptionally large and complex applications.

### RPCz

RPCz provides details on sent and received RPC messages, which is categorized  by RPC methods. This includes overall and error counts, average latency per call, RPCs sent per second, and input/output size per second.

### Statsz

Statsz is focused on metrics, as it displays metrics and measures for exported views. These views are grouped into directories using their namespaces

## Design and Implementation

### Tracez Details

For OpenTelemetry, a custom [span processor](../../specification/trace/sdk.md#span-processor) SHOULD be made to interface with the [Tracer API](../../specification/trace/api.md#tracer) to collect spans. This span processor collects references to running spans and exports completed spans to its own memory or to an aggregator that can aggregate information from multiple span processors.

There SHOULD be a `data aggregator` that tracks running, error, and latency buckets counts for spans grouped by their respective name. The aggregator MUST also hold some sampled spans to provide users with more information. To prevent memory overload, only some spans MUST be sampled for each bucket for each span name; for example, if that sampled span max number is set to 5, then only up to 55 pieces of span data can be kept for each span name in the aggregator (sampled_max \* number of buckets = 5 \* [running + error + 9 latency buckets] =  5 \* 11 = 55). Aggregation work is recommended to do periodically in batches.

When the user visits the Tracez endpoint, likely something similar to `host:port/tracez`, then the distribution of latencies for span names MUST be rendered. When clicking on buckets counts for a span name, additional details on individual sampled spans for that bucket MUST be shown. These details would include trace ID, parent ID, span ID, start time, attributes, and more depending on the type of bucket (running, error, or latency) and what's implemented/recorded in the other components. See [HTTP Server](#http-server) for more information on that and other implementation details.

For all of these, the thread safety of all of these components MUST be taken into account. With a span processor, data aggregator, and HTTP server configuration, there SHOULD be tests that ensure correct, deterministic, and safe behavior when the different components try to access the same data structures concurrently. Benchmarking is also recommended. The data aggregator and span processor SHOULD have tests at the very least. Additionally, the span data itself MUST to be thread-safe since those fields will be accessed or copied in the aggregator and server level.

### TraceConfigz Details

> TODO

### RPCz Details

> TODO

### Statsz Details

> TODO

## Shared zPages Components

### Wrapper

A zPages wrapper class acts as an API or injection point for zPages, instantiating and running all of the different zPages in the background without users needing knowledge of how they work under the hood.

An example of what happens when a user includes a wrapper: if OTel Python has Tracez and RPCz implemented and added to that wrapper, that wrapper will create instances of all the needed components (processors, aggregators, etc) for both zPages when zPages is initialized. If or when other zPages are added to OTel Python, developers adding them would only need to add the corresponding initialization code for those components in the wrapper.

Each zPages implementation MUST create a wrapper class for zPages, since they allow users to add all zPages with minimal effort. These wrappers should be as simple as adding 2 lines of code to include zPages (zPages import + initialization line).

### HTTP Server

All zPages MUST have a HTTP Server to render information on a webpage when a host:port and endpoint is accessed. All zPages MUST be accessed from the same host:port; For example, host1 should equal host2 and port1 should equal port2 for `host1:post1/tracez` and `host2:port2/rpcz`. There SHOULD be handlers to group logic by type of zPage, and there SHOULD be a landing page. This landing page would be at the root `host:port/`, displaying links to currently implemented zPages for that repository. Similar behavior MAY be implemented for any invalid endpoints as well.

Traditionally, zPages have approached this by rendering web pages purely on the server-side. This means the server would only serve static resources (HTML, CSS and possibly Javascript) when the user accesses a given endpoint. Based on the type of zPage and the server language used, a pure server-side approach would generate HTML pages using hardcoded strings from scratch or using a template; this would tightly couple the data and UI layer.

The following endpoints SHOULD be used for serving files (which are ideally standardized, per the [Shared Static Files](#shared-static-files) sections under future possibilities), for any HTTP server approach for any zPage:

- `host:port/{zpage}` display the main page and aggregations
- `host:port/{zpage}/style.css` SHOULD contain the styling logic. This MAY also be embedded in the HTML, but SHOULD be separated and linked in the page head using `<link rel="stylesheet" href="/{zpage}/style.css">`
- If server-side only:
  - `host:port/{zpage}/{...}`, and other variants SHOULD display detailed information on the data described by the {...}
    - an example of this: If a user accesses `host:port/tracez?type=error&name=span1`, that Tracez page should display all currently sampled error spans with the name `span1`
- If adding client-side:
  - `host:port/{zpage}/script.js` SHOULD return the frontend Javascript code if these zPages uses client-side interaction. This MAY also be embedded in the HTML, but SHOULD be separated and linked in the page head using `<script src="/{zpage}/script.js">`

All zPages need some server-side rendering, but the data and UI layer MAY be separated by adding client-side functionality. This separation has benefits including 1.) allowing users to consume zPages data without a browser, styling, or Javascript, such as when using wget on the endpoints serving JSON data and 2.) adding extensibility to zPages (e.g. the frontend can be centralized and used in multiple  OTel language repositories). This approach is detailed below.

Instead of directly translating native data structures to HTML strings based on the stored information, the data layer MUST do 2 things depending on the webpage endpoint accessed: 1. Serve the static HTML, JS, and CSS files, which are not not data dependent and 2. Act like a web REST API by translating stored data to JSON. Whether the data layer does one or the other depends on which URL endpoint is accessed; the former is intended for the initial zPages load, and latter for user interactions. If the client requests the data via a request parameter or "Accept" HTTP header, that data should be available as a JSON-encoded response.

If using the server/client approach for the HTTP server, the following endpoints and data formatting (using proto3 definitions) SHOULD be used for serving JSON:

- Tracez
  - `host:post/tracez/api/aggregations` SHOULD return `repeated TracezCounts`, which describes of error, running, and latency counts for all span name groupings. The latency array size MUST equal exactly the number of latency buckets used.

    ```proto3
    message TracezCounts {
          string spanname = 1;
          repeated uint32 latency = 2; // [A]
          uint32 running = 3;
          uint32 error = 4;
        }
    ```

  - `host:post/tracez/api/latency/{bucket_index}/{span_name}` SHOULD return `repeated LatencyData`, which describes latency sampled spans with the name {span_name} at latency band index {bucket_index}. Latency bands are determined by the developer, but they MUST be increasing in duration and map to what is determined within Tracez [A]. An example of latency buckets could be, as used in OTel C++ Tracez: [>0s, >10µs, >100µs, >1ms, >10ms, >100ms, >1s, >10s, >100s]. The array MUST be size sampled_max or less.

    ```proto3
    message LatencyData {
          bytes traceid = 1;
          bytes spanid = 2;
          bytes parentid = 3;
          fixed64 starttime = 4;
          fixed64 endtime = 5;
          repeated opentelemetry.proto.common.v1.KeyValue attributes = 6; // [1]
          repeated Event events = 7; // [2]
          repeated Link links = 8; // [3]
    }
    ```

  - `host:post/tracez/api/running/{span_name}` SHOULD return `repeated RunningData`, which describes running sampled spans with the name {span_name}. The array MUST be size sampled_max or less.

    ```proto3
    message RunningData {
          bytes traceid = 1;
          bytes spanid = 2;
          bytes parentid = 3;
          fixed64 starttime = 4;
          repeated opentelemetry.proto.common.v1.KeyValue attributes = 5; // [1]
          repeated Event events = 6; // [2]
          repeated Link links = 7; // [3]
    }
    ```

  - `host:post/tracez/api/error/{span_name}` SHOULD return `repeated ErrorData`, which describes error sampled spans with the name {span_name}. The array MUST be size sampled_max or less.

    ```proto3
    message ErrorData {
          bytes traceid = 1;
          bytes spanid = 2;
          bytes parentid = 3;
          fixed64 starttime = 4;
          repeated opentelemetry.proto.common.v1.KeyValue attributes = 5; // [1]
          repeated Event events = 6; // [2]
          repeated Link links = 7; // [3]
          Status status = 8; // [4]
    }
    ```

    Key: [[1]](https://github.com/open-telemetry/opentelemetry-proto/blob/ca6dcbbf390d8b3ce419a931eb351d189a3eb4fa/opentelemetry/proto/trace/v1/trace.proto#L152) attribute, [[2]](https://github.com/open-telemetry/opentelemetry-proto/blob/ca6dcbbf390d8b3ce419a931eb351d189a3eb4fa/opentelemetry/proto/trace/v1/trace.proto#L169) event, [[3]](https://github.com/open-telemetry/opentelemetry-proto/blob/ca6dcbbf390d8b3ce419a931eb351d189a3eb4fa/opentelemetry/proto/trace/v1/trace.proto#L196) link, [[4]](https://github.com/open-telemetry/opentelemetry-proto/blob/ca6dcbbf390d8b3ce419a931eb351d189a3eb4fa/opentelemetry/proto/trace/v1/trace.proto#L231) status

> TODO: add more zPage endpoint specs (i.e. URL and data formatting, required/optional parameters) and additional review of fields desired as we likely want many/all of the OTLP fields (e.g. SpanKind)

The UI/frontend/rendering layer is the HTML, CSS, and Javascript itself, in contrast to the logic to serve those files. This frontend uses the data layer's API on the client-side within the browser with Javascript by accessing certain endpoints depending on the user's actions. The data returned interacts with the Javascript, which determines and executes the logic necessary to render updates to the HTML DOM. Modifying the HTML DOM means there are no unnecessary requesting and re-rendering static files, and only parts of the webpage are changed. This makes subsequent data queries quicker and requires no knowledge of client-side rendering for the zPages developer.

In either case, a benefit of reasoning about the zPages HTTP server as a separate component means that zPages can be mounted in an existing server. For example, this can be done in Java by calling zPages logic from a servlet. It's also worth noting that having zPages in an embedded HTTP server increases the vulnerability of application and security risks by increasing its attack surface area. A malicious actor could potentially read sensitive data in telemetry, perform DOS attacks on the HTTP server, or initiate a telemetry storm by reconfiguring how telemetry is collected (i.e. through TraceConfigz); zPages should be reserved for protected dev environments for most cases because of this.

-------------

## Future Possibilities

### Shared Static Files

All HTML, CSS, and Javascript files would be used across different OTel language repositories for their in-process zPages

- Pros
  - When client-side features are rolled out (including filtering/sorting data, interval refreshing, unit toggles), changes are all centralized
  - Rendering logic and responsibility is focused and can be more effective, zPages developers can focus on other priorities
  - Less difficult to share frontend information post-setup, follows OpenTelemetry's philosophy of being standardized
- Cons
  - Adds computation of converting native data structures into JSON strings and serving these static files. May need extra libraries
  - Some process has to be created to update the static files in a repository and serving them at the correct endpoints
  - Initial setup may be difficult (one way this can be achieved is with Github modules)

### Out-process

Out-process zPages are ones that are compatible across different languages, which executes the processing of tracing and metrics information outside of applications (as opposed to in-process zPages).

- Pros
  - zPages can be added to any OpenTelemetry repository, and future development can be completely focused there
- Cons
  - More complicated than using local methods since it require setup (i.e. RPC or exporters) to allow zPages and applications to communicate. This would make it similar to other tracing systems.

> GENERAL TODO: Add pictures/figures/videos, proxy/shim layer, and design docs links
