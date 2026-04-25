# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
