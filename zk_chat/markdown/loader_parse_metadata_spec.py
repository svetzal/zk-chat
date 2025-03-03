import pytest

from zk_chat.markdown.loader import parse_metadata


class DescribeMetadataParser:
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

    def should_parse_json_metadata_correctly(self, json_metadata_str):
        expected_metadata = {
            "title": "Sample Document",
            "author": "John Doe"
        }
        metadata = parse_metadata(json_metadata_str)
        assert metadata == expected_metadata

    def should_parse_yaml_metadata_correctly(self, yaml_metadata_str):
        expected_metadata = {
            "title": "Sample Document",
            "author": "John Doe"
        }
        metadata = parse_metadata(yaml_metadata_str)
        assert metadata == expected_metadata

    def should_return_empty_dict_for_invalid_metadata(self, invalid_metadata_str):
        expected_metadata = {}
        metadata = parse_metadata(invalid_metadata_str)
        assert metadata == expected_metadata

    def should_return_empty_dict_for_empty_metadata(self, empty_metadata_str):
        expected_metadata = {}
        metadata = parse_metadata(empty_metadata_str)
        assert metadata == expected_metadata
