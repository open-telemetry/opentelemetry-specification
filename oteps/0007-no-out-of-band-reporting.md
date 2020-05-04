# Remove support to report out-of-band telemetry from the API

## TL;DR

This section tries to summarize all the changes proposed in this RFC:

1. Remove API requirement to support reporting out-of-band telemetry.
2. Move Resource to SDK, API will always report telemetry for the current application so no need to
allow configuring the Resource in any instrumentation.
3. New APIs should be designed without this requirement.

## Motivation

Currently the API package is designed with a goal to support reporting out-of-band telemetry, but
this requirements forces a lot of trade-offs and unnecessary complicated APIs (e.g. `Resource` must
be exposed in the API package to allow telemetry to be associated with the source of the telemetry).

Reporting out-of-band telemetry is a required for the OpenTelemetry ecosystem, but this can be done
via a few different other options that does not require to use the API package:

* The OpenTelemetry Service, users can write a simple [receiver][otelsvc-receiver] that parses and
produces the OpenTelemetry data.
* Using the SDK's exporter framework, users can write directly OpenTelemetry data.

## Internal details

Here is a list of decisions and trade-offs related to supporting out-of-band reporting:

1. Add `Resource` concept into the API.
   * Example in the create metric we need to allow users to specify the resource, see
   [here][create-metric]. The developer that writes the instrumentation has no knowledge about where
   the monitored resource is deployed so there is no way to configure the right resource.
2. [RFC](./0002-remove-spandata.md) removes support to report SpanData.
   * This will require that the trace API has to support all the possible fields to be configured
   via the API, for example need to allow users to set a pre-generated `SpanId` that can be avoided
   if we do not support out-of-band reporting.
3. Sampling logic for out-of-band spans will get very complicated because it will be incorrect to
sample these data.
4. Associating the source of the telemetry with the telemetry data gets very simple. All data
produced by one instance of the API implementation belongs to only one Application.

This can be rephrased as "one API implementation instance" can report telemetry about only the
current Application.

### Resource changes

This RFC does not suggest to remove the `Resource` concept or to modify any API in this interface,
it only suggests to move this concept to the SDK level.

Every implementation of the API (SDK in OpenTelemetry case) instance will have one `Resource` that
describes the running Application. There may be cases where in the same binary there are multiple
Application running (e.g. Java application server), every application will have it's own SDK
instance configured with it's own `Resource`.

## Related Issues

* [opentelemetry-specification/62](https://github.com/open-telemetry/opentelemetry-specification/issues/62)
* [opentelemetry-specification/61](https://github.com/open-telemetry/opentelemetry-specification/issues/61)

[otelsvc-receiver]: https://github.com/open-telemetry/opentelemetry-service#config-receivers
[create-metric]: https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/metrics/api.md#create-metric
