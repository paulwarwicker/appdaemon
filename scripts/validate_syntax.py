#!/usr/bin/env python3
"""Validate syntax of Python (and optionally YAML) files under a directory.

Usage:
  python validate_syntax.py [path]

Exit code: 0 if all files valid (or skipped), non-zero if any syntax errors found.
"""
from __future__ import annotations
import argparse
import os
import sys
import py_compile
import traceback


def validate_python_file(path: str) -> tuple[bool, str | None]:
    try:
        py_compile.compile(path, doraise=True)
        return True, None
    except py_compile.PyCompileError as e:
        return False, str(e)
    except Exception:
        return False, traceback.format_exc()


def validate_yaml_file(path: str) -> tuple[bool | None, str | None]:
    try:
        import yaml
    except Exception:
        return None, "PyYAML not installed"
    try:
        with open(path, "r", encoding="utf-8") as f:
            yaml.safe_load(f)
        return True, None
    except Exception as e:
        return False, str(e)


def iter_files(root: str, exts: set[str]):
    for dirpath, _, filenames in os.walk(root):
        # skip any directory named .ignore
        parts = dirpath.split(os.sep)
        if ".ignore" in parts:
            continue
        for fn in filenames:
            if any(fn.lower().endswith(ext) for ext in exts):
                yield os.path.join(dirpath, fn)


def main() -> int:
    p = argparse.ArgumentParser(description="Validate syntax of files in a directory")
    p.add_argument("path", nargs="?", default=".", help="Directory to scan (default: current dir)")
    p.add_argument("--extensions", default="py,yml,yaml",
                   help="Comma-separated extensions to check (default: py,yml,yaml)")
    p.add_argument("--no-yaml", action="store_true", help="Skip YAML checks even if yaml files present")
    args = p.parse_args()

    root = os.path.abspath(args.path)
    exts = {"." + e.strip().lstrip(".") for e in args.extensions.split(",") if e.strip()}

    if not os.path.exists(root):
        print(f"Path does not exist: {root}", file=sys.stderr)
        return 2

    errors: list[tuple[str, str]] = []
    skipped_yaml = False

    for fp in iter_files(root, exts):
        if fp.lower().endswith(".py"):
            ok, msg = validate_python_file(fp)
            if not ok:
                errors.append((fp, msg or "Unknown Python syntax error"))
            else:
                print(f"OK: {fp}")
        elif fp.lower().endswith(('.yml', '.yaml')):
            if args.no_yaml:
                print(f"SKIP YAML (disabled): {fp}")
                continue
            ok, msg = validate_yaml_file(fp)
            if ok is True:
                print(f"OK YAML: {fp}")
            elif ok is None:
                skipped_yaml = True
                print(f"SKIP YAML (PyYAML missing): {fp}")
            else:
                errors.append((fp, msg or "Unknown YAML parse error"))
        else:
            # other extensions listed; treat as text and skip
            print(f"SKIP (unhandled ext): {fp}")

    if errors:
        print("\nSyntax errors found:")
        for fp, msg in errors:
            print(f"- {fp}: {msg}")
        return 1

    if skipped_yaml:
        print("\nAll checked files OK, but YAML checks were skipped (PyYAML not installed).")
        return 0

    print("\nAll checked files OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
