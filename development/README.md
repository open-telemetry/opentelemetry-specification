# Features in Development

This folder is used for features in
[Development](../specification/document-status.md). `Development` status is for components
that are on track to become part of the specification, but that require a faster cadence
of merges and collaboration.

Features in Development must be:

- Implementable as a plugin to OpenTelemetry components (API, SDK, collector, etc.).
- Be in active development or testing.
- Approved as a general direction via OTEP process.

To avoid any confusion, all files in this directory must have a note about its Development status.

Development status precedes the alpha version (see
[OTEP 0232](../oteps/0232-maturity-of-otel.md#explanation)).
All changes in the `development` folder go through the regular review process. Changes are allowed to be merged faster as completeness of a solution is not a requirement. Approval means that proposed changes are OK for experimentation.

When the feature or parts of it are developed far enough to declare them as an alpha version of a main project and move out of the Development status, it must go through a **new** OTEP PR and it must be expected that design and APIs will be changed. In fact, the same people who approved the experiment may likely be the most critical reviewers. It demonstrates an interest and involvement, not critique.
