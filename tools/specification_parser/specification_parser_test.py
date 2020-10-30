from unittest import TestCase
from os.path import abspath, curdir, join

from specification_parser import (
    find_markdown_file_paths,
    parse_requirements,
)


class TestSpecificationParser(TestCase):
    """
    Tests for the specification parser
    """

    @classmethod
    def setUpClass(cls):
        cls.current_directory_path = abspath(curdir)
        cls.test_specification_md_path = join(
            cls.current_directory_path, "test_specification.md"
        )
        cls.parsed_requirements = parse_requirements(
            [cls.test_specification_md_path]
        )[cls.test_specification_md_path]

    def test_find_markdown_file_paths(self):
        self.assertIn(
            self.test_specification_md_path,
            find_markdown_file_paths(self.current_directory_path)
        )

    def test_requirement_1(self):
        assert self.parsed_requirements["Requirement 1"] == {
            "description": "> This **MUST** be done.",
            "RFC 2119 Keywords": ["MUST"]
        }

    def test_requirement_2(self):
        assert self.parsed_requirements["Requirement 2"] == {
            "description": "> This **MUST NOT** be done.",
            "RFC 2119 Keywords": ["MUST NOT"]
        }

    def test_requirement_3(self):
        assert self.parsed_requirements["Requirement 3"] == {
            "description": "> This **SHOULD** be done\n> in a certain way.",
            "RFC 2119 Keywords": ["SHOULD"]
        }
