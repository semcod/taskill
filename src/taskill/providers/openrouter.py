"""OpenRouter provider.

Reads OPENROUTER_API_KEY and LLM_MODEL from env (loaded via .env in config).
Uses HTTP directly to keep deps minimal — no openai SDK needed.
"""

from __future__ import annotations

import os
from typing import Any

try:
    from subllm import available_routes, complete as subllm_complete
except ImportError:
    available_routes = None
    subllm_complete = None

from taskill.providers.base import (
    SYSTEM_PROMPT,
    GeneratedDocs,
    Provider,
    ProviderError,
    build_user_prompt,
    parse_json_loosely,
)


# OpenRouter model strings often arrive as "openrouter/qwen/qwen3-coder-next" — the leading
# "openrouter/" segment is litellm-style. The OpenRouter REST API itself wants just
# "qwen/qwen3-coder-next". We strip the prefix automatically.
def _normalize_model(model: str) -> str:
    if model.startswith("openrouter/"):
        return model[len("openrouter/") :]
    return model


class OpenRouterProvider(Provider):
    name = "openrouter"

    def is_available(self) -> bool:
        if available_routes is None:
            return False
        return bool(available_routes("semcod-taskill", "execute"))

    def generate(self, context: dict[str, Any]) -> GeneratedDocs:
        if subllm_complete is None:
            raise ProviderError("subactor-subllm is not available")

        _DEFAULT_TIMEOUT = 120
        timeout = self.options.get("timeout", _DEFAULT_TIMEOUT)
        try:
            response = subllm_complete(
                "semcod-taskill",
                "execute",
                [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": build_user_prompt(context)},
                ],
                timeout_seconds=timeout,
            )
            content = response.content
            model = response.model
        except Exception as e:
            raise ProviderError(f"SubLLM request failed: {e}") from e

        parsed = parse_json_loosely(content)
        if parsed is None:
            raise ProviderError("Model did not return valid JSON")

        return GeneratedDocs(
            changelog_entries=list(parsed.get("changelog_entries", [])),
            todo_completed=list(parsed.get("todo_completed", [])),
            todo_new=list(parsed.get("todo_new", [])),
            summary=str(parsed.get("summary", "")),
            provider_name=f"{self.name}:{model}",
        )
