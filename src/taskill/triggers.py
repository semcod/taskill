"""Decide whether thresholds in taskill.yaml are met → should we run?"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from taskill.config import Triggers
from taskill.git_state import ProjectSnapshot
from taskill.state import TaskillState


@dataclass
class TriggerEvaluation:
    should_run: bool
    reasons: list[str]
    skipped: list[str]

    def summary(self) -> str:
        if self.should_run:
            return "RUN: " + "; ".join(self.reasons)
        return "SKIP: thresholds not met"


def evaluate(
    triggers: Triggers,
    state: TaskillState,
    snapshot: ProjectSnapshot,
    project_root: Path,
) -> TriggerEvaluation:
    reasons: list[str] = []
    skipped: list[str] = []

    # 1. time since last run
    if state.last_run_dt is None:
        reasons.append("never run before")
    else:
        delta_h = (datetime.now(timezone.utc) - state.last_run_dt).total_seconds() / 3600
        if delta_h >= triggers.min_hours_since_last_run:
            reasons.append(f"{delta_h:.1f}h since last run (≥{triggers.min_hours_since_last_run}h)")
        else:
            skipped.append(f"only {delta_h:.1f}h since last run")

    # 2. commits since last
    n_commits = len(snapshot.commits_since_last_run)
    if n_commits >= triggers.min_commits_since_last_run:
        reasons.append(f"{n_commits} new commit(s)")
    else:
        skipped.append(f"only {n_commits} commits (<{triggers.min_commits_since_last_run})")

    # 3. changed files
    n_changed = len(snapshot.changed_files)
    if n_changed >= triggers.changed_files_threshold:
        reasons.append(f"{n_changed} changed file(s)")
    else:
        skipped.append(f"only {n_changed} files changed")

    # 4. coverage delta
    if triggers.coverage_change_pct is not None and snapshot.coverage_pct is not None and \
       state.last_coverage_pct is not None:
        delta = abs(snapshot.coverage_pct - state.last_coverage_pct)
        if delta >= triggers.coverage_change_pct:
            reasons.append(f"coverage moved {delta:.1f}pp")
        else:
            skipped.append(f"coverage Δ {delta:.1f}pp")

    # 5. failed tests changed
    if triggers.failed_tests_changed and snapshot.failed_tests is not None and \
       state.last_failed_tests is not None and snapshot.failed_tests != state.last_failed_tests:
        reasons.append(
            f"failed tests {state.last_failed_tests} → {snapshot.failed_tests}"
        )

    # 6. SUMD changed
    if snapshot.sumd_hash and snapshot.sumd_hash != state.last_sumd_hash:
        reasons.append("SUMD.md changed")

    # 7. watched files mtime
    for rel in triggers.watch_files:
        p = project_root / rel
        if not p.exists():
            continue
        mtime = p.stat().st_mtime
        prev = state.file_mtimes.get(rel)
        if prev is None or mtime > prev:
            reasons.append(f"{rel} touched")

    if triggers.require_all:
        # AND semantics: must have NO skipped reasons
        should_run = bool(reasons) and not skipped
    else:
        should_run = bool(reasons)

    return TriggerEvaluation(should_run=should_run, reasons=reasons, skipped=skipped)
