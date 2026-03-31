from __future__ import annotations

from pathlib import Path
import re


def test_gitignore_covers_cache_and_tmp_artifacts() -> None:
    root = Path(__file__).resolve().parents[1]
    contents = (root / ".gitignore").read_text()
    assert "__pycache__/" in contents
    assert ".pytest_cache/" in contents
    assert "build/" in contents
    assert "dist/" in contents
    assert "tmp/" in contents
    assert "*.egg-info/" in contents


def test_tmp_directory_does_not_ship_raw_archives() -> None:
    root = Path(__file__).resolve().parents[1]
    archives = list((root / "tmp").rglob("*.zip")) if (root / "tmp").exists() else []
    assert archives == []


def test_docs_avoid_absolute_local_paths() -> None:
    root = Path(__file__).resolve().parents[1]
    absolute_path_pattern = re.compile(r"[A-Za-z]:\\\\|/Users/|/home/")
    text_files = [root / "README.md", *sorted((root / "docs").rglob("*.md"))]
    for path in text_files:
        contents = path.read_text()
        assert not absolute_path_pattern.search(contents), path
