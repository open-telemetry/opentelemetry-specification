# Specification Principles

This document defines common principles that will help designers create and extend
the OpenTelemetry specification to adapt to new use cases and fix issues.

## OpenTelemetry Mission and Values

It should be taken in context of the [overal values of OpenTelemetry](https://opentelemetry.io/community/mission/), which lays out the following core values:

- [Telemetry should be easy](https://opentelemetry.io/community/mission/#telemetry-should-be-easy)
- [Telemetry should be universal](https://opentelemetry.io/community/mission/#telemetry-should-be-universal)
- [Telemetry should be vendor-neutral](https://opentelemetry.io/community/mission/#telemetry-should-be-vendor-neutral)
- [Telemetry should be loosely-coupled](https://opentelemetry.io/community/mission/#telemetry-should-be-loosely-coupled)
- [Telemetry should be built-in](https://opentelemetry.io/community/mission/#telemetry-should-be-built-in)

Additionally, it lays out the following core Engineering Values:

- [Compatibility](https://opentelemetry.io/community/mission/#we-value-_compatibility_)
- [Stability](https://opentelemetry.io/community/mission/#we-value-_stability_)
- [Resilience](https://opentelemetry.io/community/mission/#we-value-_resilience_)
- [Performance](https://opentelemetry.io/community/mission/#we-value-_performance_)
  - See [Specification Performance Principles](performance.md) for more details.

In addition to these core values, there are a set of things we've learned about
Specification work and drive how we write our Specification.

## Specification Principles

Here are the key principles of the OpenTelemetry Specification:

- [Be User Driven](#be-user-driven)
- [Be General](#be-general)
- [Be Stable](#be-stable)
- [Be Consistent](#be-consistent)
- [Be Simple](#be-stable)

Note that at times some of these principles are at odds with each other. For
example, keeping things stable may put constraints on possible simplicity. These
principles are a rubric to guide design, and form a specturm through which we
evaluate additions or changes to the Specification.

Let's look at each in more detail.

### Be User Driven

The specification is useless without the ecosystem it enables. Changes should
focus on real world use cases, and real user needs. Additionally, changes should
be implementable across the entire OpenTelemetry ecosystem.

This means proposals should think "end to end" not "add this one little thing".

Projects and proposals should provide prototypes or implementations
prior to solidification within the Specification.

We have a few simple rules of thumb regarding prototypes:

- API / SDK Changes should be prototyped in three languages.  The goal is
  coverage of possible API designs, not any specific language:
  - One language should cover typed Object-Oriented ecosystems (Java, C#, etc.)
  - One language should cover dynamically typed ecosystems (Python, Javascript)
  - One language should cover structural ecosystems (e.g. Go, Rust)
- Protocol changes should be prototyped both on the client and the server.
- Prototypes can be unmerged Pull Requests, existing projects, etc. but must
  demonstrate the feature with confidence that the Specification of it will
  be successful.

### Be General

The specification needs to be implemented across a wide range of languages,
frameworks, ecosystems and communities. OpenTelemetry components should be
allowed to provide idiomatic experiences to their users.

THe Specification should focus on *what* not *how*. When describing how, use
non-normative language or supplementary guidelines, like this document.

### Be Stable

Don't. Break. Users.

Yes, this is a repeat of the overall OpenTelemetry mission of
[Stability](https://opentelemetry.io/community/mission/#we-value-_stability_).
That's how important stability is.

To achieve OpenTelemetry's mission of "Telemetry should be built-in", we need to
create a set of components that are safe for users to depend on. Instability
breaks trust, and hurts the mission of being a built-in solution.

When things do change, the specification (and implementation) should do the
heavy lifting to ensure seamless, smooth experience for the OpenTelemetry
ecosystem.

### Be Consistent

Don't make users learn new concepts and behaviors for each feature they interact
with in OpenTelemetry.  This has three sub-principles:

- Favor fewer broadly applicable features over many narrowly defined ones.
- Prefer similar concepts and behaviors between signals.
- Reuse naming conventions between signals, components, where possible.

### Be Simple

Simple is better than complicated. Abstractions should pay for themselves.
OpenTelemetry has a large scope and many components. Solving a complex problem
with simple design and solution leads to a much lower maintenance burden and
easier evolution in the future.

Additionally, a Specification is read and interpreted by many individuals.
Complex language, nuanced wording and unclear descriptions lead to confusion and
often times poor user experience as sections are not interpreted as desired.
