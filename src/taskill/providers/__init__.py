"""Provider chain. First successful provider wins.

Order is determined by config (taskill.yaml: providers: [...]).
Default order: windsurf_mcp → openrouter → algorithmic.

Providers are discovered via entry points under "taskill.providers".
"""
from __future__ import annotations

import importlib.metadata
from typing import TYPE_CHECKING

from taskill.providers.algorithmic import AlgorithmicProvider
from taskill.providers.base import GeneratedDocs, Provider, ProviderError
from taskill.providers.openrouter import OpenRouterProvider
from taskill.providers.windsurf_mcp import WindsurfMcpProvider

if TYPE_CHECKING:
    from taskill.config import ProviderConfig

__all__ = [
    "Provider",
    "ProviderError",
    "GeneratedDocs",
    "AlgorithmicProvider",
    "OpenRouterProvider",
    "WindsurfMcpProvider",
    "build_chain",
    "discover_providers",
]


def discover_providers() -> dict[str, type[Provider]]:
    """Discover all registered providers via entry points.

    Falls back to built-in registry if entry points are not available
    (e.g., during development before install).
    """
    registry: dict[str, type[Provider]] = {}

    # Try to load from entry points
    try:
        entry_points = importlib.metadata.entry_points(group="taskill.providers")
        for ep in entry_points:
            try:
                provider_cls = ep.load()
                if isinstance(provider_cls, type) and issubclass(provider_cls, Provider):
                    registry[ep.name] = provider_cls
            except Exception:
                # Silently skip broken entry points
                continue
    except Exception:
        # Entry points not available (e.g., not installed), fall back to built-ins
        pass

    # Always ensure built-ins are available as fallback
    registry.setdefault("windsurf_mcp", WindsurfMcpProvider)
    registry.setdefault("openrouter", OpenRouterProvider)
    registry.setdefault("algorithmic", AlgorithmicProvider)

    return registry


def build_chain(provider_configs: list[ProviderConfig]) -> list[Provider]:
    """Materialize provider config list into provider instances (only enabled)."""
    registry = discover_providers()
    chain = []
    for cfg in provider_configs:
        if not cfg.enabled:
            continue
        cls = registry.get(cfg.name)
        if cls is None:
            continue
        chain.append(cls(options=cfg.options))
    return chain
