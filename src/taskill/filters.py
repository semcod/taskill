"""Project filtering utilities for taskill.

Detects project types/languages based on manifest files and directory structure.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

# Language to manifest file mapping
LANGUAGE_MANIFESTS: dict[str, list[str]] = {
    "python": ["pyproject.toml", "setup.py", "setup.cfg", "requirements.txt", "Pipfile"],
    "javascript": ["package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml"],
    "typescript": ["package.json", "tsconfig.json"],
    "rust": ["Cargo.toml", "Cargo.lock"],
    "go": ["go.mod", "go.sum"],
    "java": ["pom.xml", "build.gradle", "build.gradle.kts"],
    "kotlin": ["build.gradle.kts", "pom.xml"],
    "csharp": [".csproj", ".sln"],
    "cpp": ["CMakeLists.txt", "Makefile", "configure.ac", "meson.build"],
    "c": ["Makefile", "CMakeLists.txt", "configure.ac"],
    "ruby": ["Gemfile", ".gemspec", "Rakefile"],
    "php": ["composer.json", "composer.lock"],
    "swift": ["Package.swift", ".xcodeproj"],
    "elixir": ["mix.exs"],
    "haskell": ["package.yaml", "*.cabal", "stack.yaml"],
    "scala": ["build.sbt", "pom.xml"],
    "dart": ["pubspec.yaml"],
    "flutter": ["pubspec.yaml"],
}

# Manifest file to project type mapping (for --manifest filter)
MANIFEST_PROJECT_TYPES: dict[str, str] = {
    "pyproject.toml": "python",
    "setup.py": "python",
    "setup.cfg": "python",
    "requirements.txt": "python",
    "Pipfile": "python",
    "poetry.lock": "python",
    "package.json": "javascript",
    "package-lock.json": "javascript",
    "yarn.lock": "javascript",
    "pnpm-lock.yaml": "javascript",
    "tsconfig.json": "typescript",
    "Cargo.toml": "rust",
    "go.mod": "go",
    "pom.xml": "java",
    "build.gradle": "java/kotlin",
    "build.gradle.kts": "kotlin",
    "CMakeLists.txt": "cpp",
    "Makefile": "c/cpp",
    "Gemfile": "ruby",
    "composer.json": "php",
    "Package.swift": "swift",
    "mix.exs": "elixir",
    "pubspec.yaml": "dart/flutter",
}


@dataclass
class ProjectInfo:
    """Detected project information."""
    path: Path
    name: str
    detected_languages: list[str]
    manifests_found: list[str]


def detect_project_languages(path: Path) -> list[str]:
    """Detect programming languages used in a project directory.

    Args:
        path: Project root directory

    Returns:
        List of detected language names (sorted by confidence, most likely first)
    """
    detected: list[str] = []
    manifest_counts: dict[str, int] = {}

    for lang, manifests in LANGUAGE_MANIFESTS.items():
        count = 0
        for manifest in manifests:
            # Handle wildcards (e.g., "*.cabal")
            if manifest.startswith("*."):
                ext = manifest[1:]  # .cabal
                if any(f.suffix == ext for f in path.iterdir() if f.is_file()):
                    count += 1
            elif (path / manifest).exists():
                count += 1

        if count > 0:
            manifest_counts[lang] = count

    # Sort by number of manifest matches (descending), then alphabetically
    detected = sorted(manifest_counts.keys(), key=lambda x: (-manifest_counts[x], x))
    return detected


def find_manifests(path: Path) -> list[str]:
    """Find all manifest files in a project directory.

    Args:
        path: Project root directory

    Returns:
        List of manifest filenames found
    """
    found: list[str] = []
    all_manifests = set()
    for manifests in LANGUAGE_MANIFESTS.values():
        all_manifests.update(manifests)

    for manifest in all_manifests:
        if manifest.startswith("*."):
            ext = manifest[1:]
            for f in path.iterdir():
                if f.is_file() and f.suffix == ext:
                    found.append(f.name)
        elif (path / manifest).exists():
            found.append(manifest)

    return sorted(found)


def analyze_project(path: Path) -> ProjectInfo:
    """Analyze a project directory and detect its characteristics.

    Args:
        path: Project root directory

    Returns:
        ProjectInfo with detected languages and manifests
    """
    path = Path(path).resolve()
    return ProjectInfo(
        path=path,
        name=path.name,
        detected_languages=detect_project_languages(path),
        manifests_found=find_manifests(path),
    )


def create_manifest_filter(manifests: list[str]) -> Callable[[Path], bool]:
    """Create a filter function that checks for required manifest files.

    Args:
        manifests: List of manifest filenames to require

    Returns:
        Filter function that returns True if all manifests exist
    """
    def _filter(path: Path) -> bool:
        for manifest in manifests:
            if manifest.startswith("*."):
                ext = manifest[1:]
                if not any(f.suffix == ext for f in path.iterdir() if f.is_file()):
                    return False
            elif not (path / manifest).exists():
                return False
        return True
    return _filter


def create_language_filter(languages: list[str]) -> Callable[[Path], bool]:
    """Create a filter function that checks for detected languages.

    Args:
        languages: List of language names to match (case-insensitive)

    Returns:
        Filter function that returns True if any language matches
    """
    lang_lower = [lang.lower() for lang in languages]

    def _filter(path: Path) -> bool:
        detected = detect_project_languages(path)
        detected_lower = [d.lower() for d in detected]
        return any(lang in detected_lower for lang in lang_lower)
    return _filter


def create_extension_filter(extensions: list[str]) -> Callable[[Path], bool]:
    """Create a filter function that checks for file extensions.

    Args:
        extensions: List of file extensions (with or without dot)

    Returns:
        Filter function that returns True if any file with extension exists
    """
    # Normalize extensions (ensure they start with .)
    exts = [ext if ext.startswith(".") else f".{ext}" for ext in extensions]

    def _filter(path: Path) -> bool:
        for file in path.rglob("*"):
            if file.is_file() and file.suffix in exts:
                return True
        return False
    return _filter


def create_name_filter(patterns: list[str]) -> Callable[[Path], bool]:
    """Create a filter function that checks directory name.

    Args:
        patterns: List of name substrings to match (case-insensitive)

    Returns:
        Filter function that returns True if any pattern is in the name
    """
    patterns_lower = [p.lower() for p in patterns]

    def _filter(path: Path) -> bool:
        name_lower = path.name.lower()
        return any(pattern in name_lower for pattern in patterns_lower)
    return _filter
