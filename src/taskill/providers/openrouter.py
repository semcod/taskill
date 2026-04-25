"""OpenRouter provider.

Reads OPENROUTER_API_KEY and LLM_MODEL from env (loaded via .env in config).
Uses HTTP directly to keep deps minimal — no openai SDK needed.
"""
from __future__ import annotations

import os
from typing import Any

import httpx

from taskill.providers.base import (
    GeneratedDocs,
    Provider,
    ProviderError,
    SYSTEM_PROMPT,
    build_user_prompt,
    parse_json_loosely,
)


# OpenRouter model strings often arrive as "openrouter/qwen/qwen3-coder-next" — the leading
# "openrouter/" segment is litellm-style. The OpenRouter REST API itself wants just
# "qwen/qwen3-coder-next". We strip the prefix automatically.
def _normalize_model(model: str) -> str:
    if model.startswith("openrouter/"):
        return model[len("openrouter/"):]
    return model


class OpenRouterProvider(Provider):
    name = "openrouter"

    def is_available(self) -> bool:
        return bool(os.getenv("OPENROUTER_API_KEY"))

    def generate(self, context: dict[str, Any]) -> GeneratedDocs:
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ProviderError("OPENROUTER_API_KEY not set")

        model = _normalize_model(os.getenv("LLM_MODEL", "qwen/qwen3-coder-next"))
        base_url = self.options.get("base_url", "https://openrouter.ai/api/v1")
        timeout = self.options.get("timeout", 120)

        payload = {
            "model": model,
            "temperature": self.options.get("temperature", 0.2),
            "max_tokens": self.options.get("max_tokens", 4096),
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(context)},
            ],
            # JSON mode if model supports it; harmless if it doesn't
            "response_format": {"type": "json_object"},
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            # OpenRouter recommends these for analytics / better routing
            "HTTP-Referer": self.options.get("referer", "https://github.com/oqlos/taskill"),
            "X-Title": "taskill",
        }

        try:
            with httpx.Client(timeout=timeout) as client:
                resp = client.post(f"{base_url}/chat/completions", json=payload, headers=headers)
        except httpx.HTTPError as e:
            raise ProviderError(f"OpenRouter request failed: {e}") from e

        if resp.status_code != 200:
            raise ProviderError(
                f"OpenRouter returned {resp.status_code}: {resp.text[:300]}"
            )

        try:
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            raise ProviderError(f"Malformed OpenRouter response: {e}") from e

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

