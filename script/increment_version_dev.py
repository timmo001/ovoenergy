#!/usr/bin/env python3
"""Increment development version in setup.py.

If version is X.Y.Z.devN -> X.Y.Z.dev(N+1)
If version is X.Y.Z -> X.Y.(Z+1).dev0
"""

from __future__ import annotations

from pathlib import Path
import re


def main() -> None:
    """Increment development version in setup.py."""
    project_root = Path(__file__).resolve().parents[1]
    setup_path = project_root / "setup.py"
    contents = setup_path.read_text(encoding="utf-8")

    match = re.search(r'version="([^"]+)"', contents)
    if not match:
        raise SystemExit("version field not found in setup.py")

    version = match.group(1)
    dev_match = re.search(r"^(\d+)\.(\d+)\.(\d+)(?:\.dev(\d+))?$", version)
    if not dev_match:
        raise SystemExit(f"Unexpected version format: {version}")

    major, minor, patch, dev = dev_match.groups()
    if dev is None:
        new_version = f"{major}.{minor}.{int(patch) + 1}.dev0"
    else:
        new_version = f"{major}.{minor}.{patch}.dev{int(dev) + 1}"

    new_contents = contents.replace(
        f'version="{version}"', f'version="{new_version}"', 1
    )
    setup_path.write_text(new_contents, encoding="utf-8")
    print(f"Updated version to {new_version}")


if __name__ == "__main__":
    main()
