import pytest

from zk_chat.markdown.markdown_utilities import MarkdownUtilities


class DescribeMarkdownUtilities:
    """
    Tests for the MarkdownUtilities class which handles markdown file operations
    """

    @pytest.fixture
    def json_metadata_str(self):
        return '{"title": "Sample Document", "author": "John Doe"}'

    @pytest.fixture
    def yaml_metadata_str(self):
        return 'title: Sample Document\nauthor: John Doe'

    @pytest.fixture
    def invalid_metadata_str(self):
        return 'title: Sample Document\nauthor: John Doe\n---\nInvalid'

    @pytest.fixture
    def empty_metadata_str(self):
        return ''

    @pytest.fixture
    def file_content_with_json_metadata(self):
        return """---
{
    "title": "Sample Document",
    "author": "John Doe"
}
---
This is the content of the document."""

    @pytest.fixture
    def file_content_with_yaml_metadata(self):
        return """---
title: Sample Document
author: John Doe
---
This is the content of the document."""

    @pytest.fixture
    def file_content_with_incorrect_metadata_start_marker(self):
        return """--
title: Sample Document
author: John Doe
---
This is the content of the document."""

    @pytest.fixture
    def file_content_with_incorrect_metadata_end_marker(self):
        return """---
title: Sample Document
author: John Doe
--
This is the content of the document."""

    @pytest.fixture
    def file_content_without_metadata(self):
        return "This is the content of the document without metadata."

    @pytest.fixture
    def file_content_with_no_content(self):
        return """---
{
    "title": "Sample Document",
    "author": "John Doe"
}
---"""

    @pytest.fixture
    def file_content_with_no_metadata_and_separators_in_body_content(self):
        return """This is part one of the content.
---
This is part two of the content."""

    @pytest.fixture
    def file_content_empty(self):
        return ""

    def should_parse_json_metadata_correctly(self, json_metadata_str):
        expected_metadata = {
            "title": "Sample Document",
            "author": "John Doe"
        }
        metadata = MarkdownUtilities.parse_metadata(json_metadata_str)
        assert metadata == expected_metadata

    def should_parse_yaml_metadata_correctly(self, yaml_metadata_str):
        expected_metadata = {
            "title": "Sample Document",
            "author": "John Doe"
        }
        metadata = MarkdownUtilities.parse_metadata(yaml_metadata_str)
        assert metadata == expected_metadata

    def should_return_empty_dict_for_invalid_metadata(self, invalid_metadata_str):
        expected_metadata = {}
        metadata = MarkdownUtilities.parse_metadata(invalid_metadata_str)
        assert metadata == expected_metadata

    def should_return_empty_dict_for_empty_metadata(self, empty_metadata_str):
        expected_metadata = {}
        metadata = MarkdownUtilities.parse_metadata(empty_metadata_str)
        assert metadata == expected_metadata

    def should_extract_json_metadata_and_content_correctly(self, file_content_with_json_metadata):
        expected_metadata = {
            "title": "Sample Document",
            "author": "John Doe"
        }
        expected_content = "This is the content of the document."
        metadata, content = MarkdownUtilities.split_metadata_and_content(file_content_with_json_metadata)
        assert metadata == expected_metadata
        assert content == expected_content

    def should_extract_yaml_metadata_and_content_correctly(self, file_content_with_yaml_metadata):
        expected_metadata = {
            "title": "Sample Document",
            "author": "John Doe"
        }
        expected_content = "This is the content of the document."
        metadata, content = MarkdownUtilities.split_metadata_and_content(file_content_with_yaml_metadata)
        assert metadata == expected_metadata
        assert content == expected_content

    def should_treat_incorrect_start_marker_as_content(self, file_content_with_incorrect_metadata_start_marker):
        expected_metadata = {}
        expected_content = """--
title: Sample Document
author: John Doe
---
This is the content of the document."""
        metadata, content = MarkdownUtilities.split_metadata_and_content(file_content_with_incorrect_metadata_start_marker)
        assert metadata == expected_metadata
        assert content == expected_content

    def should_treat_incorrect_end_marker_as_content(self, file_content_with_incorrect_metadata_end_marker):
        expected_metadata = {}
        expected_content = """---
title: Sample Document
author: John Doe
--
This is the content of the document."""
        metadata, content = MarkdownUtilities.split_metadata_and_content(file_content_with_incorrect_metadata_end_marker)
        assert metadata == expected_metadata
        assert content == expected_content

    def should_handle_content_without_metadata(self, file_content_without_metadata):
        expected_metadata = {}
        expected_content = "This is the content of the document without metadata."
        metadata, content = MarkdownUtilities.split_metadata_and_content(file_content_without_metadata)
        assert metadata == expected_metadata
        assert content == expected_content

    def should_handle_metadata_without_content(self, file_content_with_no_content):
        expected_metadata = {
            "title": "Sample Document",
            "author": "John Doe"
        }
        expected_content = ""
        metadata, content = MarkdownUtilities.split_metadata_and_content(file_content_with_no_content)
        assert metadata == expected_metadata
        assert content == expected_content

    def should_handle_empty_file(self, file_content_empty):
        expected_metadata = {}
        expected_content = ""
        metadata, content = MarkdownUtilities.split_metadata_and_content(file_content_empty)
        assert metadata == expected_metadata
        assert content == expected_content

    def should_preserve_separators_in_content_when_no_metadata(self,
            file_content_with_no_metadata_and_separators_in_body_content):
        expected_metadata = {}
        expected_content = """This is part one of the content.
---
This is part two of the content."""
        metadata, content = MarkdownUtilities.split_metadata_and_content(file_content_with_no_metadata_and_separators_in_body_content)
        assert metadata == expected_metadata
        assert content == expected_content