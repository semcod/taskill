"""Algorithmic fallback — no LLM required.

Strategy:
- Categorize commits via Conventional Commits prefixes.
- Move TODO lines that match commit subjects (fuzzy) to changelog.
- Detect '[x]' checkboxes in TODO and treat as completed.
- For new TODO items: scan commits for 'TODO:' / 'FIXME:' markers in body.

This is the safety net. Always available, always deterministic, ~zero deps.
"""
from __future__ import annotations

import re
from collections import defaultdict
from typing import Any

from taskill.providers.base import GeneratedDocs, Provider

CATEGORY_HEADINGS = {
    "feat":     "### Added",
    "fix":      "### Fixed",
    "perf":     "### Performance",
    "refactor": "### Changed",
    "docs":     "### Documentation",
    "test":     "### Tests",
    "build":    "### Build",
    "ci":       "### CI",
    "chore":    "### Chore",
    "style":    "### Style",
    "revert":   "### Reverted",
}


class AlgorithmicProvider(Provider):
    name = "algorithmic"

    def is_available(self) -> bool:
        return True  # always

    def generate(self, context: dict[str, Any]) -> GeneratedDocs:
        snap = context["snapshot"]
        existing_todo = context.get("existing_todo") or ""

        # 1. group commits by conventional type
        by_type: dict[str, list[str]] = defaultdict(list)
        breaking: list[str] = []
        uncategorized: list[str] = []
        for c in snap.commits_since_last_run:
            ctype = c.conventional_type
            line = self._format_commit(c)
            if c.is_breaking:
                breaking.append(line)
            if ctype:
                by_type[ctype].append(line)
            else:
                uncategorized.append(line)

        # 2. build changelog entries grouped by category
        entries: list[str] = []
        if breaking:
            entries.append("### ⚠ BREAKING CHANGES")
            entries.extend(breaking)
        for ctype in ["feat", "fix", "perf", "refactor", "docs", "test",
                      "build", "ci", "chore", "style", "revert"]:
            if by_type.get(ctype):
                entries.append(CATEGORY_HEADINGS[ctype])
                entries.extend(by_type[ctype])
        if uncategorized:
            entries.append("### Other")
            entries.extend(uncategorized)

        # 3. detect completed TODOs
        todo_completed = self._find_completed_todos(existing_todo, snap.commits_since_last_run)

        # 4. extract TODO/FIXME from commit bodies
        todo_new = self._extract_new_todos(snap.commits_since_last_run)

        n_total = len(snap.commits_since_last_run)
        summary = (
            f"{n_total} commit(s); "
            f"{len(by_type.get('feat', []))} features, "
            f"{len(by_type.get('fix', []))} fixes."
        ) if n_total else "No new commits — refreshing docs only."

        return GeneratedDocs(
            changelog_entries=entries,
            todo_completed=todo_completed,
            todo_new=todo_new,
            summary=summary,
            provider_name=self.name,
        )

    @staticmethod
    def _format_commit(commit) -> str:  # type: ignore[no-untyped-def]
        # strip the conventional prefix from the bullet text — heading already conveys it
        subject = re.sub(
            r"^(feat|fix|docs|chore|refactor|test|perf|ci|build|style|revert)(\([^)]+\))?!?:\s*",
            "",
            commit.subject,
        )
        return f"- {subject} ({commit.short_sha})"

    @staticmethod
    def _find_completed_todos(todo_text: str, commits) -> list[str]:  # type: ignore[no-untyped-def]
        """Return TODO lines that look completed.

        Two signals:
        1. Line starts with `- [x]` or `* [x]`  → explicitly checked off.
        2. Line content has high token overlap with a commit subject.
        """
        completed: list[str] = []
        for raw_line in todo_text.splitlines():
            line = raw_line.rstrip()
            if not line.strip():
                continue

            # explicit checkbox
            if re.match(r"^\s*[-*+]\s*\[[xX]\]", line):
                completed.append(line)
                continue

            # only check unchecked todo bullets
            m = re.match(r"^\s*[-*+]\s*(\[\s\]\s*)?(.+)$", line)
            if not m:
                continue
            text = m.group(2).lower()
            text_tokens = set(re.findall(r"\w{4,}", text))
            if len(text_tokens) < 2:
                continue
            for c in commits:
                commit_tokens = set(re.findall(r"\w{4,}", c.subject.lower()))
                if not commit_tokens:
                    continue
                overlap = text_tokens & commit_tokens
                # need ≥2 shared significant tokens AND ≥40% of TODO tokens covered.
                # 40% (not 50%) accommodates plurals/stems without proper stemming —
                # e.g. "refresh tokens" in TODO vs "refresh token" in commit.
                if len(overlap) >= 2 and len(overlap) / len(text_tokens) >= 0.4:
                    completed.append(line)
                    break
        return completed

    @staticmethod
    def _extract_new_todos(commits) -> list[str]:  # type: ignore[no-untyped-def]
        new: list[str] = []
        pat = re.compile(r"\b(TODO|FIXME|XXX)[:\s]+([^\n]+)", re.IGNORECASE)
        seen: set[str] = set()
        for c in commits:
            for m in pat.finditer(c.body or ""):
                _MAX_TODO_TEXT_LEN = 160
                text = m.group(2).strip().rstrip(".")[:_MAX_TODO_TEXT_LEN]
                if text and text.lower() not in seen:
                    seen.add(text.lower())
                    new.append(f"- [ ] {text}")
        return new
