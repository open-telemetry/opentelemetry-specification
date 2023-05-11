# Heroku

**Status**: [Experimental](../../../document-status.md)

**NOTICE** Semantic Conventions are moving to a
[new location](http://github.com/open-telemetry/semantic-conventions).

No changes to this document are allowed.

**type:** `heroku`

**Description:** [Heroku dyno metadata]

<!-- semconv heroku -->
| Attribute  | Type | Description  | Examples  | Requirement Level |
|---|---|---|---|---|
| `heroku.release.creation_timestamp` | string | Time and date the release was created | `2022-10-23T18:00:42Z` | Opt-In |
| `heroku.release.commit` | string | Commit hash for the current release | `e6134959463efd8966b20e75b913cafe3f5ec` | Opt-In |
| `heroku.app.id` | string | Unique identifier for the application | `2daa2797-e42b-4624-9322-ec3f968df4da` | Opt-In |
<!-- endsemconv -->

**Mapping:**

| Dyno metadata environment variable | Resource attribute                  |
|------------------------------------|-------------------------------------|
| `HEROKU_APP_ID`                    | `heroku.app.id`                     |
| `HEROKU_APP_NAME`                  | `service.name`                      |
| `HEROKU_DYNO_ID`                   | `service.instance.id`               |
| `HEROKU_RELEASE_CREATED_AT`        | `heroku.release.creation_timestamp` |
| `HEROKU_RELEASE_VERSION`           | `service.version`                   |
| `HEROKU_SLUG_COMMIT`               | `heroku.release.commit`             |

Additionally, [the `cloud.provider` resource attribute MUST be set to `heroku`](../cloud.md).

[Heroku dyno metadata]: https://devcenter.heroku.com/articles/dyno-metadata
