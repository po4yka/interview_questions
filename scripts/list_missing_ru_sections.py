from pathlib import Path

ROOT = Path('InterviewQuestions')
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
