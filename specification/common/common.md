# Common specification concepts

**Status**: [Stable, Feature-freeze](../document-status.md)

<details>
<summary>
Table of Contents
</summary>

- [Attributes](#attributes)

</details>

## Attributes

Attributes are a list of zero or more key-value pairs. An `Attribute` MUST have the following properties:

- The attribute key, which MUST be a non-`null` and non-empty string.
- The attribute value, which is either:
  - A primitive type: string, boolean, double precision floating point (IEEE 754-1985) or signed 64 bit integer.
  - An array of primitive type values. The array MUST be homogeneous,
    i.e. it MUST NOT contain values of different types. For protocols that do
    not natively support array values such values SHOULD be represented as JSON strings.

Attribute values expressing a numerical value of zero, an empty string, or an
empty array are considered meaningful and MUST be stored and passed on to
processors / exporters.

Attribute values of `null` are not valid and attempting to set a `null` value is
undefined behavior.

`null` values SHOULD NOT be allowed in arrays. However, if it is impossible to
make sure that no `null` values are accepted
(e.g. in languages that do not have appropriate compile-time type checking),
`null` values within arrays MUST be preserved as-is (i.e., passed on to span
processors / exporters as `null`). If exporters do not support exporting `null`
values, they MAY replace those values by 0, `false`, or empty strings.
This is required for map/dictionary structures represented as two arrays with
indices that are kept in sync (e.g., two attributes `header_keys` and `header_values`,
both containing an array of strings to represent a mapping
`header_keys[i] -> header_values[i]`).

See [Attribute and Label Naming](attribute-and-label-naming.md) for naming guidelines.
