"""Tests for vault path normalization."""

from pathlib import Path

from zk_chat.vault_path import normalize_vault_path


class DescribeNormalizeVaultPath:
    """Tests for the normalize_vault_path helper function."""

    def should_resolve_symlink_to_its_target(self, tmp_path):
        real = tmp_path / "real"
        real.mkdir()
        link = tmp_path / "link"
        link.symlink_to(real)

        assert normalize_vault_path(link) == normalize_vault_path(real)
        assert normalize_vault_path(real) == str((tmp_path / "real").resolve())

    def should_return_absolute_path_for_relative_input(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        sub = tmp_path / "sub"
        sub.mkdir()

        result = normalize_vault_path("sub")

        assert result == str(Path("sub").resolve())

    def should_expand_user_home(self, tmp_path, monkeypatch):
        monkeypatch.setenv("HOME", str(tmp_path))

        result = normalize_vault_path("~/vault")

        assert result == str((tmp_path / "vault").resolve())

    def should_treat_distinct_directories_as_different(self, tmp_path):
        dir_a = tmp_path / "a"
        dir_b = tmp_path / "b"
        dir_a.mkdir()
        dir_b.mkdir()

        assert normalize_vault_path(dir_a) != normalize_vault_path(dir_b)
