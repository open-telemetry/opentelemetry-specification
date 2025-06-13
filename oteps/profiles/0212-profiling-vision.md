# Propose OpenTelemetry profiling vision

The following are high-level items that define our long-term vision for
Profiling support in the OpenTelemetry project that we aspire to achieve.

While this vision document reflects our current desires, it is meant to be a
guide towards a collectively agreed upon set of objectives rather than a
checklist of requirements. A group of OpenTelemetry community members have
participated in a series of bi-weekly meetings for 2 months. The group
represents a cross-section of industry and domain expertise, who have found
common cause in the creation of this document.  It is our shared intention to
continue to ensure alignment moving forward. As our vision evolves and matures,
we intend to incorporate our learnings further to facilitate an optimal outcome.

This document and efforts thus far are motivated by:

- This [long-standing issue](https://github.com/open-telemetry/oteps/issues/139)
  created in October 2020
- A conversation about priorities at the in-person OpenTelemetry meeting at Kubecon EU
  2022
- Increasing community interest in profiling as an observability signal
  alongside logs, metrics, and traces

## What is profiling

While the terms "profile" and "profiling" can have slightly different meanings
depending on the context, for the purposes of this OTEP we are defining the two
terms as follows:

- Profile: A collection of stack traces with some metric associated with each
  stack trace, typically representing the number of times that stack trace was
  encountered
- Profiling: The process of collecting profiles from a running program,
  application, or the system

## How profiling aligns with the OpenTelemetry vision

The [OpenTelemetry
vision](https://opentelemetry.io/community/mission/#vision-mdash-the-world-we-imagine-for-otel-end-users)
states:

_Effective observability is powerful because it enables developers to innovate
faster while maintaining high reliability. But effective observability
absolutely requires high-quality telemetry – and the performant, consistent
instrumentation that makes it possible._

While existing OpenTelemetry signals fit all of these criteria, until recently
no effort has been explicitly geared towards creating performant and consistent
instrumentation based upon profiling data.

## Making a well-rounded observability suite by adding profiling

Currently Logs, Metrics, and Traces are widely accepted as the main “pillars” of
observability, each providing a different set of data from which a user can
query to answer questions about their system/application.

Profiling data can help further this goal by answering certain questions about a
system or application which logs, metrics, and traces are less equipped to
answer. We aim to facilitate implementations capable of best-in-class support
for collecting, processing, and transporting this profiling data.

Our goals for profiling align with those of OpenTelemetry as a whole:

- **Profiling should be easy**: the nature of profiling offers fast
  time-to-value by often being able to optionally drop in a minimal amount of
  code and instantly have details about application resource utilization
- **Profiling should be universal**: currently profiling is slightly different
  across different languages, but with a little effort the representation of
  profiling data can be standardized in a way where not only are languages
  consistent, but profiling data itself is also consistent with the other
  observability signals as well
- **Profiling should be vendor neutral**: From one profiling agent, users should
  be able to send data to whichever vendor they like (or no vendor at all) and
  interoperate with other OSS projects

## Current state of profilers

As it currently stands, the method for collecting profiles for an application
and the format of the profiles collected varies greatly depending on several
factors such as:

- Language (and language runtime)
- Profiler Type
- Data type being profiled (i.e. cpu, memory, etc)
- Availability or utilization of symbolic information

A fairly comprehensive taxonomy of various profiling formats can be found on the
[profilerpedia website](https://profilerpedia.markhansen.co.nz/formats/).

As a result of this variation, the tooling and collection of profiling data
lacks in exactly the areas in which OpenTelemetry has built as its core
engineering values:

- Profiling currently lacks compatibility: Each vendor, open source project, and
  language has different ways of collecting, sending, and storing profiling data
  and often with no regard to linking to other signals
- Profiling currently lacks consistency: Currently profiling agents and formats
  can change arbitrarily with no unified criteria for how to take end-users into
  account

## Making profiling compatible with other signals

Profiles are particularly useful in the context of other signals. For example,
having a profile for a particular “slow” span in a trace yields more actionable
information than simply knowing that the span was slow.

OpenTelemetry will define how profiles will be correlated with logs, traces, and
metrics and how this correlation information will be stored.

Correlation will work across 2 major dimensions:

- To correlate telemetry emitted for the same request (also known as request or
  trace context correlation)
- To correlate telemetry emitted from the same source (also known as resource
  context correlation)

## Standardize profiling data model for industry-wide sharing and reuse

We will design a profiling data model that will aim to represent the vast
majority of profiling data with the following goals in mind:

- Profiling formats should be as compact as possible
- Profiling data should be transferred as efficiently as possible and the model
  should be lossless with intentional bias for enabling efficient marshaling,
  transcoding (to and from other formats), and analysis
- Profiling formats should be able to be unambiguously mapped to the
  standardized data model (i.e. collapsed, pprof, JFR, etc.)
- Profiling formats should contain mechanisms for representing relationships
  between other telemetry signals (i.e. linking call stacks with spans)

## Supporting legacy profiling formats

For existing profilers we will provide instructions on how these legacy formats
can emit profiles in a manner that makes them compatible with OpenTelemetry’s
approach and enables telemetry data correlation.

Particularly for popular profilers such as the ones native to Golang and Java
(JFR) we will help to have them produce OpenTelemetry-compatible profiles with
minimal overhead.

## Performance considerations

Profiling agents can be architected in a variety of differing ways, with
reasonable trade offs made that may impact performance, completeness, accuracy
and so on. Similarly, the manner in which such a profiler might produce or
consume OpenTelemetry-compatible data could vary significantly. As such, in our
standardization effort it is not feasible to be prescriptive on the matter of
resource usage for profilers.

However, the output of OpenTelemetry's standardization effort must take into
account that some existing profilers are designed to be low overhead and high
performance. For example, they may operate in a whole-datacenter, always-on
manner, and/or in environments where they must guarantee low CPU/RAM/network
usage. The OpenTelemetry standardisation effort should take this into account
and strive to produce a format that is usable by profilers of this nature
without sacrificing their performance guarantees.

Similar to other OpenTelemetry signals, we target production environments. Thus, the
profiling signal must be implementable with low overhead and conforming to
OpenTelemetry-wide runtime overhead / intrusiveness and wire data size requirements.

## Promoting cloud-native best practices with profiling

The CNCF’s mission states: _Cloud native technologies empower organizations to
build and run scalable applications in modern, dynamic environments such as
public, private, and hybrid clouds_

We will have best-in-class support for profiles emitted in cloud native
environments (e.g. Kubernetes, serverless, etc), including legacy applications
running in those environments. As we aim to achieve this goal we will center our
efforts around making profiling applications resilient, manageable and
observable.  This is in line with the Cloud Native Computing Foundation and
OpenTelemetry missions and will thus allow us to further expand and leverage
those communities to further the respective missions.

## Profiling use cases

- Tracking resource utilization of an application over time to understand how
  code changes, hardware configuration changes, and ephemeral environmental
  issues influence performance
- Understanding what code is responsible for consuming resources (i.e. CPU, Ram,
  disk, network)
- Planning for resource allotment for a group of services running in production
- Comparing profiles of different versions of code to understand how code has
  improved or degraded over time
- Detecting frequently used and "dead" code in production
- Breaking a trace span into code-level granularity (i.e. function call and line
  of code) to understand the performance for that particular unit
