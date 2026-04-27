# The OpenTelemetry approach to upgrading

Managing widely distributed software at scale requires careful design related to
backwards compatibility, versioning, and upgrading. The OpenTelemetry approach is
described below. If you are planning on using OpenTelemetry, it can be helpful to
understand how we approach this problem.

## Component Overview

To facilitate smooth upgrading and long term support, OpenTelemetry clients are
factored into several components. We use the following terms in the rest of this
document.

**Packages** is a generic term for units of code which reference each other via
some form of dependency management. Note that every programming language has a
different approach to dependency management, and may use a different term, such
as module or library, to represent this concept.

**The API** refers to the set of software packages that contain all of the interfaces
and constants needed to write OpenTelemetry instrumentation. An implementation of
the API may be registered during application startup. If no other implementation
is registered, the API registers a no-op implementation by default.

**The SDK** refers to a framework which implements the API, provided by the OpenTelemetry
project. While alternative API implementations may be written to handle special
cases, we expect most users to install the SDK when running OpenTelemetry.

**Plugin Interfaces** refer to extension points provided by the SDK. These include
interfaces for controlling sampling, exporting data, and various other lifecycle
hooks. Note that these interfaces are not part of the API. They are part of the SDK.

**Instrumentation** refers to any code which calls the API. This includes the instrumentation
provided by the OpenTelemetry project, third party instrumentation, plus application
code and libraries which instrument themselves natively.

**Plugins** refer to any package which implements an SDK Plugin Interface. This
includes the plugins provided by the OpenTelemetry project, plus third party plugins.

There is an important distinction between Plugins and Instrumentation. Plugins implement
the Plugin Interfaces. Instrumentation calls the API. This difference is relevant
to OpenTelemetry’s approach to upgrading.

## Dependency Management

It is very important that OpenTelemetry users and implementors stay up to date with
the latest version of the OpenTelemetry API. OpenTelemetry follows strict rules in
regards to backwards compatibility. It is always safe to upgrade to the latest minor
version of an OpenTelemetry package.

### Application Developers

Developers who plan to install the OpenTelemetry SDK in their application are advised
to accept all minor version upgrades. This will ensure that applications
will always be built with the latest optimizations and security patches.

Likewise, application developers are encouraged to depend upon all future versions
of the current major version of the OpenTelemetry API. This will ensure that version
conflicts will not occur when instrumentation is upgraded to make use of new features
in future minor versions.

### Library Maintainers

Developers who maintain OSS libraries are encouraged to use the OpenTelemetry API
to add instrumentation directly into their library code. We refer to this approach
as "native instrumentation."

When adding the OpenTelemetry API as a dependency to your library, it is very important
to depend upon to ***all future versions*** of the current major version.

Depending on a specific minor version ***can lead to version conflicts*** with other
libraries that make use of API features added in later minor versions. Minor version
bumps of the API will never cause a compatibility issue with existing instrumentation.
It is completely safe to depend on future versions of the API.

### SDK Implementors

Maintainers of the official OpenTelemetry SDKs as well as maintainers of alternative
SDKs MUST keep their implementations up to date and compatible with the latest version
of the OpenTelemetry API.

When new minor versions of the OpenTelemetry API are released, they will contain
new features. This includes new interfaces, as well as new methods on current interfaces.
SDK maintainers are expected to release new versions which implement these features
in a timely manner.

If you do not believe you will be able to continue to maintain an implementation
in this manner, we strongly recommend that you do not implement an alternative SDK.
It is inevitable that OpenTelemetry will release new features, and that application
developers and library maintainers will make use of these features.

## The OpenTelemetry upgrade path

Before we get into the design requirements, here’s how upgrading actually works.
Note that all OpenTelemetry components (API, SDK, Plugins, Instrumentation) have
separate version numbers.

### API changes

When new functionality is added to the OpenTelemetry API, a new minor version of
the API is released. These API changes are always additive and backward compatible
from the perspective of existing Instrumentation packages which import and call
prior versions. Instrumentation written against all prior minor versions of the
API continues to work, and may be composed together into the same application without
creating a dependency conflict.

API implementations are expected to always target the latest version of the API.
When a new version of the API is released, a version of the SDK which supports the
API is released in tandem. Old versions of the SDK are not expected to support newer
versions of the API.

### SDK changes

Bugs fixes, security patches, and performance improvements are released as patch
versions of the SDK. Support for new versions of the API are released as minor versions.
New Plugin Interfaces are released as a minor version bump to the SDK.

Breaking changes to Plugin Interfaces are handled through deprecation. Instead of
breaking a Plugin Interface, a new interface is created and the existing interface
is marked as deprecated. Plugins which target the deprecated interface continue
to work, and the SDK provides default implementations of any missing functionality.
After one year, the deprecated Plugin Interface may be removed in a major version
release of the SDK.

## Design requirements and explanations

This approach to upgrading solves two critical design requirements, while minimizing
the maintenance overhead associated with legacy code.

* Callers of the API are never broken.
* Users of the SDK can easily upgrade to the latest version.

Indefinite support for existing Instrumentation is a critical feature of OpenTelemetry.
Millions of lines of code are expected to be written against the API. This includes
shared libraries which ship with integrated OpenTelemetry instrumentation. These
libraries must be able to compose together into applications without OpenTelemetry
creating a dependency conflict. While some Instrumentation will be updated to the
latest version of the API, such as that provided by the OpenTelemetry project, other
Instrumentation will never be updated.

Consuming new Instrumentation may require users to upgrade to the latest version
of the SDK. If it was not easy to perform this upgrade, the OpenTelemetry project
would be forced to support older versions of the SDK, as well as older versions
of the entire Instrumentation ecosystem.

This would be an enormous maintenance effort at best. But, as the OpenTelemetry
project only controls a portion of that ecosystem, it is also unfeasible. OpenTelemetry
cannot require that libraries with native instrumentation support multiple versions
of the API. Ensuring that application owners and operators can upgrade to the latest
version of the SDK resolves this issue.

The primary blocker to upgrading the SDK is out of date Plugins. If a new version
of the SDK were to break existing Plugin Interfaces, no user would be able to upgrade
their SDK until the Plugins they depend on have been upgraded. Users could be caught
between instrumentation they depend on requiring a version of the API which is not
compatible with the version of the SDK which supports their Plugins.

By following a deprecation pattern with Plugin Interfaces, we create a one year
window in which the Plugin ecosystem can upgrade after the release of a new SDK.
We believe this is sufficient time for any Plugin which is actively maintained
to make an upgrade, and for defunct Plugins to be identified and replaced.

By ensuring that the SDK can be easily upgraded, we also provide a path for application
owners and operators to rapidly consume critical bug fixes and security patches,
without the need to backport these patches across a large number of prior SDK versions.
