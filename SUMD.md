# taskill

Daily project hygiene: keep README / CHANGELOG / TODO in sync with reality. LLM-first, algorithmic fallback.

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Interfaces](#interfaces)
- [Configuration](#configuration)
- [Dependencies](#dependencies)
- [Deployment](#deployment)
- [Environment Variables (`.env.example`)](#environment-variables-envexample)
- [Release Management (`goal.yaml`)](#release-management-goalyaml)
- [Code Analysis](#code-analysis)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Intent](#intent)

## Metadata

- **name**: `taskill`
- **version**: `0.1.7`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, testql(1), app.doql.less, goal.yaml, .env.example, project/(2 analysis files)

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

### DOQL Application Declaration (`app.doql.less`)

```less markpact:doql path=app.doql.less
// LESS format — define @variables here as needed

app {
  name: taskill;
  version: 0.1.7;
}

dependencies {
  runtime: "pyyaml>=6.0, python-dotenv>=1.0, httpx>=0.27, click>=8.1, rich>=13.7, goal>=2.1.0, costs>=0.1.20, pfix>=0.1.60";
  dev: "pytest>=7.0, pytest-asyncio>=0.21, ruff>=0.1, mypy>=1.5, goal>=2.1.0, costs>=0.1.20, pfix>=0.1.60";
}

interface[type="cli"] {
  framework: click;
}
interface[type="cli"] page[name="taskill"] {

}

integration[name="github"] {
  type: scm;
}

deploy {
  target: pip;
}

environment[name="local"] {
  runtime: python;
  env_file: .env;
  python_version: >=3.10;
}
```

## Interfaces

### CLI Entry Points

- `taskill`

### testql Scenarios

#### `testql-scenarios/generated-cli-tests.testql.toon.yaml`

```toon markpact:testql path=testql-scenarios/generated-cli-tests.testql.toon.yaml
# SCENARIO: CLI Command Tests
# TYPE: cli
# GENERATED: true

CONFIG[2]{key, value}:
  cli_command, python -mtaskill
  timeout_ms, 10000

LOG[3]{message}:
  "Test CLI help command"
  "Test CLI version command"
  "Test CLI main workflow"
```

## Configuration

```yaml
project:
  name: taskill
  version: 0.1.7
  env: local
```

## Dependencies

### Runtime

```text markpact:deps python
pyyaml>=6.0
python-dotenv>=1.0
httpx>=0.27
click>=8.1
rich>=13.7
goal>=2.1.0
costs>=0.1.20
pfix>=0.1.60
```

### Development

```text markpact:deps python scope=dev
pytest>=7.0
pytest-asyncio>=0.21
ruff>=0.1
mypy>=1.5
goal>=2.1.0
costs>=0.1.20
pfix>=0.1.60
```

## Deployment

```bash markpact:run
pip install taskill

# development install
pip install -e .[dev]
```

## Environment Variables (`.env.example`)

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENROUTER_API_KEY` | `*(not set)*` |  |
| `LLM_MODEL` | `openrouter/qwen/qwen3-coder-next` | (taskill auto-strips the openrouter/ prefix for the OpenRouter REST API) |
| `GITHUB_ROOT` | `$HOME/github` | Root directory for bulk-run (default: $HOME/github) |
| `TASKILL_MAX_DEPTH` | `2` | Max directory depth to scan for repos |
| `TASKILL_MAX_PROJECTS` | `0` | Max number of projects to process (0 = unlimited) |
| `TASKILL_DRY_RUN` | `false` | Preview changes without writing |
| `TASKILL_FORCE` | `false` | Override triggers |
| `TASKILL_FILTER` | `*(not set)*` | Comma-separated repo names to filter |

## Release Management (`goal.yaml`)

- **versioning**: `semver`
- **commits**: `conventional` scope=`taskill`
- **changelog**: `keep-a-changelog`
- **build strategies**: `python`, `nodejs`, `rust`
- **version files**: `VERSION`, `pyproject.toml:version`, `venv/lib/python3.13/site-packages/matplotlib/__init__.py:__version__`

## Code Analysis

### `project/map.toon.yaml`

```toon markpact:analysis path=project/map.toon.yaml
# taskill | 29f 3366L | python:25,shell:3,less:1 | 2026-04-25
# stats: 115 func | 22 cls | 29 mod | CC̄=3.6 | critical:4 | cycles:0
# alerts[5]: CC _print_bulk_table=13; CC _apply_filters=12; CC _print_run_result=12; CC status=11; CC _scan=9
# hotspots[5]: bulk_run fan=13; status fan=12; load_config fan=12; run fan=10; bulk_run_cmd fan=10
# evolution: baseline
# Keys: M=modules, D=details, i=imports, e=exports, c=classes, f=functions, m=methods
M[29]:
  app.doql.less,33
  daily_update.sh,94
  project.sh,47
  src/taskill/__init__.py,31
  src/taskill/bulk.py,262
  src/taskill/cli.py,362
  src/taskill/config.py,171
  src/taskill/core.py,211
  src/taskill/git_state.py,148
  src/taskill/providers/__init__.py,76
  src/taskill/providers/algorithmic.py,156
  src/taskill/providers/base.py,127
  src/taskill/providers/openrouter.py,97
  src/taskill/providers/windsurf_mcp.py,134
  src/taskill/state.py,43
  src/taskill/triggers.py,136
  src/taskill/updaters/__init__.py,55
  src/taskill/updaters/base.py,46
  src/taskill/updaters/changelog.py,120
  src/taskill/updaters/readme.py,99
  src/taskill/updaters/todo.py,132
  tests/__init__.py,1
  tests/test_algorithmic.py,94
  tests/test_bulk.py,280
  tests/test_config.py,61
  tests/test_providers.py,77
  tests/test_triggers.py,119
  tests/test_updaters.py,152
  tree.sh,2
D:
  src/taskill/__init__.py:
  src/taskill/bulk.py:
    e: find_repos,_scan,resolve_repo_config,_rebase_config,_load_shared_config,_apply_filters,_run_single_repo,bulk_run,BulkResult
    BulkResult: total_repos(0),ran_count(0),changed_count(0),as_dict(0),summary(0)  # Aggregate result of running taskill across multiple repos.
    find_repos(root;max_depth)
    _scan(directory;repos;depth;max_depth)
    resolve_repo_config(repo;shared_config)
    _rebase_config(base;new_root)
    _load_shared_config(shared_config)
    _apply_filters(repos;repo_filter;max_projects)
    _run_single_repo(repo;shared_cfg;force;dry_run)
    bulk_run(root;shared_config)
  src/taskill/cli.py:
    e: _setup_logging,main,_print_run_result,run,status,init,release,_print_bulk_table,bulk_run_cmd,clean_todo
    _setup_logging(verbose)
    main(ctx;verbose;config)
    _print_run_result(result)
    run(ctx;force;dry_run;as_json)
    status(ctx;as_json)
    init(force)
    release(version;changelog)
    _print_bulk_table(result)
    bulk_run_cmd(root;shared_config;max_depth;max_projects;force;dry_run;as_json;repo_filter)
    clean_todo(todo)
  src/taskill/config.py:
    e: load_config,Triggers,ProviderConfig,IntegrationConfig,TaskillConfig
    Triggers:  # Conditions that must be met to run an update.
    ProviderConfig:  # Single provider configuration.
    IntegrationConfig:  # Optional CI / VCS / orchestrator integration.
    TaskillConfig: env_model(0),env_api_key(0)
    load_config(path;project_root)
  src/taskill/core.py:
    e: TaskillResult,Taskill
    TaskillResult: as_dict(0)
    Taskill: __init__(2),run(1),status(0),_snapshot(0),_build_context(1),_maybe_pyqual_report(0),_apply(2),_update_state(1)
  src/taskill/git_state.py:
    e: _run,head_sha,commits_since,changed_files_since,read_coverage,read_failed_tests,file_hash,collect_snapshot,Commit,ProjectSnapshot
    Commit: conventional_type(0),is_breaking(0)
    ProjectSnapshot:
    _run(cmd;cwd)
    head_sha(project_root)
    commits_since(project_root;since_sha)
    changed_files_since(project_root;since_sha)
    read_coverage(project_root)
    read_failed_tests(project_root)
    file_hash(path)
    collect_snapshot(project_root;files;last_commit_sha)
  src/taskill/providers/__init__.py:
    e: discover_providers,build_chain
    discover_providers()
    build_chain(provider_configs)
  src/taskill/providers/algorithmic.py:
    e: AlgorithmicProvider
    AlgorithmicProvider: is_available(0),generate(1),_format_commit(1),_find_completed_todos(2),_extract_new_todos(1)
  src/taskill/providers/base.py:
    e: build_user_prompt,parse_json_loosely,ProviderError,GeneratedDocs,Provider
    ProviderError:  # Provider failed — chain falls through to next provider.
    GeneratedDocs: __post_init__(0)  # What every provider returns.
    Provider: __init__(1),is_available(0),generate(1)  # Abstract provider — produces docs from a project snapshot.
    build_user_prompt(context)
    parse_json_loosely(text)
  src/taskill/providers/openrouter.py:
    e: _normalize_model,OpenRouterProvider
    OpenRouterProvider: is_available(0),generate(1)
    _normalize_model(model)
  src/taskill/providers/windsurf_mcp.py:
    e: _mcp_lib_present,_candidate_endpoints,WindsurfMcpProvider
    WindsurfMcpProvider: is_available(0),generate(1)
    _mcp_lib_present()
    _candidate_endpoints(options)
  src/taskill/state.py:
    e: load_state,save_state,TaskillState
    TaskillState: last_run_dt(0),stamp(0)
    load_state(path)
    save_state(path;state)
  src/taskill/triggers.py:
    e: _check_time,_check_commits,_check_changed_files,_check_coverage,_check_failed_tests,_check_sumd,_check_watched_files,evaluate,TriggerEvaluation
    TriggerEvaluation: summary(0)
    _check_time(state;triggers;reasons;skipped)
    _check_commits(snapshot;triggers;reasons;skipped)
    _check_changed_files(snapshot;triggers;reasons;skipped)
    _check_coverage(snapshot;state;triggers;reasons;skipped)
    _check_failed_tests(snapshot;state;triggers;reasons)
    _check_sumd(snapshot;state;reasons)
    _check_watched_files(triggers;state;project_root;reasons)
    evaluate(triggers;state;snapshot;project_root)
  src/taskill/updaters/__init__.py:
    e: discover_updaters
    discover_updaters()
  src/taskill/updaters/base.py:
    e: UpdateResult,DocumentUpdater
    UpdateResult:  # What every updater returns.
    DocumentUpdater: __init__(1),apply(3)  # Abstract updater — applies changes to a document file.
  src/taskill/updaters/changelog.py:
    e: update_changelog,release_unreleased,ChangelogUpdater
    ChangelogUpdater: apply(3),_update_changelog(2)  # Updater for CHANGELOG.md files.
    update_changelog(path;entries)
    release_unreleased(path;version;today)
  src/taskill/updaters/readme.py:
    e: render_status_block,update_readme,ReadmeUpdater
    ReadmeUpdater: apply(3),_update_readme(3)  # Updater for README.md files.
    render_status_block(snapshot;summary)
    update_readme(path;snapshot;summary)
  src/taskill/updaters/todo.py:
    e: update_todo,empty_todo,TodoUpdater
    TodoUpdater: apply(3),_partition_lines(2),_dedup_new_items(2),_assemble_output(3),_update_todo(3)  # Updater for TODO.md files.
    update_todo(path;completed_lines;new_items)
    empty_todo(path;header)
  tests/__init__.py:
  tests/test_algorithmic.py:
    e: _commit,_snap,test_groups_commits_by_conventional_type,test_breaking_change_surfaces_first,test_detects_explicit_checkbox_completion,test_detects_completion_via_token_overlap,test_extracts_new_todos_from_commit_bodies,test_empty_input_is_safe,test_always_available
    _commit(subject;body)
    _snap(commits)
    test_groups_commits_by_conventional_type()
    test_breaking_change_surfaces_first()
    test_detects_explicit_checkbox_completion()
    test_detects_completion_via_token_overlap()
    test_extracts_new_todos_from_commit_bodies()
    test_empty_input_is_safe()
    test_always_available()
  tests/test_bulk.py:
    e: _make_repo,test_find_repos_finds_direct_children,test_find_repos_respects_max_depth,test_find_repos_skips_hidden_and_noise_dirs,test_find_repos_does_not_descend_into_repos,test_find_repos_returns_empty_for_nonexistent,test_resolve_repo_config_uses_local_yaml,test_resolve_repo_config_uses_dot_taskill_yaml,test_resolve_repo_config_falls_back_to_shared,test_resolve_repo_config_falls_back_to_defaults,test_resolve_repo_config_local_wins_over_shared,test_bulk_run_no_repos,test_bulk_run_executes_each_repo,test_bulk_run_repo_filter,test_bulk_run_with_shared_config,test_bulk_run_max_projects_limits_count,test_bulk_run_max_projects_zero_means_unlimited,test_bulk_run_filters_before_max_projects,test_bulk_run_summary_format,test_bulk_result_as_dict
    _make_repo(path)
    test_find_repos_finds_direct_children(tmp_path)
    test_find_repos_respects_max_depth(tmp_path)
    test_find_repos_skips_hidden_and_noise_dirs(tmp_path)
    test_find_repos_does_not_descend_into_repos(tmp_path)
    test_find_repos_returns_empty_for_nonexistent(tmp_path)
    test_resolve_repo_config_uses_local_yaml(tmp_path)
    test_resolve_repo_config_uses_dot_taskill_yaml(tmp_path)
    test_resolve_repo_config_falls_back_to_shared(tmp_path)
    test_resolve_repo_config_falls_back_to_defaults(tmp_path)
    test_resolve_repo_config_local_wins_over_shared(tmp_path)
    test_bulk_run_no_repos(tmp_path)
    test_bulk_run_executes_each_repo(tmp_path)
    test_bulk_run_repo_filter(tmp_path)
    test_bulk_run_with_shared_config(tmp_path)
    test_bulk_run_max_projects_limits_count(tmp_path)
    test_bulk_run_max_projects_zero_means_unlimited(tmp_path)
    test_bulk_run_filters_before_max_projects(tmp_path)
    test_bulk_run_summary_format(tmp_path)
    test_bulk_result_as_dict(tmp_path)
  tests/test_config.py:
    e: test_missing_yaml_returns_defaults,test_yaml_overrides_defaults,test_dotenv_loaded_from_project_root,test_process_env_overrides_dotenv,test_files_config_merges_with_defaults
    test_missing_yaml_returns_defaults(tmp_path)
    test_yaml_overrides_defaults(tmp_path)
    test_dotenv_loaded_from_project_root(tmp_path;monkeypatch)
    test_process_env_overrides_dotenv(tmp_path;monkeypatch)
    test_files_config_merges_with_defaults(tmp_path)
  tests/test_providers.py:
    e: test_discover_providers_returns_builtins,test_build_chain_with_enabled_providers,test_build_chain_with_unknown_provider,test_build_chain_preserves_order,test_build_chain_empty_config,test_build_chain_all_disabled
    test_discover_providers_returns_builtins()
    test_build_chain_with_enabled_providers()
    test_build_chain_with_unknown_provider()
    test_build_chain_preserves_order()
    test_build_chain_empty_config()
    test_build_chain_all_disabled()
  tests/test_triggers.py:
    e: _snap,_commit,test_first_run_always_triggers,test_recent_run_skips_when_no_commits,test_commits_above_threshold_triggers,test_coverage_delta_triggers,test_coverage_within_threshold_does_not_trigger,test_sumd_change_triggers,test_require_all_with_partial_match_does_not_trigger,test_watched_file_mtime_triggers
    _snap()
    _commit(subject)
    test_first_run_always_triggers(tmp_path)
    test_recent_run_skips_when_no_commits(tmp_path)
    test_commits_above_threshold_triggers(tmp_path)
    test_coverage_delta_triggers(tmp_path)
    test_coverage_within_threshold_does_not_trigger(tmp_path)
    test_sumd_change_triggers(tmp_path)
    test_require_all_with_partial_match_does_not_trigger(tmp_path)
    test_watched_file_mtime_triggers(tmp_path)
  tests/test_updaters.py:
    e: test_changelog_creates_file_with_entries,test_changelog_appends_to_unreleased,test_changelog_dedupes_existing_entries,test_changelog_empty_entries_no_op,test_release_promotes_unreleased,test_todo_archives_completed,test_todo_appends_new_under_discovered,test_todo_dedupes_new_items,test_todo_no_change_no_write,test_empty_todo_resets,_snap,test_readme_inserts_status_when_no_markers,test_readme_replaces_only_marker_block,test_readme_creates_file_when_missing
    test_changelog_creates_file_with_entries(tmp_path)
    test_changelog_appends_to_unreleased(tmp_path)
    test_changelog_dedupes_existing_entries(tmp_path)
    test_changelog_empty_entries_no_op(tmp_path)
    test_release_promotes_unreleased(tmp_path)
    test_todo_archives_completed(tmp_path)
    test_todo_appends_new_under_discovered(tmp_path)
    test_todo_dedupes_new_items(tmp_path)
    test_todo_no_change_no_write(tmp_path)
    test_empty_todo_resets(tmp_path)
    _snap()
    test_readme_inserts_status_when_no_markers(tmp_path)
    test_readme_replaces_only_marker_block(tmp_path)
    test_readme_creates_file_when_missing(tmp_path)
```

## Call Graph

*55 nodes · 50 edges · 14 modules · CC̄=1.8*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `load_config` *(in src.taskill.config)* | 8 | 6 | 35 | **41** |
| `generate` *(in src.taskill.providers.windsurf_mcp.WindsurfMcpProvider)* | 7 | 0 | 32 | **32** |
| `generate` *(in src.taskill.providers.openrouter.OpenRouterProvider)* | 6 | 0 | 27 | **27** |
| `status` *(in src.taskill.cli)* | 11 ⚠ | 0 | 25 | **25** |
| `_print_run_result` *(in src.taskill.cli)* | 12 ⚠ | 1 | 20 | **21** |
| `bulk_run_cmd` *(in src.taskill.cli)* | 5 | 0 | 20 | **20** |
| `run` *(in src.taskill.core.Taskill)* | 11 ⚠ | 0 | 20 | **20** |
| `bulk_run` *(in src.taskill.bulk)* | 3 | 1 | 14 | **15** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/semcod/taskill
# nodes: 55 | edges: 50 | modules: 14
# CC̄=1.8

HUBS[20]:
  src.taskill.config.load_config
    CC=8  in:6  out:35  total:41
  src.taskill.providers.windsurf_mcp.WindsurfMcpProvider.generate
    CC=7  in:0  out:32  total:32
  src.taskill.providers.openrouter.OpenRouterProvider.generate
    CC=6  in:0  out:27  total:27
  src.taskill.cli.status
    CC=11  in:0  out:25  total:25
  src.taskill.cli._print_run_result
    CC=12  in:1  out:20  total:21
  src.taskill.cli.bulk_run_cmd
    CC=5  in:0  out:20  total:20
  src.taskill.core.Taskill.run
    CC=11  in:0  out:20  total:20
  src.taskill.bulk.bulk_run
    CC=3  in:1  out:14  total:15
  src.taskill.git_state.collect_snapshot
    CC=3  in:1  out:13  total:14
  src.taskill.cli.run
    CC=6  in:0  out:13  total:13
  src.taskill.git_state.read_coverage
    CC=7  in:1  out:11  total:12
  src.taskill.triggers.evaluate
    CC=3  in:2  out:10  total:12
  src.taskill.core.Taskill._apply
    CC=4  in:0  out:12  total:12
  src.taskill.updaters.readme.ReadmeUpdater._update_readme
    CC=5  in:0  out:10  total:10
  src.taskill.bulk._apply_filters
    CC=12  in:1  out:8  total:9
  src.taskill.git_state.commits_since
    CC=7  in:1  out:8  total:9
  src.taskill.providers.windsurf_mcp._candidate_endpoints
    CC=5  in:2  out:7  total:9
  src.taskill.bulk._scan
    CC=9  in:2  out:7  total:9
  src.taskill.git_state.read_failed_tests
    CC=5  in:1  out:8  total:9
  src.taskill.providers.base.parse_json_loosely
    CC=4  in:2  out:6  total:8

MODULES:
  src.taskill.bulk  [8 funcs]
    _apply_filters  CC=12  out:8
    _load_shared_config  CC=4  out:5
    _rebase_config  CC=1  out:3
    _run_single_repo  CC=2  out:3
    _scan  CC=9  out:7
    bulk_run  CC=3  out:14
    find_repos  CC=2  out:5
    resolve_repo_config  CC=4  out:4
  src.taskill.cli  [8 funcs]
    _print_run_result  CC=12  out:20
    _setup_logging  CC=2  out:1
    bulk_run_cmd  CC=5  out:20
    clean_todo  CC=1  out:6
    main  CC=1  out:6
    release  CC=2  out:8
    run  CC=6  out:13
    status  CC=11  out:25
  src.taskill.config  [1 funcs]
    load_config  CC=8  out:35
  src.taskill.core  [5 funcs]
    __init__  CC=2  out:2
    _apply  CC=4  out:12
    _snapshot  CC=1  out:1
    run  CC=11  out:20
    status  CC=1  out:3
  src.taskill.git_state  [8 funcs]
    _run  CC=2  out:2
    changed_files_since  CC=4  out:2
    collect_snapshot  CC=3  out:13
    commits_since  CC=7  out:8
    file_hash  CC=2  out:4
    head_sha  CC=2  out:1
    read_coverage  CC=7  out:11
    read_failed_tests  CC=5  out:8
  src.taskill.providers  [2 funcs]
    build_chain  CC=4  out:4
    discover_providers  CC=6  out:7
  src.taskill.providers.base  [1 funcs]
    parse_json_loosely  CC=4  out:6
  src.taskill.providers.openrouter  [2 funcs]
    generate  CC=6  out:27
    _normalize_model  CC=2  out:2
  src.taskill.providers.windsurf_mcp  [4 funcs]
    generate  CC=7  out:32
    is_available  CC=2  out:3
    _candidate_endpoints  CC=5  out:7
    _mcp_lib_present  CC=2  out:0
  src.taskill.state  [1 funcs]
    load_state  CC=3  out:6
  src.taskill.triggers  [8 funcs]
    _check_changed_files  CC=2  out:3
    _check_commits  CC=2  out:3
    _check_coverage  CC=5  out:3
    _check_failed_tests  CC=5  out:1
    _check_sumd  CC=3  out:1
    _check_time  CC=3  out:5
    _check_watched_files  CC=5  out:4
    evaluate  CC=3  out:10
  src.taskill.updaters.changelog  [2 funcs]
    release_unreleased  CC=4  out:6
    update_changelog  CC=1  out:2
  src.taskill.updaters.readme  [3 funcs]
    _update_readme  CC=5  out:10
    render_status_block  CC=6  out:5
    update_readme  CC=1  out:2
  src.taskill.updaters.todo  [2 funcs]
    empty_todo  CC=1  out:1
    update_todo  CC=1  out:2

EDGES:
  src.taskill.cli.main → src.taskill.cli._setup_logging
  src.taskill.cli.run → src.taskill.config.load_config
  src.taskill.cli.run → src.taskill.cli._print_run_result
  src.taskill.cli.status → src.taskill.config.load_config
  src.taskill.cli.release → src.taskill.updaters.changelog.release_unreleased
  src.taskill.cli.bulk_run_cmd → src.taskill.bulk.bulk_run
  src.taskill.cli.clean_todo → src.taskill.updaters.todo.empty_todo
  src.taskill.git_state.head_sha → src.taskill.git_state._run
  src.taskill.git_state.commits_since → src.taskill.git_state._run
  src.taskill.git_state.changed_files_since → src.taskill.git_state._run
  src.taskill.git_state.collect_snapshot → src.taskill.git_state.head_sha
  src.taskill.git_state.collect_snapshot → src.taskill.git_state.commits_since
  src.taskill.git_state.collect_snapshot → src.taskill.git_state.changed_files_since
  src.taskill.git_state.collect_snapshot → src.taskill.git_state.read_coverage
  src.taskill.git_state.collect_snapshot → src.taskill.git_state.read_failed_tests
  src.taskill.git_state.collect_snapshot → src.taskill.git_state.file_hash
  src.taskill.triggers.evaluate → src.taskill.triggers._check_time
  src.taskill.triggers.evaluate → src.taskill.triggers._check_commits
  src.taskill.triggers.evaluate → src.taskill.triggers._check_changed_files
  src.taskill.triggers.evaluate → src.taskill.triggers._check_coverage
  src.taskill.triggers.evaluate → src.taskill.triggers._check_failed_tests
  src.taskill.triggers.evaluate → src.taskill.triggers._check_sumd
  src.taskill.triggers.evaluate → src.taskill.triggers._check_watched_files
  src.taskill.core.Taskill.__init__ → src.taskill.state.load_state
  src.taskill.core.Taskill.__init__ → src.taskill.config.load_config
  src.taskill.core.Taskill.run → src.taskill.triggers.evaluate
  src.taskill.core.Taskill.run → src.taskill.providers.build_chain
  src.taskill.core.Taskill.status → src.taskill.triggers.evaluate
  src.taskill.core.Taskill._snapshot → src.taskill.git_state.collect_snapshot
  src.taskill.core.Taskill._apply → src.taskill.updaters.changelog.update_changelog
  src.taskill.core.Taskill._apply → src.taskill.updaters.todo.update_todo
  src.taskill.core.Taskill._apply → src.taskill.updaters.readme.update_readme
  src.taskill.bulk.find_repos → src.taskill.bulk._scan
  src.taskill.bulk.resolve_repo_config → src.taskill.config.load_config
  src.taskill.bulk.resolve_repo_config → src.taskill.bulk._rebase_config
  src.taskill.bulk._load_shared_config → src.taskill.config.load_config
  src.taskill.bulk._run_single_repo → src.taskill.bulk.resolve_repo_config
  src.taskill.bulk.bulk_run → src.taskill.bulk._load_shared_config
  src.taskill.bulk.bulk_run → src.taskill.bulk.find_repos
  src.taskill.bulk.bulk_run → src.taskill.bulk._apply_filters
  src.taskill.bulk.bulk_run → src.taskill.bulk._run_single_repo
  src.taskill.updaters.readme.ReadmeUpdater._update_readme → src.taskill.updaters.readme.render_status_block
  src.taskill.providers.windsurf_mcp.WindsurfMcpProvider.is_available → src.taskill.providers.windsurf_mcp._mcp_lib_present
  src.taskill.providers.windsurf_mcp.WindsurfMcpProvider.is_available → src.taskill.providers.windsurf_mcp._candidate_endpoints
  src.taskill.providers.windsurf_mcp.WindsurfMcpProvider.generate → src.taskill.providers.windsurf_mcp._candidate_endpoints
  src.taskill.providers.windsurf_mcp.WindsurfMcpProvider.generate → src.taskill.providers.base.parse_json_loosely
  src.taskill.providers.windsurf_mcp.WindsurfMcpProvider.generate → src.taskill.providers.windsurf_mcp._mcp_lib_present
  src.taskill.providers.openrouter.OpenRouterProvider.generate → src.taskill.providers.openrouter._normalize_model
  src.taskill.providers.openrouter.OpenRouterProvider.generate → src.taskill.providers.base.parse_json_loosely
  src.taskill.providers.build_chain → src.taskill.providers.discover_providers
```

## Test Contracts

*Scenarios as contract signatures — what the system guarantees.*

### Cli (1)

**`CLI Command Tests`**

## Intent

Daily project hygiene: keep README / CHANGELOG / TODO in sync with reality. LLM-first, algorithmic fallback.
