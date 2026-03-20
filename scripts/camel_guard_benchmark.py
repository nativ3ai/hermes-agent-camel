#!/usr/bin/env python3
"""Run the CaMeL on/off benchmark and optionally write the markdown report."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agent.camel_benchmark import DOC_PATH, render_json, render_markdown, run_policy_comparison, write_default_fixtures


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare Hermes runtime behavior with CaMeL off vs on.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of markdown.")
    parser.add_argument("--write-doc", action="store_true", help=f"Write the markdown report to {DOC_PATH}.")
    args = parser.parse_args()

    write_default_fixtures()
    outcomes = run_policy_comparison()

    if args.write_doc:
        DOC_PATH.write_text(render_markdown(outcomes), encoding="utf-8")

    if args.json:
        print(render_json(outcomes))
    else:
        print(render_markdown(outcomes))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
