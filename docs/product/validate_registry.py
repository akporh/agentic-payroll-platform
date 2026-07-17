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

    # STORY-REGISTRY.md schema: story_id | title | feature_id | feature_name | classification | status | confidence | sprint_refs | evidence_refs | story_file
    story_ids_in_registry = set()
    for row in story_registry_rows:
        if not row:
            continue
        story_ids_in_registry.add(row[0])
        if len(row) > 3:
            story_id, feat_ref, feat_name_displayed = row[0], row[2], row[3]
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
