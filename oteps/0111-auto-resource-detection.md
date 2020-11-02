# Automatic Resource Detection

Introduce a mechanism to support auto-detection of resources.

## Motivation

Resource information, i.e. attributes associated with the entity producing
telemetry, can currently be supplied to tracer and meter providers or appended
in custom exporters. In addition to this, it would be useful to have a mechanism
to automatically detect resource information from the host (e.g. from an
environment variable or from aws, gcp, etc metadata) and apply this to all kinds
of telemetry. This will in many cases prevent users from having to manually
configure resource information.

Note there are some existing implementations of this already in the SDKs (see
[below](#prior-art-and-alternatives)), but nothing currently in the
specification.

## Explanation

In order to apply auto-detected resource information to all kinds of telemetry,
a user will need to configure which resource detector(s) they would like to run
(e.g. AWS EC2 detector).

If multiple detectors are configured, and more than one of these successfully
detects a resource, the resources will be merged according to the Merge
interface already defined in the specification, i.e. the earliest matched
resource's attributes will take precedence. Each detector may be run in
parallel, but to ensure deterministic results, the resources must be merged in
the order the detectors were added.

A default implementation of a detector that reads resource data from the
`OTEL_RESOURCE` environment variable will be included in the SDK. The
environment variable will contain of a list of key value pairs, and these are
expected to be represented in a format similar to the [W3C
Baggage](https://github.com/w3c/baggage/blob/master/baggage/HTTP_HEADER_FORMAT.md#header-content),
except that additional semi-colon delimited metadata is not supported, i.e.:
`key1=value1,key2=value2`. If the user does not specify any resource, this
detector will be run by default.

Custom resource detectors related to specific environments (e.g. specific cloud
vendors) must be implemented as packages separate to the core SDK, and users
will need to import these separately.

## Internal details

As described above, the following will be added to the Resource SDK
specification:

- An interface for "detectors", to retrieve resource information
- Specification for a global function to merge resources returned by a set of
  detectors
- Details of the "from environment variable" detector implementation as
  described above
- Specification that default detection (from environment variable) runs once on
  startup, and is used by all tracer & meter providers by default if no custom
  resource is supplied

### Usage

The following example in Go creates a tracer and meter provider that uses
resource information automatically detected from AWS or GCP:

Assumes a dependency has been added on the `otel/api`, `otel/sdk`,
`otel/awsdetector`, and `otel/gcpdetector` packages.

```go
resource, _ := sdkresource.Detect(ctx, 5 * time.Second, awsdetector.ec2, gcpdetector.gce)
tp := sdktrace.NewProvider(sdktrace.WithResource(resource))
mp := push.New(..., push.WithResource(resource))
```

### Components

#### Detector

The `Detector` interface will simply contain a `Detect` function that returns a
Resource.

The `Detect` function should contain a mechanism to timeout and cancel the
operation. If a detector is not able to detect a resource, it must return an
uninitialized resource such that the result of each call to `Detect` can be
merged.

#### Global Function

The SDK will also provide a global `Detect` function. This will take a timeout
duration and a set of detectors that should be run and merged in order as
described in the intro, and return a resource.

### Error Handling

In the case of one or more detectors raising an error, there are two reasonable
options:

1. Ignore that detector, and continue with a warning (likely meaning we will
   continue without expected resource information)
2. Crash the application (raise a panic)

The user can decide how to recover from failure.

## Trade-offs and mitigations

- This OTEP proposes storing Vendor resource detection packages outside of the
  SDK. This ensures the SDK is free of vendor specific code. Given the
  relatively straightforward & minimal amount of code generally needed to
  perform resource detection, and the relatively small number of cloud
  providers, we may instead decide its okay for all the resource detection code
  to live in the SDK directly.
  - If we do allow Vendor resource detection packages in the SDK, we presumably
    need to restrict these to not being able to use non-trivial libraries
- This OTEP proposes only performing environment variable resource detection by
  default. Given the relatively small number of cloud providers, we may instead
  decide its okay to run all detectors by default. This raises the question of
  if any restrictions would need to be put on this, and how we would handle this
  in the future if the number of Cloud Providers rises. It would be difficult to
  back out of running these by default as that would lead to a breaking change.
- This OTEP proposes a global function the user calls with the detectors they
  want to run, and then expects the user to pass these into the providers. An
  alternative option (that was previously proposed in this OTEP) would be to
  supply a set of detectors directly to the metric or trace provider instead of,
  or as an additional option to, a static resource. That would result in
  marginally simpler setup code where the user doesn't need to call `AutoDetect`
  themselves. Another advantage of this approach is that its easier to specify
  default detectors and override these separately to any static resource the
  user may want to provide. On the downside, this approach adds the complexity
  of having to deal with the merging the detected resource with a static
  resource if provided. It also potentially adds a lot of complexity around how
  to avoid having detectors run multiple times since they will be configured for
  each provider. Avoiding having to specify detectors for tracer & meter
  providers is the primary reason for not going with that option in the end.
- The attribute proto now supports arrays & maps. We could support parsing this
  out of the `OTEL_RESOURCE` environment variable similar to how Correlation
  Context supports semi colon lists of keys & key-value pairs, but the added
  complexity is probably not worthwhile implementing unless someone has a good
  use case for this.
- In the case of an error at resource detection time, another alternative would
  be to start a background thread to retry following some strategy, but it's not
  clear that there would be much value in doing this, and it would add
  considerable unnecessary complexity.

## Prior art and alternatives

This proposal is largely inspired by the existing OpenCensus specification, the
OpenCensus Go implementation, and the OpenTelemetry JS implementation. For
reference, see the relevant section of the [OpenCensus
specification](https://github.com/census-instrumentation/opencensus-specs/blob/master/resource/Resource.md#populating-resources)

### Existing OpenTelemetry implementations

- Resource detection implementation in JS SDK
  [here](https://github.com/open-telemetry/opentelemetry-js/tree/master/packages/opentelemetry-resources):
  The JS implementation is very similar to this proposal. This proposal states
  that the SDK will allow detectors to be passed into telemetry providers
  directly instead of just having a global `DetectResources` function which the
  user will need to call and pass in explicitly. In addition, vendor specific
  resource detection code is currently in the JS resource package, so this would
  need to be separated.
- Environment variable resource detection in Java SDK
  [here](https://github.com/open-telemetry/opentelemetry-java/blob/master/sdk/src/main/java/io/opentelemetry/sdk/resources/EnvVarResource.java):
  This implementation does not currently include a detector interface, but is
  used by default for tracer and meter providers

## Open questions

- Does this interfere with any other upcoming specification changes related to
  resources?
- If custom detectors need to live outside the core repo, what is the
  expectation regarding where they should be hosted?
- Also see the [Trade-offs and mitigations](#trade-offs-and-mitigations) section

## Future possibilities

When the Collector is run as an agent, the same interface, shared with the Go
SDK, could be used to append resource information detected from the host to all
kinds of telemetry in a Processor (probably as an extension to the existing
Resource Processor). This would require a translation from the SDK resource to
the collector's internal representation of a resource.
