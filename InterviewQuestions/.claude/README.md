# Claude Code Configuration for Interview Questions Vault

**Purpose**: Claude Code Skills and configuration for maintaining this bilingual Obsidian interview questions vault.

**Version**: 2.0
**Last Updated**: 2025-01-05

---

## Overview

This directory contains Claude Code configuration for automated vault maintenance:

- **Custom Instructions**: Auto-loaded brief context (`custom_instructions.md`)
- **Skills**: 17 specialized skills for common workflows (`skills/`)
- **Documentation**: This README

---

## Directory Structure

```
.claude/
├── README.md                           # This file
├── custom_instructions.md              # Auto-loaded context (~500 tokens)
└── skills/                             # Skills directory (17 skills)
    │
    │   # Original Skills (Content Creation)
    ├── obsidian-qna-creator/           # Create Q&A notes
    │   ├── SKILL.md
    │   └── core/
    │       ├── taxonomy_validator.py
    │       ├── filename_generator.py
    │       └── yaml_builder.py
    ├── obsidian-validator/             # Validate single notes
    │   ├── SKILL.md
    │   └── core/
    │       ├── validator.py
    │       └── severity_reporter.py
    ├── obsidian-translator/            # Add translations
    │   └── SKILL.md
    ├── obsidian-concept-creator/       # Create concept notes
    │   └── SKILL.md
    ├── obsidian-moc-creator/           # Create MOCs
    │   └── SKILL.md
    ├── obsidian-link-analyzer/         # Suggest links
    │   └── SKILL.md
    │
    │   # New Skills (Vault Maintenance)
    ├── vault-health-report/            # Generate vault health reports
    │   └── SKILL.md
    ├── batch-validator/                # Validate multiple files at once
    │   └── SKILL.md
    ├── android-enforcer/               # Android-specific rule enforcement
    │   └── SKILL.md
    ├── link-fixer/                     # Fix orphans and broken links
    │   └── SKILL.md
    ├── gap-analyzer/                   # Identify content gaps
    │   └── SKILL.md
    ├── bulk-normalizer/                # Batch YAML normalization
    │   └── SKILL.md
    ├── translation-auditor/            # Audit bilingual content
    │   └── SKILL.md
    ├── duplicate-detector/             # Find duplicate questions
    │   └── SKILL.md
    ├── study-path-builder/             # Create learning progressions
    │   └── SKILL.md
    ├── code-validator/                 # Validate code examples
    │   └── SKILL.md
    └── url-ingestor/                   # Generate Q&As from URLs
        └── SKILL.md
```

---

## Skills Overview

### Priority 1 Skills (Most Frequently Used)

#### 1. obsidian-qna-creator
**Purpose**: Create bilingual interview Q&A notes with full validation

**Use When**:
- Creating new interview questions
- Adding questions from external sources
- Building study content

**What It Does**:
- Determines correct folder from topic
- Generates valid filename
- Creates bilingual EN/RU structure
- Sets proper YAML frontmatter
- Links to MOC and related notes
- Validates against TAXONOMY.md

**Example**:
```
User: "Create a note about Kotlin coroutine context"
→ Creates: 70-Kotlin/q-coroutine-context--kotlin--medium.md
→ With complete YAML and bilingual content
```

#### 2. obsidian-validator
**Purpose**: Comprehensive validation of notes against vault rules

**Use When**:
- After creating/editing notes
- Before committing changes
- Auditing vault health

**What It Does**:
- Checks YAML completeness
- Validates topic against TAXONOMY.md
- Verifies folder placement
- Checks bilingual content
- Reports severity levels (REQUIRED, FORBIDDEN, WARNING, NOTE)

**Example**:
```
User: "Validate 40-Android/q-compose-state--android--medium.md"
→ Runs 20+ validation checks
→ Reports issues with severity and suggestions
```

#### 3. obsidian-translator
**Purpose**: Add missing language translations to existing notes

**Use When**:
- English-only notes need Russian
- Russian-only notes need English
- Updating language_tags

**What It Does**:
- Identifies missing language sections
- Translates while preserving code and links
- Updates language_tags YAML field
- Maintains status: draft

**Example**:
```
User: "Translate q-coroutine-basics--kotlin--easy.md to Russian"
→ Adds # Вопрос (RU) and ## Ответ (RU) sections
→ Updates YAML language_tags to [en, ru]
```

### Priority 2 Skills (Less Frequent)

#### 4. obsidian-concept-creator
**Purpose**: Create reusable concept notes in `10-Concepts/`

**Use When**:
- Documenting fundamental concepts
- Creating reference material
- Building concept library

#### 5. obsidian-moc-creator
**Purpose**: Create Maps of Content (MOCs) to organize notes

**Use When**:
- Organizing questions by topic
- Creating study guides
- Building navigation structure

#### 6. obsidian-link-analyzer
**Purpose**: Suggest and add cross-references between notes

**Use When**:
- Enhancing existing notes
- Building knowledge graph
- Finding related questions

### New Skills: Vault Maintenance (Added 2025-01-05)

#### 7. vault-health-report
**Purpose**: Generate comprehensive vault health reports with statistics and issue detection

**Use When**:
- Weekly/monthly vault health checks
- Before major content updates
- Monitoring vault quality over time

**What It Does**:
- Counts notes by topic, difficulty, status
- Identifies YAML issues across vault
- Finds orphaned notes and broken links
- Reports translation coverage
- Calculates overall health score (0-100)

#### 8. batch-validator
**Purpose**: Validate multiple files at once with aggregated reporting

**Use When**:
- After creating multiple notes
- Before committing changes
- Auditing entire folders or topics

**What It Does**:
- Validates all notes in a folder or by topic
- Groups issues by severity (CRITICAL, ERROR, WARNING)
- Generates fix suggestions and checklists

#### 9. android-enforcer
**Purpose**: Validate and auto-fix Android-specific rules

**Use When**:
- Creating Android Q&A notes
- Auditing Android content
- Fixing subtopic-to-tag mirroring

**What It Does**:
- Checks `android/<subtopic>` tag mirroring
- Validates subtopics against ANDROID-SUBTOPICS list
- Auto-adds missing mirrored tags

#### 10. link-fixer
**Purpose**: Bulk fix link-related issues across the vault

**Use When**:
- Fixing orphaned notes
- Repairing broken links
- Improving vault connectivity

**What It Does**:
- Finds and fixes orphaned notes
- Adds missing related links based on similarity
- Removes broken links
- Suggests bidirectional links

#### 11. gap-analyzer
**Purpose**: Identify content gaps and suggest new Q&As to create

**Use When**:
- Planning content sprints
- Quarterly content reviews
- Identifying under-represented topics

**What It Does**:
- Analyzes coverage by topic and difficulty
- Finds topics with missing difficulty levels
- Suggests specific Q&A titles to fill gaps
- Generates prioritized content roadmaps

#### 12. bulk-normalizer
**Purpose**: Batch normalize YAML frontmatter across files

**Use When**:
- Monthly maintenance
- After bulk content imports
- Standardizing metadata format

**What It Does**:
- Standardizes field ordering
- Converts multi-line arrays to single-line
- Updates timestamps
- Removes duplicate fields

#### 13. translation-auditor
**Purpose**: Audit bilingual content quality and completeness

**Use When**:
- Reviewing translation coverage
- Quality control for bilingual content
- Finding partially translated notes

**What It Does**:
- Finds partially translated sections
- Checks EN/RU content parity
- Reports translation completeness by folder
- Flags inconsistent terminology

#### 14. duplicate-detector
**Purpose**: Find duplicate or near-duplicate questions

**Use When**:
- Quarterly vault audits
- After bulk content imports
- Cleaning up redundant content

**What It Does**:
- Detects exact title duplicates
- Finds semantically similar questions
- Suggests merge candidates
- Generates deduplication reports

#### 15. study-path-builder
**Purpose**: Create learning progressions and study paths

**Use When**:
- Building study guides
- Creating MOCs with learning order
- Helping users navigate content

**What It Does**:
- Builds easy → medium → hard chains
- Suggests prerequisite relationships
- Generates study guides
- Creates progression MOCs

#### 16. code-validator
**Purpose**: Validate and analyze code examples in notes

**Use When**:
- After creating algorithm questions
- During technical content review
- Quality control for code examples

**What It Does**:
- Checks Kotlin/Java/Python syntax
- Verifies code block language tags
- Detects missing imports
- Flags incomplete or placeholder code

#### 17. url-ingestor
**Purpose**: Generate Q&A notes from web articles and documentation

**Use When**:
- Content sprints from reference materials
- Expanding topic coverage
- Importing from documentation

**What It Does**:
- Fetches and parses URL content
- Extracts key concepts as questions
- Generates bilingual Q&A structure
- Auto-classifies topic and difficulty

---

## How to Use Skills

### Automatic Activation (Recommended)

Claude Code automatically activates relevant skills based on your request:

```
User: "Create a note about Android ViewModel"
→ Claude activates obsidian-qna-creator skill
→ Follows skill instructions to create note
```

### Manual Activation

You can explicitly request a skill:

```
User: "Use obsidian-validator to check this note"
→ Claude activates obsidian-validator skill
→ Runs comprehensive validation
```

### Skill Invocation (Advanced)

If using Claude Code CLI or API:

```bash
# Via Skill tool
/skill obsidian-qna-creator

# Via prompt
"Activate the obsidian-qna-creator skill to create a note about..."
```

---

## Custom Instructions

**File**: `custom_instructions.md`

**Purpose**: Brief context auto-loaded at every session start

**Token Usage**: ~500 tokens (vs. ~5,000 for full documentation)

**Contains**:
- Core vault principles (REQUIRED/FORBIDDEN rules)
- Bilingual structure requirement
- Link to TAXONOMY.md for controlled vocabularies
- Link to CLAUDE.md for full documentation
- Link to templates in `_templates/`

**What's NOT in custom_instructions**:
- Detailed workflows (moved to Skills)
- Example sessions (in CLAUDE.md)
- Complete validation rules (in Skills)

This keeps baseline token usage low while providing essential context.

---

## Token Efficiency

### Before Skills Implementation

```
Context at session start:
- Custom instructions: ~5,000 tokens
- Workflow documentation: ~10,000 tokens (if referenced)
Total: ~15,000 tokens (always loaded)
```

### With Skills Implementation

```
Context at session start:
- Custom instructions: ~500 tokens (brief)
- 6 skill descriptions: ~600 tokens (100 each)
Total: ~1,100 tokens baseline

When skill activated:
- Baseline: ~1,100 tokens
- Active skill: ~3,000 tokens
- Total during task: ~4,100 tokens
```

**Savings**: ~85% reduction in baseline token usage

**Benefits**:
- More tokens available for actual work
- Faster response times
- Lower costs per session
- Only load what's needed

---

## Helper Scripts

### Python Validators

Skills can include Python helper scripts for:

**taxonomy_validator.py**:
- Load and parse TAXONOMY.md
- Validate topic against controlled list
- Validate Android subtopics
- Fast validation without LLM processing

**filename_generator.py**:
- Generate valid filenames from components
- Enforce naming conventions
- Handle slug generation

**yaml_builder.py**:
- Build YAML frontmatter
- Enforce required fields
- Validate format (no brackets in moc, etc.)

**validator.py**:
- Comprehensive note validation
- Check YAML, content, links
- Report severity levels

### Usage in Skills

Skills can import and use these helpers:

```python
from core.taxonomy_validator import validate_topic
from core.filename_generator import generate_qna_filename

if not validate_topic(topic):
    raise ValueError(f"Invalid topic: {topic}")

filename = generate_qna_filename(slug, topic, difficulty)
```

---

## Vault Rules Quick Reference

### Core Principles (Non-Negotiable)

**REQUIRED**:
1. Both EN and RU in same file
2. Exactly ONE topic from TAXONOMY.md
3. English-only tags
4. Status: draft (for AI)
5. Link to MOC and ≥2 related items
6. No emoji
7. Folder matches topic
8. YAML format: `moc: moc-name` (no brackets)

**FORBIDDEN**:
1. Splitting EN/RU into separate files
2. Russian in tags
3. Multiple topics in `topic` field
4. Setting `status: reviewed` or `ready` (AI can't)
5. Brackets in YAML `moc` field
6. Double brackets in YAML `related` field
7. Emoji anywhere
8. File in wrong folder

### Key Files

- **Full rules**: `../AGENTS.md`
- **Quick checklist**: `../00-Administration/AGENT-CHECKLIST.md`
- **Controlled vocabularies**: `../00-Administration/Vault-Rules/TAXONOMY.md`
- **File naming**: `../00-Administration/Vault-Rules/FILE-NAMING-RULES.md`
- **Templates**: `../_templates/_tpl-qna.md`, `_tpl-concept.md`, `_tpl-moc.md`

---

## Installation & Setup

### For Claude Code Users

1. **This directory is already set up** - no installation needed
2. Skills automatically available when Claude Code runs in this directory
3. Custom instructions auto-load from `custom_instructions.md`

### For New Contributors

1. Review `custom_instructions.md` to understand vault principles
2. Review skill descriptions in `skills/*/SKILL.md`
3. Read `../CLAUDE.md` for full documentation
4. Check `../00-Administration/Vault-Rules/TAXONOMY.md` for controlled vocabularies

### For Developers

To add new skills:

1. Create skill directory: `skills/new-skill-name/`
2. Create `SKILL.md` with YAML frontmatter and instructions
3. Add helper scripts in `core/` subdirectory (optional)
4. Update this README with skill description
5. Test skill activation

**Skill Template**:
```markdown
---
name: skill-identifier
description: >
  Brief description of what this skill does,
  when to use it, and expected outcomes.
---

# Skill Title

## Purpose
What this skill accomplishes

## When to Use
Specific scenarios

## Process
Step-by-step instructions

## Validation
How to verify success

## Examples
Sample usage
```

---

## Troubleshooting

### Skill Not Activating

**Problem**: Claude doesn't activate skill when expected

**Solutions**:
1. Explicitly request the skill by name
2. Check skill description matches your use case
3. Verify SKILL.md has valid YAML frontmatter

### Validation Failures

**Problem**: Notes fail validation

**Solutions**:
1. Check TAXONOMY.md for valid topics
2. Review vault rules in `../AGENTS.md`
3. Use obsidian-validator skill for detailed report
4. Compare with working examples in vault

### Python Helper Issues

**Problem**: Helper scripts not working

**Solutions**:
1. Verify Python 3.8+ installed
2. Check script imports are correct
3. Ensure TAXONOMY.md path is correct
4. Run script standalone to test

---

## Contributing

### Adding New Skills

1. **Identify workflow** that's repeated frequently
2. **Design skill structure** (purpose, when to use, process)
3. **Create SKILL.md** with comprehensive instructions
4. **Add helper scripts** if validation/automation needed
5. **Test thoroughly** with multiple scenarios
6. **Document in this README**

### Updating Existing Skills

1. **Test changes** don't break existing workflows
2. **Update version** in SKILL.md if major changes
3. **Document changes** in skill's SKILL.md
4. **Update examples** to reflect new behavior

### Best Practices

- Keep skill descriptions concise (~100 tokens)
- Put detailed instructions in SKILL.md body
- Include examples in skill documentation
- Add validation steps to ensure quality
- Use helper scripts for complex validation
- Test skills with edge cases

---

## Resources

### Documentation

- **This README**: Overview and usage
- **CLAUDE.md**: Complete agent guide (parent directory)
- **CLAUDE-SKILLS-RESEARCH.md**: Implementation research (parent directory)
- **AGENTS.md**: Detailed vault rules (parent directory)

### Templates

- **Q&A**: `../_templates/_tpl-qna.md`
- **Concept**: `../_templates/_tpl-concept.md`
- **MOC**: `../_templates/_tpl-moc.md`

### Vault Rules

- **TAXONOMY.md**: Controlled vocabularies
- **FILE-NAMING-RULES.md**: Filename conventions
- **LINKING-STRATEGY.md**: Cross-reference guidelines
- **LINK-HEALTH-DASHBOARD.md**: Vault health metrics

### External Resources

- **Claude Skills GitHub**: https://github.com/anthropics/skills
- **Claude Code Docs**: https://docs.claude.com/claude-code

---

## Version History

### v2.0 (2025-01-05)
- Added 11 new vault maintenance skills
- Total skills: 17
- New skills include:
  - vault-health-report: Comprehensive vault health reports
  - batch-validator: Validate multiple files at once
  - android-enforcer: Android-specific rule enforcement
  - link-fixer: Fix orphans and broken links
  - gap-analyzer: Identify content gaps
  - bulk-normalizer: Batch YAML normalization
  - translation-auditor: Audit bilingual content
  - duplicate-detector: Find duplicate questions
  - study-path-builder: Create learning progressions
  - code-validator: Validate code examples
  - url-ingestor: Generate Q&As from URLs
- Updated documentation and directory structure

### v1.0 (2025-11-09)
- Initial implementation
- 6 core skills created
- Python helper scripts added
- Token-efficient custom instructions
- Complete documentation

---

## Support

**Issues**: Create issue in repository
**Questions**: Check `../CLAUDE.md` or `../AGENTS.md`
**Updates**: Skills may be updated as vault rules evolve

---

**Status**: Production Ready
**Maintained By**: Vault maintainers
**License**: Same as parent repository
