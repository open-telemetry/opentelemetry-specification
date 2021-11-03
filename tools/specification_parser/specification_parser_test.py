from unittest import TestCase
from os.path import abspath, curdir, join

from specification_parser import (
    find_markdown_file_paths,
    parse_requirements,
    parse_conditions
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

    def test_find_markdown_file_paths(self):
        self.assertIn(
            self.test_specification_md_path,
            find_markdown_file_paths(self.current_directory_path)
        )

    def test_parse_requirements(self):
        self.maxDiff = None
        self.assertEqual(
            [
                {
                    "id": "Some requirement",
                    "clean id": "some_requirement",
                    "content": "This MUST be done.",
                    "RFC 2119 keyword": "MUST"
                },
                {
                    "id": "Some other requirement",
                    "clean id": "some_other_requirement",
                    "content": "This MUST NOT be done.",
                    "RFC 2119 keyword": "MUST NOT"
                },
                {
                    "id": "Another requirement-name",
                    "clean id": "another_requirement_name",
                    "content": "This SHOULD be done in a certain way.",
                    "RFC 2119 keyword": "SHOULD"
                },
                {
                    "id": "This is the name of-the-requirement",
                    "clean id": "this_is_the_name_of_the_requirement",
                    "content": "This MUST NOT be done.",
                    "RFC 2119 keyword": "MUST NOT"
                },
            ],
            parse_requirements(self.test_specification_md_path)
        )

    def test_parse_conditions(self):
        self.maxDiff = None
        self.assertEqual(
            [
                {
                    "id": "Condition 1",
                    "content": "This is a condition.",
                    "children": [
                        {
                            "id": "Condition 1.1",
                            "content": "This is a condition.",
                            "children": [
                                {
                                    "id": "Condition 1.1.1",
                                    "content": "This is a condition.",
                                    "children": [
                                        {
                                            "id": "Conditional requirement name",
                                            "clean id": "conditional_requirement_name",
                                            "content": "This MAY be done.",
                                            "RFC 2119 keyword": "MAY"
                                        },
                                        {
                                            "id": "Other name",
                                            "clean id": "other_name",
                                            "content": "This SHOULD NOT be done.",
                                            "RFC 2119 keyword": "SHOULD NOT"
                                        },
                                        {
                                            "id": "Another name here",
                                            "clean id": "another_name_here",
                                            "content": "This MAY be done.",
                                            "RFC 2119 keyword": "MAY"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "id": "Condition 1.2",
                            "content": "This is a condition.",
                            "children": [
                                {
                                    "id": "And another-name",
                                    "clean id": "and_another_name",
                                    "content": "This MUST be done.",
                                    "RFC 2119 keyword": "MUST"
                                }
                            ]
                        }
                    ]
                },
                {
                    "id": "Condition 2",
                    "content": "This is a condition.",
                    "children": [
                        {
                            "id": "Condition 2.1",
                            "content": "This is a condition.",
                            "children": [
                                {
                                    "id": "Condition 2.2",
                                    "content": "This is a condition.",
                                    "children": [
                                        {
                                            "id": "The name here",
                                            "clean id": "the_name_here",
                                            "content": "This MAY be done.",
                                            "RFC 2119 keyword": "MAY"
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ],
            parse_conditions(self.test_specification_md_path)
        )
