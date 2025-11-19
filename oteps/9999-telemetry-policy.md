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

What are some prior and/or alternative approaches? For instance, is there a corresponding feature in OpenTracing or OpenCensus? What are some ideas that you have rejected?

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
