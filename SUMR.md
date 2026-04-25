# taskill

SUMD - Structured Unified Markdown Descriptor for AI-aware project refactorization

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Dependencies](#dependencies)
- [Call Graph](#call-graph)
- [Test Contracts](#test-contracts)
- [Refactoring Analysis](#refactoring-analysis)
- [Intent](#intent)

## Metadata

- **name**: `taskill`
- **version**: `0.1.7`
- **python_requires**: `>=3.10`
- **license**: Apache-2.0
- **ai_model**: `openrouter/qwen/qwen3-coder-next`
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, testql(1), app.doql.less, goal.yaml, .env.example, project/(5 analysis files)

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

## Refactoring Analysis

*Pre-refactoring snapshot — use this section to identify targets. Generated from `project/` toon files.*

### Call Graph & Complexity (`project/calls.toon.yaml`)

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

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 38f 5571L | python:18,yaml:12,yml:3,txt:2,shell:2,toml:1 | 2026-04-25
# CC̄=1.8 | critical:0/200 | dups:0 | cycles:1

HEALTH[0]: ok

REFACTOR[1]:
  1. break 1 circular dependencies

PIPELINES[38]:
  [1] Src [stamp]: stamp
      PURITY: 100% pure
  [2] Src [main]: main → _setup_logging
      PURITY: 100% pure
  [3] Src [run]: run → load_config
      PURITY: 100% pure
  [4] Src [status]: status → load_config
      PURITY: 100% pure
  [5] Src [init]: init
      PURITY: 100% pure

LAYERS:
  src/                            CC̄=4.1    ←in:0  →out:0
  │ cli                        361L  0C   10m  CC=13     ←0
  │ bulk                       261L  1C   10m  CC=12     ←1
  │ core                       210L  2C    9m  CC=11     ←0
  │ config                     170L  4C    1m  CC=8      ←3
  │ algorithmic                155L  1C    5m  CC=10     ←0
  │ git_state                  147L  2C    8m  CC=7      ←2
  │ triggers                   135L  1C    9m  CC=5      ←1
  │ windsurf_mcp               133L  1C    4m  CC=7      ←0
  │ todo                       131L  1C    7m  CC=8      ←2
  │ base                       126L  3C    6m  CC=9      ←2
  │ changelog                  119L  1C    4m  CC=12     ←2
  │ readme                      98L  1C    4m  CC=6      ←1
  │ openrouter                  96L  1C    3m  CC=6      ←0
  │ __init__                    75L  0C    2m  CC=6      ←1
  │ __init__                    54L  0C    1m  CC=6      ←0
  │ base                        45L  2C    2m  CC=2      ←0
  │ state                       42L  1C    3m  CC=3      ←1
  │ __init__                    30L  0C    0m  CC=0.0    ←0
  │
  project/                        CC̄=0.0    ←in:0  →out:0
  │ !! calls.yaml                 779L  0C    0m  CC=0.0    ←0
  │ map.toon.yaml              222L  0C  112m  CC=0.0    ←0
  │ calls.toon.yaml            169L  0C    0m  CC=0.0    ←0
  │ analysis.toon.yaml          81L  0C    0m  CC=0.0    ←0
  │ project.toon.yaml           56L  0C    0m  CC=0.0    ←0
  │ prompt.txt                  47L  0C    0m  CC=0.0    ←0
  │ evolution.toon.yaml         39L  0C    0m  CC=0.0    ←0
  │ duplication.toon.yaml       34L  0C    0m  CC=0.0    ←0
  │
  ./                              CC̄=0.0    ←in:0  →out:0
  │ !! planfile.yaml              617L  0C    0m  CC=0.0    ←0
  │ !! goal.yaml                  513L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              97L  0C    0m  CC=0.0    ←0
  │ daily_update.sh             93L  0C    0m  CC=0.0    ←0
  │ prefact.yaml                91L  0C    0m  CC=0.0    ←0
  │ tree.txt                    80L  0C    0m  CC=0.0    ←0
  │ taskill.yaml                57L  0C    0m  CC=0.0    ←0
  │ project.sh                  47L  0C    0m  CC=0.0    ←0
  │
  examples/                       CC̄=0.0    ←in:0  →out:0
  │ ansible-playbook.yml        52L  0C    0m  CC=0.0    ←0
  │ github-action.yml           51L  0C    0m  CC=0.0    ←0
  │ gitlab-ci.yml               46L  0C    0m  CC=0.0    ←0
  │
  testql-scenarios/               CC̄=0.0    ←in:0  →out:0
  │ generated-cli-tests.testql.toon.yaml    12L  0C    0m  CC=0.0    ←0
  │

COUPLING: no cross-package imports detected

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 1 groups | 18f 2388L | 2026-04-25

SUMMARY:
  files_scanned: 18
  total_lines:   2388
  dup_groups:    1
  dup_fragments: 2
  saved_lines:   29
  scan_ms:       4306

HOTSPOTS[2] (files with most duplication):
  src/taskill/providers/__init__.py  dup=29L  groups=1  frags=1  (1.2%)
  src/taskill/updaters/__init__.py  dup=29L  groups=1  frags=1  (1.2%)

DUPLICATES[1] (ranked by impact):
  [e7fb8feab50f19ae]   STRU  discover_providers  L=29 N=2 saved=29 sim=1.00
      src/taskill/providers/__init__.py:33-61  (discover_providers)
      src/taskill/updaters/__init__.py:26-54  (discover_updaters)

REFACTOR[1] (ranked by priority):
  [1] ○ extract_function   → src/taskill/utils/discover_providers.py
      WHY: 2 occurrences of 29-line block across 2 files — saves 29 lines
      FILES: src/taskill/providers/__init__.py, src/taskill/updaters/__init__.py

QUICK_WINS[1] (low risk, high savings — do first):
  [1] extract_function   saved=29L  → src/taskill/utils/discover_providers.py
      FILES: __init__.py, __init__.py

EFFORT_ESTIMATE (total ≈ 1.0h):
  medium discover_providers                  saved=29L  ~58min

METRICS-TARGET:
  dup_groups:  1 → 0
  saved_lines: 29 lines recoverable
```

### Evolution / Churn (`project/evolution.toon.yaml`)

```toon markpact:analysis path=project/evolution.toon.yaml
# code2llm/evolution | 200 func | 18f | 2026-04-25

NEXT[0]: no refactoring needed

RISKS[0]: none

METRICS-TARGET:
  CC̄:          1.8 → ≤1.3
  max-CC:      13 → ≤6
  god-modules: 0 → 0
  high-CC(≥15): 0 → ≤0
  hub-types:   0 → ≤0

PATTERNS (language parser shared logic):
  _extract_declarations() in base.py — unified extraction for:
    - TypeScript: interfaces, types, classes, functions, arrow funcs
    - PHP: namespaces, traits, classes, functions, includes
    - Ruby: modules, classes, methods, requires
    - C++: classes, structs, functions, #includes
    - C#: classes, interfaces, methods, usings
    - Java: classes, interfaces, methods, imports
    - Go: packages, functions, structs
    - Rust: modules, functions, traits, use statements

  Shared regex patterns per language:
    - import: language-specific import/require/using patterns
    - class: class/struct/trait declarations with inheritance
    - function: function/method signatures with visibility
    - brace_tracking: for C-family languages ({ })
    - end_keyword_tracking: for Ruby (module/class/def...end)

  Benefits:
    - Consistent extraction logic across all languages
    - Reduced code duplication (~70% reduction in parser LOC)
    - Easier maintenance: fix once, apply everywhere
    - Standardized FunctionInfo/ClassInfo models

HISTORY:
  prev CC̄=1.8 → now CC̄=1.8
```

## Intent

Daily project hygiene: keep README / CHANGELOG / TODO in sync with reality. LLM-first, algorithmic fallback.
