"""Command-line interface for taskill.

Commands:
  taskill run        — execute the pipeline (respects triggers; --force overrides)
  taskill status     — show what would happen without running
  taskill init       — write a starter taskill.yaml + .env.example
  taskill release    — promote [Unreleased] CHANGELOG block to a versioned heading
  taskill clean-todo — wipe TODO.md (use after manually moving items elsewhere)
"""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from taskill import __version__
from taskill.bulk import bulk_run
from taskill.config import load_config
from taskill.core import Taskill
from taskill.updaters.changelog import release_unreleased
from taskill.updaters.todo import empty_todo

console = Console()


def _setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


@click.group()
@click.version_option(__version__, prog_name="taskill")
@click.option("--verbose", "-v", is_flag=True, help="Verbose logging")
@click.option(
    "--config", "-c", default="taskill.yaml", show_default=True,
    help="Path to taskill.yaml",
)
@click.pass_context
def main(ctx: click.Context, verbose: bool, config: str) -> None:
    """taskill — keep README/CHANGELOG/TODO honest."""
    _setup_logging(verbose)
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = config


@main.command()
@click.option("--force", is_flag=True, help="Run even if triggers say no")
@click.option("--dry-run", is_flag=True, help="Don't write files or persist state")
@click.option("--json", "as_json", is_flag=True, help="Output result as JSON")
@click.pass_context
def run(ctx: click.Context, force: bool, dry_run: bool, as_json: bool) -> None:
    """Execute the update pipeline."""
    cfg = load_config(ctx.obj["config_path"])
    if dry_run:
        cfg.dry_run = True
    tk = Taskill(config=cfg)
    result = tk.run(force=force)

    if as_json:
        click.echo(json.dumps(result.as_dict(), indent=2))
        sys.exit(0 if result.ran or not result.errors else 1)

    if not result.ran:
        console.print(f"[yellow]✗ Did not run.[/yellow] {result.trigger_eval.summary()}")
        if result.errors:
            for e in result.errors:
                console.print(f"  [red]error:[/red] {e}")
        sys.exit(0)

    console.print(
        f"[green]✓ Ran via [bold]{result.provider_used}[/bold][/green]"
    )
    if result.docs and result.docs.summary:
        console.print(f"  [dim]{result.docs.summary}[/dim]")

    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_row("Changelog entries", str(len(result.docs.changelog_entries) if result.docs else 0))
    table.add_row("TODO completed", str(len(result.docs.todo_completed) if result.docs else 0))
    table.add_row("TODO new", str(len(result.docs.todo_new) if result.docs else 0))
    table.add_row("Files changed", ", ".join(result.files_changed) or "(none)")
    console.print(table)

    if result.errors:
        console.print("[dim]Provider fallthrough:[/dim]")
        for e in result.errors:
            console.print(f"  [dim]- {e}[/dim]")


@main.command()
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
@click.pass_context
def status(ctx: click.Context, as_json: bool) -> None:
    """Show what taskill would do without running it."""
    cfg = load_config(ctx.obj["config_path"])
    tk = Taskill(config=cfg)
    info = tk.status()

    if as_json:
        click.echo(json.dumps(info, indent=2, default=str))
        return

    table = Table(title="taskill status", show_header=True, header_style="bold cyan")
    table.add_column("Field"); table.add_column("Value")
    color = "green" if info["would_run"] else "yellow"
    table.add_row("Would run?", f"[{color}]{info['would_run']}[/{color}]")
    table.add_row("HEAD", str(info["head"] or "—")[:12])
    table.add_row("Pending commits", str(info["commits_pending"]))
    table.add_row("Coverage", f"{info['coverage']:.1f}%" if info["coverage"] else "—")
    table.add_row("Failed tests", str(info["failed_tests"]) if info["failed_tests"] is not None else "—")
    table.add_row("Last run", str(info["last_run"] or "never"))
    console.print(table)

    if info["reasons"]:
        console.print("[green]Reasons to run:[/green]")
        for r in info["reasons"]:
            console.print(f"  • {r}")
    if info["skipped_because"]:
        console.print("[yellow]Why not running:[/yellow]")
        for r in info["skipped_because"]:
            console.print(f"  • {r}")


@main.command()
@click.option("--force", is_flag=True, help="Overwrite existing taskill.yaml")
def init(force: bool) -> None:
    """Generate a starter taskill.yaml + .env.example in the current directory."""
    yml = Path("taskill.yaml")
    env = Path(".env.example")

    if yml.exists() and not force:
        console.print(f"[yellow]{yml} already exists — use --force to overwrite[/yellow]")
        sys.exit(1)

    yml.write_text(STARTER_YAML, encoding="utf-8")
    if not env.exists():
        env.write_text(STARTER_ENV, encoding="utf-8")

    console.print(f"[green]✓[/green] Wrote {yml} and {env}")
    console.print("Next: copy [bold].env.example[/bold] → [bold].env[/bold] and add your OpenRouter key,")
    console.print("then run [cyan]taskill status[/cyan] to inspect, [cyan]taskill run[/cyan] to execute.")


@main.command()
@click.argument("version")
@click.option(
    "--changelog", default="CHANGELOG.md", show_default=True,
    help="Path to CHANGELOG.md",
)
def release(version: str, changelog: str) -> None:
    """Promote [Unreleased] section to a versioned [VERSION] heading."""
    p = Path(changelog)
    if release_unreleased(p, version):
        console.print(f"[green]✓[/green] Released v{version} in {p}")
    else:
        console.print(f"[yellow]Nothing to release in {p}[/yellow]")
        sys.exit(1)


@main.command("bulk-run")
@click.option(
    "--root", "-r", default=".", show_default=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Parent directory to scan for repos",
)
@click.option(
    "--shared-config", "-s", default=None,
    type=click.Path(exists=False),
    help="Optional shared taskill.yaml used as base for repos without their own config",
)
@click.option(
    "--max-depth", default=2, show_default=True, type=int,
    help="Max directory levels to descend looking for git repos",
)
@click.option(
    "--max-projects", default=0, show_default=True, type=int,
    help="Maximum number of projects to process (0 = unlimited)",
)
@click.option("--force", is_flag=True, help="Run even if triggers say no")
@click.option("--dry-run", is_flag=True, help="Don't write files or persist state")
@click.option("--json", "as_json", is_flag=True, help="Output result as JSON")
@click.option(
    "--filter", "-f", "repo_filter", multiple=True,
    help="Only run on repos whose name contains this substring (repeatable)",
)
def bulk_run_cmd(
    root: str,
    shared_config: str | None,
    max_depth: int,
    max_projects: int,
    force: bool,
    dry_run: bool,
    as_json: bool,
    repo_filter: tuple[str, ...],
) -> None:
    """Run taskill across all git repos under a directory.

    Useful for fleet-wide hygiene: keep README/CHANGELOG/TODO in sync
    across many self-hosted projects with a single shared config.
    """
    result = bulk_run(
        root=Path(root),
        shared_config=Path(shared_config) if shared_config else None,
        max_depth=max_depth,
        max_projects=max_projects,
        force=force,
        dry_run=dry_run,
        repo_filter=list(repo_filter) if repo_filter else None,
    )

    if as_json:
        click.echo(json.dumps(result.as_dict(), indent=2, default=str))
        sys.exit(0 if not result.errors else 1)

    console.print(f"[bold cyan]Bulk run:[/bold cyan] {result.root}")
    console.print(f"[dim]{result.summary()}[/dim]\n")

    if not result.per_repo and not result.skipped and not result.errors:
        console.print("[yellow]No repos found.[/yellow]")
        return

    table = Table(title="Per-repo results", show_header=True, header_style="bold cyan")
    table.add_column("Repo")
    table.add_column("Ran")
    table.add_column("Provider")
    table.add_column("Files changed")
    table.add_column("Note")

    for repo_path, repo_result in result.per_repo.items():
        ran_color = "green" if repo_result.ran else "yellow"
        ran_str = f"[{ran_color}]{repo_result.ran}[/{ran_color}]"
        provider = repo_result.provider_used or "—"
        files = ", ".join(repo_result.files_changed) or "—"
        note = ""
        if not repo_result.ran:
            note = repo_result.trigger_eval.summary()
        elif repo_result.errors:
            note = f"{len(repo_result.errors)} provider fallthroughs"
        table.add_row(repo_path.name, ran_str, provider, files, note)

    for repo_path, reason in result.skipped:
        table.add_row(repo_path.name, "[dim]skip[/dim]", "—", "—", reason)

    for repo_path, error in result.errors:
        table.add_row(repo_path.name, "[red]error[/red]", "—", "—", error)

    console.print(table)

    if result.errors:
        sys.exit(1)


@main.command("clean-todo")
@click.option("--todo", default="TODO.md", show_default=True)
@click.confirmation_option(prompt="This will erase TODO.md content. Continue?")
def clean_todo(todo: str) -> None:
    """Reset TODO.md to an empty header. Use after a release."""
    empty_todo(Path(todo))
    console.print(f"[green]✓[/green] {todo} reset")


# ─── starter templates ──────────────────────────────────────────────────

STARTER_YAML = """# taskill.yaml — daily project hygiene config
# Run: taskill status   (preview)
#      taskill run      (execute when triggers fire)
#      taskill run --force --dry-run   (preview the actual output)

# Files taskill manages
files:
  readme: README.md
  changelog: CHANGELOG.md
  todo: TODO.md
  sumd: SUMD.md
  sumr: SUMR.md

# When should taskill run?  (OR semantics by default — any one true → run)
triggers:
  min_hours_since_last_run: 24
  min_commits_since_last_run: 1
  changed_files_threshold: 1
  coverage_change_pct: 2.0      # absolute pp; null to disable
  failed_tests_changed: true
  watch_files: [SUMD.md, SUMR.md]
  require_all: false            # set true for AND semantics

# Provider chain — first one that succeeds wins.
# Comment out any provider you don't want.
providers:
  - name: windsurf_mcp
    enabled: true
    options:
      endpoint: stdio
      command: ["windsurf", "mcp", "serve"]
      tool_name: complete
  - name: openrouter
    enabled: true
    options:
      base_url: https://openrouter.ai/api/v1
      temperature: 0.2
      max_tokens: 4096
      timeout: 120
  - name: algorithmic
    enabled: true     # always-on safety net; keep this on

# Optional: reuse other tools in your stack (loose coupling — subprocess calls)
reuse:
  pyqual: true
  llx: false
  prefact: false

# Where state lives (tracks last run, last sha, last coverage…)
state_file: .taskill/state.json

# CI/VCS integrations — read by `taskill ci-config` (stub for now)
integrations:
  github: {}
  gitlab: {}
  ansible: {}

dry_run: false
"""

STARTER_ENV = """# Copy this file to .env and fill in your credentials.
# .env is loaded automatically by taskill (process env wins on conflict).

OPENROUTER_API_KEY=

# Default: openrouter/qwen/qwen3-coder-next
# (taskill auto-strips the openrouter/ prefix for the OpenRouter REST API)
LLM_MODEL=openrouter/qwen/qwen3-coder-next

# Optional: explicit Windsurf MCP endpoint (otherwise auto-discovered)
# WINDSURF_MCP_ENDPOINT=ws://localhost:7777
"""


if __name__ == "__main__":
    main()
