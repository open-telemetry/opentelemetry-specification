# Technical Review and Specification Conformance for ${LANGUAGE}/${SIGNAL}/${MAJOR_VERSION} library

Technical Committee Sponsor(s): []

Expected Release Date: []

Expected Version Number: []

Spec Compliance Matrix is up to date: [Permanent link to the matrix]

Versioning And Stability Document: [Link to version document]

Public Code Documentation: [Link to godoc, javadoc, etc.]

Public Examples: [Link to couple of official usage examples]

Discovered Issues: [List of filed issues by the TC members during the review process]

## TODOs

This section must be deleted when the PR for starting the review is opened,
but it contains a list of important TODOs that maintainers MUST do before starting the process.

The Language Maintainers MUST:

* Prior to starting the review, update the
[compliance matrix](https://github.com/open-telemetry/opentelemetry-specification/blob/main/spec-compliance-matrix.md)
for that language/signal.
* Each language implementation MUST follow
[the versioning and stability requirements](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/versioning-and-stability.md)
and prepare the public documentation about the versioning and stability guarantees.
* Work with a Technical Committee Sponsor(s) during review. The Technical
Committee members are not language experts, and are expected to work with the
language maintainers and/or invited language experts to perform this review
process. Language maintainers SHOULD respond to any question/issue
(github issues, github discussions, gitter, or comments in the review PR)
during the review time in a reasonable amount of time to not delay the review
process (ideally 1 business day).

It is highly recommended to have at least 2 members of the Technical Committee
as sponsors. Any Technical Committee member can be a sponsor, and any Technical
Committee member can provide feedback during the review process.

Technical Committee Sponsor(s) MUST:

* Do the due diligence and review the public documentation and examples, and
ensure specification conformance.
* Ensure conformance with the versioning and stability document.
* Ensure consistent names across implementations (e.g. TraceId vs GlobalId)
* Avoid confusions across implementation (e.g. same public API has different behaviors)
* Ensure no experimental features (signals) are part of the released packages (e.g. api, sdk, etc.).

The OpenTelemetry Technical Committee MUST attend one of the language SIG
meetings and have a public discussion with the language maintainers to discuss
any issues found during the review process.
