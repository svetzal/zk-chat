import pytest
from markdown.loader import split_metadata_and_content

@pytest.fixture
def file_content_with_json_metadata():
    return """---
{
    "title": "Sample Document",
    "author": "John Doe"
}
---
This is the content of the document."""

@pytest.fixture
def file_content_with_yaml_metadata():
    return """---
title: Sample Document
author: John Doe
---
This is the content of the document."""

@pytest.fixture
def file_content_with_incorrect_metadata_start_marker():
    return """--
title: Sample Document
author: John Doe
---
This is the content of the document."""

@pytest.fixture
def file_content_with_incorrect_metadata_end_marker():
    return """---
title: Sample Document
author: John Doe
--
This is the content of the document."""

@pytest.fixture
def file_content_without_metadata():
    return "This is the content of the document without metadata."

@pytest.fixture
def file_content_with_no_content():
    return """---
{
    "title": "Sample Document",
    "author": "John Doe"
}
---"""

@pytest.fixture
def file_content_empty():
    return ""

def test_split_metadata_and_content_with_json_metadata(file_content_with_json_metadata):
    expected_metadata = {
        "title": "Sample Document",
        "author": "John Doe"
    }
    expected_content = "This is the content of the document."
    metadata, content = split_metadata_and_content(file_content_with_json_metadata)
    assert metadata == expected_metadata
    assert content == expected_content

def test_split_metadata_and_content_with_yaml_metadata(file_content_with_yaml_metadata):
    expected_metadata = {
        "title": "Sample Document",
        "author": "John Doe"
    }
    expected_content = "This is the content of the document."
    metadata, content = split_metadata_and_content(file_content_with_yaml_metadata)
    assert metadata == expected_metadata
    assert content == expected_content

def test_split_metadata_and_content_with_incorrect_metadata_start_marker(
        file_content_with_incorrect_metadata_start_marker):
    expected_metadata = {'author': 'John Doe', 'title': 'Sample Document'}
    expected_content = """This is the content of the document."""
    metadata, content = split_metadata_and_content(file_content_with_incorrect_metadata_start_marker)
    assert metadata == expected_metadata
    assert content == expected_content

def test_split_metadata_and_content_with_incorrect_metadata_end_marker(
        file_content_with_incorrect_metadata_end_marker):
    expected_metadata = {}
    expected_content = """---
title: Sample Document
author: John Doe
--
This is the content of the document."""
    metadata, content = split_metadata_and_content(file_content_with_incorrect_metadata_end_marker)
    assert metadata == expected_metadata
    assert content == expected_content

def test_split_metadata_and_content_without_metadata(file_content_without_metadata):
    expected_metadata = {}
    expected_content = "This is the content of the document without metadata."
    metadata, content = split_metadata_and_content(file_content_without_metadata)
    assert metadata == expected_metadata
    assert content == expected_content

def test_split_metadata_and_content_with_no_content(file_content_with_no_content):
    expected_metadata = {
        "title": "Sample Document",
        "author": "John Doe"
    }
    expected_content = ""
    metadata, content = split_metadata_and_content(file_content_with_no_content)
    assert metadata == expected_metadata
    assert content == expected_content

def test_split_metadata_and_content_with_empty_file(file_content_empty):
    expected_metadata = {}
    expected_content = ""
    metadata, content = split_metadata_and_content(file_content_empty)
    assert metadata == expected_metadata
    assert content == expected_content