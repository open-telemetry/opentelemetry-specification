# (Open) Telemetry Without Manual Instrumentation

**Status:** `proposed`

_Cross-language requirements for automated approaches to extracting portable telemetry data with zero source code modification._

## Motivation

The purpose of OpenTelemetry is to make robust, portable telemetry a built-in feature of cloud-native software. For some software and some situations, that instrumentation can literally be part of the source code. In other situations, it’s not so simple: for example, we can’t necessarily edit or even recompile some of our software, the OpenTelemetry instrumentation only exists as a plugin, or instrumentation just never rises to the top of the priority list for a service-owner. Furthermore, there is occasionally a desire to disable instrumentation for a single plugin or module at runtime, again without requiring developers to make changes to source code.

One way to navigate situations like these is with a software layer that adds OpenTelemetry instrumentation to a service without modifying the source code for that service. (In the conventional APM world, these software layers are often called “agents”, though that term is overloaded and ambiguous so we try avoid it in this document.)

### Why “cross-language”?

Many people have correctly observed that “agent” design is highly language-dependent. This is certainly true, but there are still higher-level “product” objectives for OpenTelemetry that can guide the design choices we make across languages and help users form a consistent impression of what OpenTelemetry provides (and what it does not).

### Suggested reading

* This GitHub issue: [Propose an "Auto-Instrumentation SIG"](https://github.com/open-telemetry/community/pull/87)
* [Rough notes from the June 11, 2019 meeting](https://docs.google.com/document/d/1ix0WtzB5j-DRj1VQQxraoqeUuvgvfhA6Sd8mF5WLNeY/edit) following this ^^ issue
* The [rough draft for this RFC](https://docs.google.com/document/d/1sovSQIGdxXtsauxUNp4qUMEIJZzObdukzPT52eyPCHM/edit#), including the comments

## Proposed guidelines

### Requirements

Without further ado, here are a set of requirements for “official” OpenTelemetry efforts to accomplish zero-source-code-modification instrumentation (i.e., “OpenTelemetry agents”) in any given language:
* _Manual_ source code modifications "very strongly discouraged", with an exception for languages or environments that leave no credible alternatives. Any code changes must be trivial and `O(1)` per source file (rather than per-function, etc).
* Licensing must be permissive (e.g., ASL / BSD)
* Packaging must allow vendors to “wrap” or repackage the portable (OpenTelemetry) library into a single asset that’s delivered to customers
    * That is, vendors do not want to require users to comprehend both an OpenTelemetry package and a vendor-specific package
* Explicit, whitebox OpenTelemetry instrumentation must interoperate with the “automatic” / zero-source-code-modification / blackbox instrumentation.
    * If the blackbox instrumentation starts a Span, whitebox instrumentation must be able to discover it as the active Span (and vice versa)
    * Relatedly, there also must be a way to discover and avoid potential conflicts/overlap/redundancy between explicit whitebox instrumentation and blackbox instrumentation of the same libraries/packages
        * That is, if a developer has already added the “official” OpenTelemetry plugin for, say, gRPC, then when the blackbox instrumentation effort adds gRPC support, it should *not* “double-instrument” it and create a mess of extra spans/etc

* The code in the OpenTelemetry package must not take a hard dependency on any particular vendor/vendors (that sort of functionality should work via a plugin or registry mechanism)
    * Further, the code in the OpenTelemetry package must be isolated to avoid possible conflicts with the host application (e.g., shading in Java, etc)


### Nice-to-have properties

* Run-time integration (vs compile-time integration)
* Automated and modular testing of individual library/package plugins
    * Note that this also makes it easy to test against multiple different versions of any given library
* A fully pluggable architecture, where plugins can be registered at runtime without requiring changes to the central repo at github.com/open-telemetry
    * E.g., for ops teams that want to write a plugin for a proprietary piece of legacy software they are unable to recompile
* Augemntation of whitebox instrumentation by blackbox instrumentation (or, perhaps, vice versa). That is, not only can the trace context be shared by these different flavors of instrumentation, but even things like in-flight Span objects can be shared and co-modified (e.g., to use runtime interposition to grab local variables and attach them to a manually-instrumented span).


## Trade-offs and mitigations

Approaching a problem this language-specific at the cross-language altitude is intrinsically challenging since "different languages are different" – e.g., in Go there is no way to perform the kind of runtime interpositioning that's possible in Python, Ruby, or even Java.

There is also a school of thought that we should only be focusing on the bits and bytes that actually escape the running process and ignore how that's actually accomplished. This has a certain elegance to it, but it also runs afoul of the need to have manual instrumentation interoperate with the zero-touch instrumentation, especially when it comes to the (shared) distributed context itself.

## Prior art and alternatives

There are many proprietary APM language agents – no need to list them all here. The Datadog APM "language agents" are notable in that they were conceived and written post-OpenTracing and thus have been built to interoperate with same. There are a number of mature JVM language agents that are pure OSS (e.g., [Glowroot](https://glowroot.org/)).

