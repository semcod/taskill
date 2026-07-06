"""Config loading: taskill.yaml + .env.

Mirrors pyqual's config style (declarative, YAML-first, profile-friendly).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

# ───────────────────────────── data classes ─────────────────────────────


@dataclass
class Triggers:
    """Conditions that must be met to run an update.

    All thresholds are OR-ed by default (any one true → run).
    Set `require_all: true` for AND semantics.
    """

    min_hours_since_last_run: float = 24.0
    min_commits_since_last_run: int = 1
    changed_files_threshold: int = 1
    coverage_change_pct: float | None = None
    failed_tests_changed: bool = False
    require_all: bool = False
    # File-mtime triggers (optional)
    watch_files: list[str] = field(default_factory=lambda: ["SUMD.md", "SUMR.md"])


@dataclass
class ProviderConfig:
    """Single provider configuration."""

    name: str  # "windsurf_mcp" | "openrouter" | "algorithmic"
    enabled: bool = True
    options: dict[str, Any] = field(default_factory=dict)


@dataclass
class IntegrationConfig:
    """Optional CI / VCS / orchestrator integration."""

    github: dict[str, Any] = field(default_factory=dict)
    gitlab: dict[str, Any] = field(default_factory=dict)
    ansible: dict[str, Any] = field(default_factory=dict)


# Default command template taskill shells out to for each task. ``{task}`` is
# replaced with the task text. ``coru text ... --llm`` routes the natural-language
# task through coru's litellm planner (OpenRouter) and executes the mapped
# actions autonomously.
DEFAULT_KORU_COMMAND = ["coru", "text", "{task}", "--llm"]


@dataclass
class KoruConfig:
    """Autonomous task execution via the koru/coru ecosystem.

    When ``taskill`` runs with no subcommand, it resolves pending tasks from a
    list (see ``source``) and hands each one to ``command`` (default:
    ``coru text "<task>" --llm``) so coru executes it autonomously.
    """

    enabled: bool = True
    # Command template; a single "{task}" token is replaced with the task text.
    command: list[str] = field(default_factory=lambda: list(DEFAULT_KORU_COMMAND))
    # Where to read the task list from: "auto" tries todo → planfile → file.
    source: str = "auto"  # "auto" | "todo" | "planfile" | "file"
    # Path used when source is "file" (one task per non-empty, non-comment line).
    task_file: str = "TASK.md"
    # Cap tasks executed per invocation (None = no cap). Keep small for safety.
    max_tasks: int | None = 1
    # Skip the batch confirmation (equivalent to passing -y on the CLI).
    auto_confirm: bool = False
    # After a task succeeds, tick its "- [ ]" checkbox in TODO.md (todo source).
    mark_done: bool = True
    # Verification gate: commands run after each task. A string is run via the
    # shell; a list is run as argv. "{task}" is substituted. When any command
    # exits non-zero the task is marked FAILED (and rolled back if enabled), and
    # its TODO checkbox is NOT ticked. Empty list = no gate (legacy behavior).
    #   e.g. ["pytest -q", "pyqual", "prefact --check {task}"]
    verify: list = field(default_factory=list)
    # On a failed task (command error or failed verification), restore the
    # working tree: revert tracked changes and delete task-created untracked
    # files (pre-existing untracked files are left untouched).
    rollback_on_fail: bool = True


DEFAULT_FILES = {
    "readme": "README.md",
    "changelog": "CHANGELOG.md",
    "todo": "TODO.md",
    "sumd": "SUMD.md",
    "sumr": "SUMR.md",
}

DEFAULT_REUSE = {
    "pyqual": True,  # invoke `pyqual report` if available
    "llx": False,  # invoke llx for richer LLM context
    "prefact": False,  # invoke prefact for refactoring hints
}


@dataclass
class TaskillConfig:
    project_root: Path
    files: dict[str, str] = field(default_factory=lambda: dict(DEFAULT_FILES))
    triggers: Triggers = field(default_factory=Triggers)
    providers: list[ProviderConfig] = field(default_factory=list)
    integrations: IntegrationConfig = field(default_factory=IntegrationConfig)
    state_file: str = ".taskill/state.json"
    dry_run: bool = False
    reuse: dict[str, bool] = field(default_factory=lambda: dict(DEFAULT_REUSE))
    koru: KoruConfig = field(default_factory=KoruConfig)

    @property
    def env_model(self) -> str:
        return os.getenv("LLM_MODEL", "openrouter/qwen/qwen3-coder-next")

    @property
    def env_api_key(self) -> str | None:
        return os.getenv("OPENROUTER_API_KEY")


# ───────────────────────────── loader ─────────────────────────────

DEFAULT_PROVIDERS = [
    ProviderConfig(
        name="windsurf_mcp",
        enabled=True,
        options={
            "endpoint": "stdio",  # or ws://localhost:PORT
            "tool_name": "windsurf",
        },
    ),
    ProviderConfig(
        name="openrouter",
        enabled=True,
        options={
            "base_url": "https://openrouter.ai/api/v1",
            "temperature": 0.2,
            "max_tokens": 4096,
            "timeout": 120,  # seconds
        },
    ),
    ProviderConfig(name="algorithmic", enabled=True, options={}),
]


def load_config(
    path: str | Path = "taskill.yaml",
    project_root: Path | None = None,
) -> TaskillConfig:
    """Load config from YAML + .env. Missing YAML → defaults.

    Resolution order for project_root:
      1. explicit arg
      2. directory of taskill.yaml
      3. cwd
    """
    path = Path(path)
    if project_root is None:
        project_root = path.parent.resolve() if path.exists() else Path.cwd()

    # .env has higher priority than process env? No — process env wins (CI-friendly).
    env_path = project_root / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=False)

    raw: dict[str, Any] = {}
    if path.exists():
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    # Triggers
    trig_raw = raw.get("triggers", {})
    triggers = Triggers(
        min_hours_since_last_run=trig_raw.get("min_hours_since_last_run", 24.0),
        min_commits_since_last_run=trig_raw.get("min_commits_since_last_run", 1),
        changed_files_threshold=trig_raw.get("changed_files_threshold", 1),
        coverage_change_pct=trig_raw.get("coverage_change_pct"),
        failed_tests_changed=trig_raw.get("failed_tests_changed", False),
        require_all=trig_raw.get("require_all", False),
        watch_files=trig_raw.get("watch_files", ["SUMD.md", "SUMR.md"]),
    )

    # Providers (preserve order from YAML; if missing, use defaults)
    providers_raw = raw.get("providers")
    if providers_raw:
        providers = [
            ProviderConfig(
                name=p["name"],
                enabled=p.get("enabled", True),
                options=p.get("options", {}),
            )
            for p in providers_raw
        ]
    else:
        providers = DEFAULT_PROVIDERS

    # Integrations
    integ_raw = raw.get("integrations", {})
    integrations = IntegrationConfig(
        github=integ_raw.get("github", {}),
        gitlab=integ_raw.get("gitlab", {}),
        ansible=integ_raw.get("ansible", {}),
    )

    # Koru autonomous execution
    koru_raw = raw.get("koru", {}) or {}
    koru = KoruConfig(
        enabled=koru_raw.get("enabled", True),
        command=koru_raw.get("command", list(DEFAULT_KORU_COMMAND)),
        source=koru_raw.get("source", "auto"),
        task_file=koru_raw.get("task_file", "TASK.md"),
        max_tasks=koru_raw.get("max_tasks", 1),
        auto_confirm=koru_raw.get("auto_confirm", False),
        mark_done=koru_raw.get("mark_done", True),
        verify=koru_raw.get("verify", []) or [],
        rollback_on_fail=koru_raw.get("rollback_on_fail", True),
    )

    return TaskillConfig(
        project_root=Path(raw.get("project_root", project_root)).resolve(),
        files={**DEFAULT_FILES, **raw.get("files", {})},
        triggers=triggers,
        providers=providers,
        integrations=integrations,
        state_file=raw.get("state_file", ".taskill/state.json"),
        dry_run=raw.get("dry_run", False),
        reuse={**DEFAULT_REUSE, **raw.get("reuse", {})},
        koru=koru,
    )
