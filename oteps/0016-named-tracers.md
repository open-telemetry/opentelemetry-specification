# Named Tracers and Meters

**Status:** `approved`

_Creating Tracers and Meters using a factory mechanism and naming those Tracers / Meters in accordance with the library that provides the instrumentation for those components._

## Suggested reading

* [Proposal: Tracer Components](https://github.com/open-telemetry/opentelemetry-specification/issues/10)
* [Global Instance discussions](https://github.com/open-telemetry/opentelemetry-specification/labels/global%20instance)
* [Proposal: Add a version resource](https://github.com/open-telemetry/oteps/pull/38)

## Motivation

The mechanism of "Named Tracers and Meters" proposed here is motivated by following scenarios:

* For a consumer of OpenTelemetry instrumentation libraries, there is currently no possibility of influencing the amount of the data produced by such libraries. Instrumentation libraries can easily "spam" backend systems, deliver bogus data or - in the worst case - crash or slow down applications. These problems might even occur suddenly in production environments caused by external factors such as increasing load or unexpected input data.

* If a library hasn't implemented [semantic conventions](https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/data-semantic-conventions.md) correctly or those conventions change over time, it's currently hard to interpret and sanitize these data selectively. The produced Spans or Metrics cannot be associated with those instrumentation libraries later.

This proposal attempts to solve the stated problems by introducing the concept of:
 * _Named Tracers and Meters_ identified via a **name** (e.g. _"io.opentelemetry.contrib.mongodb"_) and a **version** (e.g._"semver:1.0.0"_) which is associated with the Tracer / Meter and the Spans / Metrics it produces.
 * A `TracerFactory` / `MeterFactory` as the only means of creating a Tracer or Meter.

Based on such an identifier, a Sampler could be implemented that discards Spans or Metrics from certain libraries. Also, by providing custom Exporters, Span or Metric data could be sanitized before it gets processed in a back-end system. However, this is beyond the scope of this proposal, which only provides the fundamental mechanisms.

## Explanation

From a user perspective, working with *Named Tracers / Meters* and `TracerFactory` / `MeterFactory` is conceptually similar to how e.g. the [Java logging API](https://docs.oracle.com/javase/7/docs/api/java/util/logging/Logger.html#getLogger(java.lang.String)) and logging frameworks like [log4j](https://www.slf4j.org/apidocs/org/slf4j/LoggerFactory.html) work. In analogy to requesting Logger objects through LoggerFactories, a tracing library would create specific Tracer / Meter objects through a TracerFactory / MeterFactory.

New Tracers or Meters can be created by providing the name and version of an instrumentation library. The version (following the convention proposed in https://github.com/open-telemetry/oteps/pull/38) is basically optional but *should* be supplied since only this information enables following scenarios:
* Only a specific range of versions of a given instrumentation library need to be suppressed, while other versions are allowed (e.g. due to a bug in those specific versions).
* Go modules allow multiple versions of the same middleware in a single build so those need to be determined at runtime.

```java
// Create a tracer/meter for a given instrumentation library in a specific version.
Tracer tracer = OpenTelemetry.getTracerFactory().getTracer("io.opentelemetry.contrib.mongodb", "semver:1.0.0");
Meter meter = OpenTelemetry.getMeterFactory().getMeter("io.opentelemetry.contrib.mongodb", "semver:1.0.0");
```

These factories (`TracerFactory` and `MeterFactory`) replace the global `Tracer` / `Meter` singleton objects as ubiquitous points to request Tracer and Meter instances.

 The *name* used to create a Tracer or Meter must identify the *instrumentation* libraries (also referred to as *integrations*) and not the instrumented libraries. These instrumentation libraries could be libraries developed in an OpenTelemetry repository, a 3rd party implementation or even auto-injected code (see [Open Telemetry Without Manual Instrumentation OTEP](https://github.com/open-telemetry/oteps/blob/master/text/0001-telemetry-without-manual-instrumentation.md)). See also the examples for identifiers at the end.
If a library (or application) has instrumentation built-in, it is both the instrumenting and instrumented library and should pass its own name here. In all other cases (and to distinguish them from that case), the distinction between instrumenting and instrumented library is very important. For example, if an HTTP library `com.example.http` is instrumented by either `io.opentelemetry.contrib.examplehttp` or `com.example.company.examplehttpintegration`, then it is important that the Tracer is not named `com.example.http` but after the actual instrumentation library.

If no name (null or empty string) is specified, following the suggestions in ["error handling proposal"](https://github.com/open-telemetry/opentelemetry-specification/pull/153), a "smart default" will be applied and a default Tracer / Meter implementation is returned.

### Examples (of Tracer and Meter names)

Since Tracer and Meter names describe the libraries which use those Tracers and Meters, their names should be defined in a way that makes them as unique as possible.
The name of the Tracer / Meter should represent the identity of the library, class or package that provides the instrumentation. 

Examples (based on existing contribution libraries from OpenTracing and OpenCensus):

* `io.opentracing.contrib.spring.rabbitmq`
* `io.opentracing.contrib.jdbc`
* `io.opentracing.thrift`
* `io.opentracing.contrib.asynchttpclient`
* `io.opencensus.contrib.http.servlet`
* `io.opencensus.contrib.spring.sleuth.v1x`
* `io.opencesus.contrib.http.jaxrs`
* `github.com/opentracing-contrib/go-amqp` (Go)
* `github.com/opentracing-contrib/go-grpc` (Go)
* `OpenTracing.Contrib.NetCore.AspNetCore` (.NET)
* `OpenTracing.Contrib.NetCore.EntityFrameworkCore` (.NET)

## Internal details

By providing a `TracerFactory` / `MeterFactory` and *Named Tracers / Meters*, a vendor or OpenTelemetry implementation gains more flexibility in providing Tracers and Meters and which attributes they set in the resulting Spans and Metrics that are produced.

On an SDK level, the SpanData class and its Metrics counterpart are extended with a `getLibraryResource` function that returns the resource associated with the Tracer / Meter that created it.

## Prior art and alternatives

This proposal originates from an `opentelemetry-specification` proposal on [components](https://github.com/open-telemetry/opentelemetry-specification/issues/10) since having a concept of named Tracers would automatically enable determining this semantic `component` property.

Alternatively, instead of having a `TracerFactory`, existing (global) Tracers could return additional indirection objects (called e.g. `TraceComponent`), which would be able to produce spans for specifically named traced components.

```java
TraceComponent traceComponent = OpenTelemetry.Tracing.getTracer().componentBuilder("io.opentelemetry.contrib.mongodb", "semver:1.0.0");
Span span = traceComponent.spanBuilder("someMethod").startSpan();
```

Overall, this would not change a lot compared to the `TracerFactory` since the levels of indirection until producing an actual span are the same.

Instead of setting the `component` property based on the given Tracer names, those names could also be used as *prefixes* for produced span names (e.g. `<TracerName-SpanName>`). However, with regard to data quality and semantic conventions, a dedicated `component` set on spans is probably preferred.

Instead of using plain strings as an argument for creating new Tracers, a `Resource` identifying an instrumentation library could be used. Such resources must have a _version_ and a _name_ label (there could be semantic convention definitions for those labels). This implementation alternative mainly depends on the availability of the `Resource` data type on an API level (see https://github.com/open-telemetry/opentelemetry-specification/pull/254).

```java
// Create resource for given instrumentation library information (name + version)
Map<String, String> libraryLabels = new HashMap<>();
libraryLabels.put("name", "io.opentelemetry.contrib.mongodb");
libraryLabels.put("version", "1.0.0");
Resource libraryResource = Resource.create(libraryLabels);
// Create tracer for given instrumentation library.
Tracer tracer = OpenTelemetry.getTracerFactory().getTracer(libraryResource);
```

Those given alternatives could be applied to Meters and Metrics in the same way.

## Future possibilities

Based on the Resource information identifying a Tracer or Meter these could be configured (enabled / disabled) programmatically or via external configuration sources (e.g. environment).

Based on this proposal, future "signal producers" (i.e. logs) can use the same or a similar creation approach.

