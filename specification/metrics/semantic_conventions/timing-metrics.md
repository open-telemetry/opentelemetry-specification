# General Semantic Conventions for Timed Operations

<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [Overview](#overview)
- [Duration Instrument](#duration-instrument)
  * [Value](#value)
  * [Metric Labels](#metric-labels)

<!-- tocstop -->

## Overview

This document describes the metric instruments and labels to use when measuring
the timing of any operation.

This is the generic specification; there are context-specific specifications
that follow from it for the following:

* [HTTP operations](./http-metrics.md)
* TODO: add the rest of these when they're written

## Duration Instrument

For each category of operation, a single `ValueRecorder` metric instrument
should be created.
Its name should include the name of the category, followed by the kind of
operation being timed, like this:

```
{category}.{subcategory}.duration
```

If the duration is derived from spans that follow one of the common
semantic-conventional _areas_, the category should be the label prefix used in
that semantic convention, and the subcategory should be the span kind.

Example names:

* `http.server.duration`
* `db.client.duration`
* `messaging.producer.duration`
* `rpc.client.duration`

### Value

The duration of each operation **in seconds** should be recorded onto this value
recorder.

### Metric Labels

It is up to the implementor to annotate the duration instruments with labels
specific to the represented operation, but care should be taken when adding
labels to avoid excessive cardinality.

If there is a corresponding span for the operation with defined trace semantic
conventions, the labels should follow the attribute guidelines found in those
semantic conventions, with the following caveats:

1. Do not include any high-cardinality attributes, or replace them with a
low-cardinality substitution.
2. Replace non-string values with reasonable string representations when
possible, and do not include attributes that cannot be easily represented as a
string.
