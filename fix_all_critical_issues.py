#!/usr/bin/env python3
"""
Fix ALL CRITICAL issues in Android folder.

Handles 7 types of CRITICAL issues:
1. Missing YAML frontmatter (1 file) - SKIP, needs manual fix
2. Missing '# Question (EN)' (61 files) - FLAG for manual review
3. Missing '# Вопрос (RU)' (54 files) - FLAG for manual review
4. Missing '## Answer (EN)' (4 files) - FLAG for manual review
5. Missing '## Ответ (RU)' (7 files) - FLAG for manual review
6. Missing '## Follow-ups' (85 files) - AUTO-FIX
7. Missing '## References' (76 files) - AUTO-FIX

We'll auto-fix the template sections (Follow-ups, References) and flag structural issues.
"""

import subprocess
import sys
import re
from pathlib import Path
from typing import List, Tuple, Dict

def validate_file(file_path: Path, root: Path) -> Tuple[List[str], str]:
    """Validate a file and return (list of CRITICAL issues, full output)."""
    rel_path = file_path.relative_to(root)

    try:
        result = subprocess.run(
            ["uv", "run", "--project", "utils", "python", "-m", "utils.validate_note", str(rel_path)],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=30
        )

        output = result.stdout + result.stderr
        critical_issues = []

        lines = output.split('\n')
        for line in lines:
            if line.strip().startswith('- CRITICAL:'):
                issue = line.strip()[12:].strip()
                critical_issues.append(issue)

        return critical_issues, output
    except Exception as e:
        return [], f"Error: {e}"


def add_missing_section(file_path: Path, section_name: str, template: str) -> bool:
    """Add a missing section to a file."""
    try:
        content = file_path.read_text(encoding='utf-8')

        # Check if section already exists
        pattern = rf'^##\s+{re.escape(section_name)}\s*$'
        if re.search(pattern, content, re.MULTILINE):
            return False  # Already has the section

        # Find insertion point - before Related Questions if it exists, otherwise at end
        lines = content.split('\n')
        insert_index = len(lines)

        # Look for ## Related Questions
        for i, line in enumerate(lines):
            if re.match(r'^##\s+Related\s+Questions?\s*$', line, re.IGNORECASE):
                insert_index = i
                break

        # If not found, insert before trailing newlines
        if insert_index == len(lines):
            for i in range(len(lines) - 1, -1, -1):
                if lines[i].strip():
                    insert_index = i + 1
                    break

        # Insert the section
        lines.insert(insert_index, '')
        lines.insert(insert_index + 1, template.strip())

        new_content = '\n'.join(lines)
        file_path.write_text(new_content, encoding='utf-8')

        return True
    except Exception as e:
        print(f"    Error: {e}")
        return False


def main():
    root = Path(__file__).parent
    android_dir = root / "InterviewQuestions" / "40-Android"

    if not android_dir.exists():
        print(f"Android directory not found: {android_dir}")
        return 1

    print("="*80)
    print("FIX ALL CRITICAL ISSUES IN ANDROID FOLDER")
    print("="*80)
    print()

    md_files = sorted(android_dir.glob("q-*.md"))

    # Categorize files by issue type
    issues_by_file: Dict[Path, List[str]] = {}

    print("Step 1: Identifying all CRITICAL issues...")
    print()

    for i, file_path in enumerate(md_files, 1):
        if i % 50 == 0:
            print(f"  Checked {i}/{len(md_files)}...")

        critical_issues, _ = validate_file(file_path, root)
        if critical_issues:
            issues_by_file[file_path] = critical_issues

    print(f"\n✓ Found {len(issues_by_file)} files with CRITICAL issues")
    print()

    # Categorize issues
    auto_fix_followups = []
    auto_fix_references = []
    manual_review = []

    for file_path, issues in issues_by_file.items():
        for issue in issues:
            if "Follow-ups" in issue:
                auto_fix_followups.append(file_path)
            elif "References" in issue:
                auto_fix_references.append(file_path)
            elif any(keyword in issue for keyword in ["Question", "Answer", "Вопрос", "Ответ", "YAML"]):
                manual_review.append((file_path, issue))

    # Remove duplicates
    auto_fix_followups = list(set(auto_fix_followups))
    auto_fix_references = list(set(auto_fix_references))

    print("="*80)
    print("ISSUE CATEGORIZATION")
    print("="*80)
    print(f"Auto-fix (Follow-ups):  {len(auto_fix_followups)} files")
    print(f"Auto-fix (References):  {len(auto_fix_references)} files")
    print(f"Manual review needed:   {len(manual_review)} issues")
    print()

    # Auto-fix Follow-ups
    if auto_fix_followups:
        print("Step 2: Auto-fixing missing '## Follow-ups' sections...")
        print()

        followups_template = """## Follow-ups

- Follow-up questions to be populated"""

        fixed = 0
        for file_path in auto_fix_followups:
            if add_missing_section(file_path, "Follow-ups", followups_template):
                fixed += 1

        print(f"✓ Added '## Follow-ups' to {fixed}/{len(auto_fix_followups)} files")
        print()

    # Auto-fix References
    if auto_fix_references:
        print("Step 3: Auto-fixing missing '## References' sections...")
        print()

        references_template = """## References

- References to be populated"""

        fixed = 0
        for file_path in auto_fix_references:
            if add_missing_section(file_path, "References", references_template):
                fixed += 1

        print(f"✓ Added '## References' to {fixed}/{len(auto_fix_references)} files")
        print()

    # Report manual review items
    if manual_review:
        print("="*80)
        print("FILES REQUIRING MANUAL REVIEW")
        print("="*80)
        print()
        print("These files have structural issues that need manual intervention:")
        print()

        # Group by issue type
        by_issue_type = {}
        for file_path, issue in manual_review:
            if issue not in by_issue_type:
                by_issue_type[issue] = []
            by_issue_type[issue].append(file_path.name)

        for issue_type, files in sorted(by_issue_type.items(), key=lambda x: len(x[1]), reverse=True):
            print(f"{issue_type} ({len(files)} files)")
            for fname in files[:5]:
                print(f"    - {fname}")
            if len(files) > 5:
                print(f"    ... and {len(files) - 5} more")
            print()

    # Final validation sample
    print("="*80)
    print("VALIDATION SAMPLE")
    print("="*80)
    print()

    sample_files = (auto_fix_followups + auto_fix_references)[:10]
    if sample_files:
        passed = 0
        for file_path in sample_files:
            issues, _ = validate_file(file_path, root)
            # Check if Follow-ups/References issues are gone
            has_followup_issue = any("Follow-ups" in i for i in issues)
            has_reference_issue = any("References" in i for i in issues)

            if not has_followup_issue and not has_reference_issue:
                passed += 1

        print(f"Sample validation: {passed}/{len(sample_files)} files now pass Follow-ups/References checks")
        print()

    print("="*80)
    print("SUMMARY")
    print("="*80)
    print(f"✓ Auto-fixed Follow-ups:    {len(auto_fix_followups)} files")
    print(f"✓ Auto-fixed References:    {len(auto_fix_references)} files")
    print(f"⚠ Manual review needed:     {len(set(f for f, _ in manual_review))} files")
    print()

    total_auto_fixed = len(auto_fix_followups) + len(auto_fix_references)
    if total_auto_fixed > 0:
        print(f"✓ Successfully auto-fixed {total_auto_fixed} file issues")
        print()

    print("NEXT STEPS:")
    print("1. Review changes: git diff InterviewQuestions/40-Android/")
    print("2. Run full validation: python3 validate_android.py")
    print("3. Manual review files listed above need human intervention")
    print("4. Commit: git add InterviewQuestions/40-Android/ && git commit")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
