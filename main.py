#!/usr/bin/env python3
"""Entry point of this site repository (thin wrapper around the wikibase-static package).

    python main.py                      all steps in order (from-csv, load, build, search, rdf, sparql)
    python main.py --strict             the same, but any WARN line (a dead link, a model rule) is an error
    python main.py --strict check-crm   SHACL check: every class reaches the CIDOC CRM (after the default run; needs wikibase-static 0.8.0)
    python main.py csv-fmt              bring the tables in data/csv/ into canonical form (--check: only report)
    python main.py --list               print the steps and exit

The model is kept in data/csv/ (four tables and idmap.csv). ``tools/import_pack.py`` made them once from the
chublets.software Wikibase Starter Pack; from now on they are edited. Everything else is done by the installed
package ``wikibase-static`` (0.6.0 or later); this file only points it at this repository (WBS_ROOT) and starts
the steps. It will be replaced by the command line of the package once the template repository exists
(PRIMER.md of wikibase-static, S9). Any further arguments are passed to the step.

``--strict`` is what the GitHub workflow runs (.github/workflows/site.yml): the steps write ``WARN: ...``
lines for problems and this wrapper turns them into exit code 1, as the package's own main.py does.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# (name, module, in the default run). csv-fmt is a verb: it rewrites the tables, so it never runs by itself.
STEPS = [
    ("csv-fmt", "step_csv_fmt", False),
    ("from-csv", "step_from_csv", True),
    ("load", "step_load", True),
    ("build", "step_build", True),
    ("search", "step_search", True),
    ("rdf", "step_rdf", True),
    ("sparql", "step_sparql", True),
    ("check-crm", "step_check_crm", False),
]


def run(module: str, extra: list[str]) -> tuple[int, int]:
    """Run one step, pass its output through line by line; returns (exit code, number of WARN lines)."""
    env = dict(os.environ, WBS_ROOT=str(ROOT), PYTHONIOENCODING="utf-8")
    proc = subprocess.Popen(
        [sys.executable, "-m", f"wikibase_static.{module}", *extra], cwd=ROOT, env=env,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace",
    )
    warnings = 0
    assert proc.stdout is not None
    for raw in proc.stdout:
        line = raw.rstrip("\n")
        if line.lstrip().startswith("WARN"):
            warnings += 1
        print(line, flush=True)
    return proc.wait(), warnings


def main(argv: list[str]) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    strict = argv[:1] == ["--strict"]
    if strict:
        argv = argv[1:]
    if argv[:1] == ["--list"]:
        for name, _module, default in STEPS:
            print(f"{name:9} {'default' if default else 'verb'}")
        return 0
    names = [name for name, _m, _d in STEPS]
    if argv and argv[0] in names:
        steps = [(argv[0], next(m for n, m, _d in STEPS if n == argv[0]), argv[1:])]
    elif argv:
        print(f"unknown step {argv[0]!r}; use --list", file=sys.stderr)
        return 2
    else:
        steps = [(name, module, []) for name, module, default in STEPS if default]

    total_warnings = 0
    for name, module, extra in steps:
        print(f"[{name}]", flush=True)
        code, warnings = run(module, extra)
        total_warnings += warnings
        if code:
            return code
    if strict and total_warnings:
        print(f"--strict: {total_warnings} warning(s) treated as errors", flush=True)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
