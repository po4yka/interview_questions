#!/usr/bin/env python3
"""Validate all Android notes and generate a summary."""

import subprocess
import sys
from pathlib import Path

def main():
    root = Path(__file__).parent
    android_dir = root / "InterviewQuestions" / "40-Android"

    if not android_dir.exists():
        print(f"Android directory not found: {android_dir}")
        return 1

    md_files = sorted(android_dir.glob("q-*.md"))
    print(f"Found {len(md_files)} Android Q&A files to validate\n")

    total = len(md_files)
    passed = 0
    failed = 0
    errors = []

    for i, file_path in enumerate(md_files, 1):
        rel_path = file_path.relative_to(root)
        print(f"[{i}/{total}] Validating {rel_path.name}...", end=" ")

        try:
            result = subprocess.run(
                ["uv", "run", "--project", "utils", "python", "-m", "utils.validate_note", str(rel_path), "--quiet"],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0 and "No issues" in result.stdout:
                print("✓ PASS")
                passed += 1
            else:
                print("✗ FAIL")
                failed += 1
                errors.append({
                    'file': rel_path.name,
                    'output': result.stdout + result.stderr
                })
        except subprocess.TimeoutExpired:
            print("✗ TIMEOUT")
            failed += 1
        except Exception as e:
            print(f"✗ ERROR: {e}")
            failed += 1

    print(f"\n{'='*80}")
    print("VALIDATION SUMMARY")
    print(f"{'='*80}")
    print(f"Total files:  {total}")
    print(f"Passed:       {passed} ({passed/total*100:.1f}%)")
    print(f"Failed:       {failed} ({failed/total*100:.1f}%)")

    if errors:
        print(f"\n{'='*80}")
        print("FAILED FILES (first 10)")
        print(f"{'='*80}")
        for error in errors[:10]:
            print(f"\n{error['file']}:")
            print(error['output'][:500])

    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
