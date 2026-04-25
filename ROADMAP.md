# taskill ROADMAP

This is the deliberate "what's next" plan. v0.1 is the working version. Everything below is the refactor + extensions you asked for, ordered by what unblocks the most use-cases.

## v0.1.0 — working baseline (shipped)

Provider chain (Windsurf MCP → OpenRouter → algorithmic), triggers, state, three updaters, CLI, integration examples. ~13 modules. Designed so v0.2 can extend without rewriting.

## v0.2 — first refactor wave

Goal: make every external touchpoint a real plugin instead of inline code.

### v0.2.1 — provider plugin protocol

The `Provider` ABC works for the three built-ins, but third-party providers should be discoverable through `entry_points`:

```toml
[project.entry-points."taskill.providers"]
my_provider = "my_pkg.provider:MyProvider"
```

The chain builder switches from a hard-coded registry (`providers/__init__.py:build_chain`) to a `pkg_resources.iter_entry_points` lookup. Existing built-ins re-register themselves through the same mechanism so there's no special-casing.

This is the single most important refactor — it turns "add another LLM" from a PR into a separate package.

### v0.2.2 — async-native MCP transport

The current `WindsurfMcpProvider` only handles stdio with a configured `command`, and it wraps the async MCP session in a synchronous `asyncio.run()` call from inside `generate()`. That's fine for a CLI but bad for:

- Servers that expose MCP over WebSocket / SSE / Unix socket
- Long-running daemons that already have an event loop
- Connection pooling across multiple `taskill run` invocations in the same process

Refactor: introduce `AsyncProvider` alongside `Provider`, push the async layer all the way to `Taskill.run()`, expose a `taskill.run_async()` entry point. Built-ins stay sync; only MCP and future streaming providers go async.

### v0.2.3 — pluggable updaters

Same protocol-via-entry_points story, but for documents. Some users want:

- Update a wiki page instead of `README.md`
- Sync `CHANGELOG.md` to GitHub Releases as it's written
- Mirror TODOs to a `TODO.json` for a custom dashboard

Move `update_changelog`, `update_todo`, `update_readme` behind a `DocumentUpdater` ABC with `apply(docs, snapshot, config) -> list[Path]`. Wire entry points the same way.

### v0.2.4 — `llx` and `prefact` reuse

Currently `core._maybe_pyqual_report()` is a one-off subprocess. Generalize it:

```yaml
reuse:
  pyqual:
    enabled: true
    command: ["pyqual", "report", "--json"]
    inject_as: pyqual_report
  llx:
    enabled: true
    command: ["llx", "context", "--format=json"]
    inject_as: llx_context
  prefact:
    enabled: true
    command: ["prefact", "suggest", "--json"]
    inject_as: prefact_suggestions
```

Each result is JSON-decoded and put into the LLM context dict under its `inject_as` key. The system prompt gets a corresponding "if X is provided, use it for Y" section. Adding a fourth tool is one YAML block, no code change.

This is the cleanest answer to your question "can these packages be reused?" — yes, but as data sources, not dependencies.

## v0.3 — CI/CD integrations as first-class citizens

Right now the GitHub Actions / GitLab CI / Ansible files in `examples/` are templates. Make them real:

### v0.3.1 — `taskill ci-config <provider>`

Generates the workflow file for the chosen CI:

```bash
taskill ci-config github > .github/workflows/taskill.yml
taskill ci-config gitlab > .gitlab-ci.yml
taskill ci-config ansible > playbooks/taskill.yml
```

The generated file already contains the right secrets (`OPENROUTER_API_KEY`), the right triggers (push to main, scheduled cron at 06:00 UTC), and the post-run PR/MR creation step.

### v0.3.2 — native PR/MR creators

Instead of relying on `peter-evans/create-pull-request@v6`, ship `taskill.integrations.github.open_pr()` and `taskill.integrations.gitlab.open_mr()`. They consume `TaskillResult.files_changed` and a token, push a branch, and open the PR/MR with the LLM's `summary` as the description.

This gives parity across CI providers and makes the "one tool, many backends" promise real.

### v0.3.3 — Ansible module

Ship `taskill.integrations.ansible_module` so users get a proper `community.taskill.run` module instead of `command: taskill run`. Lets fleet-wide hygiene runs report changed/unchanged correctly to Ansible.

## v0.4 — `pyqual`-style profiles

Right now every project starts from the same `taskill.yaml`. Borrow pyqual's `profile:` shortcut:

```yaml
profile: python-library
# expands to: triggers tuned for libraries, providers ordered for offline-first,
# pyqual reuse on, llx/prefact off
```

Profiles live in `taskill.profiles` and are user-extensible via the same entry-points pattern. Likely starting profiles: `python-library`, `python-app`, `monorepo-package`, `ci-only`, `windsurf-first`.

## v0.5 — multi-repo / monorepo

State management was designed with this in mind (it's per-config-file, not per-process). The missing pieces:

- `taskill bulk-run --root /home/me/github` — scan a directory tree, run taskill in every repo whose triggers fire
- Per-repo overrides via `.taskill.yaml` while a parent directory holds shared `taskill.yaml`
- Combined report so you can see "of 47 repos, 12 needed updates today, here are the diffs"

This is the layer that would replace the manual loop you're doing daily across `oqlos/testql`, `oqlos/pyqual`, etc.

## v0.6 — wider trigger sources

Currently triggers are local: git, files, coverage. Add:

- GitHub issue/PR activity (run when issues are closed referencing this repo)
- Webhook-driven (Slack message, Linear ticket, Jira)
- Scheduled-by-time-of-day with timezone awareness

The trigger system in `triggers.py` is already a list-of-rules with an `evaluate()` step, so this is "add new rule types," not "rewrite the engine."

## Things that are explicitly NOT planned

- **Generating code.** That's `prefact` / `llx`. taskill is a documentation janitor.
- **Replacing `pyqual`.** taskill *consumes* pyqual reports, never duplicates them.
- **A web UI.** Use the JSON output (`taskill run --json`) and your existing dashboard. The CLI/JSON contract is the API.
- **Bundling the `mcp` package as a hard dep.** It stays optional. Algorithmic fallback must always work without any extras installed.

## Migration notes (v0.1 → v0.2)

When v0.2 lands, existing `taskill.yaml` files keep working. The `providers:` list will accept both inline names (current behavior) and entry-point IDs (`my_pkg:my_provider`). The `reuse:` block changes from `bool` to `dict` — the loader will detect a bool and translate it to `{enabled: true}` automatically for one minor version, then warn, then drop the shim.

State files (`.taskill/state.json`) carry a schema version (added in v0.1, currently `1`); v0.2 will bump to `2` and migrate transparently on first read.

## How to contribute to this roadmap

These items are roughly priority-ordered, not promised by date. If you need something earlier, the simplest path is opening an issue with the use-case — most of v0.3 and beyond is shaped by what people actually run taskill against.
