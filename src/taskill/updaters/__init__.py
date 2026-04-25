"""Document updaters — apply GeneratedDocs to README/CHANGELOG/TODO."""
from taskill.updaters.changelog import update_changelog
from taskill.updaters.todo import update_todo
from taskill.updaters.readme import update_readme

__all__ = ["update_changelog", "update_todo", "update_readme"]
