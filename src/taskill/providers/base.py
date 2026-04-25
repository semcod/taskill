"""Provider abstraction + shared types."""
from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


class ProviderError(Exception):
    """Provider failed — chain falls through to next provider."""


@dataclass
class GeneratedDocs:
    """What every provider returns."""
    readme: str | None = None
    changelog_entries: list[str] = None  # type: ignore[assignment]  # markdown bullets
    todo_completed: list[str] = None     # type: ignore[assignment]  # items to remove from TODO
    todo_new: list[str] = None           # type: ignore[assignment]  # new items detected
    summary: str = ""
    provider_name: str = "unknown"

    def __post_init__(self) -> None:
        if self.changelog_entries is None:
            self.changelog_entries = []
        if self.todo_completed is None:
            self.todo_completed = []
        if self.todo_new is None:
            self.todo_new = []


class Provider(ABC):
    """Abstract provider — produces docs from a project snapshot."""

    name: str = "abstract"

    def __init__(self, options: dict[str, Any] | None = None) -> None:
        self.options = options or {}

    @abstractmethod
    def is_available(self) -> bool:
        """Quick self-check. Should NOT raise — just return False."""

    @abstractmethod
    def generate(self, context: dict[str, Any]) -> GeneratedDocs:
        """Generate docs.

        `context` keys (see core.build_context):
          - snapshot: ProjectSnapshot
          - existing_readme, existing_changelog, existing_todo: str
          - sumd, sumr: str | None
          - project_name: str
          - pyqual_report: dict | None
        """


# ─── shared prompt template (used by LLM providers) ──────────────────────

SYSTEM_PROMPT = """You are taskill, a release-notes / docs janitor.
Given a project snapshot (commits, changed files, coverage, SUMD), output STRICT JSON:

{
  "summary": "1-2 sentence high-level description of what changed",
  "changelog_entries": ["- feat: thing one", "- fix: thing two"],
  "todo_completed": ["- exact text of TODO line that is now done"],
  "todo_new": ["- new thing discovered from commits"],
  "readme_patches": null
}

Rules:
- changelog_entries: markdown bullets, conventional-commits style if possible
- todo_completed: copy line text VERBATIM from the existing TODO; don't paraphrase
- Be conservative — when unsure, omit. False positives are worse than misses.
- Output ONLY JSON. No prose. No code fences.
"""


def build_user_prompt(context: dict[str, Any]) -> str:
    snap = context["snapshot"]
    commits = "\n".join(
        f"  {c.short_sha} {c.subject}" for c in snap.commits_since_last_run[:50]
    ) or "  (no new commits)"
    changed = "\n".join(f"  {f}" for f in snap.changed_files[:50]) or "  (none)"
    todo = context.get("existing_todo") or "(empty)"
    sumd = context.get("sumd") or "(no SUMD.md)"
    coverage = f"{snap.coverage_pct:.1f}%" if snap.coverage_pct else "n/a"
    failed = snap.failed_tests if snap.failed_tests is not None else "n/a"

    return f"""Project: {context.get('project_name', 'unknown')}

# Commits since last taskill run
{commits}

# Changed files
{changed}

# Coverage: {coverage}    Failed tests: {failed}

# Current TODO.md (truncated)
{todo[:4000]}

# SUMD.md (project structure summary, truncated)
{sumd[:3000]}

Now produce the JSON described in the system prompt."""


def parse_json_loosely(text: str) -> dict[str, Any] | None:
    """Be forgiving: strip ```json fences, extract first {...} block."""
    text = text.strip()
    # strip fences
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.MULTILINE)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # find first balanced { ... }
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
