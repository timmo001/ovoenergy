#!/usr/bin/env python3
"""Print the current package version from setup.py.

This script reads the version string from the repository's setup.py and prints
only the version to stdout.
"""

from __future__ import annotations

from pathlib import Path
import re


def main() -> None:
    """Print the current package version from setup.py."""
    project_root = Path(__file__).resolve().parents[1]
    setup_path = project_root / "setup.py"
    setup_contents = setup_path.read_text(encoding="utf-8")
    match = re.search(r'version="([^"]+)"', setup_contents)
    if not match:
        raise SystemExit("version field not found in setup.py")
    print(match.group(1))


if __name__ == "__main__":
    main()
