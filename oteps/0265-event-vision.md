# Event Basics

## Motivation

The introduction of Events has been contentious, so we want to document and agree on a few basics.

### What are OpenTelemetry Events?

OpenTelemetry Events are a type of OpenTelemetry Log that requires an event name and follows a specific structure implied by that event name.

They are a core concept in OpenTelemetry Semantic Conventions.

### OTLP

Since OpenTelemetry Events are a type of OpenTelemetry Log, they share the same OTLP log data structure and pipeline.

### API

OpenTelemetry SHOULD provide a (user-facing) Logs API that includes the capability to emit OpenTelemetry Events.

### Interoperability with other logging libraries

OpenTelemetry SHOULD provide a way to send OpenTelemetry Logs from the OpenTelemetry Logs API to other logging libraries (e.g., Log4j).
This allows users to integrate OpenTelemetry Logs into an existing (non-OpenTelemetry) log stream.

OpenTelemetry SHOULD provide a way to bypass the OpenTelemetry Logs API entirely and emit OpenTelemetry Logs (including Events)
directly via existing language-specific logging libraries, if that library has the capability to do so.

OpenTelemetry will recommend that
[instrumentation libraries](../specification/glossary.md#instrumentation-library)
use the OpenTelemetry Logs API to emit OpenTelemetry Events rather than using other logging libraries to emit OpenTelemetry Events. This recommendation aims to provide users with a simple and consistent
onboarding experience that avoids mixing approaches.

OpenTelemetry will also recommend that application developers use the OpenTelemetry Logs API to emit OpenTelemetry Events instead of using another
logging library, as this helps prevent accidentally emitting logs that lack an event name or are unstructured.

Recommending the OpenTelemetry Logs API for emitting OpenTelemetry Events, rather than using other logging libraries, contributes to a clearer overall
OpenTelemetry API story. This ensures a unified approach with first-class user-facing APIs for traces, metrics, and events,
all suitable for direct use in native instrumentation.

### Relationship to Span Events

Events are intended to replace Span Events in the long term.
Span Events will be deprecated to signal that users should prefer Events.

See [OTEP 4430: Span Event API deprecation plan](4430-span-event-api-deprecation-plan.md)
for more details.

### SDK

This refers to the existing OpenTelemetry Logs SDK.

## Alternatives

Many alternatives were considered over the past 2+ years.

These alternatives primarily boil down to differences in naming (e.g. whether to even use the word Event)
and organization (e.g. whether Event API should be something separate from Logs API).

The state of this OTEP represents the option that we think will be the least confusing to the most number of users across the wide range of different language ecosystems that are supported.

## Open questions

* How to support routing logs from the Logs API to a language-specific logging library
  while simultaneously routing logs from the language-specific logging library to an OpenTelemetry Logging Exporter?
* How do log bodies interoperate with other logging libraries?
  OpenTelemetry Logs have two places to put structure (attributes and body), while often logging libraries only have one layer of structure,
  which makes it non-obvious how to do a two-way mapping between them in this case.
* How do event bodies interoperate with Span Events?
* Should the Logs API have an `Enabled` function based on severity level and event name?
* What kind of capabilities should the OpenTelemetry Logs API have now that it is user-facing?
  (Keeping in mind the bundle size constraints of browsers and possibly other client environments.)
* What kind of ergonomic improvements make sense now that the OpenTelemetry Logs API is user-facing?
  (Keeping in mind the bundle size constraints of browsers and possibly other client environments.)
* How do OpenTelemetry Events relate to raw metric events?
  (e.g. [opentelemetry-specification/617](https://github.com/open-telemetry/opentelemetry-specification/issues/617)).
* How do OpenTelemetry Events relate to raw span events?
  (e.g. a streaming SDK).
* Should event name be captured as an attribute or as a top-level field?
* How will Event / Span Event interoperability work in the presence of sampling (e.g. since Span Events are sampled along with Spans)?
