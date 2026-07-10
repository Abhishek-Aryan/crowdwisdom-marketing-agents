"""
Vault Sync — Verify Obsidian vault integrity.

Checks:
1. All expected output files exist
2. File sizes are reasonable (not empty, not truncated)
3. [[wikilinks]] in 00_Run_Summary.md resolve to actual files
4. JSON files are valid
5. All files are readable
"""
import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import OBSIDIAN_VAULT


EXPECTED_FILES = {
    "00_Run_Summary.md": {"min_size": 500, "type": "markdown"},
    "01_Marketing_Strategy.md": {"min_size": 5000, "type": "markdown"},
    "02_Pain_Point_Analysis.md": {"min_size": 5000, "type": "markdown"},
    "03_Ad_Scripts.md": {"min_size": 3000, "type": "markdown"},
    "04_Influencer_Research.md": {"min_size": 3000, "type": "markdown"},
    "05_Influencer_Outreach.md": {"min_size": 2000, "type": "markdown"},
    "06_Email_Nurture_Sequence.md": {"min_size": 3000, "type": "markdown"},
    "07_YouTube_Research.md": {"min_size": 2000, "type": "markdown"},
    "raw_ads.json": {"min_size": 1000, "type": "json"},
    "selected_ads.json": {"min_size": 500, "type": "json"},
}


def check_vault(vault_path: str = None) -> dict:
    """Run all vault checks. Returns dict of results."""
    vault = vault_path or OBSIDIAN_VAULT
    results = {"passed": [], "warnings": [], "errors": []}

    if not os.path.isdir(vault):
        results["errors"].append(f"Vault directory does not exist: {vault}")
        return results

    # Check each expected file
    for filename, spec in EXPECTED_FILES.items():
        filepath = os.path.join(vault, filename)
        if not os.path.exists(filepath):
            results["errors"].append(f"MISSING: {filename}")
            continue

        size = os.path.getsize(filepath)
        if size < spec["min_size"]:
            results["warnings"].append(
                f"SMALL: {filename} is {size:,} bytes (expected >= {spec['min_size']:,})"
            )
        else:
            results["passed"].append(f"OK: {filename} ({size:,} bytes)")

        # Validate JSON files
        if spec["type"] == "json":
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    results["passed"].append(f"  JSON valid: {len(data)} items in {filename}")
                else:
                    results["warnings"].append(f"  JSON not a list: {filename}")
            except json.JSONDecodeError as e:
                results["errors"].append(f"  JSON INVALID: {filename} — {e}")

        # Check markdown readability
        if spec["type"] == "markdown":
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                if len(content.strip()) == 0:
                    results["errors"].append(f"  EMPTY: {filename}")
            except Exception as e:
                results["errors"].append(f"  UNREADABLE: {filename} — {e}")

    # Check wikilinks in summary
    summary_path = os.path.join(vault, "00_Run_Summary.md")
    if os.path.exists(summary_path):
        import re
        with open(summary_path, "r", encoding="utf-8") as f:
            summary = f.read()
        wikilinks = re.findall(r'\[\[([^\]]+)\]\]', summary)
        for link in wikilinks:
            link_file = f"{link}.md"
            if os.path.exists(os.path.join(vault, link_file)):
                results["passed"].append(f"  Wikilink resolves: [[{link}]]")
            else:
                results["warnings"].append(f"  BROKEN LINK: [[{link}]] → {link_file} not found")

    return results


def print_report(results: dict):
    """Print a formatted vault report."""
    print("\n" + "=" * 60)
    print("  VAULT SYNC REPORT")
    print("=" * 60)

    for msg in results["passed"]:
        print(f"  ✓ {msg}")
    for msg in results["warnings"]:
        print(f"  ⚠ {msg}")
    for msg in results["errors"]:
        print(f"  ✗ {msg}")

    total = len(results["passed"]) + len(results["warnings"]) + len(results["errors"])
    print(f"\n  Passed: {len(results['passed'])}/{total}")
    print(f"  Warnings: {len(results['warnings'])}")
    print(f"  Errors: {len(results['errors'])}")

    if results["errors"]:
        print("\n  STATUS: FAIL")
        return False
    elif results["warnings"]:
        print("\n  STATUS: PASS (with warnings)")
        return True
    else:
        print("\n  STATUS: ALL CLEAR")
        return True


if __name__ == "__main__":
    vault = sys.argv[1] if len(sys.argv) > 1 else None
    results = check_vault(vault)
    ok = print_report(results)
    sys.exit(0 if ok else 1)
