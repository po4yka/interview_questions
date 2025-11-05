#!/usr/bin/env python3
"""
Force-update ALL References sections with specific documentation links.

Replaces generic https://developer.android.com/docs with specific links
based on subtopics in YAML frontmatter.
"""

import sys
import re
import yaml
from pathlib import Path
from typing import Optional, Tuple, List

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
    reference_map = {
        # UI
        'ui-compose': 'https://developer.android.com/develop/ui/compose',
        'ui-views': 'https://developer.android.com/develop/ui/views',
        'ui-custom-views': 'https://developer.android.com/develop/ui/views/layout/custom-views',
        'ui-fragments': 'https://developer.android.com/guide/fragments',
        'ui-activities': 'https://developer.android.com/guide/components/activities',
        'ui-recyclerview': 'https://developer.android.com/develop/ui/views/layout/recyclerview',
        'ui-navigation': 'https://developer.android.com/guide/navigation',
        'ui-animation': 'https://developer.android.com/develop/ui/views/animations',
        'ui-graphics': 'https://developer.android.com/develop/ui/views/graphics',
        'ui-accessibility': 'https://developer.android.com/guide/topics/ui/accessibility',
        'ui-theming': 'https://developer.android.com/develop/ui/views/theming',
        'ui-state': 'https://developer.android.com/topic/architecture/ui-layer',
        'compose': 'https://developer.android.com/develop/ui/compose',
        'compose-multiplatform': 'https://www.jetbrains.com/lp/compose-multiplatform/',

        # Architecture
        'lifecycle': 'https://developer.android.com/topic/libraries/architecture/lifecycle',
        'architecture-mvvm': 'https://developer.android.com/topic/architecture',
        'architecture-mvi': 'https://developer.android.com/topic/architecture',
        'architecture-clean': 'https://developer.android.com/topic/architecture',
        'architecture-modularization': 'https://developer.android.com/topic/modularization',
        'architecture-components': 'https://developer.android.com/topic/architecture',
        'viewmodel': 'https://developer.android.com/topic/libraries/architecture/viewmodel',
        'livedata': 'https://developer.android.com/topic/libraries/architecture/livedata',
        'activity': 'https://developer.android.com/guide/components/activities',

        # Data
        'room': 'https://developer.android.com/training/data-storage/room',
        'data-room': 'https://developer.android.com/training/data-storage/room',
        'datastore': 'https://developer.android.com/topic/libraries/architecture/datastore',
        'data-datastore': 'https://developer.android.com/topic/libraries/architecture/datastore',
        'data-persistence': 'https://developer.android.com/training/data-storage',
        'cache-offline': 'https://developer.android.com/training/data-storage',
        'files-media': 'https://developer.android.com/training/data-storage/shared',
        'serialization': 'https://developer.android.com/guide/topics/data',

        # Networking
        'networking': 'https://developer.android.com/training/basics/network-ops',
        'networking-http': 'https://developer.android.com/training/basics/network-ops/connecting',
        'network-security-config': 'https://developer.android.com/training/articles/security-config',

        # Concurrency
        'coroutines': 'https://developer.android.com/kotlin/coroutines',
        'concurrency-coroutines': 'https://developer.android.com/kotlin/coroutines',
        'concurrency-threading': 'https://developer.android.com/guide/background/threading',
        'threads-sync': 'https://developer.android.com/guide/background/threading',

        # Dependency Injection
        'di-dagger': 'https://developer.android.com/training/dependency-injection/dagger-basics',
        'di-hilt': 'https://developer.android.com/training/dependency-injection/hilt-android',
        'di-koin': 'https://insert-koin.io/docs/reference/introduction',

        # Testing
        'testing-unit': 'https://developer.android.com/training/testing/local-tests',
        'testing-ui': 'https://developer.android.com/training/testing/ui-testing',
        'testing-instrumented': 'https://developer.android.com/training/testing/instrumented-tests',
        'testing-integration': 'https://developer.android.com/training/testing/integration-testing',
        'testing-benchmark': 'https://developer.android.com/topic/performance/benchmarking',

        # Background
        'background-workmanager': 'https://developer.android.com/topic/libraries/architecture/workmanager',
        'background-services': 'https://developer.android.com/develop/background-work/services',
        'background-execution': 'https://developer.android.com/develop/background-work',
        'background-jobs': 'https://developer.android.com/topic/performance/scheduling',
        'service': 'https://developer.android.com/develop/background-work/services',
        'foreground-services': 'https://developer.android.com/develop/background-work/services/foreground-services',
        'broadcast-receiver': 'https://developer.android.com/guide/components/broadcasts',
        'content-provider': 'https://developer.android.com/guide/topics/providers/content-providers',

        # Performance
        'performance-optimization': 'https://developer.android.com/topic/performance',
        'performance-memory': 'https://developer.android.com/topic/performance/memory-overview',
        'performance-rendering': 'https://developer.android.com/topic/performance/rendering',
        'performance-startup': 'https://developer.android.com/topic/performance/vitals/launch-time',
        'profiling': 'https://developer.android.com/studio/profile',
        'strictmode-anr': 'https://developer.android.com/topic/performance/vitals/anr',
        'app-startup': 'https://developer.android.com/topic/libraries/app-startup',

        # Security
        'keystore-crypto': 'https://developer.android.com/training/articles/keystore',
        'security': 'https://developer.android.com/topic/security',
        'privacy-sdks': 'https://developer.android.com/privacy',

        # Navigation
        'navigation': 'https://developer.android.com/guide/navigation',
        'intents-deeplinks': 'https://developer.android.com/training/app-links',

        # Notifications & Communication
        'notifications': 'https://developer.android.com/develop/ui/views/notifications',
        'communication': 'https://developer.android.com/training/sharing',
        'sharing': 'https://developer.android.com/training/sharing',
        'shortcuts': 'https://developer.android.com/develop/ui/views/launch/shortcuts',

        # Media
        'media': 'https://developer.android.com/media',
        'camera': 'https://developer.android.com/media/camera',
        'camerax': 'https://developer.android.com/training/camerax',
        'imaging': 'https://developer.android.com/media/images',
        'graphics': 'https://developer.android.com/develop/ui/views/graphics',
        'animations': 'https://developer.android.com/develop/ui/views/animations',

        # Localization
        'i18n-l10n': 'https://developer.android.com/guide/topics/resources/localization',
        'accessibility': 'https://developer.android.com/guide/topics/ui/accessibility',

        # Build & Deploy
        'gradle': 'https://developer.android.com/build',
        'gradle-build': 'https://developer.android.com/build',
        'build-variants': 'https://developer.android.com/build/build-variants',
        'ci-cd': 'https://developer.android.com/studio/publish',
        'release-engineering': 'https://developer.android.com/studio/publish',
        'app-bundle': 'https://developer.android.com/guide/app-bundle',
        'static-analysis': 'https://developer.android.com/studio/write/lint',
        'dependency-management': 'https://developer.android.com/build/dependencies',
        'play-console': 'https://developer.android.com/distribute/console',

        # Platform Features
        'permissions': 'https://developer.android.com/guide/topics/permissions',
        'sensors': 'https://developer.android.com/guide/topics/sensors',
        'location': 'https://developer.android.com/training/location',
        'bluetooth': 'https://developer.android.com/guide/topics/connectivity/bluetooth',
        'processes': 'https://developer.android.com/guide/components/processes-and-threads',

        # Specialized
        'android-auto': 'https://developer.android.com/training/cars',
        'automotive': 'https://developer.android.com/training/cars',
        'tv': 'https://developer.android.com/training/tv',
        'leanback': 'https://developer.android.com/training/tv',
        'chromeos': 'https://developer.android.com/chromeos',
        'desktop': 'https://developer.android.com/topic/arc',
        'arcore': 'https://developers.google.com/ar',
        'xr': 'https://developers.google.com/ar',
        '3d': 'https://developer.android.com/develop/ui/views/graphics/opengl',
        'adaptive-ui': 'https://developer.android.com/guide/topics/large-screens',
        'bubbles': 'https://developer.android.com/develop/ui/views/notifications/bubbles',
        'enterprise': 'https://developer.android.com/work',
        'mdm': 'https://developer.android.com/work',
        'kmp': 'https://kotlinlang.org/docs/multiplatform.html',
        'billing': 'https://developer.android.com/google/play/billing',
        'analytics': 'https://firebase.google.com/docs/analytics',
        'ab-testing': 'https://firebase.google.com/docs/ab-testing',
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


def has_generic_reference(content: str) -> bool:
    """Check if References section has only generic link."""
    pattern = r'^## References\n+(.*?)(?=\n^##|\Z)'
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)

    if not match:
        return False

    section_content = match.group(1).strip()

    # Check if it only has the generic link
    lines = [l.strip() for l in section_content.split('\n') if l.strip()]

    # If only one line and it's the generic docs link
    if len(lines) == 1 and 'developer.android.com/docs' in lines[0]:
        return True

    return False


def update_references(file_path: Path) -> Tuple[bool, str]:
    """Update References section with specific links."""
    try:
        content = file_path.read_text(encoding='utf-8')

        # Extract frontmatter
        frontmatter, _ = extract_yaml_frontmatter(content)

        if not frontmatter:
            return False, "No YAML frontmatter"

        topic = frontmatter.get('topic', '')
        subtopics = frontmatter.get('subtopics', [])

        if not isinstance(subtopics, list):
            subtopics = [subtopics] if subtopics else []

        # Generate references
        if topic == 'android':
            refs = get_android_references(subtopics)
        elif topic == 'kotlin':
            refs = [
                'https://kotlinlang.org/docs/',
                'https://developer.android.com/kotlin'
            ]
        else:
            refs = ['https://developer.android.com/docs']

        # Build new section
        refs_lines = ["## References", ""]
        for ref in refs:
            refs_lines.append(f"- {ref}")

        new_section = '\n'.join(refs_lines)

        # Replace in content
        pattern = r'^## References\n+.*?(?=\n^##|\Z)'

        if re.search(pattern, content, re.MULTILINE | re.DOTALL):
            new_content = re.sub(
                pattern,
                new_section + '\n\n',
                content,
                flags=re.MULTILINE | re.DOTALL
            )
            file_path.write_text(new_content, encoding='utf-8')
            return True, f"Updated with {len(refs)} specific references"

        return False, "No References section found"

    except Exception as e:
        return False, f"Error: {e}"


def main():
    root = Path(__file__).parent
    android_dir = root / "InterviewQuestions" / "40-Android"

    print("="*80)
    print("UPDATE REFERENCES TO SPECIFIC DOCUMENTATION LINKS")
    print("="*80)
    print()

    md_files = sorted(android_dir.glob("q-*.md"))

    # Find files with generic references
    files_to_update = []

    print("Step 1: Finding files with generic references...")
    print()

    for i, file_path in enumerate(md_files, 1):
        if i % 50 == 0:
            print(f"  Checked {i}/{len(md_files)}...")

        content = file_path.read_text(encoding='utf-8')
        if has_generic_reference(content):
            files_to_update.append(file_path)

    print()
    print(f"✓ Found {len(files_to_update)} files with generic references")
    print()

    if not files_to_update:
        print("No files need updating!")
        return 0

    # Update all files
    print(f"Step 2: Updating {len(files_to_update)} files with specific links...")
    print()

    success = 0
    improved = 0  # Files that got more specific links

    for i, file_path in enumerate(files_to_update, 1):
        if i % 10 == 0:
            print(f"  Progress: {i}/{len(files_to_update)}...")

        ok, msg = update_references(file_path)
        if ok:
            success += 1
            # Check if we added more than just the generic link
            if "specific" in msg:
                num_refs = int(msg.split()[2])
                if num_refs > 1:
                    improved += 1

    print()
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Files updated:          {success}/{len(files_to_update)}")
    print(f"With specific links:    {improved}")
    print(f"Still generic only:     {success - improved}")
    print()

    print("NEXT STEPS:")
    print("1. Review sample:")
    if files_to_update:
        print(f"   git diff InterviewQuestions/40-Android/{files_to_update[0].name}")
    print()
    print("2. Commit:")
    print("   git add InterviewQuestions/40-Android/")
    print('   git commit -m "Update References with specific documentation links"')
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
