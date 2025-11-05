#!/usr/bin/env python3
"""
Populate ALL '## Related Questions' sections with actual links from YAML.

Finds all files with empty/template Related Questions sections and populates
them with links from the YAML 'related' field.
"""

import subprocess
import sys
import re
import yaml
from pathlib import Path
from typing import Optional, Tuple, List

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
        return None, content


def has_empty_related_questions(content: str) -> bool:
    """Check if file has empty/template Related Questions section."""
    # Look for Related Questions section
    match = re.search(r'^## Related Questions\n+(.*?)(?=\n^##|\Z)', content, re.MULTILINE | re.DOTALL)

    if not match:
        return False  # No section at all

    section_content = match.group(1).strip()

    # Check if empty or contains template text
    if not section_content:
        return True

    if 'to be populated' in section_content.lower():
        return True

    # Check if has subsections (like ### Prerequisites)
    # These are manually curated and should NOT be touched
    if re.search(r'^###\s+', section_content, re.MULTILINE):
        return False  # Has subsections, don't touch

    # Check if has actual links
    if '[[' in section_content or 'http' in section_content:
        return False  # Has links

    return True  # Empty or placeholder


def populate_related_questions(file_path: Path) -> Tuple[bool, str]:
    """
    Populate Related Questions section with links from YAML.
    Returns (success, message)
    """
    try:
        content = file_path.read_text(encoding='utf-8')

        # Extract YAML
        frontmatter, body = extract_yaml_frontmatter(content)

        if not frontmatter or 'related' not in frontmatter:
            return False, "No 'related' field in YAML"

        related_field = frontmatter['related']
        if isinstance(related_field, str):
            related_links = [related_field]
        elif isinstance(related_field, list):
            related_links = related_field
        else:
            return False, f"Invalid 'related' field type: {type(related_field)}"

        if not related_links:
            return False, "Empty 'related' field"

        # Build new section content
        section_lines = ["## Related Questions", ""]
        for link in related_links:
            # Format as wikilink if not already
            if not link.startswith('[['):
                section_lines.append(f"- [[{link}]]")
            else:
                section_lines.append(f"- {link}")

        new_section = '\n'.join(section_lines)

        # Find and replace the Related Questions section
        # Pattern: from "## Related Questions" to next "##" or end
        pattern = r'^## Related Questions\n+.*?(?=\n^##|\Z)'

        if re.search(pattern, content, re.MULTILINE | re.DOTALL):
            # Replace existing section
            new_content = re.sub(
                pattern,
                new_section + '\n\n',
                content,
                flags=re.MULTILINE | re.DOTALL
            )

            file_path.write_text(new_content, encoding='utf-8')
            return True, f"Populated with {len(related_links)} links"
        else:
            return False, "No Related Questions section found"

    except Exception as e:
        return False, f"Error: {e}"


def main():
    root = Path(__file__).parent
    android_dir = root / "InterviewQuestions" / "40-Android"

    if not android_dir.exists():
        print(f"Android directory not found: {android_dir}")
        return 1

    print("="*80)
    print("POPULATE RELATED QUESTIONS WITH ACTUAL LINKS FROM YAML")
    print("="*80)
    print()

    md_files = sorted(android_dir.glob("q-*.md"))

    # Step 1: Find files with empty/template sections
    print("Step 1: Identifying files with empty/template Related Questions...")
    print()

    files_to_fix = []
    files_no_section = []
    files_already_populated = []

    for i, file_path in enumerate(md_files, 1):
        if i % 50 == 0:
            print(f"  Checked {i}/{len(md_files)}...")

        content = file_path.read_text(encoding='utf-8')

        if '## Related Questions' not in content:
            files_no_section.append(file_path)
        elif has_empty_related_questions(content):
            files_to_fix.append(file_path)
        else:
            files_already_populated.append(file_path)

    print()
    print(f"✓ Files with Related Questions section: {len(md_files) - len(files_no_section)}")
    print(f"  - Already populated: {len(files_already_populated)}")
    print(f"  - Empty/template (need fixing): {len(files_to_fix)}")
    print(f"  - No section at all: {len(files_no_section)}")
    print()

    if not files_to_fix:
        print("✓ All Related Questions sections are already populated!")
        return 0

    # Step 2: Populate empty sections
    print(f"Step 2: Populating {len(files_to_fix)} empty sections with YAML links...")
    print()

    success_count = 0
    no_yaml_links = []
    failed = []

    for i, file_path in enumerate(files_to_fix, 1):
        if i % 10 == 0:
            print(f"  Progress: {i}/{len(files_to_fix)}...")

        success, message = populate_related_questions(file_path)

        if success:
            success_count += 1
        elif "No 'related' field" in message or "Empty 'related'" in message:
            no_yaml_links.append(file_path.name)
        else:
            failed.append((file_path.name, message))

    print()
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Files processed:         {len(files_to_fix)}")
    print(f"Successfully populated:  {success_count}")
    print(f"No YAML links:           {len(no_yaml_links)}")
    print(f"Failed:                  {len(failed)}")
    print()

    if no_yaml_links:
        print("Files without YAML 'related' field (first 10):")
        for fname in no_yaml_links[:10]:
            print(f"  - {fname}")
        if len(no_yaml_links) > 10:
            print(f"  ... and {len(no_yaml_links) - 10} more")
        print()

    if failed:
        print("Files that failed (first 5):")
        for fname, msg in failed[:5]:
            print(f"  - {fname}: {msg}")
        print()

    # Step 3: Validation sample
    if success_count > 0:
        print("Step 3: Validating sample...")
        print()

        sample = files_to_fix[:min(5, len(files_to_fix))]
        for file_path in sample:
            content = file_path.read_text(encoding='utf-8')
            if has_empty_related_questions(content):
                print(f"  ✗ {file_path.name} - Still empty!")
            else:
                print(f"  ✓ {file_path.name} - Now populated")
        print()

    print("="*80)
    print("NEXT STEPS")
    print("="*80)
    print("1. Review changes:")
    if files_to_fix:
        print(f"   git diff InterviewQuestions/40-Android/{files_to_fix[0].name}")
    print()
    print("2. Validate:")
    print("   python3 validate_android.py")
    print()
    print("3. Commit:")
    print("   git add InterviewQuestions/40-Android/")
    print('   git commit -m "Populate Related Questions sections with YAML links"')
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
