"""README updater — refresh marked sections only.

Philosophy: never overwrite the whole README. We only touch sections wrapped in
HTML comment markers, so users can curate the rest by hand:

    <!-- taskill:status:start -->
    ...auto-generated content...
    <!-- taskill:status:end -->

If the markers don't exist, we append a status block at the bottom.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from taskill.git_state import ProjectSnapshot
from taskill.updaters.base import DocumentUpdater, UpdateResult

START = "<!-- taskill:status:start -->"
END = "<!-- taskill:status:end -->"


def render_status_block(snapshot: ProjectSnapshot, summary: str) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    coverage = f"{snapshot.coverage_pct:.1f}%" if snapshot.coverage_pct is not None else "—"
    failed = (
        str(snapshot.failed_tests) if snapshot.failed_tests is not None else "—"
    )
    head = (snapshot.head_sha or "")[:7] or "—"

    lines = [
        START,
        "",
        "## Status",
        "",
        f"_Last updated by [taskill](https://github.com/oqlos/taskill) at {now}_",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| HEAD | `{head}` |",
        f"| Coverage | {coverage} |",
        f"| Failing tests | {failed} |",
        f"| Commits in last cycle | {len(snapshot.commits_since_last_run)} |",
    ]
    if summary:
        lines += ["", f"> {summary}"]
    lines += ["", END]
    return "\n".join(lines)


class ReadmeUpdater(DocumentUpdater):
    """Updater for README.md files."""

    name = "readme"

    def apply(
        self,
        path: Path,
        snapshot: ProjectSnapshot,
        docs: dict[str, Any],
    ) -> UpdateResult:
        """Apply readme updates from generated docs."""
        summary = docs.get("summary", "")
        changed = self._update_readme(path, snapshot, summary)
        return UpdateResult(changed=changed, path=path, updater_name=self.name)

    def _update_readme(self, path: Path, snapshot: ProjectSnapshot, summary: str) -> bool:
        block = render_status_block(snapshot, summary)

        if not path.exists():
            # don't invent a README — too presumptuous. Just write the block.
            path.write_text(f"# {path.parent.name}\n\n{block}\n", encoding="utf-8")
            return True

        original = path.read_text(encoding="utf-8")

        if START in original and END in original:
            pattern = re.compile(
                rf"{re.escape(START)}.*?{re.escape(END)}", re.DOTALL
            )
            updated = pattern.sub(block, original)
        else:
            sep = "\n\n" if not original.endswith("\n\n") else ""
            updated = original.rstrip() + "\n\n" + block + "\n"

        if updated == original:
            return False
        path.write_text(updated, encoding="utf-8")
        return True


# Backward-compatible wrapper function
def update_readme(path: Path, snapshot: ProjectSnapshot, summary: str) -> bool:
    """Update README.md with status block."""
    updater = ReadmeUpdater()
    return updater._update_readme(path, snapshot, summary)
