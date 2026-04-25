"""taskill — daily project hygiene automation.

Keeps README.md / CHANGELOG.md / TODO.md in sync with reality:
- reads git log, SUMD.md, SUMR.md, test results, coverage
- moves completed TODO items to CHANGELOG
- regenerates README sections that are out of date
- runs daily (or per metric thresholds) standalone, in CI, or via Ansible

Provider chain (first match wins):
1. Windsurf MCP   (when configured — uses your existing JetBrains plugin context)
2. OpenRouter     (LLM via OPENROUTER_API_KEY + LLM_MODEL)
3. Algorithmic    (deterministic fallback: conventional commits + heuristics)
"""

__version__ = "0.1.2"

from taskill.config import TaskillConfig, load_config
from taskill.core import Taskill, TaskillResult

__all__ = ["TaskillConfig", "load_config", "Taskill", "TaskillResult", "__version__"]
