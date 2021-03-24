# Semantic Convention YAML Language

First, the syntax with a pseudo [EBNF](https://en.wikipedia.org/wiki/Extended_Backus-Naur_form) grammar is presented.
Then, the semantic of each field is described.

## Syntax

All attributes are lower case.

```bnf
groups ::= semconv
       | semconv groups

semconv ::= id brief [note] [prefix] [extends] [span_kind] attributes [constraints]

id    ::= string
brief ::= string
note  ::= string

prefix ::= string

# extends MUST point to an existing semconv id
extends ::= string

span_kind ::= "client"
          |   "server"
          |   "producer"
          |   "consumer"
          |   "internal"

attributes ::= (id type brief examples | ref [brief] [examples]) [required] [note]

# ref MUST point to an existing attribute id
ref ::= id

type ::= "string"
     |   "int"
     |   "double"
     |   "boolean"
     |   "string[]"
     |   "int[]"
     |   "double[]"
     |   "boolean[]"
     |   enum

enum ::= [allow_custom_values] members

allow_custom_values := boolean

members ::= member {member}

member ::= id value [brief] [note]

required ::= "always"
         |   "conditional" <condition>

examples ::= <example_value> {<example_value>}

constraints ::= constraint {constraint}

constraint ::= any_of
           |   include

any_of ::= id {id}

include ::= id

```

## Semantics

### Groups

Groups contain the list of semantic conventions and it is the root node of each yaml file.

### Semantic Convention

The field `semconv` represents a semantic convention and it is made by:

- `id`, string that uniquely identifies the semantic convention.
- `brief`, string, a brief description of the semantic convention.
- `note`, optional string, a more elaborate description of the semantic convention.
    It defaults to an empty string.
- `prefix`, optional string, prefix for the attributes for this semantic convention.
    It defaults to an empty string.
- `extends`, optional string, reference another semantic convention `id`.
    It inherits the prefix, constraints, and all attributes defined in the specified semantic convention.
- `span_kind`, optional enum, specifies the kind of the span.
- `attributes`, list of attributes that belong to the semantic convention.
- `constraints`, optional list, additional constraints (See later). It defaults to an empty list.

### Attributes

An attribute is defined by:

- `id`, string that uniquely identifies the attribute.
- `type`, either a string literal denoting the type or an enum definition (See later).
   The accepted string literals are:

  * "string": String attributes.
  * "int": Integer attributes.
  * "double": Double attributes.
  * "boolean": Boolean attributes.
  * "string[]": Array of strings attributes.
  * "int[]": Array of integer attributes.
  * "double[]": Array of double attributes.
  * "boolean[]": Array of booleans attributes.

  See the [specification of Attributes](../specification/common/common.md#attributes) for the definition of the value types.
- `ref`, optional string, reference an existing attribute, see later.
- `required`, optional, specifies if the attribute is mandatory.
    Can be "always", or "conditional". When omitted, the attribute is not required.
    When set to "conditional",the string provided as `<condition>` MUST specify
    the conditions under which the attribute is required.
- `brief`, string, brief description of the attribute.
- `note`, optional string, additional notes to the attribute. It defaults to an empty string.
- `examples`, sequence/dictionary of example values for the attribute.
   They are optional for boolean and enum attributes.
   Example values must be of the same type of the attribute.
   If only a single example is provided, it can directly be reported without encapsulating it into a sequence/dictionary.

Examples for setting the `examples` field:

A single example value for a string attribute. All the following three representations are equivalent:

```yaml
examples: 'this is a single string'
```

or

```yaml
examples: ['this is a single string']
```

or

```yaml
examples:
   - 'this is a single string'
```

Attention, the following will throw a type mismatch error because a string type as example value is expected and not an array of string:

```yaml
examples:
   - ['this is an error']

examples: [['this is an error']]
```

Multiple example values for a string attribute:

```yaml
examples: ['this is a single string', 'this is another one']
```

or

```yaml
examples:
   - 'this is a single string'
   - 'this is another one'
```

A single example value for an array of strings attribute:

```yaml
examples: ['first element of first array', 'second element of first array']
```

or

```yaml
examples:
   - ['first element of first array', 'second element of first array']
```

Attention, the following will throw a type mismatch error because an array of strings as type for the example values is expected and not a string:

```yaml
examples: 'this is an error'
```

Multiple example values for an array of string attribute:

```yaml
examples: [ ['first element of first array', 'second element of first array'], ['first element of second array', 'second element of second array'] ]
```

or

```yaml
examples:
   - ['first element of first array', 'second element of first array']
   - ['first element of second array', 'second element of second array']
```

### Ref

`ref` MUST have an id of an existing attribute. When it is set, `id` and `type` MUST NOT be present.
`ref` is useful for specifying that an existing attribute of another semantic convention is part of
the current semantic convention and inherit its `brief`, `note`, and `example` values. However, if these
fields are present in the current attribute definition, they override the inherited values.

### Type

An attribute type can either be a string, int, double, boolean, array of strings, array of int, array of double,
array of booleans, or an enumeration. If it is an enumeration, additional fields are required:

- `allow_custom_values`, optional boolean, set to false to not accept values
     other than the specified members. It defaults to `true`.
- `members`, list of enum entries.

An enum entry has the following fields:

- `id`, string that uniquely identifies the enum entry.
- `value`, string, int, or boolean; value of the enum entry.
- `brief`, optional string, brief description of the enum entry value. It defaults to the value of `id`.
- `note`, optional string, longer description. It defaults to an empty string.

### Constraints

Allow to define additional requirements on the semantic convention.
Currently, it supports `any_of` and `include`.

#### Any Of

`any_of` accepts a list of sequences. Each sequence contains a list of attribute ids that are required.
`any_of` enforces that all attributes of at least one of the sequences are set.

#### Include

`include` accepts a semantic conventions `id`. It includes as part of this semantic convention all constraints
and required attributes that are not already defined in the current semantic convention.
