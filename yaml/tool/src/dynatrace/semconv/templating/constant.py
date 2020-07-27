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


import typing

from dynatrace.semconv.model.semantic_convention import (
    SemanticConvention,
    SemanticConventionSet,
)
from dynatrace.semconv.templating.jinja import BaseRenderer


class JavaRenderer(BaseRenderer):
    def __init__(self, pkg_name: str, class_name: str):
        self.pkg_name = pkg_name
        self.class_name = class_name

    def get_data_single_file(
        self, semconvset: SemanticConventionSet, template_path: str
    ) -> dict:
        data = super().get_data_single_file(semconvset, template_path)
        data.update(
            {"pkg": self.pkg_name, "class_name": self.class_name,}
        )
        return data

    def get_data_multiple_files(
        self, semconv: SemanticConvention, template_path: str
    ) -> dict:
        data = super().get_data_multiple_files(semconv, template_path)
        data.update(
            {"pkg": self.pkg_name, "class_name": self.class_name,}
        )
        return data

    def get_auto_escape_extensions(self) -> typing.List[str]:
        return ["java.j2"]


class PythonRenderer(BaseRenderer):
    def get_auto_escape_extensions(self) -> typing.List[str]:
        return ["py.j2"]


class CppRenderer(BaseRenderer):
    def __init__(self, namespace: str):
        self.namespace = namespace

    def get_data_single_file(self, semconvset, template_path: str) -> dict:
        data = super().get_data_single_file(semconvset, template_path)
        data.update(
            {"namespace": self.namespace,}
        )
        return data

    def get_data_multiple_files(self, semconv, template_path: str) -> dict:
        data = super().get_data_multiple_files(semconv, template_path)
        data.update(
            {"namespace": self.namespace,}
        )
        return data

    def get_auto_escape_extensions(self) -> typing.List[str]:
        return ["cpp.j2"]


class TypeScriptRenderer(BaseRenderer):
    def get_auto_escape_extensions(self) -> typing.List[str]:
        return ["ts.j2"]
