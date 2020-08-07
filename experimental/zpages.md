# zPages
## Table of Contents
- [Overview](#overview)
  - [Types of zPages](#types-of-zpages)
    - [TraceZ](#tracez)
      - [TraceConfigz](#traceconfigz) 
    - [RPCz](#rpcz)
    - [StatsZ](#statsz)
- [Design and Implementation](#design-and-implementation)
  - [TraceZ](#tracez-details)
    - [TraceConfigZ](#traceconfigz-details)
  - [RPCz](#rpcz-details)
  - [StatsZ](#statsz-details)
  - [Shared zPages Components](#shared-zpages-components)
    - [Wrapper](#wrapper)
    - [HTTP Server](#http-server)
- [Future possibilities / Exploration](#future-possibilities)
  - [Out-process Implementation](#out-process)
  - [Shared Static Files](#shared-static-files)

## Overview
zPages are webpages that allow easy viewing of tracing/metrics information. When included for a process, zPages will display basic information about that process on a webpage.

The idea of "zPages" originates from one of OpenTelemetry's predecessors, [OpenCensus](https://opencensus.io/). You can read more about it [here](https://opencensus.io/zpages). OpenCensus has different zPage implementations in [Java](https://opencensus.io/zpages/java/), [Go](https://opencensus.io/zpages/go/), and [Node](https://opencensus.io/zpages/node/) and there has been similar internal solutions developed at companies like Uber. Within OpenTelemetry, zPages are also either developed or being developed in [C#](https://github.com/open-telemetry/opentelemetry-dotnet/tree/master/src/OpenTelemetry.Exporter.ZPages), Java, and C++.

While zPages are uniquely useful in being more lightweight and quicker compared to installing external exporters like Jaeger and Zipkin, they still offer many useful ways to debug and gain insight into applications. The uses depend on the type of zPage, which is detailed below

## Types of zPages
### TraceZ
TraceZ shows information on tracing, including aggregation counts for latency, running, and errors for spans grouped by name. It also allows users to look closer at details for spans that are sampled.

This type of zPage is useful particularly for debugging latency issues (slow parts of applications), deadlocks (running spans that don't end), and errors (where error happen and what types). They're also good for spotting patterns, like seeing what speeds are typical for operations with a given span name.

You can read about TraceZ more [here](https://opencensus.io/zpages/java/#tracez).

### TraceConfigZ

TraceConfigZ is closely related to TraceZ, allowing the user to modify how spans are sampled or how much data to keep in TraceZ by updating the TraceZ components accordingly.

For example, the sampling probability can be increased, decreased, or customized in other ways (i.e. depending on span parentage). Number of kept attritubtes, annotations, events, and links can also be adjusted.

You can read about TraceConfigZ more [here](https://opencensus.io/zpages/java/#traceconfigz).

### RPCz
RPCz provides details on sent and received RPC messages, which is categorized  by RPC methods. This includes overall and error counts, average latency per call, RPCs sent per second, and input/output size per second.

You can read about RPCz more [here](https://docs.google.com/document/d/1RWNyUIaKTYK12tck_rQjki4jTyHFfkD8sk54mjwRwso/edit#) and [here](https://opencensus.io/zpages/java/#rpcz).

### StatsZ
StatsZ is focused more on metrics, displays stats and measues for any exported views. These views are grouped into directories using their namespaces

You can read more about StatZ [here](https://opencensus.io/zpages/java/#statsz)

## Design and Implementation
### TraceZ Details
To implement TraceZ, spans need to be collected, aggregated, and rendered on a webpage.

For OpenTelemetry, a custom `span processor` can be made to interface with the `Tracer` API to collect spans. This span processor collects references to running spans and exports completed spans to its own memory or directly to an aggregator. An alternative to a span processor is using some sort of profiler.

A `data aggregator` keeps a track of counts for running, error, and latency buckets for spans grouped by their name. It also samples some spans to provide users with more information. To prevent memory overload, only some spans are sampled for each bucket for each span name; for example, if that sampled span max number is set to 5, then only up to 55 pieces of span data can be kept for each span name in the aggregator (sampled_max * number of buckets = 5 * [running + error + 9 latency buckets] =  5 * 11 = 55).

When the user visits the TraceZ endpoint, likely something similar to host:port/tracez, then the distribution of latencies for span names will be rendered. When clicking on buckets counts for a span name, additional details on individual sampled spans for that bucket would be shown. These details would include trace ID, parent ID, span ID, start time, attributes, and more depending on the type of bucket (running, error, or latency) and what's implemented/recorded in the other components. See [HTTP Server](#http-server) for more information on implementation.

For all of these, the thread safety of all of these components needs to be taken into account. With a span processor, data aggregator, and HTTP server configuration, there needs to be tests that ensure correct, deterministic, and safe behavior when the different components try to access the same data structures concurrently. Additionally, the span data itself needs to be thread-safe since those fields will be accessed or copied in the aggregator and server level.

### TraceConfigz Details
> TODO

### RPCz Details
> TODO

### StatsZ Details
> TODO

## Shared zPages Components
### Wrapper
Each implementation ideally creates a wrapper class for zPages that allows users to add them all with minimal effort like an API, which could be as simple as adding 2 lines of code to include zPages. (importing zPages and initializing it).

This wrapper class acts as an injection point, running all of the different zPages in a background thread without users needing knowledge of how they work under the hood. An example: if a language has TraceZ and RPCz implemented, then the wrapper will spin up servers for both when a user constructs a zPages class instance. Adding StatsZ would mean those developers would only add additional code to extract the needed information and display them on a page. 

### HTTP Server
All zPages have some sort of HTTP Server component to render their information on a webpage when a host:port and endpoint is accessed.

Traditionally, zPages have approached this by rendering webpages purely on the server-side. This means it would simply resources (HTML, CSS and possibly Javascript) when the user accesses a given endpoint. Depending on the type of zPages, a pure server-side approach uses data to generate HTML pages using hardcoded strings from scratch or using a template. All zPages need some server-side rendering.

Optionally, there could also be an API layer that translates native data structures to JSON strings for a frontend to use when designated endpoints are accessed. This API layer would be paired with a frontend that provides client-side functionality, which would need Javascript. The frontend Javascript would use the API by requesting information at endpoints to add updates to the HTML DOM without unnecessarily requesting and re-rendering static resources. This makes initial page loads quicker and requires no knowledge of client-side rendering.

-------------
## Future Possibilities
### Out-process
zPages that compatible across different languages, with processing of information happening outside of applications
- Pros
  - zPages can be added to any OpenTelemetry repository, and future development can be completely focused here instead
- Cons
  - More complicated than using local methods, and requires extra setup (i.e. RPC communication setup) in applications to somehow send information to zPages to work

### Shared Static Files
All HTML, CSS, and Javascript files would be used across different OT language repositories for their in-process zPages
- Pros
  - When client-side features are rolled out (including filtering/sorting data, interval refreshing, unit toggles), changes are all centralized
  - Rendering logic and responsibility is focused and can be more effective, zPages developers can focus on other priorities
  - Less difficult to share frontend information post-setup, follows OpenTelemetry's philosophy of being standardized
- Cons
  - Adds computation of converting native data structures into JSON strings and serving these static files. May need extra libraries
  - Some process has to be created to update the static files in a repository and serving them at the correct endpoints
  - Initial setup may be difficult (one way this can be achieved is with Github modules)

### Proxy/Shim layer
> TODO

> GENERAL TODO: Link spec where possible, add pictures/figures and design docs links

