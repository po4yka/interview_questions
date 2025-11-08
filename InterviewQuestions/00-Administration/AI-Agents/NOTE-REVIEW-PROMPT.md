# Note Review Prompt

**Purpose**: Automate note validation and fixes with senior review oversight.

## Process
1. Define scope: folder or specific files
2. For each note: validate → fix → re-validate → present results
3. Wait for reviewer confirmation before proceeding
4. Track progress with checkboxes

## Validation Commands
```bash
uv sync --project utils  # one-time setup
uv run --project utils python -m utils.validate_note <path>
```

## Key Rules
- Flag folder mismatches but don't auto-move files
- Interpret validator output to fix issues
- Present results clearly for senior review

## Common Issues & Fixes
- **Missing YAML fields**: Add required fields (moc, related, etc.)
- **Invalid topics**: Check TAXONOMY.md for valid values
- **Blockquote missing**: Add `>` before questions
- **Code formatting**: Wrap generics in backticks
- **Broken links**: Fix wikilink syntax [[note-name]]

## Completion Checklist
- [ ] Pre/post validation executed
- [ ] YAML normalized to schema
- [ ] RU/EN content aligned with RU first
- [ ] Questions use blockquote syntax (`>`)
- [ ] Code properly formatted with backticks
- [ ] Content technically accurate for senior devs
- [ ] Follow-ups, References, Related Questions populated
- [ ] All validations pass

**Note**: Wait for reviewer confirmation before proceeding to next note.
```
