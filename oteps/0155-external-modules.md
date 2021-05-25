# Ecosystem Management

Proposal how to leverage wider community contributing instrumentations and other packages.

## Motivation

For OpenTelemetry to become a de-facto standard in observability there must exist a vast ecosystem of OpenTelemetry components,
including integrations with various libraries and frameworks in all languages supported by OpenTelemetry.
We cannot possibly expect that all these integrations will be provided by the core maintainers of OpenTelemetry.
We hope that wider community will integrate their projects with OpenTelemetry.
We have to encourage that by providing great documentation, examples and tooling to integration authors,
while still providing our end-users with some way to discover all available OpenTelemetry components together with some visibility into their quality.

## Explanation

The [OpenTelemetry Registry](https://opentelemetry.io/registry/) serves as a central catalogue of all known OpenTelemetry components,
both provided by core maintainers of the project and any third party.

In order for a component to be included into Registry its authors have to fill a [self-assessment form](#registry-self-assessment-form).

The registry should allow a clear visibility of component's ownership, quality and compatibility with other OpenTelemetry components.

A component can be removed from the Registry if any declaration from the self-assessment form is violated and not remedied
in a timely manner, provisionally three or four weeks.

## Internal details

We distinguish the following sources of OpenTelemetry components and integrations.

### Native or built-in instrumentations

Any library or framework can use the OpenTelemetry API to natively produce telemetry.
We encourage library authors to submit their library for inclusion into the OpenTelemetry Registry.

### Core components

OpenTelemetry SIGs may provide instrumentation for any libraries that are deemed important enough by the SIG’s maintainers.
By doing this the SIG maintainers commit to support this instrumentation (including future versions of the library),
provide updates/fixes, including security patches and guarantee that they comply with OpenTelemetry semantic conventions and best practices.

Depending on the SIG, these instances of core instrumentation may share the repository, infrastructure and maintainers with
the OpenTelemetry API/SDK implementation for this language or be separate.

All instances of core instrumentation must be included into the OpenTelemetry Registry following the usual process described above.

### Contrib components

Any language SIG may have one or more “contrib” repos containing components contributed by developers with an interest in specific parts of the instrumentation ecosystem.
These repositories may have a separate set of approvers/maintainers than the core API/SDK repo.
Contrib repositories are as important for the project success as core repository, but may not require the same level of expertise.
In fact, these repositories often calls for other set of skills and customer's understanding.
On contrib repository creation, new set of approvers and maintainers can be added as we do for any new repository, without time/contribution requirements.
Repository maintainers are also encouraged to promote contributors to approver/maintainer role in this repository
based on targeted contributions and expertise of the contrib repository rather than overall SIG scope.
It is important to keep the process fair and inclusive by following the formal guidance published [here](https://github.com/open-telemetry/community/blob/main/community-membership.md#maintainer).
A contrib repository may leverage the CODEOWNERS functionality of GitHub to assign maintainers to individual packages
even if this means granting write permissions to the whole repo.
The goal should be to distribute the load of reviewing PRs and accepting changes as much as possible, while keeping reliability and overall quality of components and fair governance.

All components in a contrib repository are expected to be included into the OpenTelemetry Registry following the usual process described above.

We should welcome all contributions and make the inclusion process (including following all our requirements) as easy as possible.
The goal is to encourage all contributors to include their components into a contrib repo as opposed to hosting them separately.
This way they can reuse existing infrastructure for testing, publishing, security scanning etc.
This will also greatly simplify responsibility transfer between different maintainers if their priorities change.
It also promotes the development and maintenance of a single instrumentation package for each instrumentation source,
so that work isn't spread amongst multiple parallel solutions.

Language SIGs are encouraged to provide a testing harness to verify that component adheres to OpenTelemetry semantic conventions
and recommendations for OpenTelemetry instrumentations design when OpenTelemetry starts publishing them.

A high volume of contrib contributions presents a burden for language maintainers. There are two suggestions for tackling this:

- Create an "experimental" folder within contrib. The contents of this folder are not reviewed or maintained by language repository maintainers, but
many of the other benefits of being within a contrib repository remain.
Experimental contributions should be marked as such in the Registry.
- Add more approvers and maintainers, perhaps some who exclusively focus on submissions to contrib.

### External components

If component authors, for whatever reason, want to host their contribution outside an OpenTelemetry contrib repository
they are free to do so (though we encourage all contributions to go into contrib or core language repositories).
Their submission for inclusion into OpenTelemetry Registry is still welcomed, subject to the same process described above.

### Distribution

Whenever OpenTelemetry components are published to any repository other than the OpenTelemetry Registry (such as npm registry or Maven Central),
only core and contrib components can be published under "opentelemetry" namespace.
Native and external components are to be published under their own namespace.

In case the OpenTelemetry SIG provides any kind of "all-in-one" instrumentation distribution (e.g. as Java and .NET do)
their should be an option to get a distribution with only core and contrib packages included.
The OpenTelemetry Registry should provide a way to easily obtain a list of these components.
The SIG may provide other distributions as well.
If possible, SIGs should provide a mechanism to include any external component during target application's build- or runtime.
This may mean a separate language-specific component API that all components are encouraged to implement.

## Trade-offs and mitigations

* How easy it is to get merge permission in contrib repo?
The harder it is, the larger is the maintenance burden on the core team.
The easier it is, the more uncertainty there is about the quality of contributions.
Can every language SIG decide this for themselves or should we decide together?

## Open questions

### Registry self-assessment form

The exact list should be developed separately, but at least the component's author should declare that

* It uses permissive OSS license approved by CNCF
* It does not have any known security vulnerabilities
* It produces telemetry which adheres to OpenTelemetry semantic conventions
* If the OpenTelemetry/SIG provides a testing harness to verify produced telemetry, that tests were used and passed
* Authors commit a reasonable effort into future maintenance of this component

### Component information in the Registry

The exact UI of component's page in the Registry is outside of this OTEP's scope, but some suggestions are:

* Short description of the component
* Link to the original repository of this component
* Clear indication of component's authors/maintainers and its OpenTelemetry status (native/core/contrib/external)
* License used
* Language and targeted library
* Links to a list of current issues and known security vulnerabilities
* Some way of component's quality as perceived by its users, e.g. rating or stars or thumbs up/down
* OpenTelemetry API/SDK and library versions that this component was tested against
* If OpenTelemetry verification harness is used by this component
* A filled self-assessment form
* Any quality indicators we may want to standardize on (e.g. test coverage)
* Dev stats (date of creation, date of last release, date of last commit)
