# OpenTelemetry Language Library Design Principles

This document defines common principles that will help designers to create language libraries that are ergonomic to use, enable multiple use cases for library users, are to a certain extent uniform across all supported languages, yet allow enough flexibility for language-specific expressiveness.

The document does not attempt to describe a language library API. For API specs see [Tracing API](tracing-api.md), [Resources API](resources-api.md).

## Requirements

1. The public API must be well-defined and clearly decoupled from the implementation, enabling end-users to swap out for alternate implementations.

2. Third party libraries and frameworks that add instrumentation to their code will have a dependency only on the public API of OpenTelemetry language library. The developers of third party libraries and frameworks do not care (and cannot know) what specific implementation of OpenTelemetry is used in the final application.

3. The developers of the final application normally decide what OpenTelemetry implementation to plug in. They should be also free to choose to not use any OpenTelemetry implementation at all, even though the application and/or its libraries are already instrumented.  The rationale is that third-party libraries and frameworks which are instrumented with OpenTelemetry must still be fully usable in the applications which do not want to use OpenTelemetry (so this removes the need for framework developers to have "instrumented" and "non-instrumented" versions of their framework).

4. Full implementation must be clearly separated into wire protocol-independent parts that implement common logic (e.g. batching, tag enrichment by process information, etc.) and protocol-dependent exporters. Protocol-dependent exporters must contain minimal functionality, thus enabling vendors to easily add support for their specific protocol to the language library.


## Proposed Generic Design

Here is a proposed generic design for a language library:

![Language Library Design Diagram](language-library-design.png)

### Public API

The instrumentation code in the end-user application and in the instrumented third-party libraries that are used by the application will call the public API of OpenTelemetry Language Library.

The public API package is a self-sufficient dependency, in the sense that if the end-user application depends only on it and does not plug a full implementation then the application will still build and run without failing, although no telemetry data will be actually delivered to a telemetry backend.

This self-sufficiency is achieved the following way.

The public API dependency will contain a minimal, virtually no-op implementation of the API. When no other implementation is explicitly included in the application all telemetry calls will effectively be no-op, any generated telemetry data will be discarded. 

It is important that values returned from this no-op implementation of API are valid and do not require the caller to perform extra checks (e.g. createSpan() method should not fail and should return a valid non-null Span object). The caller should not need to know and worry about the fact that no-op implementation is in effect. This minimizes the boilerplate and error handling in the instrumented code.

It is also important that no-op implementation incurs as little performance penalty as possible, so that third-party frameworks and libraries that are instrumented with OpenTelemetry impose negligible overheads to users of such libraries that do not want to use OpenTelemetry too.

## Full SDK Implementation
The Full SDK implementation is a separate (optional) dependency. When it is plugged in it substitutes the no-op implementation that is included in the Public API package (exact substitution mechanism is language dependent).

It is recommended to decouple common parts of the implementation from protocol-specific portion. Library designers are encouraged to specify an internal Exporter API that defines how protocol-independent and protocol-dependant parts interact. The design goals for such API will be:

- Minimize burden of implementation for protocol-dependant parts and avoid duplicate implementation of the same functionality.

- Use efficient data structures that are well suited for fast serialization to wire formats and minimize the pressure on memory managers. The latter typically requires understanding of how to optimize the rapidly-generated, short-lived telemetry data structures to make life easier for the memory manager of the specific language. General recommendation is to minimize the number of allocations and use allocation arenas where possible, thus avoiding explosion of allocation/deallocation/collection operations in the presence of high rate of telemetry data generation.

## Alternate Implementations

The end-user application may decide to take a dependency on alternate implementation. 

The alternate implementation may provide functionality that is identical to the official full SDK, but for example has better performance characteristics. This opens up the possibility of having competing and better implementations.

Another common use case for alternate implementations is automated testing. A mock implementation can be plugged in during automated tests. For example it can store all generated telemetry data in memory and provide a capability to inspect this stored data. This will allow the tests to verify that the telemetry is generated correctly. Language Library authors are encouraged to provide such mock implementation.
