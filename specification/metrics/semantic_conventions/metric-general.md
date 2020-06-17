# General

The conventions described in this section are generic; they are not specific to a
particular operation.

## Summarizing timed operations

Timed operations that may be more fully described by Spans can be summarized by a single [`ValueRecorder`](../api.md#valuerecorder) recording duration.  The instrument name should be prefixed with the Span category and kind.
The resulting name should look like `{category}.{span.kind}.duration`. See [examples](#examples) below.

For each operation being recorded, the duration of the operation **in milliseconds** should be recorded onto the `duration` instrument.

#### errors

The `duration` metric should include an `error` label indicating whether the operation failed.  The value of this label should be `true` if the operation ended in a failed state.

### Examples

A simple HTTP service would create the metric:

* `http.server.duration`

If this service also calls out to other HTTP services, it would create the additional metric:

* `http.client.duration`

If this service also queries one or more databases, it would create the additional metric:

* `db.client.duration`

All of these metrics would include labels
  * `error=true`
  * `error=false`
