# CloudEvents

**Status**: [Experimental](../../document-status.md)

This specification defines attributes for [CloudEvents](https://cloudevents.io/).
The attributes described in this document are not specific to a particular operation but rather generic. They may be used in any Span they apply to.

At this time, this specification does not cover:

- How and when Spans are created for CloudEvents

- Transport aspects of sending and receiving CloudEvents

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [Attributes](#attributes)

<!-- tocstop -->

## Attributes

<!-- semconv cloudevents -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `cloudevents.event_id` | string | The [event_id](https://github.com/cloudevents/spec/blob/master/spec.md#id) uniquely identifies the event. [1] | `123e4567-e89b-12d3-a456-426614174000`; `0001` | No |
| `cloudevents.event_source` | string | The [source](https://github.com/cloudevents/spec/blob/master/spec.md#source-1) identifies the context in which an event happened. | `https://github.com/cloudevents`; `/cloudevents/spec/pull/123`; `my-service` | No |
| `cloudevents.event_spec_version` | string | The [version of the CloudEvents specification](https://github.com/cloudevents/spec/blob/master/spec.md#specversion) which the event uses. | `1.0` | No |
| `cloudevents.event_type` | string | The [event_type](https://github.com/cloudevents/spec/blob/master/spec.md#type) contains a value describing the type of event related to the originating occurrence. | `com.github.pull_request.opened`; `com.example.object.deleted.v2` | No |
| `cloudevents.event_subject` | string | The [subject](https://github.com/cloudevents/spec/blob/master/spec.md#subject) of the event in the context of the event producer (identified by source). | `mynewfile.jpg` | No |

**[1]:** Producers MUST ensure that event_source + event_id is unique for each distinct event.  If a duplicate event is re-sent (e.g. due to a network error) it MAY have the same id.  Consumers MAY assume that Events with identical event_source and event_id are duplicates.
<!-- endsemconv -->
