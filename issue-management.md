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
  - This person, typically a technical committee member or someone the TC has assigned, is responsible for the completion of the issue.
    This may require finding collaborators or reviewers to work on the issue.
    They may also act as collaborator or reviewer, but are not required to do so.
    They are also responsible to make sure the issue is kept up to date and closed when the issue is completed.
    The sponsor is identified as the assignee of the issue.
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

These labels are applied to issues when it is unclear if they are something the project will take on.
This may be because they provide insufficient info to properly describe the problem or if the problem described is potentially out of scope.

* `triage:deciding:community-feedback` - This issue is open to community discussion. If the community can provide sufficient reasoning, it may be accepted by the project.
* `triage:deciding:insufficient-info` - This issue does not provide enough information for the project to accept it. It is left open to provide the author with time to add more details.
* `triage:deciding:tc-inbox`
* `triage:deciding:sig-inbox`

### `triage:accepted:*`

These labels are applied to issues that describe a problem that is in scope and that we would like to tackle.
Just because an issue is accepted does not mean that a solution suggested by the issue will be the solution applied.

* `triage:accepted:ready` - This issue is ready to be implemented. It is either small enough in scope or uncontroversial enough to be implemented without a TC sponsor.
* `triage:accepted:ready-with-sponsor` - This issue is ready to be implemented and has a TC sponsor assigned.
* `triage:accepted:needs-sponsor` - This issue is ready to be implemented, but does not yet have a TC sponsor. A pull request without a TC sponsor may not be reviewed in a timely manner.

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
