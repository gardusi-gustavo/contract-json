#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--root", default=".")
    root = Path(ap.parse_args().root)
    files = sorted((root / "schemas").rglob("*.json"))
    if not files:
        print("no schemas", file=sys.stderr); return 1
    for p in files:
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"{p}: {exc}", file=sys.stderr); return 1
        if not isinstance(data, dict) or not (data.get("$schema") or data.get("$ref") or data.get("type")):
            print(f"{p}: not a schema", file=sys.stderr); return 1
    print(f"json schema validation ok ({len(files)} files)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
