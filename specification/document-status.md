# Definitions of Document Statuses

Specification documents (files) may explicitly define a "Status", typically
shown immediately after the document title. When present, the "Status" applies
to the individual document only and not to the entire specification or any other
documents. The following table describes what the statuses mean.

## Maturity levels

The support guarantees and allowed changes are governed by the maturity level of the document. Maturity levels are defined in [OTEP 0232](../oteps/0232-maturity-of-otel.md#explanation) and follow the OpenTelemetry project's standard framework for describing component maturity.

|Status              |Explanation|
|--------------------|-----------|
|No explicit "Status"|Equivalent to Alpha.|
|Development        |Not all pieces of the component are in place yet, and it might not be available for users yet. Bugs and performance issues are expected to be reported. User feedback around the UX of the component is desired, such as for configuration options, component observability, technical implementation details, and planned use-cases for the component. Configuration options might break often depending on how things evolve. The component SHOULD NOT be used in production. The component MAY be removed without prior notice.|
|Alpha              |The component is ready to be used for limited non-critical production workloads, and the authors of this component welcome user feedback. Bugs and performance problems are encouraged to be reported, but component owners might not work on them immediately. The component's interface and configuration options might often change without backward compatibility guarantees. Components at this stage might be dropped at any time without notice.|
|Beta               |Same as Alpha, but the interfaces (API, configuration, generated telemetry) are treated as stable whenever possible. While there might be breaking changes between releases, component owners should try to minimize them. A component at this stage is expected to have had exposure to non-critical production workloads already during its Alpha phase, making it suitable for broader usage.|
|Release Candidate  |The component is feature-complete and ready for broader usage. The component is ready to be declared stable, it might just need to be tested in more production environments before that can happen. Bugs and performance problems are expected to be reported, and there's an expectation that the component owners will work on them. Breaking changes, including configuration options and the component's output, are only allowed under special circumstances. Whenever possible, users should be given prior notice of the breaking changes.|
|Stable             |The component is ready for general availability. Bugs and performance problems should be reported, and there's an expectation that the component owners will work on them. Breaking changes, including configuration options and the component's output, are only allowed under special circumstances. Whenever possible, users should be given prior notice of the breaking changes. See [stability guarantees](versioning-and-stability.md#stable) for details.|
|Deprecated         |Development of this component is halted. No new versions are planned, and the component might be removed from its included distributions. Note that new issues will likely not be worked on except for critical security issues. Components that are included in distributions are expected to exist for at least two minor releases or six months, whichever happens later. They also MUST communicate in which version they will be removed.|
|Unmaintained       |A component identified as unmaintained does not have an active code owner. Such components may have never been assigned a code owner, or a previously active code owner has not responded to requests for feedback within 6 weeks of being contacted. Issues and pull requests for unmaintained components SHOULD be labeled as such. After 6 months of being unmaintained, these components MAY be deprecated. Unmaintained components are actively seeking contributors to become code owners.|

The specification follows
[OTEP 0232](../oteps/0232-maturity-of-otel.md#explanation)
maturity level definitions.

## Feature freeze

In addition to the maturity levels above, documents may be marked as `Feature-freeze`. These documents are not currently accepting new feature requests, to allow the Technical Committee time to focus on other areas of the specification. Editorial changes are still accepted. Changes that address production issues with existing features are still accepted.

Feature freeze is separate from a maturity level. The maturity level represents the support requirements for the document, feature freeze only indicates the current focus of the specification community. The feature freeze label may be applied to a document at any maturity level. By definition, deprecated documents have a feature freeze in place.

## Mixed

Some documents have individual sections with different statuses. These documents are marked with the status `Mixed` at the top, for clarity.
