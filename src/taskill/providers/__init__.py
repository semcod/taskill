"""Provider chain. First successful provider wins.

Order is determined by config (taskill.yaml: providers: [...]).
Default order: windsurf_mcp → openrouter → algorithmic.
"""
from taskill.providers.base import Provider, ProviderError, GeneratedDocs
from taskill.providers.algorithmic import AlgorithmicProvider
from taskill.providers.openrouter import OpenRouterProvider
from taskill.providers.windsurf_mcp import WindsurfMcpProvider

__all__ = [
    "Provider",
    "ProviderError",
    "GeneratedDocs",
    "AlgorithmicProvider",
    "OpenRouterProvider",
    "WindsurfMcpProvider",
    "build_chain",
]


def build_chain(provider_configs):
    """Materialize provider config list into provider instances (only enabled)."""
    registry = {
        "windsurf_mcp": WindsurfMcpProvider,
        "openrouter": OpenRouterProvider,
        "algorithmic": AlgorithmicProvider,
    }
    chain = []
    for cfg in provider_configs:
        if not cfg.enabled:
            continue
        cls = registry.get(cfg.name)
        if cls is None:
            continue
        chain.append(cls(options=cfg.options))
    return chain
