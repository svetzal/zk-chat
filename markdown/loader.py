import json

import yaml


def load_markdown(document_path: str) -> (dict, str):
    with open(document_path, 'r') as file:
        file_content = file.read()
        return split_metadata_and_content(file_content)


def split_metadata_and_content(file_content):
    lines = file_content.split("\n")
    return separate_metadata_lines_from_content_lines(lines)


def separate_metadata_lines_from_content_lines(lines):
    if not lines[0].startswith("---"):
        return {}, "\n".join(lines)
    try:
        metadata_divider = lines[1:].index("---") + 1
        content = "\n".join(lines[metadata_divider + 1:])
        metadata_str = "\n".join(lines[1:metadata_divider])
        metadata = parse_metadata(metadata_str)
    except ValueError:  # no metadata markers found
        content = "\n".join(lines)
        metadata = {}
    return metadata, content


def parse_metadata(metadata_str):
    try:
        metadata = json.loads(metadata_str)
    except json.JSONDecodeError:
        try:
            metadata = yaml.safe_load(metadata_str)
        except yaml.YAMLError:
            metadata = {}
    if metadata is None:
        metadata = {}
    return metadata
