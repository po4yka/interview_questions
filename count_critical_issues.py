#!/usr/bin/env python3
"""Count CRITICAL issues remaining in Android folder."""

import subprocess
import sys
from pathlib import Path
from collections import Counter

def main():
    root = Path(__file__).parent
    android_dir = root / "InterviewQuestions" / "40-Android"

    md_files = sorted(android_dir.glob("q-*.md"))

    severity_counts = Counter()
    files_with_critical = []

    print(f"Checking {len(md_files)} Android files for CRITICAL issues...")
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

            # Count severity mentions
            if "CRITICAL:" in output:
                import re
                match = re.search(r'CRITICAL: (\d+)', output)
                if match:
                    count = int(match.group(1))
                    severity_counts['CRITICAL'] += count
                    files_with_critical.append(file_path.name)

            if "ERROR:" in output:
                import re
                match = re.search(r'ERROR: (\d+)', output)
                if match:
                    count = int(match.group(1))
                    severity_counts['ERROR'] += count

            if "WARNING:" in output:
                import re
                match = re.search(r'WARNING: (\d+)', output)
                if match:
                    count = int(match.group(1))
                    severity_counts['WARNING'] += count

        except Exception as e:
            pass

    print()
    print("="*80)
    print("ISSUE SEVERITY BREAKDOWN")
    print("="*80)
    print(f"CRITICAL:  {severity_counts['CRITICAL']:4} issues")
    print(f"ERROR:     {severity_counts['ERROR']:4} issues")
    print(f"WARNING:   {severity_counts['WARNING']:4} issues")
    print(f"TOTAL:     {sum(severity_counts.values()):4} issues")
    print()

    print(f"Files with CRITICAL issues: {len(files_with_critical)}")
    if files_with_critical:
        print()
        print("First 10 files with CRITICAL issues:")
        for fname in files_with_critical[:10]:
            print(f"  - {fname}")

    print()
    if severity_counts['CRITICAL'] == 0:
        print("✓ SUCCESS: All CRITICAL issues have been fixed!")
    else:
        print(f"⚠ {severity_counts['CRITICAL']} CRITICAL issues remain")

    return 0

if __name__ == "__main__":
    sys.exit(main())
