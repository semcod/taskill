# System Architecture Analysis

## Overview

- **Project**: /home/tom/github/semcod/taskill
- **Primary Language**: python
- **Languages**: python: 18, yaml: 12, yml: 3, txt: 2, shell: 2
- **Analysis Mode**: static
- **Total Functions**: 172
- **Total Classes**: 22
- **Modules**: 38
- **Entry Points**: 142

## Architecture by Module

### project.map.toon
- **Functions**: 102
- **File**: `map.toon.yaml`

### src.taskill.core
- **Functions**: 9
- **Classes**: 2
- **File**: `core.py`

### src.taskill.cli
- **Functions**: 8
- **File**: `cli.py`

### src.taskill.git_state
- **Functions**: 8
- **Classes**: 2
- **File**: `git_state.py`

### src.taskill.bulk
- **Functions**: 7
- **Classes**: 1
- **File**: `bulk.py`

### src.taskill.providers.base
- **Functions**: 5
- **Classes**: 3
- **File**: `base.py`

### src.taskill.providers.algorithmic
- **Functions**: 5
- **Classes**: 1
- **File**: `algorithmic.py`

### src.taskill.updaters.readme
- **Functions**: 4
- **Classes**: 1
- **File**: `readme.py`

### src.taskill.updaters.changelog
- **Functions**: 4
- **Classes**: 1
- **File**: `changelog.py`

### src.taskill.updaters.todo
- **Functions**: 4
- **Classes**: 1
- **File**: `todo.py`

### src.taskill.providers.windsurf_mcp
- **Functions**: 4
- **Classes**: 1
- **File**: `windsurf_mcp.py`

### src.taskill.providers.openrouter
- **Functions**: 4
- **Classes**: 1
- **File**: `openrouter.py`

### src.taskill.state
- **Functions**: 3
- **Classes**: 1
- **File**: `state.py`

### src.taskill.triggers
- **Functions**: 2
- **Classes**: 1
- **File**: `triggers.py`

### src.taskill.updaters.base
- **Functions**: 2
- **Classes**: 2
- **File**: `base.py`

### src.taskill.providers
- **Functions**: 2
- **File**: `__init__.py`

### src.taskill.config
- **Functions**: 1
- **Classes**: 4
- **File**: `config.py`

### src.taskill.updaters
- **Functions**: 1
- **File**: `__init__.py`

## Key Entry Points

Main execution flows into the system:

### src.taskill.cli.bulk_run_cmd
> Run taskill across all git repos under a directory.

Useful for fleet-wide hygiene: keep README/CHANGELOG/TODO in sync
across many self-hosted project
- **Calls**: main.command, click.option, click.option, click.option, click.option, click.option, click.option, click.option

### src.taskill.cli.run
> Execute the update pipeline.
- **Calls**: main.command, click.option, click.option, click.option, src.taskill.config.load_config, Taskill, tk.run, console.print

### src.taskill.providers.windsurf_mcp.WindsurfMcpProvider.generate
- **Calls**: src.taskill.providers.windsurf_mcp._candidate_endpoints, self.options.get, OpenRouterProvider._parse_json_loosely, GeneratedDocs, src.taskill.providers.windsurf_mcp._mcp_lib_present, ProviderError, ProviderError, ProviderError

### src.taskill.updaters.todo.TodoUpdater._update_todo
> Remove completed_lines from TODO and append new_items. Returns True on change.
- **Calls**: path.exists, original.splitlines, list, path.write_text, path.read_text, l.rstrip, l.strip, out_lines.append

### src.taskill.providers.openrouter.OpenRouterProvider.generate
- **Calls**: os.getenv, src.taskill.providers.openrouter._normalize_model, self.options.get, self.options.get, self._parse_json_loosely, GeneratedDocs, ProviderError, os.getenv

### src.taskill.cli.status
> Show what taskill would do without running it.
- **Calls**: main.command, click.option, src.taskill.config.load_config, Taskill, tk.status, Table, table.add_column, table.add_column

### src.taskill.providers.algorithmic.AlgorithmicProvider.generate
- **Calls**: defaultdict, self._find_completed_todos, self._extract_new_todos, len, GeneratedDocs, context.get, self._format_commit, entries.append

### src.taskill.core.Taskill.run
- **Calls**: self._snapshot, src.taskill.triggers.evaluate, src.taskill.providers.build_chain, self._build_context, TaskillResult, log.info, TaskillResult, TaskillResult

### src.taskill.updaters.changelog.ChangelogUpdater._update_changelog
> Append entries under [Unreleased]. Returns True if the file changed.
- **Calls**: path.exists, re.compile, pattern.search, m.group, set, path.write_text, path.read_text, original.startswith

### src.taskill.providers.algorithmic.AlgorithmicProvider._find_completed_todos
> Return TODO lines that look completed.

Two signals:
1. Line starts with `- [x]` or `* [x]`  → explicitly checked off.
2. Line content has high token 
- **Calls**: todo_text.splitlines, raw_line.rstrip, re.match, re.match, None.lower, set, line.strip, completed.append

### src.taskill.cli.init
> Generate a starter taskill.yaml + .env.example in the current directory.
- **Calls**: main.command, click.option, Path, Path, yml.write_text, console.print, console.print, console.print

### src.taskill.core.Taskill._apply
- **Calls**: src.taskill.updaters.changelog.update_changelog, src.taskill.updaters.todo.update_todo, src.taskill.updaters.readme.update_readme, changed.append, changed.append, changed.append, str, str

### src.taskill.updaters.readme.ReadmeUpdater._update_readme
- **Calls**: src.taskill.updaters.readme.render_status_block, path.read_text, path.write_text, path.exists, path.write_text, re.compile, pattern.sub, original.endswith

### src.taskill.providers.algorithmic.AlgorithmicProvider._extract_new_todos
- **Calls**: re.compile, set, pat.finditer, None.rstrip, seen.add, new.append, text.lower, text.lower

### src.taskill.core.Taskill._build_context
- **Calls**: self.config.reuse.get, _read, _read, _read, self._maybe_pyqual_report, self.config.files.get, p.exists, p.read_text

### src.taskill.cli.release
> Promote [Unreleased] section to a versioned [VERSION] heading.
- **Calls**: main.command, click.argument, click.option, Path, src.taskill.updaters.changelog.release_unreleased, console.print, console.print, sys.exit

### src.taskill.updaters.discover_updaters
> Discover all registered updaters via entry points.

Falls back to built-in registry if entry points are not available
(e.g., during development before
- **Calls**: registry.setdefault, registry.setdefault, registry.setdefault, importlib.metadata.entry_points, ep.load, isinstance, issubclass

### src.taskill.cli.main
> taskill — keep README/CHANGELOG/TODO honest.
- **Calls**: click.group, click.version_option, click.option, click.option, src.taskill.cli._setup_logging, ctx.ensure_object

### src.taskill.cli.clean_todo
> Reset TODO.md to an empty header. Use after a release.
- **Calls**: main.command, click.option, click.confirmation_option, src.taskill.updaters.todo.empty_todo, console.print, Path

### src.taskill.bulk.BulkResult.as_dict
- **Calls**: str, str, r.as_dict, str, str, self.per_repo.items

### src.taskill.providers.openrouter.OpenRouterProvider._parse_json_loosely
> Be forgiving: strip ```json fences, extract first {...} block.
- **Calls**: text.strip, re.sub, re.search, json.loads, json.loads, m.group

### src.taskill.updaters.todo.TodoUpdater.apply
> Apply todo updates from generated docs.
- **Calls**: docs.get, docs.get, self.options.get, self._update_todo, UpdateResult

### src.taskill.core.TaskillResult.as_dict
- **Calls**: len, len, len

### src.taskill.core.Taskill.status
> Inspect current trigger state without running anything.
- **Calls**: self._snapshot, src.taskill.triggers.evaluate, len

### src.taskill.core.Taskill._maybe_pyqual_report
> Run `pyqual report --json` if pyqual is on PATH. Tolerate failure.
- **Calls**: subprocess.run, res.stdout.strip, json.loads

### src.taskill.core.Taskill._update_state
- **Calls**: self.state.stamp, p.exists, p.stat

### src.taskill.updaters.readme.ReadmeUpdater.apply
> Apply readme updates from generated docs.
- **Calls**: docs.get, self._update_readme, UpdateResult

### src.taskill.updaters.changelog.ChangelogUpdater.apply
> Apply changelog updates from generated docs.
- **Calls**: docs.get, self._update_changelog, UpdateResult

### src.taskill.providers.windsurf_mcp.WindsurfMcpProvider.is_available
- **Calls**: bool, src.taskill.providers.windsurf_mcp._mcp_lib_present, src.taskill.providers.windsurf_mcp._candidate_endpoints

### src.taskill.state.TaskillState.stamp
- **Calls**: None.isoformat, datetime.now

## Process Flows

Key execution flows identified:

### Flow 1: bulk_run_cmd
```
bulk_run_cmd [src.taskill.cli]
```

### Flow 2: run
```
run [src.taskill.cli]
  └─ →> load_config
```

### Flow 3: generate
```
generate [src.taskill.providers.windsurf_mcp.WindsurfMcpProvider]
  └─ →> _candidate_endpoints
  └─ →> _mcp_lib_present
```

### Flow 4: _update_todo
```
_update_todo [src.taskill.updaters.todo.TodoUpdater]
```

### Flow 5: status
```
status [src.taskill.cli]
  └─ →> load_config
```

### Flow 6: _update_changelog
```
_update_changelog [src.taskill.updaters.changelog.ChangelogUpdater]
```

### Flow 7: _find_completed_todos
```
_find_completed_todos [src.taskill.providers.algorithmic.AlgorithmicProvider]
```

### Flow 8: init
```
init [src.taskill.cli]
```

### Flow 9: _apply
```
_apply [src.taskill.core.Taskill]
  └─ →> update_changelog
  └─ →> update_todo
  └─ →> update_readme
```

### Flow 10: _update_readme
```
_update_readme [src.taskill.updaters.readme.ReadmeUpdater]
  └─ →> render_status_block
```

## Key Classes

### src.taskill.core.Taskill
- **Methods**: 8
- **Key Methods**: src.taskill.core.Taskill.__init__, src.taskill.core.Taskill.run, src.taskill.core.Taskill.status, src.taskill.core.Taskill._snapshot, src.taskill.core.Taskill._build_context, src.taskill.core.Taskill._maybe_pyqual_report, src.taskill.core.Taskill._apply, src.taskill.core.Taskill._update_state

### src.taskill.bulk.BulkResult
> Aggregate result of running taskill across multiple repos.
- **Methods**: 5
- **Key Methods**: src.taskill.bulk.BulkResult.total_repos, src.taskill.bulk.BulkResult.ran_count, src.taskill.bulk.BulkResult.changed_count, src.taskill.bulk.BulkResult.as_dict, src.taskill.bulk.BulkResult.summary

### src.taskill.providers.algorithmic.AlgorithmicProvider
- **Methods**: 5
- **Key Methods**: src.taskill.providers.algorithmic.AlgorithmicProvider.is_available, src.taskill.providers.algorithmic.AlgorithmicProvider.generate, src.taskill.providers.algorithmic.AlgorithmicProvider._format_commit, src.taskill.providers.algorithmic.AlgorithmicProvider._find_completed_todos, src.taskill.providers.algorithmic.AlgorithmicProvider._extract_new_todos
- **Inherits**: Provider

### src.taskill.providers.base.Provider
> Abstract provider — produces docs from a project snapshot.
- **Methods**: 3
- **Key Methods**: src.taskill.providers.base.Provider.__init__, src.taskill.providers.base.Provider.is_available, src.taskill.providers.base.Provider.generate
- **Inherits**: ABC

### src.taskill.providers.openrouter.OpenRouterProvider
- **Methods**: 3
- **Key Methods**: src.taskill.providers.openrouter.OpenRouterProvider.is_available, src.taskill.providers.openrouter.OpenRouterProvider.generate, src.taskill.providers.openrouter.OpenRouterProvider._parse_json_loosely
- **Inherits**: Provider

### src.taskill.config.TaskillConfig
- **Methods**: 2
- **Key Methods**: src.taskill.config.TaskillConfig.env_model, src.taskill.config.TaskillConfig.env_api_key

### src.taskill.state.TaskillState
- **Methods**: 2
- **Key Methods**: src.taskill.state.TaskillState.last_run_dt, src.taskill.state.TaskillState.stamp

### src.taskill.git_state.Commit
- **Methods**: 2
- **Key Methods**: src.taskill.git_state.Commit.conventional_type, src.taskill.git_state.Commit.is_breaking

### src.taskill.updaters.readme.ReadmeUpdater
> Updater for README.md files.
- **Methods**: 2
- **Key Methods**: src.taskill.updaters.readme.ReadmeUpdater.apply, src.taskill.updaters.readme.ReadmeUpdater._update_readme
- **Inherits**: DocumentUpdater

### src.taskill.updaters.base.DocumentUpdater
> Abstract updater — applies changes to a document file.
- **Methods**: 2
- **Key Methods**: src.taskill.updaters.base.DocumentUpdater.__init__, src.taskill.updaters.base.DocumentUpdater.apply
- **Inherits**: ABC

### src.taskill.updaters.changelog.ChangelogUpdater
> Updater for CHANGELOG.md files.
- **Methods**: 2
- **Key Methods**: src.taskill.updaters.changelog.ChangelogUpdater.apply, src.taskill.updaters.changelog.ChangelogUpdater._update_changelog
- **Inherits**: DocumentUpdater

### src.taskill.updaters.todo.TodoUpdater
> Updater for TODO.md files.
- **Methods**: 2
- **Key Methods**: src.taskill.updaters.todo.TodoUpdater.apply, src.taskill.updaters.todo.TodoUpdater._update_todo
- **Inherits**: DocumentUpdater

### src.taskill.providers.windsurf_mcp.WindsurfMcpProvider
- **Methods**: 2
- **Key Methods**: src.taskill.providers.windsurf_mcp.WindsurfMcpProvider.is_available, src.taskill.providers.windsurf_mcp.WindsurfMcpProvider.generate
- **Inherits**: Provider

### src.taskill.triggers.TriggerEvaluation
- **Methods**: 1
- **Key Methods**: src.taskill.triggers.TriggerEvaluation.summary

### src.taskill.core.TaskillResult
- **Methods**: 1
- **Key Methods**: src.taskill.core.TaskillResult.as_dict

### src.taskill.providers.base.GeneratedDocs
> What every provider returns.
- **Methods**: 1
- **Key Methods**: src.taskill.providers.base.GeneratedDocs.__post_init__

### src.taskill.config.Triggers
> Conditions that must be met to run an update.

All thresholds are OR-ed by default (any one true → r
- **Methods**: 0

### src.taskill.config.ProviderConfig
> Single provider configuration.
- **Methods**: 0

### src.taskill.config.IntegrationConfig
> Optional CI / VCS / orchestrator integration.
- **Methods**: 0

### src.taskill.git_state.ProjectSnapshot
- **Methods**: 0

## Data Transformation Functions

Key functions that process and transform data:

### src.taskill.providers.openrouter.OpenRouterProvider._parse_json_loosely
> Be forgiving: strip ```json fences, extract first {...} block.
- **Output to**: text.strip, re.sub, re.search, json.loads, json.loads

### src.taskill.providers.algorithmic.AlgorithmicProvider._format_commit
- **Output to**: re.sub

### project.map.toon.test_bulk_run_summary_format

### project.map.toon.test_process_env_overrides_dotenv

## Behavioral Patterns

### recursion__scan
- **Type**: recursion
- **Confidence**: 0.90
- **Functions**: src.taskill.bulk._scan

### state_machine_TaskillState
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: src.taskill.state.TaskillState.last_run_dt, src.taskill.state.TaskillState.stamp

### state_machine_Commit
- **Type**: state_machine
- **Confidence**: 0.70
- **Functions**: src.taskill.git_state.Commit.conventional_type, src.taskill.git_state.Commit.is_breaking

## Public API Surface

Functions exposed as public API (no underscore prefix):

- `src.taskill.cli.bulk_run_cmd` - 38 calls
- `src.taskill.config.load_config` - 35 calls
- `src.taskill.cli.run` - 32 calls
- `src.taskill.providers.windsurf_mcp.WindsurfMcpProvider.generate` - 32 calls
- `src.taskill.providers.openrouter.OpenRouterProvider.generate` - 27 calls
- `src.taskill.bulk.bulk_run` - 26 calls
- `src.taskill.cli.status` - 25 calls
- `src.taskill.triggers.evaluate` - 23 calls
- `src.taskill.providers.algorithmic.AlgorithmicProvider.generate` - 21 calls
- `src.taskill.core.Taskill.run` - 20 calls
- `src.taskill.cli.init` - 13 calls
- `src.taskill.git_state.collect_snapshot` - 13 calls
- `src.taskill.git_state.read_coverage` - 11 calls
- `src.taskill.cli.release` - 8 calls
- `src.taskill.git_state.commits_since` - 8 calls
- `src.taskill.git_state.read_failed_tests` - 8 calls
- `src.taskill.updaters.discover_updaters` - 7 calls
- `src.taskill.providers.discover_providers` - 7 calls
- `src.taskill.state.load_state` - 6 calls
- `src.taskill.cli.main` - 6 calls
- `src.taskill.cli.clean_todo` - 6 calls
- `src.taskill.bulk.BulkResult.as_dict` - 6 calls
- `src.taskill.updaters.changelog.release_unreleased` - 6 calls
- `src.taskill.bulk.find_repos` - 5 calls
- `src.taskill.updaters.readme.render_status_block` - 5 calls
- `src.taskill.updaters.todo.TodoUpdater.apply` - 5 calls
- `src.taskill.providers.base.build_user_prompt` - 5 calls
- `src.taskill.state.save_state` - 4 calls
- `src.taskill.git_state.file_hash` - 4 calls
- `src.taskill.bulk.resolve_repo_config` - 4 calls
- `src.taskill.providers.build_chain` - 4 calls
- `src.taskill.core.TaskillResult.as_dict` - 3 calls
- `src.taskill.core.Taskill.status` - 3 calls
- `src.taskill.updaters.readme.ReadmeUpdater.apply` - 3 calls
- `src.taskill.updaters.changelog.ChangelogUpdater.apply` - 3 calls
- `src.taskill.providers.windsurf_mcp.WindsurfMcpProvider.is_available` - 3 calls
- `src.taskill.state.TaskillState.stamp` - 2 calls
- `src.taskill.git_state.changed_files_since` - 2 calls
- `src.taskill.bulk.BulkResult.summary` - 2 calls
- `src.taskill.updaters.readme.update_readme` - 2 calls

## System Interactions

How components interact:

```mermaid
graph TD
    bulk_run_cmd --> command
    bulk_run_cmd --> option
    run --> command
    run --> option
    run --> load_config
    generate --> _candidate_endpoints
    generate --> get
    generate --> _parse_json_loosely
    generate --> GeneratedDocs
    generate --> _mcp_lib_present
    _update_todo --> exists
    _update_todo --> splitlines
    _update_todo --> list
    _update_todo --> write_text
    _update_todo --> read_text
    generate --> getenv
    generate --> _normalize_model
    status --> command
    status --> option
    status --> load_config
    status --> Taskill
    status --> status
    generate --> defaultdict
    generate --> _find_completed_todo
    generate --> _extract_new_todos
    generate --> len
    run --> _snapshot
    run --> evaluate
    run --> build_chain
    run --> _build_context
```

## Reverse Engineering Guidelines

1. **Entry Points**: Start analysis from the entry points listed above
2. **Core Logic**: Focus on classes with many methods
3. **Data Flow**: Follow data transformation functions
4. **Process Flows**: Use the flow diagrams for execution paths
5. **API Surface**: Public API functions reveal the interface

## Context for LLM

Maintain the identified architectural patterns and public API surface when suggesting changes.