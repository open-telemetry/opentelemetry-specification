# Versioning and stability for OpenTelemetry clients

**Status**: [Stable](document-status.md)

<details>
<summary>Table of Contents</summary>

<!-- toc -->

- [Design goals](#design-goals)
- [Signal lifecycle](#signal-lifecycle)
  * [Experimental](#experimental)
  * [Stable](#stable)
    + [API Stability](#api-stability)
      - [Extending Existing API Calls](#extending-existing-api-calls)
    + [SDK Stability](#sdk-stability)
    + [Contrib Stability](#contrib-stability)
    + [Semantic Conventions Stability](#semantic-conventions-stability)
    + [Telemetry Stability](#telemetry-stability)
  * [Deprecated](#deprecated)
  * [Removed](#removed)
  * [A note on replacing signals](#a-note-on-replacing-signals)
- [Version numbers](#version-numbers)
  * [Major version bump](#major-version-bump)
  * [Minor version bump](#minor-version-bump)
  * [Patch version bump](#patch-version-bump)
- [Long Term Support](#long-term-support)
  * [API support](#api-support)
  * [SDK Support](#sdk-support)
  * [Contrib Support](#contrib-support)
- [OpenTelemetry GA](#opentelemetry-ga)

<!-- tocstop -->

</details>

This document defines the stability guarantees offered by the OpenTelemetry clients, along with the rules and procedures for meeting those guarantees.

In this document, the terms "OpenTelemetry" and "language implementations" both specifically refer to the OpenTelemetry clients.
These terms do not refer to the specification or the Collector in this document.

Each language implementation MUST take these versioning and stability requirements, and produce a language-specific document which details how these requirements will be met.
This document SHALL be placed in the root of each repo and named `VERSIONING`.

## Design goals

Versioning and stability procedures are designed to meet the following goals.

**Ensure that application owners stay up to date with the latest release of the SDK.**
We want all users to stay up to date with the latest version of the OpenTelemetry SDK.
We do not want to create hard breaks in support, of any kind, which leave users stranded on older versions.
It MUST always be possible to upgrade to the latest minor version of the OpenTelemetry SDK, without creating compilation or runtime errors.

**Never create a dependency conflict between packages which rely on different versions of OpenTelemetry. Avoid breaking all stable public APIs.**
Backwards compatibility is a strict requirement.
Instrumentation APIs cannot create a version conflict, ever. Otherwise, the OpenTelemetry API cannot be embedded in widely shared libraries, such as web frameworks.
Code written against older versions of the API MUST work with all newer versions of the API.
Transitive dependencies of the API cannot create a version conflict. The OpenTelemetry API cannot depend on a particular package if there is any chance that any library or application may require a different, incompatible version of that package.
A library that imports the OpenTelemetry API should never become incompatible with other libraries due to a version conflict in one of OpenTelemetry's dependencies.
Theoretically, APIs can be deprecated and eventually removed, but this is a process measured in years and we have no plans to do so.

**Allow for multiple levels of package stability within the same release of an OpenTelemetry component.**
Provide maintainers a clear process for developing new, experimental [signals](glossary.md#signals) alongside stable signals.
Different packages within the same release may have different levels of stability.
This means that an implementation wishing to release stable tracing today MUST ensure that experimental metrics are factored out in such a way that breaking changes to metrics API do not destabilize the trace API packages.

## Signal lifecycle

The development of each signal follows a lifecycle: experimental, stable, deprecated, removed.

The infographic below shows an example of the lifecycle of an API component.

![API Lifecycle](../internal/img/api-lifecycle.png)

### Experimental

Signals start as **experimental**, which covers alpha, beta, and release candidate versions of the signal.
While signals are experimental, breaking changes and performance issues MAY occur.
Components SHOULD NOT be expected to be feature-complete.
In some cases, the experiment MAY be discarded and removed entirely.
Long-term dependencies SHOULD NOT be taken against experimental signals.

OpenTelemetry clients MUST be designed in a manner that allows experimental signals to be created without breaking the stability guarantees of existing signals.

OpenTelemetry clients MUST NOT be designed in a manner that breaks existing users when a signal transitions from experimental to stable. This would punish users of the release candidate, and hinder adoption.

Terms which denote stability, such as "experimental," MUST NOT be used as part of a directory or import name.
Package **version numbers** MAY include a suffix, such as -alpha, -beta, -rc, or -experimental, to differentiate stable and experimental packages.

### Stable

Once an experimental signal has gone through rigorous beta testing, it MAY transition to **stable**.
Long-term dependencies MAY now be taken against this signal.

All signal components MAY become stable together, or MAY transition to stability component-by-component. The API MUST become stable before the other components.

Once a signal component is marked as stable, the following rules MUST apply until the end of that signal’s existence.

#### API Stability

Backward-incompatible changes to API packages MUST NOT be made unless the major version number is incremented.
All existing API calls MUST continue to compile and function against all future minor versions of the same major version.

Languages which ship binary artifacts SHOULD offer [ABI compatibility](glossary.md#abi-compatibility) for API packages.

##### Extending Existing API Calls

An existing API call MAY be extended without incrementing the major version
number if the particular language allows to do it in a backward-compatible
manner.

To add a new parameter to an existing API call depending on the language several
approaches are possible:

- Add a new optional parameter to existing methods. This may not be the right
  approach for languages where ABI stability is part of our guarantees since it
  likely breaks the ABI.

- Add a method overload that allows passing a different set of parameters, that
  include the new parameter. This is likely the preferred approach for languages
  where method overloads are possible.

There may be other ways to extend existing APIs in non-breaking manner. Language
maintainers SHOULD choose the idiomatic way for their language.

#### SDK Stability

Public portions of SDK packages MUST remain backwards compatible.
There are two categories of public features: **plugin interfaces** and **constructors**.
Examples of plugins include the SpanProcessor, Exporter, and Sampler interfaces.
Examples of constructors include configuration objects, environment variables, and SDK builders.

Languages which ship binary artifacts SHOULD offer [ABI compatibility](glossary.md#abi-compatibility) for SDK packages.

#### Contrib Stability

Plugins, instrumentation, and other contrib packages SHOULD be kept up to date
and compatible with the latest versions of the API, SDK, and Semantic
Conventions. If a release of the API, SDK, or Semantic Conventions contains
changes which are relevant to a contrib package, that package SHOULD be updated
and released in a timely fashion. (See limitations on instrumentation stability
in [Telemetry Stability](telemetry-stability.md).) The goal is to ensure users can
update to the latest version of OpenTelemetry, and not be held back by the
plugins that they depend on.

Public portions of contrib packages (constructors, configuration, interfaces) SHOULD remain backwards compatible.

Languages which ship binary artifacts SHOULD offer [ABI compatibility](glossary.md#abi-compatibility) for contrib packages.

**Exception:** Contrib packages MAY break stability when a required downstream dependency breaks stability.
For example, a database integration may break stability if the required database client breaks stability.
However, it is strongly RECOMMENDED that older contrib packages remain stable.
A new, incompatible version of an integration SHOULD be released as a separate contrib package, rather than break the existing contrib package.

#### Semantic Conventions Stability

Changes to telemetry produced by OpenTelemetry instrumentation SHOULD avoid
breaking analysis tools, such as dashboards and alerts. To achieve this, while
allowing the evolution of telemetry and semantic conventions, OpenTelemetry
relies on the concept of
[Telemetry Schemas](schemas/overview.md).

Changes to semantic conventions in this specification are allowed, provided that
the changes can be described by schema files. The following changes can be
currently described and are allowed:

- Renaming of span, metric, log and resource attributes.
- Renaming of metrics.
- Renaming of span events.

All such changes MUST be described in the OpenTelemetry
[Schema File Format](schemas/file_format_v1.0.0.md) and published in this repository.
For details see [how OpenTelemetry Schemas are published](schemas/overview.md#opentelemetry-schema).

See the [Telemetry Stability](telemetry-stability.md) document for details on how
instrumentations can use schemas to change the instrumentation they produce.

In addition to the 3 types of changes described above there are certain types
that are always allowed. Such changes do not need to be described (and are not
described) by schema files. Here is the list of such changes:

- Adding new attributes to the existing semantic conventions for resources,
  spans, span events or log records. Note that adding attributes to existing metrics is
  considered to be a breaking change.
- Adding semantic conventions for new types of resources, spans, span events,
  metrics or log records.

Any other changes to semantic conventions are currently prohibited. Other types
of changes MAY be introduced in the future versions of this specification. This
is only allowed if OpenTelemetry introduces a new schema file format that is
capable of describing such changes.

#### Telemetry Stability

For stability of telemetry produced by instrumentation see the
[Telemetry Stability](telemetry-stability.md) document.

### Deprecated

Signals MAY eventually be replaced. When this happens, they are marked as deprecated.

Signals SHALL only be marked as deprecated when the replacement becomes stable.
Deprecated code MUST abide by the same support guarantees as stable code.

### Removed

Support is ended by the removal of a signal from the release.
The release MUST make a major version bump when this happens.

### A note on replacing signals

Note that we currently have no plans for creating a major version of OpenTelemetry past v1.0.

For clarity, it is still possible to create new, backwards incompatible versions of existing signals without actually moving to v2.0 and breaking support.

For example, imagine we develop a new, better tracing API - let's call it AwesomeTrace.
We will never mutate the current tracing API into AwesomeTrace.
Instead, AwesomeTrace would be added as an entirely new signal which coexists and interoperates with the current tracing signal.
This would make adding AwesomeTrace a minor version bump, *not* v2.0.
v2.0 would mark the end of support for current tracing, not the addition of AwesomeTrace.
And we don't want to ever end that support, if we can help it.

This is not actually a theoretical example.
OpenTelemetry already supports two tracing APIs: OpenTelemetry and OpenTracing.
We invented a new tracing API, but continue to support the old one.

## Version numbers

OpenTelemetry clients follow [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html), with the following clarifications.

OpenTelemetry clients have four components: API, SDK, Semantic Conventions, and Contrib.

For the purposes of versioning, all code within a component MUST treated as if it were part of a single package, and versioned with the same version number,
except for Contrib, which may be a collection of packages versioned separately.

* All stable API packages MUST version together, across all signals.
Stable signals MUST NOT have separate version numbers.
There is one version number that applies to all signals that are included in the API release that is labeled with that particular version number.
* SDK packages for all signals MUST version together, across all signals.
Signals MUST NOT have separate version numbers.
There is one version number that applies to all signals that are included in the SDK release that is labeled with that particular version number.
* Semantic Conventions are a single package with a single version number.
* Each contrib package MAY have it's own version number.
* The API, SDK, Semantic Conventions, and contrib components have independent version numbers.
For example, the latest version of `opentelemetry-python-api` MAY be at v1.2.3 while the latest version of `opentelemetry-python-sdk` is at v2.3.1.
* Different language implementations have independent version numbers.
For example, it is fine to have `opentelemetry-python-api` at v1.2.8 when `opentelemetry-java-api` is at v1.3.2.
* Language implementations have version numbers which are independent of the specification they implement.
For example, it is fine for v1.8.2 of `opentelemetry-python-api` to implement v1.1.1 of the specification.

**Exception:** in some languages, package managers may react poorly to experimental packages having a version higher than 0.X.
In these cases, experimental signals MAY version independently from stable signals, in order to retain a 0.X version number.
When a signal becomes stable, the version MUST be bumped to match the other stable signals in the release.

### Major version bump

Major version bumps MUST occur when there is a breaking change to a stable interface, the removal of a deprecated signal, or a drop in support for a language or runtime version.
Major version bumps SHOULD NOT occur for changes which do not result in a drop in support of some form.

### Minor version bump

Most changes to OpenTelemetry clients result in a minor version bump.

* New backward-compatible functionality added to any component.
* Breaking changes to internal SDK components.
* Breaking changes to experimental signals.
* New experimental signals are added.
* Experimental signals become stable.
* Stable signals are deprecated.

### Patch version bump

Patch versions make no changes which would require recompilation or potentially break application code.
The following are examples of patch fixes.

* Bug fixes which don't require minor version bump per rules above.
* Security fixes.
* Documentation.

Currently, the OpenTelemetry project does NOT have plans to backport bug and security fixes to prior minor versions of the SDK.
Security and bug fixes MAY only be applied to the latest minor version.
We are committed to making it feasible for end users to stay up to date with the latest version of the OpenTelemetry SDK.

## Long Term Support

![long term support](../internal/img/long-term-support.png)

### API support

Major versions of the API MUST be supported for a minimum of **three years** after the release of the next major API version.
API support is defined as follows.

* API stability, as defined above, MUST be maintained.

* A version of the SDK which supports the latest minor version of the last major version of the API will continue to be maintained during LTS.
Bug and security fixes MUST be backported. Additional feature development is NOT RECOMMENDED.

* Contrib packages available when the API is versioned MUST continue to be maintained for the duration of LTS.
Bug and security fixes will be backported.
Additional feature development is NOT RECOMMENDED.

### SDK Support

SDK stability, as defined above, will be maintained for a minimum of **one year** after the release of the next major SDK version.

### Contrib Support

Contrib stability, as defined above, will be maintained for a minimum of **one year** after the release of the next major version of a contrib package.

## OpenTelemetry GA

The term “OpenTelemetry GA” refers to the point at which OpenTracing and OpenCensus will be fully deprecated.
The **minimum requirements** for declaring GA are as followed.

* A stable version of both tracing and metrics MUST be released in at least four languages.
* CI/CD, performance, and integration tests MUST be implemented for these languages.
