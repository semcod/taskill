"""Updater abstraction + shared types."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from taskill.git_state import ProjectSnapshot


@dataclass
class UpdateResult:
    """What every updater returns."""
    changed: bool
    path: Path
    updater_name: str = "unknown"


class DocumentUpdater(ABC):
    """Abstract updater — applies changes to a document file."""

    name: str = "abstract"

    def __init__(self, options: dict[str, Any] | None = None) -> None:
        self.options = options or {}

    @abstractmethod
    def apply(
        self,
        path: Path,
        snapshot: ProjectSnapshot,
        docs: dict[str, Any],
    ) -> UpdateResult:
        """Apply updates to the document.

        Args:
            path: Path to the document file
            snapshot: Project snapshot with git state
            docs: Dictionary containing generated docs (readme, changelog_entries,
                todo_completed, todo_new, summary)

        Returns:
            UpdateResult indicating if the file was changed
        """
