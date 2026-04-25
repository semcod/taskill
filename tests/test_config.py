"""Config loader tests."""
from __future__ import annotations

from pathlib import Path

from taskill.config import load_config


def test_missing_yaml_returns_defaults(tmp_path: Path):
    cfg = load_config(tmp_path / "nope.yaml", project_root=tmp_path)
    assert cfg.triggers.min_hours_since_last_run == 24.0
    assert len(cfg.providers) == 3   # windsurf_mcp, openrouter, algorithmic
    names = [p.name for p in cfg.providers]
    assert names == ["windsurf_mcp", "openrouter", "algorithmic"]


def test_yaml_overrides_defaults(tmp_path: Path):
    yml = tmp_path / "taskill.yaml"
    yml.write_text("""
triggers:
  min_hours_since_last_run: 6
  require_all: true
providers:
  - name: openrouter
    enabled: true
  - name: algorithmic
    enabled: false
""", encoding="utf-8")
    cfg = load_config(yml, project_root=tmp_path)
    assert cfg.triggers.min_hours_since_last_run == 6
    assert cfg.triggers.require_all is True
    assert len(cfg.providers) == 2
    assert cfg.providers[0].name == "openrouter"
    assert cfg.providers[1].enabled is False


def test_dotenv_loaded_from_project_root(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("TASKILL_TEST_VAR", raising=False)
    (tmp_path / ".env").write_text("TASKILL_TEST_VAR=fromdotenv\n", encoding="utf-8")
    load_config(tmp_path / "taskill.yaml", project_root=tmp_path)
    import os
    assert os.environ.get("TASKILL_TEST_VAR") == "fromdotenv"


def test_process_env_overrides_dotenv(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("TASKILL_TEST_VAR2", "fromprocess")
    (tmp_path / ".env").write_text("TASKILL_TEST_VAR2=fromdotenv\n", encoding="utf-8")
    load_config(tmp_path / "taskill.yaml", project_root=tmp_path)
    import os
    assert os.environ["TASKILL_TEST_VAR2"] == "fromprocess"


def test_files_config_merges_with_defaults(tmp_path: Path):
    yml = tmp_path / "taskill.yaml"
    yml.write_text("files:\n  readme: docs/README.md\n", encoding="utf-8")
    cfg = load_config(yml, project_root=tmp_path)
    assert cfg.files["readme"] == "docs/README.md"
    # untouched files keep defaults
    assert cfg.files["changelog"] == "CHANGELOG.md"
    assert cfg.files["todo"] == "TODO.md"
