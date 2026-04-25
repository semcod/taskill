"""Update TODO.md.

Two operations:
  1. Remove (or strike-through) lines that are now done.
  2. Append newly-discovered TODOs.

Behavior is conservative — we never delete user-authored text we don't recognize.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from taskill.git_state import ProjectSnapshot
from taskill.updaters.base import DocumentUpdater, UpdateResult

DEFAULT_HEADER = "# TODO\n\n"


class TodoUpdater(DocumentUpdater):
    """Updater for TODO.md files."""

    name = "todo"

    def apply(
        self,
        path: Path,
        snapshot: ProjectSnapshot,
        docs: dict[str, Any],
    ) -> UpdateResult:
        """Apply todo updates from generated docs."""
        completed = docs.get("todo_completed", [])
        new_items = docs.get("todo_new", [])
        archive_completed = self.options.get("archive_completed", True)
        changed = self._update_todo(path, completed, new_items, archive_completed=archive_completed)
        return UpdateResult(changed=changed, path=path, updater_name=self.name)

    @staticmethod
    def _partition_lines(lines: list[str], completed_set: set[str]) -> tuple[list[str], list[str]]:
        kept: list[str] = []
        archived: list[str] = []
        for line in lines:
            if line.rstrip() in completed_set and line.strip().startswith(("-", "*", "+")):
                archived.append(line)
            else:
                kept.append(line)
        return kept, archived

    @staticmethod
    def _dedup_new_items(kept: list[str], new_items: list[str]) -> list[str]:
        existing = {line.strip() for line in kept if line.strip()}
        return [item for item in new_items if item.strip() not in existing]

    @staticmethod
    def _assemble_output(
        kept: list[str],
        fresh_new: list[str],
        archived: list[str],
        *,
        archive_completed: bool = True,
    ) -> list[str]:
        out_lines = list(kept)
        if fresh_new:
            if out_lines and out_lines[-1].strip():
                out_lines.append("")
            if not any(line.startswith("# ") for line in out_lines):
                out_lines = ["# TODO", ""] + out_lines
            out_lines.append("## Discovered")
            out_lines.append("")
            out_lines.extend(fresh_new)
            out_lines.append("")
        if archive_completed and archived:
            out_lines.append("")
            out_lines.append("## Done (moved to CHANGELOG)")
            out_lines.append("")
            out_lines.extend(archived)
            out_lines.append("")
        return out_lines

    def _update_todo(
        self,
        path: Path,
        completed_lines: list[str],
        new_items: list[str],
        *,
        archive_completed: bool = True,
    ) -> bool:
        """Remove completed_lines from TODO and append new_items. Returns True on change."""
        if not (completed_lines or new_items):
            return False

        if path.exists():
            original = path.read_text(encoding="utf-8")
        else:
            original = DEFAULT_HEADER

        lines = original.splitlines(keepends=False)
        completed_set = {line.rstrip() for line in completed_lines if line.strip()}

        kept, archived = self._partition_lines(lines, completed_set)
        fresh_new = self._dedup_new_items(kept, new_items)
        out_lines = self._assemble_output(
            kept, fresh_new, archived, archive_completed=archive_completed,
        )

        joined = "\n".join(out_lines).rstrip()
        new_content = f"{joined}\n"
        if new_content == original:
            return False

        path.write_text(new_content, encoding="utf-8")
        return True


# Backward-compatible wrapper function
def update_todo(
    path: Path,
    completed_lines: list[str],
    new_items: list[str],
    *,
    archive_completed: bool = True,
) -> bool:
    """Remove completed_lines from TODO and append new_items. Returns True on change."""
    updater = TodoUpdater()
    return updater._update_todo(
        path, completed_lines, new_items, archive_completed=archive_completed,
    )


def empty_todo(path: Path, header: str = DEFAULT_HEADER) -> None:
    """Reset TODO.md to a clean empty header. Used by `taskill clean-todo`."""
    path.write_text(header, encoding="utf-8")
