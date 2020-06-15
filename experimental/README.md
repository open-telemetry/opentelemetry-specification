# Experimental features

This folder will be used to develop experimental features. Experimental status allows to develop components that are on trajectory to become a part of a main project while allowing a faster cadence of merges and collaboration.

Experimental features must be:

- Implementable as a plugin to OpenTelemetry components (API, SDK, collector, etc.).
- Be in active development or testing.
- Approved as a general direction via OTEP process.

All files in experimental folder must have a note about it's experimental status to avoid any confusion.

Experimental status precedes the alpha version. All changes in the experimental folder go through the regular review process. Changes are allowed to be merged faster as completeness of a solution is not a requirement. Approval means that proposed changes are OK for experimentation.

When the feature or parts of it are developed far enough to declare them as an alpha version of a main project and move out of the experimental status, it must go through a **new** OTEP PR and it must be expected that design and APIs will be changed. In fact, the same people who approved the experiment may likely be the most critical reviewers. It demonstrates an interest and involvement, not critique.
