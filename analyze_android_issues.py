#!/usr/bin/env python3
"""Analyze Android validation issues and categorize them."""

import subprocess
import sys
import re
from pathlib import Path
from collections import Counter, defaultdict

def main():
    root = Path(__file__).parent
    android_dir = root / "InterviewQuestions" / "40-Android"

    if not android_dir.exists():
        print(f"Android directory not found: {android_dir}")
        return 1

    md_files = sorted(android_dir.glob("q-*.md"))

    issue_categories = defaultdict(list)
    severity_counts = Counter()

    print(f"Analyzing {len(md_files)} Android files for detailed issue breakdown...")
    print(f"This may take a few minutes...\n")

    for i, file_path in enumerate(md_files, 1):
        if i % 50 == 0:
            print(f"  Analyzed {i}/{len(md_files)} files...")

        rel_path = file_path.relative_to(root)

        try:
            result = subprocess.run(
                ["uv", "run", "--project", "utils", "python", "-m", "utils.validate_note", str(rel_path)],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=30
            )

            # Parse output for issues
            lines = result.stdout.split('\n')
            in_issues = False

            for line in lines:
                line = line.strip()

                if 'Issues detected' in line:
                    in_issues = True
                    # Extract severity counts
                    match = re.findall(r'(CRITICAL|ERROR|WARNING): (\d+)', line)
                    for sev, count in match:
                        severity_counts[sev] += int(count)
                    continue

                if in_issues and line.startswith('- '):
                    # Extract issue type
                    issue = line[2:]  # Remove "- "

                    # Categorize
                    if 'Missing required heading' in issue:
                        issue_categories['Missing Required Headings'].append(file_path.name)
                    elif 'Wikilink' in issue and 'does not match' in issue:
                        # Extract link name
                        match = re.search(r'\[\[([^\]]+)\]\]', issue)
                        if match:
                            link = match.group(1)
                            issue_categories['Broken Wikilinks'].append((file_path.name, link))
                    elif 'Invalid Android subtopics' in issue:
                        # Extract invalid subtopics
                        match = re.search(r'Invalid Android subtopics: (.+?) \[', issue)
                        if match:
                            subtopics = match.group(1)
                            issue_categories['Invalid Android Subtopics'].append((file_path.name, subtopics))
                    elif 'Android tags must mirror subtopics' in issue:
                        issue_categories['Missing Android Tag Mirrors'].append(file_path.name)
                    elif 'related link' in issue and 'cannot be resolved' in issue:
                        match = re.search(r"'([^']+)'", issue)
                        if match:
                            link = match.group(1)
                            issue_categories['Broken Related Links (YAML)'].append((file_path.name, link))
                    elif 'Questions not formatted with blockquote' in issue:
                        issue_categories['Missing Blockquote Syntax'].append(file_path.name)
                    elif 'Generic type' in issue or 'not wrapped in backticks' in issue:
                        issue_categories['Code Formatting Issues'].append(file_path.name)
                    else:
                        issue_categories['Other Issues'].append((file_path.name, issue))

                if 'Passed checks:' in line:
                    in_issues = False

        except subprocess.TimeoutExpired:
            issue_categories['Timeout'].append(file_path.name)
        except Exception as e:
            issue_categories['Processing Error'].append((file_path.name, str(e)))

    # Generate report
    print(f"\n{'='*80}")
    print("ANDROID FOLDER VALIDATION ANALYSIS")
    print(f"{'='*80}\n")

    print(f"Total files analyzed: {len(md_files)}\n")

    print(f"{'='*80}")
    print("SEVERITY BREAKDOWN")
    print(f"{'='*80}")
    for severity in ['CRITICAL', 'ERROR', 'WARNING']:
        count = severity_counts.get(severity, 0)
        print(f"{severity:10} : {count:5} issues")
    print()

    print(f"{'='*80}")
    print("ISSUE CATEGORIES")
    print(f"{'='*80}\n")

    # Sort categories by frequency
    sorted_categories = sorted(issue_categories.items(), key=lambda x: len(x[1]), reverse=True)

    for category, issues in sorted_categories:
        print(f"{category}: {len(issues)} occurrences")

        if 'Wikilink' in category or 'Related' in category:
            # Show unique broken links
            unique_links = Counter([link for _, link in issues])
            print(f"  Top 10 broken links:")
            for link, count in unique_links.most_common(10):
                print(f"    - [[{link}]] ({count} files)")
        elif 'Invalid Android Subtopics' in category:
            # Show invalid subtopics
            all_subtopics = []
            for _, subtopics_str in issues:
                all_subtopics.extend([s.strip() for s in subtopics_str.split(',')])
            unique_subtopics = Counter(all_subtopics)
            print(f"  Invalid subtopics found:")
            for subtopic, count in unique_subtopics.most_common():
                print(f"    - {subtopic} ({count} files)")
        elif len(issues) <= 15:
            # Show all files for smaller categories
            for item in issues[:15]:
                if isinstance(item, tuple):
                    print(f"    - {item[0]}: {item[1][:80]}")
                else:
                    print(f"    - {item}")
        else:
            # Show sample for large categories
            print(f"  Sample files (first 10):")
            for item in issues[:10]:
                if isinstance(item, tuple):
                    print(f"    - {item[0]}")
                else:
                    print(f"    - {item}")
        print()

    print(f"{'='*80}")
    print("RECOMMENDATIONS")
    print(f"{'='*80}")
    print("""
1. HIGH PRIORITY - Fix Missing Required Headings (CRITICAL)
   - Add "## Related Questions" sections to affected files

2. HIGH PRIORITY - Fix Invalid Android Subtopics (ERROR)
   - Update subtopics to use valid values from TAXONOMY.md
   - Ensure tags mirror the corrected subtopics

3. MEDIUM PRIORITY - Fix Broken Wikilinks (ERROR)
   - Create missing concept notes (c-*.md files)
   - Or update links to existing files

4. MEDIUM PRIORITY - Fix Broken Related Links (ERROR)
   - Update YAML 'related' field to point to existing files
   - Or create the missing related question files

5. LOW PRIORITY - Code Formatting (WARNING)
   - Wrap generic types in backticks to prevent HTML interpretation
   - Ensure blockquote syntax for questions
""")

    return 0

if __name__ == "__main__":
    sys.exit(main())
