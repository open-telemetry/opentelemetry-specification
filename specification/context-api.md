# Context and Tags API

The Context API consist of a few main classes:

- `Context` is the implicit or explicit context handle, specific to each language.
- `TagMap` is an immutable object storing the key:value assignments.  See [Span](#span).

## `Context`

Whether the current Context is an explicit or implicit construct in the target language, the API provides accessors to retrieve the current Span and the current TagMap.

### Context constructors

#### `Context.Empty()`: returns context with no SpanContext and an empty TagMap

The Context API provides a way to obtain an empty Context, which has no associated SpanContext and an empty TagMap.

#### `Context.WithMap(replacement)`: support binding a new TagMap to a Context

The Context API provides a way to replace the current TagMap with a new one.  Returns a new Context with the provided TagMap.

#### `Context.NewContext(mutators...)`: support extending from an existing TagMap

The Context API provides a way to derive the a new Context by modifying the existing Context's TagMap, using one of the provided mutators:

The defined mutators are:
- `Insert(key, value)`: Enter a new key:value only if the key is not already defined
- `Upsert(key, value)`: Enter a new key:value or update the existing key:value unconditionally
- `Delete(key, value)`: Remove a key:value from the map, if it exists.

This is defined as `Context.WithMap(TagMap.FromContext().Apply(mutators))`.  Returns a new Context with the derived TagMap.  The incoming context is not modified.

### `Context` manipulation

#### `Context.Enter()/Exit()`: methods to switch the active Context

The Context API provides a way to execute code scoped to a new
context.  Depending on language features, the SDK should provide APIs
that ensure execution automatically switches out of the Context after
the scoped activity finishes.  In practice, this usually means the
Context API relies on try/finally statements, defered callbacks, or
automatic destructors to modify the active Context.

### `Context` accessors

#### `Context.Active()`: Get the current Span

This may be use to get the current SpanContext as well.  Use `Trace.Start` to update the active span.

#### `TagMap.FromContext()`: Get the current map

This returns the `TagMap` belonging to the active Context.

## `TagMap` 

### `TagMap` constructors

#### `TagMap.NewMap(pairs...)`: New map from list of key:value pairs

Construct a new map by giving an explicit key:value list.

#### `TagMap.Apply(mutators...)`: New map from list of mutators (see Context.NewContext)

Construct a new map by giving a sequence of key:value mutators.

### TagMap MaxHops

TagMap is an immutable map of key:value assignments with metadata about how each key:value assignment (i.e., tag) should propagate.  Keys are individually assigned a "Max Hops" value which determines the number of remote processes it will propagate into.  Values for Max Hops:

- `0`: The tag will propagate to internal Contexts belonging to the same trace, within the local process, but will not propagate to a remote host
- `>=1`: The tag will propagate to a depth of (up to) 1 or more remote hosts from the current node in the trace
- `-1`: The tag will propagate indefinitely (default).

The default behavior is to propagate tags indefinitely.

#### Providing explicit Max Hops

Mutators have a additional modifiers allowing `MaxHops` to be set in the application:

- `Insert(key, value).WithMaxHops(n)`: Mutator with optional MaxHops setting.
- `Upsert(key, value).WithMaxHops(n)`: Mutator with optional MaxHops setting.
- `Delete(key, value).WithMaxHops(n)`: Mutator with optional MaxHops setting.

#### `TagMap.SetMaxHops(key)`: Modify the MaxHops setting for a single key

The `SetMaxHops` API supports controlling tag propagation for a single key.

### TagMap accessors

#### `TagMap.Foreach`: Iterate over the key:values of a map

This function calls a callback with the full set of key:value assignments, along with metadata.

#### `TagMap.Len`: Count the number of key:value assignments

This function returns the map size.

#### `TagMap.HasValue`: Check whether a key exists

This function returns true if the key is defined in the map.

#### `TagMap.Value`: Lookup the key's value

This function returns the current key assignment and a boolean to indicate whether it exists.

