from re import (
    finditer, findall, compile as compile_, DOTALL, sub, match, search
)
from json import dumps
from os.path import curdir, abspath, join, splitext
from os import walk

rfc_2119_keywords_regexes = [
    r"MUST",
    r"REQUIRED",
    r"SHALL",
    r"MUST NOT",
    r"SHALL NOT",
    r"SHOULD",
    r"RECOMMENDED",
    r"SHOULD NOT",
    r"NOT RECOMMENDED",
    r"MAY",
    r"OPTIONAL",
]


def find_markdown_file_paths(root):
    markdown_file_paths = []

    for root_path, _, file_paths, in walk(root):
        for file_path in file_paths:
            absolute_file_path = join(root_path, file_path)

            _, file_extension = splitext(absolute_file_path)

            if file_extension == ".md":
                markdown_file_paths.append(absolute_file_path)

    return markdown_file_paths


def clean_content(content):

    for rfc_2119_keyword_regex in rfc_2119_keywords_regexes:

        content = sub(
            f"\\*\\*{rfc_2119_keyword_regex}\\*\\*",
            rfc_2119_keyword_regex,
            content
        )

    return sub(r"\n>", "", content)


def find_rfc_2119_keyword(content):

    for rfc_2119_keyword_regex in rfc_2119_keywords_regexes:

        if search(
            f"\\*\\*{rfc_2119_keyword_regex}\\*\\*", content
        ) is not None:
            return rfc_2119_keyword_regex


def parse_requirements(markdown_file_path):

    requirements = []

    with open(markdown_file_path, "r") as markdown_file:

        for requirement in [
            requirement_match.groupdict() for requirement_match in (
                finditer(
                    r"##### (?P<id>Requirement [0-9]+)\n\n"
                    r"> (?P<content>(.*?))\n\n",
                    markdown_file.read(),
                    DOTALL
                )
            )
        ]:

            content = requirement["content"]

            requirements.append(
                {
                    "id": requirement["id"],
                    "content": clean_content(content),
                    "RFC 2119 keyword": find_rfc_2119_keyword(content)
                }
            )

    return requirements


def parse_conditions(markdown_file_path):

    conditions = []

    with open(markdown_file_path, "r") as markdown_file:

        for condition in findall(
            r"##### Condition [0-9]+\n\n.*?\n\n",
            markdown_file.read(),
            DOTALL
        ):

            stack = []

            regex = compile_(
                r"(?P<level>(> ?)*)(?P<pounds>##### )?(?P<content>.*)"
            )

            text = ""

            for line in condition.split("\n"):
                regex_dict = regex.match(line).groupdict()

                level = len(regex_dict["level"].split())
                pounds = regex_dict["pounds"]
                content = regex_dict["content"]

                if not level and not content:
                    continue

                if not pounds:
                    text = "".join([text, content])
                    continue

                if match(
                    r"(> ?)*##### Condition [\.0-9]+", line
                ) is not None:

                    node = {
                        "id": content,
                        "content": "",
                        "children": []
                    }
                else:
                    node = {
                        "id": content,
                        "content": "",
                        "RFC 2119 keyword": None
                    }

                if not stack:
                    stack.append(node)
                    continue

                stack[-1]["content"] = clean_content(text)

                if level == len(stack) - 1:

                    stack[-1]["RFC 2119 keyword"] = find_rfc_2119_keyword(
                        text
                    )
                    stack.pop()

                elif level < len(stack) - 1:
                    stack[-1]["RFC 2119 keyword"] = find_rfc_2119_keyword(
                        text
                    )
                    for _ in range(len(stack) - level):
                        stack.pop()

                text = ""
                from ipdb import set_trace
                try:
                    stack[-1]["children"].append(node)
                except:
                    set_trace()
                stack.append(node)

            stack[-1]["content"] = clean_content(text)
            stack[-1]["RFC 2119 keyword"] = find_rfc_2119_keyword(
                text
            )

            conditions.append(stack[0])

    return conditions


def write_json_specifications(requirements, conditions):
    for md_absolute_file_path, requirement_sections in requirements.items():

        with open(
            "".join([splitext(md_absolute_file_path)[0], ".json"]), "w"
        ) as json_file:
            json_file.write(dumps(requirement_sections, indent=4))


if __name__ == "__main__":

    for markdown_file_path in find_markdown_file_paths(
        join(abspath(curdir), "specification")
    ):

        result = []
        result.extend(parse_requirements(markdown_file_path))
        result.extend(parse_conditions(markdown_file_path))

        if result:
            with open(
                "".join([splitext(markdown_file_path)[0], ".json"]), "w"
            ) as json_file:
                json_file.write(dumps(result, indent=4))
