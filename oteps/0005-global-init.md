# Global SDK initialization

*Status: proposed*

Specify the behavior of OpenTelemetry APIs and implementations at startup.

## Motivation

OpenTelemetry is designed with a separation between the API and the
SDK which implements it, allowing an application to configure and bind
any compatible SDK at runtime.  OpenTelemetry is designed to support
"zero touch" instrumentation for third party libraries through the use
of a global instance.

In many programming environments, it is possible for libraries of code
to auto-initialize, allowing them to begin operation concurrently with
the main program, e.g., while initializing static program state.  This
presents a set of opposing requirements: (1) the API supports a
configurable SDK; (2) third party libraries may use OpenTelemetry
without configuration.

## Explanation

There are several acceptable ways to address this situation.  The
feasibility of each approach varies by language.  The implementation
must select one of the following strategies:

### Service provider mechanism

Where the language provides a commonly accepted way to inject SDK
components, it should be preferred.  The Java SPI supports loading and
configuring the global SDK before it is first used, and because of
this property the service provider mechanism case leaves little else
to specify.

### Explicit initializer

When it is not possible to ensure the SDK is installed and configured
before the API is first used, loading the SDK is handed off to the
user "at the right time", as stated in [Ruby issue
19](https://github.com/open-telemetry/opentelemetry-ruby/issues/19).
In this case, a number of requirements must be specified, as discussed
next.

## Requirements: Explicit initializer

OpenTelemetry specifies that the default implementation is
non-operational (i.e., a "no-op"), requiring that API method calls
result in effectively zero instrumentation overhead.  We expect third
party libraries to use the global SDK before it is installed, which is
addressed in a requirement stated below.

The explicit initializer method should take independent `Tracer` and
`Meter` objects (e.g., `opentelemetry.Init(Tracer, Meter)`).  The SDK
may be installed no more than once.  After the first SDK installed,
subsequent calls to the explicit initializer shall log console
warnings.

In common language, uses of the global SDK instance (i.e., the Tracer
and Meter) must "begin working" once the SDK is installed, with the
following stipulations:

### Tracer

There may be loss of spans at startup.

Spans that are started before the SDK is installed are not recovered,
they continue as No-op spans.

### Meter

There may be loss of metrics at startup.

Metric SubMeasure objects (i.e., metrics w/ predefined labels)
initialized before the SDK is installed will redirect to the global
SDK after it is installed.

### Concrete types

Keys, tags, attributes, labels, resources, span context, and
distributed context are specified as pure API objects, therefore do
not depend on the SDK being installed.

## Trade-offs and mitigations

### Testing support

Testing should be performed without depending on the global SDK.

### Synchronization

Since the global Tracer and Meter objects are required to begin
working once the SDK is installed, there is some implied
synchronization overhead at startup, overhead we expect to fall after
the SDK is installed.  We recommend explicitly installing a No-op SDK
to fully disable instrumentation, as this approach will have a lower
overhead than leaving the OpenTelemetry library uninitialized.

## Prior art and alternatives

As an example that does not qualify as "commonly accepted", see [Go
issue 52](https://github.com/open-telemetry/opentelemetry-go/issues/52)
which demonstrates using the Go `plugin` package to load a
configurable SDK prior to first use.

## Open questions

What other options should be passed to the explicit global initializer?

Is there a public test for "is the SDK installed; is it a no-op"?
