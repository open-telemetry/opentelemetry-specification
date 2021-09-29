# CloudEvents

This document defines how to describe sending and receiving [CloudEvents](https://cloudevents.io/) with spans.

The transport involved in sending/receiving CloudEvents is represented by a separate span, depending on the underlying protocol used.

**Status**: [Experimental](../../document-status.md)

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [Span name](#span-name)
- [Span kind](#span-kind)
- [Attributes](#attributes)

<!-- tocstop -->

## Span name

The span name should be a combination of the `CloudEvents` prefix, followed by the event type as in the following format:

```
CloudEvents <event_type>
```

The event type SHOULD only be used as part of the span name if it is known to be of low cardinality (cf. [general span name guidelines](../api.md#span)).

Examples:

* `CloudEvents com.github.pull_request.opened`

## Span kind

When an entity is acting as a sender of CloudEvents, it should set the span kind to `PRODUCER`. When acting as a receiver, it should set the span kind to `CONSUMER`.

## Attributes

<!-- semconv cloudevents -->
| Attribute  | Type | Description  | Examples  | Required |
|---|---|---|---|---|
| `cloudevents.event_id` | string | The [event_id](https://github.com/cloudevents/spec/blob/master/spec.md#id) identifies the event within the scope of a producer. | `123e4567-e89b-12d3-a456-426614174000`; `producer-1` | No |
| `cloudevents.source` | string | The [source](https://github.com/cloudevents/spec/blob/master/spec.md#source-1) identifies the context in which an event happened. | `https://github.com/cloudevents`; `/cloudevents/spec/pull/123`; `my-service` | No |
| `cloudevents.spec_version` | string | The [version of the CloudEvents specification](https://github.com/cloudevents/spec/blob/master/spec.md#specversion) which the event uses. | `1.0` | No |
| `cloudevents.event_type` | string | The [event_type](https://github.com/cloudevents/spec/blob/master/spec.md#type) contains a value describing the type of event related to the originating occurrence. | `com.github.pull_request.opened`; `com.example.object.deleted.v2` | No |
| `cloudevents.subject` | string | The [subject](https://github.com/cloudevents/spec/blob/master/spec.md#subject) of the event in the context of the event producer (identified by source). | `mynewfile.jpg` | No |
<!-- endsemconv -->
