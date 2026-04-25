---
description: Daily documentation update workflow across multiple projects
---

# Daily Documentation Update Workflow

This workflow automates the routine task of keeping README.md, CHANGELOG.md, and TODO.md in sync across multiple projects.

## Prerequisites

1. Install taskill: `pip install taskill[mcp,schedule]`
2. Set up OPENROUTER_API_KEY in .env files (or use Windsurf MCP)
3. Ensure each project has a taskill.yaml config

## Single Project

```bash
cd /path/to/project
taskill status          # Preview what would change
taskill run             # Execute the update
taskill run --dry-run   # Preview without writing
```

## Multiple Projects (Bulk Run)

### Option 1: Using CLI command

```bash
# Run taskill on all repos under ~/github
taskill bulk-run --root ~/github --max-depth 2

# Dry-run to preview
taskill bulk-run --root ~/github --max-depth 2 --dry-run

# Force run (ignore triggers)
taskill bulk-run --root ~/github --max-depth 2 --force

# Filter specific repos (repeatable)
taskill bulk-run --root ~/github --filter taskill --filter testql

# Limit number of projects per run (useful for rate-limited LLMs)
taskill bulk-run --root ~/github --max-projects 5

# Use a shared config + JSON output
taskill bulk-run --root ~/github \
  --shared-config ~/github/taskill.yaml \
  --max-projects 10 \
  --json
```

### Option 2: Using the shell wrapper

`daily_update.sh` wraps the CLI and reads its defaults from `.env`:

```bash
# .env in the project root
GITHUB_ROOT=$HOME/github
TASKILL_MAX_DEPTH=2
TASKILL_MAX_PROJECTS=10
TASKILL_DRY_RUN=false
TASKILL_FORCE=false
TASKILL_FILTER=oqlos,semcod    # comma-separated
```

```bash
./daily_update.sh                       # uses .env defaults
./daily_update.sh --dry-run             # preview only
./daily_update.sh --force               # ignore triggers
./daily_update.sh --filter taskill,testql
./daily_update.sh --root /tmp/projects  # override target directory
```

### Option 3: Using Python script

```python
from pathlib import Path
from taskill.bulk import bulk_run

result = bulk_run(
    root=Path("/home/tom/github"),
    shared_config=Path("/home/tom/github/taskill.yaml"),  # optional
    max_depth=2,
    max_projects=10,    # 0 = unlimited
    force=False,
    dry_run=False,
    repo_filter=["taskill", "testql"],  # optional substring match
)

print(result.summary())
# 3/5 ran, 2 changed, 1 skipped, 0 errors

for repo, repo_result in result.per_repo.items():
    print(repo.name, "ran" if repo_result.ran else "skipped",
          repo_result.files_changed)
```

## What taskill does

1. **CHANGELOG.md**: Appends new entries under [Unreleased] based on git commits
2. **TODO.md**: Moves completed items to "Done (moved to CHANGELOG)" section
3. **README.md**: Updates status block between markers (HEAD, coverage, failing tests)
4. **SUMD.md/SUMR.md**: Reads these files as context for the LLM provider

## Triggers

By default, taskill only runs when:
- At least 24 hours since last run
- At least 1 new commit
- Files changed threshold met
- SUMD.md or SUMR.md modified

Use `--force` to override triggers.

## Automation

### Cron job (daily at 6 AM)

```cron
0 6 * * * cd /home/tom/github && /usr/local/bin/taskill bulk-run --root . --max-depth 2 >> ~/.taskill.log 2>&1
```

### Systemd timer

See `examples/systemd-timer/taskill.service` and `taskill.timer`.

## Shared Config

Pass a shared `taskill.yaml` via `--shared-config` to provide a default config
for all discovered repos:

```bash
# ~/github/taskill.yaml (the shared base)
triggers:
  min_hours_since_last_run: 24
  min_commits_since_last_run: 1
providers:
  - name: openrouter
    enabled: true
  - name: algorithmic
    enabled: true
```

Resolution order per repo:

1. `<repo>/taskill.yaml` (highest priority)
2. `<repo>/.taskill.yaml`
3. `--shared-config` rebased onto the repo's path
4. Built-in defaults

Each repo can override only what it needs by dropping a partial `taskill.yaml`
into its own root.

## Troubleshooting

- Use `--verbose` flag for debug output
- Check `.taskill/state.json` for last run state
- Use `--dry-run` to preview changes
- Check provider chain in taskill.yaml (windsurf_mcp → openrouter → algorithmic)
