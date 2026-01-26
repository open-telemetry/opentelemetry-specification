# The OpenTelemetry approach to upgrading

Managing widely distributed software at scale requires careful design related to backwards compatibility, versioning, and upgrading. The OpenTelemetry approach is described below. If you are planning on using OpenTelemetry, it can be helpful to understand how we approach this problem.

## Component Overview

To facilitate smooth upgrading and long term support, OpenTelemetry clients are factored into several components. We use the following terms in the rest of this document.

Packages is a generic term for units of code which reference each other via some form of dependency management. Note that every programming language has a different approach to dependency management, and may use a different term, such as module or library, to represent this concept.

The API refers to the set of software packages that contain all of the interfaces and constants needed to write OpenTelemetry instrumentation. An implementation of the API may be registered during application startup. If no other implementation is registered, the API registers a no-op implementation by default.

The SDK refers to a framework which implements the API, provided by the OpenTelemetry project. While alternative API implementations may be written to handle special cases, we expect most users to install the SDK when running OpenTelemetry.

Plugin Interfaces refer to extension points provided by the SDK. These include interfaces for controlling sampling, exporting data, and various other lifecycle hooks. Note that these interfaces are not part of the API. They are part of the SDK.

Instrumentation refers to any code which calls the API. This includes the instrumentation provided by the OpenTelemetry project, third party instrumentation, plus application code and libraries which instrument themselves natively.

Plugins refer to any package which implements an SDK Plugin Interface. This includes the plugins provided by the OpenTelemetry project, plus third party plugins.

There is an important distinction between Plugins and Instrumentation. Plugins implement the Plugin Interfaces. Instrumentation calls the API. This difference is relevant to OpenTelemetry’s approach to upgrading.

## The OpenTelemetry upgrade path

Before we get into the design requirements, here’s how upgrading actually works. Note that all OpenTelemetry components (API, SDK, plugins, instrumentation) have separate version numbers.

### API changes

When new functionality is added to the OpenTelemetry API, a new minor version of the API is released. These API changes are always additive and backward compatible from the perspective of existing Instrumentation packages which import and call prior versions. Instrumentation written against all prior minor versions of the API continues to work, and may be composed together into the same application without creating a dependency conflict.

API implementations are expected to always target the latest version of the API. When a new version of the API is released, a version of the SDK which supports the API is released in tandem. New versions of the API are not expected to support older versions of the SDK.

### SDK changes

Bugs fixes, security patches, and performance improvements are released as patch versions of the SDK. Support for new versions of the API are released as minor versions. New Plugin Interfaces and configuration options are also released as minor versions.

Breaking changes to Plugin Interfaces are handled through deprecation. Instead of breaking a Plugin Interface, a new interface is created and the existing interface is marked as deprecated. Plugins which target the deprecated interface continue to work, and the SDK provides default implementations of any missing functionality. After one year, the deprecated Plugin Interface is removed as a major version release of the SDK.

## Design requirements and explanations

This approach to upgrading solves two critical design requirements, while minimizing the maintenance overhead associated with legacy code.

* Callers of the API are never broken.
* Users of the SDK can easily upgrade to the latest version.

Indefinite support for existing Instrumentation is a critical feature of OpenTelemetry. Millions of lines of code are expected to be written against the API. This includes shared libraries which ship with integrated OpenTelemetry instrumentation. These libraries must be able to compose together into applications without OpenTelemetry creating a dependency conflict. While some Instrumentation will be updated to the latest version of the API, such as that provided by the OpenTelemetry project, other Instrumentation will never be updated.

Consuming new Instrumentation may require users to upgrade to the latest version of the SDK. If it was not easy to perform this upgrade, the OpenTelemetry project would be forced to support older versions of the SDK, as well as older versions of the entire Instrumentation ecosystem.

This would be an enormous maintenance effort at best. But, as the OpenTelemetry project only controls a portion of that ecosystem, it is also unfeasible. OpenTelemetry cannot require that libraries with native instrumentation support multiple versions of the API. Ensuring that application owners and operators can upgrade to the latest version of the SDK resolves this issue.

The primary blocker to upgrading the SDK is out of date Plugins. If a new version of the SDK were to break existing Plugin Interfaces, no user would be able to upgrade their SDK until the Plugins they depend on have been upgraded. Users could be caught between instrumentation they depend on requiring a version of the API which is not compatible with the version of the SDK which supports their Plugins.

By following a deprecation pattern with Plugin Interfaces, we create a one year window in which the Plugin ecosystem can upgrade after the release of a new SDK. We believe this is sufficient time for any Plugin which is actively maintained to make an upgrade, and for defunct Plugins to be identified and replaced.

By ensuring that the SDK can be easily upgraded, we also provide a path for application owners and operators to rapidly consume critical bugfixes and security patches, without the need to backport these patches across a large number of prior SDK versions.
