import pytest

from zk_chat.config import Config, ModelGateway
from zk_chat.upgraders.gateway_specific_index_folder import GatewaySpecificIndexFolder, Upgrader


@pytest.fixture
def config(tmp_path):
    return Config(vault=str(tmp_path), model="llama3", gateway=ModelGateway.OLLAMA)


@pytest.fixture
def upgrader(config):
    return GatewaySpecificIndexFolder(config)


class DescribeUpgrader:
    def should_not_run_by_default(self):
        upgrader = Upgrader()

        assert upgrader.should_run() is False

    def should_run_without_error(self):
        upgrader = Upgrader()

        upgrader.run()


class DescribeGatewaySpecificIndexFolder:
    def should_store_config_on_init(self, upgrader, config):
        assert upgrader.config is config

    class DescribeDbDir:
        def should_return_zk_chat_db_inside_vault(self, upgrader, config, tmp_path):
            expected = tmp_path / ".zk_chat_db"

            assert upgrader.db_dir == expected

    class DescribeIndexDir:
        def should_return_gateway_value_subdirectory_of_db_dir(self, upgrader, config, tmp_path):
            expected = tmp_path / ".zk_chat_db" / "ollama"

            assert upgrader.index_dir == expected

    class DescribeShouldRun:
        def should_return_true_when_db_dir_exists_and_index_dir_absent(self, upgrader, tmp_path):
            (tmp_path / ".zk_chat_db").mkdir()

            assert upgrader.should_run() is True

        def should_return_false_when_db_dir_does_not_exist(self, upgrader, tmp_path):
            assert upgrader.should_run() is False

        def should_return_false_when_both_db_dir_and_index_dir_exist(self, upgrader, tmp_path):
            (tmp_path / ".zk_chat_db" / "ollama").mkdir(parents=True)

            assert upgrader.should_run() is False

    class DescribeRun:
        def should_create_index_dir(self, upgrader, tmp_path):
            db_dir = tmp_path / ".zk_chat_db"
            db_dir.mkdir()

            upgrader.run()

            assert (tmp_path / ".zk_chat_db" / "ollama").exists()

        def should_move_non_gateway_files_into_index_dir(self, upgrader, tmp_path):
            db_dir = tmp_path / ".zk_chat_db"
            db_dir.mkdir()
            sqlite_file = db_dir / "chroma.sqlite3"
            sqlite_file.write_text("fake sqlite data")
            chroma_dir = db_dir / "some_chroma_data"
            chroma_dir.mkdir()

            upgrader.run()

            index_dir = tmp_path / ".zk_chat_db" / "ollama"
            assert (index_dir / "chroma.sqlite3").exists()
            assert (index_dir / "some_chroma_data").exists()

        def should_not_move_gateway_named_directories(self, upgrader, tmp_path):
            db_dir = tmp_path / ".zk_chat_db"
            db_dir.mkdir()
            sqlite_file = db_dir / "chroma.sqlite3"
            sqlite_file.write_text("data")
            ollama_dir = db_dir / "ollama"
            ollama_dir.mkdir()
            openai_dir = db_dir / "openai"
            openai_dir.mkdir()

            upgrader.run()

            assert (db_dir / "ollama").exists()
            assert (db_dir / "openai").exists()

        def should_create_index_dir_when_sqlite_file_present_and_index_dir_absent(self, upgrader, tmp_path):
            db_dir = tmp_path / ".zk_chat_db"
            db_dir.mkdir()
            (db_dir / "chroma.sqlite3").write_text("data")

            upgrader.run()

            assert (tmp_path / ".zk_chat_db" / "ollama").is_dir()
