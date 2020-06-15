# General

The conventions described in this section are generic; they are not specific to a
particular operation.

## Summarizing timed operations

Timed operations that may be more fully described by Spans can be summarized by three
metrics: `throughput`, `duration`, and `errors`.
The name of these metrics should be namespaced with the Span category and the Span
kind.

| Name                               | Type            |
| ----                               | ----            |
|`{category}.{span.kind}.throughput` | `Counter`       |
|`{category}.{span.kind}.duration`   | `ValueRecorder` |
|`{category}.{span.kind}.errors`     | `Counter`       |

### throughput

The throughput metric represents the total number of operations that occur.
For each timed operation that occurs, the value of the `throughput` metric should be
incremented by 1.

### duration

The duration metric represents the total duration of all operations that occur.
For each timed operation, the value of the `duration` metric should be incremented by
the duration of the operation in milliseconds.

### errors

The `errors` metric represents the total number of operations that failed.
For each timed operation that failed, the value of the `errors` metric should be
incremented by 1.

### Naming examples

A simple HTTP service would create three metrics:

* `http.server.throughput`
* `http.server.duration`
* `http.server.errors`

If this service also calls out to other HTTP services, it would create three additional metrics:

* `http.client.throughput`
* `http.client.duration`
* `http.client.errors`

If this service also queries one or more databases, it would create three additional metrics:

* `db.client.throughput`
* `db.client.duration`
* `db.client.errors`
