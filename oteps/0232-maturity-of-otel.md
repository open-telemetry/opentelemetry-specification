# Definition of maturity levels to be uniformly used by OpenTelemetry SIGs

On 08 Mar 2023, the OpenTelemetry GC and TC held an OpenTelemetry Leadership summit, discussing various topics. One of the themes we discussed was establishing standard rules for describing the maturity of the OpenTelemetry project. This OTEP summarizes what was discussed there and is intended to have the wider community provide feedback.

This OTEP builds on what was previously communicated by the project, especially the [Versioning and stability for OpenTelemetry clients](https://opentelemetry.io/docs/reference/specification/versioning-and-stability).

The Collector's [stability levels](https://github.com/open-telemetry/opentelemetry-collector#stability-levels) inspired the maturity levels.

## Motivation

Quite often, the community is faced with the question of the quality and maturity expectations of its diverse set of components. This OTEP aims to bring clarity by establishing a framework to communicate the maturity for SIG deliverables and components in the name of the project. As the OpenTelemetry project comprises a multitude of SIGs, and each SIG has several components of varying quality, having this framework will help set the right expectations for OpenTelemetry users using a unified nomenclature.

## Explanation

### Maturity levels

Deliverables of a SIG MUST have a declared maturity level, established by SIG maintainers (SIGs), likely with the input of the code owners. While the main deliverable can have a specific maturity level, individual components might have a different one. Examples:

* the Collector core distribution might declare itself stable and include a receiver that is not stable. In that case, the receiver has to be clearly marked as such
* the Java Agent might be declared stable, while individual instrumentation packages are not

Components SHOULD NOT be marked as stable if their user-visible interfaces are not stable. For instance, if the Collector's component "otlpreceiver" declares a dependency on the OpenTelemetry Collector API "config" package which is marked with a maturity level of "beta", the "otlpreceiver" should be at most "beta". Maintainers are free to deviate from this recommendation if they believe users are not going to be affected by future changes.

For the purposes of this document, a breaking change is defined as a change that may require consumers of our components to adapt themselves in order to avoid disruption to their usage of our components.

#### Development

Not all pieces of the component are in place yet, and it might not be available for users yet. Bugs and performance issues are expected to be reported. User feedback around the UX of the component is desired, such as for configuration options, component observability, technical implementation details, and planned use-cases for the component. Configuration options might break often depending on how things evolve. The component SHOULD NOT be used in production. The component MAY be removed without prior notice.

#### Alpha

This is the default level: any components with no explicit maturity level should be assumed to be "Alpha". The component is ready to be used for limited non-critical production workloads, and the authors of this component welcome user feedback. Bugs and performance problems are encouraged to be reported, but component owners might not work on them immediately. The component's interface and configuration options might often change without backward compatibility guarantees. Components at this stage might be dropped at any time without notice.

#### Beta

Same as Alpha, but the interfaces (API, configuration, generated telemetry) are treated as stable whenever possible. While there might be breaking changes between releases, component owners should try to minimize them. A component at this stage is expected to have had exposure to non-critical production workloads already during its Alpha phase, making it suitable for broader usage.

#### Release Candidate

The component is feature-complete and ready for broader usage. The component is ready to be declared stable, it might just need to be tested in more production environments before that can happen. Bugs and performance problems are expected to be reported, and there's an expectation that the component owners will work on them. Breaking changes, including configuration options and the component's output, are only allowed under special circumstances. Whenever possible, users should be given prior notice of the breaking changes.

#### Stable

The component is ready for general availability. Bugs and performance problems should be reported, and there's an expectation that the component owners will work on them. Breaking changes, including configuration options and the component's output, are only allowed under special circumstances. Whenever possible, users should be given prior notice of the breaking changes.

#### Deprecated

Development of this component is halted. No new versions are planned, and the component might be removed from its included distributions. Note that new issues will likely not be worked on except for critical security issues. Components that are included in distributions are expected to exist for at least two minor releases or six months, whichever happens later. They also MUST communicate in which version they will be removed, either in terms of a concrete version number or the date of a release, like: "the first release after 2023-08-01".

#### Unmaintained

A component identified as unmaintained does not have an active code owner. Such components may have never been assigned a code owner, or a previously active code owner has not responded to requests for feedback within 6 weeks of being contacted. Issues and pull requests for unmaintained components SHOULD be labeled as such. After 6 months of being unmaintained, these components MAY be deprecated. Unmaintained components are actively seeking contributors to become code owners.

## Trade-offs and mitigations

This OTEP allows SIG maintainers to declare the maturity of the SIG's deliverables without declaring which ones are key for OpenTelemetry. When, and if, this is needed, a new OTEP may be created using the maturity levels as a possible framework.

## Prior art and alternatives

* The specification status has a ["Component Lifecycle"](https://opentelemetry.io/docs/specs/status/) description, with definitions that might overlap with some of the levels listed in this OTEP.
* The same page lists the status of the different parts of the spec
* The ["Versioning and stability for OpenTelemetry clients"](https://opentelemetry.io/docs/specs/otel/versioning-and-stability/#signal-lifecycle) page has a detailed view on the lifecycle of a signal and which general stability guarantees should be expected by OpenTelemetry clients. Notably, it lacks information about maturity of the Collector. This OTEP could be seen as clashing with the last section of that page, "OpenTelemetry GA". But while that page established a point where both OpenTracing and OpenCensus would be considered deprecated, this OTEP here defines the criteria for calling OpenTelemetry "stable" and making that a requirement for a future graduation. This would also make it clear to end-users which parts of the project they can rely on.
* The OpenTelemetry Collector has its own [stability levels](https://github.com/open-telemetry/opentelemetry-collector#stability-levels), which served as inspiration to the ones here.
* [Definition of documentation states](https://opentelemetry.io/docs/specs/otel/document-status/)
* [Telemetry stability](https://opentelemetry.io/docs/specs/otel/telemetry-stability/) (uses unstable instead of experimental)

## Open questions

* Should SDKs be required to fully implement the specification before they can be marked as stable? See [open-telemetry/opentelemetry-specification#3673](https://github.com/open-telemetry/opentelemetry-specification/issues/3673)
* Should this OTEP define a file name to be adopted by all repositories to declare their deliverables and their maturity levels?

## Future possibilities

Once the maturity levels are widely adopted, the GC/TC might decide to pick and choose components from different SIGs and proceed with a graduation proposal within the CNCF. The decision framework for choosing the components will be defined at a later stage.
