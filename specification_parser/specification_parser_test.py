from unittest import TestCase
from os.path import abspath, curdir, join

from specification_parser import (
    find_markdown_file_paths,
    parse_requirements,
)


class TestSpecificationParser(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.current_directory_path = abspath(curdir)
        cls.test_specification_md_path = join(
            cls.current_directory_path, "test_specification.md"
        )

    def test_find_markdown_file_paths(self):

        self.assertEqual(
            find_markdown_file_paths(self.current_directory_path),
            [self.test_specification_md_path]
        )

    def test_parse_requirements(self):

        assert parse_requirements([self.test_specification_md_path]) == {
            (
                "/home/ocelotl/ocelotl/opentelemetry-specification/"
                "specification_parser/test_specification.json"
            ): {
                "testable_section_0": {
                    "description": "> This MUST be done.",
                    "RFC 2119 Keyword": "MUST"
                },
                "testable_section_1": {
                    "description": "> This MUST NOT be done.",
                    "RFC 2119 Keyword": "MUST NOT"
                },
                "testable_section_2": {
                    "description": "> This SHOULD be done.",
                    "RFC 2119 Keyword": "SHOULD"
                },
                "testable_section_3": {
                    "description": "> This SHOULD NOT be done.",
                    "RFC 2119 Keyword": "SHOULD NOT"
                },
                "testable_section_4": {
                    "description": "> This MAY be done.",
                    "RFC 2119 Keyword": "MAY"
                },
                "testable_section_5": {
                    "description": "> This **MAY** be done 5.",
                    "RFC 2119 Keyword": "MAY"
                },
                "testable_section_6": {
                    "description": "> This *MAY* be done 6.",
                    "RFC 2119 Keyword": "MAY"
                },
                "testable_section_7": {
                    "description": (
                        "> This *MAY* be done 7.\n> This is section 7."
                    ),
                    "RFC 2119 Keyword": "MAY"
                },
                "testable_section_8": {
                    "description": "> This *MAY* be done 8.",
                    "RFC 2119 Keyword": "MAY"
                },
                "testable_section_9": {
                    "description": (
                        "> This *MAY* be done 9.\n>\n> This is section 9.\n"
                        "> 1. Item 1\n> 2. Item 2\n>    1. Item 2.1\n"
                        ">    2. Item 2.2"
                    ),
                    "RFC 2119 Keyword": "MAY"
                }
            }
        }
