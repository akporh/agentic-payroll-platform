"""
Import docs/linear-import.csv into Linear via GraphQL API.

Usage: python scripts/import_linear.py
Reads LINEAR_API_KEY from .env in project root.
"""

import csv
import json
import time
import sys
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).parent.parent
CSV_PATH = ROOT / "docs" / "linear-import.csv"
ENV_PATH = ROOT / ".env"

TEAM_ID = "57d859cd-705c-4a14-adba-24f6326446b4"

STATE_IDS = {
    "Done":        "984ba8a0-8980-463c-aea5-b866f13ec969",
    "In Progress": "0a04735a-6b0b-4947-8ee2-dd315ad9f8dd",
    "Todo":        "4f7dcde1-2190-468f-bf3d-09c6428c33fa",
    "Backlog":     "6c60f132-b345-46d2-a49f-1a00fad33742",
}

PRIORITY_MAP = {
    "No priority": 0,
    "Urgent":      1,
    "High":        2,
    "Medium":      3,
    "Low":         4,
}


def load_api_key():
    for line in ENV_PATH.read_text().splitlines():
        if line.startswith("LINEAR_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise ValueError("LINEAR_API_KEY not found in .env")


def graphql(api_key, query, variables=None):
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    req = urllib.request.Request(
        "https://api.linear.app/graphql",
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": api_key,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
            if "errors" in data:
                raise RuntimeError(data["errors"])
            return data
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise RuntimeError(f"HTTP {e.code}: {body}")


def get_or_create_labels(api_key, label_names):
    """Return {name: id} mapping, creating any that don't exist."""
    # Fetch existing labels
    resp = graphql(api_key, """
        query($teamId: String!) {
            team(id: $teamId) {
                labels { nodes { id name } }
            }
        }
    """, {"teamId": TEAM_ID})

    existing = {n["name"]: n["id"] for n in resp["data"]["team"]["labels"]["nodes"]}
    label_map = dict(existing)

    to_create = [n for n in label_names if n not in existing]
    print(f"  Existing labels: {len(existing)}, to create: {len(to_create)}")

    for name in to_create:
        resp = graphql(api_key, """
            mutation($input: IssueLabelCreateInput!) {
                issueLabelCreate(input: $input) {
                    success
                    issueLabel { id name }
                }
            }
        """, {"input": {"name": name, "teamId": TEAM_ID}})
        label_id = resp["data"]["issueLabelCreate"]["issueLabel"]["id"]
        label_map[name] = label_id
        print(f"  Created label: {name}")
        time.sleep(0.15)

    return label_map


def create_issue(api_key, title, state_id, priority, label_ids, description, sprint, ref):
    desc_parts = []
    if sprint:
        desc_parts.append(f"**Sprint:** {sprint}")
    if ref:
        desc_parts.append(f"**Ref:** {ref}")
    if description:
        desc_parts.append(f"\n{description}")
    full_desc = "\n".join(desc_parts)

    variables = {
        "input": {
            "teamId": TEAM_ID,
            "title": title,
            "stateId": state_id,
            "priority": priority,
            "description": full_desc,
            "labelIds": label_ids,
        }
    }

    resp = graphql(api_key, """
        mutation($input: IssueCreateInput!) {
            issueCreate(input: $input) {
                success
                issue { id identifier title }
            }
        }
    """, variables)

    return resp["data"]["issueCreate"]["issue"]


def main():
    print("Loading API key...")
    api_key = load_api_key()

    print("Reading CSV...")
    rows = []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    print(f"  {len(rows)} issues to import")

    # Collect all unique label names
    all_label_names = set()
    for row in rows:
        for label in row["labels"].split(";"):
            label = label.strip()
            if label:
                all_label_names.add(label)

    print(f"\nSyncing {len(all_label_names)} labels...")
    label_map = get_or_create_labels(api_key, sorted(all_label_names))

    print(f"\nCreating {len(rows)} issues...")
    created = 0
    failed = 0

    for i, row in enumerate(rows, 1):
        title = row["title"].strip()
        if not title:
            continue

        state_id = STATE_IDS.get(row["status"], STATE_IDS["Todo"])
        priority = PRIORITY_MAP.get(row["priority"], 0)

        label_ids = []
        for label in row["labels"].split(";"):
            label = label.strip()
            if label and label in label_map:
                label_ids.append(label_map[label])

        try:
            issue = create_issue(
                api_key,
                title=title,
                state_id=state_id,
                priority=priority,
                label_ids=label_ids,
                description=row.get("description", ""),
                sprint=row.get("sprint", ""),
                ref=row.get("ref", ""),
            )
            print(f"  [{i:3}/{len(rows)}] {issue['identifier']} — {title[:60]}")
            created += 1
        except Exception as e:
            print(f"  [{i:3}/{len(rows)}] FAILED: {title[:60]} — {e}")
            failed += 1

        # Respect Linear rate limits (~10 req/s)
        time.sleep(0.12)

    print(f"\nDone. Created: {created}, Failed: {failed}")


if __name__ == "__main__":
    main()
