"""Update CHANGELOG.md following the Keep a Changelog convention.

Strategy:
- Keep the file's prelude (intro before first version heading).
- Find or create the `## [Unreleased]` section.
- Append new entries under it (deduplicated by exact line match).
"""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path

UNRELEASED_HEADING = "## [Unreleased]"

DEFAULT_HEADER = """# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

"""


def update_changelog(path: Path, entries: list[str]) -> bool:
    """Append entries under [Unreleased]. Returns True if the file changed."""
    if not entries:
        return False

    if path.exists():
        original = path.read_text(encoding="utf-8")
    else:
        original = DEFAULT_HEADER + UNRELEASED_HEADING + "\n\n"

    # ensure [Unreleased] section exists
    if UNRELEASED_HEADING not in original:
        # insert it after the header (after first blank line following "# Changelog")
        if original.startswith("# "):
            head, _, tail = original.partition("\n\n")
            original = f"{head}\n\n{UNRELEASED_HEADING}\n\n{tail}"
        else:
            original = UNRELEASED_HEADING + "\n\n" + original

    # find the [Unreleased] block (until next "## [" or EOF)
    pattern = re.compile(
        rf"({re.escape(UNRELEASED_HEADING)}\n)(.*?)(?=^## \[|\Z)",
        re.DOTALL | re.MULTILINE,
    )
    m = pattern.search(original)
    if not m:
        # shouldn't happen, but fail safely
        return False

    block_body = m.group(2)
    existing_lines = set(line.rstrip() for line in block_body.splitlines() if line.strip())

    # add only genuinely new entries; preserve order from `entries`
    new_lines: list[str] = []
    for entry in entries:
        clean = entry.rstrip()
        if clean and clean not in existing_lines:
            new_lines.append(clean)
            existing_lines.add(clean)

    if not new_lines:
        return False

    # rebuild block: keep original body, append new bullets at the end of the
    # appropriate subsection if a heading-of-headings exists; otherwise dump at end
    new_block = block_body.rstrip() + "\n\n" + "\n".join(new_lines) + "\n\n"
    updated = original[:m.start(2)] + new_block + original[m.end(2):]

    path.write_text(updated, encoding="utf-8")
    return True


def release_unreleased(path: Path, version: str, today: date | None = None) -> bool:
    """Move [Unreleased] block to a versioned [x.y.z] - YYYY-MM-DD heading.

    Optional helper, not invoked by default. Useful for `taskill release`.
    """
    if not path.exists():
        return False
    today = today or date.today()
    txt = path.read_text(encoding="utf-8")
    if UNRELEASED_HEADING not in txt:
        return False
    new_heading = f"## [{version}] - {today.isoformat()}"
    txt = txt.replace(UNRELEASED_HEADING, f"{UNRELEASED_HEADING}\n\n{new_heading}", 1)
    path.write_text(txt, encoding="utf-8")
    return True
