# Semantic conventions for Feature Flags

**Status**: [Experimental](../../document-status.md)

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [Motivation](#motivation)
- [Overview](#overview)
- [Convention](#convention)
- [Example](#example)

<!-- tocstop -->

## Motivation

Features flags are commonly used in modern applications to decouple feature releases from deployments.
Many feature flagging tools support the ability to update flag configurations in near real-time from a remote feature flag management service.
They also commonly allow rulesets to be defined that return values based on contextual information.
For example, a feature could be enabled only for a specific subset of users based on context (e.g. users email domain, membership tier, country).

Since feature flags are dynamic and affect runtime behavior, it's important to collect relevant feature flag telemetry signals.
This can be used to determine the impact a feature has on a request, enabling enhanced observability use cases, such as A/B testing or progressive feature releases.
Depending on the implementation, flag evaluations may occasionally block on an I/O operation, making the timing information collected by a span valuable.

## Overview

The following semantic convention defines how feature flags can be represented as a span in OpenTelemetry.
The terminology was defined in the [OpenFeature specification](https://docs.openfeature.dev/docs/specification/), which represents an industry consensus.
It's intended to be vendor neutral and provide flexibility for current and future use cases.

## Convention

**Span kind:** MUST always be `INTERNAL`.

A typical flag evaluation span will have no children unless the flag evaluation itself performs additional operations (e.g. HTTP request, File system operation).

The **span name** SHOULD be of the format `<feature_flag.provider_name> <feature_flag.key>` provided that `feature_flag.provider_name` is available. If `feature_flag.provider_name` is not available, the span SHOULD be named `Feature Flag <feature_flag.key>`.

<!-- semconv feature_flag -->

| Attribute                    | Type   | Description                                                  | Examples                     | Requirement Level           |
| ---------------------------- | ------ | ------------------------------------------------------------ | ---------------------------- | --------------------------- |
| `feature_flag.key`           | string | The unique identifier of the feature flag.                   | `logo-color`                 | Required                    |
| `feature_flag.provider_name` | string | The name of the service that performs the flag evaluation.   | `Flag Manager`               | Recommended                 |
| `feature_flag.variant`       | string | The human readable name that identifies the evaluated value. | `red`; `blue`; `green`       | Conditionally Required: [1] |
| `feature_flag.value`         | string | A string representation of the evaluated value.              | `ff0000`; `0000ff`; `00ff00` | Conditionally Required: [2] |

**[1]:** A variant should be used if it is available. If the variant is present, feature_flag.value should be omitted.

**[2]:** The value should only be used if the variant is not available. How the value is represented as a string should be determined by the implementer.

<!-- endsemconv -->

## Example

The following example shows how a feature flag span can be represented on a trace.

In this scenario, developers are updating an endpoint which returns the n-th number in the Fibonacci sequence.
They want to monitor the impact of this updated algorithm on the system.
After a GET request is made to `/fib`, a feature flag with the key `fib-algo-name` determines which algorithm is used during this calculation.
This feature flag is evaluated by a feature flagging service called `Flag Manager`, which returns the new algorithm only for internal test users.
The span `Flag Manager fib-algo-name` has the attribute `feature_flag.value`, which represents the algorithm that was run during this request.
This span information can then be used to understand the impact that a flag(s) had on a request and to determine whether a new feature should be rolled out to a more general audience.

```
┌───────────────────────────────────────────────────────┐
│ GET /fib                                              │
└───────────────────────────────────────────────────────┘
  ┌────────────────────────────┐ ┌───────────────────┐
  │ Flag Manager fib-algo-name │ │ GET /calcFib      │
  └────────────────────────────┘ └───────────────────┘
```

> NOTE: The `Flag Manager fib-algo-name` and `GET /calcFib` spans are children of `GET /fib`.
