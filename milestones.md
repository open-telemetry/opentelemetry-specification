# OpenTelemetry: A Roadmap to Convergence

This document covers the initial milestones for each repository developing an
implementation of the OpenTelemetry Specification for a specific language. For
each new language, we want to quickly achieve parity with existing OpenTracing
and OpenCensus implementations.

[Merging OpenTracing and OpenCensus: A Roadmap to
Convergence](https://medium.com/opentracing/a-roadmap-to-convergence-b074e5815289)
defines the goals and timelines for OpenTelemetry.

If you are interested in starting a new OpenTelemetry implementation, please do
the following:

- [Create an issue](github.com/open-telemetry/community/issues) proposing the
  new repository. Wait for repository to be created.
- Add the milestones listed below to the backlog.

## Switching to OpenTelemetry

For languages which have both an OpenTracing and OpenCensus implementation, we
would like to achieve parity in OpenTelemetry by **September, 2019**, and sunset
the existing OpenTracing and OpenCensus projects by **November, 2019**.

Parity can be defined as the following milestones:

- A set of interfaces which implement the OpenTelemetry specification in a given
  programming language.
- An SDK implementing OpenTelemetry specification.
- Backwards compatibility with OpenTracing and OpenCensus.
- Metadata helpers for recording common operations defined in the OpenTelemetry
  [semantic conventions](https://github.com/open-telemetry/opentelemetry-specification/blob/master/semantic-conventions.md).
- Tests which provide evidence of interoperability.
- Benchmarks which provide evidence of expected resource utilization.
- Documentation and getting started guide.

## Initial milestones

With OpenTelemetry we strive for consistency and unification. It is important
for users of OpenTelemetry to get the same look and feel of APIs and consistent
data collection across all languages. Consistency is achieved thru the
specifications and cross-language test cases.

As OpenTracing and OpenCensus projects converge we write specifications the same
time as we develop libraries.

Initial API specification will be complete **June, 14th**. SDK specification
will be complete end of June. Later we plan to revise specifications for both -
API and SDK every month till September while we are getting feedback. These
revisions will be documented with the CHANGELOG and will likely include breaking
changes.

Languages can use the following milestones to triage issues related to API:

- API Complete: **June, 2019**
- API revisions:
  - API revision 07/2019
  - API revision 08/2019
  - API revision 09/2019

And for SDK:

- SDK Complete: **mid July, 2019**
  - SDK revision 08/2019
  - SDK revision 09/2019

Even though stable version of OpenTelemetry may be limited to API and SDK
packages, we encourage to build a set of exporters and adapters for the most
common platforms and libraries. This milestone will confirm the API and SDK
completeness.

- Basic exporters and adapters: **August, 2019**

Finally, these two milestones can be used for extra work needed to stabilize
OpenTelemetry SDK and sunset OpenTracing and OpenCensus SDKs:

- Stable Version: **September, 2019**
- OpenTracing and OpenCensus sunset: **November, 2019**
