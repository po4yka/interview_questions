# AI Tools & Agent Documentation

Quick guide to using different AI tools with this vault.

---

## Available Documentation

| Tool | File | Description |
|------|------|-------------|
| **Cursor AI** | `../.cursor/rules/` + `../.cursorrules` | Auto-loaded rules for Cursor editor |
| **Claude Code** | `../.claude/` | Setup guide, commands, auto-loaded context |
| **Gemini CLI** | `GEMINI.md` | Command-line workflow examples |
| **ChatGPT / General** | `AGENTS.md` | General LLM agent instructions |
| **Any Agent** | `AGENT-CHECKLIST.md` | Quick validation checklist |

---

## Cursor AI

**Setup**: Rules are automatically loaded from `.cursorrules` in vault root.

**Usage**:
1. Open vault in Cursor
2. Use Cmd+K or Cmd+L to invoke AI
3. Cursor automatically knows vault rules

**Common commands**:
- "Create a Q&A note about [topic]"
- "Translate this note to Russian/English"
- "Validate this note against vault rules"
- "Suggest related concepts for this note"

**Key features**:
- Auto-loaded context (no manual setup)
- File-aware (knows current file)
- Can edit files directly

---

## Claude Code (CLI)

**Setup**: Automatic via `.claude/` configuration.

**Configuration files**:
- `.claude/README.md` - Complete setup guide and quick reference
- `.claude/custom_instructions.md` - Auto-loaded vault context
- `.claude/commands/` - Slash commands for common tasks
- `.claude/settings.local.json` - Approved permissions

**Usage**:
```bash
# In vault directory
claude-code
```

**Available slash commands**:
- `/create-qna` - Create new Q&A note
- `/create-concept` - Create concept note
- `/translate` - Add missing language to note
- `/validate` - Comprehensive note validation
- `/link-concepts` - Suggest and add concept links

**Strengths**:
- Multi-file operations
- Complex reasoning
- Detailed analysis
- File system operations
- Custom slash commands

**See**:
- `.claude/README.md` for setup and quick start
- `.claude/commands/README.md` for slash command documentation
- `AGENTS.md` for full task list

---

## Gemini CLI

**Setup**: Load context at session start (see GEMINI.md).

**Usage**:
```bash
gemini "Create Q&A about Binary Search. Topic: algorithms, Difficulty: easy. Include EN/RU."
```

**Strengths**:
- Fast single-command operations
- Batch processing
- Quick translations
- Good for scripting

**See**: `GEMINI.md` for command patterns and examples

---

## ChatGPT / General LLMs

**Setup**: Provide context manually.

**Recommended context**:
```
I'm working with a bilingual Obsidian vault for interview prep.

Rules:
- Both EN and RU in same file (never split)
- YAML frontmatter with controlled vocabularies
- Tags English-only
- Pick one topic from TAXONOMY.md
- Always set status: draft
- Link to ≥1 MOC and concepts

Files:
- Rules: 00-Administration/README.md
- Tasks: 00-Administration/AGENTS.md
- Checklist: 00-Administration/AGENT-CHECKLIST.md
- Topics: 00-Administration/TAXONOMY.md
```

**Usage**:
- Upload files for context
- Paste content for translation/validation
- Ask for outlines/summaries

**See**: `AGENTS.md` for task workflows

---

## Quick Start by Tool

### Cursor
1. Open vault in Cursor
2. Start using Cmd+K/Cmd+L (rules auto-load)

### Claude Code
1. `cd /path/to/vault`
2. `claude-code`
3. Context auto-loads from `.claude/custom_instructions.md`
4. Use `/create-qna`, `/validate`, etc. for common tasks
5. See `.claude/README.md` for full guide

### Gemini CLI
1. `cd /path/to/vault`
2. `gemini "Load context from 00-Administration/GEMINI.md"`
3. Use command patterns from GEMINI.md

### ChatGPT
1. New chat
2. Paste context (see above)
3. Upload files or paste content
4. Use task patterns from AGENTS.md

---

## Core Rules (All Tools)

Regardless of which AI tool you use:

1. **Bilingual = Same File** (EN + RU together, never split)
2. **Tags = English Only** (Russian only in content/aliases)
3. **One Topic** (exactly one from TAXONOMY.md)
4. **Status = draft** (for all AI-created content)
5. **Links Required** (moc + related fields must be populated)
6. **Android → Mirror Tags** (subtopics → android/* tags)
7. **Validate** (check TAXONOMY.md, use checklist)

---

## Recommended Workflows

### Creating New Q&A
**Best tool**: Cursor or Claude Code (can create files directly)

**Workflow**:
1. Determine topic, difficulty, folder
2. Check TAXONOMY.md for valid values
3. Use template from _templates/
4. Write EN content
5. Write RU content (or translate)
6. Validate with checklist
7. Set status: draft

### Translating Existing Note
**Best tool**: Any (Gemini CLI for speed, Cursor for convenience)

**Workflow**:
1. Read existing note
2. Identify missing language
3. Translate preserving structure
4. Update language_tags
5. Keep status: draft

### Batch Operations
**Best tool**: Gemini CLI or Claude Code

**Examples**:
- Create 10 LeetCode Q&As
- Translate all notes in folder
- Validate all Android notes

### Validation/Fixes
**Best tool**: Cursor (inline edits) or Claude Code (analysis)

**Workflow**:
1. Read note
2. Check against checklist
3. Verify YAML (topic, tags, links)
4. Check bilingual content
5. Apply fixes
6. Keep status: draft

---

## Strengths Comparison

| Feature | Cursor | Claude Code | Gemini CLI | ChatGPT |
|---------|--------|-------------|------------|---------|
| Auto-loads rules | ✅ | ✅ | ❌ | ❌ |
| Slash commands | ❌ | ✅ | ❌ | ❌ |
| File operations | ✅ | ✅ | ⚠️ | ❌ |
| Batch tasks | ⚠️ | ✅ | ✅ | ❌ |
| Inline editing | ✅ | ⚠️ | ❌ | ❌ |
| Speed | ⚠️ | ⚠️ | ✅ | ⚠️ |
| Context window | Large | Large | Medium | Medium |
| Scripting | ❌ | ⚠️ | ✅ | ❌ |
| Cost | Paid | Paid | Paid | Free/Paid |

---

## Common Tasks → Recommended Tool

| Task | Best Tool | Alternative |
|------|-----------|-------------|
| Create single Q&A | Cursor | Claude Code |
| Create 10+ Q&As | Gemini CLI | Claude Code |
| Translate note | Any | Gemini CLI (fast) |
| Validate folder | Claude Code | Gemini CLI |
| Quick fix | Cursor | Claude Code |
| Complex refactor | Claude Code | Cursor |
| Generate concepts | Cursor | Claude Code |
| Update MOCs | Cursor | Claude Code |

---

## Tips for Each Tool

### Cursor
- Use Cmd+K for inline edits
- Use Cmd+L for chat-based tasks
- Rules auto-load, no setup needed
- Great for "fix this note" type tasks

### Claude Code
- Context auto-loads from `.claude/custom_instructions.md`
- Use slash commands: `/create-qna`, `/translate`, `/validate`
- Good for multi-step reasoning
- Can handle complex file operations
- See `.claude/README.md` for complete guide

### Gemini CLI
- Use command patterns from GEMINI.md
- Great for scripting/automation
- Fast for single-purpose tasks
- Load context at session start

### ChatGPT
- Manually provide context each session
- Good for planning/outlining
- Copy-paste workflow
- Use for quick questions

---

## File Reference Quick Links

- **Vault rules**: `README.md` (this folder)
- **Topic list**: `TAXONOMY.md` (this folder)
- **Agent tasks**: `AGENTS.md` (this folder)
- **Quick checklist**: `AGENT-CHECKLIST.md` (this folder)
- **Gemini guide**: `GEMINI.md` (this folder)
- **Cursor rules**: `../.cursor/rules/` (modern) and `../.cursorrules` (legacy)
- **Claude Code config**: `../.claude/` (README, commands, settings)
- **Templates**: `../_templates/` (vault root)

---

## Example: Creating "Two Sum" Q&A

### Using Cursor
```
Cmd+K: "Create q-two-sum--algorithms--easy.md in 20-Algorithms/.
Include EN and RU. Link to moc-algorithms and c-hash-map."
```

### Using Claude Code
```
/create-qna Two Sum problem from LeetCode, algorithms, easy difficulty
```

Or more detailed:
```
"Create a Q&A note for Two Sum problem.
Topic: algorithms, Difficulty: easy
Include both English and Russian versions.
Link to relevant concepts and MOC."
```

### Using Gemini CLI
```bash
gemini "Create q-two-sum--algorithms--easy.md.
Problem: Given array, find two indices that sum to target.
Topic: algorithms, Difficulty: easy, Include EN/RU.
Link to [[moc-algorithms]] and [[c-hash-map]]."
```

### Using ChatGPT
```
[Upload _templates/_tpl-qna.md]

"Fill this template for Two Sum problem.
- Topic: algorithms
- Difficulty: easy
- Include English and Russian
- Link to moc-algorithms and c-hash-map"
```

---

**Remember**: All tools must follow the same rules. Choose based on your workflow preference.
