#!/usr/bin/env python3
"""
validate_phase3.py -- Phase 3 deliverable validation script.

Checks all 16 Phase 3 requirement IDs across the 4 output files:
  - playbook-section-scoring-formulas.md       (SCORE-01 to SCORE-08)
  - playbook-section-master-trigger-table.md   (TRIG-01, TRIG-02)
  - playbook-section-mvp-selection.md          (TRIG-03, TRIG-04)
  - playbook-section-channel-policy.md         (CHAN-01 to CHAN-04)

Exit code 0 if all existing files pass, 1 if any fail.
Files that don't exist yet report NOT_YET_CREATED (not FAIL).
"""

import os
import re
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# File paths
SCORING_FILE = os.path.join(BASE_DIR, "playbook-section-scoring-formulas.md")
TRIGGER_FILE = os.path.join(BASE_DIR, "playbook-section-master-trigger-table.md")
MVP_FILE = os.path.join(BASE_DIR, "playbook-section-mvp-selection.md")
CHANNEL_FILE = os.path.join(BASE_DIR, "playbook-section-channel-policy.md")

results = {}
any_fail = False


def read_file(path):
    """Read file contents or return None if not found."""
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def record(req_id, status, detail=""):
    """Record a requirement check result."""
    global any_fail
    results[req_id] = (status, detail)
    if status == "FAIL":
        any_fail = True


# ============================================================
# SCORING FORMULAS CHECKS (SCORE-01 through SCORE-08)
# ============================================================

scoring_content = read_file(SCORING_FILE)

if scoring_content is None:
    for i in range(1, 9):
        record(f"SCORE-{i:02d}", "NOT_YET_CREATED", "playbook-section-scoring-formulas.md not found")
else:
    # Score name to section heading mapping
    score_headings = {
        "SCORE-01": "Market Relevance",
        "SCORE-02": "User Asset Affinity",
        "SCORE-03": "Trigger Opportunity",
        "SCORE-04": "Notification Pressure",
        "SCORE-05": "Fatigue Risk",
        "SCORE-06": "Cross-sell Eligibility",
        "SCORE-07": "Churn Risk",
        "SCORE-08": "Send Score Final",
    }

    for req_id, heading_text in score_headings.items():
        issues = []

        # Check section heading exists
        heading_pattern = re.compile(r"^#{2,4}\s+.*" + re.escape(heading_text), re.MULTILINE | re.IGNORECASE)
        if not heading_pattern.search(scoring_content):
            issues.append(f"Missing section heading containing '{heading_text}'")

        # Find the section content (from heading to next same-level heading)
        section_start = None
        for m in re.finditer(r"^(#{2,4})\s+.*" + re.escape(heading_text), scoring_content, re.MULTILINE | re.IGNORECASE):
            section_start = m.start()
            heading_level = len(m.group(1))
            break

        if section_start is not None:
            # Find end of the heading line first, then search for next heading
            heading_end = scoring_content.index("\n", section_start) + 1
            rest = scoring_content[heading_end:]
            next_heading = re.search(r"^#{2," + str(heading_level) + r"}\s+", rest, re.MULTILINE)
            if next_heading:
                section_content = rest[:next_heading.start()]
            else:
                section_content = rest

            # Check for SQL/pseudocode block (``` delimiter)
            if "```" not in section_content:
                issues.append("No SQL/pseudocode block (``` delimiter) found in section")

            # Check for weight values (decimal like 0.40, 0.25, etc.)
            weight_pattern = re.compile(r"0\.\d{1,2}")
            if not weight_pattern.search(section_content):
                issues.append("No decimal weight values found (e.g., 0.40, 0.25)")
        else:
            if not issues:
                issues.append(f"Could not locate section for '{heading_text}'")

        if issues:
            record(req_id, "FAIL", "; ".join(issues))
        else:
            record(req_id, "PASS")


# ============================================================
# MASTER TRIGGER TABLE CHECKS (TRIG-01, TRIG-02)
# ============================================================

trigger_content = read_file(TRIGGER_FILE)

if trigger_content is None:
    record("TRIG-01", "NOT_YET_CREATED", "playbook-section-master-trigger-table.md not found")
    record("TRIG-02", "NOT_YET_CREATED", "playbook-section-master-trigger-table.md not found")
else:
    # TRIG-01: Count rows matching trigger_id pattern [A-F]-\d{2}
    trigger_ids = re.findall(r"[A-F]-\d{2}", trigger_content)
    unique_trigger_ids = set(trigger_ids)
    count = len(unique_trigger_ids)
    if count >= 30:
        record("TRIG-01", "PASS", f"{count} unique trigger IDs found (>= 30)")
    else:
        record("TRIG-01", "FAIL", f"Only {count} unique trigger IDs found (need >= 30)")

    # TRIG-02: Verify all 14 required columns appear in a table header
    required_columns = [
        "trigger_id", "family", "business_objective", "who_receives",
        "who_never_receives", "asset_scope", "formula_used", "threshold",
        "cooldown", "channel", "deep_link", "priority",
        "estimated_value", "estimated_risk"
    ]
    # Look for header row containing these columns (case-insensitive, allowing underscores or spaces)
    missing_columns = []
    content_lower = trigger_content.lower()
    for col in required_columns:
        # Check for column name with underscores or spaces
        col_variants = [col, col.replace("_", " "), col.replace("_", "-")]
        found = any(v in content_lower for v in col_variants)
        if not found:
            missing_columns.append(col)

    if missing_columns:
        record("TRIG-02", "FAIL", f"Missing columns: {', '.join(missing_columns)}")
    else:
        record("TRIG-02", "PASS", "All 14 required columns found")


# ============================================================
# MVP SELECTION CHECKS (TRIG-03, TRIG-04)
# ============================================================

mvp_content = read_file(MVP_FILE)

# TRIG-03: Check for MVP section with at least 10 trigger references
# Can also be in trigger table file
trig03_content = mvp_content or trigger_content

if trig03_content is None:
    record("TRIG-03", "NOT_YET_CREATED", "Neither mvp-selection.md nor master-trigger-table.md found")
else:
    mvp_section = re.search(r"(?i)(#{1,4}\s+.*MVP.*)", trig03_content)
    if mvp_section:
        # Count trigger references after MVP heading
        mvp_start = mvp_section.start()
        mvp_text = trig03_content[mvp_start:]
        trigger_refs = re.findall(r"[A-F]-\d{2}", mvp_text)
        if len(trigger_refs) >= 10:
            record("TRIG-03", "PASS", f"MVP section found with {len(trigger_refs)} trigger references")
        else:
            record("TRIG-03", "FAIL", f"MVP section found but only {len(trigger_refs)} trigger references (need >= 10)")
    else:
        record("TRIG-03", "FAIL", "No 'MVP' section heading found")

# TRIG-04: Verify "NOT to launch" or "Do Not Launch" section with at least 10 entries
if mvp_content is None:
    record("TRIG-04", "NOT_YET_CREATED", "playbook-section-mvp-selection.md not found")
else:
    not_launch_pattern = re.compile(r"(?i)(#{1,4}\s+.*(NOT\s+to\s+launch|Do\s+Not\s+Launch|not.to.launch).*)")
    not_launch_match = not_launch_pattern.search(mvp_content)
    if not_launch_match:
        not_launch_start = not_launch_match.start()
        not_launch_text = mvp_content[not_launch_start:]
        # Count entries (numbered list items or trigger references)
        entries = re.findall(r"(?:^\d+\.\s+|\*\s+|-\s+)", not_launch_text, re.MULTILINE)
        if len(entries) >= 10:
            record("TRIG-04", "PASS", f"NOT-to-launch section found with {len(entries)} entries")
        else:
            record("TRIG-04", "FAIL", f"NOT-to-launch section found but only {len(entries)} entries (need >= 10)")
    else:
        record("TRIG-04", "FAIL", "No 'NOT to launch' / 'Do Not Launch' section heading found")


# ============================================================
# CHANNEL POLICY CHECKS (CHAN-01 through CHAN-04)
# ============================================================

channel_content = read_file(CHANNEL_FILE)

if channel_content is None:
    for i in range(1, 5):
        record(f"CHAN-{i:02d}", "NOT_YET_CREATED", "playbook-section-channel-policy.md not found")
else:
    # CHAN-01: Channel decision matrix with all 6 families
    families_found = []
    for fam in ["Family A", "Family B", "Family C", "Family D", "Family E", "Family F"]:
        if fam.lower() in channel_content.lower() or fam.replace("Family ", "").lower() in channel_content.lower():
            families_found.append(fam)
    if len(families_found) >= 6:
        record("CHAN-01", "PASS", "Channel decision matrix contains all 6 families")
    else:
        missing = [f for f in ["Family A", "Family B", "Family C", "Family D", "Family E", "Family F"] if f not in families_found]
        record("CHAN-01", "FAIL", f"Missing families in channel matrix: {', '.join(missing)}")

    # CHAN-02: Deep link table with 10+ product entries matching bit2me:// pattern
    deep_links = re.findall(r"bit2me://[^\s|`\)]+", channel_content)
    unique_deep_links = set(deep_links)
    if len(unique_deep_links) >= 10:
        record("CHAN-02", "PASS", f"{len(unique_deep_links)} unique deep link patterns found")
    else:
        record("CHAN-02", "FAIL", f"Only {len(unique_deep_links)} unique deep link patterns found (need >= 10)")

    # CHAN-03: Quiet hours table with timezone regions
    regions = ["Spain", "LatAm", "EU"]
    regions_found = [r for r in regions if r.lower() in channel_content.lower()]
    if len(regions_found) >= 3:
        record("CHAN-03", "PASS", f"Quiet hours regions found: {', '.join(regions_found)}")
    else:
        record("CHAN-03", "FAIL", f"Missing quiet hours regions. Found: {', '.join(regions_found)}. Need: Spain, LatAm, EU")

    # CHAN-04: Conflict resolution table with journey vs alert rules
    conflict_patterns = [
        re.compile(r"(?i)journey.*alert|alert.*journey"),
        re.compile(r"(?i)conflict.*resolution|resolution.*conflict"),
        re.compile(r"(?i)suppress|priority.*queue"),
    ]
    conflict_found = any(p.search(channel_content) for p in conflict_patterns)
    if conflict_found:
        record("CHAN-04", "PASS", "Conflict resolution rules found")
    else:
        record("CHAN-04", "FAIL", "No conflict resolution rules found (journey vs alert)")


# ============================================================
# RESULTS OUTPUT
# ============================================================

print("\n" + "=" * 60)
print("Phase 3 Validation Results")
print("=" * 60)

pass_count = 0
fail_count = 0
not_yet_count = 0

for req_id in sorted(results.keys()):
    status, detail = results[req_id]
    icon = {"PASS": "PASS", "FAIL": "FAIL", "NOT_YET_CREATED": "----"}[status]
    detail_str = f"  ({detail})" if detail else ""
    print(f"  [{icon}] {req_id}{detail_str}")

    if status == "PASS":
        pass_count += 1
    elif status == "FAIL":
        fail_count += 1
    else:
        not_yet_count += 1

print()
print(f"Total: {pass_count} PASS, {fail_count} FAIL, {not_yet_count} NOT_YET_CREATED")
print(f"Score: {pass_count}/{pass_count + fail_count + not_yet_count}")
print()

if any_fail:
    print("RESULT: FAIL (some checks did not pass)")
    sys.exit(1)
else:
    print("RESULT: OK (all existing files pass, remaining files not yet created)")
    sys.exit(0)
