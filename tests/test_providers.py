"""Provider discovery and chain building tests."""
from __future__ import annotations

from taskill.config import ProviderConfig
from taskill.providers import build_chain, discover_providers
from taskill.providers.algorithmic import AlgorithmicProvider
from taskill.providers.openrouter import OpenRouterProvider
from taskill.providers.windsurf_mcp import WindsurfMcpProvider


def test_discover_providers_returns_builtins() -> None:
    """Entry points discovery should return all built-in providers."""
    registry = discover_providers()
    assert "windsurf_mcp" in registry
    assert "openrouter" in registry
    assert "algorithmic" in registry
    assert registry["windsurf_mcp"] is WindsurfMcpProvider
    assert registry["openrouter"] is OpenRouterProvider
    assert registry["algorithmic"] is AlgorithmicProvider


def test_build_chain_with_enabled_providers() -> None:
    """Only enabled providers should be instantiated."""
    configs = [
        ProviderConfig(name="windsurf_mcp", enabled=True, options={}),
        ProviderConfig(name="openrouter", enabled=False, options={}),
        ProviderConfig(name="algorithmic", enabled=True, options={}),
    ]
    chain = build_chain(configs)
    assert len(chain) == 2
    assert isinstance(chain[0], WindsurfMcpProvider)
    assert isinstance(chain[1], AlgorithmicProvider)


def test_build_chain_with_unknown_provider() -> None:
    """Unknown provider names should be silently skipped."""
    configs = [
        ProviderConfig(name="windsurf_mcp", enabled=True, options={}),
        ProviderConfig(name="nonexistent_provider", enabled=True, options={}),
        ProviderConfig(name="algorithmic", enabled=True, options={}),
    ]
    chain = build_chain(configs)
    assert len(chain) == 2
    assert isinstance(chain[0], WindsurfMcpProvider)
    assert isinstance(chain[1], AlgorithmicProvider)


def test_build_chain_preserves_order() -> None:
    """Provider order from config should be preserved."""
    configs = [
        ProviderConfig(name="algorithmic", enabled=True, options={}),
        ProviderConfig(name="openrouter", enabled=True, options={}),
        ProviderConfig(name="windsurf_mcp", enabled=True, options={}),
    ]
    chain = build_chain(configs)
    assert len(chain) == 3
    assert isinstance(chain[0], AlgorithmicProvider)
    assert isinstance(chain[1], OpenRouterProvider)
    assert isinstance(chain[2], WindsurfMcpProvider)


def test_build_chain_empty_config() -> None:
    """Empty provider list should return empty chain."""
    chain = build_chain([])
    assert len(chain) == 0


def test_build_chain_all_disabled() -> None:
    """All providers disabled should return empty chain."""
    configs = [
        ProviderConfig(name="windsurf_mcp", enabled=False, options={}),
        ProviderConfig(name="openrouter", enabled=False, options={}),
        ProviderConfig(name="algorithmic", enabled=False, options={}),
    ]
    chain = build_chain(configs)
    assert len(chain) == 0
