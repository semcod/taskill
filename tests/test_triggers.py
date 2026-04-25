"""Trigger evaluation tests."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from taskill.config import Triggers
from taskill.git_state import Commit, ProjectSnapshot
from taskill.state import TaskillState
from taskill.triggers import evaluate


def _snap(**kw) -> ProjectSnapshot:  # type: ignore[no-untyped-def]
    return ProjectSnapshot(
        head_sha=kw.get("head_sha", "abc"),
        commits_since_last_run=kw.get("commits", []),
        changed_files=kw.get("changed_files", []),
        coverage_pct=kw.get("coverage"),
        failed_tests=kw.get("failed_tests"),
        sumd_hash=kw.get("sumd_hash"),
    )


def _commit(subject: str = "feat: x") -> Commit:
    return Commit(sha="0", short_sha="0", author="x", date="2026-01-01T00:00:00Z",
                  subject=subject)


def test_first_run_always_triggers(tmp_path: Path) -> None:
    triggers = Triggers()
    state = TaskillState()    # never run
    snap = _snap()
    result = evaluate(triggers, state, snap, tmp_path)
    assert result.should_run
    assert "never run before" in result.reasons


def test_recent_run_skips_when_no_commits(tmp_path: Path) -> None:
    triggers = Triggers(min_hours_since_last_run=24, min_commits_since_last_run=1,
                        changed_files_threshold=1)
    state = TaskillState(last_run_iso=datetime.now(timezone.utc).isoformat())
    snap = _snap()
    result = evaluate(triggers, state, snap, tmp_path)
    assert not result.should_run


def test_commits_above_threshold_triggers(tmp_path: Path) -> None:
    triggers = Triggers(min_hours_since_last_run=24, min_commits_since_last_run=2,
                        changed_files_threshold=1)
    state = TaskillState(last_run_iso=datetime.now(timezone.utc).isoformat())
    snap = _snap(commits=[_commit(), _commit(), _commit()])
    result = evaluate(triggers, state, snap, tmp_path)
    assert result.should_run
    assert any("3 new commit" in r for r in result.reasons)


def test_coverage_delta_triggers(tmp_path: Path) -> None:
    triggers = Triggers(min_hours_since_last_run=999, min_commits_since_last_run=999,
                        changed_files_threshold=999, coverage_change_pct=2.0)
    state = TaskillState(
        last_run_iso=datetime.now(timezone.utc).isoformat(),
        last_coverage_pct=80.0,
    )
    snap = _snap(coverage=85.0)
    result = evaluate(triggers, state, snap, tmp_path)
    assert result.should_run


def test_coverage_within_threshold_does_not_trigger(tmp_path: Path) -> None:
    triggers = Triggers(min_hours_since_last_run=999, min_commits_since_last_run=999,
                        changed_files_threshold=999, coverage_change_pct=5.0)
    state = TaskillState(
        last_run_iso=datetime.now(timezone.utc).isoformat(),
        last_coverage_pct=80.0,
    )
    snap = _snap(coverage=82.0)
    result = evaluate(triggers, state, snap, tmp_path)
    assert not result.should_run


def test_sumd_change_triggers(tmp_path: Path) -> None:
    triggers = Triggers(min_hours_since_last_run=999, min_commits_since_last_run=999,
                        changed_files_threshold=999)
    state = TaskillState(
        last_run_iso=datetime.now(timezone.utc).isoformat(),
        last_sumd_hash="oldhash",
    )
    snap = _snap(sumd_hash="newhash")
    result = evaluate(triggers, state, snap, tmp_path)
    assert result.should_run
    assert any("SUMD" in r for r in result.reasons)


def test_require_all_with_partial_match_does_not_trigger(tmp_path: Path) -> None:
    triggers = Triggers(
        min_hours_since_last_run=24, min_commits_since_last_run=10,
        changed_files_threshold=1, require_all=True,
    )
    # 26h passed (✓) but 0 commits (✗)
    state = TaskillState(
        last_run_iso=(datetime.now(timezone.utc) - timedelta(hours=26)).isoformat()
    )
    snap = _snap(commits=[])
    result = evaluate(triggers, state, snap, tmp_path)
    assert not result.should_run


def test_watched_file_mtime_triggers(tmp_path: Path) -> None:
    sumd = tmp_path / "SUMD.md"
    sumd.write_text("hi", encoding="utf-8")
    triggers = Triggers(min_hours_since_last_run=999, min_commits_since_last_run=999,
                        changed_files_threshold=999, watch_files=["SUMD.md"])
    state = TaskillState(
        last_run_iso=datetime.now(timezone.utc).isoformat(),
        file_mtimes={},  # no record yet → counts as touched
    )
    result = evaluate(triggers, state, _snap(), tmp_path)
    assert result.should_run
