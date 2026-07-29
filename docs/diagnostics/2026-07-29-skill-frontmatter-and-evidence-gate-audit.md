# Skill frontmatter audit + the evidence-exists gate

**Date:** 2026-07-29
**Trigger:** `/pm` was believed not to be writing `docs/sprints/<id>/CONTEXT.md`, with the cause attributed to its frontmatter `tools:` line declaring a read-only tool set.
**Outcome:** both the cause and the defect are false — the field does not exist, and all three sprints have a `CONTEXT.md`. One unrelated record gap was found and recorded, and `/retro` now has a gate that checks claimed artefacts exist on disk.

---

## 1. What was believed

That a `tools:` line in a `SKILL.md` restricts which tools the skill may use, and that a write instruction in a skill declared `tools: Read, Glob, Grep` silently no-ops. On that basis an audit reported five further skills with the same defect — `tester`, `security`, `auditor`, `architect`, `arch-council` — all of which are instructed to write reports and all of which declared read-only tool sets.

## 2. What is actually true

Verified against <https://code.claude.com/docs/en/skills> § Frontmatter reference and <https://code.claude.com/docs/en/sub-agents> § Available tools:

| Field | Behaviour in a `SKILL.md` |
|---|---|
| `tools` | **Not a supported field. Ignored entirely.** Grants nothing, restricts nothing. |
| `allowed-tools` | Pre-approves the listed tools so they run without a permission prompt, for the invoking turn only. Docs verbatim: *"It does not restrict which tools are available: every tool remains callable."* |
| `disallowed-tools` | The only field that actually removes tools from a skill's pool. |

Two further findings that close off the alternative explanations:

- `tools:` **is** honoured in `.claude/agents/*.md` (subagent definition files), where it genuinely restricts. The same key means something in one file type and nothing in the other — this is the root of the confusion.
- Background subagents run a narrower built-in tool set than foreground ones, but `Edit` and `Write` are both **in** that set. "It ran in the background" does not explain a missing write either.

**Therefore no skill was ever prevented from writing.** The proposed fix — adding `Write, Edit` to those `tools:` lines — would have been a no-op that manufactured false confidence in a resolved defect.

### 2a. The `/pm` defect did not happen at all

Checked directly rather than inferred. All three ICM sprints have a `CONTEXT.md`, committed, and substantial:

| Sprint | `CONTEXT.md` | Created in |
|---|---|---|
| `aud-q1-trace-source` | 4,164 bytes | `ed65a30` |
| `dev-levy-rule-pct` | 6,798 bytes | `b398c72` |
| `sec-s7-timesheet-upload-guard` | 3,990 bytes | `58ec4f8` |

What is absent is `story_refs` **inside** those files. That obligation landed in `40c33cd` ("close Phase 5 — wire traceability into sprint closure") on **2026-07-29**, whereas `sec-s7` closed 2026-07-13 and `dev-levy-rule-pct` closed 2026-07-17 — the requirement is 12–16 days younger than the sprints it was being judged against. The field is missing because it did not yet exist. No write ever failed.

How the false conclusion formed: `/pm`'s frontmatter was opened during Phase 5 to add the `story_refs` bullet, `tools: Read, Glob, Grep` was seen there, and the reasoning ran backwards — *if it cannot write, the `CONTEXT.md` step has never worked*. Two errors compounded: the field is not real, **and** the claim was never checked against the disk before an audit of 15 skill files was run on top of it.

## 3. Record gaps actually found

The evidence gate defined below was run retroactively against all three closed ICM sprints.

**Item 18 — cited evidence resolves:** 17 of 17 `evidence:` paths across `aud-q1-trace-source`, `dev-levy-rule-pct` and `sec-s7-timesheet-upload-guard` resolve to existing, non-stub files. **Pass.**

**Item 19 — mandated artefacts for completed stages:** all present, including `docs/test-reports/2026-07-12-aud-q1-trace-source.md`, `docs/test-reports/2026-07-13-sec-s7-timesheet-upload-guard.md`, `docs/security/2026-07-13-sec-s7-timesheet-upload-guard-security-review.md` and `docs/audit/2026-07-12-aud-q1-trace-source-audit-review.md`. An earlier pass in this session reported `sec-s7` as having no security findings; that was wrong — the findings exist in both `docs/security/` and sprint-locally at `evidence/security/review.md`. The `security` skill permits either sprint-local location; a root `security.md` is not required. **Pass.**

**One genuine gap.** `arch-council` ran on `dev-levy-rule-pct` (2026-07-15, `state.md` stage `arch-council: complete`, `evidence: architecture.md`) but never appended its Signal History row to `docs/architecture/extraction-signals.md`. The table's last reading before this audit was dated 2026-07-04. The other two sprints recorded `arch-council: not-applicable`, so no row was owed for them.

Resolution: recorded as a **`NOT TAKEN` gap entry** in the Signal History table, not backfilled. No signal reading survives — `dev-levy-rule-pct/architecture.md` is itself a post-compaction reconstruction and contains no signal content. The sprint's substance (cadence gating plus `PERCENTAGE_OF_BASIC`, entirely internal to the existing rule model) would most likely have read GREEN like every neighbouring row, but a plausible inference written into an audit trail as an observation is a more serious defect than an admitted hole — particularly in a statutory-payroll context.

## 4. What changed

**`/retro` — new Part D, Evidence-exists gate (hard stop).** Parts A–C verify what `state.md` *says*. Part D verifies the artefacts it *claims* are on disk: every path-shaped `evidence:` value must resolve; every completed stage must have produced its skill's mandated artefact (`test` → `docs/test-reports/`, `security` → `docs/security/`, `audit` → `docs/audit/` + sprint `audit.md`, `arch-council` → `architecture.md` + a Signal History row, `pm` → `CONTEXT.md`); non-path evidence is reported as unverifiable; resolving-but-stub files (< 200 bytes) are reported separately. A missing artefact stops sprint close. Fabrication to clear the gate is prohibited — the only two valid outcomes are a reconstruction flagged as such (precedent: `dev-levy-rule-pct/architecture.md`) or the gap recorded as the record.

**Skill frontmatter normalised.** All 11 skills using the inert `tools:` key moved to `allowed-tools:`, with each list corrected to match what its body actually does (the five review skills gained `Write, Edit` — not to enable writing, which was never blocked, but so their mandated report-writing stops prompting). The two `.claude/agents/*.md` files were deliberately left on `tools:`, where the key is real and correctly restricts both reviewers to read-only.

**`/workspace-init` repaired.** It was a bare `~/.claude/skills/workspace-init.md` with no frontmatter and no directory, so it never registered as a skill despite `2.OnAiR/CLAUDE.md` instructing operators to run it. Moved to `workspace-init/SKILL.md` with proper frontmatter.

## 5. Lessons

1. **Check the artefact on disk before diagnosing why it is missing.** `ls docs/sprints/*/CONTEXT.md` would have ended this in seconds, before any theory was needed. The same omission recurred twice more in the same session: `sec-s7`'s security findings were reported missing (they were in `evidence/security/review.md` and `docs/security/`), and every one of 17 cited evidence paths turned out to resolve. Three false negatives, one cause — reasoning about a file instead of looking at it.
2. **Verify the mechanism before auditing against it.** A plausible causal story — stated confidently, by anyone — is a hypothesis until the docs or a live test confirm it. Auditing fifteen files against an unverified mechanism produces fifteen confident wrong answers, and the proposed remediation would have been a no-op presented as a fix.
3. **Check whether a requirement predates the work it is applied to.** A field absent from an old record because the rule is new is not a defect. Compare the obligation's commit date against the sprint's close date before calling anything a miss — this alone explained the entire original report.
4. **The generalisable defect is real even though this instance of it wasn't.** A step that quietly doesn't happen is indistinguishable from a step that wasn't needed. No frontmatter audit addresses that; only a completion gate that checks the artefact exists does. That is why Part D, not the rename, is the substantive change here.
5. **Absence of a record is itself a record.** Where evidence is gone, write the hole down in the same table a reader scans. An invisible gap is the failure; an admitted one is an audit trail.
