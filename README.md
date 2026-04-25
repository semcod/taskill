# taskill


## AI Cost Tracking

![PyPI](https://img.shields.io/badge/pypi-costs-blue) ![Version](https://img.shields.io/badge/version-0.1.9-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)
![AI Cost](https://img.shields.io/badge/AI%20Cost-$1.20-orange) ![Human Time](https://img.shields.io/badge/Human%20Time-5.3h-blue) ![Model](https://img.shields.io/badge/Model-openrouter%2Fqwen%2Fqwen3--coder--next-lightgrey)

- 🤖 **LLM usage:** $1.2000 (8 commits)
- 👤 **Human dev:** ~$528 (5.3h @ $100/h, 30min dedup)

Generated on 2026-04-25 using [openrouter/qwen/qwen3-coder-next](https://openrouter.ai/qwen/qwen3-coder-next)

---

> Daily project hygiene: keep `README.md` / `CHANGELOG.md` / `TODO.md` in sync with reality.
> LLM-first, algorithmic fallback. Works standalone, in CI, or via Ansible.

`taskill` is the small daemon you stop forgetting to run. Once a day (or whenever metrics drift), it reads your git log, your `SUMD.md` / `SUMR.md`, your coverage report, and updates the three documentation files everyone tells themselves they'll keep current and never do.

It uses an LLM where one is available — Windsurf MCP first (because you're probably already running it in JetBrains), OpenRouter second — and falls back to a deterministic Conventional Commits parser when no LLM is reachable. The fallback is always available and always runs offline.

`taskill` deliberately doesn't replace `pyqual`, `llx`, or `prefact`. It calls them as subprocesses when configured, picks up their reports, and stays out of the way otherwise.

## Install

```bash
pip install taskill                    # core
pip install "taskill[mcp]"             # with Windsurf MCP support
pip install "taskill[mcp,schedule]"    # with built-in scheduler
```

## Quickstart

```bash
cd your-project/
taskill init                  # writes taskill.yaml + .env.example
cp .env.example .env          # add OPENROUTER_API_KEY
taskill status                # preview without running
taskill run --dry-run         # see what would change
taskill run                   # do it
```

## What it does

Every run produces three (idempotent) edits:

1. **`CHANGELOG.md`** — appends new entries under `## [Unreleased]`, grouped by Conventional Commit type (`### Added`, `### Fixed`, `### Performance`, etc.). Uses [Keep a Changelog](https://keepachangelog.com/) layout. Existing entries are deduplicated.
2. **`TODO.md`** — moves completed items to a `## Done (moved to CHANGELOG)` section, and appends `TODO:` / `FIXME:` markers found in new commit bodies under `## Discovered`.
3. **`README.md`** — refreshes only the block between `<!-- taskill:status:start -->` and `<!-- taskill:status:end -->` markers (HEAD, coverage, failing tests, summary). Never touches the rest of the file.

## Provider chain

The chain runs top-to-bottom. First provider that's available *and* succeeds wins.

| Order | Provider | Used when |
|---|---|---|
| 1 | `windsurf_mcp` | `mcp` package installed and a Windsurf endpoint resolves |
| 2 | `openrouter` | `OPENROUTER_API_KEY` is set |
| 3 | `algorithmic` | always — pure git-log + Conventional Commits parser |

You can reorder, disable, or pass options via `taskill.yaml`:

```yaml
providers:
  - name: openrouter         # skip windsurf, go straight to OpenRouter
    enabled: true
  - name: algorithmic
    enabled: true
```

## Triggers

`taskill run` is a no-op unless one of the configured thresholds is crossed. State lives in `.taskill/state.json` so cron, GitHub Actions, and Ansible all share the same delta logic.

```yaml
triggers:
  min_hours_since_last_run: 24
  min_commits_since_last_run: 1
  changed_files_threshold: 1
  coverage_change_pct: 2.0       # absolute pp; null to disable
  failed_tests_changed: true
  watch_files: [SUMD.md, SUMR.md]
  require_all: false             # OR by default; set true for AND
```

`taskill run --force` ignores triggers entirely.

## Running it

### Cron / systemd timer

```cron
0 6 * * * cd /path/to/project && /usr/local/bin/taskill run >> ~/.taskill.log 2>&1
```

### Bulk run (multiple projects)

For fleet-wide hygiene across many repos:

```bash
taskill bulk-run --root ~/github --max-depth 2
taskill bulk-run --root ~/github --max-depth 2 --dry-run  # preview
taskill bulk-run --root ~/github --filter taskill --filter testql  # filter repos
```

See `/daily-docs-update` workflow for complete documentation.

### GitHub Actions

See `examples/github-action.yml`. Triggers on `push` to main, runs `taskill run`, opens a PR if files changed.

### GitLab CI

See `examples/gitlab-ci.yml`. Same idea, with merge-request creation via the GitLab API.

### Ansible

See `examples/ansible-playbook.yml`. Useful for fleet-wide hygiene across many self-hosted repos.

## CLI

```
taskill init           # generate taskill.yaml + .env.example
taskill status         # show what would happen, no writes
taskill run            # execute (respects triggers)
taskill run --force    # ignore triggers
taskill run --dry-run  # don't write files or state
taskill run --json     # machine-readable output
taskill bulk-run       # run across all git repos in a directory
taskill release X.Y.Z  # promote [Unreleased] → versioned heading
taskill clean-todo     # wipe TODO.md (after a release)
```

## Bulk / fleet-wide runs

When you maintain many small repos (a personal "github" folder, a self-hosted
GitLab group, a monorepo of independent packages), `taskill bulk-run` runs the
same hygiene job across all of them with a single command:

```bash
# Scan ~/github (depth 2), use a shared taskill.yaml as the base config
taskill bulk-run --root ~/github --shared-config ~/github/taskill.yaml

# Same, but only run on repos whose name matches one of the filters
taskill bulk-run --root ~/github -f oqlos -f semcod

# Process at most 5 projects per run (useful for rate-limited LLMs)
taskill bulk-run --root ~/github --max-projects 5

# Preview without writing anything
taskill bulk-run --root ~/github --dry-run --force

# Machine-readable summary for CI / dashboards
taskill bulk-run --root ~/github --json
```

### Config resolution per repo

Per-repo `taskill.yaml` (or `.taskill.yaml`) takes precedence over the shared
config, so you can have one default policy plus per-project overrides. Repos
without any local config inherit the shared one with their own `project_root`.

Resolution order for each discovered repo:

1. `<repo>/taskill.yaml` — local override (highest priority)
2. `<repo>/.taskill.yaml` — alternative local override
3. Shared config from `--shared-config`, rebased onto the repo
4. Built-in defaults

### Discovery rules

`bulk-run` walks the directory tree starting at `--root` up to `--max-depth`
levels deep (default 2). A directory containing a `.git` entry is treated as a
repo, and `bulk-run` does **not** descend into nested repos. Hidden directories
and common noise (`node_modules`, `__pycache__`, `.venv`, `dist`, `build`,
`target`, `.tox`, `.pytest_cache`) are skipped automatically.

### Daily-run wrapper

A shell wrapper (`daily_update.sh`) reads its defaults from `.env`:

```bash
# .env
GITHUB_ROOT=$HOME/github
TASKILL_MAX_DEPTH=2
TASKILL_MAX_PROJECTS=10        # cap per cron tick
TASKILL_DRY_RUN=false
TASKILL_FORCE=false
TASKILL_FILTER=oqlos,semcod    # comma-separated
```

```bash
./daily_update.sh                              # uses .env
./daily_update.sh --dry-run                    # CLI override
./daily_update.sh --root /tmp/my-projects      # different root
./daily_update.sh --filter taskill,testql      # narrow scope
```

## Extending taskill: providers and updaters as plugins

Both providers (LLM/algorithmic backends) and document updaters (CHANGELOG /
TODO / README writers) are discovered through Python entry points, so a
third-party package can register a new provider or updater without touching
this codebase.

### Custom provider

```toml
# my_pkg/pyproject.toml
[project.entry-points."taskill.providers"]
my_provider = "my_pkg.provider:MyProvider"
```

```python
# my_pkg/provider.py
from taskill.providers.base import Provider, GeneratedDocs

class MyProvider(Provider):
    name = "my_provider"

    def is_available(self) -> bool:
        return True

    def generate(self, context) -> GeneratedDocs:
        ...
```

Then reference it from `taskill.yaml` like any built-in:

```yaml
providers:
  - name: my_provider
    enabled: true
    options: { ... }
  - name: algorithmic
    enabled: true
```

### Custom updater

```toml
[project.entry-points."taskill.updaters"]
wiki = "my_pkg.wiki:WikiUpdater"
```

```python
from taskill.updaters.base import DocumentUpdater, UpdateResult

class WikiUpdater(DocumentUpdater):
    name = "wiki"

    def apply(self, path, snapshot, docs) -> UpdateResult:
        ...
        return UpdateResult(changed=True, path=path, updater_name=self.name)
```

Built-in updaters (`changelog`, `todo`, `readme`) are registered the same way,
so removing or replacing them is just a matter of the entry-point taking
precedence.

## Configuration reference

See [`taskill.yaml`](./taskill.yaml) at the repo root for the annotated default config.

## Reusing existing tools

`taskill` doesn't try to absorb `pyqual` / `llx` / `prefact`. It calls them by `subprocess` when toggled in `reuse:` and feeds their JSON output to the LLM as extra context:

```yaml
reuse:
  pyqual: true       # taskill will run `pyqual report --json`
  llx: false         # ...add llx context (planned for v0.2)
  prefact: false     # ...add prefact suggestions (planned for v0.2)
```

If a tool isn't on `PATH`, `taskill` skips it silently — no hard dependency.

## How it relates to the wider stack

```
SUMD (description) ─┐
                    ├─→ taskill ──→ README.md
git log ────────────┤              CHANGELOG.md
pyqual report ──────┤              TODO.md
SUMR (state) ───────┘
```

`taskill` reads, never generates code. That's what `prefact` / `llx` / `pyqual` are for.

## License

Licensed under Apache-2.0.
## Status

_Last updated by [taskill](https://github.com/oqlos/taskill) at 2026-04-25 09:23 UTC_

| Metric | Value |
|---|---|
| HEAD | `4618c29` |
| Coverage | — |
| Failing tests | — |
| Commits in last cycle | 0 |

> No changes were made to the project since the last taskill run.

<!-- taskill:status:end -->
