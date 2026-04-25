"""Tests for the algorithmic provider — the safety net must always work."""
from __future__ import annotations

from taskill.git_state import Commit, ProjectSnapshot
from taskill.providers.algorithmic import AlgorithmicProvider


def _commit(subject: str, body: str = "") -> Commit:
    return Commit(
        sha="0" * 40, short_sha="0000000",
        author="Test", date="2026-04-25T10:00:00Z",
        subject=subject, body=body,
    )


def _snap(commits: list[Commit]) -> ProjectSnapshot:
    return ProjectSnapshot(head_sha="abc123", commits_since_last_run=commits)


def test_groups_commits_by_conventional_type():
    p = AlgorithmicProvider()
    snap = _snap([
        _commit("feat: add OAuth"),
        _commit("fix: nullptr in parser"),
        _commit("feat(api): paginate /users"),
        _commit("just a regular message"),
    ])
    out = p.generate({"snapshot": snap, "existing_todo": ""})

    joined = "\n".join(out.changelog_entries)
    assert "### Added" in joined
    assert "### Fixed" in joined
    assert "### Other" in joined  # uncategorized commit
    assert "add OAuth" in joined
    assert "nullptr in parser" in joined


def test_breaking_change_surfaces_first():
    p = AlgorithmicProvider()
    snap = _snap([
        _commit("feat!: removed legacy /v1 endpoint"),
        _commit("fix: typo"),
    ])
    out = p.generate({"snapshot": snap, "existing_todo": ""})
    assert out.changelog_entries[0].startswith("### ⚠ BREAKING")


def test_detects_explicit_checkbox_completion():
    todo = """# TODO

- [ ] not done yet
- [x] this is done
* [X] capital X also counts
"""
    p = AlgorithmicProvider()
    out = p.generate({"snapshot": _snap([]), "existing_todo": todo})
    assert any("this is done" in line for line in out.todo_completed)
    assert any("capital X" in line for line in out.todo_completed)
    assert not any("not done yet" in line for line in out.todo_completed)


def test_detects_completion_via_token_overlap():
    todo = "- implement OAuth login flow with refresh tokens\n- something unrelated"
    p = AlgorithmicProvider()
    snap = _snap([_commit("feat: implement OAuth refresh token rotation")])
    out = p.generate({"snapshot": snap, "existing_todo": todo})
    assert any("OAuth" in line for line in out.todo_completed)


def test_extracts_new_todos_from_commit_bodies():
    p = AlgorithmicProvider()
    snap = _snap([
        _commit("fix: parser bug",
                body="Fixed the immediate issue.\nTODO: refactor the tokenizer"),
        _commit("feat: caching", body="FIXME: invalidation strategy"),
    ])
    out = p.generate({"snapshot": snap, "existing_todo": ""})
    text = "\n".join(out.todo_new)
    assert "tokenizer" in text
    assert "invalidation" in text


def test_empty_input_is_safe():
    p = AlgorithmicProvider()
    out = p.generate({"snapshot": _snap([]), "existing_todo": ""})
    assert out.changelog_entries == []
    assert out.todo_completed == []
    assert out.todo_new == []
    assert "No new commits" in out.summary


def test_always_available():
    assert AlgorithmicProvider().is_available() is True
