"""Bulk operations for running taskill across multiple repositories.

Supports the "monorepo / fleet hygiene" use case: scan a parent directory for
git repos, run taskill in each one, optionally with a shared base config that
each repo can override locally.

Usage:
    from taskill.bulk import bulk_run, find_repos

    result = bulk_run(
        root=Path("/home/me/github"),
        shared_config=Path("/home/me/github/taskill.yaml"),  # optional
        max_depth=2,
        force=False,
        dry_run=False,
    )
    for repo, repo_result in result.per_repo.items():
        print(repo, repo_result.ran)
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from taskill.config import TaskillConfig, load_config
from taskill.core import Taskill, TaskillResult

log = logging.getLogger("taskill.bulk")

# Per-repo config filenames, in priority order. First match wins.
LOCAL_CONFIG_NAMES = ("taskill.yaml", ".taskill.yaml")


@dataclass
class BulkResult:
    """Aggregate result of running taskill across multiple repos."""
    root: Path
    per_repo: dict[Path, TaskillResult] = field(default_factory=dict)
    skipped: list[tuple[Path, str]] = field(default_factory=list)  # (path, reason)
    errors: list[tuple[Path, str]] = field(default_factory=list)   # (path, error)

    @property
    def total_repos(self) -> int:
        return len(self.per_repo) + len(self.skipped) + len(self.errors)

    @property
    def ran_count(self) -> int:
        return sum(1 for r in self.per_repo.values() if r.ran)

    @property
    def changed_count(self) -> int:
        return sum(1 for r in self.per_repo.values() if r.files_changed)

    def as_dict(self) -> dict[str, Any]:
        return {
            "root": str(self.root),
            "total_repos": self.total_repos,
            "ran": self.ran_count,
            "changed": self.changed_count,
            "skipped": [{"path": str(p), "reason": r} for p, r in self.skipped],
            "errors": [{"path": str(p), "error": e} for p, e in self.errors],
            "per_repo": {
                str(p): r.as_dict() for p, r in self.per_repo.items()
            },
        }

    def summary(self) -> str:
        return (
            f"{self.ran_count}/{self.total_repos} ran, "
            f"{self.changed_count} changed, "
            f"{len(self.skipped)} skipped, "
            f"{len(self.errors)} errors"
        )


def find_repos(root: Path, max_depth: int = 2) -> list[Path]:
    """Find git repositories under root, up to max_depth levels deep.

    A directory is considered a repo if it contains a `.git` entry (file or dir).
    Stops descending into a repo once found (no nested repo scan).

    Args:
        root: Directory to scan
        max_depth: Maximum directory levels to descend (1 = direct children only)

    Returns:
        Sorted list of repo paths
    """
    root = Path(root).resolve()
    if not root.is_dir():
        return []

    repos: list[Path] = []
    _scan(root, repos, depth=0, max_depth=max_depth)
    return sorted(repos)


def _scan(directory: Path, repos: list[Path], depth: int, max_depth: int) -> None:
    """Recursively scan for git repos."""
    if depth > max_depth:
        return

    # Is this directory itself a repo?
    try:
        is_repo = (directory / ".git").exists()
    except (PermissionError, OSError):
        return
    if is_repo:
        repos.append(directory)
        return  # don't descend into nested repos

    if depth == max_depth:
        return

    try:
        children = sorted(directory.iterdir())
    except (PermissionError, OSError):
        return

    for child in children:
        try:
            if not child.is_dir():
                continue
        except (PermissionError, OSError):
            continue
        # skip hidden / common noise dirs
        if child.name.startswith(".") or child.name in {
            "node_modules", "__pycache__", "venv", ".venv", "dist", "build",
            "target", ".tox", ".pytest_cache",
        }:
            continue
        _scan(child, repos, depth + 1, max_depth)


def resolve_repo_config(
    repo: Path,
    shared_config: TaskillConfig | None = None,
) -> TaskillConfig:
    """Resolve config for a single repo.

    Resolution order:
      1. Local taskill.yaml or .taskill.yaml in the repo (highest priority)
      2. Shared config inherited from parent directory (project_root rebased)
      3. Defaults

    Args:
        repo: Path to the repo
        shared_config: Optional shared config from parent directory

    Returns:
        TaskillConfig pointing at this repo's project_root
    """
    # 1. Local config file in the repo
    for name in LOCAL_CONFIG_NAMES:
        local_path = repo / name
        if local_path.exists():
            return load_config(local_path, project_root=repo)

    # 2. Shared config rebased onto this repo
    if shared_config is not None:
        return _rebase_config(shared_config, repo)

    # 3. Defaults via load_config with non-existent path
    return load_config(repo / "taskill.yaml", project_root=repo)


def _rebase_config(base: TaskillConfig, new_root: Path) -> TaskillConfig:
    """Return a copy of `base` with project_root rebased to `new_root`."""
    from copy import deepcopy
    cfg = deepcopy(base)
    cfg.project_root = Path(new_root).resolve()
    return cfg


def _load_shared_config(shared_config: Path | TaskillConfig | None) -> TaskillConfig | None:
    """Pre-load shared config if a path was given."""
    if isinstance(shared_config, TaskillConfig):
        return shared_config
    if shared_config is None:
        return None
    shared_path = Path(shared_config)
    if shared_path.exists():
        return load_config(shared_path, project_root=shared_path.parent)
    log.warning("Shared config %s not found, using defaults", shared_path)
    return None


def _apply_filters(
    repos: list[Path],
    repo_filter: list[str] | None,
    max_projects: int,
    required_files: list[str] | None = None,
) -> tuple[list[Path], list[tuple[Path, str]]]:
    """Apply name filter, required-file filter and max_projects cap. Returns (kept, skipped)."""
    skipped: list[tuple[Path, str]] = []
    if required_files:
        missing = [repo for repo in repos if not all((repo / f).exists() for f in required_files)]
        repos = [repo for repo in repos if all((repo / f).exists() for f in required_files)]
        log.info("Filtered out %d repos (missing required files)", len(missing))
        skipped.extend((repo, f"missing required files: {required_files}") for repo in missing)
    if repo_filter:
        filtered_out = [repo for repo in repos if not any(f in repo.name for f in repo_filter)]
        repos = [repo for repo in repos if any(f in repo.name for f in repo_filter)]
        log.info("Filtered out %d repos", len(filtered_out))
        skipped.extend((repo, "filtered out") for repo in filtered_out)
    if max_projects > 0 and len(repos) > max_projects:
        limit_skipped = repos[max_projects:]
        repos = repos[:max_projects]
        log.info("Limiting to first %d matching repos", max_projects)
        skipped.extend((repo, "max_projects limit") for repo in limit_skipped)
    return repos, skipped


def _run_single_repo(
    repo: Path, shared_cfg: TaskillConfig | None, force: bool, dry_run: bool,
) -> TaskillResult:
    """Run taskill on a single repo."""
    cfg = resolve_repo_config(repo, shared_cfg)
    if dry_run:
        cfg.dry_run = True
    tk = Taskill(config=cfg)
    return tk.run(force=force)


def bulk_run(
    root: Path,
    shared_config: Path | TaskillConfig | None = None,
    *,
    max_depth: int = 2,
    max_projects: int = 0,
    force: bool = False,
    dry_run: bool = False,
    repo_filter: list[str] | None = None,
    required_files: list[str] | None = None,
) -> BulkResult:
    """Run taskill across all repos found under `root`.

    Args:
        root: Parent directory containing one or more repos
        shared_config: Optional path to shared taskill.yaml or pre-loaded config.
                       Used as base for repos that don't have their own config.
        max_depth: How deep to recurse looking for repos
        max_projects: Maximum number of projects to process (0 = unlimited)
        force: Forward to Taskill.run (ignore triggers)
        dry_run: Forward to Taskill (don't write files or persist state)
        repo_filter: Optional list of repo names to include (substring match).
                     If provided, only repos whose name matches one of these are run.
        required_files: Optional list of file names that must exist in a repo to be included.

    Returns:
        BulkResult with per-repo TaskillResult and aggregated counts.
    """
    root = Path(root).resolve()
    shared_cfg = _load_shared_config(shared_config)

    repos = find_repos(root, max_depth=max_depth)
    log.info("Found %d repos under %s", len(repos), root)

    repos, skipped = _apply_filters(repos, repo_filter, max_projects, required_files)

    result = BulkResult(root=root)
    result.skipped.extend(skipped)

    for repo in repos:
        try:
            repo_result = _run_single_repo(repo, shared_cfg, force, dry_run)
            result.per_repo[repo] = repo_result
            log.info(
                "%s: ran=%s, changed=%s",
                repo.name, repo_result.ran, repo_result.files_changed,
            )
        except Exception as e:
            log.exception("Error running taskill in %s", repo)
            result.errors.append((repo, str(e)))
        except KeyboardInterrupt:
            log.warning("Interrupted at %s — returning partial results", repo.name)
            break

    return result
