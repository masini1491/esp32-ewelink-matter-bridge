#!/usr/bin/env python3
"""Fail-fast check for the compile probe's pinned Matter OTA metadata."""

import re
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: verify_compile_probe_metadata.py <CMakeLists.txt>", file=sys.stderr)
        return 2
    text = Path(sys.argv[1]).read_text(encoding="utf-8")
    version = re.search(r"(?m)^\s*set\(PROJECT_VER\s+\"([^\"]*)\"\s*\)", text)
    number = re.search(r"(?m)^\s*set\(PROJECT_VER_NUMBER\s+([^\s\)]+)\s*\)", text)
    if not version or not version.group(1):
        print("missing or empty PROJECT_VER in compile-probe CMakeLists.txt", file=sys.stderr)
        return 1
    if not number:
        print("missing PROJECT_VER_NUMBER in compile-probe CMakeLists.txt", file=sys.stderr)
        return 1
    if not re.fullmatch(r"[0-9]+", number.group(1)):
        print("PROJECT_VER_NUMBER must be a numeric value", file=sys.stderr)
        return 1
    print(f"compile-probe metadata valid: PROJECT_VER={version.group(1)} PROJECT_VER_NUMBER={number.group(1)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
