# Conformance Clause

Conformance to OpenTelemetry is defined in this conformance clause. This
conformance clause follows the
[W3C Recommendation QA Framework: Specification Guidelines](https://www.w3.org/TR/2005/REC-qaframe-spec-20050817/).

## Parts of the specification

### Normative Parts

_Normative Parts_ of this specification define its strict requirements. They
are identified by a level 5 header followed by the word *Requirement* or the
words *Conditional Requirement* and an identifying number.

#### Requirement Normative Parts

A _Requirement Normative Part_ defines a certain requirement that the
implementations of OpenTelemetry are to implement. The mandatoriness of the
requirement is defined by the RFC 2119 word that appears in the Requirement
Normative Part.

Here is an example of a Requirement Normative Part:

##### Requirement 4

> The trace **MUST** have an identifier.

This is the markdown code for the previous example:

```
##### Requirement 4:

> The trace **MUST** have an identifier.
```

The header for a requirement must be of level 5 (a header that begins with 5 `#`
characters). The requirement number must be unique per file and continuously increasing
from 1.

A blank line must follow the header.

The `>` character serves as a delimiter for the Normative Part, it must be the
first character of any line that makes the content of the Normative Part.
Multiple lines can start with this character:

```
##### Requirement 6:

> The span **MAY** include
> additional metadata.
```

#### Conditional Requirement Normative Parts

A _Conditional Requirement Normative Part_ has the same characteristics of a
Requirement Normative Part but it is preceded by a _condition_. Some
requirements of this specification are conditional, they are valid only for
certain implementations if a certain condition is fulfilled by such
implementation. For example, a requirement that refers to certain software
pattern would be valid for some implementations that can follow that pattern
and not be valid for other implementations that can not. The implementations
that can follow that pattern can be subjected to additional requirements,
defined in Conditional Requirement Normative parts.

Here is an example of a Conditional Requirement Normative Part:

##### Condition 1

> The API does not operate directly on the `Context`.
>
> ##### Conditional Requirement 1.1
>
> > The API **MUST** provide an `extract` function to extract the `Baggage`
> > from a `Context` instance.

The header for a condition must be of level 5. The condition number must be
unique per file and continuously increasing from 1. The conditional requirement
number must be composed of the containing condition number a period and an
unique number continuously increasing from 1. As more condition or requirement
levels are nested more numbers separated by periods are correspondingly to be
added to the condition or conditional requirement numbers.

A blank line must follow the header.

The `>` character indicates the scope of the condition, it must be the first
character of any line that makes the content of the condition. Any requirement
inside the scope of the condition is valid only if the condition is true for
the particular implementation. Other conditions may also be inside the scope of
another condition. A contained condition inside the scope of a containing
condition is to be evaluated only if the containing condition is true for the
particular implementation.

This is the markdown code for the previous example:

```
##### Condition 1

> The API does not operate directly on the `Context`.
>
> ##### Conditional Requirement 1.1
>
> > The API **MUST** provide an `extract` function to extract the `Baggage`
> > from a `Context` instance.
```

### Informative Parts

Any other part of a file that includes at least one Requirement Normative Part
is considered an _Informative Part_. An Informative Part does not specify any
requirement, it is only intended to help the reader of the specification
understand it better. There is no requirement for the writing of an Informative
Part, any text, table, image, diagram, etc. can be included.

Regardless of the language used in an informative part, it is never to be
considered normative in any way. Only requirements defined in a Requirement
Normative Part have any mandatoriness for the implementations of OpenTelemetry.

### Normative Language

Every one of the Requirement Normative Parts must include one and only one of
the following words:

- MUST
- REQUIRED
- SHALL
- SHALL NOT
- MUST NOT
- SHOULD
- RECOMMENDED
- SHOULD NOT
- NOT RECOMMENDED
- MAY
- OPTIONAL

These words are to be interpreted as they are defined in
[RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119). These two kinds of
Normative Parts (Requirement Normative Parts and Conditional Requirement
Normative Parts) are explained with more detail next.

## OpenTelemetry Conformance Model

### Products

The OpenTelemetry Conformance Model defines conformance for the following
_products_:

- API: the interfaces that the application and library developers use directly
- SDK: the implementation of the interfaces in the API
- Semantic Conventions: FIXME: add a brief description of Semantic Conventions
- OTLP: FIXME: Add a brief description of OTLP

### Conformance Designations

There is only one conformance designation: _Full_. This conformance designation
applies to all the products listed [here](#products). This conformance
designation requires that all requirements are implemented accordingly to their
mandatoriness. Some requirements are conditional, these requirements are to be
implemented accordingly to their mandatoriness if the corresponding
condition applies to the corresponding implementation.

#### Profiles

OpenTelemetry does not address nor define profiles to subdivide its technology.

#### Modules

OpenTelemetry does not address nor define modules to subdivide its technology.

#### Levels

OpenTelemetry does not address nor define levels to subdivide its technology.

#### Deprecated Features

OpenTelemetry does not have any deprecated features. OpenTelemetry may have
deprecated features in the future.

#### Obsolete Features

OpenTelemetry does not have any obsolete features. OpenTelemetry may have
obsolete features in the future.

#### Optional Features

OpenTelemetry does not have any optional features. OpenTelemetry may have
optional features in the future.

#### Extensibility

OpenTelemetry is not extensible.

#### Conformance Claims

OpenTelemetry conformance claims must include the following:

- Specification Name: OpenTelemetry
- Specification Version: OpenTelemetry Version Number
- Degree of Conformance: Full
- Date: Date when the claim is made
