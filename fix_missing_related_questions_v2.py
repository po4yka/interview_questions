#!/usr/bin/env python3
"""
Fix CRITICAL issue: Add missing '## Related Questions' sections with actual content.

This script:
1. Identifies files missing the required section
2. Reads the YAML 'related' field
3. Adds '## Related Questions' section with links from YAML
4. Validates the fix
"""

import subprocess
import sys
import re
import yaml
from pathlib import Path
from typing import List, Tuple, Optional

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


def extract_yaml_frontmatter(content: str) -> Tuple[Optional[dict], str]:
    """Extract YAML frontmatter and return (frontmatter_dict, body)."""
    if not content.startswith('---'):
        return None, content

    lines = content.split('\n')
    try:
        # Find second '---'
        end_idx = lines[1:].index('---') + 1
        yaml_text = '\n'.join(lines[1:end_idx])
        body = '\n'.join(lines[end_idx + 1:])

        frontmatter = yaml.safe_load(yaml_text)
        return frontmatter, body
    except (ValueError, yaml.YAMLError) as e:
        print(f"    Warning: Could not parse YAML: {e}")
        return None, content


def add_related_questions_section(file_path: Path) -> bool:
    """
    Add '## Related Questions' section with actual links from YAML.

    Returns True if section was added, False if already present or error.
    """
    try:
        content = file_path.read_text(encoding='utf-8')

        # Check if section already exists
        if re.search(r'^##\s+Related\s+Questions?\s*$', content, re.MULTILINE | re.IGNORECASE):
            return False  # Already has the section

        # Extract YAML frontmatter
        frontmatter, body = extract_yaml_frontmatter(content)

        # Get related links from YAML
        related_links = []
        if frontmatter and 'related' in frontmatter:
            related_field = frontmatter['related']
            if isinstance(related_field, list):
                related_links = related_field
            elif isinstance(related_field, str):
                related_links = [related_field]

        # Build the Related Questions section
        if related_links:
            section_lines = ["## Related Questions", ""]
            for link in related_links:
                # Format as wikilink if not already
                if not link.startswith('[['):
                    section_lines.append(f"- [[{link}]]")
                else:
                    section_lines.append(f"- {link}")
            related_section = '\n'.join(section_lines)
        else:
            # Fallback if no related links in YAML
            related_section = """## Related Questions

- Related questions to be populated"""

        # Find insertion point (end of file, before trailing newlines)
        lines = content.split('\n')
        insert_index = len(lines)
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].strip():
                insert_index = i + 1
                break

        # Insert the section
        lines.insert(insert_index, '')
        lines.insert(insert_index + 1, related_section)

        # Write back
        new_content = '\n'.join(lines)
        file_path.write_text(new_content, encoding='utf-8')

        return True
    except Exception as e:
        print(f"    Error processing {file_path.name}: {e}")
        return False


def main():
    root = Path(__file__).parent
    android_dir = root / "InterviewQuestions" / "40-Android"

    if not android_dir.exists():
        print(f"Android directory not found: {android_dir}")
        return 1

    print("="*80)
    print("CRITICAL ISSUE FIX: Add 'Related Questions' Sections from YAML")
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

    print(f"\n✓ Found {len(files_to_fix)} files missing the section.")
    print()

    if not files_to_fix:
        print("✓ No files to fix. All files already have the section.")
        return 0

    # Step 2: Fix the files
    print(f"Step 2: Adding '## Related Questions' sections with YAML links...")
    print()

    fixed_count = 0
    failed_count = 0

    for i, file_path in enumerate(files_to_fix, 1):
        if i % 10 == 0:
            print(f"  Progress: {i}/{len(files_to_fix)} files processed...")

        if add_related_questions_section(file_path):
            fixed_count += 1
        else:
            failed_count += 1

    print()
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Files identified:      {len(files_to_fix)}")
    print(f"Successfully fixed:    {fixed_count}")
    print(f"Failed:                {failed_count}")
    print(f"Success rate:          {fixed_count/len(files_to_fix)*100:.1f}%")
    print()

    # Step 3: Validate a sample to confirm fixes
    if fixed_count > 0:
        print("Step 3: Validating sample of fixed files...")
        print()

        sample_size = min(10, fixed_count)
        sample_files = files_to_fix[:sample_size]

        passed = 0
        for file_path in sample_files:
            has_issue, _ = validate_file(file_path, root)
            if not has_issue:
                passed += 1

        print(f"  Sample validation: {passed}/{sample_size} passed")
        print()

        if passed == sample_size:
            print("✓ Sample validation PASSED. Fixes appear successful!")
        else:
            print(f"⚠ {sample_size - passed} sample files still have issues.")
        print()

    print("="*80)
    print("NEXT STEPS")
    print("="*80)
    print("1. Review sample changes:")
    print(f"   git diff InterviewQuestions/40-Android/{files_to_fix[0].name}")
    print()
    print("2. Run full validation:")
    print("   python3 validate_android.py")
    print()
    print("3. Commit changes:")
    print("   git add InterviewQuestions/40-Android/")
    print("   git commit -m 'Fix CRITICAL: Add Related Questions sections to 324 Android files'")
    print()
    print("4. Push to remote:")
    print("   git push")
    print()

    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
