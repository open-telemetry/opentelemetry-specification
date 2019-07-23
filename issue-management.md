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


## Writing specs

Specification is written in markdown format. Please make sure files are rendered
OK on GitHub.

We highly encourage to use line breaks in markdown files at `80` characters
wide. There are tools that can do it for you effectively. Please submit proposal
to include your editor settings required to enable this behavior so the out of
the box settings for this repository will be consistent.
