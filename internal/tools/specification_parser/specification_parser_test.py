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

    def test_parseable_section_0(self):
        assert self.parsed_requirements["parseable_section_0"] == {
            "description": "> This MUST be done.",
            "BCP 14 Keywords": ["MUST"]
        }

    def test_parseable_section_1(self):
        assert self.parsed_requirements["parseable_section_1"] == {
            "description": "> This MUST NOT be done.",
            "BCP 14 Keywords": ["MUST NOT"]
        }

    def test_parseable_section_2(self):
        assert self.parsed_requirements["parseable_section_2"] == {
            "description": "> This SHOULD be done.",
            "BCP 14 Keywords": ["SHOULD"]
        }

    def test_parseable_section_3(self):
        assert self.parsed_requirements["parseable_section_3"] == {
            "description": "> This SHOULD NOT be done.",
            "BCP 14 Keywords": ["SHOULD NOT"]
        }

    def test_parseable_section_4(self):
        assert self.parsed_requirements["parseable_section_4"] == {
            "description": "> This MAY be done.",
            "BCP 14 Keywords": ["MAY"]
        }

    def test_parseable_section_5(self):
        assert self.parsed_requirements["parseable_section_5"] == {
            "description": "> This **MAY** be done 5.",
            "BCP 14 Keywords": ["MAY"]
        }

    def test_parseable_section_6(self):
        assert self.parsed_requirements["parseable_section_6"] == {
            "description": "> This *MAY* be done 6.",
            "BCP 14 Keywords": ["MAY"]
        }

    def test_parseable_section_7(self):
        assert self.parsed_requirements["parseable_section_7"] == {
            "description": (
                "> This *MAY* be done 7.\n> This is section 7."
            ),
            "BCP 14 Keywords": ["MAY"]
        }

    def test_parseable_section_8(self):
        assert self.parsed_requirements["parseable_section_8"] == {
            "description": "> This *MAY* be done 8.\n>\n> This is section 8.",
            "BCP 14 Keywords": ["MAY"]
        }

    def test_parseable_section_9(self):
        assert self.parsed_requirements["parseable_section_9"] == {
            "description": (
                "> This *MAY* be done 9.\n>\n> This is section 9.\n>\n"
                "> 1. Item 1\n> 2. Item 2\n>    1. Item 2.1\n"
                ">    2. Item 2.2"
            ),
            "BCP 14 Keywords": ["MAY"]
        }

    def test_parseable_section_10(self):
        assert self.parsed_requirements["parseable_section_10"] == {
            "description": (
                "> This *MAY* be done 10\n>\n> If this is done, then this "
                "MUST be that and MUST NOT be\n> something else."
            ),
            "BCP 14 Keywords": ["MAY", "MUST", "MUST NOT"]
        }
