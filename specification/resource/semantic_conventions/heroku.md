# Heroku

**Status**: [Experimental](../../document-status.md)

**type:** `heroku`

**Description:** Heroku dyno metadata [1]

<!-- semconv cloud -->
| Attribute                         | Type   | Description                           | Examples                                | Requirement Level |
|-----------------------------------|--------|---------------------------------------|-----------------------------------------|-------------------|
| heroku.release.version            | string | Identifier for the current release    | `v42`                                   | Recommended       |
| heroku.release.creation_timestamp | string | Time and date the release was created | `2022-10-23T18:00:42Z`                  | Recommended       |
| heroku.release.commit             | string | Commit hash for the current release   | `e6134959463efd8966b20e75b913cafe3f5ec` | Recommended       |
| heroku.app.name                   | string | Application name                      | `foo-app`                               | Recommended       |
| heroku.app.id                     | string | Unique identifier for the application | `2daa2797-e42b-4624-9322-ec3f968df4da`  | Recommended       |
| heroku.dyno.id                    | string | Dyno identifier. Used as host name    | `2vac3221-f56c-1897-4453-ba4d8638c1ac`  | Recommended       |

[1]: https://devcenter.heroku.com/articles/dyno-metadata