# TraceConfig

Global configuration of the trace service. This allows users to change configs for the default
sampler, maximum events to be kept, etc.

## TraceParams
Represents the set of parameters that users can control
* Default `Sampler` - used when creating a Span if no specific sampler is given. The default sampler
is a [Probability](Sampling.md) sampler with the probability set to `1/10000`.

### Limits

We define limits on the number of attributes, annotations, message events and links on each span
in order to prevent unbounded memory increase for long-running spans.

When limits are exceeded, implementations should by default preserve the most recently added values
and drop the oldest values. Implementations may make this policy configurable.

Implementations should track the number of dropped items per span. Some backends provide dedicated
support for tracking these counts. Others do not, but exporters may choose to represent these in
exported spans in some way (for example, as a tag).

Implementations may support tracking the total number of dropped items in stats as outlined.

| Item | Default Limit | Measure for dropped items |
| --- | --- | --- |
| Attributes | 32 | opencensus.io/trace/dropped_attributes |
| Annotations | 32 | opencensus.io/trace/dropped_annotations |
| Message Events | 128 | opencensus.io/trace/dropped_message_events |
| Links | 32 | opencensus.io/trace/dropped_links |

No views should be registered by default on these measures. Users may register views if they
are interested in recording these measures.

Implementations should provide a way to override the globals per-span.

## API Summary
* Permanently update the active TraceParams.
* Temporary update the active TraceParams. This API allows changing of the active params for a
certain period of time. No more than one active temporary update can exist at any moment.
* Get current active TraceParams.
