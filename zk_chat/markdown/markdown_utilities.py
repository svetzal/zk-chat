import json
from typing import Tuple, Dict

import yaml


class MarkdownUtilities:
    """
    Utility class for handling markdown files with metadata sections.
    Supports both JSON and YAML metadata formats.
    """

    @staticmethod
    def load_markdown(document_path: str) -> Tuple[Dict, str]:
        """
        Load a markdown file and split it into metadata and content.

        Parameters
        ----------
        document_path : str
            Path to the markdown file

        Returns
        -------
        Tuple[Dict, str]
            A tuple containing the metadata dictionary and the content string
        """
        with open(document_path, 'r') as file:
            file_content = file.read()
            return MarkdownUtilities.split_metadata_and_content(file_content)

    @staticmethod
    def split_metadata_and_content(file_content: str) -> Tuple[Dict, str]:
        """
        Split the file content into metadata and content sections.

        Parameters
        ----------
        file_content : str
            Raw content of the markdown file

        Returns
        -------
        Tuple[Dict, str]
            A tuple containing the metadata dictionary and the content string
        """
        lines = file_content.split("\n")
        return MarkdownUtilities.separate_metadata_lines_from_content_lines(lines)

    @staticmethod
    def separate_metadata_lines_from_content_lines(lines: list) -> Tuple[Dict, str]:
        """
        Separate metadata and content from the lines of the file.

        Parameters
        ----------
        lines : list
            List of lines from the markdown file

        Returns
        -------
        Tuple[Dict, str]
            A tuple containing the metadata dictionary and the content string
        """
        if not lines[0].startswith("---"):
            return {}, "\n".join(lines)
        try:
            metadata_divider = lines[1:].index("---") + 1
            content = "\n".join(lines[metadata_divider + 1:])
            metadata_str = "\n".join(lines[1:metadata_divider])
            metadata = MarkdownUtilities.parse_metadata(metadata_str)
        except ValueError:  # no metadata markers found
            content = "\n".join(lines)
            metadata = {}
        return metadata, content

    @staticmethod
    def parse_metadata(metadata_str: str) -> Dict:
        """
        Parse metadata string in either JSON or YAML format.

        Parameters
        ----------
        metadata_str : str
            String containing metadata in either JSON or YAML format

        Returns
        -------
        Dict
            Parsed metadata as a dictionary
        """
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