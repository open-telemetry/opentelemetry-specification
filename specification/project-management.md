# Project Management

Some specification changes are small enough in scope such that they can be resolved with a single PR or an OTEP written by a single person. However, this is rarely the case for large, meaningful changes. Most spec work ends up being organized into projects.

At minimum, specification projects require the following resources to be successful:

* A group of designers and subject matter experts need to dedicate a significant amount of their work time to the project. These participants are needed to design the spec, write a set of OTEPs, and create multiple prototypes. This group needs to meet with each other (and  with TC members) on a regular basis to develop a  successful set of  proposals.
* A portion of the TC needs to be aware of and participate in the development of the project, to review the proposals and help guide the participants through the specification process.
* Spec approvers and the broader community need to be aware of progress being made on the project, so they can be prepared to participate when proposals are ready for review.

## Project Tracking Issue

Every project has a high level **Project Tracking Issue**, which describes the project. This issue is frequently edited and kept up to date by the working group. To create a tracking issue, please use the Project Tracking Issue template.

The project tracking issue must contain the following information:

### Description

Describes the goals, objectives, and requirements for the project. This include the motivations for starting the project now, as opposed to later.

### Project Board

Projects should be managed using a github project board. The project board should be pre-populated with issues that cover all known deliverables, organized by timeline milestones. The project board should be linked to in the tracking issue.

A TC member associated with the project can create the board, along with a new github label to automatically associate issues and PRs with the project. The project lead and all other relevant project members should have edit access to the board.
The project lead is responsible for maintaining the board and keeping it up-to-date.

### Deliverables

A description of what this project is planning to deliver, or is in the process of delivering. This includes all OTEPs and their associated prototypes.

In general, OTEPs are not accepted unless they come with working prototypes available to review in at least two languages. Please discuss these requirements with a TC member before submitting an OTEP.

### Staffing / Help Wanted

Who is currently planning to work on the project? If a project requires specialized domain expertise, please list it here. If a project is missing a critical mass of people in order to begin work, please clarify.

#### Required staffing

Projects cannot be started until the following participants have been identified:

* Every project needs a project lead, who is willing to bottom line the project and address any issues which are not handled by other project members.
* At least two sponsoring TC members. TC sponsors are dedicated to attending meetings, reviewing proposals, and in general being aware of the state of the project and it’s technical details. TC sponsors guide the project through the spec process, keep the tracking issue up to date, and help to ensure that relevant community members provide input at the appropriate times.
* Engineers willing to write prototypes in at least two languages (if relevant to project). Languages should be fairly different from each other (for example. Java and Python).
* Maintainers or approvers from those languages committed to reviewing the prototypes.

### Meeting Times

Once a project is started, the working group should meet regularly for discussion. These meeting times should be posted on the OpenTelemetry public calendar.

### Timeline

What is the expected timeline the project will aim to adhere to, and what resources and deliverables will be needed for each portion of the timeline? If the project has not been started, please describe this timeline in relative terms (one month in, two weeks later, etc). If a project has started, please include actual dates.

### Labels

The tracking issue should be properly labeled to indicate what parts of the specification it is focused on.

### Linked Issues and PRs

All PRs, Issues, and OTEPs related to the project should link back to the tracking issue, so that they can be easily found.

## Specification Project Lifecycle

All specification projects have the same lifecycle, and are tracked on the Specification Project Board, which the community can use to get a high-level view of the specification roadmap.

The project lifecycle is as follows:

* A **Project Tracking Issue** is created. The tracking issue includes all the necessary information for the TC and spec community to evaluate the breadth and depth of the work being proposed.
* If a project is approved, it is added to the list of **Potential Projects**. This list is roughly ordered in the order we expect we will start the project.
* Potential projects are moved to the list of **Scheduled Projects** once they have a planned start date. Having a planned start date lets potential contributors know when they need to make themselves available, and get prepared to begin their work. Subject matter experts and participants who plan to do a lot of work – such as building prototypes – benefit greatly from having a start date, as they can plan for their participantion with their employers and coworkers.
* Once a project is begun, it is moved to the list of **Current Projects**. Projects are only started when the necessary resources are available to move them quickly to completion. This means that the necessary subject matter experts have been identified, and at least two TC members are committed to review and guide the project through the specification process.
* Once all OTEPs have been approved and integrated into the spec, and the working group is no longer meeting, projects are moved to **Completed Projects**.

## Project Board

To track our specification projects, we use a GitHub project board. This board only contains Project Tracking Issues, and is organized into the following columns:

### Current Projects

Projects that are actively being moved to completion. Projects may be in one of  several different states: design, proposal review, and implementation.

### Scheduled Projects

Many projects require people (such as subject matter experts) and other resources whose participation/availability must be planned out in advance. In general, projects may be able to move faster when their start date is scheduled and known in advance, so participants can prepare their schedules and do preliminary research.

Scheduled projects are projects which have not started yet, but have a scheduled start date.

### Potential Projects

Any project which has a tracking issue and has been approved by the TC as a needed feature for OpenTelemetry. Roughly organized by priority.

### Completed Projects

Projects which have been successfully implemented, and no longer need any attention beyond responding to user feedback.
