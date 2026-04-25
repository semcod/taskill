"""Windsurf MCP provider — first in the chain.

Why first: the user runs the Windsurf plugin in JetBrains, which exposes
an MCP server with rich workspace context (open files, diagnostics, etc.).
If reachable, it produces better results than a cold OpenRouter call.

Discovery (in order):
  1. options.endpoint == "stdio" → spawn `windsurf mcp` (or path from options.command)
  2. options.endpoint starts with "ws://" or "http://" → connect remotely
  3. WINDSURF_MCP_ENDPOINT env var
  4. Probe known JetBrains plugin sockets at ~/.codeium/windsurf/mcp.sock
     and ~/.windsurf/mcp.sock

If the optional `mcp` package is not installed, this provider is unavailable
(returns False from is_available) and the chain falls through cleanly to
OpenRouter. This is intentional — taskill should not require MCP to work.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from taskill.providers.base import (
    SYSTEM_PROMPT,
    GeneratedDocs,
    Provider,
    ProviderError,
    build_user_prompt,
    parse_json_loosely,
)


def _mcp_lib_present() -> bool:
    try:
        import mcp  # noqa: F401
        return True
    except ImportError:
        return False


def _candidate_endpoints(options: dict[str, Any]) -> list[str]:
    cands: list[str] = []
    ep = options.get("endpoint")
    if ep:
        cands.append(ep)
    env_ep = os.getenv("WINDSURF_MCP_ENDPOINT")
    if env_ep:
        cands.append(env_ep)
    home = Path.home()
    for sock in (home / ".codeium" / "windsurf" / "mcp.sock",
                 home / ".windsurf" / "mcp.sock"):
        if sock.exists():
            cands.append(f"unix://{sock}")
    return cands


class WindsurfMcpProvider(Provider):
    name = "windsurf_mcp"

    def is_available(self) -> bool:
        if not _mcp_lib_present():
            return False
        # consider available if at least one candidate endpoint resolves
        return bool(_candidate_endpoints(self.options))

    def generate(self, context: dict[str, Any]) -> GeneratedDocs:
        if not _mcp_lib_present():
            raise ProviderError(
                "MCP library not installed (pip install 'taskill[mcp]')"
            )

        # Lazy import — keep MCP truly optional
        try:
            from mcp import ClientSession  # type: ignore
            from mcp.client.stdio import StdioServerParameters, stdio_client  # type: ignore
        except ImportError as e:
            raise ProviderError(f"MCP import failed: {e}") from e

        endpoints = _candidate_endpoints(self.options)
        if not endpoints:
            raise ProviderError("No Windsurf MCP endpoint configured or discovered")

        # NOTE: full MCP plumbing is async; for the working version we delegate
        # to a sync helper that picks the simplest viable path (stdio command).
        # Remote ws/unix transports land in the refactor (see ROADMAP.md).
        cmd = self.options.get("command")
        if not cmd:
            raise ProviderError(
                "Windsurf MCP stdio requires options.command (e.g. 'windsurf mcp serve')"
            )

        try:
            import asyncio

            async def _run() -> str:
                params = StdioServerParameters(
                    command=cmd[0] if isinstance(cmd, list) else cmd,
                    args=cmd[1:] if isinstance(cmd, list) else [],
                )
                async with stdio_client(params) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        # Use a generic 'chat' or 'complete' tool exposed by the server.
                        tool_name = self.options.get("tool_name", "complete")
                        result = await session.call_tool(
                            tool_name,
                            arguments={
                                "system": SYSTEM_PROMPT,
                                "prompt": build_user_prompt(context),
                            },
                        )
                        # MCP tool result content blocks
                        for block in result.content:
                            if hasattr(block, "text"):
                                return block.text  # type: ignore[no-any-return]
                        raise ProviderError("Empty response from MCP tool")

            content = asyncio.run(_run())
        except Exception as e:  # broad — MCP can fail many ways; surface cleanly
            raise ProviderError(f"Windsurf MCP call failed: {e}") from e

        parsed = parse_json_loosely(content)
        if parsed is None:
            raise ProviderError("Windsurf MCP did not return valid JSON")

        return GeneratedDocs(
            changelog_entries=list(parsed.get("changelog_entries", [])),
            todo_completed=list(parsed.get("todo_completed", [])),
            todo_new=list(parsed.get("todo_new", [])),
            summary=str(parsed.get("summary", "")),
            provider_name=self.name,
        )
