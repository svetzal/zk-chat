"""Tests for VaultStatusService."""

from unittest.mock import Mock

import pytest

from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway
from zk_chat.services.vault_status_service import DbInfo, VaultStatusService


@pytest.fixture
def mock_filesystem():
    return Mock(spec=MarkdownFilesystemGateway)


@pytest.fixture
def service(mock_filesystem):
    return VaultStatusService(mock_filesystem)


class DescribeVaultStatusService:
    """Tests for the VaultStatusService component."""

    def should_be_instantiated_with_filesystem_gateway(self, mock_filesystem):
        svc = VaultStatusService(mock_filesystem)

        assert isinstance(svc, VaultStatusService)

    class DescribeCountMarkdownFiles:
        def should_return_count_of_markdown_files(self, service, mock_filesystem):
            mock_filesystem.iterate_markdown_files.return_value = iter(["a.md", "b.md", "c.md"])

            result = service.count_markdown_files()

            assert result == 3

        def should_return_zero_when_no_markdown_files(self, service, mock_filesystem):
            mock_filesystem.iterate_markdown_files.return_value = iter([])

            result = service.count_markdown_files()

            assert result == 0

    class DescribeGetDbInfo:
        def should_return_none_when_db_directory_missing(self, service, tmp_path):
            result = service.get_db_info(str(tmp_path))

            assert result is None

        def should_return_db_info_when_directory_exists(self, service, tmp_path):
            db_dir = tmp_path / ".zk_chat_db"
            db_dir.mkdir()
            test_file = db_dir / "data.bin"
            test_file.write_bytes(b"x" * 100)

            result = service.get_db_info(str(tmp_path))

            assert isinstance(result, DbInfo)
            assert result.location == str(db_dir)
            assert result.total_size == 100
            assert result.file_count == 1

        def should_aggregate_size_across_multiple_files(self, service, tmp_path):
            db_dir = tmp_path / ".zk_chat_db"
            db_dir.mkdir()
            (db_dir / "file1.bin").write_bytes(b"x" * 50)
            (db_dir / "file2.bin").write_bytes(b"y" * 75)

            result = service.get_db_info(str(tmp_path))

            assert result.total_size == 125
            assert result.file_count == 2

        def should_aggregate_size_across_subdirectories(self, service, tmp_path):
            db_dir = tmp_path / ".zk_chat_db"
            sub_dir = db_dir / "subdir"
            sub_dir.mkdir(parents=True)
            (db_dir / "root_file.bin").write_bytes(b"a" * 30)
            (sub_dir / "sub_file.bin").write_bytes(b"b" * 20)

            result = service.get_db_info(str(tmp_path))

            assert result.total_size == 50
            assert result.file_count == 2
