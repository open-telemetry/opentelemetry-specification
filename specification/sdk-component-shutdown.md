<!--- Hugo front matter used to generate the website version of this page:
linkTitle: SDK component shutdown
--->

# Shutdown of opt-in SDK components

**Status**: [Development](document-status.md)

The tracing, metrics, and logs SDKs already require shutdown of specified
components, such as processors, readers, and exporters. Other user-provided
components can also own resources. Examples among components supplied during
construction include a `Sampler`, a `MetricProducer`, and a stateful
configurator or `View` where the language represents one as an object. State
captured only by a function closure is not visible to this mechanism. Here, a
user-provided component is an application-supplied value that performs an SDK
extension role, rather than a passive configuration value.

A user-provided component MAY opt in to SDK-managed cleanup by exposing a
language-idiomatic shutdown operation in addition to its existing component
operations. An SDK can preserve this opt-in signal through a separate optional
interface such as `Shutdowner`, an optional method with a default implementation
on an existing interface, or a wrapper that forwards the operation. SDKs MUST
NOT make the operation a new requirement of existing component interfaces.
Exposing an operation matching the SDK's optional shutdown contract constitutes
opt-in, including for existing implementations. When an SDK-provided object
accepts a user-provided component during its programmatic construction, it MUST
invoke the component's optional shutdown operation as part of its own
`Shutdown`, without a separate registration call. Components without the
optional operation are unaffected. Existing required shutdown paths remain in
effect and MUST NOT be duplicated for the same ownership relationship.

The SDK-provided object that accepts the component owns this shutdown call. A
provider MUST wait for its existing required child `Shutdown` operations to
complete or abort before shutting down optional components it directly owns. An
SDK-provided composite component MUST apply the same rule to its directly held
delegates. A user-provided composite component is responsible for its own
delegates. A required child shutdown failure MUST NOT prevent attempts to shut
down optional components, subject to cancellation or deadline. Before invoking
an optional shutdown operation, the owner MUST stop admitting new operations
under its control that use the component. An SDK-provided composite MAY rely on
its owning SDK object to stop admitting such operations. Operations already in
flight can remain and may reach the component after its shutdown operation
returns. The component MUST tolerate such calls or coordinate their completion
before releasing resources.

If construction of the SDK-provided object accepting a component fails, the SDK
MUST NOT invoke that component's optional shutdown operation; the application
retains cleanup responsibility. An owner MUST attempt an optional shutdown
operation once per configured role or delegate slot that it owns, unless
shutdown has been canceled or its deadline has expired. The same instance
configured in multiple roles or slots can therefore receive multiple calls. An
owner MUST NOT start an operation after shutdown is canceled or its deadline
expires. A failure in one operation MUST NOT prevent attempts of others, subject
to cancellation and deadline. Where `Shutdown` provides an outcome, its first
call MUST NOT report success if an operation fails, times out, or remains
unattempted due to cancellation or deadline expiration. If the outcome can
report only one reason, a timeout SHOULD take precedence over failure when both
occur.

The owner MUST wait for an asynchronous optional shutdown operation to complete
before reporting successful `Shutdown`, subject to its deadline. An operation
that times out may continue running. The application remains responsible for
resources whose shutdown did not complete; fallback cleanup MUST coordinate with
any still-running operation or be idempotent.

Supplying an opt-in component transfers shutdown responsibility to each SDK
object that accepts it. An application sharing one component across separately
shut down SDK objects MUST ensure that shutdown by one owner leaves the resource
usable by the others, for example through reference-counted ownership. An
application cannot rely on the SDK to discover shared ownership. The same
instance may be accepted in multiple roles and receive multiple shutdown calls;
its optional operation SHOULD be idempotent in that case. This mechanism covers
components supplied during programmatic construction; it does not specify
declarative configuration, later configuration updates, or component
replacement.
