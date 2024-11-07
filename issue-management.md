# Issue Management

## Roles

- Author:
  - This is the person who has opened or posted the issue.
- Collaborator:
  - Person(s) that are actually doing the work related to the ticket. Once work is done,
    they work with the Reviewer to get feedback implemented and complete the work. They
    are responsible for making sure issue status labels are up to date.
- Reviewer:
  - Person whose Approval is needed to merge the PR.
- Sponsor:
  - The [specification sponsors](https://github.com/open-telemetry/community/blob/main/community-membership.md#specification-sponsor), identified as the assignee of the issue, is responsible for the completion of the issue.
- Triager:
  - This person is responsible for applying appropriate labels as outlined below,
    following up on issues to ensure they are complete,
    and closing issues that are too vague or out of scope.
    They should work closely with the author to analyze the issue and add relevant
    details/information/guidance that would be helpful to the resolution of the issue.

## Issue Triage

Issue triagers are responsible for applying the labels defined below which indicate
what stage of the process an issue is in. There are 3 main categories of triage labels:
deciding, accepted, and rejected. Within each category, there are several labels
which provide more context. Following are the definitions of each triage label and when they are applied.

### `triage:deciding:*`

These labels are applied to issues when it is unclear yet if they are something the project will take on.

* `triage:deciding:community-feedback` - This issue is open to community discussion. If the community can provide sufficient reasoning, it may be accepted by the project.
* `triage:deciding:needs-info` - This issue does not provide enough information for the project to accept it. It is left open to provide the author with time to add more details.
* `triage:deciding:tc-inbox` - This issue needs attention from the TC in order to move forward. It may need TC input for triage, or to unblock a discussion that is deadlocked.

### `triage:accepted:*`

These labels are applied to issues that describe a problem that is in scope and that we would like to tackle.
Just because an issue is accepted does not mean that a solution suggested by the issue will be the solution applied.

* `triage:accepted:ready` - This issue is ready to be implemented. It is either small enough in scope or uncontroversial enough to be implemented without a TC sponsor.
* `triage:accepted:ready-with-sponsor` - This issue is ready to be implemented and has a specification sponsor assigned.
* `triage:accepted:needs-sponsor` - This issue is ready to be implemented, but does not yet have a specification sponsor. A pull request without a specification sponsor may not be reviewed in a timely manner.

### `triage:followup`

This label is managed [by an automated workflow](https://github.com/open-telemetry/opentelemetry-specification/blob/main/.github/scripts/triage-helper/app.py) and should not be added manually. The label is added to issues that meet both of these criteria:
* The issue has a `triage:deciding:*` label and does not already have the `triage:followup` label
* There has been at least one comment or reference since the most recent triage, where a triage is one of these
  * `triage:deciding:*` label was added
  * `triage:followup` label was removed

### `triage:rejected:*`

Rejected issues are issues that describe a problem that cannot or will not be solved by the project in the proposed form.

* `triage:rejected:declined`
* `triage:rejected:duplicate`
* `triage:rejected:insufficient-info`
* `triage:rejected:out-of-scope`
* `triage:rejected:scope-too-large`

## SIG Specific Issues

Many SIGs track work in the specification repo that is outside of the triage process listed above.
These issues, which may be created by a SIG or just assigned to them, should be added to the SIG's project board and given the label `sig-issue`.
If an issue is labeled as a `sig-issue`, it is the responsibility of the SIG to prioritize
the issue appropriately, and ensure it is completed or closed as won't fix.
