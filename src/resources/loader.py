"""
Content loading and indexing utilities.

Scans the /content directory and exposes its contents as MCP resources
and as searchable text for tools.
"""

from __future__ import annotations

import re
from pathlib import Path

from mcp import types

# File extensions treated as plain text
TEXT_EXTENSIONS = {".md", ".txt", ".tex", ".csv", ".json", ".yaml", ".yml"}


class ContentLoader:
    def __init__(self, content_root: Path):
        self.root = content_root
        self._index: dict[str, Path] = {}
        self._build_index()

    # ------------------------------------------------------------------
    # Internal

    def _build_index(self) -> None:
        """Walk content root and index all readable files by URI key."""
        self._index.clear()
        if not self.root.exists():
            return
        for path in self.root.rglob("*"):
            if path.is_file() and path.suffix in TEXT_EXTENSIONS:
                # URI: content://<relative-posix-path>
                key = "content://" + path.relative_to(self.root).as_posix()
                self._index[key] = path

    def _read_text(self, path: Path) -> str:
        return path.read_text(encoding="utf-8", errors="replace")

    # ------------------------------------------------------------------
    # MCP resource interface

    def list_resources(self) -> list[types.Resource]:
        self._build_index()  # refresh on each list call
        resources = []
        for uri, path in sorted(self._index.items()):
            resources.append(
                types.Resource(
                    uri=uri,  # type: ignore[arg-type]
                    name=path.name,
                    description=f"Content file: {path.relative_to(self.root).as_posix()}",
                    mimeType="text/markdown" if path.suffix == ".md" else "text/plain",
                )
            )
        return resources

    def read_resource(self, uri: str) -> str:
        self._build_index()
        path = self._index.get(uri)
        if path is None:
            raise FileNotFoundError(f"Resource not found: {uri}")
        return self._read_text(path)

    # ------------------------------------------------------------------
    # Search interface (used by tools)

    def search(self, query: str, section: str | None = None) -> list[dict]:
        """
        Simple full-text search across indexed content.

        Args:
            query: Search terms (case-insensitive).
            section: Optional subfolder to restrict search (e.g. "exams", "notes").

        Returns:
            List of dicts with keys: uri, path, snippet.
        """
        self._build_index()
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        results = []
        for uri, path in self._index.items():
            if section and not path.relative_to(self.root).parts[0] == section:
                continue
            text = self._read_text(path)
            match = pattern.search(text)
            if match:
                start = max(0, match.start() - 150)
                end = min(len(text), match.end() + 150)
                snippet = "..." + text[start:end].strip() + "..."
                results.append({"uri": uri, "path": str(path), "snippet": snippet})
        return results

    def get_section(self, section: str) -> list[dict]:
        """Return all files from a named content subfolder."""
        self._build_index()
        results = []
        for uri, path in self._index.items():
            parts = path.relative_to(self.root).parts
            if parts and parts[0] == section:
                results.append({"uri": uri, "name": path.name, "text": self._read_text(path)})
        return results
