"""Updater tests — keep edits idempotent and bounded."""
from __future__ import annotations

from pathlib import Path

from taskill.git_state import ProjectSnapshot
from taskill.updaters.changelog import release_unreleased, update_changelog
from taskill.updaters.readme import END, START, update_readme
from taskill.updaters.todo import empty_todo, update_todo

# ─── changelog ───────────────────────────────────────────────────────────

def test_changelog_creates_file_with_entries(tmp_path: Path) -> None:
    cl = tmp_path / "CHANGELOG.md"
    changed = update_changelog(cl, ["### Added", "- thing one"])
    assert changed
    text = cl.read_text(encoding="utf-8")
    assert "## [Unreleased]" in text
    assert "thing one" in text


def test_changelog_appends_to_unreleased(tmp_path: Path) -> None:
    cl = tmp_path / "CHANGELOG.md"
    cl.write_text(
        "# Changelog\n\n## [Unreleased]\n\n### Added\n- existing\n\n"
        "## [0.1.0] - 2026-01-01\n\n- old\n",
        encoding="utf-8",
    )
    update_changelog(cl, ["### Added", "- newcomer"])
    txt = cl.read_text(encoding="utf-8")
    # newcomer must land in [Unreleased], not after [0.1.0]
    unrel_idx = txt.index("[Unreleased]")
    v01_idx = txt.index("[0.1.0]")
    assert unrel_idx < txt.index("newcomer") < v01_idx
    assert "existing" in txt  # didn't clobber prior content


def test_changelog_dedupes_existing_entries(tmp_path: Path) -> None:
    cl = tmp_path / "CHANGELOG.md"
    update_changelog(cl, ["### Added", "- duplicate"])
    update_changelog(cl, ["### Added", "- duplicate"])
    txt = cl.read_text(encoding="utf-8")
    assert txt.count("- duplicate") == 1


def test_changelog_empty_entries_no_op(tmp_path: Path) -> None:
    cl = tmp_path / "CHANGELOG.md"
    assert update_changelog(cl, []) is False
    assert not cl.exists()


def test_release_promotes_unreleased(tmp_path: Path) -> None:
    cl = tmp_path / "CHANGELOG.md"
    cl.write_text("# Changelog\n\n## [Unreleased]\n\n- thing\n", encoding="utf-8")
    assert release_unreleased(cl, "0.2.0")
    txt = cl.read_text(encoding="utf-8")
    assert "## [0.2.0]" in txt
    # original [Unreleased] heading still there (above the new versioned one)
    assert "[Unreleased]" in txt


# ─── todo ────────────────────────────────────────────────────────────────

def test_todo_archives_completed(tmp_path: Path) -> None:
    td = tmp_path / "TODO.md"
    td.write_text("# TODO\n\n- [x] done\n- not done\n", encoding="utf-8")
    update_todo(td, ["- [x] done"], [])
    txt = td.read_text(encoding="utf-8")
    assert "Done (moved to CHANGELOG)" in txt
    # the line moved out of the active list
    active_section = txt.split("Done (moved")[0]
    assert "[x] done" not in active_section


def test_todo_appends_new_under_discovered(tmp_path: Path) -> None:
    td = tmp_path / "TODO.md"
    td.write_text("# TODO\n\n- existing\n", encoding="utf-8")
    update_todo(td, [], ["- [ ] brand new"])
    txt = td.read_text(encoding="utf-8")
    assert "## Discovered" in txt
    assert "brand new" in txt
    assert "existing" in txt


def test_todo_dedupes_new_items(tmp_path: Path) -> None:
    td = tmp_path / "TODO.md"
    td.write_text("# TODO\n\n- [ ] already there\n", encoding="utf-8")
    update_todo(td, [], ["- [ ] already there", "- [ ] new one"])
    txt = td.read_text(encoding="utf-8")
    assert txt.count("already there") == 1
    assert "new one" in txt


def test_todo_no_change_no_write(tmp_path: Path) -> None:
    td = tmp_path / "TODO.md"
    td.write_text("# TODO\n", encoding="utf-8")
    assert update_todo(td, [], []) is False


def test_empty_todo_resets(tmp_path: Path) -> None:
    td = tmp_path / "TODO.md"
    td.write_text("# TODO\n\n- a\n- b\n", encoding="utf-8")
    empty_todo(td)
    assert td.read_text(encoding="utf-8") == "# TODO\n\n"


# ─── readme ──────────────────────────────────────────────────────────────

def _snap() -> ProjectSnapshot:
    return ProjectSnapshot(
        head_sha="abc1234567890",
        commits_since_last_run=[],
        coverage_pct=87.5,
        failed_tests=0,
    )


def test_readme_inserts_status_when_no_markers(tmp_path: Path) -> None:
    rm = tmp_path / "README.md"
    rm.write_text("# My Project\n\nIntro paragraph.\n", encoding="utf-8")
    update_readme(rm, _snap(), "test summary")
    txt = rm.read_text(encoding="utf-8")
    assert START in txt and END in txt
    assert "Intro paragraph." in txt   # didn't touch existing content
    assert "abc1234" in txt
    assert "87.5%" in txt


def test_readme_replaces_only_marker_block(tmp_path: Path) -> None:
    rm = tmp_path / "README.md"
    rm.write_text(
        f"# Top\n\n## Manual section\nhand-written\n\n{START}\nold status\n{END}\n\n## Footer\n",
        encoding="utf-8",
    )
    update_readme(rm, _snap(), "new summary")
    txt = rm.read_text(encoding="utf-8")
    assert "hand-written" in txt
    assert "Footer" in txt
    assert "old status" not in txt
    assert "new summary" in txt


def test_readme_creates_file_when_missing(tmp_path: Path) -> None:
    rm = tmp_path / "README.md"
    update_readme(rm, _snap(), "fresh start")
    assert rm.exists()
    txt = rm.read_text(encoding="utf-8")
    assert "fresh start" in txt
