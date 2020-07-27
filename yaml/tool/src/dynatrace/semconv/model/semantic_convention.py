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

import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Union, Iterable, Tuple

import typing
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedSeq

from dynatrace.semconv.model.constraints import Include, AnyOf
from dynatrace.semconv.model.exceptions import ValidationError
from dynatrace.semconv.model.semantic_attribute import SemanticAttribute, Required
from dynatrace.semconv.model.utils import validate_values, validate_id


class SpanKind(Enum):
    EMPTY = 1
    CLIENT = 2
    SERVER = 3
    CONSUMER = 4
    PRODUCER = 5
    INTERNAL = 6

    @staticmethod
    def parse(span_kind_value):
        if span_kind_value is None:
            return SpanKind.EMPTY
        kind_map = {
            "client": SpanKind.CLIENT,
            "server": SpanKind.SERVER,
            "producer": SpanKind.PRODUCER,
            "consumer": SpanKind.CONSUMER,
            "internal": SpanKind.INTERNAL,
        }
        return kind_map.get(span_kind_value)


@dataclass
class SemanticConvention:
    """ Contains the model extracted from a yaml file"""

    semconv_id: str
    brief: str
    note: str
    prefix: str
    extends: str
    span_kind: SpanKind
    attrs_by_name: "Dict[str, SemanticAttribute]"
    constraints: "Set[Union[Include, AnyOf]]"
    _position: List[int]

    @property
    def attributes(self):
        return list(self.attrs_by_name.values())

    @staticmethod
    def parse(yaml_file):
        yaml = YAML().load(yaml_file)
        models = []
        available_keys = (
            "id",
            "brief",
            "note",
            "prefix",
            "extends",
            "span_kind",
            "attributes",
            "constraints",
        )
        mandatory_keys = ("id", "brief")
        for group in yaml["groups"]:
            validate_values(group, available_keys, mandatory_keys)
            validate_id(group["id"], group.lc.data["id"])
            span_kind = SpanKind.parse(group.get("span_kind"))
            if span_kind is None:
                position = group.lc.data["span_kind"]
                msg = "Invalid value for span_kind: {}".format(group.get("span_kind"))
                raise ValidationError.from_yaml_pos(position, msg)
            prefix = group.get("prefix", "")
            if prefix != "":
                validate_id(prefix, group.lc.data["prefix"])
            position = group.lc.data["id"]
            model = SemanticConvention(
                semconv_id=group["id"].strip(),
                brief=str(group["brief"]).strip(),
                note=group.get("note", "").strip(),
                prefix=prefix.strip(),
                extends=group.get("extends", "").strip(),
                span_kind=span_kind,
                attrs_by_name=SemanticAttribute.parse(prefix, group.get("attributes"))
                if "attributes" in group
                else {},
                constraints=SemanticConvention.parse_constraint(
                    group.get("constraints", ())
                ),
                _position=position,
            )
            models.append(model)
        return models

    @staticmethod
    def parse_constraint(yaml_constraints):
        """ This method parses the yaml representation for semantic convention attributes
            creating a list of Constraint objects.
        """
        constraints = ()
        allowed_keys = ("include", "any_of")
        for constraint in yaml_constraints:
            validate_values(constraint, allowed_keys)
            if len(constraint.keys()) > 1:
                position = constraint.lc.data[list(constraint)[1]]
                msg = "Invalid entry in constraint array - multiple top-level keys in entry."
                raise ValidationError.from_yaml_pos(position, msg)
            if "include" in constraint:
                constraints += (Include(constraint.get("include")),)
            elif "any_of" in constraint:
                choice_sets = ()
                for constraint_list in constraint.get("any_of"):
                    inner_id_list = ()
                    if isinstance(constraint_list, CommentedSeq):
                        inner_id_list = tuple(
                            attr_constraint for attr_constraint in constraint_list
                        )
                    else:
                        inner_id_list += (constraint_list,)
                    choice_sets += (inner_id_list,)
                constraints += (AnyOf(choice_sets),)
        return constraints

    def contains_attribute(self, attr: "SemanticAttribute"):
        for local_attr in self.attributes:
            if local_attr.attr_id is not None:
                if local_attr.fqn == attr.fqn:
                    return True
            if local_attr == attr:
                return True
        return False

    def all_attributes(self):
        attr: SemanticAttribute
        return SemanticConvention.unique_attr(
            [attr for attr in self.attributes] + self.conditional_attributes()
        )

    def sampling_attributes(self):
        attr: SemanticAttribute
        return SemanticConvention.unique_attr(
            [attr for attr in self.attributes if attr.sampling_relevant]
        )

    def required_attributes(self):
        attr: SemanticAttribute
        return SemanticConvention.unique_attr(
            [attr for attr in self.attributes if attr.required == Required.ALWAYS]
        )

    def conditional_attributes(self):
        attr: SemanticAttribute
        return SemanticConvention.unique_attr(
            [attr for attr in self.attributes if attr.required == Required.CONDITIONAL]
        )

    @staticmethod
    def unique_attr(l: list) -> list:
        output = []
        for x in l:
            if x.fqn not in [attr.fqn for attr in output]:
                output.append(x)
        return output

    def any_of(self):
        result = []
        for constraint in self.constraints:
            if isinstance(constraint, AnyOf):
                result.append(constraint)
        return result

    def has_attribute_constraint(self, attr):
        return any(
            attribute.equivalent_to(attr)
            for constraint in self.constraints
            if isinstance(constraint, AnyOf)
            for attr_list in constraint.choice_list_attributes
            for attribute in attr_list
        )


@dataclass
class SemanticConventionSet:
    """ Contains the list of models.
        From this structure we will generate md/constants/etc with a pretty print of the structure.
    """

    debug: bool
    models: typing.Dict[str, SemanticConvention] = field(default_factory=dict)
    errors: bool = False

    def parse(self, file):
        with open(file, "r", encoding="utf-8") as yaml_file:
            try:
                semconv_models = SemanticConvention.parse(yaml_file)
                for model in semconv_models:
                    if model.semconv_id in self.models:
                        self.errors = True
                        print("Error parsing {}\n".format(file), file=sys.stderr)
                        print(
                            "Semantic convention '{}' is already defined.".format(
                                model.semconv_id
                            ),
                            file=sys.stderr,
                        )
                    self.models[model.semconv_id] = model
            except ValidationError as e:
                self.errors = True
                print("Error parsing {}\n".format(file), file=sys.stderr)
                print(e, file=sys.stderr)

    def has_error(self):
        return self.errors

    def check_unique_fqns(self):
        group_by_fqn: typing.Dict[str, str] = {}
        for model in self.models.values():
            for attr in model.attributes:
                if not attr.ref:
                    if group_by_fqn.get(attr.fqn):
                        self.errors = True
                        print(
                            "Attribute {} of Semantic convention '{}' is already defined in {}.".format(
                                attr.fqn, model.semconv_id, group_by_fqn.get(attr.fqn)
                            ),
                            file=sys.stderr,
                        )
                    group_by_fqn[attr.fqn] = model.semconv_id

    def finish(self):
        """ Resolves values referenced from other models using `ref` and `extends` attributes AFTER all models were parsed.
            Here, sanity checks for `ref/extends` attributes are performed.
        """
        semconv: SemanticConvention
        # Before resolving attributes, we verify that no duplicate exists.
        self.check_unique_fqns()
        fixpoint = False
        index = 0
        tmp_debug = self.debug
        # This is a hot spot for optimizations
        while not fixpoint:
            fixpoint = True
            if index > 0:
                self.debug = False
            for semconv in self.models.values():
                # Ref first, extends and includes after!
                fixpoint_ref = self.resolve_ref(semconv)
                fixpoint_inc = self.resolve_include(semconv)
                fixpoint = fixpoint and fixpoint_ref and fixpoint_inc
            index += 1
        self.debug = tmp_debug
        # After we resolve any local dependency, we can resolve parent/child relationship
        self._populate_extends()
        # From string containing attribute ids to SemanticAttribute objects
        self._populate_anyof_attributes()

    def _populate_extends(self):
        """
        This internal method goes through every semantic convention to resolve parent/child relationships.
        :return: None
        """
        unprocessed: typing.Dict[str, SemanticConvention]
        unprocessed = self.models.copy()
        # Iterate through the list and remove the semantic conventions that have been processed.
        while len(unprocessed) > 0:
            semconv = next(iter(unprocessed.values()))
            self._populate_extends_single(semconv, unprocessed)

    def _populate_extends_single(
        self,
        semconv: SemanticConvention,
        unprocessed: typing.Dict[str, SemanticConvention],
    ):
        """
        Resolves the parent/child relationship for a single Semantic Convention. If the parent **p** of the input
        semantic convention **i** has in turn a parent **pp**, it recursively resolves **pp** before processing **p**.
        :param semconv: The semantic convention for which resolve the parent/child relationship.
        :param semconvs: The list of remaining semantic conventions to process.
        :return: A list of remaining semantic convention to process.
        """
        # Resolve parent of current Semantic Convention
        if semconv.extends:
            extended = self.models.get(semconv.extends)
            if extended is None:
                raise ValidationError.from_yaml_pos(
                    semconv._position,
                    "Semantic Convention {} extends {} but the latter cannot be found!".format(
                        semconv.semconv_id, semconv.extends
                    ),
                )
            # TODO: add inheritance of constraints
            for constraint in extended.constraints:
                if constraint not in semconv.constraints and isinstance(
                    constraint, AnyOf
                ):
                    semconv.constraints += (constraint.import_anyof(),)
            # Process hierarchy chain
            not_yet_processed = extended.extends in unprocessed
            if extended.extends and not_yet_processed:
                # Recursion on parent if was not already processed
                parent_extended = self.models.get(extended.extends)
                self._populate_extends_single(parent_extended, unprocessed)

            # inherit prefix and constraints
            if not semconv.prefix:
                semconv.prefix = extended.prefix
            # Attributes
            parent_attributes = {}
            for ext_attr in extended.attrs_by_name.values():
                parent_attributes[ext_attr.fqn] = ext_attr.inherit_attribute()
            # By induction, parent semconv is already correctly sorted
            parent_attributes.update(
                SemanticConventionSet._sort_attributes_dict(semconv.attrs_by_name)
            )
            semconv.attrs_by_name = parent_attributes
        else:  # No parent, sort of current attributes
            semconv.attrs_by_name = SemanticConventionSet._sort_attributes_dict(
                semconv.attrs_by_name
            )
        # delete from remaining semantic conventions to process
        del unprocessed[semconv.semconv_id]

    @staticmethod
    def _sort_attributes_dict(
        attributes: typing.Dict[str, SemanticAttribute]
    ) -> typing.Dict[str, SemanticAttribute]:
        """
        First  imported, and then defined attributes.
        :param attributes: Dictionary of attributes to sort
        :return: A sorted dictionary of attributes
        """
        return dict(
            sorted(attributes.items(), key=lambda kv: 0 if kv[1].imported else 1)
        )

    def _populate_anyof_attributes(self):
        any_of: AnyOf
        for semconv in self.models.values():
            for any_of in semconv.constraints:
                if isinstance(any_of, AnyOf):
                    for attr_ids in any_of.choice_list_ids:
                        constraint_attrs = []
                        for attr_id in attr_ids:
                            ref_attr = self._lookup_attribute(attr_id)
                            if ref_attr is not None:
                                constraint_attrs.append(ref_attr)
                        if constraint_attrs:
                            any_of.add_attributes(constraint_attrs)

    def resolve_ref(self, semconv: SemanticConvention):
        fixpoint_ref = True
        attr: SemanticAttribute
        for attr in semconv.attributes:
            if attr.ref is not None and attr.attr_id is None:
                # There are changes
                fixpoint_ref = False
                ref_attr = self._lookup_attribute(attr.ref)
                if not ref_attr:
                    raise ValidationError.from_yaml_pos(
                        semconv._position,
                        "Semantic Convention {} reference `{}` but it cannot be found!".format(
                            semconv.semconv_id, attr.ref
                        ),
                    )
                attr.attr_type = ref_attr.attr_type
                if not attr.brief:
                    attr.brief = ref_attr.brief
                if not attr.note:
                    attr.note = ref_attr.note
                if attr.examples is None:
                    attr.examples = ref_attr.examples
                attr.attr_id = attr.ref
        return fixpoint_ref

    def resolve_include(self, semconv: SemanticConvention):
        fixpoint_inc = True
        for constraint in semconv.constraints:
            if isinstance(constraint, Include):
                include_semconv: SemanticConvention
                include_semconv = self.models.get(constraint.semconv_id)
                # include required attributes and constraints
                if include_semconv is None:
                    raise ValidationError.from_yaml_pos(
                        semconv._position,
                        "Semantic Convention {} includes {} but the latter cannot be found!".format(
                            semconv.semconv_id, constraint.semconv_id
                        ),
                    )
                # We resolve the parent/child relationship of the included semantic convention, if any
                self._populate_extends_single(
                    include_semconv, {include_semconv.semconv_id: include_semconv}
                )
                attr: SemanticAttribute
                for attr in include_semconv.attributes:
                    if semconv.contains_attribute(attr):
                        if self.debug:
                            print(
                                "[Includes] {} already contains attribute {}".format(
                                    semconv.semconv_id, attr
                                )
                            )
                        continue
                    # There are changes
                    fixpoint_inc = False
                    semconv.attrs_by_name[attr.fqn] = attr.import_attribute()
                for inc_constraint in include_semconv.constraints:
                    if (
                        isinstance(inc_constraint, Include)
                        or inc_constraint in semconv.constraints
                    ):
                        # We do not include "include" constraint or the constraint was already imported
                        continue
                    # We know the type of the constraint
                    inc_constraint: AnyOf
                    # There are changes
                    fixpoint_inc = False
                    semconv.constraints += (inc_constraint.import_anyof(),)
        return fixpoint_inc

    def _lookup_attribute(self, attr_id: str) -> Union[SemanticAttribute, None]:
        return next(
            (
                attr
                for model in self.models.values()
                for attr in model.attributes
                if attr.fqn == attr_id and attr.ref is None
            ),
            None,
        )

    def attributes(self):
        output = []
        for semconv in self.models.values():
            output.extend(semconv.attributes)
        return output
