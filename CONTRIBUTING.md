# Contributing

Welcome to OpenTelemetry specifications repository!

Before you start - see OpenTelemetry general
[contributing](https://github.com/open-telemetry/community/blob/main/guides/contributor/README.md)
requirements and recommendations.

## Sign the CLA

Before you can contribute, you will need to sign the [Contributor License
Agreement](https://easycla.lfx.linuxfoundation.org/).

## Proposing a Change

### Trivial Changes

_Examples: fixing a typo, rewording a sentence for clarity, correcting a
broken link._

Clarifications, wording, spelling/grammar, and formatting fixes can be made
directly via pull request with no associated issue.

### Smaller Changes

_Examples: defining a new term, adding a new optional parameter to an existing
API, stabilizing an existing feature, tightening a SHOULD to a MUST._

[Create an issue](https://github.com/open-telemetry/opentelemetry-specification/issues/new/choose)
describing the proposed change and wait for acceptance before opening a PR.
If the issue is not accepted, the PR will be rejected. See
[issue-management.md](./issue-management.md) for the full issue lifecycle,
triage labels, and role definitions.

A [Draft PR](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests#draft-pull-requests)
may be opened alongside the issue to illustrate the idea before it is accepted.

The PR description must include links to prototypes:

- For new features at Development maturity level, a prototype is required. It
  should be a working demonstration in a spec-bound implementation with that
  SIG's maintainers' support (e.g. an unmerged PR with stated intent to merge
  if the spec PR is merged).
- Before a feature can be stabilized, prototypes in multiple languages are
  required. The number is at the discretion of the [spec maintainers][spec-maintainers],
  though three is typical.

If the change adds or modifies SDK component configuration, the PR must link
to a corresponding proposed change to the
[declarative configuration schema](https://github.com/open-telemetry/opentelemetry-configuration).
These PRs should be approved and merged together.

### Significant Changes

_Examples: new metric types (e.g. [exponential histograms](./oteps/0149-exponential-histogram.md)),
new signals (e.g. [Events and Logs API](./oteps/0202-events-and-logs-api.md)),
new cross-cutting systems (e.g. [declarative configuration](./oteps/0225-configuration.md))._

Significant changes should go through the [OpenTelemetry Enhancement
Proposal](./oteps/README.md) process. See the OTEP README for guidance on what
changes require an OTEP.

## When an Issue Is Closed

If you opened an issue and later found it closed, please don't read it as a sign
that we didn't value it. We read every issue, and closing an issue is not meant to dismiss you.

### Why was my issue closed?

Unfortunately, we can't always act on every request. Proposals may conflict with one another,
a proposal would pull the specification in a direction it can't go right now,
we may have to make a call between competing proposals or it is not possible to reach
consensus among a large group of maintainers that cover a lot of domains.

You can often tell _why_ an issue was closed from its `triage:rejected:*` label
(for example `duplicate`, `out-of-scope`, or `insufficient-info`). See
[issue-management.md](./issue-management.md) for what each label means.

### A closed issue is not a deleted issue

Closing an issue only changes its status. The discussion, the
context, and your idea all stay on GitHub, and we can reopen an issue at any time
if circumstances change or new information comes to light. Closed issues have been
reopened before.

### We're human, and we sometimes get it wrong

Triage is done by people, and people make mistakes. If you think your issue was
closed in error, or that it deserves another look, please say so. You can comment
on the issue or reach out in the
[#otel-specification](https://cloud-native.slack.com/archives/C01N7PP1THC)
channel on CNCF Slack. If you are new to the CNCF Slack community, you can
[create an account](https://slack.cncf.io/). We try to be reasonable and we're
always glad to reconsider.

### Please keep contributing

However your particular issue turns out, we hope you'll stick around. Your input
makes OpenTelemetry better, and we'd love to see your next issue, comment, or
pull request. Thank you for being part of the community.

## Writing Specs

Specification is written in Markdown. Please make sure files render correctly
on GitHub. We highly encourage line breaks at 80 characters wide — there are
editor tools that can do this automatically. Please submit a proposal to include
your editor settings so the out-of-the-box configuration for this repository
stays consistent.

Clearly define requirements using the keywords defined in [Notation Conventions
and Compliance](./specification/README.md#notation-conventions-and-compliance),
while heeding the guidance in [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119)
about sparing use of imperatives:

> Imperatives of the type defined in this memo must be used with care and
> sparingly. In particular, they MUST only be used where it is actually required
> for interoperation or to limit behavior which has potential for causing harm
> (e.g., limiting retransmissions). For example, they must not be used to try
> to impose a particular method on implementors where the method is not required
> for interoperability.

It is important to build a specification that is clear and useful, not one that
is needlessly restrictive and complex.

Please see [Specification Principles](specification/specification-principles.md)
for more information.

## Tooling

Install the latest LTS release of [Node.js](https://nodejs.org/) and run
`npm install` before using any of the targets below. For example, using
[nvm][] under Linux:

```bash
nvm install --lts
```

[nvm]: https://github.com/nvm-sh/nvm/blob/master/README.md#installing-and-updating

### Checks

Run all checks (spell, lint, style, links):

```bash
make check
```

> [!NOTE]
> Link checking requires Docker and can take a long time. Run it before
> submitting a PR.

Run checks individually:

```bash
make language-analysis  # spell (cspell) and prose (textlint)
make markdownlint       # Markdown style
make markdown-link-check # link validity (requires Docker)
```

See [markdownlint](.markdownlint.yaml) for the full rule set.

### Autofixes

```bash
make fix          # fix textlint violations
make markdown-toc # regenerate tables of contents
```

To fix markdownlint violations, use the
[Visual Studio Code markdownlint extension](https://github.com/DavidAnson/vscode-markdownlint)
`fixAll` command, or follow the
[markdownlint instructions](https://github.com/igorshubovych/markdownlint-cli#fixing-issues).

### Compliance Matrix

To update the [compliance matrix](./spec-compliance-matrix.md), edit the
language YAML file in `spec-compliance-matrix/` (e.g. `go.yaml`, `java.yaml`)
and regenerate:

```bash
make compliance-matrix
```

Compliance matrix updates do not require a CHANGELOG entry. Use a `chore:`
prefix in the PR title (e.g., `chore: Update .NET compliance matrix`).

## Pull Requests

A PR is **ready to merge** when:

- It has received two or more approvals from [code owners][code-owners],
  with approvals from at least two companies.
- There are no outstanding `request changes` from [code owners][code-owners].
- It has been at least two working days since the last modification (not required
  for trivial changes such as typos, cosmetic fixes, or rebases).
- For non-trivial changes, the `Unreleased` section of
  [CHANGELOG.md](./CHANGELOG.md) has been updated under the appropriate
  subsection.

Any [spec maintainer][spec-maintainers]
can merge a PR that is ready to merge. Maintainers may impose additional
requirements at their discretion (e.g. more approvals, waiting for a release).

If a PR is stuck, the owner should:

- Post a summary of open perspectives in the PR description.
- Tag relevant subdomain experts (check the change history).
- Raise it in the [#otel-specification](https://cloud-native.slack.com/archives/C01N7PP1THC)
  channel on CNCF Slack. If you are new to the CNCF Slack community,
  you can [create an account](https://slack.cncf.io/).
- Consider narrowing the scope or splitting the PR.

If still stuck after two weeks, bring it to the [OpenTelemetry Specification SIG
meeting](https://github.com/open-telemetry/community/blob/main/README.md#specification-sigs).

[spec-maintainers]: README.md#maintainers
[code-owners]: ./.github/CODEOWNERS
