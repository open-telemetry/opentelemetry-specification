# Experimental features

This folder will be used to develop experimental features. Experimental status allows to develop components that are on trajectory to become a part of a main project while allowing a faster cadence of merges and collaboration.

Experimental features must be:

- Implementeable as a plugin to OpenTelemetry components (API, SDK, collector, etc.).
- Be in active development or testing.
- Approved as a general direction via OTEP process.

Experimental status precedes the alpha version. All changes for experimental folder go via the regular review process. Changes are allowed to be merged faster as completeness of a solution is not a requirement. Approval means that proposed changes are OK for experimentation.

When the feature or it's part is developed enough to move to alpha version of a main project and out of experimental status, it must go thru the ***new*** PR and it must be expected that design and APIs will be changed. In fact, the same people who approved the experiment may likely be the most critical reviewers. It demonstrates an interest and involvement, not the critique.
