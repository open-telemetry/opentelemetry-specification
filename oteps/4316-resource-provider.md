# Entity Provider

Define a mechanism for updating the entities and resources associated with an application.

## Motivation

Resources were originally defined as immutable. For the common cases related to
server-side application development, because the lifespan for most resources associated
with server-side applications either match or outlive the lifespan of the application.

However, it turns out that not all swans are white, and some resources utilized
by applications change while the application is still running. This is especially
true in client-side applications running in the browser and on mobile devices.

Examples of resources whose availability may change include networking (wifi, cellular, none),
application state (foreground, background, sleeping), and session management (sessions
starting and ending without the application being shut down or the browser being
refreshed).

Tracking these resource changes are critical. Without them, it would be impossible
to segment the telemetry correctly. The lifespan of a session is a far more important
segmentation than the lifespan of an application instance, as the application lifespan
is often somewhat arbitrary. The performance of an application when it is foregrounded
cannot be understood when the foregrounded telemetry is mixed with backgrounded
telemetry. Failure modes may exist when network availability drops due to a switch
in networking – how an application performs when it has access to wifi vs when it
does not is a critical distinction.

Additionally, the notion of "Resource Detectors", while specified, is mostly
left to SDKs to figure out the details and remains a bit of a wild west for
non-SDK implementors. Most SDKs provide extension mechanisms for resource
detection, and these extensions look awkwardly like other insturmentation, but
without the benefit of a clear API and stability guarantees.

Even within Semantic conventions, it has been problematic defining conventions
for resource and sorting out code generation capabilities for providing these
attributes. Going forward, we'd like to provide a clear, stable mechanism for
instrumentation to provide resource attributes, with clear a "initialization"
phase to continue to ensure consistent, reliable observability with existing
Resource use cases.

## Explanation

Changes to resources and entities are managed via an EntityProvider. When the resources
represented by an entity change, the telemetry system records these changes by updating
the entity managed by the EntityProvider. These changes are then propagated to the
rest of the telemetry system via EntityListeners that have been registered with the
EntityProvider.

The loose coupling provided by a EntityProvider allows each subsystem to focus
on their various responsibilities without having to be directly aware of each other.
For a highly extensible cross-cutting concern such as OpenTelemetry, this loose
coupling is a valuable feature.

Additionally, an explicit initialization phase is added for SDK components,
where EntityProvider while provide a clear signal when initialization across
Resource detection has completed prior to reporting signals.

## High Level Details

This OTEP proposes two main changes to Resource within OpenTelemetry:

- The creation of an API which can be used to report entity changes where
  the lifetime of the entity does not match the lifetime of the SDK.
- An explicit initialization phase to the SDK, which allows for coordination
  between resource detection and signal providers.

## API Details

A new `EntityProvider` API is added, which allows reporting resource Entity
values.

The API provides three primary user cases:

- Instrumentation can provide entity status in a one-time fashion, which is
  used to identify the resource at startup of the SDK.
- Instrumentation can provide an entity in a scoped manner (add, then delete)
  when it can attach directly to the Entities lifecycle. For example, reporting
  [Activity](https://developer.android.com/guide/components/activities/activity-lifecycle)
  status in Android.
- Instrumentation can watch for entity changes and replace or update the status
  of the entity in the SDK. For example, updating session / page status when
  a page comes back from inactive.


### EntityProvider

The `EntityProvider` API MUST provide the following operations:

* `Add or Update Entity`
* `Add or Replace Entity`
* `Delete Entity`

#### Add or Update Entity

`Add or Update Entity` appends a new entity on to the end of the list of
entities.  If the Entity already exists, then the description of the entity
is updated.

Add or Update Entity MUST accept the following parameters:

* `type`: the type of the Entity being created.
* `ID`: the set of attributes which identify the entity.
* `description`: the set of attributes which describe the entity.
* `schema_url` (optional): The Schema URL that should be recorded for entity.

If the incoming Entity's `type` is not found in the current list of entities,
then the new Entity is added to the list.

If the incoming Entity conflicts with an existing entity, it is ignored.

Otherwise, the description of the Entity is updated with the incoming
description.

#### Add or Replace Entity

`Add or Replace Entity` adds replaces the resource attributes associated with an entity.

Add or Replace Entity MUST accept the following parameters:

* `type`: the type of the Entity being created.
* `ID`: the set of attributes which identify the entity.
* `description`: the set of attributes which describe the entity.
* `schema_url` (optional): The Schema URL that should be recorded for entity.

This is equivalent to an (optional) "delete" then "addOrUpdate" for an entity.

#### Delete Entity

`Delete Entity` removes the resource attributes associated with an entity.

Delete Entity MUST accept the following parameters:

* `type`: the type of the Entity being removed.

## SDK details

Like the other Providers used in OpenTelemetry, the EntityProvider MUST allow
for alternative implementations. This means that the EntityProvider API and
the EntityProvider implementation we provide MUST be loosely coupled, following
the same API/SDK pattern used everywhere in OpenTelemetry.

### EntityListener

An EntityListener MUST provide the following operations:

- `On ResourceInitialize`
- `On EntityState`
- `On EntityDelete`

#### On ResourceInitialize

`On ResourceInitialize` MUST accept the following parameters:

* `Resource`: represents the entire set of resources after initalize.

This operation MUST only be called once per EntityProvider.

#### On EntityState

`On EntityState` MUST accept the following parameters:

* `EntityState`: represents the entity that has changed.
* `Resource`: represents the entire set of resources after the entity changes
  have been applied.

#### On EntityDelete

`On EntityDelete` MUST accept the following parameters:

* `EntityDelete`: represents the entity that has been deleted.
* `Resource`: represents the entire set of resources after the entity
  has been deleted.

### EntityProvider

In addition to providing the `EntityProvider` API, an `EntityProvider` MUST
provide the following operations in the SDK:

* `On Change`
* (optional) `GetResource`

For multithreaded systems, all calls to `AddorUpdateEntity`, `UpdateEntity` and
`DeleteEntity` SHOULD avoid inconsistent reads and writes using appropriate
concurrency mechanisms by treating each method as an atomic operation.

The resource reference held by the EntityProvider SHOULD be updated atomically,
so that calls to `GetResource` do not require a lock.

Calls to EntityListeners SHOULD be serialized, to avoid thread safety issues and
ensure that callbacks are processed in the right order.

EntityProvider has two states:

- *Resource detection*: The provider is initializing, and waiting for
   ResourceDetectors to complete. No events will be fired.
- *Initialized*: A complete resource is available and operations will fire
  listener events.

#### EntityProvider creation

Creation of a EntityProvider MUST accept the following parameters:

* `detectors`: a list of ResourceDetectors.
* (optional) `initialization_timeout`: A timeout for when to abandon slow
  ResourceDetectors and consider a resource initialized.

EntityProvider MUST allow initial resource detection during its creation. This
initialization SHOULD not block other SDK providers from initializing (e.g.
MeterProvider, TracerProvider).

EntityProvider SHOULD provide the `EntityProvider` API to `ResourceDetector`s
during resource detection phase.

An EntityProvider MAY allow customizable concurrency behavior, e.g. using a
separate thread for EntityListener events.

Internally, the entities discovered via resource detection MUST be merged in
the order provided to create the initial resource.

During resource detection, EntityProvider MUST NOT fire any EntityListener
events.

Upon completion of the resource detection phase, EntityProvider MUST fire
an `On ResourceInitialize` event to all EntityListeners.

Any calls to `GetResource` operation, if provided, SHOULD block until
resource detection is completed.

Upon failure for resource detection to complete within a timeout, a resource
SHOULD be constructed with available completed detection, `GetResource`
operations MUST be unblocked and `On ResourceInitialize` event MUST be fired
to all EntityListeners.

#### Add or Update Entity

The `Add or Update Entity` operation MUST match the API definition.

The behavior MUST match the following:

  - If the incoming Entity's `type` is not found in the current list of entities,
then the new Entity is added to the list.
  - After an entity is created, it MUST be appended to the list of current entities.
A new resource object MUST be generated by merging the list of entities together
in order.
  - If the incoming Entity's `type` parameter matches an existing Entity in
the current list AND the `ID` attributes for these entities are different, then
the SDK MUST ignore the new entity.
  - If the incoming Entity's `type` parameter matches an existing Entity in the
current list AND the `ID` attributes for these entities are the same but
the `schema_url` is different, then the SDK MUST ignore the new entity.
  - If the incoming Entity's `type` parameter matches an existing Entity in the
current list AND the `ID` attributes for these entities are the same AND the
`schema_url` is the same, then the SDK MUST add any new attributes found in the
`description` to the existing entity. Any new `description` attributes with the
same keys as existing `description` attributes SHOULD replace previous values.

`Add or Update Entity` MUST trigger the `On EntityState` operation for all
registered `EntityListeners`.

#### Add or Replace Entity

The `Add or Replace Entity` operation MUST match the API definition.

The behavior MUST match the following:

- If an existing Entity with the same `type` already exists, then
  `Add or Replace Entity` MUST not trigger an `On EntityDelete` operation.
  Instead, a single `On EntityUpdate` event will be sent with fully updated
  resource, and the new entity.
- A new entity should be created and added to the list of entities. After the
  entity is created, it MUST be appended to the list of current entities. A new
  resource object MUST be generated by merging the list of entities together
  in order.

`Replace Entity` MUST trigger the `On EntityState` operation for all
registered `EntityListener`s.

NOTE: `EntityListener`s SHOULD receive an `On EntityDelete` operation when
a previous entity was removed before receiving an `On EntityUpdate` for the
new entity.

#### Delete Entity

The `Delete Entity` operation MUST accept the parameters defined in the API.

After an entity is deleted, a new resource object MUST be generated by merging
the list of entities together in order.

`Delete Entity` MUST trigger the `On EntityState` operation for all
registered `EntityListeners`.

#### Get Resource

`Get Resource` MUST return a reference to the current resource held by the
EntityProvider.

This operation MAY block when EntityProvider is in a resource detection state,
but MUST NOT block indefinitely.

#### On Change

`On Change` registers an `EntityListener` to be called every time an entity is updated
or deleted.

If the `EntityProvider` is already initialized, then it MUST call
`On ResourceInitialize` immediately with the current resource held by the
EntityProvider.

### SDK Changes

All other signal providers (TracerProvider, MeterProvider, LoggerProvider, etc)
MUST be updated to use EntityProvider to obtain `Resource`. This SHOULD be done
through either using `EntityListener` interface.  This MAY be done via a
`Get Resource` operation, although this limits how the SDK can handle resource
changes.

How SDKs handle resource changes is listed under [open questions](#open-questions).

### SDK Helpers

SDKs which do not provder a `Get Resource` operation MAY provide a
`LatestResource` component which acts as an `EntityListener` and provides a
mechanism to remember and retrieve the latest resource.

## Trade-offs and mitigations

This change should be fully backwards compatible, with one potential exception:
fingerprinting. It is possible that an analysis tool which accepts OTLP may identify
individual services by creating an identifier by hashing all of the resource attributes.

In practice, the only implementation we have discovered that does this is the OpenTelemetry
Go SDK. But the Go SDK is not a backend; all analysis tools have a specific concept
of identity that is fulfilled by a specific subject of resource attributes.

Since we control the Go SDK, we can develop a path forward specific to that particular
library. That path should be identified before this OTEP is accepted.

Beyond fingerprinting, there are no destabilizing changes because the resources
that we have already declared "immutable" match the lifespan of the application
and have no reason to be updated. Developers are not going to start messing with
the `service.instance.id` resource arbitrarily just because they can, and resource
detectors solve the problem of accidentally starting the application while async
resources are still being fetched.

## Prior art and alternatives

An alternative to updating resources would be to create span, metrics, and log
processors which attach these resource attributes to every instance of every
span and log.

There are two problems to this approach. One is that the duplication of attributes
is very inefficient. This is a problem on clients, which have limited network
bandwidth and processing power. This problem is compounded by a lack of support
for gzip and other compression algorithms on the browser.

Second, and perhaps more important, is that this approach does not match our data
model. These application states are global; they are not specific to any particular
transaction or event. Span attributes should record information specific to that
particular operation, log record attributes should record information specific to
that particular event. The correct place in our data model model for attributes
that identify the application, describe the environment the application is running
in, and describe the resources available to that application should be modelled
as resource attributes.

## Open questions

### How should spans be batched when they bridge a resource change?

The primary open question – which must be resolved before this OTEP is accepted –
is how to handle spans that bridge a change in resources.

For example, a long running background operation may span more than one session.
Networking may change from wifi to a cellular connection at any time, a user might
log in at any time, the application might be backgrounded at any time.

Simply put, how should the SDK handle spans that have already started when a resource
changes? What about the logs that are associated with that span? EntityState can be
used to record the exact moment when these values change. But resources need to act
as search indexes and metric dimensions. For those situations, we only get to pick
one value.

The simplest implementation is for the BatchProcessor to listen for resource changes,
and to flush the current batch whenever a change occurs. The old batch gets the old
resource, the new batch gets the new resource. This would be easy to implement,
but is it actually what we want? Either as part of this OTEP or as a quick follow
up, we need to define the expected behavior for the BatchProcessor when it is listening
for resource changes.

### What if a resource thrashes?

Because entity changes can now update resources, and those updates may trigger batch and flushing operations within the SDK, it is possible for rapid changes to resources to create a cascade of SDK operations that may lead to performance issues.

Investigating the practical implications of this problem has not led to any examples of resources that can be expected to exhibit this behavior. For the time being, backoff or other thrash mitigation strategies are left out of this proposal. If a specific resource does end up requiring some form of throttling, the resource detector that updates that particular resource should manage this issue. If a common strategy for throttling emerges, it can be added to the EntityProvider at a later date.

## FAQ

### Is there some distinction between "identifying resources" and "updatable resources"?

Surprising as it may be, there is no direct correlation between an attribute being
"identifying" and that attribute matching the lifespan of an application.

Some resources are used to identify a service instance – `service.name`, `service.instance.id`, etc.
These resources naturally match the lifespan of the service instance. An "immutability requirement"
is not necessary in this case because there is no reason to ever update these values.

Other resources are used to identify other critical lifespans, and these values
do change. For example, the user's identity may change as the user logs in and out
of the application. And multiple sessions may start and end over the lifespan of
an application.

Therefore there is no need to conflate "identifying" with "immutable." Telemetry
simply models reality. If we change a resource attribute that is not supposed to
change, that is an implementation error. If we don't change a resource attribute
when the application state changes, that is also an implementation error. With the
correct tools these errors are unlikely, as it is very obvious when these individual
attributes should and shouldn't change.

### Why were resources immutable in the first place?

Use of the term "immutable" points at the real reason this requirement was initially
added to the specification. When an application initially boots up, gathering some resources
require async operations that may take time to acquire. The start of the application
must be delayed until all of these resources are resolved, otherwise the initial
batches of telemetry would be poorly indexed. This initial telemetry is critical
and too valuable to lose due to a late loading of certain resources.

A convenient cudgel with which to beat developers into doing the right thing is
to make the resource object "immutable" by not providing an update function. This
makes it impossible to late load resources and helps to avoid this mistake when
installing OpenTelemetry in an application.

However, OpenTelemetry has since developed a resource detector pattern that gives
developers the tools they need to cleanly resolve all initial resources before
application start. This is a sufficient solution for the bootstrapping problem;
at this point in OpenTelemetry's development adding an update function to resources
would not cause issues in this regard.

## Example Usage

DRAFT

## Example Implementation

Pseudocode examples for a possible Validator and EntityProvider implementation.
Attention is placed on making the EntityProvider thread safe, without introducing
any locking or synchronization overhead to `GetResource`, which is the only
EntityProvider method on the hot path for OpenTelemetry instrumentation.

```php
// Example of a thread-safe EntityProvider
class EntityProvider{
  
  *Resource resource
  Lock lock
  OrderedMap[string:Entity] entities // an ordered map of Entities that uses entity IDs as keys
  Array[EntityListener] listeners
  
  GetResource() Resource {
    return this.resource;
  }
  
  OnChange(EntityListener listener) {
    this.lock.Acquire();

    listeners.Append(listener);

    this.lock.Release();
  }

  AddEntity(string ID, string name, Map[Attribute] attributes){
    this.lock.Acquire();

    // Acquire the correct entity based on ID
    var entity = NewEntity(ID, name, attributes);
    
    // Append the entity to the end of the OrderedMap and set the key to the ID
    this.entities.Append(ID, entity);

    // create a new resource
    var mergedResource = NewResource(this.entities);

    // safely change the resource reference without blocking
    AtomicSwap(this.resource, mergedResource);

    // create an EntityState event from the entity
    var entityState = entity.EntityState();

    // calling listeners inside of the lock ensures that the listeners do not fire
    // out of order or get called simultaneously by multiple threads, but would
    // also allow a poorly implemented listener to block the EntityProvider.
    for (listener in this.listeners) {
        listener.OnEntityState(entityState, mergedResource);
    }

    this.lock.Release();
  }
  
  UpdateEntity(string ID, Map[Attribute] attributes){
    this.lock.Acquire();

    // Acquire the correct entity based on ID
    var entity = this.entities[ID]
    
    // If there is no entity, log the error and return. This follows the pattern
    // of not returning errors in the OpenTelemetry API.
    if(!entity) {
      LogError(EntityNotFound);
      this.lock.Release();
      return;
    }
    
    // Replace the attributes on the entity.
    entity.attributes = attributes;
    
    // create a new resource
    var mergedResource = NewResource(this.entities);

    // safely change the resource reference without blocking
    AtomicSwap(this.resource, mergedResource);

    // create an EntityState event from the entity
    var entityState = entity.EntityState();

    // calling listeners inside of the lock ensures that the listeners do not fire
    // out of order or get called simultaneously by multiple threads, but would
    // also allow a poorly implemented listener to block the EntityProvider.
    for (listener in this.listeners) {
        listener.OnEntityState(entityState, mergedResource);
    }

    this.lock.Release();
  }

  DeleteEntity(string ID, Map[Attribute] attributes){
    this.lock.Acquire();

    // Acquire the correct entity based on ID
    var entity = this.entities[ID]
    
    // If there is no entity, log the error and return. This follows the pattern
    // of not returning errors in the OpenTelemetry API.
    if (!entity) {
      LogError(EntityNotFound);
      this.lock.Release();
      return;
    }

    // remove the entity from the map
    this.entities.Delete(ID);
    
    // create a new resource
    var mergedResource = NewResource(this.entities);

    // safely change the resource reference without blocking
    AtomicSwap(this.resource, mergedResource);

    // create an EntityDelete event from the entity
    var entityDelete = entity.EntityDelete();

    // calling listeners inside of the lock ensures that the listeners do not fire
    // out of order or get called simultaneously by multiple threads, but would
    // also allow a poorly implemented listener to block the EntityProvider.
    for (listener in this.listeners) {
        listener.OnEntityDelete(entityDelete, mergedResource);
    }

    this.lock.Release();
  }
}
```
