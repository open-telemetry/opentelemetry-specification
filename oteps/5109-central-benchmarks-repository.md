# A Central OpenTelemetry Benchmarks Repository

Establish a project-owned `open-telemetry/benchmarks` repository that
hosts cross-language scenario definitions, runs them on language
implementation releases, and publishes a historical dashboard. The scope
is intentionally limited to a single scenario and at least two language
harnesses; further scenarios and languages can be added incrementally in
the new repository.

## Motivation

The specification already contains performance-related guidance:

- [`specification/performance-benchmark.md`](../specification/performance-benchmark.md)
  defines a span-throughput methodology, CPU and memory measurement
  guidance, and a reporting format.

This document has not resulted in cross-language benchmarking outcomes
to date. It is span-only, predates the metrics and logs signals, and
does not define a central place where the resulting numbers are
reported, compared, or tracked over time. Each language implementation
that benchmarks itself does so in its own repository, with its own
methodology, in its own format. There is no equivalent of the
[spec compliance matrix](../spec-compliance-matrix.md) for performance.

The project's own [engineering values](https://opentelemetry.io/community/mission/)
state that "high performance is a requirement for OpenTelemetry", yet
there is no project-wide mechanism to track it. Both
[`metrics/api.md`](../specification/metrics/api.md) and
[`trace/api.md`](../specification/trace/api.md) require the API to be a
no-op when no SDK is configured, but the project has no shared evidence
that every implementation satisfies this requirement, nor cross-release
visibility into how the cost of that path evolves over time.

## Explanation

A new repository, `open-telemetry/benchmarks`, is created under the
project organization. It contains:

1. Scenario definitions any language implementation can implement in a consistent manner.
2. A GitHub Actions workflow that runs language-specific harnesses (one
   per scenario, per language) and publishes results.
3. A historical record of results per scenario, per language, per
   release.
4. A GitHub Pages dashboard of release-over-release trends.

This repository is a trend tracker, not a regression-detection CI.
Per-commit and nightly regression detection belongs in each language
implementation's own repository, where the maintainers control the
cadence, the thresholds, and the response to a failed run. The
dashboard proposed here records one data point per tracked release of
each participating implementation; its purpose is cross-release
visibility, not gating individual changes.

### The initial scenario

Scenario S1: counter increment with a stable attribute set, API-only.

- Depends only on the OTel API package; no SDK package is referenced or
  loaded.
- The benchmark increments a `Counter` instrument by 1 in a tight loop
  with the same attribute values on every call. The attribute set uses
  three string attributes, for example:
  - `http.request.method` = `"GET"`
  - `url.scheme` = `"https"`
  - `server.address` = `"example.com"`
- Single-threaded (one OS thread); async or coroutine-style code is
  fine where idiomatic. Multi-threaded and contended variants are
  deferred to follow-up scenarios.
- Reported metrics per run:
  - `ns/op` (median).
  - `allocations/op` (heap allocations per operation), where the
    language exposes it; bytes/op optional.

S1 is chosen as the first scenario because:

1. It exercises an existing normative requirement (the
   [API no-op requirement](../specification/metrics/noop.md)), so no new
   specification language is needed to justify it.
2. OpenTelemetry's goal is native instrumentation in every library and
   framework. The first question a library owner will ask is "what does
   this cost when no SDK is configured?" — a high no-op cost directly
   slows down the library itself. A publicly tracked, per-release
   answer to that question removes a key adoption blocker.

### Initial languages

The initial rollout requires harnesses for Scenario S1 in at least two
languages. Specific languages are not fixed by this OTEP; whichever
maintainers contribute first count toward the minimum, and further
languages can be added later without their own OTEP.

## Internal details

### Repository layout

```text
open-telemetry/benchmarks/
├── README.md
├── scenarios/
│   └── S1-counter-increment-api-only.md
├── harnesses/
│   └── <language>/
├── .github/workflows/
│   └── run-benchmark.yml
└── docs/
```

### Update cadence

Each language harness pins the SDK package version it benchmarks in its
own manifest (`csproj`, `Cargo.toml`, `build.gradle`, etc.), checked
into the repository. A bot such as
[Dependabot](https://docs.github.com/en/code-security/dependabot) or
[Renovate](https://docs.renovatebot.com/) watches the corresponding
package registry and opens a pull request whenever the tracked SDK
publishes a new release. Merging that pull request triggers the
benchmarks workflow on the bare-metal runner and appends the resulting
data point to the dashboard. No cross-repository permissions are
needed; the trigger lives entirely inside the benchmarks repository.

`workflow_dispatch` remains supported as an escape hatch for ad-hoc
runs (backfill, comparing the same SDK on two runtime versions,
re-running a stale point). If a release alters the API the harness
uses, the bump pull request needs manual maintainer attention; this is
expected to be rare since scenarios target stable APIs.

When onboarding, an implementation should backfill at least two prior
tracked releases so the dashboard starts with a trend rather than a
single point.

### Execution environment

Benchmark runs use the OpenTelemetry project's existing shared
self-hosted bare-metal runner, already used by other OTel benchmark
workflows and documented in
[`open-telemetry/community/docs/how-to-provision-bare-metal-runner.md`](https://github.com/open-telemetry/community/blob/main/docs/how-to-provision-bare-metal-runner.md).
The benchmarks repository needs to be added to the set of repositories
authorized to use it, following the process in
[`how-to-use-bare-metal-runner.md`](https://github.com/open-telemetry/community/blob/main/docs/how-to-use-bare-metal-runner.md#request-access)
(open an issue in `open-telemetry/community` requesting access). No new
infrastructure is required.

Each data point records environment metadata (runner, runtime, OS,
benchmark tool versions) so shifts caused by environment rather than
the implementation can be identified.

### Tooling choice

[`benchmark-action/github-action-benchmark`](https://github.com/benchmark-action/github-action-benchmark)
is one viable option, already used by `opentelemetry-rust`, `otel-arrow`,
and the OpenTelemetry Collector to publish benchmark trends. This OTEP
does not commit to a specific tool; the exit criteria below require a
public dashboard with historical results, not a particular
implementation.

### Exit criteria for the initial rollout

The initial rollout established by this OTEP is complete when all of the
following are true:

1. `open-telemetry/benchmarks` exists, with the layout above and a
   `CODEOWNERS` defining ownership. Ownership follows the same model as
   [`opentelemetry.io`](https://github.com/open-telemetry/opentelemetry.io):
   each per-language harness subfolder is owned by the approvers of the
   corresponding language implementation; shared content (scenarios,
   workflows, top-level docs) is owned by the repository's top-level
   maintainers.
2. Scenario S1 is documented such that any language implementation can
   produce a conforming harness from the document alone.
3. Harnesses for S1 exist in at least two languages, merged and
   runnable.
4. The benchmark workflow has run S1 on at least one tracked release
   from at least one participating language and the resulting data
   point appears on the dashboard.
5. The dashboard is publicly visible on GitHub Pages and shows at least
   one data point per participating language for the most recent release
   of each.

### Out of scope

The following are explicitly not part of the work proposed here and
should not be conflated with it in review:

- Scenarios other than S1.
- Per-commit or nightly regression-detection CI. That responsibility
  remains with each language implementation's own repository; the
  dashboard proposed here records one data point per tracked release of
  each implementation and is intended for release-over-release trend
  visibility, not for gating individual changes.
- Replacing or deprecating
  [`specification/performance-benchmark.md`](../specification/performance-benchmark.md).
  That document remains; this repository provides the central reporting
  location it does not.

Each of the above is reasonable follow-up work and is sketched in
[Future possibilities](#future-possibilities).

## Trade-offs and mitigations

- A dashboard covering only the initial participating languages is not
  representative of every language implementation. The repository and
  scenario format should be designed for any implementation to add a
  harness on its own schedule. The README will state that the dashboard
  reflects participating implementations only and is not a ranking. The
  dashboard plots one trend chart per language rather than side-by-side
  comparisons, to keep per-implementation evolution the primary view.
- S1 exercises only the metrics API. Equivalent API-only scenarios for
  span creation and log emission are reasonable follow-up work and are
  listed under [Future possibilities](#future-possibilities).

## Prior art and alternatives

- [`specification/performance-benchmark.md`](../specification/performance-benchmark.md)
  — existing methodology document with no central reporting location.
  This OTEP provides that location.
- [spec-compliance-matrix](../spec-compliance-matrix.md) — the conformance
  analogue this OTEP is the performance equivalent of.
- [opentelemetry-rust-contrib#548 review thread](https://github.com/open-telemetry/opentelemetry-rust-contrib/pull/548#discussion_r2850585180)
  — example of a "no-op path" doing meaningful work, illustrating the
  kind of behavior a release-over-release trend view would surface.

Alternatives considered:

- Federated model: each language repo runs the shared scenarios itself
  and pushes results to a central dashboard, with no central harness
  code. Not chosen because maintaining consistent CI configurations
  across N repositories has more overhead than hosting everything in
  one place.

## Open questions

- Top-level repository ownership. Per-language harness subfolders are
  owned by that language implementation's approvers (as in
  `opentelemetry.io`); proposed interim maintainers for shared content
  and repository ownership are Cijo Thomas (@cijothomas, Microsoft) and
  Martin Costello (@martincostello, Grafana Labs), until a long-term owner is chosen (for example a new
  Performance SIG, the Spec Sponsors, or the TC).

## Prototypes

A working prototype of the model described in this OTEP is available at
<https://github.com/cijothomas/otel-benchmarks>, with a live dashboard
at <https://cijothomas.github.io/otel-benchmarks/>. It exercises
Scenario S1 across .NET, Rust, and Java using each language's native
benchmarking framework (BenchmarkDotNet, Criterion, JMH), publishes
results through a unified schema, and records per-data-point
environment metadata (runner image, runtime version, CPU model, kernel
version, benchmark framework version). The prototype is hosted under a
personal account, runs on shared GitHub-hosted CI runners, and is
intended only to demonstrate the end-to-end shape of the proposed
model — not to publish authoritative performance numbers.

## Future possibilities

The following items are deliberately not part of this OTEP and are listed
here as a non-binding sketch of plausible follow-up work:

- Expand scenarios to cover additional signals (spans, logs), SDK
  fast-path operations (sampling, aggregation), and multi-threaded or
  contended workloads.
- Onboard additional languages beyond those contributed during the
  initial rollout.
