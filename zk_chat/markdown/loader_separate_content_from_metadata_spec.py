import pytest

from zk_chat.markdown.loader import split_metadata_and_content


class DescribeContentSeparator:
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

    def should_extract_json_metadata_and_content_correctly(self, file_content_with_json_metadata):
        expected_metadata = {
            "title": "Sample Document",
            "author": "John Doe"
        }
        expected_content = "This is the content of the document."
        metadata, content = split_metadata_and_content(file_content_with_json_metadata)
        assert metadata == expected_metadata
        assert content == expected_content

    def should_extract_yaml_metadata_and_content_correctly(self, file_content_with_yaml_metadata):
        expected_metadata = {
            "title": "Sample Document",
            "author": "John Doe"
        }
        expected_content = "This is the content of the document."
        metadata, content = split_metadata_and_content(file_content_with_yaml_metadata)
        assert metadata == expected_metadata
        assert content == expected_content

    def should_treat_incorrect_start_marker_as_content(self, file_content_with_incorrect_metadata_start_marker):
        expected_metadata = {}
        expected_content = """--
title: Sample Document
author: John Doe
---
This is the content of the document."""
        metadata, content = split_metadata_and_content(file_content_with_incorrect_metadata_start_marker)
        assert metadata == expected_metadata
        assert content == expected_content

    def should_treat_incorrect_end_marker_as_content(self, file_content_with_incorrect_metadata_end_marker):
        expected_metadata = {}
        expected_content = """---
title: Sample Document
author: John Doe
--
This is the content of the document."""
        metadata, content = split_metadata_and_content(file_content_with_incorrect_metadata_end_marker)
        assert metadata == expected_metadata
        assert content == expected_content

    def should_handle_content_without_metadata(self, file_content_without_metadata):
        expected_metadata = {}
        expected_content = "This is the content of the document without metadata."
        metadata, content = split_metadata_and_content(file_content_without_metadata)
        assert metadata == expected_metadata
        assert content == expected_content

    def should_handle_metadata_without_content(self, file_content_with_no_content):
        expected_metadata = {
            "title": "Sample Document",
            "author": "John Doe"
        }
        expected_content = ""
        metadata, content = split_metadata_and_content(file_content_with_no_content)
        assert metadata == expected_metadata
        assert content == expected_content

    def should_handle_empty_file(self, file_content_empty):
        expected_metadata = {}
        expected_content = ""
        metadata, content = split_metadata_and_content(file_content_empty)
        assert metadata == expected_metadata
        assert content == expected_content

    def should_preserve_separators_in_content_when_no_metadata(self,
            file_content_with_no_metadata_and_separators_in_body_content):
        expected_metadata = {}
        expected_content = """This is part one of the content.
---
This is part two of the content."""
        metadata, content = split_metadata_and_content(file_content_with_no_metadata_and_separators_in_body_content)
        assert metadata == expected_metadata
        assert content == expected_content
