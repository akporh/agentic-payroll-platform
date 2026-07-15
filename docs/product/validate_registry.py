#!/usr/bin/env python3
"""Validate internal consistency of docs/product/.

Standard-library only, no dependencies. Checks:
  1. Every story_id in STORY-REGISTRY.md has a matching file in stories/.
  2. Every file in stories/ (other than TEMPLATE.md) has a matching row in STORY-REGISTRY.md.
  3. Every capability_id referenced in FEATURES.md exists in CAPABILITIES.md.
  4. Every outcome_id referenced in CAPABILITIES.md exists in OUTCOMES.md.

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
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not cells or not cells[0]:
            continue
        if any(marker in cells[0] for marker in PLACEHOLDER_MARKERS):
            continue
        rows.append(cells)
    return rows


def main() -> int:
    errors: list[str] = []

    stories_dir = HERE / "stories"
    story_registry_rows = read_table_rows(HERE / "STORY-REGISTRY.md")
    story_ids_in_registry = {row[0] for row in story_registry_rows if row}

    story_files = {
        p.stem for p in stories_dir.glob("*.md") if p.name != "TEMPLATE.md"
    } if stories_dir.exists() else set()

    for story_id in story_ids_in_registry:
        if story_id not in story_files:
            errors.append(
                f"STORY-REGISTRY.md lists '{story_id}' but stories/{story_id}.md does not exist"
            )

    for story_file in story_files:
        if story_file not in story_ids_in_registry:
            errors.append(
                f"stories/{story_file}.md exists but '{story_file}' is not in STORY-REGISTRY.md"
            )

    features_rows = read_table_rows(HERE / "FEATURES.md")
    capabilities_rows = read_table_rows(HERE / "CAPABILITIES.md")
    outcomes_rows = read_table_rows(HERE / "OUTCOMES.md")

    capability_ids = {row[0] for row in capabilities_rows if row}
    outcome_ids = {row[0] for row in outcomes_rows if row}

    # FEATURES.md schema: feature_id | name | description | capability_id | status | story_count
    for row in features_rows:
        if len(row) > 3:
            cap_ref = row[3]
            if cap_ref and cap_ref not in capability_ids:
                errors.append(
                    f"FEATURES.md row '{row[0]}' references capability_id '{cap_ref}' not found in CAPABILITIES.md"
                )

    # CAPABILITIES.md schema: capability_id | name | type | description | outcome_id | status | sprint_or_track_refs
    for row in capabilities_rows:
        if len(row) > 4:
            outcome_ref = row[4]
            if outcome_ref and outcome_ref not in outcome_ids:
                errors.append(
                    f"CAPABILITIES.md row '{row[0]}' references outcome_id '{outcome_ref}' not found in OUTCOMES.md"
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
