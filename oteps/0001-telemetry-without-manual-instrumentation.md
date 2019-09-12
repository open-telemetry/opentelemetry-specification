# (Open) Telemetry Without Manual Instrumentation

**Status:** `approved`

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
* From the standpoint of the actual telemetry being gathered, the same standards and expectations (about tagging, metadata, and so on) apply to "whitebox" instrumentation and automatic instrumentation
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

## Proposal

### What is our desired end state for OpenTelemetry end-users?

To reiterate much of the above:
* First and foremost, **portable OpenTelemetry instrumentation can be installed without manual source code modification**
* There’s one “clear winner” when it comes to portable, automatic instrumentation; just like with OpenTracing and OpenCensus, this is a situation where choice is not necessarily a good thing. End-users who wish to contribute instrumentation plugins should not have their enthusiasm and generosity diluted across competing projects.
* As much as such a thing is possible, consistency across languages
* Broad coverage / “plugin support”
* Broad vendor support for OpenTelemetry
* All other things being equal, get all of these ^^ benefits ASAP!

### What's the basic proposal?

Given the desired end state, the Datadog tracers seem like the closest-fit, permissively-licensed option out there today. We asked Datadog's leadership whether they would be interested in donating that code to OpenTelemetry, and they were receptive to the idea. (I.e., this would not be a "hard fork" that must be maintained in parallel forever)

### The overarching (technical) process, per-language

* Start with [the Datadog `dd-trace-foo` tracers](https://github.com/DataDog?utf8=✓&q=dd-trace&type=source&language=)
* For each language:
  * Fork the Datadog `datadog/dd-trace-foo` repo into a `open-telemetry/auto-instr-foo` OpenTelemetry repo (exact naming TBD)
  * In parallel:
    * The `dd-trace-foo` codebases already do a good job separating Datadog-specific functionality from general-purpose functionality. Where needed, make that boundary even more explicit through an API (or "SPI", really).
    * Create a new `dd-trace-foo` lib that wraps `auto-instr-foo` and includes the Datadog-specific pieces factored out above
    * Show that it’s also possible to bind to arbitrary OpenTelemetry-based tracers to the above API/SPI
  * Declare the forked `auto-instr-foo` repository ready for production beta use
  * For some (ideally brief) period:
    * When new plugins are added to Datadog's (original) repo, merge them over into the `auto-instr-foo` repo
    * Allow Datadog end-users to bind to either for some period of time (ultimately Datadog's decision on timeline here, and does not prevent other tracers from using `auto-instr-foo`)
    * Finally, when the combination of `auto-instr-foo` and a Datadog wrapper is functionally equivalent to the `dd-trace-foo` mainline, the latter can be safely replaced by the former.
      * Note that, by design, this is not expected to affect Datadog end-users
  * Moved repo is GA’d: all new plugins (and improvements to the auto-instrumentation core) happen in the `auto-instr-foo` repo

There are some languages that will have OpenTelemetry support before they have Datadog `dd-trace-foo` support. In those situations, we will fall back to the requirements in this OTEP and leave the technical determinations up to the language SIG and the OpenTelemetry TC.

### Governance of the auto-instrumentation libraries

The maintainers for each language `foo` will retain their Approver/Maintainer status and privileges for the `auto-instr-foo` repositories.

### Mini-FAQ about this proposal

**Will this be the only auto-instrumentation story for OpenTelemetry?** It need not be. The auto-instrumentation libraries described above will have no privileged access to OpenTelemetry APIs, and as such they have no exclusive advantage over any other auto-instrumentation libraries.

**What about auto-instrumenting _Project X_? Why aren't we using that instead??** First of all, there's nothing preventing any of us from taking great ideas from _Project X_ and incorporating them into these auto-instrumentation libraries. We propose that we start with the Datadog codebases and iterate from there as need be. If there are improvements to be made in any given language, they will be welcomed by all.

## Prior art and alternatives

There are many proprietary APM language agents – no need to survey them all here. There is a much smaller list of "APM agents" (or other auto-instrumentation efforts) that are already permissively-licensed OSS. For instance, when we met to discuss options for JVM (longer notes [here](https://docs.google.com/document/d/1ix0WtzB5j-DRj1VQQxraoqeUuvgvfhA6Sd8mF5WLNeY/edit#heading=h.kjctiyv4rxup)), we came away with the following list:
* [Honeycomb's Java beeline](https://github.com/honeycombio/beeline-java)
* [Datadog's Java tracer](https://github.com/datadog/dd-trace-java)
* [Glowroot](https://glowroot.org/)
* [SpecialAgent](https://github.com/opentracing-contrib/java-specialagent)

The most obvious "alternative approach" would be to choose "starting points" independently in each language. This has several problems:
* Higher likelihood of "hard forks": we want to avoid an end state where two projects (the OpenTelemetry version, and the original version) evolve – and diverge – independently
* Higher likelihood of "concept divergence" across languages: while each language presents unique requirements and challenges, the Datadog auto-instrumentation libraries were written by a single organization with some common concepts and architectural requirements (they were also written to be OpenTracing-compatible, which greatly increases our odds of success given the similarities to OpenTelemetry)
* Datadog would also like a uniform strategy here, and this donation requires their consent (unless we want to do a hard fork, which is suboptimal for everyone). So starting with the Datadog libraries in "all but one" (or "all but two", etc) languages makes this less palatable for them
