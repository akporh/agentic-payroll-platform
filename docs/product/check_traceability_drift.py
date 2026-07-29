#!/usr/bin/env python3
"""Traceability drift detector — warns when code ships with no story_ref.

WHY THIS EXISTS
---------------
`docs/product/ID-ALLOCATION.md` claims a strong property: *an item absent from
this table is an item no known evidence records.* That claim is only as true as
the last sprint that closed properly.

The sprint workflow's only enforcement point is `/retro`'s Close Gate, which
hard-stops on an unresolved `story_ref` — but it fires solely when a sprint is
formally closed. Ad-hoc work done without a sprint workspace, or in a workspace
that is never closed, is invisible to it. That is not hypothetical: D-026
records three sprints found missing from the inventory after its 2026-07-15
horizon, and `dev-levy-rule-pct` ran `roadmap` and `pm` retroactively.

So untracked work does not merely go unrecorded — it makes the registry assert
something false. This script narrows the window in which that can happen
silently.

WHAT IT DOES
------------
At pre-push time it looks at the commits about to leave the machine, and for
any that touch application code it asks a single question: *is this work
attributable to a story?* Work is attributable if the commit message names a
`STORY-<nnnn>`, or if a sprint workspace is currently active and declares
`story_refs`.

WHAT IT DELIBERATELY DOES NOT DO
--------------------------------
It never blocks. `check()` always reports; `main()` always exits 0. A gate here
would be bypassed with `--no-verify` on the first genuine emergency and would
then be decoration — worse than nothing, because it would look like a control.
This warns at the last moment you still have full context on what you just did.

It is also deliberately NOT part of `validate_registry.py`. That script asserts
`docs/product/` is internally consistent and is deterministic — same files in,
same answer out. Reading git state would make its result depend on branch
position and upstream config, so a PASS would stop meaning what it means today.
Two scripts, two claims, two independent failure modes. (`roadmap-split` DEC-06.)
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent

# Paths whose change implies delivered product work. Docs, tests and the sprint
# machinery are excluded: a docs-only or test-only commit is not the drift this
# is looking for, and flagging it would train the reader to ignore the warning.
CODE_PREFIXES = ("backend/", "frontend/src/", "migrations/versions/")

STORY_RE = re.compile(r"STORY-\d{4}")


def _git(*args: str) -> str:
    """Run a git command, returning stripped stdout ('' on any failure)."""
    try:
        out = subprocess.run(
            ["git", *args], cwd=REPO, capture_output=True, text=True, timeout=15
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return out.stdout.strip() if out.returncode == 0 else ""


def _commit_range() -> str | None:
    """The commits about to be pushed, as a git range.

    Prefers the tracked upstream. Falls back to origin/<branch>, then to the
    merge-base with the default branch. Returns None when no sensible range
    exists (a fresh branch with no remote counterpart), in which case the
    caller skips silently rather than flagging every commit in history.
    """
    upstream = _git("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}")
    if upstream:
        return f"{upstream}..HEAD"

    branch = _git("rev-parse", "--abbrev-ref", "HEAD")
    if branch and _git("rev-parse", "--verify", f"origin/{branch}"):
        return f"origin/{branch}..HEAD"

    for base in ("origin/uat", "origin/main"):
        if _git("rev-parse", "--verify", base):
            mb = _git("merge-base", base, "HEAD")
            if mb:
                return f"{mb}..HEAD"
    return None


def _active_sprint_story_refs() -> tuple[str | None, list[str]]:
    """The active sprint name and the story_refs its state.md declares."""
    current = REPO / "docs" / "sprints" / "CURRENT.md"
    if not current.exists():
        return None, []

    m = re.search(r"active_sprints:\s*\[([^\]]*)\]", current.read_text(encoding="utf-8"))
    if not m or not m.group(1).strip():
        return None, []

    sprint = m.group(1).split(",")[0].strip().strip("'\"")
    if not sprint:
        return None, []

    state = REPO / "docs" / "sprints" / sprint / "state.md"
    refs = STORY_RE.findall(state.read_text(encoding="utf-8")) if state.exists() else []
    return sprint, sorted(set(refs))


def check() -> list[str]:
    """Return one warning line per unattributable commit."""
    rng = _commit_range()
    if rng is None:
        return []

    log = _git("log", "--format=%H%x1f%s%x1f%b%x1e", rng)
    if not log:
        return []

    sprint, sprint_refs = _active_sprint_story_refs()
    warnings: list[str] = []

    for entry in log.split("\x1e"):
        entry = entry.strip("\n")
        if not entry:
            continue
        parts = entry.split("\x1f")
        if len(parts) < 3:
            continue
        sha, subject, body = parts[0], parts[1], parts[2]

        files = _git("show", "--name-only", "--format=", sha)
        touched = [
            f for f in files.splitlines()
            if f.strip().startswith(CODE_PREFIXES)
        ]
        if not touched:
            continue

        # Attributable if the commit says so itself, or an active sprint does.
        if STORY_RE.search(f"{subject}\n{body}") or sprint_refs:
            continue

        detail = f"{len(touched)} code file(s)"
        warnings.append(f"{sha[:8]}  {subject[:64]}  ({detail})")

    if warnings and sprint and not sprint_refs:
        warnings.append(
            f"NOTE: sprint '{sprint}' is active but its state.md declares no story_refs."
        )
    return warnings


def main() -> int:
    warnings = check()
    if not warnings:
        return 0

    print("")
    print("  traceability drift — code is being pushed with no story_ref:")
    print("")
    for w in warnings:
        print(f"    {w}")
    print("")
    print("  docs/product/ claims that an item absent from it does not exist.")
    print("  Un-tracked work does not just go unrecorded — it makes that claim false.")
    print("")
    print("  To resolve: run /pm to allocate a STORY-<nnnn>, or name an existing")
    print("  one in the commit message. This is a warning, not a gate — the push")
    print("  continues either way.")
    print("")
    return 0


if __name__ == "__main__":
    sys.exit(main())
