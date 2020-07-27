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

from dataclasses import dataclass, field, replace
from typing import List, Tuple, Set

from dynatrace.semconv.model.semantic_attribute import SemanticAttribute


# We cannot frozen due to later evaluation of the attributes
@dataclass
class AnyOf:
    """Defines a constraint where at least one of the list of attributes must be set.
    The implementation of this class is evaluated in two times. At parsing time, the choice_list_ids field is
    populated. After all yaml files are parsed, the choice_list_attributes field is populated with the object
    representation of the attribute ids of choice_list_ids.

    Attributes:
        choice_list_ids             Contains the lists of attributes ids that must be set.
        imported                    True if it is inherited by another semantic convention, i.e. by include or extends.
        choice_list_attributes      Contains the list of attributes objects. This list contains the same lists of
                                    attributes of choice_list_ids but instead of the ids, it contains the respective
                                    objects representations.
    """

    choice_list_ids: Tuple[Tuple[str, ...]]
    imported: bool = False
    choice_list_attributes: Tuple[Tuple[SemanticAttribute, ...]] = ()

    def __eq__(self, other):
        if not isinstance(other, AnyOf):
            return False
        return self.choice_list_ids == other.choice_list_ids

    def __hash__(self):
        return hash(self.choice_list_ids)

    def add_attributes(self, attr: List[SemanticAttribute]):
        self.choice_list_attributes += (attr,)

    def import_anyof(self):
        return replace(self, imported=True)


@dataclass(frozen=True)
class Include:
    semconv_id: str
