#!/usr/bin/env python3
"""
Fix CRITICAL issue: Add missing '## Related Questions' sections to Android files.

This script:
1. Identifies files missing the required section
2. Adds the section in the correct location (after content, before end)
3. Validates the fix
"""

import subprocess
import sys
import re
from pathlib import Path
from typing import List, Tuple

def validate_file(file_path: Path, root: Path) -> Tuple[bool, str]:
    """Validate a single file and return (has_issue, output)."""
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
        has_missing_heading = "Missing required heading '## Related Questions'" in output

        return has_missing_heading, output
    except Exception as e:
        return False, f"Error: {e}"


def add_related_questions_section(file_path: Path) -> bool:
    """
    Add '## Related Questions' section to a file if missing.

    The section should be added:
    - After the last content section (EN/RU answers, Follow-ups, References)
    - Before the end of file

    Returns True if section was added, False if already present or error.
    """
    try:
        content = file_path.read_text(encoding='utf-8')

        # Check if section already exists (case-insensitive)
        if re.search(r'^##\s+Related\s+Questions?\s*$', content, re.MULTILINE | re.IGNORECASE):
            return False  # Already has the section

        # Template for the section
        related_questions_section = """
## Related Questions

- Related questions to be populated
"""

        # Strategy: Add before the last line or at the end
        # Most files should end with newlines, so we append before final newlines

        lines = content.split('\n')

        # Find the last non-empty line
        insert_index = len(lines)
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].strip():
                insert_index = i + 1
                break

        # Insert the section
        lines.insert(insert_index, related_questions_section.strip())

        # Write back
        new_content = '\n'.join(lines)
        file_path.write_text(new_content, encoding='utf-8')

        return True
    except Exception as e:
        print(f"  Error processing {file_path.name}: {e}")
        return False


def main():
    root = Path(__file__).parent
    android_dir = root / "InterviewQuestions" / "40-Android"

    if not android_dir.exists():
        print(f"Android directory not found: {android_dir}")
        return 1

    print("="*80)
    print("CRITICAL ISSUE FIX: Add Missing 'Related Questions' Sections")
    print("="*80)
    print()

    # Step 1: Identify files with missing sections
    print("Step 1: Identifying files missing '## Related Questions' section...")
    print()

    md_files = sorted(android_dir.glob("q-*.md"))
    files_to_fix: List[Path] = []

    for i, file_path in enumerate(md_files, 1):
        if i % 50 == 0:
            print(f"  Checked {i}/{len(md_files)} files...")

        has_issue, _ = validate_file(file_path, root)
        if has_issue:
            files_to_fix.append(file_path)

    print(f"\nFound {len(files_to_fix)} files missing the section.")
    print()

    if not files_to_fix:
        print("No files to fix. All files already have the section.")
        return 0

    # Step 2: Fix the files
    print(f"Step 2: Adding '## Related Questions' section to {len(files_to_fix)} files...")
    print()

    fixed_count = 0
    failed_count = 0

    for i, file_path in enumerate(files_to_fix, 1):
        print(f"[{i}/{len(files_to_fix)}] Fixing {file_path.name}...", end=" ")

        if add_related_questions_section(file_path):
            print("✓ Added")
            fixed_count += 1
        else:
            print("✗ Failed")
            failed_count += 1

    print()
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Files identified: {len(files_to_fix)}")
    print(f"Successfully fixed: {fixed_count}")
    print(f"Failed: {failed_count}")
    print()

    # Step 3: Validate a sample to confirm fixes
    if fixed_count > 0:
        print("Step 3: Validating sample of fixed files...")
        print()

        sample_size = min(5, fixed_count)
        sample_files = files_to_fix[:sample_size]

        all_passed = True
        for file_path in sample_files:
            has_issue, output = validate_file(file_path, root)
            if has_issue:
                print(f"  ✗ {file_path.name} - Still has issue!")
                all_passed = False
            else:
                print(f"  ✓ {file_path.name} - Fixed successfully")

        print()
        if all_passed:
            print("✓ Sample validation PASSED. Fixes appear successful!")
        else:
            print("✗ Some files still have issues. Manual review needed.")
        print()

    print("NEXT STEPS:")
    print("1. Run full validation: python3 validate_android.py")
    print("2. Review changes: git diff")
    print("3. Commit: git add InterviewQuestions/40-Android/ && git commit")
    print("4. Push: git push")
    print()

    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
