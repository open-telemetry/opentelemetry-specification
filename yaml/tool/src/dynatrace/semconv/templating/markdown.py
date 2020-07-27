#   Copyright 2020 Dynatrace LLC
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import glob
import io
import os
import re
import sys
import typing
from pathlib import PurePath

from dynatrace.semconv.model.constraints import AnyOf, Include
from dynatrace.semconv.model.semantic_attribute import (
    SemanticAttribute,
    EnumAttributeType,
    Required,
    EnumMember,
)
from dynatrace.semconv.model.semantic_convention import (
    SemanticConventionSet,
    SemanticConvention,
)
from dynatrace.semconv.model.utils import ID_RE


class RenderContext:
    is_full: bool
    is_remove_constraint: bool
    group_key: str
    break_counter: int
    enums: list
    notes: list
    note_index: int
    current_md: str
    current_semconv: SemanticConvention

    def __init__(self, break_count):
        self.is_full = False
        self.is_remove_constraint = False
        self.group_key = ""
        self.break_count = break_count
        self.enums = []
        self.notes = []
        self.note_index = 1
        self.current_md = ""
        self.current_semconv = None

    def clear_table_generation(self):
        self.notes = []
        self.enums = []
        self.note_index = 1

    def add_note(self, msg: str):
        self.note_index += 1
        self.notes.append(msg)

    def add_enum(self, attr: SemanticAttribute):
        self.enums.append(attr)


class MarkdownRenderer:
    p_start = re.compile("<!--\\s*semconv\\s+(.+)-->")
    p_semconv_selector = re.compile(
        r"(?P<semconv_id>{})(?:\((?P<parameters>.*)\))?".format(ID_RE.pattern)
    )
    p_end = re.compile("<!--\\s*endsemconv\\s*-->")
    default_break_conditional_labels = 50
    valid_parameters = ["tag", "full", "remove_constraints"]

    prelude = "<!-- semconv {} -->\n"
    table_headers = "| Attribute  | Type | Description  | Example  | Required |\n|---|---|---|---|---|\n"

    def __init__(
        self,
        md_folder,
        semconvset: SemanticConventionSet,
        exclude: list = [],
        break_count=default_break_conditional_labels,
        check_only=False,
    ):
        self.render_ctx = RenderContext(break_count)
        self.semconvset = semconvset
        # We load all markdown files to render
        self.file_names = sorted(
            set(glob.glob("{}/**/*.md".format(md_folder), recursive=True))
            - set(exclude)
        )
        # We build the dict that maps each attribute that has to be rendered to the latest visited file
        # that contains it
        self.filename_for_attr_fqn = self._create_attribute_location_dict()
        self.check_only = check_only

    """
    This method renders attributes as markdown table entry
    """

    def to_markdown_attr(
        self, attribute: SemanticAttribute, output: io.StringIO,
    ):
        name = self.render_attribute_id(attribute.fqn)
        attr_type = (
            "enum"
            if isinstance(attribute.attr_type, EnumAttributeType)
            else attribute.attr_type
        )
        description = ""
        if attribute.deprecated:
            if "deprecated" in attribute.deprecated.lower():
                description = "**{}**<br>".format(attribute.deprecated)
            else:
                description = "**Deprecated: {}**<br>".format(attribute.deprecated)
        description += attribute.brief
        if attribute.note:
            description += " [{}]".format(self.render_ctx.note_index)
            self.render_ctx.add_note(attribute.note)
        examples = ""
        if isinstance(attribute.attr_type, EnumAttributeType):
            if attribute.is_local and not attribute.ref:
                self.render_ctx.add_enum(attribute)
            example_list = attribute.examples if attribute.examples else ()
            examples = (
                "<br>".join("`{}`".format(ex) for ex in example_list)
                if example_list
                else "`{}`".format(attribute.attr_type.members[0].value)
            )
            # Add better type info to enum
            if attribute.attr_type.custom_values:
                attr_type = attribute.attr_type.enum_type
            else:
                attr_type = "{} enum".format(attribute.attr_type.enum_type)
        elif attribute.attr_type:
            example_list = attribute.examples if attribute.examples else []
            examples = "<br>".join("`{}`".format(ex) for ex in example_list)
        if attribute.required == Required.ALWAYS:
            required = "Yes"
        elif attribute.required == Required.CONDITIONAL:
            if len(attribute.required_msg) < self.render_ctx.break_count:
                required = "Conditional<br>{}".format(attribute.required_msg)
            else:
                # We put the condition in the notes after the table
                required = "Conditional [{}]".format(self.render_ctx.note_index)
                self.render_ctx.add_note(attribute.required_msg)
        else:
            # check if they are required by some constraint
            if (
                not self.render_ctx.is_remove_constraint
                and self.render_ctx.current_semconv.has_attribute_constraint(attribute)
            ):
                required = "See below"
            else:
                required = "No"
        output.write(
            "| {} | {} | {} | {} | {} |\n".format(
                name, attr_type, description, examples, required
            )
        )

    """
    This method renders anyof constraints into markdown lists
    """

    def to_markdown_anyof(self, anyof: AnyOf, output: io.StringIO):
        if anyof.imported and not self.render_ctx.is_full:
            return ""
        output.write("\nAt least one of the following is required:\n\n")
        for choice in anyof.choice_list_ids:
            output.write("* ")
            list_of_choice = ", ".join(self.render_attribute_id(c) for c in choice)
            output.write(list_of_choice)
            output.write("\n")

    def to_markdown_notes(self, output: io.StringIO):
        """ Renders notes after a Semantic Convention Table
        :return:
        """
        counter = 1
        for note in self.render_ctx.notes:
            output.write("\n**[{}]:** {}\n".format(counter, note))
            counter += 1

    def to_markdown_enum(self, output: io.StringIO):
        """ Renders enum types after a Semantic Convention Table
        :return:
        """
        attr: SemanticAttribute
        for attr in self.render_ctx.enums:
            enum: EnumAttributeType
            enum = attr.attr_type
            output.write("\n`" + attr.fqn + "` ")
            if enum.custom_values:
                output.write(
                    "MUST be one of the following or, if none of the listed values apply, a custom value"
                )
            else:
                output.write("MUST be one of the following")
            output.write(":\n\n")
            output.write("| Value  | Description |\n|---|---|")
            member: EnumMember
            counter = 1
            notes = []
            for member in enum.members:
                description = member.brief
                if member.note:
                    description += " [{}]".format(counter)
                    counter += 1
                    notes.append(member.note)
                output.write("\n| `{}` | {} |".format(member.value, description))
            counter = 1
            if not notes:
                output.write("\n")
            for note in notes:
                output.write("\n\n**[{}]:** {}".format(counter, note))
                counter += 1
            if notes:
                output.write("\n")

    """
    Method to render in markdown an attribute id. If the id points to an attribute in another rendered table, a markdown
    link is introduced.
    """

    def render_attribute_id(self, attribute_id):
        md_file = self.filename_for_attr_fqn.get(attribute_id)
        if md_file:
            path = PurePath(self.render_ctx.current_md)
            if path.as_posix() != PurePath(md_file).as_posix():
                diff = PurePath(os.path.relpath(md_file, start=path.parent)).as_posix()
                if diff != ".":
                    return "[{}]({})".format(attribute_id, diff)
        return "`{}`".format(attribute_id)

    """
    Entry method to translate attributes and constraints of a semantic convention into Markdown
    """

    def to_markdown_constraint(
        self, obj: typing.Union[AnyOf, Include], output: io.StringIO,
    ):
        if isinstance(obj, AnyOf):
            self.to_markdown_anyof(obj, output)
            return
        elif isinstance(obj, Include):
            return
        raise Exception(
            "Trying to generate Markdown for a wrong type {}".format(type(obj))
        )

    def render_md(self):
        for md_filename in self.file_names:
            with open(md_filename, encoding="utf-8") as md_file:
                content = md_file.read()
                output = io.StringIO()
                self._render_single_file(content, md_filename, output)
            if self.check_only:
                if content != output.getvalue():
                    sys.exit(
                        "File "
                        + md_filename
                        + " contains a table that would be reformatted."
                    )
            else:
                with open(md_filename, "w", encoding="utf-8") as md_file:
                    md_file.write(output.getvalue())
        if self.check_only:
            print("{} files left unchanged.".format(len(self.file_names)))

    """
    This method creates a dictionary that associates each attribute with the latest table in which it is rendered.
    This is required by the ref attributes to point to the correct file
    """

    def _create_attribute_location_dict(self):
        m = {}
        for md in self.file_names:
            with open(md, "r", encoding="utf-8") as markdown:
                self.current_md = md
                content = markdown.read()
                for match in self.p_start.finditer(content):
                    semconv_id, _ = self._parse_semconv_selector(match.group(1).strip())
                    semconv = self.semconvset.models.get(semconv_id)
                    if not semconv:
                        raise ValueError(
                            "Semantic Convention ID {} not found".format(semconv_id)
                        )
                    a: SemanticAttribute
                    valid_attr = (
                        a for a in semconv.attributes if a.is_local and not a.ref
                    )
                    for attr in valid_attr:
                        m[attr.fqn] = md
        return m

    def _parse_semconv_selector(self, selector: str):
        semconv_id = selector
        parameters = {}
        m = self.p_semconv_selector.match(selector)
        if m:
            semconv_id = m.group("semconv_id")
            pars = m.group("parameters")
            if pars:
                for par in pars.split(","):
                    key_value = par.split("=")
                    if len(key_value) > 2:
                        raise ValueError(
                            "Wrong syntax in "
                            + m.group(4)
                            + " in "
                            + self.render_ctx.current_md
                        )
                    key = key_value[0].strip()
                    if key not in self.valid_parameters:
                        raise ValueError(
                            "Unexpected parameter `"
                            + key_value[0]
                            + "` in "
                            + self.render_ctx.current_md
                        )
                    if key in parameters:
                        raise ValueError(
                            "Parameter `"
                            + key_value[0]
                            + "` already defined in "
                            + self.render_ctx.current_md
                        )
                    value = key_value[1] if len(key_value) == 2 else ""
                    parameters[key] = value
        return semconv_id, parameters

    def _render_single_file(self, content: str, md: str, output: io.StringIO):
        last_match = 0
        self.render_ctx.current_md = md
        # The current implementation swallows nested semconv tags
        while True:
            match = self.p_start.search(content, last_match)
            if not match:
                break
            semconv_id, parameters = self._parse_semconv_selector(
                match.group(1).strip()
            )
            semconv = self.semconvset.models.get(semconv_id)
            if not semconv:
                # We should not fail here since we would detect this earlier
                # But better be safe than sorry
                raise ValueError(
                    "Semantic Convention ID {} not found".format(semconv_id)
                )
            output.write(content[last_match : match.start(0)])
            self._render_table(semconv, parameters, output)
            end_match = self.p_end.search(content, last_match)
            if not end_match:
                raise ValueError("Missing ending <!-- endsemconv --> tag")
            last_match = end_match.end()
        output.write(content[last_match:])

    def _render_table(
        self, semconv: SemanticConvention, parameters, output: io.StringIO
    ):
        header: str
        header = semconv.semconv_id
        if parameters:
            header += "("
            header += ",".join(
                par + "=" + val if val else par for par, val in parameters.items()
            )
            header = header + ")"
        output.write(MarkdownRenderer.prelude.format(header))
        self.render_ctx.clear_table_generation()
        self.render_ctx.current_semconv = semconv
        self.render_ctx.is_remove_constraint = "remove_constraints" in parameters
        self.render_ctx.group_key = parameters.get("tag")
        self.render_ctx.is_full = "full" in parameters
        attr_to_print = []
        attr: SemanticAttribute
        for attr in sorted(
            semconv.attributes, key=lambda a: "" if a.ref is None else a.ref
        ):
            if self.render_ctx.group_key is not None:
                if attr.tag == self.render_ctx.group_key:
                    attr_to_print.append(attr)
                continue
            if self.render_ctx.is_full or attr.is_local:
                attr_to_print.append(attr)
        if attr_to_print:
            output.write(MarkdownRenderer.table_headers)
            for attr in attr_to_print:
                self.to_markdown_attr(attr, output)
        self.to_markdown_notes(output)
        if not self.render_ctx.is_remove_constraint:
            for cnst in semconv.constraints:
                self.to_markdown_constraint(cnst, output)
        self.to_markdown_enum(output)

        output.write("<!-- endsemconv -->")
