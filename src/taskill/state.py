"""Persistent state — what was the project's snapshot last time we ran?"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class TaskillState:
    last_run_iso: str | None = None
    last_commit_sha: str | None = None
    last_coverage_pct: float | None = None
    last_failed_tests: int | None = None
    last_sumd_hash: str | None = None
    file_mtimes: dict[str, float] = field(default_factory=dict)

    @property
    def last_run_dt(self) -> datetime | None:
        if not self.last_run_iso:
            return None
        return datetime.fromisoformat(self.last_run_iso)

    def stamp(self) -> None:
        self.last_run_iso = datetime.now(timezone.utc).isoformat()


def load_state(path: Path) -> TaskillState:
    if not path.exists():
        return TaskillState()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return TaskillState(**data)
    except (json.JSONDecodeError, TypeError):
        # corrupt state → start fresh, don't crash
        return TaskillState()


def save_state(path: Path, state: TaskillState) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(state), indent=2), encoding="utf-8")
