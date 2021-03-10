from re import finditer, findall
from json import dumps
from os.path import curdir, abspath, join, splitext
from os import walk


def find_markdown_file_paths(root):
    markdown_file_paths = []

    for root_path, _, file_paths, in walk(root):
        for file_path in file_paths:
            absolute_file_path = join(root_path, file_path)

            _, file_extension = splitext(absolute_file_path)

            if file_extension == ".md":
                markdown_file_paths.append(absolute_file_path)

    return markdown_file_paths


def parse_requirements(markdown_file_paths):
    requirements = {}

    for markdown_file_path in markdown_file_paths:

        with open(markdown_file_path, "r") as markdown_file:

            text = markdown_file.read()

            requirement_matches = [
                requirement_match.groupdict() for requirement_match in (
                    finditer(
                        r"###### requirement:\s(?P<key>[_\w]+)\n\n"
                        r"(?P<description>(>.*\n)+)",
                        text,
                    )
                )
            ]

        if not requirement_matches:
            continue

        md_file_path = "".join([splitext(markdown_file_path)[0], ".md"])

        requirements[md_file_path] = {}

        for requirement in requirement_matches:

            requirement_key = requirement["key"]

            assert (
                requirement_key not in
                requirements[md_file_path].keys()
            ), "Repeated requirement key {} found in {}".format(
                requirement_key, markdown_file_path
            )

            requirement_description = requirement["description"].strip()

            BCP_14_keyword_matches = []

            for BCP_14_keyword_regex in [
                # 2. MUST NOT
                r"MUST NOT",
                r"SHALL NOT",
                # 1. MUST
                r"MUST(?! NOT)",
                r"REQUIRED",
                r"SHALL(?! NOT)",
                # 4. SHOULD NOT
                r"SHOULD NOT",
                r"NOT RECOMMENDED",
                # 3. SHOULD
                r"SHOULD(?! NOT)",
                r"(?<!NOT )RECOMMENDED",
                # 5. MAY
                r"MAY",
                r"OPTIONAL",

            ]:
                BCP_14_keyword_matches.extend(
                    findall(
                        BCP_14_keyword_regex,
                        requirement_description
                    )
                )

            requirement_key_path = "{}:{}".format(
                markdown_file_path, requirement_key
            )

            assert (
                len(BCP_14_keyword_matches) != 0
            ), "No BCP 14 keywords were found in {}".format(
                requirement_key_path
            )

            requirements[md_file_path][requirement_key] = {}

            requirements[md_file_path][requirement_key]["description"] = (
                requirement_description
            )

            BCP_14_keyword_matches.reverse()

            requirements[md_file_path][requirement_key][
                "BCP 14 Keywords"
            ] = BCP_14_keyword_matches

    return requirements


def write_json_specifications(requirements):
    for md_absolute_file_path, requirement_sections in requirements.items():

        with open(
            "".join([splitext(md_absolute_file_path)[0], ".json"]), "w"
        ) as json_file:
            json_file.write(dumps(requirement_sections, indent=4))

if __name__ == "__main__":
    write_json_specifications(
        parse_requirements(
            find_markdown_file_paths(
                join(abspath(curdir), "specification")
            )
        )
    )
