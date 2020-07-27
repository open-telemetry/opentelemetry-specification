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

import abc
import datetime
import os.path
import re
import typing

from jinja2 import Environment, FileSystemLoader, select_autoescape

from dynatrace.semconv.model.semantic_convention import (
    SemanticConventionSet,
    SemanticConvention,
)
from dynatrace.semconv.model.utils import ID_RE


def to_doc_brief(doc_string: str) -> str:
    if doc_string is None:
        return ""
    doc_string = doc_string.strip()
    if doc_string.endswith("."):
        return doc_string[:-1]
    return doc_string


def merge(list: typing.List, elm):
    return list.extend(elm)


def to_const_name(name: str) -> str:
    return name.upper().replace(".", "_").replace("-", "_")


def to_camelcase(name: str, first_upper=False) -> str:
    first, *rest = name.replace("_", ".").split(".")
    if first_upper:
        first = first.capitalize()
    return first + "".join(word.capitalize() for word in rest)


class BaseRenderer(abc.ABC):
    pattern = "{{{}}}".format(ID_RE.pattern)
    matcher = re.compile(pattern)

    def get_data_single_file(self, semconvset, template_path: str) -> dict:
        """Returns a dictionary that contains all SemanticConventions to fill the template."""
        return {
            "template": template_path,
            "semconvs": semconvset.models,
            "attributes": semconvset.attributes(),
        }

    def get_data_multiple_files(self, semconv, template_path: str) -> dict:
        """Returns a dictionary with the data from a single SemanticConvention to fill the template."""
        return {"template": template_path, "semconv": semconv}

    @abc.abstractmethod
    def get_auto_escape_extensions(self) -> typing.List[str]:
        pass

    def setup_environment(self, env: Environment):
        env.filters["to_doc_brief"] = to_doc_brief
        env.filters["to_const_name"] = to_const_name
        env.filters["merge"] = merge
        env.filters["to_camelcase"] = to_camelcase

    def prefix_output_file(
        self, file_name: str, pattern: str, semconv: SemanticConvention
    ):
        base = os.path.basename(file_name)
        dir = os.path.dirname(file_name)
        value = getattr(semconv, pattern)
        return dir + "/" + to_camelcase(value, True) + base

    def render(
        self,
        semconvset: SemanticConventionSet,
        template_path: str,
        output_file,
        pattern: str,
    ):
        file_name = os.path.basename(template_path)
        folder = os.path.dirname(template_path)
        env = Environment(
            loader=FileSystemLoader(searchpath=folder),
            autoescape=select_autoescape(self.get_auto_escape_extensions()),
        )
        self.setup_environment(env)
        if pattern:
            semconv: SemanticConvention
            for semconv in semconvset.models.values():
                output_name = self.prefix_output_file(output_file, pattern, semconv)
                data = self.get_data_multiple_files(semconv, template_path)
                template = env.get_template(file_name, data)
                template.globals["now"] = datetime.datetime.utcnow()
                template.globals["version"] = os.environ.get("ARTIFACT_VERSION", "dev")
                template.stream(data).dump(output_name)
        else:
            data = self.get_data_single_file(semconvset, template_path)
            template = env.get_template(file_name, data)
            template.globals["now"] = datetime.datetime.utcnow()
            template.globals["version"] = os.environ.get("ARTIFACT_VERSION", "dev")
            template.stream(data).dump(output_file)
