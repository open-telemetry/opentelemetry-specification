# Version Semantic Attribute

Add a standard `version` semantic attribute.

## Motivation

When creating trace data or metrics, it can be extremely useful to know the specific version that
emitted the iota of span or measurement being viewed. However, versions can mean different things
to different systems and users. In addition, downstream analysis systems may wish to expose
functionality related to the type of a version (such as detecting when versions are newer or older).
To support this, we should standardize a `version` attribute with optional hints as to the type of the
version.

## Explanation

A `version` is a semantic attribute that can be applied to other resources, such as `Service`,
`Component`, `Library`, `Device`, `Platform`, etc. A `version` attribute is optional, but recommended.
The definition of a `version` is a key-value attribute pair of `string` to `string`, with naming schemas
available to hint at the type of a version, such as the following:

`version=semver:1.2.3` (a semantic version)
`version=git:8ae73a` (a git sha hash)
`version=0.0.4.2.20190921` (a untyped version)

## Internal details

Since this is just an attribute pair, no special handling is required, although SDKs may provide helper methods
to construct schema-appropriate values.

## Prior art and alternatives

Tagging service resources with their version is generally suggested by analysis tools -- see [JAEGER_TAGS](https://www.jaegertracing.io/docs/1.8/client-features/) for an example -- but lacks standardization.
