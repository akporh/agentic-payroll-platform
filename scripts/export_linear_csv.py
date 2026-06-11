"""
Export ROADMAP.md items to a Linear-compatible CSV for bulk import.

Run: python scripts/export_linear_csv.py
Output: docs/linear-import.csv
"""

import csv
import re
import sys
from pathlib import Path

ROADMAP = Path(__file__).parent.parent / "docs" / "ROADMAP.md"
OUTPUT = Path(__file__).parent.parent / "docs" / "linear-import.csv"

# Status mapping
STATUS_MAP = {
    "✅": "Done",
    "⚠️": "In Progress",
    "🔜": "Todo",
    "⬜": "Todo",
    "🔮": "Backlog",
}

# Priority — open items get higher priority
PRIORITY_MAP = {
    "✅": "No priority",
    "⚠️": "Medium",
    "🔜": "High",
    "⬜": "Low",
    "🔮": "No priority",
}

EPIC_LABELS = {
    "A1": "Onboarding: Workspace Setup",
    "A2": "Onboarding: Workforce",
    "A3": "Pay Events",
    "A4": "Execution",
    "A5": "Governance",
    "A6": "Disbursement",
    "A7": "Audit & Inspect",
    "A8": "Correctness",
    "A9": "Temporal & Retroactive",
    "A10": "Snapshot & Reproducibility",
}

TRACK_LABELS = {
    "Track A": "Track A – Defect Fixes",
    "Track B": "Track B – Schema",
    "Track C": "Track C – Engine",
    "Track D": "Track D – Warnings",
    "Track E": "Track E – Client 3",
    "Track F": "Track F – API Routes",
    "Track G": "Track G – Frontend",
    "Track H": "Track H – Exports",
    "Track I": "Track I – Governance",
    "Track J": "Track J – Post-Onboarding Config",
    "Track K": "Track K – Client B Defects",
    "Track L": "Track L – Client B Onboarding",
    "Track M": "Track M – Statutory Deductions",
    "Track N": "Track N – Proration",
    "Track O": "Track O – Employee Schema",
    "Track S": "Track S – Security",
    "Track Q": "Track Q – Audit",
    "Track UI": "Track UI – Design System",
}


def detect_status(text):
    for icon, status in STATUS_MAP.items():
        if icon in text:
            return icon, status
    return None, None


def clean_title(text, icon):
    # Strip the status icon
    if icon:
        text = text.replace(icon, "")
    # Strip ref codes like (P0-1), (FIX-1), ✅, etc.
    text = re.sub(r"\s*\([^)]+\)\s*", " ", text)
    # Strip leading dashes, pipes, numbers
    text = re.sub(r"^[\s\-\|\d\.]+", "", text)
    # Strip trailing em-dash notes
    text = re.sub(r"\s*—.*$", "", text)
    # Strip bold markers
    text = text.replace("**", "")
    # Strip remaining icons
    for icon in STATUS_MAP.keys():
        text = text.replace(icon, "")
    return text.strip()


def extract_ref(text):
    """Extract reference codes like P0-1, FIX-1, WC-1, etc."""
    refs = re.findall(r"\(([A-Z0-9\-/]+)\)", text)
    return ", ".join(refs) if refs else ""


def parse_roadmap(path):
    issues = []
    current_sprint = "Sprint 0"
    current_epic = None
    current_track = None

    sprint_pattern = re.compile(r"^#+\s+(Sprint \d+|Phase \d+|Track [A-Z]+|Phase 3)")
    epic_pattern = re.compile(r"\*\*(A\d+)\s*[—–-]")
    track_header_pattern = re.compile(r"###\s+(Track [A-Z]+)\s*[—–]")
    bullet_pattern = re.compile(r"^[-*]\s+(.+)")
    table_row_pattern = re.compile(r"^\|\s*\d+\s*\|(.+?)\|")

    with open(path, encoding="utf-8") as f:
        lines = f.readlines()

    for i, raw_line in enumerate(lines):
        line = raw_line.rstrip()

        # Detect sprint/phase section
        m = re.match(r"^##\s+(Sprint \d+|Phase \d+)[^#]", line)
        if m:
            current_sprint = m.group(1).strip()
            # Normalise: "Phase 1 — Single-Workspace..." → "Phase 1"
            current_sprint = re.sub(r"\s*[—–].*", "", current_sprint).strip()
            current_track = None
            continue

        # Detect track section header (### Track X)
        m = track_header_pattern.match(line)
        if m:
            track_key = m.group(1).strip()
            current_track = TRACK_LABELS.get(track_key, track_key)
            continue

        # Also catch "### Track S" style without em-dash
        m = re.match(r"^###\s+(Track [A-Z]+)\s*(?:—|–|-|$)", line)
        if m:
            track_key = m.group(1).strip()
            current_track = TRACK_LABELS.get(track_key, track_key)
            continue

        # Detect sprint-numbered subsection  e.g. "## Sprint 14 —"
        m = re.match(r"^##\s+(Sprint \d+)\s*[—–]", line)
        if m:
            current_sprint = m.group(1).strip()
            current_track = None
            continue

        # Detect epic header e.g. **A1 — Workspace Setup**
        m = epic_pattern.search(line)
        if m:
            epic_code = m.group(1)
            current_epic = EPIC_LABELS.get(epic_code, epic_code)
            continue

        # Also plain section headers like "### Onboarding (A1 + A2)"
        m = re.match(r"^###\s+(.+?)\s*\(A(\d+)", line)
        if m:
            epic_code = f"A{m.group(2)}"
            current_epic = EPIC_LABELS.get(epic_code, epic_code)
            current_track = None
            continue

        # --- Bullet point items ---
        m = bullet_pattern.match(line)
        if m:
            content = m.group(1).strip()
            icon, status = detect_status(content)
            if not status:
                continue  # Skip lines with no status icon
            title = clean_title(content, icon)
            if len(title) < 4:
                continue
            ref = extract_ref(content)
            labels = []
            if current_epic:
                labels.append(current_epic)
            if current_track:
                labels.append(current_track)
            issues.append({
                "title": title,
                "status": status,
                "priority": PRIORITY_MAP.get(icon, "No priority"),
                "labels": "; ".join(labels),
                "sprint": current_sprint,
                "ref": ref,
                "description": content.strip(),
            })
            continue

        # --- Table row items (| # | Item ... | ... |) ---
        m = table_row_pattern.match(line)
        if m:
            content = m.group(1).strip()
            icon, status = detect_status(content)
            if not status:
                continue
            title = clean_title(content, icon)
            if len(title) < 4:
                continue
            ref = extract_ref(content)
            labels = []
            if current_epic:
                labels.append(current_epic)
            if current_track:
                labels.append(current_track)
            issues.append({
                "title": title,
                "status": status,
                "priority": PRIORITY_MAP.get(icon, "No priority"),
                "labels": "; ".join(labels),
                "sprint": current_sprint,
                "ref": ref,
                "description": content.strip(),
            })

    return issues


def write_csv(issues, output_path):
    fieldnames = ["title", "status", "priority", "labels", "sprint", "description", "ref"]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for issue in issues:
            writer.writerow(issue)
    return len(issues)


def main():
    if not ROADMAP.exists():
        print(f"ERROR: {ROADMAP} not found", file=sys.stderr)
        sys.exit(1)

    print(f"Parsing {ROADMAP} ...")
    issues = parse_roadmap(ROADMAP)

    # Summary
    by_status = {}
    for issue in issues:
        by_status[issue["status"]] = by_status.get(issue["status"], 0) + 1

    print(f"\nFound {len(issues)} issues:")
    for status, count in sorted(by_status.items()):
        print(f"  {status}: {count}")

    count = write_csv(issues, OUTPUT)
    print(f"\nWrote {count} rows → {OUTPUT}")
    print("\nNext step: Linear → Settings → Import → CSV → upload this file.")
    print("Tip: map 'sprint' column to a Label or Cycle in Linear's import wizard.")


if __name__ == "__main__":
    main()
