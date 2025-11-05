#!/usr/bin/env python3
"""Identify all types of CRITICAL issues in Android folder."""

import subprocess
import sys
from pathlib import Path
from collections import defaultdict

def main():
    root = Path(__file__).parent
    android_dir = root / "InterviewQuestions" / "40-Android"

    md_files = sorted(android_dir.glob("q-*.md"))

    critical_issues_by_type = defaultdict(list)
    total_critical = 0

    print(f"Analyzing {len(md_files)} Android files for CRITICAL issues...")
    print()

    for i, file_path in enumerate(md_files, 1):
        if i % 50 == 0:
            print(f"  Checked {i}/{len(md_files)}...")

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

            if "CRITICAL:" in output:
                # Parse the output to find CRITICAL issues
                lines = output.split('\n')
                for line in lines:
                    if line.strip().startswith('- CRITICAL:'):
                        issue_text = line.strip()[12:].strip()  # Remove "- CRITICAL: "
                        critical_issues_by_type[issue_text].append(file_path.name)
                        total_critical += 1

        except Exception as e:
            pass

    print()
    print("="*80)
    print("CRITICAL ISSUES BY TYPE")
    print("="*80)
    print()

    # Sort by frequency
    sorted_issues = sorted(critical_issues_by_type.items(), key=lambda x: len(x[1]), reverse=True)

    for issue_type, files in sorted_issues:
        print(f"{issue_type}")
        print(f"  Count: {len(files)} files")
        print(f"  Sample files:")
        for fname in files[:5]:
            print(f"    - {fname}")
        print()

    print("="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total CRITICAL issues: {total_critical}")
    print(f"Unique issue types: {len(critical_issues_by_type)}")
    print(f"Files affected: {sum(len(v) for v in critical_issues_by_type.values())}")
    print()

    return 0

if __name__ == "__main__":
    sys.exit(main())
