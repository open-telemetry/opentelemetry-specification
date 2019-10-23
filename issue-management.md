# Issue Management for OpenTelemetry

It's an important community goal for OpenTelemetry that our members find the backlogs
to be responsive, and easy to take part in. Shared practices will simplify collaboration
and engagement as well as help standardize on automation and overall project management.

SIGs are encouraged to experiment with labels and backlog management procedures,
including project board. This document only covers the bare bones of issue management
which should work the same across all SIGs, to help maintain a responsive backlog and
allow us to track work across all projects in a similar manner.

## Roles

- OP:
  - Original Poster. This is the person who has opened or posted the issue.
- Maintainer (aka Triager, or anyone performing that role):
  - Person who is triaging the issue by determining its workability. This person is
    responsible for getting the tickets to one of two stages - 1) `help-wanted`
    2) `will-not-fix`. They are responsible for triaging by working with the OP to get
    additional information as needed and analyzing the issue and adding relevant
    details/information/guidance that would be helpful to the resolution of the issue.
- Collaborator:
  - Person(s) that are actually doing the work related to the ticket. Once work is done,
    they work with the Reviewer to get feedback implemented and complete the work. They
    are responsible for making sure issue status labels are up to date.
- Reviewer:
  - Person whose Approval is needed to merge the PR.

## Opening an Issue

- An issue is filed by OP.
- A Maintainer responds and asks clarifying questions within 1-2 business days.
- The Maintainer processes the issue and labels it as:
  - `bug`
  - `enhancement`
  - `needs-discussion`
  - `documentation` or
  - `will-not-fix` (thereby closing the issue with explicit reasons)
- The Maintainer can also label the issue as
  - `URGENT` (for critical issues)
  - `help-wanted` for issues which require work and have no one assigned
- Once a Collaborator is assigned, please remove `help-wanted` and add `wip` to
  the issue.

## Closing an Issue

- Review criteria:
  - For interface and design changes: 2 approvals - which must be from reviewers
    who work at different companies than the Collaborator.
  - For smaller or internal changes: 1 approval from a different company.
- For `URGENT` issues:
  - Collaborator: please provide an initial assessment of the issues to OP ASAP or
    within 1 business day, whichever is earlier.
  - Reviewer: please review and provide feedback ASAP or within 1 business day,
    whichever is earlier.
  - Collaborator: please provide an update and/or response to each review comment ASAP
    or within 1 business day, whichever is sooner. Merge should happen as soon as
    review criteria are met.
- For non-`URGENT` issues
  - Collaborator: please provide an initial response or assessment of the issue to
    OP within 3 business days.
  - Reviewer: please review and provide feedback within 3 business days.
  - Collaborator: please provide an update and/or response to each review comment
    within 3 business days. Once all review comments are resolved, please allow
    1-2 business days for others to raise additional comments/questions, unless
    the changes are fixing typos, bugs, documentation, test enhancements, or
    implementing already discussed design.

When closing an issue that we `will-not-fix` or we believe need no further
action, please provide the rationale for closing, and indicate that OP can
re-open for discussion if there are additional info, justification and
questions.

## When Issues Get Stuck

Some issues are not directly related to a particular code change. If an
issue is worth considering in the issue backlog, but not scoped clearly
enough for work to begin, then please label it `needs-discussion`.

- When possible, move the discussion forward by using tests and code examples.
- If discussion happens elsewhere, record relevant meeting notes into the
  issue.
- When an agreement is made, clearly summarize the decision, and list any
  resulting action items which need to be addressed.

If an issue is stuck because someone is not responding, please add the `stale`
label. It is possible to automate this. E.g. <https://github.com/apps/stale>
The minimum time elapsed before the `stale` label is applied is proposed to be
one week.
