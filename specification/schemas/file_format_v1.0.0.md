---
# Hugo front matter used to generate the website version of this page:
linkTitle: 1.0.0
---

# Schema File Format 1.0.0

**Status**: [Development](../document-status.md)

A Schema File is a YAML file that describes the schema of a particular version.
It defines the transformations that can be used to convert the telemetry data
represented in any other older compatible version of the same schema family to
this schema version.

## File Structure

Here is the structure of the Schema File:

```yaml
# Defines the file format. MUST be set to 1.0.0.
file_format: 1.0.0

# The Schema URL that this file is published at. The version number in the URL
# MUST match the highest version number in the "versions" section below.
# Note: the schema version number in the URL is not related in any way to
# the file_format setting above.
schema_url: https://opentelemetry.io/schemas/1.2.0

# Definitions for each schema version in this family.
# Note: the ordering of versions is defined according to semver
# version number ordering rules.
versions:
  <version_number_last>:
    # definitions for this version. See details below.

  <version_number_previous>:
    # definitions for previous version
    ...
  <version_number_first>:
    # Defines the first version.
```

Each `<version_number>` section has the following structure:

```yaml
  <version_number>:
    all:
      changes:
        # sequence of transformations.

    resources:
      changes:
        # sequence of transformations.

    spans:
      changes:
        # sequence of transformations.

    span_events:
      changes:
        # sequence of transformations.

    metrics:
      changes:
        # sequence of transformations.

    logs:
      changes:
        # sequence of transformations.
```

There are 6 sub-sections under each version definition: "all", "resources",
"spans", "span_events", "metrics", "logs". The last 5 sub-sections in this list
contain definitions that apply only to the corresponding telemetry data type.
Section "all" contains definitions that apply to all types of telemetry data.

Below we describe each section in detail.

### all Section

"all" section in the schema file defines transformations. It must contain a
sub-section named "changes" that defines how attributes were renamed from the
previous version to this version.

The "changes" section is a sequence of transformations. Only one transformation
is supported for section "all": "rename_attributes" transformation.

"rename_attributes" transformation requires a map of key/value pairs, where the
key is the old name of the attribute used in the previous version, the value is
the new name of the attribute starting from this version. Here is the structure:

```yaml
    all:
      changes:
        - rename_attributes:
            attribute_map:
              # map of key/values.
```

The transformations in section "all" apply to the following telemetry data:
resource attributes, span attributes, span event attributes, log attributes,
metric attributes.

Important: when converting from the previous version to the current version the
transformation sequence in section "all" is performed first. After that the
transformations in the specific section ("resources", "spans", "span_events",
"metrics" or "logs") that correspond to the data type that is being converted
are applied.

Note that "rename_attributes" transformation in most cases is reversible. It is
possible to apply it backwards, so that telemetry data is converted from this
version to the previous version. The only exception is when 2 or more different
attributes in the previous version are renamed to the same attribute in the new
version. In that case the reverse transformation is not possible since it would
be ambiguous. When the reverse transformation is not possible it is considered
an incompatible change. In this case the MAJOR version number of the schema
SHOULD be increased in the new version.

### resources Section

"resources" section is very similar in its structure to "all". Like section
"all" the transformations in section "resources" may contain only
"rename_attributes" transformation.

The only difference from section "all" is that this transformation is only
applicable to Resource data type.

Here is the structure:

```yaml
    resources:
      changes:
        - rename_attributes:
            attribute_map:
              # map of key/values. The keys are the old attribute name used
              # the previous version, the values are the new attribute name
              # starting from this version.
```

### spans Section

"spans" section in the schema file defines transformations that are applicable
only to Span data type. It must contain a sub-section named "changes" that
defines a sequence of actions to be applied to convert Spans from the previous
version to this version.

One transformation is supported for section "span":  "rename_attributes".

#### rename_attributes Transformation

This is similar to the "rename_attributes" transformation supported in "all" and
"resource" sections. In addition it is also possible to optionally specify spans
that the transformation should apply to. Here is the structure:

```yaml
    spans:
      changes:
        - rename_attributes:
            attribute_map:
              # map of key/values. The keys are the old attribute name used
              # in the previous version, the values are the new attribute name
              # starting from this version.

            apply_to_spans:
              # Optional. If it is missing the transformation is applied
              # to all spans. If it is present the transformation is applied
              # only to the spans with the name that is found in the sequence
              # specified below.
```

### span_events Section

"spans_events" section in the schema file defines transformations that are
applicable only to Span's Event data type. It must contain a sub-section named
"changes" that defines a sequence of actions to be applied to convert events
from the previous version to this version.

Two transformations are supported for section "spans_events": "rename_events"
and "rename_attributes".

#### rename_events Transformation

This transformation allows to change event names. It is applied to all events or
only to events of spans that have the specified name. Here is the structure:

```yaml
    span_events:
      changes:
        - rename_events:
            name_map:
              # The keys are old event name used in the previous version, the
              # values are the new event name starting from this version.
```

#### rename_attributes Transformation

This is similar to the "rename_attributes" transformation supported in "all" and
"resource" sections. In addition it is also possible to optionally specify spans
and events that the transformation should apply to (both optional conditions
must match, if specified, for transformation to be applicable). Here is the
structure:

```yaml
    span_events:
      changes:
        - rename_attributes:
            attribute_map:
              # map of key/values. The keys are the old attribute name used
              # in the previous version, the values are the new attribute name
              # starting from this version.

            apply_to_spans:
              # Optional span names to apply to. If empty applies to all spans.

            apply_to_events:
              # Optional event names to apply to. If empty applies to all events.
```

### metrics Section

"metrics" section in the schema file defines transformations that are applicable
only to Metric data type. It must contain a sub-section named "changes" that
defines a sequence of actions to be applied to convert metrics from the previous
version to this version.

Two transformations are supported for section "metrics": "rename_metrics" and
"rename_attributes".

#### rename_metrics Transformation

This transformation allows to change metric names. It is applied to all metrics.
Here is the structure:

```yaml
    metrics:
      changes:
        - rename_metrics:
            # map of key/values. The keys are the old metric name used
            # in the previous version, the values are the new metric name
            # starting from this version.
```

#### rename_attributes Transformation

This is similar to the "rename_attributes" transformation supported in "span"
sections. Here is the structure:

```yaml
    metrics:
      changes:
        - rename_attributes:
            attribute_map:
              # map of key/values. The keys are the old attribute name used
              # in the previous version, the values are the new attribute name
              # starting from this version.

            apply_to_metrics:
              # Optional. If it is missing the transformation is applied
              # to all metrics. If it is present the transformation is applied
              # only to the metrics with the name that is found in the sequence
              # specified below.
```

### logs Section

"logs" section in the schema file defines transformations that are applicable
only to the Log Record data type. It must contain a sub-section named "changes"
that defines a sequence of actions to be applied to convert logs from the
previous version to this version.

One transformation is supported for section "logs": "rename_attributes".

#### rename_attributes Transformation

This is similar to the "rename_attributes" transformation supported in "spans"
section. Here is the structure:

```yaml
    logs:
      changes:
        - rename_attributes:
            attribute_map:
              # map of key/values. The keys are the old attribute name used
              # the previous version, the values are the new attribute name
              # starting from this version.
```

### Order of Transformations

When converting from older version X to newer version Y of the schema (both
belonging to the same schema family) the transformations specified in each
version in the range [X..Y] are applied one by one, i.e. first we convert from X
to X+1, then from X+1 to X+2, ..., Y-2 to Y-1, Y-1 to Y. (Note, version numbers
are not a continuum of integer numbers. The notion of adding a natural number 1
to the version number is a placeholder for the phrase "next newer version number
that is defined for this schema family".)

The transformations that are listed for a particular version X describe changes
that happened since the schema version that precedes version X and belongs to
the same schema family. These transformations are listed in 6 sections: "all",
"resources", "spans", "span_events", "metrics", "logs". Here is the order in
which the transformations are applied:

- Transformations in section "all" always are applied first, before any of the
  transformations in the other 5 sections.

- Transformations in section "spans" are applied before transformations in
  section "span_events".

- The order in which the transformations in remaining sections ("resources",
  "metrics", logs") are applied relative to each other or relative to "spans"
  section is undefined (since there are not-interdependencies, the order does
  not matter).

In the "changes" subsection of each particular one of these 6 sections the
sequence of transformations is applied in the order it is listed in the schema
file, from top to bottom.

When converting in the opposite direction, from newer version Y to older version
X the order of transformation listed above is exactly the reverse, with each
individual transformation also performing the reverse conversion.

### Schema File Format Number

The "file_format" setting in the schema file specifies the format version of the
file. The format version follows the MAJOR.MINOR.PATCH format, similar to semver
2.0.

The "file_format" setting is used by consumers of the file to know if they are
capable of interpreting the content of the file.

The current value for this setting is "1.0.0". Any change to this number MUST
follow the OTEP process and be published in the specification.

The current schema file format allows representing a limited set of
transformations of telemetry data. We anticipate that in the future more types
of transformations may be desirable to support or other, additional information
may be desirable to record in the schema file.

As the schema file format evolves over time the format version number SHOULD
change according to the following rules:

- PATCH number SHOULD be increased when the file format changes in a way that
  does not affect the existing consumers of the file. For example addition of a
  completely new section in the schema file that has no effect on existing
  sections and has no effect on any existing schema functionality may be done
  via incrementing the PATCH number only. This approach is only valid if the new
  setting in the file is completely and safely ignorable by all existing
  processing logic.

  For example adding a completely new section that describes the full state of
  the schema has no effect on existing consumers which only care about "changes"
  section (unless we explicitly define the semantics of the new section such
  that it _needs_ to be taken into account when processing schema changes). So,
  adding such a new section can be done using a PATCH number increase.

- MINOR number SHOULD be increased if a new setting is added to the file format
  in a backward compatible manner. "Backward compatible" in this context means
  that consumers that are aware of the new MINOR number can consume the file of
  a particular MINOR version number or of any MINOR version number lower than
  that, provided that MAJOR version numbers are the same. Typically, this means
  that the added setting in file format is optional and the default value of the
  setting matches the behavior of the previous file format version.

  Note: there is no "forward compatibility" based on MINOR version number.
  Consumers which support reading up to a particular MINOR version number SHOULD
  NOT attempt to consume files with higher MINOR version numbers.

- MAJOR number SHOULD be increased if the file format is changed in an
  incompatible way. For example adding a new transformation type in the
  "changes" section is an incompatible change because it cannot be ignored by
  existing schema conversion logic, so such a change will require a new MAJOR
  number.

Correspondingly:

- Consumers of the schema file SHOULD NOT attempt to interpret the schema file
  if the MAJOR version number is different (higher or lower) than what the
  consumer supports.

- Consumers of the schema file SHOULD NOT attempt to interpret the schema file
  if the MINOR version number is higher than what the consumer supports.

- Consumers MAY ignore the PATCH number.

To illustrate this with some examples:

<table>
  <tr>
   <td><strong>File Format Version</strong>
   </td>
   <td><strong>Consumer's Expected Version</strong>
   </td>
   <td><strong>Consumer Can Read?</strong>
   </td>
  </tr>
  <tr>
   <td>1.0.0
   </td>
   <td>1.0.0
   </td>
   <td>yes
   </td>
  </tr>
  <tr>
   <td>1.0.x
   </td>
   <td>1.0.y
   </td>
   <td>yes, for any x and y.
   </td>
  </tr>
  <tr>
   <td>1.a.x
   </td>
   <td>1.b.x
   </td>
   <td>if a&lt;b then yes, otherwise no.
   </td>
  </tr>
  <tr>
   <td>2.0.0
   </td>
   <td>1.x.y
   </td>
   <td>no
   </td>
  </tr>
</table>

## Appendix A. Example Schema File

```yaml
# Defines the file format. MUST be set to 1.0.0.
file_format: 1.0.0

# The Schema URL that this file is published at. The version number in the URL
# MUST match the highest version number in the "versions" section below.
# Note: the schema version number in the URL is not related in any way to
# the file_format setting above.
schema_url: https://opentelemetry.io/schemas/1.1.0

# Definitions for each schema version in this family.
# Note: the ordering of versions is defined according to semver
# version number ordering rules.
versions:
  1.1.0:
    # Definitions for version 1.1.0.
    all:
      # Definitions that apply to all data types.
      changes:
        # Transformations to apply when converting from version 1.0.0 to 1.1.0.
        - rename_attributes:
            # map of key/values. The keys are the old attribute name used
            # the previous version, the values are the new attribute name
            # starting from this version.
            # Rename k8s.* to kubernetes.*
            k8s.cluster.name: kubernetes.cluster.name
            k8s.namespace.name: kubernetes.namespace.name
            k8s.node.name: kubernetes.node.name
            k8s.node.uid: kubernetes.node.uid
            k8s.pod.name: kubernetes.pod.name
            k8s.pod.uid: kubernetes.pod.uid
            k8s.container.name: kubernetes.container.name
            k8s.replicaset.name: kubernetes.replicaset.name
            k8s.replicaset.uid: kubernetes.replicaset.uid
            k8s.cronjob.name: kubernetes.cronjob.name
            k8s.cronjob.uid: kubernetes.cronjob.uid
            k8s.job.name: kubernetes.job.name
            k8s.job.uid: kubernetes.job.uid
            k8s.statefulset.name: kubernetes.statefulset.name
            k8s.statefulset.uid: kubernetes.statefulset.uid
            k8s.daemonset.name: kubernetes.daemonset.name
            k8s.daemonset.uid: kubernetes.daemonset.uid
            k8s.deployment.name: kubernetes.deployment.name
            k8s.deployment.uid: kubernetes.deployment.uid

    resources:
      # Definitions that apply to Resource data type.
      changes:
        - rename_attributes:
            telemetry.auto.version: telemetry.auto_instr.version

    spans:
      # Definitions that apply to Span data type.
      changes:
        - rename_attributes:
            attribute_map:
              # map of key/values. The keys are the old attribute name used
              # in the previous version, the values are the new attribute name
              # starting from this version.
              peer.service: peer.service.name
            apply_to_spans:
              # apply only to spans named "HTTP GET"
              - "HTTP GET"

    span_events:
      # Definitions that apply to Span Event data type.
      changes:
        - rename_events:
            # The keys are old event name used in the previous version, the
            # values are the new event name starting from this version.
            name_map: {stacktrace: stack_trace}

        - rename_attributes:
            attribute_map:
              peer.service: peer.service.name
            apply_to_events:
              # Optional event names to apply to. If empty applies to all events.
              - exception.stack_trace

    metrics:
      # Definitions that apply to Metric data type.
      changes:
        - rename_metrics:
            # map of key/values. The keys are the old metric name used
            # in the previous version, the values are the new metric name
            # starting from this version.
            container.cpu.usage.total: cpu.usage.total
            container.memory.usage.max: memory.usage.max

        - rename_attributes:
            attribute_map:
              status: state
            apply_to_metrics:
              # Optional. If it is missing the transformation is applied
              # to all metrics. If it is present the transformation is applied
              # only to the metrics with the name that is found in the sequence
              # specified below.
              - system.cpu.utilization
              - system.memory.usage
              - system.memory.utilization
              - system.paging.usage

    logs:
      # Definitions that apply to LogRecord data type.
      changes:
        - rename_attributes:
            attribute_map:
              process.executable_name: process.executable.name

  1.0.0:
    # First version of this schema family.
```
