# Maturity levels

**Status**: [Stable][]

Deliverables of a SIG MUST have a declared maturity level, established by SIG
maintainers, likely with the input of the code owners. While the main
deliverable can have a specific maturity level, individual components might
have a different one. Examples:

- Collector core distribution might declare itself [Stable][] and include a
  receiver that is not [Stable][]. In that case, the receiver has to be clearly
  marked as such
- Java agent might be declared [Stable][], while individual instrumentation
  packages are not

Components SHOULD NOT be marked as [Stable][] if their user-visible interfaces are
not [Stable][]. For instance, if the Collector's component `otlpreceiver` declares
a dependency on the OpenTelemetry Collector API "config" package which is
marked with a maturity level of [Beta][], the `otlpreceiver` should be at most
[Beta][]. Maintainers are free to deviate from this recommendation if they
believe users are not going to be affected by future changes.

For the purposes of this document, a breaking change is defined as a change
that may require consumers of our components to adapt themselves in order to
avoid disruption to their usage of our components.

## Development

Not all pieces of the component are in place yet, and it might not be available
for users yet. Bugs and performance issues are expected to be reported. User
feedback around the UX of the component is desired, such as for configuration
options, component observability, technical implementation details, and
planned use-cases for the component. Configuration options might break often
depending on how things evolve. The component SHOULD NOT be used in
production. The component MAY be removed without prior notice.

## Alpha

This is the default level: any components with no explicit maturity level
should be assumed to be Alpha. The component is ready to be used for limited
non-critical production workloads, and the authors of this component welcome
user feedback. Bugs and performance problems are encouraged to be reported,
but component owners might not work on them immediately. The component's
interface and configuration options might often change without backward
compatibility guarantees. Components at this stage might be dropped at any
time without notice.

## Beta

Same as [Alpha][], but the interfaces (API, configuration, generated telemetry)
are treated as [Stable][] whenever possible. While there might be breaking changes
between releases, component owners should try to minimize them. A component at
this stage is expected to have had exposure to non-critical production
workloads already during its [Alpha][] phase, making it suitable for broader
usage.

## Release Candidate

The component is feature-complete and ready for broader usage. The component
is ready to be declared [Stable][], it might just need to be tested in more
production environments before that can happen. Bugs and performance problems
are expected to be reported, and there's an expectation that the component
owners will work on them. Breaking changes, including configuration options
and the component's output, are only allowed under special circumstances.
Whenever possible, users should be given prior notice of the breaking changes.

## Stable

The component is ready for general availability. Bugs and performance problems
should be reported, and there's an expectation that the component owners will
work on them. Breaking changes, including configuration options and the
component's output, are only allowed under special circumstances. Whenever
possible, users should be given prior notice of the breaking changes.

## Deprecated

Development of this component is halted. No new versions are planned, and the
component might be removed from its included distributions. Note that new
issues will likely not be worked on except for critical security issues.
Components that are included in distributions are expected to exist for at
least two minor releases or six months, whichever happens later. They also
MUST communicate in which version they will be removed, either in terms of a
concrete version number or the date of a release, like: "the first release
after 2023-08-01".

## Unmaintained

A component identified as Unmaintained does not have an active code owner.
Such components may have never been assigned a code owner, or a previously
active code owner has not responded to requests for feedback within 6 weeks of
being contacted. Issues and pull requests for Unmaintained components SHOULD
be labeled as such. After 6 months of being Unmaintained, these components MAY
be [Deprecated][]. Unmaintained components are actively seeking contributors to
become code owners.

## References

- [OTEP0232 Definition of maturity levels to be uniformly used by OpenTelemetry SIGs](../oteps/0232-maturity-of-otel.md)

[Alpha]: #alpha
[Beta]: #beta
[Deprecated]: #deprecated
[Stable]: #stable
