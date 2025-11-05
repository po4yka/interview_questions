#!/usr/bin/env python3
"""
Populate Follow-ups and References sections with actual content.

Strategy:
- Follow-ups: Suggest related questions based on subtopics and difficulty
- References: Add official documentation links based on topic and subtopics
"""

import subprocess
import sys
import re
import yaml
from pathlib import Path
from typing import Optional, Tuple, List, Dict

def extract_yaml_frontmatter(content: str) -> Tuple[Optional[dict], str]:
    """Extract YAML frontmatter."""
    if not content.startswith('---'):
        return None, content

    lines = content.split('\n')
    try:
        end_idx = lines[1:].index('---') + 1
        yaml_text = '\n'.join(lines[1:end_idx])
        body = '\n'.join(lines[end_idx + 1:])
        frontmatter = yaml.safe_load(yaml_text)
        return frontmatter, body
    except (ValueError, yaml.YAMLError):
        return None, content


def get_android_references(subtopics: List[str]) -> List[str]:
    """Generate Android documentation references based on subtopics."""
    # Map subtopics to official documentation
    reference_map = {
        'ui-compose': 'https://developer.android.com/develop/ui/compose',
        'ui-views': 'https://developer.android.com/develop/ui/views',
        'ui-custom-views': 'https://developer.android.com/develop/ui/views/layout/custom-views',
        'ui-fragments': 'https://developer.android.com/guide/fragments',
        'ui-activities': 'https://developer.android.com/guide/components/activities',
        'lifecycle': 'https://developer.android.com/topic/libraries/architecture/lifecycle',
        'architecture-mvvm': 'https://developer.android.com/topic/architecture',
        'architecture-mvi': 'https://developer.android.com/topic/architecture',
        'architecture-components': 'https://developer.android.com/topic/architecture',
        'data-room': 'https://developer.android.com/training/data-storage/room',
        'data-datastore': 'https://developer.android.com/topic/libraries/architecture/datastore',
        'data-persistence': 'https://developer.android.com/training/data-storage',
        'networking': 'https://developer.android.com/training/basics/network-ops',
        'network-security-config': 'https://developer.android.com/training/articles/security-config',
        'concurrency-coroutines': 'https://developer.android.com/kotlin/coroutines',
        'concurrency-threading': 'https://developer.android.com/guide/background/threading',
        'di-dagger': 'https://developer.android.com/training/dependency-injection/dagger-basics',
        'di-hilt': 'https://developer.android.com/training/dependency-injection/hilt-android',
        'di-koin': 'https://insert-koin.io/docs/reference/introduction',
        'testing-unit': 'https://developer.android.com/training/testing/local-tests',
        'testing-ui': 'https://developer.android.com/training/testing/ui-testing',
        'testing-integration': 'https://developer.android.com/training/testing/integration-testing',
        'background-workmanager': 'https://developer.android.com/topic/libraries/architecture/workmanager',
        'background-services': 'https://developer.android.com/develop/background-work/services',
        'background-jobs': 'https://developer.android.com/topic/performance/scheduling',
        'performance-optimization': 'https://developer.android.com/topic/performance',
        'performance-memory': 'https://developer.android.com/topic/performance/memory-overview',
        'performance-rendering': 'https://developer.android.com/topic/performance/rendering',
        'keystore-crypto': 'https://developer.android.com/training/articles/keystore',
        'security': 'https://developer.android.com/topic/security',
        'navigation': 'https://developer.android.com/guide/navigation',
        'intents-deeplinks': 'https://developer.android.com/training/app-links',
        'notifications': 'https://developer.android.com/develop/ui/views/notifications',
        'media': 'https://developer.android.com/media',
        'graphics': 'https://developer.android.com/develop/ui/views/graphics',
        'animations': 'https://developer.android.com/develop/ui/views/animations',
        'i18n-l10n': 'https://developer.android.com/guide/topics/resources/localization',
        'accessibility': 'https://developer.android.com/guide/topics/ui/accessibility',
        'gradle-build': 'https://developer.android.com/build',
        'ci-cd': 'https://developer.android.com/studio/publish',
        'app-bundle': 'https://developer.android.com/guide/app-bundle',
        'permissions': 'https://developer.android.com/guide/topics/permissions',
        'sensors': 'https://developer.android.com/guide/topics/sensors',
        'location': 'https://developer.android.com/training/location',
    }

    refs = []

    # Add specific docs for each subtopic
    for subtopic in subtopics:
        if subtopic in reference_map:
            refs.append(reference_map[subtopic])

    # If no specific refs found, add general Android docs
    if not refs:
        refs.append('https://developer.android.com/docs')

    return list(set(refs))  # Remove duplicates


def populate_followups(file_path: Path, frontmatter: dict, vault_dir: Path) -> Tuple[bool, str]:
    """Generate Follow-ups section based on file metadata."""

    # Get related files from YAML
    related = frontmatter.get('related', [])
    if isinstance(related, str):
        related = [related]

    if not related:
        return False, "No related questions in YAML"

    # Build Follow-ups section
    followups_lines = ["## Follow-ups", ""]

    # Add related questions as follow-ups
    for link in related[:3]:  # Max 3 follow-ups
        # Format as wikilink
        if not link.startswith('[['):
            followups_lines.append(f"- [[{link}]]")
        else:
            followups_lines.append(f"- {link}")

    followups_section = '\n'.join(followups_lines)

    # Replace in content
    content = file_path.read_text(encoding='utf-8')
    pattern = r'^## Follow-ups\n+.*?(?=\n^##|\Z)'

    if re.search(pattern, content, re.MULTILINE | re.DOTALL):
        new_content = re.sub(
            pattern,
            followups_section + '\n\n',
            content,
            flags=re.MULTILINE | re.DOTALL
        )
        file_path.write_text(new_content, encoding='utf-8')
        return True, f"Added {len(related[:3])} follow-ups"

    return False, "No Follow-ups section found"


def populate_references(file_path: Path, frontmatter: dict) -> Tuple[bool, str]:
    """Generate References section based on topic and subtopics."""

    topic = frontmatter.get('topic', '')
    subtopics = frontmatter.get('subtopics', [])

    if not isinstance(subtopics, list):
        subtopics = [subtopics] if subtopics else []

    # Generate references
    refs = []

    if topic == 'android':
        refs = get_android_references(subtopics)
    elif topic == 'kotlin':
        refs = [
            'https://kotlinlang.org/docs/',
            'https://developer.android.com/kotlin'
        ]
    else:
        refs = ['https://developer.android.com/docs']

    # Build References section
    refs_lines = ["## References", ""]
    for ref in refs:
        refs_lines.append(f"- {ref}")

    refs_section = '\n'.join(refs_lines)

    # Replace in content
    content = file_path.read_text(encoding='utf-8')
    pattern = r'^## References\n+.*?(?=\n^##|\Z)'

    if re.search(pattern, content, re.MULTILINE | re.DOTALL):
        new_content = re.sub(
            pattern,
            refs_section + '\n\n',
            content,
            flags=re.MULTILINE | re.DOTALL
        )
        file_path.write_text(new_content, encoding='utf-8')
        return True, f"Added {len(refs)} references"

    return False, "No References section found"


def has_template_text(content: str, section_name: str) -> bool:
    """Check if section has placeholder/template text."""
    pattern = rf'^## {re.escape(section_name)}\n+(.*?)(?=\n^##|\Z)'
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)

    if not match:
        return False

    section_content = match.group(1).strip()
    return 'to be populated' in section_content.lower()


def main():
    root = Path(__file__).parent
    android_dir = root / "InterviewQuestions" / "40-Android"

    print("="*80)
    print("POPULATE FOLLOW-UPS AND REFERENCES WITH ACTUAL CONTENT")
    print("="*80)
    print()

    md_files = sorted(android_dir.glob("q-*.md"))

    # Find files needing updates
    followups_to_fix = []
    references_to_fix = []

    print("Step 1: Identifying files with template sections...")
    print()

    for i, file_path in enumerate(md_files, 1):
        if i % 50 == 0:
            print(f"  Checked {i}/{len(md_files)}...")

        content = file_path.read_text(encoding='utf-8')

        if has_template_text(content, 'Follow-ups'):
            followups_to_fix.append(file_path)

        if has_template_text(content, 'References'):
            references_to_fix.append(file_path)

    print()
    print(f"✓ Found {len(followups_to_fix)} files with template Follow-ups")
    print(f"✓ Found {len(references_to_fix)} files with template References")
    print()

    # Process Follow-ups
    if followups_to_fix:
        print(f"Step 2: Populating {len(followups_to_fix)} Follow-ups sections...")
        print()

        success = 0
        failed = []

        for i, file_path in enumerate(followups_to_fix, 1):
            if i % 10 == 0:
                print(f"  Progress: {i}/{len(followups_to_fix)}...")

            frontmatter, _ = extract_yaml_frontmatter(file_path.read_text(encoding='utf-8'))
            if frontmatter:
                ok, msg = populate_followups(file_path, frontmatter, android_dir)
                if ok:
                    success += 1
                else:
                    failed.append((file_path.name, msg))

        print(f"\n✓ Populated {success}/{len(followups_to_fix)} Follow-ups sections")
        if failed:
            print(f"  Failed: {len(failed)} files (no related questions in YAML)")
        print()

    # Process References
    if references_to_fix:
        print(f"Step 3: Populating {len(references_to_fix)} References sections...")
        print()

        success = 0

        for i, file_path in enumerate(references_to_fix, 1):
            if i % 10 == 0:
                print(f"  Progress: {i}/{len(references_to_fix)}...")

            frontmatter, _ = extract_yaml_frontmatter(file_path.read_text(encoding='utf-8'))
            if frontmatter:
                ok, msg = populate_references(file_path, frontmatter)
                if ok:
                    success += 1

        print(f"\n✓ Populated {success}/{len(references_to_fix)} References sections")
        print()

    # Summary
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Follow-ups populated:   {len(followups_to_fix)} files")
    print(f"References populated:   {len(references_to_fix)} files")
    print(f"Total updates:          {len(followups_to_fix) + len(references_to_fix)}")
    print()

    print("NEXT STEPS:")
    print("1. Review sample changes:")
    if followups_to_fix:
        print(f"   git diff InterviewQuestions/40-Android/{followups_to_fix[0].name}")
    print()
    print("2. Commit:")
    print("   git add InterviewQuestions/40-Android/")
    print('   git commit -m "Populate Follow-ups and References with actual content"')
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
