# OpenTelemetry Language Library Design Principles

This document defines common principles that will help designers create language libraries that are easy to use, are uniform across all supported languages, yet allow enough flexibility for language-specific expressiveness. 

The language libraries are expected to provide full features out of the box and allow for innovation and experimentation through extensibility points.

The document does not attempt to describe a language library API. For API specs see [specification](specification/README.md).

## Requirements

1. The OpenTelemetry API must be well-defined and clearly decoupled from the implementation. This allows end users to consume API only without also consuming the implementation (see points 2 and 3 for why it is important).

2. Third party libraries and frameworks that add instrumentation to their code will have a dependency only on the API of OpenTelemetry language library. The developers of third party libraries and frameworks do not care (and cannot know) what specific implementation of OpenTelemetry is used in the final application.

3. The developers of the final application normally decide how to configure OpenTelemetry SDK and what extensions to use. They should be also free to choose to not use any OpenTelemetry implementation at all, even though the application and/or its libraries are already instrumented.  The rationale is that third-party libraries and frameworks which are instrumented with OpenTelemetry must still be fully usable in the applications which do not want to use OpenTelemetry (so this removes the need for framework developers to have "instrumented" and "non-instrumented" versions of their framework).

4. Language library implementation must be clearly separated into wire protocol-independent parts that implement common logic (e.g. batching, tag enrichment by process information, etc.) and protocol-dependent telemetry exporters. Telemetry exporters must contain minimal functionality, thus enabling vendors to easily add support for their specific protocol to the language library.


## Language Library Generic Design

Here is a generic design for a language library (arrows indicate calls):

![Language Library Design Diagram](language-library-design.png)

### Expected Usage

The OpenTelemetry Language Library will be composed of 2 packages: API package and SDK package.

Third-party libraries and frameworks that want to be instrumented in OpenTelemetry-compatible way will have a dependency on the API package. The developers of these third-party libraries will add calls to telemetry API to produce telemetry data.

Applications that use third-party libraries that are instrumented with OpenTelemetry API will have a choice to enable or not enable the actual delivery of telemetry data. The application can also call telemetry API directly to produce additional telemetry data.

In order to enable telemetry the application must take a dependency on the OpenTelemetry SDK, which implements the delivery of the telemetry. The application must also configure exporters so that the SDK knows where and how to deliver the telemetry. The details of how exporters are enabled and configured are language specific.


### API and Minimal Implementation

The API package is a self-sufficient dependency, in the sense that if the end-user application or a third-party library depends only on it and does not plug a full SDK implementation then the application will still build and run without failing, although no telemetry data will be actually delivered to a telemetry backend.

This self-sufficiency is achieved the following way.

The API dependency will contain a minimal implementation of the API. When no other implementation is explicitly included in the application no telemetry data will be collected. Here is what active components will look like in this case:

![Minimal Operation Diagram](language-library-minimal.png)

It is important that values returned from this minimal implementation of API are valid and do not require the caller to perform extra checks (e.g. createSpan() method should not fail and should return a valid non-null Span object). The caller should not need to know and worry about the fact that minimal implementation is in effect. This minimizes the boilerplate and error handling in the instrumented code.

It is also important that minimal implementation incurs as little performance penalty as possible, so that third-party frameworks and libraries that are instrumented with OpenTelemetry impose negligible overheads to users of such libraries that do not want to use OpenTelemetry too.

### SDK Implementation

The SDK implementation is a separate (optional) dependency. When it is plugged in it substitutes the minimal implementation that is included in the API package (exact substitution mechanism is language dependent). Here is what active components will look like in this case:

![Full Operation Diagram](language-library-full.png)

It is recommended to decouple common parts of the implementation from protocol-specific Telemetry Exporters. Library designers are encouraged to specify an internal Telemetry Exporter API that defines how protocol-independent and protocol-dependant parts interact. The boundary and design goals for such API will be:

- Place common functionality such as queuing, batching, tagging, etc. in the protocol-independent parts of the implementation. This functionality will be applicable regardless of what Telemetry Exporter is used.

- Minimize burden of implementation for protocol-dependant telemetry exporters. The Telemetry Exporter is expected to be primarily a simple telemetry data encoder and transmitter.

- Use efficient data structures that are well suited for fast serialization to wire formats and minimize the pressure on memory managers. The latter typically requires understanding of how to optimize the rapidly-generated, short-lived telemetry data structures to make life easier for the memory manager of the specific language. General recommendation is to minimize the number of allocations and use allocation arenas where possible, thus avoiding explosion of allocation/deallocation/collection operations in the presence of high rate of telemetry data generation.

### Alternate Implementations

The end-user application may decide to take a dependency on alternate implementation. 

The SDK provides flexibility and extensibility that may be used by many implementations. Before developing an alternative implementation, please, review extensibility points provided by OpenTelemetry.

An example use case for alternate implementations is automated testing. A mock implementation can be plugged in during automated tests. For example it can store all generated telemetry data in memory and provide a capability to inspect this stored data. This will allow the tests to verify that the telemetry is generated correctly. Language Library authors are encouraged to provide such mock implementation.

Note that mocking is also possible by using the SDK and a Mock Exporter without needed to swap out the entire SDK. 

The mocking approach chosen will depend on the testing goals and at which point exactly it is desirable to intercept the telemetry data path during the test.