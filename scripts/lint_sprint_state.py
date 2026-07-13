#!/usr/bin/env python3
"""
Mechanical validator for docs/sprints/<id>/ workspaces (ICM sprint workflow,
Changeset 7 of docs/diagnostics/2026-07-12-nonlinear-icm-sprint-workflow-
implementation-plan.md).

Read-only. Never modifies state.md, decisions.md, STAGE-REGISTRY.md, or
WORKFLOW.md. Standalone script — no ~/.claude/settings.json hook and no CI
wiring are added by this changeset (per D8: script-first).

Usage:
    python scripts/lint_sprint_state.py                # resolve active sprint from CURRENT.md
    python scripts/lint_sprint_state.py <workspace-dir>  # validate an explicit workspace

Exit code 0 on PASS, non-zero on any detected defect. All defects are
collected and printed in one run — the script never stops at the first
failure.

---------------------------------------------------------------------------
Parsing assumptions (explicit, by design — this is NOT a general YAML
parser; it is a narrow, documented reader for exactly the two shapes this
project's `docs/sprints/*/state.md` and `decisions.md` files use)
---------------------------------------------------------------------------

PyYAML is not a dependency of this project (grep requirements.txt) even
though it happens to be installed on this development machine. Per this
changeset's instructions, no new dependency is added; the subset actually
used in these files is small enough to read reliably with the standard
library alone. Supported subset:

  - a single ```yaml fenced code block per file
  - flat `key: value` fields at a single, consistent indent level within
    each block (a "stage" block in state.md, a "decision" block in
    decisions.md)
  - inline lists: `key: [a, b, c]`
  - block-style lists: `key:` followed by more-indented `- item` lines
    (used by this project's `waiting_for:` field)
  - folded scalars: `key: >` followed by more-indented lines, joined with
    single spaces until the indentation returns to the field level (a
    narrow reading of YAML's `>` folding indicator — blank lines inside a
    folded block are not treated as paragraph breaks, since none of this
    project's folded fields currently contain one)
  - bare continuation: a `key: value` line followed by more-indented lines
    that are themselves not `key: value`/list-item lines is treated as a
    continuation of that scalar, joined with spaces (this project's
    `reference:` field in decisions.md wraps this way without an explicit
    `>` marker)
  - state.md: `stages:` maps to a nested mapping; each entry is
    `  <stage_id>:` (2-space indent) followed by that stage's fields at
    4-space indent
  - decisions.md: a top-level list of mappings, `- id: <value>` (0-space
    indent, "- " marker) followed by that decision's remaining fields at
    2-space indent

NOT supported (and not present in any current sprint-workspace file):
quoted/escaped keys, anchors/aliases, multi-document streams, `|` literal
block scalars, flow mappings `{...}`, YAML tags, blank lines inside a
folded scalar.

If a file's fenced block cannot be read under this subset, the script
reports E005 (UNPARSEABLE_YAML_BLOCK) with the offending file and line
rather than guessing.

---------------------------------------------------------------------------
Known limitations (documented, not silently ignored)
---------------------------------------------------------------------------

- `compensating_control` is optional per WORKFLOW.md's own schema ("what
  covers the risk instead, if anything"); WORKFLOW.md does not define a
  machine-checkable rule for when it becomes mandatory ("where required"
  is a judgement call). This script does not attempt to infer that
  judgement and never flags a missing `compensating_control`.
- "complete stage with required evidence missing" (checklist item 8) is
  enforced only for the one stage this project's own convention and D7
  make unambiguous: `test` (mandatory evidence-writer per D7). No other
  stage has a machine-readable "evidence is mandatory here" signal in
  STAGE-REGISTRY.md, so this script does not invent one for other stages.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

VALID_STATUSES = {
    "not-started", "eligible", "active", "blocked",
    "complete", "skipped", "not-applicable", "needs-rework",
}
TERMINAL_STATUSES = {"complete", "skipped", "not-applicable"}
DECISION_REQUIRED_STATUSES = {"skipped", "not-applicable", "needs-rework"}
VALID_DECISION_TYPES = {
    "skip", "not-applicable", "activate", "allow-parallel", "rework", "block",
}
# Maps a stage status that requires a decision to the decision_type(s) that
# legitimately explain it, per WORKFLOW.md's "Recording HITL decisions" section.
STATUS_TO_EXPECTED_DECISION_TYPES = {
    "skipped": {"skip"},
    "not-applicable": {"not-applicable"},
    "needs-rework": {"rework"},
}
# Stages where this project's own convention makes "evidence on completion"
# unambiguous (see module docstring, Known limitations).
MANDATORY_EVIDENCE_ON_COMPLETE = {"test"}

_KEY_LINE_RE = re.compile(r"^[A-Za-z_][\w\- ]*:( |$)")


@dataclass
class Defect:
    code: str
    message: str
    file: str = ""
    stage: str = ""
    decision_id: str = ""

    def render(self) -> str:
        loc = []
        if self.file:
            loc.append(self.file)
        if self.stage:
            loc.append(f"stage={self.stage}")
        if self.decision_id:
            loc.append(f"decision={self.decision_id}")
        loc_str = f" [{', '.join(loc)}]" if loc else ""
        return f"{self.code}{loc_str}: {self.message}"


class LintError(Exception):
    """Fatal — cannot proceed with validation at all."""


# ---------------------------------------------------------------------------
# Minimal fenced-YAML reader (see module docstring for the supported subset)
# ---------------------------------------------------------------------------

def _fenced_yaml_lines(path: Path) -> list[tuple[int, str]]:
    text = path.read_text()
    m = re.search(r"```yaml\n(.*?)```", text, re.S)
    if not m:
        raise LintError(f"{path}: no ```yaml fenced block found")
    out = []
    for raw in m.group(1).split("\n"):
        if raw.strip() == "":
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        out.append((indent, raw.strip()))
    return out


def _parse_fields(lines: list[tuple[int, str]]) -> tuple[dict, list[str]]:
    """Parse a flat run of `key: value` lines (with folded/continuation
    support) that all belong to one stage or one decision entry. Returns
    (fields, duplicate_keys)."""
    if not lines:
        return {}, []
    field_indent = lines[0][0]
    fields: dict = {}
    dups: list[str] = []
    i = 0
    while i < len(lines):
        indent, text = lines[i]
        if indent != field_indent:
            # Unexpected indent jump at field level — not present in any
            # current file; skip defensively rather than mis-parse.
            i += 1
            continue
        key, _, rest = text.partition(":")
        key = key.strip()
        rest = rest.strip()
        i += 1
        if rest == ">":
            parts = []
            while i < len(lines) and lines[i][0] > field_indent:
                parts.append(lines[i][1])
                i += 1
            value: object = " ".join(parts)
        elif rest.startswith("[") and rest.endswith("]"):
            inner = rest[1:-1].strip()
            value = [v.strip() for v in inner.split(",")] if inner else []
        elif rest == "" and i < len(lines) and lines[i][0] > field_indent and lines[i][1].startswith("- "):
            # Block-style list: `key:` followed by more-indented `- item` lines.
            items = []
            list_indent = lines[i][0]
            while i < len(lines) and lines[i][0] == list_indent and lines[i][1].startswith("- "):
                items.append(lines[i][1][2:].strip())
                i += 1
            value = items
        else:
            parts = [rest]
            while i < len(lines) and lines[i][0] > field_indent:
                nxt_indent, nxt_text = lines[i]
                if _KEY_LINE_RE.match(nxt_text) or nxt_text.startswith("- "):
                    break
                parts.append(nxt_text)
                i += 1
            value = " ".join(p for p in parts if p)
        if key in fields:
            dups.append(key)
        fields[key] = value
    return fields, dups


def parse_state(path: Path) -> tuple[dict, dict[str, dict], list[str]]:
    """Returns (top_level_fields, {stage_id: fields}, duplicate_stage_ids)."""
    lines = _fenced_yaml_lines(path)
    try:
        stages_idx = next(i for i, (ind, t) in enumerate(lines) if ind == 0 and t == "stages:")
    except StopIteration:
        raise LintError(f"{path}: no top-level 'stages:' key found")
    top_fields, _ = _parse_fields(lines[:stages_idx])
    body = lines[stages_idx + 1:]
    stages: dict[str, dict] = {}
    dup_stage_ids: list[str] = []
    i = 0
    while i < len(body):
        indent, text = body[i]
        if indent != 2 or not text.endswith(":"):
            raise LintError(f"{path}: expected a 2-space-indented 'stage_id:' line, got {text!r}")
        stage_id = text[:-1].strip()
        i += 1
        field_lines = []
        while i < len(body) and body[i][0] > 2:
            field_lines.append(body[i])
            i += 1
        fields, _ = _parse_fields(field_lines)
        if stage_id in stages:
            dup_stage_ids.append(stage_id)
        stages[stage_id] = fields
    return top_fields, stages, dup_stage_ids


def parse_decisions(path: Path) -> tuple[list[dict], list[str]]:
    """Returns (decisions, duplicate_decision_ids)."""
    lines = _fenced_yaml_lines(path)
    decisions: list[dict] = []
    seen_ids: set[str] = set()
    dup_ids: list[str] = []
    i = 0
    while i < len(lines):
        indent, text = lines[i]
        if indent != 0 or not text.startswith("- "):
            raise LintError(f"{path}: expected a top-level '- id: ...' entry, got {text!r}")
        after = text[2:]
        key, _, rest = after.partition(":")
        if key.strip() != "id":
            raise LintError(f"{path}: expected '- id: <value>' as the first field of a decision entry, got {text!r}")
        entry_id = rest.strip()
        i += 1
        field_lines = []
        while i < len(lines) and lines[i][0] > 0:
            field_lines.append(lines[i])
            i += 1
        fields, _ = _parse_fields(field_lines)
        fields["id"] = entry_id
        if entry_id in seen_ids:
            dup_ids.append(entry_id)
        seen_ids.add(entry_id)
        decisions.append(fields)
    return decisions, dup_ids


def parse_registry(path: Path) -> tuple[list[str], dict[str, set[str]]]:
    """Returns (valid_stage_ids in file order, {stage_id: declared_compatible_stage_ids})."""
    text = path.read_text()
    headers = list(re.finditer(r"^## `([a-z0-9\-]+)`\s*$", text, re.M))
    if not headers:
        raise LintError(f"{path}: no '## `stage_id`' headers found")
    valid_ids = [h.group(1) for h in headers]
    compatible: dict[str, set[str]] = {sid: set() for sid in valid_ids}
    for idx, h in enumerate(headers):
        start = h.end()
        end = headers[idx + 1].start() if idx + 1 < len(headers) else len(text)
        block = text[start:end]
        row = re.search(r"\|\s*Parallel compatibility\s*\|\s*(.*?)\s*\|\s*$", block, re.M)
        if not row:
            continue
        cell = row.group(1).strip()
        m = re.fullmatch(r"`([a-z0-9\-]+)`", cell)
        if m and m.group(1) in valid_ids:
            compatible[h.group(1)].add(m.group(1))
    return valid_ids, compatible


# ---------------------------------------------------------------------------
# Sprint discovery
# ---------------------------------------------------------------------------

def resolve_workspace(explicit_path: str | None, sprints_root: Path) -> Path:
    if explicit_path:
        ws = Path(explicit_path)
        if not ws.is_dir():
            raise LintError(f"Workspace not found: {ws}")
        return ws
    current_md = sprints_root / "CURRENT.md"
    if not current_md.is_file():
        raise LintError(f"No CURRENT.md found at {current_md} and no workspace path given")
    lines = _fenced_yaml_lines(current_md)
    fields, _ = _parse_fields(lines)
    active = fields.get("active_sprints")
    if isinstance(active, str):
        # Not expected in the current file (list form is used), but handle
        # a bare scalar defensively rather than mis-parse.
        active = [active] if active else []
    if not active:
        raise LintError(f"No active sprint declared in {current_md} (active_sprints is empty)")
    if len(active) > 1:
        raise LintError(f"More than one active sprint declared in {current_md}: {active}")
    ws = sprints_root / active[0]
    if not ws.is_dir():
        raise LintError(f"Active sprint '{active[0]}' declared in {current_md} but {ws} does not exist")
    return ws


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate(workspace: Path) -> tuple[list[Defect], dict[str, dict], list[dict]]:
    defects: list[Defect] = []
    registry_path = workspace.parent / "STAGE-REGISTRY.md"
    if not registry_path.is_file():
        raise LintError(f"STAGE-REGISTRY.md not found at {registry_path}")
    valid_stage_ids, compatible = parse_registry(registry_path)
    valid_stage_id_set = set(valid_stage_ids)

    for name in ("CONTEXT.md", "state.md", "decisions.md"):
        if not (workspace / name).is_file():
            defects.append(Defect("E004", f"required file missing: {name}", file=str(workspace / name)))

    state_path = workspace / "state.md"
    decisions_path = workspace / "decisions.md"
    if not state_path.is_file() or not decisions_path.is_file():
        # Cannot proceed with stage/decision checks without both.
        return defects, {}, []

    top_fields, stages, dup_stage_ids = parse_state(state_path)
    decisions, dup_decision_ids = parse_decisions(decisions_path)

    for sid in dup_stage_ids:
        defects.append(Defect("E012", "duplicate stage entry in state.md", file=str(state_path), stage=sid))

    # --- Stage validation ---------------------------------------------------
    for sid in stages:
        if sid not in valid_stage_id_set:
            defects.append(Defect("E010", "stage ID not present in STAGE-REGISTRY.md", file=str(state_path), stage=sid))
    for sid in valid_stage_ids:
        if sid not in stages:
            defects.append(Defect("E011", "registered stage ID missing from state.md", file=str(state_path), stage=sid))

    # --- Status validation ---------------------------------------------------
    for sid, fields in stages.items():
        status = fields.get("status")
        if status not in VALID_STATUSES:
            defects.append(Defect("E020", f"invalid status value: {status!r}", file=str(state_path), stage=sid))

    # --- Decision integrity ---------------------------------------------------
    decisions_by_id: dict[str, dict] = {}
    for d in decisions:
        decisions_by_id.setdefault(d["id"], d)

    for did in dup_decision_ids:
        defects.append(Defect("E031", "duplicate decision ID in decisions.md", file=str(decisions_path), decision_id=did))

    for d in decisions:
        dtype = d.get("decision_type")
        if dtype not in VALID_DECISION_TYPES:
            defects.append(Defect("E033", f"unsupported decision_type: {dtype!r}", file=str(decisions_path), decision_id=d.get("id", "")))
        dstage = d.get("stage")
        if dstage not in valid_stage_id_set:
            defects.append(Defect("E032", f"decision references unknown stage: {dstage!r}", file=str(decisions_path), decision_id=d.get("id", "")))

    for sid, fields in stages.items():
        status = fields.get("status")
        dref = fields.get("decision_ref")
        if dref:
            if dref not in decisions_by_id:
                defects.append(Defect("E030", f"orphaned decision_ref: {dref!r} has no matching decisions.md entry", file=str(state_path), stage=sid))
            else:
                # E064: decision_type/stage-status coherence, and the
                # decision's own `stage` field must match the citing stage
                # — a stage citing another stage's decision is itself a
                # form of bad decision_ref.
                dtype = decisions_by_id[dref].get("decision_type")
                dstage = decisions_by_id[dref].get("stage")
                if dstage and dstage != sid:
                    defects.append(Defect(
                        "E064",
                        f"stage cites decision_ref {dref!r}, but that decision's own stage field is {dstage!r}, not {sid!r}",
                        file=str(state_path), stage=sid,
                    ))
                if status in STATUS_TO_EXPECTED_DECISION_TYPES:
                    if dtype not in STATUS_TO_EXPECTED_DECISION_TYPES[status]:
                        defects.append(Defect(
                            "E064",
                            f"stage status {status!r} cites decision_ref {dref!r} whose decision_type is {dtype!r}, "
                            f"expected one of {sorted(STATUS_TO_EXPECTED_DECISION_TYPES[status])}",
                            file=str(state_path), stage=sid,
                        ))
                elif dtype in {"skip", "not-applicable", "rework"}:
                    defects.append(Defect(
                        "E064",
                        f"stage status {status!r} cites decision_ref {dref!r} whose decision_type is {dtype!r}, "
                        f"which implies a skip/not-applicable/rework state this stage's status does not reflect",
                        file=str(state_path), stage=sid,
                    ))
        if status in DECISION_REQUIRED_STATUSES:
            missing = [f for f in ("reason", "decision_owner", "decision_ref", "date") if not fields.get(f)]
            if missing:
                defects.append(Defect(
                    "E034",
                    f"stage status {status!r} is missing required decision metadata: {missing}",
                    file=str(state_path), stage=sid,
                ))

    # --- Dependency validation ---------------------------------------------------
    def _as_list(v) -> list[str]:
        if v is None:
            return []
        if isinstance(v, list):
            return v
        return [v]

    for sid, fields in stages.items():
        for key in ("depends_on", "waiting_for", "may_run_with"):
            for ref in _as_list(fields.get(key)):
                if ref not in valid_stage_id_set:
                    defects.append(Defect("E040", f"{key} references unknown stage: {ref!r}", file=str(state_path), stage=sid))
                elif ref == sid:
                    defects.append(Defect("E061", f"stage lists itself in {key}", file=str(state_path), stage=sid))

    def status_of(sid: str) -> str | None:
        return stages.get(sid, {}).get("status")

    for sid, fields in stages.items():
        status = fields.get("status")
        depends_on = [d for d in _as_list(fields.get("depends_on")) if d in valid_stage_id_set]
        dep_statuses = [status_of(d) for d in depends_on]
        all_terminal = all(s in TERMINAL_STATUSES for s in dep_statuses) if depends_on else True

        if status == "eligible" and not all_terminal:
            non_terminal = [d for d, s in zip(depends_on, dep_statuses) if s not in TERMINAL_STATUSES]
            defects.append(Defect(
                "E041",
                f"marked eligible but depends_on has non-terminal stage(s): {non_terminal}",
                file=str(state_path), stage=sid,
            ))

        if status == "blocked":
            non_terminal = [d for d, s in zip(depends_on, dep_statuses) if s not in TERMINAL_STATUSES]
            if depends_on and not non_terminal:
                defects.append(Defect(
                    "E042",
                    "marked blocked but every depends_on entry is already terminal — no legitimate unmet dependency",
                    file=str(state_path), stage=sid,
                ))
            waiting_for = [w for w in _as_list(fields.get("waiting_for")) if w in valid_stage_id_set]
            for w in waiting_for:
                if status_of(w) in TERMINAL_STATUSES:
                    defects.append(Defect(
                        "E060",
                        f"waiting_for names {w!r}, but that stage's status ({status_of(w)!r}) is already terminal",
                        file=str(state_path), stage=sid,
                    ))

        if status == "complete" and not all_terminal:
            non_terminal = [d for d, s in zip(depends_on, dep_statuses) if s not in TERMINAL_STATUSES]
            defects.append(Defect(
                "E043",
                f"marked complete but depends_on has non-terminal stage(s): {non_terminal}",
                file=str(state_path), stage=sid,
            ))

        if status == "complete" and sid in MANDATORY_EVIDENCE_ON_COMPLETE and not fields.get("evidence"):
            defects.append(Defect(
                "E063",
                f"stage {sid!r} is complete but has no 'evidence' field (mandatory per D7)",
                file=str(state_path), stage=sid,
            ))

    # E044: dependency cycle detection (depends_on graph).
    graph = {sid: [d for d in _as_list(fields.get("depends_on")) if d in stages] for sid, fields in stages.items()}
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {sid: WHITE for sid in stages}

    def dfs(node: str, path: list[str]) -> list[str] | None:
        color[node] = GRAY
        for nxt in graph.get(node, []):
            if color.get(nxt) == GRAY:
                return path + [nxt]
            if color.get(nxt) == WHITE:
                cyc = dfs(nxt, path + [nxt])
                if cyc:
                    return cyc
        color[node] = BLACK
        return None

    for sid in stages:
        if color[sid] == WHITE:
            cyc = dfs(sid, [sid])
            if cyc:
                defects.append(Defect("E044", f"dependency cycle detected: {' -> '.join(cyc)}", file=str(state_path)))
                break

    # --- Parallel-execution validation ---------------------------------------------------
    for sid, fields in stages.items():
        for other in _as_list(fields.get("may_run_with")):
            if other not in valid_stage_id_set or other == sid:
                continue  # already flagged by E040/E061 above
            legal = other in compatible.get(sid, set()) or sid in compatible.get(other, set())
            if not legal:
                defects.append(Defect(
                    "E050",
                    f"may_run_with pairing ({sid}, {other}) is not declared compatible in STAGE-REGISTRY.md",
                    file=str(state_path), stage=sid,
                ))

    # --- Sprint-level consistency ---------------------------------------------------
    if top_fields.get("status") == "complete":
        non_terminal = [sid for sid, f in stages.items() if f.get("status") not in TERMINAL_STATUSES]
        if non_terminal:
            defects.append(Defect(
                "E070",
                f"sprint marked complete but these stages are not terminal: {sorted(non_terminal)}",
                file=str(state_path),
            ))

    return defects, stages, decisions


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[1] if __doc__ else "")
    parser.add_argument("workspace", nargs="?", default=None,
                         help="Path to a docs/sprints/<id>/ workspace. Omit to resolve the active sprint from CURRENT.md.")
    parser.add_argument("--sprints-root", default=None,
                         help="Directory containing CURRENT.md and STAGE-REGISTRY.md (defaults to the workspace's parent, or docs/sprints/ relative to this script).")
    args = parser.parse_args(argv)

    default_sprints_root = Path(__file__).resolve().parent.parent / "docs" / "sprints"
    sprints_root = Path(args.sprints_root) if args.sprints_root else default_sprints_root

    try:
        workspace = resolve_workspace(args.workspace, sprints_root)
        result = validate(workspace)
    except LintError as e:
        print(f"FAIL: {e}")
        return 2

    defects, stages, decisions = result

    if defects:
        print(f"FAIL — {len(defects)} defect(s) found in {workspace}\n")
        for d in defects:
            print(" -", d.render())
        return 1

    print(f"PASS — {workspace}")
    print(f"  sprint            : {workspace.name}")
    print(f"  stages checked    : {len(stages)}")
    print(f"  decisions checked : {len(decisions)}")
    print("  checks completed  : required-files, stage-registry, status-values, "
          "decision-integrity, dependency-graph, cycle-detection, parallel-compatibility, "
          "sprint-level consistency")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
