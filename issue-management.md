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

* `triage:deciding:needs-community-feedback` - This issue is open to community discussion. If the community can provide sufficient reasoning, it may be accepted by the project.
* `triage:deciding:needs-info` - This issue does not provide enough information for the project to accept it. It is left open to provide the author with time to add more details.
* `triage:deciding:tc-inbox` - This issue needs attention from the TC in order to move forward. It may need TC input for triage, or to unblock a discussion that is deadlocked.

### `triage:accepted:*`

These labels are applied to issues that describe a problem that is in scope and that we would like to tackle.
Just because an issue is accepted does not mean that a solution suggested by the issue will be the solution applied.

* `triage:accepted:ready` - This issue is ready to be implemented. It is either small enough in scope or uncontroversial enough to be implemented without a TC sponsor.
* `triage:accepted:ready-with-sponsor` - This issue is ready to be implemented and has a specification sponsor assigned.
* `triage:accepted:needs-sponsor` - This issue is ready to be implemented, but does not yet have a specification sponsor. A pull request without a specification sponsor may not be reviewed in a timely manner.

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

## Issues blocking implementation

SIGs that implement and document the specification in their respective language may run into issues with the specification,
that block their implementation, or they may want to request a specification change related to an implementation change. To
highlight issues of that kind SIG maintainers can request a `maintainer-blocked` or `maintainer-request` label being added
to their issue, if the following conditions are met:

* their issue points to at least one issue in an implementation repo, of which they are a maintainer.
* they summarize in the issue description what is blocking this issue and/or what change is required to move that issue forward.
* they tag all maintainers of the implementation repo in the issue description (@open-telemetry/<sig>-maintainers). No action from the other maintainers is expected, except they disagree with
  the request of this issue being tagged as `maintainer-blocked` or `maintainer-request`
* they will share the issue with all other SIGs either via the [Maintainer Meeting](https://github.com/open-telemetry/community?tab=readme-ov-file#cross-cutting-sigs) or via a message to [#otel-maintainers](https://cloud-native.slack.com/archives/C01NJ7V1KRC) on CNCF slack. This way maintainers of other implementation SIGs can comment if they have the same request.

A triager will add the requested label to the issue if those conditions are met. The difference between the 2 labels is as follows:

- `maintainer-blocked` means that there is an issue with the specification that blocks the SIG from implementing an existing part of the specification.
- `maintainer-request` means that there is no blocking issue with an existing part of the specification. This means, that the SIG either wants to implement something that is not yet part of the specification, or that they can go forward with the implementation regardless, but want to clarify ambiguity or inaccuracy.
