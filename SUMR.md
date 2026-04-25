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
- **version**: `0.1.1`
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
  version: 0.1.1;
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

*34 nodes · 28 edges · 12 modules · CC̄=4.3*

### Hubs (by degree)

| Function | CC | in | out | total |
|----------|----|----|-----|-------|
| `load_config` *(in src.taskill.config)* | 8 | 3 | 35 | **38** |
| `run` *(in src.taskill.cli)* | 16 ⚠ | 0 | 32 | **32** |
| `generate` *(in src.taskill.providers.windsurf_mcp.WindsurfMcpProvider)* | 7 | 0 | 32 | **32** |
| `generate` *(in src.taskill.providers.openrouter.OpenRouterProvider)* | 6 | 0 | 27 | **27** |
| `evaluate` *(in src.taskill.triggers)* | 21 ⚠ | 2 | 23 | **25** |
| `status` *(in src.taskill.cli)* | 11 ⚠ | 0 | 25 | **25** |
| `run` *(in src.taskill.core.Taskill)* | 11 ⚠ | 0 | 20 | **20** |
| `collect_snapshot` *(in src.taskill.git_state)* | 3 | 1 | 13 | **14** |

```toon markpact:analysis path=project/calls.toon.yaml
# code2llm call graph | /home/tom/github/semcod/taskill
# nodes: 34 | edges: 28 | modules: 12
# CC̄=4.3

HUBS[20]:
  src.taskill.config.load_config
    CC=8  in:3  out:35  total:38
  src.taskill.cli.run
    CC=16  in:0  out:32  total:32
  src.taskill.providers.windsurf_mcp.WindsurfMcpProvider.generate
    CC=7  in:0  out:32  total:32
  src.taskill.providers.openrouter.OpenRouterProvider.generate
    CC=6  in:0  out:27  total:27
  src.taskill.triggers.evaluate
    CC=21  in:2  out:23  total:25
  src.taskill.cli.status
    CC=11  in:0  out:25  total:25
  src.taskill.core.Taskill.run
    CC=11  in:0  out:20  total:20
  src.taskill.git_state.collect_snapshot
    CC=3  in:1  out:13  total:14
  src.taskill.updaters.readme.update_readme
    CC=6  in:1  out:11  total:12
  src.taskill.git_state.read_coverage
    CC=7  in:1  out:11  total:12
  src.taskill.core.Taskill._apply
    CC=4  in:0  out:12  total:12
  src.taskill.git_state.read_failed_tests
    CC=5  in:1  out:8  total:9
  src.taskill.providers.windsurf_mcp._candidate_endpoints
    CC=5  in:2  out:7  total:9
  src.taskill.git_state.commits_since
    CC=7  in:1  out:8  total:9
  src.taskill.providers.discover_providers
    CC=6  in:1  out:7  total:8
  src.taskill.cli.release
    CC=2  in:0  out:8  total:8
  src.taskill.state.load_state
    CC=3  in:1  out:6  total:7
  src.taskill.updaters.changelog.release_unreleased
    CC=4  in:1  out:6  total:7
  src.taskill.updaters.readme.render_status_block
    CC=6  in:1  out:5  total:6
  src.taskill.git_state._run
    CC=2  in:4  out:2  total:6

MODULES:
  src.taskill.cli  [6 funcs]
    _setup_logging  CC=2  out:1
    clean_todo  CC=1  out:6
    main  CC=1  out:6
    release  CC=2  out:8
    run  CC=16  out:32
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
  src.taskill.triggers  [1 funcs]
    evaluate  CC=21  out:23
  src.taskill.updaters.changelog  [1 funcs]
    release_unreleased  CC=4  out:6
  src.taskill.updaters.readme  [2 funcs]
    render_status_block  CC=6  out:5
    update_readme  CC=6  out:11
  src.taskill.updaters.todo  [1 funcs]
    empty_todo  CC=1  out:1

EDGES:
  src.taskill.providers.build_chain → src.taskill.providers.discover_providers
  src.taskill.providers.windsurf_mcp.WindsurfMcpProvider.is_available → src.taskill.providers.windsurf_mcp._mcp_lib_present
  src.taskill.providers.windsurf_mcp.WindsurfMcpProvider.is_available → src.taskill.providers.windsurf_mcp._candidate_endpoints
  src.taskill.providers.windsurf_mcp.WindsurfMcpProvider.generate → src.taskill.providers.windsurf_mcp._candidate_endpoints
  src.taskill.providers.windsurf_mcp.WindsurfMcpProvider.generate → src.taskill.providers.windsurf_mcp._mcp_lib_present
  src.taskill.providers.openrouter.OpenRouterProvider.generate → src.taskill.providers.openrouter._normalize_model
  src.taskill.git_state.head_sha → src.taskill.git_state._run
  src.taskill.git_state.commits_since → src.taskill.git_state._run
  src.taskill.git_state.changed_files_since → src.taskill.git_state._run
  src.taskill.git_state.collect_snapshot → src.taskill.git_state.head_sha
  src.taskill.git_state.collect_snapshot → src.taskill.git_state.commits_since
  src.taskill.git_state.collect_snapshot → src.taskill.git_state.changed_files_since
  src.taskill.git_state.collect_snapshot → src.taskill.git_state.read_coverage
  src.taskill.git_state.collect_snapshot → src.taskill.git_state.read_failed_tests
  src.taskill.git_state.collect_snapshot → src.taskill.git_state.file_hash
  src.taskill.updaters.readme.update_readme → src.taskill.updaters.readme.render_status_block
  src.taskill.core.Taskill.__init__ → src.taskill.state.load_state
  src.taskill.core.Taskill.__init__ → src.taskill.config.load_config
  src.taskill.core.Taskill.run → src.taskill.triggers.evaluate
  src.taskill.core.Taskill.run → src.taskill.providers.build_chain
  src.taskill.core.Taskill.status → src.taskill.triggers.evaluate
  src.taskill.core.Taskill._snapshot → src.taskill.git_state.collect_snapshot
  src.taskill.core.Taskill._apply → src.taskill.updaters.readme.update_readme
  src.taskill.cli.main → src.taskill.cli._setup_logging
  src.taskill.cli.run → src.taskill.config.load_config
  src.taskill.cli.status → src.taskill.config.load_config
  src.taskill.cli.release → src.taskill.updaters.changelog.release_unreleased
  src.taskill.cli.clean_todo → src.taskill.updaters.todo.empty_todo
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
# nodes: 34 | edges: 28 | modules: 12
# CC̄=4.3

HUBS[20]:
  src.taskill.config.load_config
    CC=8  in:3  out:35  total:38
  src.taskill.cli.run
    CC=16  in:0  out:32  total:32
  src.taskill.providers.windsurf_mcp.WindsurfMcpProvider.generate
    CC=7  in:0  out:32  total:32
  src.taskill.providers.openrouter.OpenRouterProvider.generate
    CC=6  in:0  out:27  total:27
  src.taskill.triggers.evaluate
    CC=21  in:2  out:23  total:25
  src.taskill.cli.status
    CC=11  in:0  out:25  total:25
  src.taskill.core.Taskill.run
    CC=11  in:0  out:20  total:20
  src.taskill.git_state.collect_snapshot
    CC=3  in:1  out:13  total:14
  src.taskill.updaters.readme.update_readme
    CC=6  in:1  out:11  total:12
  src.taskill.git_state.read_coverage
    CC=7  in:1  out:11  total:12
  src.taskill.core.Taskill._apply
    CC=4  in:0  out:12  total:12
  src.taskill.git_state.read_failed_tests
    CC=5  in:1  out:8  total:9
  src.taskill.providers.windsurf_mcp._candidate_endpoints
    CC=5  in:2  out:7  total:9
  src.taskill.git_state.commits_since
    CC=7  in:1  out:8  total:9
  src.taskill.providers.discover_providers
    CC=6  in:1  out:7  total:8
  src.taskill.cli.release
    CC=2  in:0  out:8  total:8
  src.taskill.state.load_state
    CC=3  in:1  out:6  total:7
  src.taskill.updaters.changelog.release_unreleased
    CC=4  in:1  out:6  total:7
  src.taskill.updaters.readme.render_status_block
    CC=6  in:1  out:5  total:6
  src.taskill.git_state._run
    CC=2  in:4  out:2  total:6

MODULES:
  src.taskill.cli  [6 funcs]
    _setup_logging  CC=2  out:1
    clean_todo  CC=1  out:6
    main  CC=1  out:6
    release  CC=2  out:8
    run  CC=16  out:32
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
  src.taskill.triggers  [1 funcs]
    evaluate  CC=21  out:23
  src.taskill.updaters.changelog  [1 funcs]
    release_unreleased  CC=4  out:6
  src.taskill.updaters.readme  [2 funcs]
    render_status_block  CC=6  out:5
    update_readme  CC=6  out:11
  src.taskill.updaters.todo  [1 funcs]
    empty_todo  CC=1  out:1

EDGES:
  src.taskill.providers.build_chain → src.taskill.providers.discover_providers
  src.taskill.providers.windsurf_mcp.WindsurfMcpProvider.is_available → src.taskill.providers.windsurf_mcp._mcp_lib_present
  src.taskill.providers.windsurf_mcp.WindsurfMcpProvider.is_available → src.taskill.providers.windsurf_mcp._candidate_endpoints
  src.taskill.providers.windsurf_mcp.WindsurfMcpProvider.generate → src.taskill.providers.windsurf_mcp._candidate_endpoints
  src.taskill.providers.windsurf_mcp.WindsurfMcpProvider.generate → src.taskill.providers.windsurf_mcp._mcp_lib_present
  src.taskill.providers.openrouter.OpenRouterProvider.generate → src.taskill.providers.openrouter._normalize_model
  src.taskill.git_state.head_sha → src.taskill.git_state._run
  src.taskill.git_state.commits_since → src.taskill.git_state._run
  src.taskill.git_state.changed_files_since → src.taskill.git_state._run
  src.taskill.git_state.collect_snapshot → src.taskill.git_state.head_sha
  src.taskill.git_state.collect_snapshot → src.taskill.git_state.commits_since
  src.taskill.git_state.collect_snapshot → src.taskill.git_state.changed_files_since
  src.taskill.git_state.collect_snapshot → src.taskill.git_state.read_coverage
  src.taskill.git_state.collect_snapshot → src.taskill.git_state.read_failed_tests
  src.taskill.git_state.collect_snapshot → src.taskill.git_state.file_hash
  src.taskill.updaters.readme.update_readme → src.taskill.updaters.readme.render_status_block
  src.taskill.core.Taskill.__init__ → src.taskill.state.load_state
  src.taskill.core.Taskill.__init__ → src.taskill.config.load_config
  src.taskill.core.Taskill.run → src.taskill.triggers.evaluate
  src.taskill.core.Taskill.run → src.taskill.providers.build_chain
  src.taskill.core.Taskill.status → src.taskill.triggers.evaluate
  src.taskill.core.Taskill._snapshot → src.taskill.git_state.collect_snapshot
  src.taskill.core.Taskill._apply → src.taskill.updaters.readme.update_readme
  src.taskill.cli.main → src.taskill.cli._setup_logging
  src.taskill.cli.run → src.taskill.config.load_config
  src.taskill.cli.status → src.taskill.config.load_config
  src.taskill.cli.release → src.taskill.updaters.changelog.release_unreleased
  src.taskill.cli.clean_todo → src.taskill.updaters.todo.empty_todo
```

### Code Analysis (`project/analysis.toon.yaml`)

```toon markpact:analysis path=project/analysis.toon.yaml
# code2llm | 25f 2730L | python:17,yml:3,shell:2,yaml:2,toml:1 | 2026-04-25
# CC̄=4.3 | critical:2/60 | dups:0 | cycles:0

HEALTH[2]:
  🟡 CC    evaluate CC=21 (limit:15)
  🟡 CC    run CC=16 (limit:15)

REFACTOR[1]:
  1. split 2 high-CC methods  (CC>15)

PIPELINES[29]:
  [1] Src [is_available]: is_available → _mcp_lib_present
      PURITY: 100% pure
  [2] Src [generate]: generate → _candidate_endpoints
      PURITY: 100% pure
  [3] Src [is_available]: is_available
      PURITY: 100% pure
  [4] Src [generate]: generate → _normalize_model
      PURITY: 100% pure
  [5] Src [_parse_json_loosely]: _parse_json_loosely
      PURITY: 100% pure

LAYERS:
  src/                            CC̄=4.3    ←in:0  →out:0
  │ !! cli                        253L  0C    7m  CC=16     ←0
  │ core                       211L  2C    9m  CC=11     ←0
  │ config                     170L  4C    1m  CC=8      ←2
  │ algorithmic                155L  1C    5m  CC=10     ←0
  │ git_state                  147L  2C    8m  CC=7      ←2
  │ windsurf_mcp               135L  1C    4m  CC=7      ←0
  │ openrouter                 114L  1C    4m  CC=6      ←1
  │ todo                       113L  1C    3m  CC=1      ←1
  │ changelog                  112L  1C    3m  CC=12     ←1
  │ base                       105L  3C    5m  CC=9      ←2
  │ !! triggers                    94L  1C    2m  CC=21     ←1
  │ __init__                    75L  0C    2m  CC=6      ←1
  │ readme                      71L  0C    2m  CC=6      ←1
  │ base                        44L  2C    2m  CC=2      ←0
  │ state                       42L  1C    3m  CC=3      ←1
  │ __init__                    20L  0C    0m  CC=0.0    ←0
  │ __init__                     6L  0C    0m  CC=0.0    ←0
  │
  ./                              CC̄=0.0    ←in:0  →out:0
  │ !! goal.yaml                  512L  0C    0m  CC=0.0    ←0
  │ pyproject.toml              97L  0C    0m  CC=0.0    ←0
  │ taskill.yaml                57L  0C    0m  CC=0.0    ←0
  │ project.sh                  47L  0C    0m  CC=0.0    ←0
  │ tree.sh                      1L  0C    0m  CC=0.0    ←0
  │
  examples/                       CC̄=0.0    ←in:0  →out:0
  │ ansible-playbook.yml        52L  0C    0m  CC=0.0    ←0
  │ github-action.yml           51L  0C    0m  CC=0.0    ←0
  │ gitlab-ci.yml               46L  0C    0m  CC=0.0    ←0
  │

COUPLING: no cross-package imports detected

EXTERNAL:
  validation: run `vallm batch .` → validation.toon
  duplication: run `redup scan .` → duplication.toon
```

### Duplication (`project/duplication.toon.yaml`)

```toon markpact:analysis path=project/duplication.toon.yaml
# redup/duplication | 1 groups | 17f 1955L | 2026-04-25

SUMMARY:
  files_scanned: 17
  total_lines:   1955
  dup_groups:    1
  dup_fragments: 2
  saved_lines:   29
  scan_ms:       5752

HOTSPOTS[2] (files with most duplication):
  src/taskill/providers/__init__.py  dup=29L  groups=1  frags=1  (1.5%)
  src/taskill/updaters/__init__.py  dup=29L  groups=1  frags=1  (1.5%)

DUPLICATES[1] (ranked by impact):
  [e7fb8feab50f19ae]   STRU  discover_providers  L=29 N=2 saved=29 sim=1.00
      src/taskill/providers/__init__.py:33-61  (discover_providers)
      src/taskill/updaters/__init__.py:31-59  (discover_updaters)

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
# code2llm/evolution | 60 func | 15f | 2026-04-25

NEXT[2] (ranked by impact):
  [1] !  SPLIT-FUNC      run  CC=16  fan=16
      WHY: CC=16 exceeds 15
      EFFORT: ~1h  IMPACT: 256

  [2] !  SPLIT-FUNC      evaluate  CC=21  fan=11
      WHY: CC=21 exceeds 15
      EFFORT: ~1h  IMPACT: 231


RISKS[0]: none

METRICS-TARGET:
  CC̄:          4.3 → ≤3.0
  max-CC:      21 → ≤10
  god-modules: 0 → 0
  high-CC(≥15): 2 → ≤1
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
  (first run — no previous data)
```

## Intent

Daily project hygiene: keep README / CHANGELOG / TODO in sync with reality. LLM-first, algorithmic fallback.
