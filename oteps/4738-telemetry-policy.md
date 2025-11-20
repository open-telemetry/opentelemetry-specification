# Telemetry Policies

Defines a new concept for OpenTelemetry: Telemetry Policy.

## Motivation

OpenTelemetry provides a robust, standards based instrumentation solution.
this includes many great components, e.g.

- Declarative configuration
- Control Protocol via OpAMP
- X-language extension points in the SDK (samplers, processors, views)
- Telemetry-Plane controls via the OpenTelemetry collector.

However, OpenTelemetry still struggles to provide true "remote control"
capabilities that are implementation agnostic. When using OpAMP with an
OpenTelemetry collector, the "controlling server" of OpAMP needs to understand
the configuraiton layout of an OpenTelemetry collector.  If a user asked the
server to "filter out all attributes starting with `x.`", the server would
need to understand/parse the OpenTelemetry collector configuration. If the
controlling sever was also managing an OpenTelemetry SDK, then it would need
a *second* implementation of the 'filter attribute" feature for the SDK vs.
the Collector. Additionally, as the OpenTelemetry collector allows custom
configuration file formats, there is no way for a "controlling server" to
operate with an OpenTelemetry Collection distribution without understanding all
possible implementations it may need to talk to.

Additionally, existing remote-control capabilities in OpenTelemetry are not
"guaranteed" to be usable due to specification language. For example, today
one can use the Jaeger Remote Sampler specified for OpenTelemetry SDKs and the
jaeger remote sampler extension in the OpenTelemetry collector to dynamically
control the sampling of spans in SDKs. However, File-based configuration does
not require dynamic reloading of configuration. This means attempting to
provide a solution like Jaeger-remote-sampler with just OpAMP + file-based
config is impossible, today.

However, we believe there is a way to acheive our goals without changing
the direction of OpAmp or File-based configuration. Instead we can break apart
the notion of "Configuration" from "Policy", providing a new capability in
OpenTelemetry.

## Explanation

We define a new concept called a `Telemetry Policy`.  A Policy is an
intent-based specification from a user of OpenTelemetry.

- **Typed**: A policy self identifies its "type". Policies of different types
  cannot be merged, but policies of the same type MUST be merged together.
- **Clearly specified behavior**: A policy type enforces a specific behavior for
  a clear use case, e.g. trace sampling, metric aggregation, attribute
  filtering.
- **Implementation Agnostic**: I can use the exact same policy in the collector
  or an SDK or any other component supporting OpenTelemetry's ecosystem.
- **Standalone**: I don't need to understand how a pipeline is configured to define
  policy.
- **Dynamic**: We expect policies to be defined and driven outside the lifecycle
  of a single collector or SDK. This means the SDK behavior needs the ability
  to change post-instantiation.
- **Idempotnent**: I can give a policy to multiple components in a
  telemetry-plane safely. E.g. if both an SDK and collector obtain an
  attribute-filter policy, it would only occur once.

Every policy is defined with the following:

- A `type` denoting the use case for the policy
- A json schema denoting what a valid definitin of the policy entails.
- TODO - A merge algorithm, denoting how multiple policies can be merged
  together in a component to create desired behavior.
- TODO - A specification denoting the behavior the policy enforces.
- TODO - *implicily* a policy has a target resource / signal it is aimed at.
  This will be used to route policies to destinations.

Example policy types include: 
- `trace-sampling`: define how traces are sampled
- `metric-rate`: define sampling period for metrics
- `log-filter`: define how logs are sampled/filtered
- `attribute-redaction`: define attributes which need redaction/removal.
- `metric-aggregation`: define how metrics should be aggregated (i.e. views).
- `exemplar-sampling`: define how exemplars are sampled

TODO - more examples?

TODO - Remaining high level pieces:

- SDK Components
  - `PolicyProvider`
    - Can "push" policies into the provider.
    - Provides "observable" access to policies (e.g. notify on change)
  - Extension Points
    - `PolicySampler`: Pulls relevant `trace-sampling` policies from
      PolicyProvider, and uses them.
    - `PolicyLogProcessor`: Pulls Relevant `log-filter` policies from
      PolicyProvider and uses them.
    - `PolicyPeriodicMetricReader`: Pulls Relevant `metric-rate` policies
      from PolicyProvider and uses them to export metrics.
    - TODO: SDK-wide attribute processors
    - TODO: SDK-view policies
- Collector Components
  - `PolicyProcessor`
    - Pulls configured policies that can be enforced as a processor.
    - E.g. `log-filter`, `attribute-redaction`
  - TODO - others?
- OpAmp Interaction
  - Policy = custom extension
  - Can we safely "roll back" a policy if it caused a breakage?
- Confguration Interaction: We always expect "policy-aware" components to be configured, policies are ignorant of pipelines.


## Internal details

TDOO - write

From a technical perspective, how do you propose accomplishing the proposal? In particular, please explain:

* How the change would impact and interact with existing functionality
* Likely error modes (and how to handle them)
* Corner cases (and how to handle them)

While you do not need to prescribe a particular implementation - indeed, OTEPs should be about **behaviour**, not implementation! - it may be useful to provide at least one suggestion as to how the proposal *could* be implemented. This helps reassure reviewers that implementation is at least possible, and often helps them inspire them to think more deeply about trade-offs, alternatives, etc.

## Trade-offs and mitigations

TODO - write

What are some (known!) drawbacks? What are some ways that they might be mitigated?

Note that mitigations do not need to be complete *solutions*, and that they do not need to be accomplished directly through your proposal. A suggested mitigation may even warrant its own OTEP!

## Prior art and alternatives

TODO - discuss https://github.com/open-telemetry/opentelemetry-specification/pull/4672

### Declarative Config + OpAMP as sole control for telemetry

The declarative config + OpAMP could be used to send any config to any
component in OpenTelemetry. Here, we would leverage OpAMP configuration passing
and the open-extension and definitions of Declarative Config to pass the whole
behavior of an SDK or Collector from an OpAMP "controlling server" down to a
component and have them dynamically reload behavior.

What this solution doesn't do is answer how to understand what config can be
sent to what component, and how to drive control / policy independent of
implementation or pipeline set-up.  For example, imagine a simple collector
configuration:

```yaml
recievers:
  otlp:
  prometheus:
    # ... config ...
processors:
  batch:
  memorylimiter:
  transform/drop_attribute:
    # config to drop an attribute
exporters:
  otlp:
pipelines:
  metrics/crtical:
    receivers: [otlp]
    processors: [batch, transform/drop_attribute]
    exporters: [otlp]
  metrics/all:
    receivers: [prometheus]
    processors: [memorylimiter]
    exporters: [otlp]
```

Here, we have two pipelines with intended purposes and tuned configurations.
One which will *not* drop metrics when memory limits are reached and another
that will. Now - if we want to drop a particular metric from being reported,
which pipeline do we modify?  Should we construct a new processor for that
purpose?  Should we always do so?

Now imagine we *also* have an SDK we're controlling with declarative config. If
we want to control metric inclusion in that SDK, we'd need to generate a
completely different looking configuration file, as follows:

```yaml
file_format: '1.0-rc.1'
# ... other config ...
meter_provider:
  readers:
    - my_custom_metric_filtering_reader:
        my_filter_config: # defines what to filter
        wrapped: 
          periodic:
            exporter:
              otlp_http:
                endpoint: ${OTEL_EXPORTER_OTLP_ENDPOINT:-http://localhost:4318}/v1/metric
```

Here, I've created a custom component in java to allow filtering which metrics are read.
However, to insert / use this component I need to have all of the following:

- Know that this component exists in the java SDK
- Know how to wire it into any existing metric export pipeline (e.g. my reader
  wraps another reader that has the real export config).
  Note: This likely means I need to understand the rest of the exporter
  configuration or be able to parse it.

This is not ideal for a few reasons:

- Anyone designing a server that can control telemetry flow MUST have a deep
  understanding of all components it could control and their implementations.
- We don't have a "safe" mechanism to declare what configuration is supported
  or could be sent to a specific component (note: we can design one)
- The level of control we'd expose from our telemetry systems is *expansive*
  and possibly dangerous. 
  - We cannot limit the impact of any remote configuration on the working of a
    system. We cannot prevent changes that may take down a process.
  - We cannot limit the execution overhead of configuration or fine-grained
    control over what changes would be allowed remotely.

## Open questions

What are some questions that you know aren't resolved yet by the OTEP? These may be questions that could be answered through further discussion, implementation experiments, or anything else that the future may bring.

## Prototypes

Link to any prototypes or proof-of-concept implementations that you have created.
This may include code, design documents, or anything else that demonstrates the
feasibility of your proposal.

Depending on the scope of the change, prototyping in multiple programming
languages might be required.

## Future possibilities

What are some future changes that this proposal would enable?
