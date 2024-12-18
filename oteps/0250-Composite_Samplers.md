# Composite Samplers Proposal

This proposal addresses head-based sampling as described by the [Open Telemetry SDK](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/trace/sdk.md#sampling).
It introduces additional _composite samplers_.
Composite samplers use other samplers (_delegates_ or _children_) to make sampling decisions.
The composite samplers invoke the delegate samplers, but eventually make the final call.

Some of the new samplers proposed here have been designed to work with Consistent Probability Samplers. For detailed description of this concept see [probability sampling (OTEP 235)](https://github.com/open-telemetry/oteps/blob/main/text/trace/0235-sampling-threshold-in-trace-state.md).
Also see Draft PR 3910 [Probability Samplers based on W3C Trace Context Level 2](https://github.com/open-telemetry/opentelemetry-specification/pull/3910).

## Motivation

The need for configuring head sampling has been explicitly or implicitly indicated in several discussions, both within the [Sampling SIG](https://docs.google.com/document/d/1gASMhmxNt9qCa8czEMheGlUW2xpORiYoD7dBD7aNtbQ) and in the wider community.
Some of the discussions are going back a number of years, see for example

- issue [173](https://github.com/open-telemetry/opentelemetry-specification/issues/173): Way to ignore healthcheck traces when using automatic tracer across all languages?
- issue [1060](https://github.com/open-telemetry/opentelemetry-java-instrumentation/issues/1060): Exclude URLs from Tracing
- issue [1844](https://github.com/open-telemetry/opentelemetry-specification/issues/1844): Composite Sampler

Unfortunately, some of the valuable ideas flowing at the sampling SIG meetings never got recorded at the time of their inception, but see [Sampling SIG Research Notes](https://github.com/open-telemetry/oteps/pull/213) or the comments under [OTEP 240: A Sampling Configuration proposal](https://github.com/open-telemetry/oteps/pull/240) for some examples.

## The Goal

The goal of this proposal is to help creating advanced sampling configurations using pre-defined building blocks. Let's consider the following example of sampling requirements. It is believed that many users will have requirements following a similar pattern. Most notable elements here are trace classification based on target URL, some spans requiring special handling, and putting a sanity cap on the total volume of exported spans.

### Example

Head-based sampling requirements.

- for root spans:
  - drop all `/healthcheck` requests
  - capture all `/checkout` requests
  - capture 25% of all other requests
- for non-root spans
  - follow the parent sampling decision
  - however, capture all calls to service `/foo` (even if the trace will be incomplete)
- in any case, do not exceed 1000 spans/minute

We present two quite different approaches to composite samplers. The first one uses only the current [sampling API](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/trace/sdk.md#sampling).
It can be applied to a large variety of samplers, but may not work correctly for Consistent Probability Samplers. It is also not very efficient nor elegant.

The second approach is applicable exclusively to Consistent Probability Samplers, and is more efficient and less prone to misconfiguration. It requires additional API to be provided by the delegate samplers.

__Note__: both approaches call for calculating _unions_ of Attribute sets.
Whenever such union is constructed, in case of conflicting attribute keys, the attribute definition from the last set that uses that key takes effect. Similarly, whenever modifications of `Tracestate` are performed in sequence, in case of conflicting keys, the last modification erases the previous values.

## Approach One

The following new composite samplers are proposed.

### AnyOf

`AnyOf` is a composite sampler which takes a non-empty list of Samplers (delegates) as the argument. The intention is to make `RECORD_AND_SAMPLE` decision if __any of__ the delegates decides to `RECORD_AND_SAMPLE`.

Upon invocation of its `shouldSample` method, it MUST go through the whole list and invoke `shouldSample` method on each delegate sampler, passing the same arguments as received, and collecting the delegates' sampling Decisions.

`AnyOf` sampler MUST return a `SamplingResult` with the following elements.

- If all of the delegate Decisions are `DROP`, the composite sampler MUST return `DROP` Decision as well.
If any of the delegate Decisions is `RECORD_AND_SAMPLE`, the composite sampler MUST return `RECORD_AND_SAMPLE` Decision.
Otherwise, if any of the delegate Decisions is `RECORD_ONLY`, the composite sampler MUST return `RECORD_ONLY` Decision.
- The set of span `Attributes` to be added to the `Span` is the union of the sets of `Attributes` as provided by those delegate samplers which produced a sampling Decision other than `DROP`.
- The `Tracestate` to be used with the new `Span` is obtained by cumulatively applying all the potential modifications of the parent `Tracestate` by the delegate samplers.

Each delegate sampler MUST be given a chance to participate in the sampling decision as described above and MUST see the same _parent_ state. The resulting sampling Decision does not depend on the order of the delegate samplers.

### Conjunction

`Conjunction` is a composite sampler which takes two Samplers (delegates) as the arguments. These delegate samplers will be hereby referenced as First and Second. This kind of composition forms conditional chaining of both samplers.

Upon invocation of its `shouldSample` method, the Conjunction sampler MUST invoke `shouldSample` method on the First sampler, passing the same arguments as received, and examine the received sampling Decision.
Upon receiving `DROP` or `RECORD_ONLY` decision it MUST return the `SamplingResult` (which includes a set of `Attributes` and `Tracestate` in addition to the sampling Decision) from the First sampler, and it MUST NOT proceed with querying the Second sampler.
If the sampling decision from the First sampler is `RECORD_AND_SAMPLE`, the Conjunction sampler MUST invoke `shouldSample` method on the Second sampler, effectively passing the `Tracestate` received from the First sampler as the parent trace state.

If the sampling Decision from the Second sampler is `RECORD_AND_SAMPLE`, the Conjunction sampler MUST return a `SamplingResult` which is constructed as follows:

- The sampling Decision is `RECORD_AND_SAMPLE`.
- The set of span `Attributes` to be added to the `Span` is the union of the sets of `Attributes` as provided by both samplers.
- The `Tracestate` to be used with the new `Span` is as provided by the Second sampler.

If the sampling Decision from the Second sampler is `RECORD_ONLY`, the Conjunction sampler MUST return a `SamplingResult` which is constructed as follows:

- The sampling Decision is `RECORD_ONLY`.
- The set of span `Attributes` to be added to the `Span` is the set of `Attributes` returned by the First sampler.
- The `Tracestate` to be used with the new `Span` is the `Tracestate` provided by the Second sampler.

If the sampling Decision from the Second sampler is `DROP`, the Conjunction sampler MUST return a `SamplingResult` which is constructed as follows:

- The sampling Decision is `DROP`.
- The set of span `Attributes` to be added to the `Span` is empty.
- The `Tracestate` to be used with the new `Span` is the `Tracestate` provided by the Second sampler.

### RuleBased

`RuleBased` is a composite sampler which performs `Span` categorization (e.g. when sampling decision depends on `Span` attributes) and sampling.
The Spans can be grouped into separate categories, and each category can use a different Sampler.
Categorization of Spans is aided by `Predicates`.

#### Predicate

The Predicates represent logical expressions which can access `Span` `Attributes` (or anything else available when the sampling decision is to be made), and perform tests on the accessible values.
For example, one can test if the target URL for a SERVER span matches a given pattern.
`Predicate` interface allows users to create custom categories based on information that is available at the time of making the sampling decision.

##### SpanMatches

This is a routine/function/method for `Predicate`, which returns `true` if a given `Span` matches, i.e. belongs to the category described by the Predicate.

##### Required Arguments for Predicates

The arguments represent the values that are made available for `ShouldSample`.

- `Context` with parent `Span`.
- `TraceId` of the `Span` to be created.
- Name of the `Span` to be created.
- Initial set of `Attributes` of the `Span` to be created.
- Collection of links that will be associated with the `Span` to be created.

#### Required Arguments for RuleBased

- `SpanKind`
- list of pairs (`Predicate`, `Sampler`)

For making the sampling decision, if the `Span` kind matches the specified kind, the sampler goes through the list in the provided order and calls `SpanMatches` on `Predicate`s passing the same arguments as received by `ShouldSample`. If a call returns `true`, the corresponding `Sampler` will be called to make the final sampling decision. If the `SpanKind` does not match, or none of the calls to `SpanMatches` yield `true`, the final decision is `DROP`.

The order of `Predicate`s is essential. If more than one `Predicate` matches a `Span`, only the Sampler associated with the first matching `Predicate` will be used.

## Summary - Approach One

### Example - sampling configuration

Going back to our example of sampling requirements, we can now configure the head sampler to support this particular case, using an informal notation of samplers and their arguments.
First, let's express the requirements for the ROOT spans as follows.

```
S1 = RuleBased(ROOT, {
 (http.target == /healthcheck) => AlwaysOff,
 (http.target == /checkout) => AlwaysOn,
 true => TraceIdRatioBased(0.25)
 })
```

Note: technically, `ROOT` is not a `SpanKind`, but is a special token matching all Spans with invalid parent context (i.e. the ROOT spans, regardless of their kind).

In the next step, we can build the sampler to handle non-root spans as well:

```
S2 = ParentBased(S1)
```

The special case of calling service `/foo` can now be supported by:

```
S3 = AnyOf(S2, RuleBased(CLIENT, { (http.url == /foo) => AlwaysOn })
```

Finally, the last step is to put a limit on the stream of exported spans. One of the available rate limiting sampler that we can use is Jaeger [RateLimitingSampler](https://github.com/open-telemetry/opentelemetry-java/blob/main/sdk-extensions/jaeger-remote-sampler/src/main/java/io/opentelemetry/sdk/extension/trace/jaeger/sampler/RateLimitingSampler.java):

```
S4 = Conjunction(S3, RateLimitingSampler(1000 * 60))
```

### Limitations of composite samplers in Approach One

Not all samplers can participate as components of composite samplers without undesired or unexpected effects. Some samplers require that they _see_ each `Span` being created, even if the span is going to be dropped. Some samplers update the trace state or maintain internal state, and for their correct behavior it it is assumed that their sampling decisions will be honored by the tracer at the face value in all cases. A good example for this are rate limiting samplers which have to keep track of the rate of created spans and/or the rate of positive sampling decisions.

The need to encode and decode the `Tracestate` multiple times affects performance of the composite samplers. This drawback is eliminated in Approach Two.

## Approach Two

A principle of operation for Approach Two is that `ShouldSample` is invoked only once, on the root of the tree formed by composite samplers. All the logic provided by the composition of samplers is handled by calculating the threshold values, delegating the calculation downstream as necessary.

### New API

To make this approach possible, all Consistent Probability Samplers which participate in the samplers composition need to implement the following API, in addition to the standard Sampler API. We will use the term _Composable Sampler_ to denote Consistent Probability Samplers which provide the new API and conform to the rules described here.
The composite samplers in Approach Two are Composable Samplers as well.

#### GetSamplingIntent

This is a routine/function/method for all Composable Samplers. Its purpose is to query the sampler about the activities it would perform had it been asked to make a sampling decision for a given span, however, without constructing the actual sampling Decision.

#### Required Arguments for GetSamplingIntent

The arguments are the same as for [`ShouldSample`](https://github.com/open-telemetry/opentelemetry-specification/blob/main/specification/trace/sdk.md#shouldsample) except for the `TraceId`.

- `Context` with parent `Span`.
- Name of the `Span` to be created.
- `SpanKind` of the `Span` to be created.
- Initial set of `Attributes` of the `Span` to be created.
- Collection of links that will be associated with the `Span` to be created.

#### Return value

The return value is a structure (`SamplingIntent`) with the following elements:

- The THRESHOLD value represented as a 14-character hexadecimal string, with value of `null` representing non-probabilistic `DROP` decision (implementations MAY use different representation, if it appears more performant or convenient),
- A function (`IsAdjustedCountReliable`) that provides a `boolean` value indicating that the adjusted count (calculated as reciprocal of the sampling probability) can be faithfully used to estimate span metrics,
- A function (`GetAttributes`) that provides a set of `Attributes` to be added to the `Span` in case of positive final sampling decision,
- A function (`UpdateTraceState`) that given an input `Tracestate` and sampling Decision provides a `Tracestate` to be associated with the `Span`. The samplers SHOULD NOT add or modify the `th` value for the `ot` key within these functions.

#### Requirements for the basic samplers

The `ConsistentAlwaysOff` sampler MUST provide a `SamplingIntent` with

- The THRESHOLD value of `null` (or equivalent),
- `IsAdjustedCountReliable` returning `false`,
- `GetAttributes` returning an empty set,
- `UpdateTraceState` returning its argument, without any modifications.

The `ConsistentAlwaysOn` sampler MUST provide a `SamplingIntent` with

- The THRESHOLD value of `00000000000000` (or equivalent),
- `IsAdjustedCountReliable` returning `true`,
- `GetAttributes` returning an empty set,
- `UpdateTraceState` returning its argument, without any modifications.

#### Constructing `SamplingResult`

The process of constructing the final `SamplingResult` in response to a call to `ShouldSample` on the root sampler of the composite samplers tree consists of the following steps.

- The sampler gets its own `SamplingIntent`, it is a recursive process as described below (unless the sampler is a leaf),
- The sampler compares the received THRESHOLD value with the trace Randomness value to arrive at the final sampling `Decision`,
- The sampler calls the received `UpdateTraceState` function passing the parent `Tracestate` and the final sampling `Decision` to get the new `Tracestate` to be associated with the `Span` - again, in most cases this is a recursive step,
- In case of positive sampling decision:
  - the sampler calls the received `GetAttributes` function to determine the set of `Attributes` to be added to the `Span`, in most cases it will be a recursive step,
  - the sampler calls the received `IsAdjustedCountReliable` function, and in case of `true` it modifies the `th` value for the `ot` key in the `Tracestate` according to the received THRESHOLD; if the returned value is `false`, it removes the `th` value for the `ot` key from the `Tracestate`,
- In case of negative sampling decision, it removes the `th` value for the `ot` key from the `Tracestate`.

### ConsistentRuleBased

This composite sampler re-uses the concept of Predicates from Approach One.

#### Required Arguments for ConsistentRuleBased

- `SpanKind`
- list of pairs (`Predicate`, `ComposableSampler`)

For calculating the `SamplingIntent`, if the `Span` kind matches the specified kind, the sampler goes through the list in the provided order and calls `SpanMatches` on `Predicate`s passing the same arguments as received. If a call returns `true`, the result is as returned by `GetSamplingIntent` called on the corresponding `ComposableSampler`. If the `SpanKind` does not match, or none of the calls to `SpanMatches` yield `true`, the result is obtained by calling `GetSamplingIntent` on `ConsistentAlwaysOffSampler`.

### ConsistentParentBased

The functionality of `ConsistentParentBased` sampler corresponds to the standard `ParentBased` sampler.
It takes one ComposableSampler delegate as the argument.
The delegate is used to make sampling decisions for ROOT spans.

The behavior of `ConsistentParentBased` caters to the case where a non-probabilistic sampler was used to sample the parent span.

Upon invocation of its `GetSamplingIntent` function, the sampler checks if there's a valid parent span context. If there isn't, the sampler MUST return the result of calling `GetSamplingIntent` on the delegate.

Otherwise, the sampler attempts to extract the threshold value from the parent trace state.
The sampler MUST return a `SamplingIntent` as follows.

If the parent trace state has a valid threshold T:

- The resulting THRESHOLD value is T.
- The `IsAdjustedCountReliable` returns `true`.

If the parent trace state has no valid threshold, the sampler examines the `sampled` flag from the traceparent.

If the flag is set:

- The resulting THRESHOLD value is `00000000000000` (or equivalent).
- The `IsAdjustedCountReliable` returns `false`.

If the flag is not set:

- The resulting THRESHOLD value is `null` (or equivalent).
- The `IsAdjustedCountReliable` returns `false`.

In all cases with valid parent context:

- The `GetAttributes` function returns empty set.
- The `UpdateTraceState` function returns its argument, without any modifications.

### ConsistentAnyOf

`ConsistentAnyOf` is a composite sampler which takes a non-empty list of ComposableSamplers (delegates) as the argument. The intention is to make a positive sampling decision if __any of__ the delegates would make a positive decision.

Upon invocation of its `GetSamplingIntent` function, it MUST go through the whole list and invoke `GetSamplingIntent` function on each delegate sampler, passing the same arguments as received.

`ConsistentAnyOf` sampler MUST return a `SamplingIntent` which is constructed as follows:

- If any of the delegates returned a non-`null` threshold value, the resulting threshold is the lexicographical minimum value T from the set of those non-`null` values, otherwise `null`.
- The `IsAdjustedCountReliable` returns `true`, if any of the delegates returning the threshold value equal to T returns `true` upon calling its `IsAdjustedCountReliable` function, otherwise it returns `false`.
- The `GetAttributes` function calculates the union of `Attribute` sets as returned by the calls to `GetAttributes` function for each delegate, in the declared order.
- The `UpdateTraceState` function makes a chain of calls to the `UpdateTraceState` functions as returned by the delegates, passing the received `Tracestate` as argument to subsequent calls and returning the last value received.

Each delegate sampler MUST be given a chance to participate in calculating the `SamplingIntent` as described above and MUST see the same argument values. The order of the delegate samplers does not affect the final sampling `Decision`.

### ConsistentRateLimiting

`ConsistentRateLimiting` is a composite sampler that helps control the average rate of sampled spans while allowing another sampler (the delegate) to provide sampling hints.

#### Required Arguments for ConsistentRateLimiting

- ComposableSampler (delegate)
- maximum sampling (throughput) target rate

The sampler SHOULD measure and keep the average rate of incoming spans, and therefore also of the desired ratio between the incoming span rate to the target span rate.
Upon invocation of its `GetSamplingIntent` function, the composite sampler MUST get the `SamplingIntent` from the delegate sampler, passing the same arguments as received.

The returned `SamplingIntent` is constructed as follows.

- If using the obtained threshold value as the final threshold would entail sampling more spans than the declared target rate, the sampler SHOULD set the threshold to a value that would meet the target rate. Several algorithms can be used for threshold adjustment, no particular behavior is prescribed by the specification though.
- The `IsAdjustedCountReliable` returns the result of calling this function on the `SamplingIntent` provided by the delegate.
- The `GetAttributes` function returns the result of calling this function on the `SamplingIntent` provided by the delegate.
- The `UpdateTraceState` function returns the `Tracestate` as returned by calling `UpdateTraceState` from the delegate's `SamplingIntent`.

TO DO: consider introducing a `ConsistentConjuntion` sampler (similar to `Conjunction` from Approach One) that would generalize the relationship between the delegate and the principal sampler, and remove the explicit delegate from `ConsistentRateLimiting`.

## Summary - Approach Two

### Example - sampling configuration with Approach Two

With the samplers introduced by Approach Two, our example requirements can be coded in a very similar way as with Approach One. However, the work of the samplers configured this way forms a tree of `GetSamplingIntent` invocations rather than `ShouldSample` invocations as in Approach One.

```
S = ConsistentRateLimiting(
     ConsistentAnyOf(
       ConsistentParentBased(
         ConsistentRuleBased(ROOT, {
             (http.target == /healthcheck) => ConsistentAlwaysOff,
             (http.target == /checkout) => ConsistentAlwaysOn,
             true => ConsistentFixedThreshold(0.25)
         }),
       ConsistentRuleBased(CLIENT, {
         (http.url == /foo) => ConsistentAlwaysOn
       }
     ),
     1000 * 60
   )
```

### Limitations of composite samplers in Approach Two

Making sampling decisions with samplers from Approach Two is more efficient than in Approach One, especially if, platform permitting, `null` values can be used for `GetAttributes` and `UpdateTraceState` functions to represent the prevailing trivial cases of _no-new-attributes_ and _no-special-trace-state-keys_. The only limitation of this approach that it operates exclusively within the domain of Composable Samplers (a subset of Consistent Probability Samplers).

Developers of Composable Samplers should consider that the sampling Decision they declare as their intent might be different from the final sampling Decision.

### Prototyping

A prototype implementation of ComposableSamplers for Java is available, see [ConsistentSampler](https://github.com/open-telemetry/opentelemetry-java-contrib/blob/main/consistent-sampling/src/main/java/io/opentelemetry/contrib/sampler/consistent56/ConsistentSampler.java) and its subclasses.

## Prior art

A number of composite samplers are already available as independent contributions
([RuleBasedRoutingSampler](https://github.com/open-telemetry/opentelemetry-java-contrib/blob/main/samplers/src/main/java/io/opentelemetry/contrib/sampler/RuleBasedRoutingSampler.java),
[Stratified Sampling](https://github.com/open-telemetry/opentelemetry-dotnet/tree/main/docs/trace/stratified-sampling-example),
LinksBasedSampler [for Java](https://github.com/open-telemetry/opentelemetry-java-contrib/blob/main/samplers/src/main/java/io/opentelemetry/contrib/sampler/LinksBasedSampler.java)
and [for DOTNET](https://github.com/open-telemetry/opentelemetry-dotnet/tree/main/docs/trace/links-based-sampler)).
Also, historically, some Span categorization was introduced by [JaegerRemoteSampler](https://www.jaegertracing.io/docs/1.54/sampling/#remote-sampling).

This proposal aims at generalizing these ideas, and at providing a bit more formal specification for the behavior of the composite samplers.
