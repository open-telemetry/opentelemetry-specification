<!--- Hugo front matter used to generate the website version of this page:
linkTitle: SDK component shutdown
--->

# Shutdown of user-provided SDK components

**Status**: [Development](document-status.md)

The tracing, metrics, and logs SDKs already require providers to shut down
specified child components, such as processors, readers, and exporters. Other
user-provided components can also own resources. Examples include a custom
`Sampler`, a `MetricProducer`, state captured by a `TracerConfigurator`,
`MeterConfigurator`, or `LoggerConfigurator`, and custom state used when
configuring a metrics `View`. A `View` itself is configuration; an action for
View-related state only closes resources tracked by the application.

Each SDK signal provider MUST provide a programmatic way to register one or
more shutdown actions during provider construction. A shutdown action releases
resources associated with a user-provided component. Registration MAY use a
callback, an explicitly registered lifecycle object, or another
language-idiomatic form. It MUST NOT require adding a method to an existing
component interface. It MUST preserve existing provider construction calls and
plugin implementations, following the [SDK compatibility
rules](versioning-and-stability.md#extending-apisdk-abstractions). Supplying a
component to the SDK does not, by itself, register an action for it. Existing
specified shutdown paths remain in effect.

Registration takes effect only after provider construction succeeds. If
construction fails, the SDK MUST NOT invoke the registered actions; the
application remains responsible for its user-provided resources.

When a provider's `Shutdown` is called, the provider MUST invoke its existing
required child `Shutdown` operations. It MUST NOT start registered actions
until those operations have completed or aborted. An asynchronous provider
`Shutdown` can chain the actions after child operations finish. The provider
MUST attempt each registered action once unless its shutdown deadline has
expired. It MUST NOT start an action more than once per registration or after
the deadline, if one exists. A failure in one action MUST NOT prevent attempts
of other actions, subject to the shutdown deadline.

The provider MUST wait for an asynchronous action to complete before reporting
a successful `Shutdown`, subject to the same timeout. Where `Shutdown`
provides an outcome, it MUST NOT report success if an action fails, times out,
or remains unattempted when the deadline expires. If the outcome distinguishes
timeout from failure, a timeout SHOULD take precedence when both occur. The SDK
cannot necessarily stop a user action that continues running after the timeout.
The application remains responsible for resources whose registered actions did
not complete during `Shutdown`. Fallback cleanup MUST be safe if an action is
still running, through coordination or idempotence.

An application registering an action MUST ensure it is safe to invoke while
SDK operations using its resources remain in flight, or coordinate with those
operations before releasing the resources. For example, a `MetricProducer`
action may need to coordinate with an in-flight `Produce` call after a
`MetricReader` shutdown fails or times out. A resource shared across providers
MUST remain alive until all providers using it have stopped. An application can
register cleanup with an owner that shuts down after all other users, or
coordinate last-user cleanup across providers. If an existing specified
shutdown path already closes a component, registering an additional action for
it can close the component twice.

The order among registered actions is unspecified. An application requiring
ordered cleanup can register one action that coordinates its components.
This mechanism specifies registration during programmatic provider
construction. It does not specify later registration or registration through
declarative configuration.
