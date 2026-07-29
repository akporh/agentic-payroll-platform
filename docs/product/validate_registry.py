#!/usr/bin/env python3
"""Validate internal consistency of docs/product/.

Standard-library only, no dependencies. Checks:
  1. Every story_id in STORY-REGISTRY.md has exactly one matching file in stories/.
  2. Every file in stories/ (other than TEMPLATE.md) has exactly one matching row in STORY-REGISTRY.md.
  3. Every capability_id referenced in FEATURES.md exists in CAPABILITIES.md.
  4. Every outcome_id referenced in CAPABILITIES.md exists in OUTCOMES.md.
  5. No duplicate IDs within any single registry (OUTCOMES.md, CAPABILITIES.md,
     FEATURES.md, STORY-REGISTRY.md).
  6. No story-file ID prefix is ambiguous (two different story_ids both match
     the same filename stem) and no story_id matches more than one file.
  7. Every human-readable display-name field (a feature's `capability_name`, a
     capability's `outcome_name`, a story's `feature_name`) exactly matches the
     current authoritative `name` of the parent row it references, and is not
     missing.

Story files are named `<story-id>-<descriptive-slug>.md` (e.g.
`PT-A4-31-component-source-trace-fix.md`) so a filename alone identifies the
story without opening it — the story ID is not required to be the exact
filename stem. A file matches a registry story_id if its stem equals the
story_id exactly, or starts with "<story_id>-".

On the empty scaffold (zero content rows in every registry) this passes trivially.
Run: python3 docs/product/validate_registry.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLACEHOLDER_MARKERS = ("*(no rows", "*(none")


def read_table_rows(md_path: Path, heading: str = "## Registry") -> list[list[str]]:
    """Return data rows (as lists of stripped cell strings) from the markdown
    table under the given heading (default '## Registry', to avoid picking up
    the '## Schema' documentation table instead), skipping the header row,
    the '---' separator row, and any placeholder row."""
    if not md_path.exists():
        print(f"MISSING FILE: {md_path}")
        return []

    lines = md_path.read_text().splitlines()
    try:
        start = next(i for i, line in enumerate(lines) if line.strip() == heading)
    except StopIteration:
        print(f"MISSING HEADING '{heading}' in {md_path}")
        return []

    table_lines = [
        line for line in lines[start + 1 :] if line.strip().startswith("|")
    ]
    if len(table_lines) < 2:
        return []

    rows = []
    for line in table_lines[2:]:  # skip header + separator
        cells = [c.strip().strip("`") for c in line.strip().strip("|").split("|")]
        if not cells or not cells[0]:
            continue
        if any(marker in cells[0] for marker in PLACEHOLDER_MARKERS):
            continue
        rows.append(cells)
    return rows


def check_duplicate_ids(rows: list[list[str]], registry_name: str, errors: list[str]) -> None:
    seen: dict[str, int] = {}
    for row in rows:
        if not row:
            continue
        rid = row[0]
        seen[rid] = seen.get(rid, 0) + 1
    for rid, count in seen.items():
        if count > 1:
            errors.append(f"{registry_name} has {count} rows with duplicate id '{rid}'")


def stem_matches_story_id(stem: str, story_id: str) -> bool:
    return stem == story_id or stem.startswith(story_id + "-")


def main() -> int:
    errors: list[str] = []

    outcomes_rows = read_table_rows(HERE / "OUTCOMES.md")
    capabilities_rows = read_table_rows(HERE / "CAPABILITIES.md")
    features_rows = read_table_rows(HERE / "FEATURES.md")
    story_registry_rows = read_table_rows(HERE / "STORY-REGISTRY.md")

    check_duplicate_ids(outcomes_rows, "OUTCOMES.md", errors)
    check_duplicate_ids(capabilities_rows, "CAPABILITIES.md", errors)
    check_duplicate_ids(features_rows, "FEATURES.md", errors)
    check_duplicate_ids(story_registry_rows, "STORY-REGISTRY.md", errors)

    outcome_names = {row[0]: row[1] for row in outcomes_rows if len(row) > 1}
    capability_names = {row[0]: row[1] for row in capabilities_rows if len(row) > 1}
    feature_names = {row[0]: row[1] for row in features_rows if len(row) > 1}

    # CAPABILITIES.md schema: capability_id | name | type | description | outcome_id | outcome_name | status | sprint_or_track_refs
    for row in capabilities_rows:
        if len(row) > 5:
            cap_id, outcome_ref, outcome_name_displayed = row[0], row[4], row[5]
            if outcome_ref and outcome_ref not in outcome_names:
                errors.append(
                    f"CAPABILITIES.md row '{cap_id}' references outcome_id '{outcome_ref}' not found in OUTCOMES.md"
                )
            elif outcome_ref:
                if not outcome_name_displayed:
                    errors.append(
                        f"CAPABILITIES.md row '{cap_id}' is missing its outcome_name display field"
                    )
                elif outcome_name_displayed != outcome_names[outcome_ref]:
                    errors.append(
                        f"CAPABILITIES.md row '{cap_id}' displays outcome_name '{outcome_name_displayed}' "
                        f"but OUTCOMES.md '{outcome_ref}' is actually named '{outcome_names[outcome_ref]}'"
                    )

    # FEATURES.md schema: feature_id | name | description | capability_id | capability_name | status | story_count
    for row in features_rows:
        if len(row) > 4:
            feat_id, cap_ref, cap_name_displayed = row[0], row[3], row[4]
            if cap_ref and cap_ref not in capability_names:
                errors.append(
                    f"FEATURES.md row '{feat_id}' references capability_id '{cap_ref}' not found in CAPABILITIES.md"
                )
            elif cap_ref:
                if not cap_name_displayed:
                    errors.append(
                        f"FEATURES.md row '{feat_id}' is missing its capability_name display field"
                    )
                elif cap_name_displayed != capability_names[cap_ref]:
                    errors.append(
                        f"FEATURES.md row '{feat_id}' displays capability_name '{cap_name_displayed}' "
                        f"but CAPABILITIES.md '{cap_ref}' is actually named '{capability_names[cap_ref]}'"
                    )

    # STORY-REGISTRY.md schema (D-019/D-020, 2026-07-28):
    # story_id | origin_code | title | feature_id | feature_name | classification
    #   | status | confidence | ac_owner | sprint_refs | evidence_refs | story_file
    # NOTE: origin_code was inserted at index 1, shifting feature_id 2->3 and
    # feature_name 3->4. Keep these indices in step with the header if it changes again.
    story_ids_in_registry = set()
    story_feature_of: dict[str, str] = {}
    for row in story_registry_rows:
        if not row:
            continue
        story_ids_in_registry.add(row[0])

        # origin_code is mandatory: it is the only bridge from a legacy identifier
        # (PT-*, sprint item code, track code) to the current story ID.
        if len(row) > 1:
            if not row[1].strip():
                errors.append(
                    f"STORY-REGISTRY.md row '{row[0]}' has an empty origin_code — "
                    f"mandatory per D-019; use 'None (authored here)' for a forward-authored story"
                )

        if len(row) > 4:
            story_feature_of[row[0]] = row[3]
            story_id, feat_ref, feat_name_displayed = row[0], row[3], row[4]
            if feat_ref and feat_ref not in feature_names:
                errors.append(
                    f"STORY-REGISTRY.md row '{story_id}' references feature_id '{feat_ref}' not found in FEATURES.md"
                )
            elif feat_ref:
                if not feat_name_displayed:
                    errors.append(
                        f"STORY-REGISTRY.md row '{story_id}' is missing its feature_name display field"
                    )
                elif feat_name_displayed != feature_names[feat_ref]:
                    errors.append(
                        f"STORY-REGISTRY.md row '{story_id}' displays feature_name '{feat_name_displayed}' "
                        f"but FEATURES.md '{feat_ref}' is actually named '{feature_names[feat_ref]}'"
                    )

    stories_dir = HERE / "stories"
    story_file_stems = {
        p.stem for p in stories_dir.glob("*.md") if p.name != "TEMPLATE.md"
    } if stories_dir.exists() else set()

    for story_id in story_ids_in_registry:
        matches = [stem for stem in story_file_stems if stem_matches_story_id(stem, story_id)]
        if not matches:
            errors.append(
                f"STORY-REGISTRY.md lists '{story_id}' but no stories/{story_id}[-*].md file exists"
            )
        elif len(matches) > 1:
            errors.append(
                f"STORY-REGISTRY.md id '{story_id}' matches more than one file in stories/: {sorted(matches)}"
            )

    for stem in story_file_stems:
        matches = [sid for sid in story_ids_in_registry if stem_matches_story_id(stem, sid)]
        if not matches:
            errors.append(
                f"stories/{stem}.md exists but no story_id in STORY-REGISTRY.md matches it"
            )
        elif len(matches) > 1:
            errors.append(
                f"stories/{stem}.md ambiguously matches more than one story_id: {sorted(matches)}"
            )

    # --- Phase 3B additions (D-023) -------------------------------------------------

    # FEATURES.md 'stories' column must round-trip against STORY-REGISTRY.md's
    # feature_id, both directions. This is what makes the feature->story direction
    # navigable at all; a bare story_count could never answer "which stories?".
    # FEATURES.md schema: feature_id | name | description | capability_id
    #   | capability_name | status | stories | migrated | allocated
    listed_by_feature: dict[str, set[str]] = {}
    for row in features_rows:
        if len(row) > 6:
            listed = {
                tok.strip().strip("`")
                for tok in row[6].split(",")
                if tok.strip() and tok.strip() != "—"
            }
            listed_by_feature[row[0]] = listed
            if len(row) > 7 and row[7].strip().isdigit():
                if len(listed) != int(row[7].strip()):
                    errors.append(
                        f"FEATURES.md row '{row[0]}' lists {len(listed)} story id(s) "
                        f"but its migrated count says {row[7].strip()}"
                    )
            for sid in listed:
                if sid not in story_ids_in_registry:
                    errors.append(
                        f"FEATURES.md row '{row[0]}' lists story '{sid}' which has no STORY-REGISTRY.md row"
                    )
                elif story_feature_of.get(sid) != row[0]:
                    errors.append(
                        f"FEATURES.md row '{row[0]}' lists story '{sid}', but that story's "
                        f"feature_id is '{story_feature_of.get(sid)}'"
                    )
    for sid, fid in story_feature_of.items():
        if sid not in listed_by_feature.get(fid, set()):
            errors.append(
                f"STORY-REGISTRY.md '{sid}' maps to feature '{fid}', but that feature's "
                f"stories column does not list it"
            )

    # No live PT-* identifier may survive. Legacy codes belong in origin_code
    # (and in SOURCE-INDEX.md / ID-ALLOCATION.md, which are lookup surfaces) —
    # anywhere else means a re-key was missed and the reference is now dangling.
    legacy_id = re.compile(r"\bPT-[A-Z]+\d*-\d+\b")
    lookup_surfaces = {"SOURCE-INDEX.md", "ID-ALLOCATION.md", "README.md", "TEMPLATE.md"}
    for md in sorted(HERE.rglob("*.md")):
        if md.name in lookup_surfaces:
            continue
        in_amendment_history = False
        for n, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
            if line.startswith("## "):
                in_amendment_history = line.strip().lower().startswith("## amendment history")
            if in_amendment_history or not legacy_id.search(line):
                continue
            # Legitimate places a legacy code may still appear:
            #   - the origin_code column of a STORY-REGISTRY.md content row
            #   - the **Origin code(s):** header field of a story file
            #   - an annotated rewrite, "`STORY-0101` (was `PT-A1-21`)"
            if line.startswith("| `STORY-") or line.startswith("**Origin code(s):**"):
                continue
            # A legacy code shown alongside its replacement is a mapping statement,
            # not a dangling reference — e.g. "`STORY-0101` (was `PT-A1-21`)".
            if re.search(r"\bSTORY-\d{4}\b", line):
                continue
            errors.append(
                f"{md.relative_to(HERE)}:{n} contains a live PT-* identifier outside "
                f"an origin_code declaration — re-key missed?"
            )

    # Link existence. Path style is fixed by README (relative inside docs/product/,
    # repo-root-relative outside it); this check is what makes relocating the tree
    # a loud, one-pass fix rather than a slow rot of dead citations.
    repo_root = HERE.parent.parent
    link = re.compile(r"`((?:\.\./|docs/)[A-Za-z0-9._/-]+?\.(?:md|py))`")
    for md in sorted(HERE.rglob("*.md")):
        for n, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
            for ref in link.findall(line):
                target = (md.parent / ref) if ref.startswith("../") else (repo_root / ref)
                if not target.exists():
                    errors.append(
                        f"{md.relative_to(HERE)}:{n} references '{ref}' which does not exist on disk"
                    )

    # Every migrated story must be reachable from the reverse index, or the
    # source -> story direction silently stops working for it.
    source_index = HERE / "SOURCE-INDEX.md"
    if source_index.exists():
        index_text = source_index.read_text(encoding="utf-8")
        for sid in sorted(story_ids_in_registry):
            if sid not in index_text:
                errors.append(f"SOURCE-INDEX.md does not mention '{sid}'")
    else:
        errors.append("SOURCE-INDEX.md is missing — the reverse lookup has no home")

    if errors:
        print(f"FAIL — {len(errors)} consistency error(s):")
        for e in errors:
            print(f"  - {e}")
        return 1

    total_rows = len(story_registry_rows) + len(features_rows) + len(capabilities_rows) + len(outcomes_rows)
    print(
        f"PASS — docs/product/ registries are internally consistent "
        f"({total_rows} total content row(s) checked)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
