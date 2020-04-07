# OpenTelemetry Logs Vision

The following are high-level items that define our long-term vision for 
Logs support in OpenTelemetry project, what we aspire to achieve.

This a vision document that reflects our current desires. It is not a commitment
to implement everything precisely as listed. The primary purpose of this
document is to ensure all contributors work in alignment. As our vision changes
over time maintainers reserve the right to add, modify, and remove items from
this document.

(The content in this proposal is a starting point for discussion. I believe it
is important for us to collectively come up with such vision. I am posting
this PR largely to open the discussion. Comments, thoughts and opinions are
highly welcome!)

This document uses vocabulary introduced in https://github.com/open-telemetry/oteps/pull/91.

### First-class Citizen

Logs are a first-class citizen in observability, along with traces and metrics.
We will aim to have best-in-class support for logs at OpenTelemetry.

### Correlation

OpenTelemetry will define how logs will be correlated with traces and metrics
and how this correlation information will be stored.

Correlation will work across 2 major dimensions:
- To correlate telemetry emitted for the same request (also known as Request
  or Trace Context Correlation),
- To correlate telemetry emitted from the same source (also known as Resource
  Context Correlation).

### Logs Data Model

We will design a Log Data model that will aim to correctly represent all types
of logs. The purpose of the data model is to have a common understanding of what
a log record is, what data needs to be recorded, transferred, stored and
interpreted by a logging system.

Existing log formats can be unambiguously mapped to this data model. Reverse 
mapping from this data model is also possible to the extent that the target log 
format has equivalent capabilities.

We will produce mapping recommendations for commonly used log formats.

### Log Protocol

Armed with the Log Data model we will aim to design a high performance protocol
for logs, which will pursue the same [design goals](https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/protocol/design-goals.md)
as we had for the traces and metrics protocol.

Most notably the protocol will aim to be highly reliable, have low resource
consumption, be suitable for all participant nodes, ensure high throughput,
allow backpressure signalling and be load-balancer friendly (see the design
goals link above for clarifications).

The reason for this design is to have a single OpenTelemetry protocol that can
deliver logs, traces and metrics via one connection and satisfy all design
goals.

### Unified Collection

We aim to have high-performance, unified
[Collector](https://github.com/open-telemetry/opentelemetry-collector/) that
support logs, traces and metrics in one package, symmetrically and uniformly for
all 3 types of telemetry data (see also
[Collector vision](https://github.com/open-telemetry/opentelemetry-collector/blob/8310e665ec1babfd56ca5b1cfec91c1f997f4f2c/docs/vision.md)).

The unified Collector will support multiple log protocols including the newly
designed OpenTelemetry log protocol.

Unified collection is important for the following reasons:
- One agent (or one collector) to deploy and manage.
- One place of configuration for target endpoints, authentication tokens, etc.
- Uniform tagging of all 3 types of telemetry data (enrichment by attributes
  of resources where the data comes from or by user-defined attributes),
  enabling correct correlation across Resource dimensions later on the backend.

## Cloud Native

We will have best-in-class support for logs emitted in cloud native environments
(e.g. Kubernetes, serverless, etc), including legacy applications running
in such environments. This is in line with our CNCF mission.

## Support Legacy

We will produce guidelines on how legacy applications can emit logs in a
manner that makes them compatible with OpenTelemetry's approach and enables
telemetry data correlation. We will also have a reasonable story around
logs that are emitted by sources over which we may have no control and which
emit logs in pre-defined formats via pre-defined mediums (e.g. flat file logs,
Syslog, etc).

We will have technical solutions or guidelines for using popular logging
libraries in a OpenTelemetry-compatible manner and we may produce logging
libraries for languages where gaps exist.

This is important because we believe software that was created before
OpenTelemetry should not be disregarded and should benefit from OpenTelemetry
efforts where possible.

### Auto-instrumentation

To enable functionality that requires modification of how logs are emitted we
will work on auto-instrumenting solutions. This will reduce the adoption barrier
for existing deployments.

### Applicable to All Log Sources

Logging support at OpenTelemetry will be applicable to all sorts of log sources:
system logs, infrastructure logs, third-party and first-party application logs.

### Standalone and Embedded Logs

OpenTelemetry will support both logs embedded inside [Spans](https://github.com/open-telemetry/opentelemetry-specification/blob/master/specification/api-tracing.md#span)
and standalone logs recorded elsewhere. The support of embedded logs is
important for OpenTelemetry's primary use cases, where errors and exceptions
need to be embedded in Spans. The support of standalone logs is important for
legacy applications which may not emit Spans at all.

## Legacy Use Cases

Logging technology has a decades-long history. There exists a large number of
logging libraries, collection agents, network protocols, open-source and
proprietary backends. We recognize this fact and aim to make our proposals in a
manner that honours valid legacy use-cases, while at the same time suggests
better solutions where they are due.
