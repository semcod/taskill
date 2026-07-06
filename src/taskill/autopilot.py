"""Autonomous task execution — hand tasks from a list to koru/coru.

Running ``taskill`` with no subcommand resolves pending tasks from a list (a
``TODO.md`` checklist, ``planfile.yaml`` tickets, or a plain ``TASK.md`` file)
and runs each one through the koru/coru autonomous pipeline — by default
``coru text "<task>" --llm``, which routes the natural-language task through
coru's litellm planner (OpenRouter) and executes the mapped actions.

The point: execute the tasks you'd otherwise have to write out or hunt down by
hand — they're already on the list, so taskill just does them.
"""

from __future__ import annotations

import logging
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

import yaml

from taskill.config import TaskillConfig

log = logging.getLogger("taskill.autopilot")

# Matches an unchecked GitHub-style checklist item: "- [ ] do the thing".
_UNCHECKED_RE = re.compile(r"^\s*[-*]\s*\[\s\]\s+(?P<text>.+?)\s*$")


@dataclass
class TaskRun:
    task: str
    returncode: int
    skipped: bool = False
    reason: str = ""  # why it failed (e.g. "verify: pytest -q", "command error")
    rolled_back: bool = False

    @property
    def ok(self) -> bool:
        return self.returncode == 0 and not self.skipped


# ───────────────────────────── task resolution ─────────────────────────────


def _tasks_from_todo(todo_path: Path) -> list[str]:
    """Return the text of every unchecked ``- [ ]`` item in a TODO file."""
    if not todo_path.exists():
        return []
    tasks: list[str] = []
    for line in todo_path.read_text(encoding="utf-8").splitlines():
        m = _UNCHECKED_RE.match(line)
        if m:
            tasks.append(m.group("text").strip())
    return tasks


def _tasks_from_planfile(planfile_path: Path) -> list[str]:
    """Return the title of every open ticket in a planfile.yaml."""
    if not planfile_path.exists():
        return []
    try:
        data = yaml.safe_load(planfile_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return []
    tickets = data.get("tickets") if isinstance(data, dict) else None
    if not isinstance(tickets, list):
        return []
    tasks: list[str] = []
    for ticket in tickets:
        if not isinstance(ticket, dict):
            continue
        if str(ticket.get("status", "")).lower() in {"done", "closed", "completed"}:
            continue
        title = ticket.get("title") or ticket.get("description")
        if title:
            tasks.append(str(title).strip())
    return tasks


def _tasks_from_file(task_file: Path) -> list[str]:
    """Return one task per non-empty, non-comment line of a plain task file."""
    if not task_file.exists():
        return []
    tasks: list[str] = []
    for line in task_file.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            tasks.append(stripped)
    return tasks


def resolve_tasks(config: TaskillConfig) -> tuple[list[str], str]:
    """Resolve pending tasks and the source they came from.

    ``source: auto`` tries TODO checkboxes, then planfile tickets, then the task
    file, returning the first non-empty list.
    """
    root = config.project_root
    todo_path = root / config.files.get("todo", "TODO.md")
    planfile_path = root / "planfile.yaml"
    task_file = root / config.koru.task_file

    resolvers = {
        "todo": lambda: _tasks_from_todo(todo_path),
        "planfile": lambda: _tasks_from_planfile(planfile_path),
        "file": lambda: _tasks_from_file(task_file),
    }

    order = ["todo", "planfile", "file"] if config.koru.source == "auto" else [config.koru.source]
    for src in order:
        resolver = resolvers.get(src)
        if resolver is None:
            continue
        tasks = resolver()
        if tasks:
            return tasks, src
    return [], config.koru.source


# ───────────────────────────── execution ─────────────────────────────


def build_command(command_template: list[str], task: str) -> list[str]:
    """Substitute ``{task}`` in the command template (or append the task)."""
    if any("{task}" in tok for tok in command_template):
        return [tok.replace("{task}", task) for tok in command_template]
    return [*command_template, task]


def run_task(task: str, config: TaskillConfig, *, dry_run: bool) -> TaskRun:
    """Run a single task through the configured koru/coru command."""
    cmd = build_command(config.koru.command, task)
    if dry_run:
        log.info("[dry-run] would run: %s", " ".join(cmd))
        return TaskRun(task=task, returncode=0, skipped=True)
    try:
        result = subprocess.run(cmd, cwd=config.project_root)
        return TaskRun(task=task, returncode=result.returncode)
    except FileNotFoundError:
        log.error("Command not found: %s (is coru installed and on PATH?)", cmd[0])
        return TaskRun(task=task, returncode=127)


# ───────────────────────────── verification & rollback ─────────────────────────────


def _norm_verify_command(entry, task: str) -> list[str]:
    """Normalize a verify entry (str → shell, list → argv) with {task} substituted."""
    if isinstance(entry, str):
        return ["sh", "-c", entry.replace("{task}", task)]
    return [str(tok).replace("{task}", task) for tok in entry]


def run_verify(config: TaskillConfig, task: str) -> tuple[bool, str]:
    """Run each configured verify command. Return (all_passed, failed_command).

    An empty ``verify`` list means "no gate" and always passes.
    """
    for entry in config.koru.verify:
        cmd = _norm_verify_command(entry, task)
        label = entry if isinstance(entry, str) else " ".join(cmd)
        try:
            result = subprocess.run(cmd, cwd=config.project_root)
        except FileNotFoundError:
            log.error("Verify command not found: %s", cmd[0])
            return False, label
        if result.returncode != 0:
            return False, label
    return True, ""


def _git_untracked(root: Path) -> set[str]:
    """Return the set of untracked (not-ignored) file paths in the repo."""
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--others", "--exclude-standard"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return set()
    return {line for line in result.stdout.splitlines() if line.strip()}


def rollback_worktree(root: Path, untracked_before: set[str]) -> None:
    """Undo the working-tree changes a task made.

    Reverts tracked modifications (``git checkout -- .``) and deletes untracked
    files that appeared during the task; untracked files that already existed
    before the task are left untouched.
    """
    subprocess.run(
        ["git", "-C", str(root), "checkout", "--", "."],
        capture_output=True,
        text=True,
    )
    new_untracked = _git_untracked(root) - untracked_before
    for rel in new_untracked:
        target = root / rel
        try:
            if target.is_file() or target.is_symlink():
                target.unlink()
        except OSError as exc:
            log.warning("Could not remove task-created file %s: %s", target, exc)


def run_task_verified(task: str, config: TaskillConfig, *, dry_run: bool) -> TaskRun:
    """Run a task, then gate on ``verify``; roll back the working tree on failure."""
    root = config.project_root
    has_git = (root / ".git").exists()
    guard = has_git and (bool(config.koru.verify) or config.koru.rollback_on_fail)
    untracked_before = _git_untracked(root) if (guard and not dry_run) else set()

    run = run_task(task, config, dry_run=dry_run)
    if dry_run or run.skipped:
        return run

    def _fail(reason: str) -> TaskRun:
        rolled = False
        if config.koru.rollback_on_fail and has_git:
            rollback_worktree(root, untracked_before)
            rolled = True
        rc = run.returncode if run.returncode != 0 else 1
        return TaskRun(task=task, returncode=rc, reason=reason, rolled_back=rolled)

    if run.returncode != 0:
        return _fail("command error")

    passed, failed_cmd = run_verify(config, task)
    if not passed:
        return _fail(f"verify: {failed_cmd}")

    return run


def mark_task_done(todo_path: Path, task: str) -> bool:
    """Tick the ``- [ ]`` checkbox for ``task`` in the TODO file. Returns True on change."""
    if not todo_path.exists():
        return False
    lines = todo_path.read_text(encoding="utf-8").splitlines(keepends=True)
    changed = False
    for i, line in enumerate(lines):
        m = _UNCHECKED_RE.match(line)
        if m and m.group("text").strip() == task:
            lines[i] = line.replace("[ ]", "[x]", 1)
            changed = True
            break
    if changed:
        todo_path.write_text("".join(lines), encoding="utf-8")
    return changed
