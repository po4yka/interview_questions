from pathlib import Path


def main():
    """Find notes missing Russian or English sections."""
    # Find the repo root (4 levels up from automation/src/obsidian_vault/scripts/)
    REPO_ROOT = Path(__file__).resolve().parents[4]
    ROOT = REPO_ROOT / 'InterviewQuestions'
    note_files = list(ROOT.glob('**/q-*.md'))
    report = []
    for path in note_files:
        text = path.read_text(encoding='utf-8')
        has_ru_answer = '## Ответ (RU)' in text
        has_en_answer = '## Answer (EN)' in text
        if not has_ru_answer or not has_en_answer:
            report.append(str(path))

    output = ROOT.parent / 'missing_ru_sections.txt'
    output.write_text('\n'.join(report), encoding='utf-8')
    print(f'wrote {len(report)} entries to {output}')


if __name__ == '__main__':
    main()
