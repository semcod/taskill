"""Document updaters — apply GeneratedDocs to README/CHANGELOG/TODO.

Updaters are discovered via entry points under "taskill.updaters".
"""
from __future__ import annotations

import importlib.metadata
from typing import TYPE_CHECKING

from taskill.updaters.base import DocumentUpdater, UpdateResult
from taskill.updaters.changelog import ChangelogUpdater, update_changelog
from taskill.updaters.readme import ReadmeUpdater, update_readme
from taskill.updaters.todo import TodoUpdater, update_todo

if TYPE_CHECKING:
    from taskill.git_state import ProjectSnapshot

__all__ = [
    "DocumentUpdater",
    "UpdateResult",
    "ChangelogUpdater",
    "TodoUpdater",
    "ReadmeUpdater",
    "update_changelog",
    "update_todo",
    "update_readme",
    "discover_updaters",
]


def discover_updaters() -> dict[str, type[DocumentUpdater]]:
    """Discover all registered updaters via entry points.

    Falls back to built-in registry if entry points are not available
    (e.g., during development before install).
    """
    registry: dict[str, type[DocumentUpdater]] = {}
    
    # Try to load from entry points
    try:
        entry_points = importlib.metadata.entry_points(group="taskill.updaters")
        for ep in entry_points:
            try:
                updater_cls = ep.load()
                if isinstance(updater_cls, type) and issubclass(updater_cls, DocumentUpdater):
                    registry[ep.name] = updater_cls
            except Exception:
                # Silently skip broken entry points
                continue
    except Exception:
        # Entry points not available (e.g., not installed), fall back to built-ins
        pass
    
    # Always ensure built-ins are available as fallback
    registry.setdefault("changelog", ChangelogUpdater)
    registry.setdefault("todo", TodoUpdater)
    registry.setdefault("readme", ReadmeUpdater)
    
    return registry
