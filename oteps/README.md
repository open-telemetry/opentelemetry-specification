# OpenTelemetry Enhancement Proposal (OTEP)

## Evolving OpenTelemetry at the speed of Markdown

OpenTelemetry uses an "OTEP" (similar to a RFC) process for proposing changes to the OpenTelemetry Specification.

> [!NOTE]
> OTEPs are documents of intent. They become requirements only after their contents have been
> [integrated](#integrating-the-otep-into-the-spec) into the actual [Specification](../specification).

### Table of Contents

- [OpenTelemetry Enhancement Proposal (OTEP)](#opentelemetry-enhancement-proposal-otep)
  - [Evolving OpenTelemetry at the speed of Markdown](#evolving-opentelemetry-at-the-speed-of-markdown)
    - [Table of Contents](#table-of-contents)
    - [What changes require an OTEP](#what-changes-require-an-otep)
      - [Extrapolating cross-cutting changes](#extrapolating-cross-cutting-changes)
    - [OTEP scope](#otep-scope)
    - [Writing an OTEP](#writing-an-otep)
    - [Submitting the OTEP](#submitting-the-otep)
    - [Integrating the OTEP into the Spec](#integrating-the-otep-into-the-spec)
    - [Implementing the OTEP](#implementing-the-otep)
  - [Changes to the OTEP process](#changes-to-the-otep-process)
  - [Background on the OpenTelemetry OTEP process](#background-on-the-opentelemetry-otep-process)

### What changes require an OTEP

The OpenTelemetry OTEP process is intended for changes that are **cross-cutting** - that is, applicable across *languages* and *implementations* - and either **introduce new behaviour**, **change desired behaviour**, or otherwise **modify requirements**.

In practice, this means that OTEPs should be used for such changes as:

- New tracer configuration options
- Additions to span data
- New metric types
- Modifications to extensibility requirements

On the other hand, they do not need to be used for such changes as:

- Bug fixes
- Rephrasing, grammatical fixes, typos, etc.
- Refactoring
- Things that affect only a single language or implementation

**Note:** The above lists are intended only as examples and are not meant to be exhaustive. If you don't know whether a change requires an OTEP, please feel free to ask!

#### Extrapolating cross-cutting changes

Sometimes, a change that is only immediately relevant within a single language or implementation may be indicative of a problem upstream in the specification. We encourage you to add an OTEP if and when you notice such cases.

### OTEP scope

While OTEPs are intended for "significant" changes, we recommend trying to keep each OTEP's scope as small as makes sense. A general rule of thumb is that if the core functionality proposed could still provide value without a particular piece, then that piece should be removed from the proposal and used instead as an *example* (and, ideally, given its own OTEP!).

For example, an OTEP proposing configurable sampling *and* various samplers should instead be split into one OTEP proposing configurable sampling as well as an OTEP per sampler.

### Writing an OTEP

- First, [fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo) this repo.
- Copy [`0000-template.md`](./0000-template.md) to `0000-my-OTEP.md`, where `my-OTEP` is a title relevant to your proposal, and `0000` is the OTEP ID.
  Leave the number as is for now. Once a Pull Request is made, update this ID to match the PR ID.
- Fill in the template. Put care into the details: It is important to present convincing motivation, demonstrate an understanding of the design's impact, and honestly assess the drawbacks and potential alternatives.

### Submitting the OTEP

- An OTEP is `proposed` by posting it as a PR. Once the PR is created, update the OTEP file name to use the PR ID as the OTEP ID.
- An OTEP is `approved` when four reviewers github-approve the PR. The OTEP is then merged.
- If an OTEP is `rejected` or `withdrawn`, the PR is closed. Note that these OTEPs submissions are still recorded, as GitHub retains both the discussion and the proposal, even if the branch is later deleted.
- If an OTEP discussion becomes long, and the OTEP then goes through a major revision, the next version of the OTEP can be posted as a new PR, which references the old PR. The old PR is then closed. This makes OTEP review easier to follow and participate in.

### Integrating the OTEP into the Spec

- Once an OTEP is `approved`, an issue is created in this repo to integrate the OTEP into the actual spec.
- When reviewing the spec PR for the OTEP, focus on whether the spec is written clearly, and reflects the changes approved in the OTEP. Please abstain from relitigating the approved OTEP changes at this stage.
- An OTEP is `integrated` when four reviewers github-approve the spec PR. The PR is then merged, and the spec is versioned.

### Implementing the OTEP

- Once an OTEP is `integrated` into the spec, an issue is created in the backlog of every relevant OpenTelemetry implementation.
- PRs are made until the all the requested changes are implemented.
- The status of the OpenTelemetry implementation is updated to reflect that it is implementing a new version of the spec.

## Changes to the OTEP process

The hope and expectation is that the OTEP process will **evolve** with the OpenTelemetry. The process is by no means fixed.

Have suggestions? Concerns? Questions? **Please** raise an issue or raise the matter on our [community](https://github.com/open-telemetry/community) chat.

## Background on the OpenTelemetry OTEP process

Our OTEP process borrows from the [Rust RFC](https://github.com/rust-lang/rfcs) and [Kubernetes Enhancement Proposal](https://github.com/kubernetes/enhancements) processes, the former also being [very influential](https://github.com/kubernetes/enhancements/tree/master/keps/sig-architecture/0000-kep-process/README.md#prior-art) on the latter; as well as the [OpenTracing OTEP](https://github.com/opentracing/specification/blob/master/rfc_process.md) process. Massive kudos and thanks to the respective authors and communities for providing excellent prior art 💖

[slack-image]: https://img.shields.io/badge/Slack-4A154B?style=for-the-badge&logo=slack&logoColor=white
[slack-url]: https://cloud-native.slack.com/archives/C01N7PP1THC
