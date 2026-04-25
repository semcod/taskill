"""Bulk operations tests."""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from taskill.bulk import (
    BulkResult,
    bulk_run,
    find_repos,
    resolve_repo_config,
)
from taskill.config import load_config


def _make_repo(path: Path) -> Path:
    """Create a minimal git repo at the given path."""
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "init", "-q"], cwd=path, check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.email", "test@test"], cwd=path, check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "test"], cwd=path, check=True,
    )
    # initial commit so HEAD exists
    (path / "README.md").write_text("# test\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=path, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-q", "-m", "initial"], cwd=path, check=True,
        capture_output=True,
    )
    return path


# ─── find_repos ────────────────────────────────────────────────────────────

def test_find_repos_finds_direct_children(tmp_path: Path) -> None:
    """Repos at depth 1 should be found."""
    _make_repo(tmp_path / "repo1")
    _make_repo(tmp_path / "repo2")
    (tmp_path / "not_a_repo").mkdir()

    repos = find_repos(tmp_path, max_depth=2)
    assert len(repos) == 2
    names = {r.name for r in repos}
    assert names == {"repo1", "repo2"}


def test_find_repos_respects_max_depth(tmp_path: Path) -> None:
    """Repos beyond max_depth should not be found."""
    _make_repo(tmp_path / "deep" / "nested" / "repo")
    repos_d1 = find_repos(tmp_path, max_depth=1)
    repos_d3 = find_repos(tmp_path, max_depth=3)
    assert len(repos_d1) == 0
    assert len(repos_d3) == 1


def test_find_repos_skips_hidden_and_noise_dirs(tmp_path: Path) -> None:
    """Hidden dirs and noise dirs (node_modules, etc.) should be skipped."""
    _make_repo(tmp_path / ".hidden" / "repo")
    _make_repo(tmp_path / "node_modules" / "repo")
    _make_repo(tmp_path / "real" / "repo")

    repos = find_repos(tmp_path, max_depth=3)
    assert len(repos) == 1
    assert repos[0].name == "repo"
    assert "real" in str(repos[0])


def test_find_repos_does_not_descend_into_repos(tmp_path: Path) -> None:
    """Once a repo is found, nested repos inside it should not be scanned."""
    parent = _make_repo(tmp_path / "parent")
    _make_repo(parent / "nested")

    repos = find_repos(tmp_path, max_depth=3)
    assert len(repos) == 1
    assert repos[0].name == "parent"


def test_find_repos_returns_empty_for_nonexistent(tmp_path: Path) -> None:
    """Non-existent dirs should return empty list."""
    repos = find_repos(tmp_path / "nope", max_depth=2)
    assert repos == []


# ─── resolve_repo_config ──────────────────────────────────────────────────

def test_resolve_repo_config_uses_local_yaml(tmp_path: Path) -> None:
    """Local taskill.yaml should win over shared config."""
    repo = _make_repo(tmp_path / "repo")
    (repo / "taskill.yaml").write_text(
        "triggers:\n  min_hours_since_last_run: 6\n",
        encoding="utf-8",
    )
    cfg = resolve_repo_config(repo, shared_config=None)
    assert cfg.triggers.min_hours_since_last_run == 6
    assert cfg.project_root == repo.resolve()


def test_resolve_repo_config_uses_dot_taskill_yaml(tmp_path: Path) -> None:
    """`.taskill.yaml` should also be picked up."""
    repo = _make_repo(tmp_path / "repo")
    (repo / ".taskill.yaml").write_text(
        "triggers:\n  min_hours_since_last_run: 12\n",
        encoding="utf-8",
    )
    cfg = resolve_repo_config(repo, shared_config=None)
    assert cfg.triggers.min_hours_since_last_run == 12


def test_resolve_repo_config_falls_back_to_shared(tmp_path: Path) -> None:
    """When no local config, shared config should be rebased onto repo."""
    repo = _make_repo(tmp_path / "repo")
    shared_yml = tmp_path / "shared.yaml"
    shared_yml.write_text(
        "triggers:\n  min_hours_since_last_run: 48\n",
        encoding="utf-8",
    )
    shared = load_config(shared_yml, project_root=tmp_path)

    cfg = resolve_repo_config(repo, shared_config=shared)
    assert cfg.triggers.min_hours_since_last_run == 48
    # project_root must be rebased to the repo
    assert cfg.project_root == repo.resolve()


def test_resolve_repo_config_falls_back_to_defaults(tmp_path: Path) -> None:
    """No local, no shared → defaults."""
    repo = _make_repo(tmp_path / "repo")
    cfg = resolve_repo_config(repo, shared_config=None)
    assert cfg.triggers.min_hours_since_last_run == 24.0
    assert cfg.project_root == repo.resolve()


def test_resolve_repo_config_local_wins_over_shared(tmp_path: Path) -> None:
    """Local config should override shared even when both exist."""
    repo = _make_repo(tmp_path / "repo")
    (repo / "taskill.yaml").write_text(
        "triggers:\n  min_hours_since_last_run: 1\n",
        encoding="utf-8",
    )
    shared_yml = tmp_path / "shared.yaml"
    shared_yml.write_text(
        "triggers:\n  min_hours_since_last_run: 99\n",
        encoding="utf-8",
    )
    shared = load_config(shared_yml, project_root=tmp_path)
    cfg = resolve_repo_config(repo, shared_config=shared)
    assert cfg.triggers.min_hours_since_last_run == 1


# ─── bulk_run ─────────────────────────────────────────────────────────────

def test_bulk_run_no_repos(tmp_path: Path) -> None:
    """Empty directory should yield empty result."""
    result = bulk_run(tmp_path, max_depth=1, force=True, dry_run=True)
    assert isinstance(result, BulkResult)
    assert result.total_repos == 0
    assert result.ran_count == 0


def test_bulk_run_executes_each_repo(tmp_path: Path) -> None:
    """Each found repo should be run."""
    _make_repo(tmp_path / "a")
    _make_repo(tmp_path / "b")

    result = bulk_run(tmp_path, max_depth=1, force=True, dry_run=True)
    assert result.total_repos == 2
    assert len(result.per_repo) == 2
    # both should have ran (force=True bypasses triggers, dry_run=True avoids writes)
    assert result.ran_count == 2


def test_bulk_run_repo_filter(tmp_path: Path) -> None:
    """repo_filter should restrict which repos are run."""
    _make_repo(tmp_path / "alpha")
    _make_repo(tmp_path / "beta")
    _make_repo(tmp_path / "gamma")

    result = bulk_run(
        tmp_path, max_depth=1, force=True, dry_run=True,
        repo_filter=["alpha", "gamma"],
    )
    # 2 ran, 1 skipped (beta)
    assert result.ran_count == 2
    assert len(result.skipped) == 1
    assert result.skipped[0][0].name == "beta"


def test_bulk_run_with_shared_config(tmp_path: Path) -> None:
    """Shared config should be used as base for repos without their own."""
    repo_a = _make_repo(tmp_path / "a")
    repo_b = _make_repo(tmp_path / "b")
    # b has its own override
    (repo_b / "taskill.yaml").write_text(
        "triggers:\n  min_hours_since_last_run: 1\n",
        encoding="utf-8",
    )
    shared_yml = tmp_path / "shared.yaml"
    shared_yml.write_text(
        "triggers:\n  min_hours_since_last_run: 100\n",
        encoding="utf-8",
    )

    result = bulk_run(
        tmp_path, shared_config=shared_yml,
        max_depth=1, force=True, dry_run=True,
    )
    assert result.ran_count == 2


def test_bulk_run_max_projects_limits_count(tmp_path: Path) -> None:
    """max_projects should cap the number of processed repos."""
    _make_repo(tmp_path / "a")
    _make_repo(tmp_path / "b")
    _make_repo(tmp_path / "c")

    result = bulk_run(
        tmp_path, max_depth=1, max_projects=2,
        force=True, dry_run=True,
    )
    # Only 2 of 3 repos should be processed
    assert len(result.per_repo) == 2
    assert result.ran_count == 2


def test_bulk_run_max_projects_zero_means_unlimited(tmp_path: Path) -> None:
    """max_projects=0 should process all repos."""
    _make_repo(tmp_path / "a")
    _make_repo(tmp_path / "b")
    _make_repo(tmp_path / "c")

    result = bulk_run(
        tmp_path, max_depth=1, max_projects=0,
        force=True, dry_run=True,
    )
    assert len(result.per_repo) == 3


def test_bulk_run_filters_before_max_projects(tmp_path: Path) -> None:
    """repo_filter should be applied before max_projects limit."""
    _make_repo(tmp_path / "alpha")
    _make_repo(tmp_path / "beta")
    _make_repo(tmp_path / "gamma")

    result = bulk_run(
        tmp_path, max_depth=1, max_projects=1,
        force=True, dry_run=True,
        repo_filter=["gamma"],
    )
    assert len(result.per_repo) == 1
    assert next(iter(result.per_repo)).name == "gamma"
    assert result.ran_count == 1


def test_bulk_run_summary_format(tmp_path: Path) -> None:
    """Summary string should contain key counts."""
    _make_repo(tmp_path / "a")
    result = bulk_run(tmp_path, max_depth=1, force=True, dry_run=True)
    summary = result.summary()
    assert "ran" in summary
    assert "changed" in summary


def test_bulk_result_as_dict(tmp_path: Path) -> None:
    """as_dict should produce a JSON-serializable structure."""
    _make_repo(tmp_path / "a")
    result = bulk_run(tmp_path, max_depth=1, force=True, dry_run=True)
    d = result.as_dict()
    assert "root" in d
    assert "total_repos" in d
    assert "per_repo" in d
    assert d["total_repos"] == 1
