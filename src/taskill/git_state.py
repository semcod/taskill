"""Read project state from git, filesystem, and (optionally) pyqual reports."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Commit:
    sha: str
    short_sha: str
    author: str
    date: str
    subject: str
    body: str = ""

    @property
    def conventional_type(self) -> str | None:
        """Parse 'feat(scope): xxx' → 'feat'. Returns None if not conventional."""
        m = re.match(r"^(feat|fix|docs|chore|refactor|test|perf|ci|build|style|revert)(\([^)]+\))?!?:\s",
                     self.subject)
        return m.group(1) if m else None

    @property
    def is_breaking(self) -> bool:
        return "!" in self.subject.split(":")[0] or "BREAKING CHANGE" in self.body


@dataclass
class ProjectSnapshot:
    head_sha: str | None
    commits_since_last_run: list[Commit] = field(default_factory=list)
    changed_files: list[str] = field(default_factory=list)
    coverage_pct: float | None = None
    failed_tests: int | None = None
    sumd_hash: str | None = None
    sumd_text: str | None = None
    sumr_text: str | None = None


SUBPROCESS_TIMEOUT = 30


def _run(cmd: list[str], cwd: Path) -> str:
    try:
        out = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, check=False, timeout=SUBPROCESS_TIMEOUT
        )
        return out.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ""


def head_sha(project_root: Path) -> str | None:
    sha = _run(["git", "rev-parse", "HEAD"], project_root)
    return sha or None


def commits_since(project_root: Path, since_sha: str | None) -> list[Commit]:
    """Get commits since a SHA (exclusive). If since_sha is None, return last 50."""
    rng = f"{since_sha}..HEAD" if since_sha else "-50"
    sep = "\x1e"  # record sep
    fmt = f"%H{sep}%h{sep}%an{sep}%aI{sep}%s{sep}%b\x1f"
    raw = _run(["git", "log", rng, f"--pretty=format:{fmt}"], project_root)
    if not raw:
        return []
    commits: list[Commit] = []
    for record in raw.split("\x1f"):
        record = record.strip("\n")
        if not record:
            continue
        parts = record.split(sep)
        if len(parts) < 5:
            continue
        sha, short, author, date, subject = parts[:5]
        body = parts[5] if len(parts) > 5 else ""
        commits.append(Commit(sha=sha, short_sha=short, author=author,
                              date=date, subject=subject, body=body))
    return commits


def changed_files_since(project_root: Path, since_sha: str | None) -> list[str]:
    if not since_sha:
        return []
    out = _run(["git", "diff", "--name-only", f"{since_sha}..HEAD"], project_root)
    return [line for line in out.splitlines() if line]


def read_coverage(project_root: Path) -> float | None:
    """Look for common coverage report locations."""
    for candidate in ("coverage.json", ".coverage.json", "htmlcov/coverage.json"):
        p = project_root / candidate
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                pct = data.get("totals", {}).get("percent_covered")
                if pct is not None:
                    return float(pct)
            except (json.JSONDecodeError, KeyError, TypeError):
                pass
    # coverage.xml — minimal extraction
    xml = project_root / "coverage.xml"
    if xml.exists():
        m = re.search(r'line-rate="([0-9.]+)"', xml.read_text(encoding="utf-8"))
        if m:
            return float(m.group(1)) * 100
    return None


def read_failed_tests(project_root: Path) -> int | None:
    """Look for pytest junit xml or pyqual report."""
    for candidate in ("junit.xml", "test-results.xml", "reports/junit.xml"):
        p = project_root / candidate
        if p.exists():
            xml = p.read_text(encoding="utf-8")
            m = re.search(r'failures="(\d+)"', xml)
            e = re.search(r'errors="(\d+)"', xml)
            if m:
                return int(m.group(1)) + (int(e.group(1)) if e else 0)
    return None


def file_hash(path: Path) -> str | None:
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def collect_snapshot(
    project_root: Path,
    files: dict[str, str],
    last_commit_sha: str | None,
) -> ProjectSnapshot:
    sumd_path = project_root / files.get("sumd", "SUMD.md")
    sumr_path = project_root / files.get("sumr", "SUMR.md")

    return ProjectSnapshot(
        head_sha=head_sha(project_root),
        commits_since_last_run=commits_since(project_root, last_commit_sha),
        changed_files=changed_files_since(project_root, last_commit_sha),
        coverage_pct=read_coverage(project_root),
        failed_tests=read_failed_tests(project_root),
        sumd_hash=file_hash(sumd_path),
        sumd_text=sumd_path.read_text(encoding="utf-8") if sumd_path.exists() else None,
        sumr_text=sumr_path.read_text(encoding="utf-8") if sumr_path.exists() else None,
    )
