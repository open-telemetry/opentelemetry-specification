# New Signal Release Process

This document defines the release requirements and process followed by the
OpenTelemetry libraries, along with the rules and procedures for meeting those
requirements.

In this document, the terms "OpenTelemetry" and "language implementations" both
specifically refer to the OpenTelemetry client libraries. These terms do not
refer to the specification or the Collector in this document.

Every OpenTelemetry official major release MUST follow the release process
proposed in this document. A  "major release" refers to a new version of any
[signal](../specification/glossary.md#signals) (adding a new signal to an
already released major version of the library, or a major version bump for an
existing released signal) for OpenTelemetry client libraries.

The OpenTelemetry [Technical Committee](https://github.com/open-telemetry/community/blob/main/tech-committee-charter.md) (with guidance from language maintainers) is responsible to setup release dates
and ensure quality standards of the official releases
[here](https://github.com/open-telemetry/community/blob/main/tech-committee-charter.md#responsibilities-of-the-technical-committee).

To graduate the release process, each language implementation MUST do:

* Technical and Specification Compliance Review

The OpenTelemetry Technical Committee reserves the right to change and improve
this process during time based on the prior experiences.

## Technical and Specification Compliance Review

The OpenTelemetry [Technical Committee](https://github.com/open-telemetry/community/blob/main/tech-committee-charter.md)
commits to ensure that every decision will be made in less than 14 days (2 weeks)
after the process is started.

To begin the technical and specification compliance review language maintainers
MUST submit a PR and complete this [template](new-signal-release-process-template.md).
The name of the file MUST be `release-review-${LANGUAGE}-${SIGNAL}-v${MAJOR_VERSION}.md`,
and the title of the PR MUST be `Release review for ${LANGUAGE}/${SIGNAL}/v${MAJOR_VERSION}`.

During the review process, breaking changes related to the new signal MAY be
needed to comply with the specification, it is highly recommended to start
the process as soon as possible (a good time would be immediately after the
release of the first RC), but after all features and planned changes are merged.

After the review is approved, it is highly recommended to not make any major
change to the public API because that will cause the review to invalidate and the
process needs to be redone.
