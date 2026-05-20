#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0

"""Validate SPDX headers on Python source files."""

from __future__ import annotations

import pathlib
import sys
from typing import Iterable, List

REQUIRED_HEADER = "SPDX-License-Identifier: Apache-2.0"

# Keep the check focused on production source trees.
ROOTS: List[pathlib.Path] = [
    pathlib.Path("purviewcli"),
    pathlib.Path("tools") / "PurviewMCPServer",
]

EXCLUDED_PARTS = {
    "__pycache__",
    ".venv",
    "build",
    "dist",
    "site",
}


def is_excluded(path: pathlib.Path) -> bool:
    return any(part in EXCLUDED_PARTS for part in path.parts)


def iter_python_files() -> Iterable[pathlib.Path]:
    for root in ROOTS:
        if not root.exists():
            continue
        for file_path in root.rglob("*.py"):
            if not is_excluded(file_path):
                yield file_path


def has_required_header(file_path: pathlib.Path) -> bool:
    with file_path.open("r", encoding="utf-8", errors="ignore") as handle:
        head = "\n".join([handle.readline() for _ in range(6)])
    return REQUIRED_HEADER in head


def main() -> int:
    missing: List[pathlib.Path] = []
    checked = 0

    for file_path in iter_python_files():
        checked += 1
        if not has_required_header(file_path):
            missing.append(file_path)

    if missing:
        print("[X] Missing SPDX header in the following files:")
        for path in missing:
            print(f" - {path.as_posix()}")
        print(f"\nFAILED Checked {checked} files, {len(missing)} missing header(s).")
        return 1

    print(f"[OK] SPDX headers verified for {checked} Python files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
