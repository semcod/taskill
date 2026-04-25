# pyqual

Declarative quality gate loops for AI-assisted development

## Contents

- [Metadata](#metadata)
- [Architecture](#architecture)
- [Dependencies](#dependencies)
- [Source Map](#source-map)
- [Intent](#intent)

## Metadata

- **name**: `pyqual`
- **version**: `0.1.143`
- **python_requires**: `>=3.13`
- **license**: MIT
- **ecosystem**: SUMD + DOQL + testql + taskfile
- **generated_from**: pyproject.toml, Taskfile.yml, Makefile, src/

## Architecture

```
SUMD (description) → DOQL/source (code) → taskfile (automation) → testql (verification)
```

## Source Map

- dashboard/node_modules/flatted/python/flatted.py
- dashboard/api/main.py
- dashboard/constants.py
- conftest.py
- examples/custom_gates/metric_history.py
- examples/custom_gates/composite_gates.py
- examples/custom_gates/dynamic_thresholds.py
- examples/custom_gates/composite_simple.py
- examples/custom_plugins/performance_collector.py
- examples/custom_plugins/code_health_collector.py
- examples/integration_example.py
- examples/basic/sync_if_fail.py
- examples/basic/minimal.py
- examples/basic/check_gates.py
- examples/basic/run_pipeline.py
- examples/multi_gate_pipeline/run_pipeline.py
- examples/ticket_workflow/sync_tickets.py
- tests/test_release_validation.py
- tests/test_bulk_run.py
- tests/test_validation.py
- tests/test_secrets_collector.py
- tests/test_pipeline_stages.py
- tests/test_report.py
- tests/test_report_badges.py
- tests/test_profiles.py
- tests/test_tickets.py
- tests/test_report_helpers.py
- tests/test_pyqual.py
- tests/test_github_actions.py
- tests/test_bulk_init_pkg/conftest.py
- tests/test_bulk_init_pkg/test_fingerprint.py
- tests/test_bulk_init_pkg/test_fixtures.py
- tests/test_bulk_init_pkg/__init__.py
- tests/test_bulk_init_pkg/test_yaml_generation.py
- tests/test_bulk_init_pkg/test_heuristics.py
- tests/__init__.py
- tests/test_config.py
- tests/test_report_readme.py
- tests/test_cli_run_helpers.py
- tests/test_report_project_badges.py
- tests/test_profiles_module.py
- tests/report_helpers.py
- tests/test_report_generate.py
- tests/test_runtime_errors.py
- tests/test_bulk_init.py
- tests/test_report_quality_badges.py
- tests/pipeline_test.py
- tests/test_llx_mcp.py
- tests/config_test.py
- tests/test_report_collect.py
