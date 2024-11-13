# Move OTEPS to the Specification repository

Let's move OTEP documentation and PRs back into the [Specification](https://github.com/open-telemetry/opentelemetry-specification) repository.

## Motivation

Moving OTEPs back into the specification solves two main issues:

- Maintaining its tooling infrastructure (currently woefully out of date)
- Bringing it into the existing triage and voting process currently within the
  Specification.

## Explanation

Originally, OTEPs were kept as a separate repository to keep disjoint/disruptive designs as a separate repository.  There are a few differences between a normal PR and an OTEP:

- OTEPs are expected to be directional and subject to change when actually entered into the specification.
- OTEPs require more approvals than specification PRs
- OTEPs have different PR worklfows (whether due to accidental omission or conscious decision), e.g. staleness checks, linting.

As OpenTelemetry is stabilizing, the need for OTEPs to live outside the specification is growing less, and we face challenges like:

- Keeping OTEP tooling up to date
- Advertising the repositories existence
  - New contributors to OpenTelemetry often can't find recorded decision that exist in OTEPs.
  - Getting reviews from folks used to checking the Specification repository, but not the less-frequently-worked-on OTEP repository.

To solve these, let's move OTEPs into a directory within the [specification repository](https://github.com/open-telemetry/opentelemetry-specification).
We would also update all tooling and expected reviews to match existing standards for OTEPs.  Given the maintainers of OTEPs are the same as
maintainers of the specification, this should not change the bar for acceptance.

## Internal details

The following changes would occur:

- The following files would be moved to the specification repo:
  - `text/` directory -> `oteps/text/`
  - `0000-template.md` -> `oteps/0000-template.md`
- Update the specification `Makefile` to include linting, spell checking, link checking and TOC-ing the oteps directory.
- A one-time cleanup of OTEP markdown upon import to the specification repository.
- Close existing OTEP PRs and ask folks to reopen against the specification repository.
- New labels within the specification repository to tag OTEPs, including automation to set these on PR open.
- Updating contributing guidelines to include a section about OTEPs.
- Add `oteps/README.md` file outlining that OTEPS are not normative and part of enhancement proposal process.
- Add disclaimer to the header of every OTEP that the contents are not normative and part of the enhancement proposal process.

## Trade-offs and mitigations

Moving into the specification repository DOES mean that we would have a directory with a different quality bar and, somewhat, process than the rest of the repository.
This can be mitigated through the use of clear, vibrant labels for OTEPS, and updating process guidelines for the specification repository to retain the important
aspects of the current OTEP status.

## Prior art and alternatives

OTEPs were originally based on common enhancement proposal processes in other ecosystems, where enhancements live outside core repositories and follow a more rigorous criteria and evaluation. We are finding this
problematic for OpenTelemetry for reasons discussed above. Additionally, unlike many other ecosystems where enhancement/design is kept separate from core code, OpenTelemetry *already* keeps its design separate
form core code via the Specification vs. implementation repositories. Unlike these other OSS projects, our Specification generally requires rigorous discussion, design and prototyping prior to acceptance.  Even
after acceptance into the specification, work is still required for improvements to roll out to the ecosystem. Effectively: The OpenTelemetry specification has no such thing as a "small" change: There are only medium changes that appear small, but would be enhancements in other proejcts or large changes that require an OTEP.

## Open questions

What are the important portions of the OTEP process to bring over? Have we missed anything in this description?

## Future possibilities

In the future, we could figure out how to make OTEPs more searchable, discoverable and highlighted within the opentelemetry.io website.

Additionally, we can look at extending staleness deadlines for OTEP labeled PRs.
