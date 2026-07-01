# Releasing

1. Prepare a [draft release](https://github.com/open-telemetry/opentelemetry-specification/releases).
   Do not publish it yet.
2. Run the [opentelemetry.io workflow](https://github.com/open-telemetry/opentelemetry.io/actions/workflows/build-dev.yml)
   against the `opentelemetry-specification` submodule as a smoke test. Fix any
   broken links and confirm with the Communications SIG (`#otel-comms`).
   Re-confirm after any new PRs merge into the release PR.
3. Update [CHANGELOG.md](CHANGELOG.md):
   - Rename the existing `Unreleased` section to the new version (e.g. `1.50.0`),
     removing any empty subsections.
   - Add a new `Unreleased` section at the top with empty subsections.
   - Verify no entries are missing or in the wrong section.
4. Copy the changelog entries into the draft release description and un-draft it.
5. Once approved, confirm the date in the CHANGELOG is current, then merge to
   create the release tag (e.g. `v1.50.0`).

The release is auto-discovered by [opentelemetry.io](https://github.com/open-telemetry/opentelemetry.io)
pipelines, which will publish the new specification version via a bot-generated PR.
