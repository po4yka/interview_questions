# Agent Checklist

**References**: AGENTS.md | TAXONOMY.md

## Critical Rules
- Both EN/RU in same file
- ONE topic from TAXONOMY.md
- English-only tags
- status: draft
- ≥1 MOC + ≥2 related links
- NO emoji, brackets, Russian tags

## Pre-Creation Checklist
- [ ] Valid topic from TAXONOMY.md
- [ ] Correct folder matches topic
- [ ] Template: _templates/_tpl-qna.md (Q&A), _tpl-concept.md (concept), _tpl-moc.md (MOC)
- [ ] Naming: q-<slug>--<topic>--<difficulty>.md | c-<slug>.md | moc-<topic>.md

## YAML Fields
- [ ] id: <subject>-<serial>
- [ ] title: "EN / RU" & aliases: [EN, RU]
- [ ] topic: ONE from TAXONOMY.md
- [ ] subtopics: [1-3 values]
- [ ] question_kind & difficulty
- [ ] language_tags: [en, ru]
- [ ] status: draft
- [ ] moc: moc-<topic> (no brackets)
- [ ] related: [c-*, q-*] (array, no brackets)
- [ ] created/updated: YYYY-MM-DD
- [ ] tags: [english-only, difficulty/*, android/*]

**YAML Format**: moc: moc-name | related: [item1, item2] | NO brackets

## Content Structure
- [ ] # Question (EN) & # Вопрос (RU)
- [ ] ## Answer (EN) & ## Ответ (RU)
- [ ] Equivalent content in both languages
- [ ] Code examples with complexity analysis
- [ ] Wikilinks: [[note-name]]
- [ ] Follow-ups & References sections

## Tags
- [ ] difficulty/easy|medium|hard
- [ ] android/* for Android subtopics
- [ ] English-only, kebab-case
- [ ] Namespaced: lang/*, platform/*, topic/*

## Links
- [ ] moc: moc-<topic> (no brackets)
- [ ] related: [c-*, q-*] (2+ items, array, no brackets)
- [ ] Content wikilinks: [[note-name]]
- [ ] Android: subtopics → android/* tags

## Validation
- [ ] File in correct folder
- [ ] No emoji, no trailing spaces
- [ ] Both languages present
- [ ] Equivalent EN/RU content

## References
- **AGENTS.md**: Detailed agent instructions
- **Vault-Rules/TAXONOMY.md**: Topics, subtopics, difficulty levels
- **_templates/**: Note templates
- **00-Administration/**: All administrative docs

**Last Updated**: 2025-11-08
