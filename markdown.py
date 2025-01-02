import json


def load_markdown(document_path: str) -> (dict, str):
    with open(document_path, 'r') as file:
        file_content = file.read()
        lines = file_content.split("\n")
        try:
            metadata_divider = lines.index("---")
            if metadata_divider == 0:
                metadata_divider = lines[1:].index("---") + 1
            content = "\n".join(lines[metadata_divider + 1:])
            json_data = "\n".join(lines[1:metadata_divider])
            metadata = json.loads(json_data)
        except ValueError:
            content = "\n".join(lines)
            metadata = {}

        return metadata, content
