# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.10] - 2026-04-25

### Fixed
- Fix unused-imports issues (ticket-db5e9dd3)
- Fix magic-numbers issues (ticket-dba8c3c5)
- Fix unused-imports issues (ticket-af09dd4b)
- Fix magic-numbers issues (ticket-ea7332e2)
- Fix unused-imports issues (ticket-9c26f888)
- Fix magic-numbers issues (ticket-f494aa3e)
- Fix ai-boilerplate issues (ticket-3bd97300)
- Fix string-concat issues (ticket-b6a4b573)
- Fix unused-imports issues (ticket-5432ca41)
- Fix magic-numbers issues (ticket-bd9bfba5)
- Fix unused-imports issues (ticket-d5ad71d9)
- Fix magic-numbers issues (ticket-fe3ac057)
- Fix unused-imports issues (ticket-4d94a8de)
- Fix magic-numbers issues (ticket-8d730c8d)
- Fix unused-imports issues (ticket-7a0100b5)
- Fix magic-numbers issues (ticket-bbec1630)
- Fix unused-imports issues (ticket-8a420046)
- Fix unused-imports issues (ticket-1e4e88a3)
- Fix unused-imports issues (ticket-e510c6ac)
- Fix string-concat issues (ticket-827efc22)
- Fix unused-imports issues (ticket-d605ceff)
- Fix unused-imports issues (ticket-36ce53f0)
- Fix string-concat issues (ticket-2afcff30)
- Fix unused-imports issues (ticket-3865ee88)
- Fix unused-imports issues (ticket-f2dc4a4e)
- Fix llm-generated-code issues (ticket-190195e3)
- Fix string-concat issues (ticket-b05e6370)
- Fix unused-imports issues (ticket-fdbb78c9)
- Fix string-concat issues (ticket-605e46fa)
- Fix unused-imports issues (ticket-8062d9b4)
- Fix smart-return-type issues (ticket-c98c14b7)
- Fix unused-imports issues (ticket-14a6db68)
- Fix smart-return-type issues (ticket-af05b203)
- Fix unused-imports issues (ticket-885edd98)
- Fix duplicate-imports issues (ticket-f77051af)
- Fix smart-return-type issues (ticket-1f6a0131)
- Fix unused-imports issues (ticket-1ced127f)
- Fix smart-return-type issues (ticket-22f03c7b)
- Fix unused-imports issues (ticket-11ba31e7)
- Fix smart-return-type issues (ticket-098fd02a)
- Fix unused-imports issues (ticket-3ec5ceaf)

## [Unreleased]

## [0.1.2] - 2026-04-25

### Docs
- Update CHANGELOG.md
- Update README.md
- Update SUMD.md
- Update SUMR.md
- Update TODO.md
- Update project/README.md
- Update project/context.md

### Test
- Update testql-scenarios/generated-cli-tests.testql.toon.yaml
- Update tests/test_providers.py

### Other
- Update app.doql.less
- Update planfile.yaml
- Update prefact.yaml
- Update project/analysis.toon.yaml
- Update project/calls.mmd
- Update project/calls.png
- Update project/calls.toon.yaml
- Update project/calls.yaml
- Update project/compact_flow.mmd
- Update project/compact_flow.png
- ... and 9 more files

## [0.1.1] - 2026-04-25

### Docs
- Update CHANGELOG.md
- Update README.md
- Update ROADMAP.md
- Update SUMD.md
- Update TODO.md

### Test
- Update tests/__init__.py
- Update tests/test_algorithmic.py
- Update tests/test_config.py
- Update tests/test_triggers.py
- Update tests/test_updaters.py

### Other
- Update .env.example
- Update .gitignore
- Update PKG-INFO
- Update examples/ansible-playbook.yml
- Update examples/github-action.yml
- Update examples/gitlab-ci.yml
- Update examples/systemd-timer/taskill.service
- Update examples/systemd-timer/taskill.timer
- Update project.sh
- Update taskill.yaml
- ... and 1 more files

## [0.1.0] - 2026-04-25

### Added

- Initial working version
- Provider chain: Windsurf MCP → OpenRouter → algorithmic fallback
- Trigger system with state persistence in `.taskill/state.json`
- CHANGELOG / TODO / README updaters (idempotent, marker-bounded)
- CLI: `taskill init / status / run / release / clean-todo`
- `.env` loading via `python-dotenv`; auto-strips `openrouter/` prefix from `LLM_MODEL`
- Conventional Commits parser for the algorithmic provider
- Loose-coupling integration with `pyqual` (subprocess + JSON report)
- Example configs for GitHub Actions, GitLab CI, Ansible
