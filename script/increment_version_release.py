#!/usr/bin/env python3
"""Increment release version and set to next development cycle in setup.py.

X.Y.Z (or X.Y.Z.devN) -> X.Y.(Z+1).dev0
"""

from __future__ import annotations

from pathlib import Path
import re


def main() -> None:
    """Increment release version and set to next development cycle in setup.py."""
    project_root = Path(__file__).resolve().parents[1]
    setup_path = project_root / "setup.py"
    contents = setup_path.read_text(encoding="utf-8")

    match = re.search(r'version="([^"]+)"', contents)
    if not match:
        raise SystemExit("version field not found in setup.py")

    version = match.group(1)
    base = re.sub(r"\.dev\d*$", "", version)
    base_match = re.fullmatch(r"^(\d+)\.(\d+)\.(\d+)$", base)
    if not base_match:
        raise SystemExit(f"Unexpected base version format: {base}")

    major, minor, patch = base_match.groups()
    new_version = f"{major}.{minor}.{int(patch) + 1}.dev0"

    new_contents = contents.replace(
        f'version="{version}"', f'version="{new_version}"', 1
    )
    setup_path.write_text(new_contents, encoding="utf-8")
    print(f"Updated version to {new_version}")


if __name__ == "__main__":
    main()
