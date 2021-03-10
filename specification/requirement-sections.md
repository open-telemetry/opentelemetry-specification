# Requirement Sections

<details>
<summary>
Table of Contents
</summary>
<!-- Re-generate TOC with `markdown-toc --no-first-h1 -i` -->

<!-- toc -->

- [Requirement Sections](#requirement-sections)
  * [Requirement Sections Format](#requirement-sections-format)
    + [Key Format](#key-format)
    + [Description Format](#description-format)
    + [Example](#example)
  * [Purpose of the requirement sections](#purpose-of-the-requirement-sections)

<!-- tocstop -->

</details>

This document explains how the OpenTelemetry specification requirement sections are written.

## Overview

The OpenTelemetry specification is written in several [Markdown](https://github.github.com/gfm/) files.

Each one of these files can contain any resource to explain and describe its part of the specification.
Examples of these resources are images, diagrams, code, regular text, etc.

Also, included in the same Markdown documents that make the OpenTelemetry specification
are to be included specific sections named _requirement sections_ that follow a specific
format. These sections are the part of the document that more formally describes each of
the specific requirements that the OpenTelemetry specification has.

Each of these requirement sections has 2 components:

1. A unique **key**, a string that identifies the requirement section in a Markdown document
2. A **description**, a string that MUST include at least one of the [BCP 14 keywords](https://tools.ietf.org/html/bcp14).

### Requirement Sections Format

Each one of these requirement sections are written also in Markdown syntax in order for them to integrate
with the rest of the document.

#### Key Format

The key of every requirement section MUST be unique in the document that contains it. This key
MUST be written in this manner:

```
###### requirement: unique_key_identifier
```

The first six `#` symbols create a Markdown heading for the requirement section. The `requirement: `
string that follows indicates that this particular header is part of a requirement section and not
just any Markdown six `#` level heading. The following string indicated by `unique_key_indetifier` MUST be
unique in the document that contains it. The characters that make this string MUST only be
alphanumeric characters and underscores.

#### Description Format

The description of every requirement section MUST be written as a
[block quote](https://github.github.com/gfm/#block-quotes) immediately following a blank line after a requirement section key:

```
> The span MUST have an identifier.
>
> More text can be placed here as well.
```

The description MUST include at least one BCP 14 keyword.

#### Example

Here is a small example that shows how a Markdown document can have requirement sections to describe
its specific requirements:

```
# Some title for some OpenTelemetry concept

This part describes some OpenTelemetry concept. It can include examples, images, diagrams, etc.

After the concept is described, its specifc requirements are written in requirement sections:

###### requirement: concept_identifier

> The concept MUST have an identifier.
>
> The concept is important for OpenTelemetry.

###### requirement: concept_documentation

> The concept SHOULD be documented in every implementation.
```

### Purpose of the requirement sections

The idea behind writing the requirements in this manner is to make it easy for the reader to find all the
requirements included in an OpenTelemetry specification document. In this way, it is also easy to find all
the requirements a certain implementation must comply with. With all the requirements available for the
implementation developer, it is easy to make a list of test cases, one for every requirement section, and
to test the implementation against these test cases to measure compliance with the specification. This is
why the key must be unique, so that it can be used to form a name for the particular testing function for
that requirement.

With the requirements specified in this way, it is also easier for the specification and implementation
developers to refer to a certain requirement unequivocally, making communication between developers more
clear.

It is also possible to parse the Markdown documents and extract from them a list of the requirements in a
certain format. A parser that does this is provided. Itproduces JSON documents for every Markdown document
that includes at least one requirement section. With these JSON files, a testing schema can be produced for
every implementation that can help developers know how compliant with the specification the implementation is.

The parser can also work as a checker that makes sure that every requirement section is compliant with this
specification. This can even be incorporated to the CI of the repo where the OpenTelemetry specification is
in order to reject any change that adds a non-compliant requirement section.

Finally, it makes the specification developer follow a "testing mindset" while writing requirements. For example,
when writing a requirement, the specification developers ask themselves "can a test be written for this statement?".
This helps writing short, concise requirements that are clear for the implementation developers.

### Running the specification parser

The included specification parser can be run from the root directory of the OpenTelemetry specification directory
like this:

```
python internal/tools/specification_parser/specification_parser.py
```

This will recursively look for Markdown files in the `specification` directory. For every Markdown file that has at
least one requirement section, it will generate a corresponding JSON file with the key, description and BCP 14
keyword or every requirement section.

Once the JSON files are generated, they can be used by implementations as checklists to write test cases. These
test cases then are written to implement what is said in the description of each item in the JSON file. This set of
test cases can be used to measure how compliant with the specification an implementation is.
