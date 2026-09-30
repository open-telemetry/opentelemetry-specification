<!--- Hugo front matter used to generate the website version of this page:
linkTitle: SDK component shutdown
--->

# Shutdown of opt-in SDK components

**Status**: [Development](document-status.md)

Some user-provided SDK components can own resources without a required shutdown
operation. Examples include a `Sampler`, an `IdGenerator`, and a
`MetricProducer`. An SDK MAY support optional shutdown at an extension point
where it accepts such components during programmatic construction. A component
opts in with a language-idiomatic shutdown operation, for example through a
separate interface. Existing component interfaces do not gain a required
shutdown operation.

For each supported role, the SDK MUST call the optional operation as part of
`Shutdown` on the SDK object that accepted the component, unless shutdown has
been canceled or its deadline has expired. Supplying the component is
sufficient; no separate shutdown registration is needed. Existing required
shutdown of processors, readers, and exporters still applies.

The SDK SHOULD call optional shutdown after its required child shutdown
operations and SHOULD include any resulting failure in its `Shutdown` outcome.
SDK-provided composite components SHOULD forward shutdown to opted-in
delegates. Calls already in flight can still reach a component after its
shutdown operation returns. Such components can tolerate these calls or
coordinate their completion before releasing resources. An application sharing
a component among SDK objects is responsible for coordinating its lifetime
across their shutdown calls.

An SDK can also apply optional shutdown to an object-valued configurator or
`View` that exposes the operation. A function value can opt in only if the
SDK can observe that operation; state hidden solely in its closure cannot be
detected. This mechanism covers components supplied during programmatic
construction; it does not specify later configuration updates or declarative
configuration.
