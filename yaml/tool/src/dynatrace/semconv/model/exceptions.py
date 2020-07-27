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


class ValidationError(Exception):
    """ Exception raised if validation errors occur
    Attributes:
        line -- line in the file where the error occurred
        column -- column in the file where the error occurred
        message -- reason of the error
    """

    @classmethod
    def from_yaml_pos(cls, pos, msg):
        # the yaml parser starts counting from 0
        # while in document is usually reported starting from 1
        return cls(pos[0] + 1, pos[1] + 1, msg)

    def __init__(self, line, column, message):
        super(ValidationError, self).__init__(line, column, message)
        self.message = message
        self.line = line
        self.column = column

    def __str__(self):
        return "{} - @{}:{}".format(self.message, self.line, self.column)
