# Post-GA Workflow

## Specification Changes

The following changes to the Specification v1.x will be allowed after GA:

- Editorial changes.
- API: additive, non-breaking changes. This is done in order to stay
  compatible with previous versions. Adding entirely new API components,
  such as logging, is thus allowed.
- SDK changes.
- Semantic conventions for new libraries.

The `main` branch will always contain the latest changes, and branches will be used to track published releases.

API-breaking changes can be accepted under `experimental` subdirectories.

## OTEPS

OTEPs are used as a mean to add entirely new components (such as logging) or to introduce API-breaking changes. They will have similar rules as Specification PRs regarding their lifetime:

- OTEP PRs will be automatically marked stale after 14 days without activity.
- OTEP PRs will be automatically closed 14 days after being marked stale.

## Releases

Minor releases are expected to approximately happen every 6 months, containing additive, non-breaking changes in the API, as mentioned above.

Major releases are allowed to contain breaking changes in the API.

Language SIGs releases MUST point to what Specification Tag/Version are they complying to.
