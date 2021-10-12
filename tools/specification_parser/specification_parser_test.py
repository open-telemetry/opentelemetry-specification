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
        self.assertEqual(
            [
                {
                    "id": "Requirement 1",
                    "content": "This MUST be done.",
                    "RFC 2119 keyword": "MUST"
                },
                {
                    "id": "Requirement 2",
                    "content": "This MUST NOT be done.",
                    "RFC 2119 keyword": "MUST NOT"
                },
                {
                    "id": "Requirement 3",
                    "content": "This SHOULD be done in a certain way.",
                    "RFC 2119 keyword": "SHOULD"
                },
                {
                    "id": "Requirement 4",
                    "content": "This MUST NOT be done.",
                    "RFC 2119 keyword": "MUST NOT"
                },
            ],
            parse_requirements([self.test_specification_md_path])
        )

    def test_parse_conditions(self):
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
                                            "id": "Conditional Requirement 1.1.1.1",
                                            "content": "This MAY be done.",
                                            "RFC 2119 keyword": "MAY"
                                        },
                                        {
                                            "id": "Conditional Requirement 1.1.1.2",
                                            "content": "This SHOULD NOT be done.",
                                            "RFC 2119 keyword": "SHOULD NOT"
                                        },
                                        {
                                            "id": "Conditional Requirement 1.1.1.3",
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
                                    "id": "Conditional Requirement 1.2.1",
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
                                            "id": "Conditional Requirement 2.2.1",
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
            parse_conditions([self.test_specification_md_path])
        )
