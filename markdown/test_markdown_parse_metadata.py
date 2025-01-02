import pytest

from markdown.markdown import parse_metadata


@pytest.fixture
def json_metadata_str():
    return '{"title": "Sample Document", "author": "John Doe"}'

@pytest.fixture
def yaml_metadata_str():
    return 'title: Sample Document\nauthor: John Doe'

@pytest.fixture
def invalid_metadata_str():
    return 'title: Sample Document\nauthor: John Doe\n---\nInvalid'

@pytest.fixture
def empty_metadata_str():
    return ''

def test_parse_metadata_with_json(json_metadata_str):
    expected_metadata = {
        "title": "Sample Document",
        "author": "John Doe"
    }
    metadata = parse_metadata(json_metadata_str)
    assert metadata == expected_metadata

def test_parse_metadata_with_yaml(yaml_metadata_str):
    expected_metadata = {
        "title": "Sample Document",
        "author": "John Doe"
    }
    metadata = parse_metadata(yaml_metadata_str)
    assert metadata == expected_metadata

def test_parse_metadata_with_invalid_metadata(invalid_metadata_str):
    expected_metadata = {}
    metadata = parse_metadata(invalid_metadata_str)
    assert metadata == expected_metadata

def test_parse_metadata_with_empty_metadata(empty_metadata_str):
    expected_metadata = None
    metadata = parse_metadata(empty_metadata_str)
    assert metadata == expected_metadata