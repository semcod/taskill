"""Taskill core orchestrator.

Pipeline:
  1. Load config + state
  2. Collect snapshot (git + filesystem + optional pyqual report)
  3. Evaluate triggers — bail if thresholds not met
  4. Walk provider chain until one succeeds
  5. Apply updates to README/CHANGELOG/TODO
  6. Persist new state
"""
from __future__ import annotations

import json
import logging
import subprocess
from dataclasses import dataclass, field
from typing import Any

from taskill.config import TaskillConfig, load_config
from taskill.git_state import ProjectSnapshot, collect_snapshot
from taskill.providers import GeneratedDocs, ProviderError, build_chain
from taskill.state import load_state, save_state
from taskill.triggers import TriggerEvaluation, evaluate
from taskill.updaters import update_changelog, update_readme, update_todo

log = logging.getLogger("taskill")


@dataclass
class TaskillResult:
    ran: bool
    trigger_eval: TriggerEvaluation
    provider_used: str | None = None
    docs: GeneratedDocs | None = None
    files_changed: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "ran": self.ran,
            "should_have_run": self.trigger_eval.should_run,
            "reasons": self.trigger_eval.reasons,
            "skipped_because": self.trigger_eval.skipped,
            "provider": self.provider_used,
            "summary": self.docs.summary if self.docs else "",
            "changelog_added": len(self.docs.changelog_entries) if self.docs else 0,
            "todo_completed": len(self.docs.todo_completed) if self.docs else 0,
            "todo_new": len(self.docs.todo_new) if self.docs else 0,
            "files_changed": self.files_changed,
            "errors": self.errors,
        }


class Taskill:
    def __init__(self, config: TaskillConfig | None = None, config_path: str = "taskill.yaml"):
        self.config = config or load_config(config_path)
        self.state_path = self.config.project_root / self.config.state_file
        self.state = load_state(self.state_path)

    # ── public API ─────────────────────────────────────────────────────

    def run(self, force: bool = False) -> TaskillResult:
        snapshot = self._snapshot()
        trig = evaluate(self.config.triggers, self.state, snapshot, self.config.project_root)

        if not (trig.should_run or force):
            log.info("Skipping: %s", trig.summary())
            return TaskillResult(ran=False, trigger_eval=trig)

        # build chain — only currently-available providers
        chain = build_chain(self.config.providers)
        if not chain:
            return TaskillResult(
                ran=False, trigger_eval=trig,
                errors=["No providers configured"],
            )

        context = self._build_context(snapshot)
        docs: GeneratedDocs | None = None
        used: str | None = None
        errors: list[str] = []

        for provider in chain:
            if not provider.is_available():
                log.info("Provider %s unavailable, skipping", provider.name)
                continue
            try:
                log.info("Trying provider: %s", provider.name)
                docs = provider.generate(context)
                used = docs.provider_name or provider.name
                break
            except ProviderError as e:
                msg = f"{provider.name}: {e}"
                log.warning(msg)
                errors.append(msg)
                continue

        if docs is None:
            return TaskillResult(
                ran=False, trigger_eval=trig,
                errors=errors or ["All providers failed or unavailable"],
            )

        # apply updates
        files_changed: list[str] = []
        if not self.config.dry_run:
            files_changed = self._apply(docs, snapshot)
            self._update_state(snapshot)
            save_state(self.state_path, self.state)
        else:
            log.info("Dry-run: not writing files or state")

        return TaskillResult(
            ran=True,
            trigger_eval=trig,
            provider_used=used,
            docs=docs,
            files_changed=files_changed,
            errors=errors,  # non-fatal failures from providers we skipped past
        )

    def status(self) -> dict[str, Any]:
        """Inspect current trigger state without running anything."""
        snapshot = self._snapshot()
        trig = evaluate(self.config.triggers, self.state, snapshot, self.config.project_root)
        return {
            "would_run": trig.should_run,
            "reasons": trig.reasons,
            "skipped_because": trig.skipped,
            "head": snapshot.head_sha,
            "commits_pending": len(snapshot.commits_since_last_run),
            "coverage": snapshot.coverage_pct,
            "failed_tests": snapshot.failed_tests,
            "last_run": self.state.last_run_iso,
        }

    # ── internals ──────────────────────────────────────────────────────

    def _snapshot(self) -> ProjectSnapshot:
        return collect_snapshot(
            self.config.project_root,
            self.config.files,
            self.state.last_commit_sha,
        )

    def _build_context(self, snapshot: ProjectSnapshot) -> dict[str, Any]:
        root = self.config.project_root

        def _read(name: str) -> str:
            p = root / self.config.files.get(name, f"{name.upper()}.md")
            return p.read_text(encoding="utf-8") if p.exists() else ""

        ctx: dict[str, Any] = {
            "snapshot": snapshot,
            "existing_readme": _read("readme"),
            "existing_changelog": _read("changelog"),
            "existing_todo": _read("todo"),
            "sumd": snapshot.sumd_text,
            "sumr": snapshot.sumr_text,
            "project_name": root.name,
        }

        # optional: enrich with pyqual report (loose coupling — subprocess)
        if self.config.reuse.get("pyqual"):
            ctx["pyqual_report"] = self._maybe_pyqual_report()

        return ctx

    def _maybe_pyqual_report(self) -> dict[str, Any] | None:
        """Run `pyqual report --json` if pyqual is on PATH. Tolerate failure."""
        try:
            _PYQUAL_TIMEOUT = 30
            res = subprocess.run(
                ["pyqual", "report", "--json"],
                cwd=self.config.project_root,
                capture_output=True, text=True, timeout=_PYQUAL_TIMEOUT, check=False,
            )
            if res.returncode == 0 and res.stdout.strip():
                return json.loads(res.stdout)
        except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError):
            pass
        return None

    def _apply(self, docs: GeneratedDocs, snapshot: ProjectSnapshot) -> list[str]:
        root = self.config.project_root
        changed: list[str] = []

        cl = root / self.config.files["changelog"]
        if update_changelog(cl, docs.changelog_entries):
            changed.append(str(cl.relative_to(root)))

        td = root / self.config.files["todo"]
        if update_todo(td, docs.todo_completed, docs.todo_new):
            changed.append(str(td.relative_to(root)))

        rm = root / self.config.files["readme"]
        if update_readme(rm, snapshot, docs.summary):
            changed.append(str(rm.relative_to(root)))

        return changed

    def _update_state(self, snapshot: ProjectSnapshot) -> None:
        self.state.stamp()
        self.state.last_commit_sha = snapshot.head_sha
        self.state.last_coverage_pct = snapshot.coverage_pct
        self.state.last_failed_tests = snapshot.failed_tests
        self.state.last_sumd_hash = snapshot.sumd_hash
        self.state.last_todo_hash = snapshot.todo_hash
        self.state.last_readme_hash = snapshot.readme_hash
        for rel in self.config.triggers.watch_files:
            p = self.config.project_root / rel
            if p.exists():
                self.state.file_mtimes[rel] = p.stat().st_mtime
