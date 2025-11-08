# Obsidian Interview Vault

This repository documents a **personal** Obsidian vault designed for building and maintaining a bilingual (RU/EN) interview Q&A knowledge base across **CS**, **Algorithms/LeetCode**, **Android**, **System Design**, and related topics.

---

## Design Principles (Normative)

* **One note = one Q&A**: A single note holds both the original question/answer and its translation.
* **Folders encode coarse topics; YAML + tags encode fine‑grained facets**.
* **English-only tags** for consistency (Russian appears in content/aliases, not in tags).
* **YAML-first**: every note starts with complete frontmatter; Dataview-ready.
* **Link richly**: connect to concept notes, MOCs (Maps of Content), follow‑ups, and similar questions.
* **Templated**: new notes are created via a Templater/Template to ensure uniformity.

### MUST / SHOULD / MAY

* **MUST** keep EN & RU for the same item **in the same note**.
* **MUST** include required YAML fields from the schema below.
* **MUST** use English tags (lower‑kebab or lower‑snake consistently).
* **SHOULD** link each question to at least one concept/MOC.
* **SHOULD** use aliases for bilingual titles.
* **MAY** maintain concept notes and MOCs per topic.

---

## Folder Layout (Topics & Types)

> Keep hierarchy shallow. Use folders for coarse grouping; rely on YAML/tags/links for the rest.

```
📄 README.md (this file - located at root level)
📁 InterviewQuestions/    # Main content directory
├── 00-Administration/   # Administrative documentation and guides
├── 10-Concepts/         # Reusable theory and concept notes
├── 20-Algorithms/       # Coding interview problems, LeetCode-style
├── 30-System-Design/    # System design scenarios and trade-offs
├── 40-Android/          # Android platform, APIs, patterns, pitfalls
├── 50-Backend/          # Backend, databases, and server-side topics
├── 60-CompSci/          # Computer science fundamentals
├── 70-Kotlin/           # Kotlin language and ecosystem
├── 80-Tools/            # Development tools and workflows
├── 90-MOCs/            # Maps of Content (topic hubs)
├── _templates/          # Templater templates for new notes
├── config/              # Configuration files
├── scripts/             # Utility scripts
├── utils/               # Python utilities and validation tools
└── validators/          # AI validation and processing modules
```

**Notes**

* **00-Administration/** contains administrative documentation, guides, and system documentation organized in subfolders
* Files **belong to exactly one topic folder** (20-Algorithms, 40-Android, etc.). Use tags/links for cross-cutting concerns (e.g., `hash-table`, `graphs`).
* **10-Concepts/** contains reusable theory and concept notes referenced by many questions.
* **90-MOCs/** contains Maps of Content (hub notes) that index topics via links and Dataview queries.
* **_templates/** contains Templater templates for creating new notes consistently.
* **utils/** and **validators/** contain Python tools for AI-assisted content validation and processing.

---

## File Naming Convention

* **Questions (Q&A)**: `q-<slug>--<short-topic>--<difficulty>.md`

  * Example: `q-two-sum--algorithms--easy.md`
* **Concepts**: `c-<slug>.md` -> `c-hash-map.md`
* **MOCs**: `moc-<topic>.md` -> `moc-algorithms.md`

Keep filenames **English, kebab-case**, short and stable. Language variants are handled inside the note and via `aliases`.

---

## YAML Frontmatter Schema (Required)

```yaml
---
# Identity
id: algo-001               # <subject>-<serial> format (e.g., algo-001, android-134)
title: Two Sum / Два слагаемых
aliases:                   # all common titles; EN & RU recommended
  - Two Sum
  - Два слагаемых

# Classification
topic: algorithms          # one of: algorithms | system-design | android | cs | behavioral
subtopics: [arrays, hash-map]  # optional, small set
question_kind: coding      # coding | theory | system-design | android
difficulty: easy           # easy | medium | hard

# Language & provenance
original_language: en      # en | ru
language_tags: [en, ru]    # which languages exist in this note
sources:
  - url: https://leetcode.com/problems/two-sum/
    note: Original statement

# Workflow & relations
status: draft              # draft | reviewed | ready
moc: moc-algorithms        # link to Map of Content (WITHOUT brackets)
related: [c-hash-map, q-three-sum--algorithms--medium]  # cross-links (array, WITHOUT double brackets)

# Timestamps (ISO8601)
created: 2025-09-28
updated: 2025-09-28

# Tags (English only; no leading # in YAML)
tags: [leetcode, arrays, hash-map, difficulty/easy]
---
```

**Rules**

* `topic` is **exactly one** coarse category (matches top-level folder).
* `tags` are **English**, descriptive, reusable (`android`, `dp`, `graphs`, `concurrency`, `io`, `kotlin`).
* Represent difficulty as both a field (`difficulty`) and an optional namespaced tag (`difficulty/easy`).
* Use `aliases` for bilingual titles; keep filenames English.

---

## Note Body Template (Bilingual in One Note)

```markdown
# Вопрос (RU)
> Точная русская формулировка задачи.

# Question (EN)
> Clear, concise English version of the prompt.

---

## Ответ (RU)
Подробное объяснение на русском. Код при необходимости.

## Answer (EN)
Explain approach, complexity, trade-offs, pitfalls. Include code when relevant.

---

## Follow-ups
- Variation A …
- Edge cases …

## References
- [[c-hash-map]]
- Link(s) to external sources (also listed in YAML `sources`).

## Related Questions
- [[q-three-sum--algorithms--medium]]
```

**Rules**

* Keep **both languages side by side**; they must be semantically equivalent.
* Prefer **EN code identifiers/comments**; RU comments optional.
* Keep answers **complete yet skimmable** with headings and lists.

---

## Tagging Rules

* Tags are **English**; keep them short and reusable (`arrays`, `hash-map`, `two-pointers`, `greedy`, `dp`, `graphs`, `kotlin`, `android/compose`).
* Use **namespaces** for controlled vocabularies: `difficulty/easy`, `lang/kotlin`, `platform/android`.
* Do **not** duplicate the folder name as a tag unless useful for search (e.g., `topic/algorithms`).

---

## Linking Rules (Backlinks, Concepts, MOCs)

* Every Q&A **SHOULD** link to at least one **Concept** (`c-*`) and one **MOC** (`moc-*`).
* Use concept notes for reusable theory (e.g., `c-binary-tree`, `c-consistent-hashing`).
* MOCs act as human‑curated hubs per topic, mixing links + Dataview query blocks.
* For sequencing (follow‑up chains), link forward/back and optionally add `related` in YAML.

---

## MOCs (Maps of Content)

* Location: `MOCs/`
* Name: `moc-<topic>.md` -> `moc-android.md`
* Content: brief overview, manual list of key notes, and auto lists via Dataview.

**Example MOC Skeleton**

````markdown
# Algorithms — MOC

## Start Here
- [[c-complexity-analysis]]
- [[c-hash-map]]

## Easy Starters (Dataview)
```dataview
TABLE difficulty, file.link, subtopics
FROM ""
WHERE topic = "algorithms" AND startswith(file.name, "q-") AND difficulty = "easy"
SORT file.name ASC
````

## By Technique

```dataview
LIST file.link
FROM ""
WHERE topic = "algorithms" AND startswith(file.name, "q-") AND contains(tags, "two-pointers")
```

````

---

## Dataview Examples (Queries)
- **All LeetCode by difficulty**
```dataview
TABLE difficulty, subtopics, status
FROM ""
WHERE topic = "algorithms" AND startswith(file.name, "q-") AND contains(tags, "leetcode")
SORT difficulty ASC, file.name ASC
````

* **Android questions touching Compose**

```dataview
LIST file.link
FROM ""
WHERE topic = "android" AND startswith(file.name, "q-") AND contains(tags, "android/compose")
```

* **Recently Updated**

```dataview
TABLE updated, topic, difficulty
FROM ""
WHERE updated >= date(today) - dur(30 days)
SORT updated DESC
```

---

## Templates (Templater) — New Q&A

Create a template file (e.g., `_tpl-qna.md`) and bind it to a hotkey.

```markdown
---
id: <subject>-XXX              # Fill in: algo-001, android-134, kotlin-042, etc.
title: <%- tp.file.title %>
aliases: []
topic: <%* /* choose: algorithms | system-design | android | cs | behavioral */ %>
subtopics: []
question_kind: coding
difficulty: easy
original_language: ru
language_tags: [ru, en]
sources: []
status: draft
moc: []
related: []
created: <% tp.date.now("YYYY-MM-DD") %>
updated: <% tp.date.now("YYYY-MM-DD") %>
tags: []
---

# Вопрос (RU)

# Question (EN)

---

## Ответ (RU)

## Answer (EN)

---

## Follow-ups

## References
```

**Rules**

* Template should populate required YAML keys and the bilingual skeleton.
* Consider a small helper `tp.user.uid()` that returns a short unique suffix.

---

## AI Tools & Workflows

The vault includes comprehensive AI-assisted workflows for content creation, validation, and maintenance.

### AI Agent Guidelines
- **AGENTS.md**: General AI agent instructions for the entire project
- **GEMINI.md**: Specific guidance for Gemini CLI usage
- **CLAUDE.md**: Claude Code integration and workflows
- **.cursor/rules/**: Cursor AI editor rules for automated assistance

### AI Integration
- **LM Studio**: Local AI processing setup for translation and validation
- **Validation Tools**: Python-based content validation with AI assistance
- **Agent Checklists**: Standardized workflows for AI-assisted content creation

### Administrative Documentation
Located in `00-Administration/` with organized subfolders:
- **AI-Agents/**: Agent checklists and prompts
- **AI-Integration/**: Tool setup guides
- **Validation/**: Content validation systems
- **Vault-Rules/**: Taxonomy and file naming rules
- **Linking-System/**: Link health monitoring and MOCs

**Rule**: All AI-generated content remains **draft** until human review; update `status` to `reviewed/ready` after verification.

---

## Maintenance & Hygiene

* **Statuses**: `draft` -> `reviewed` -> `ready`.
* **Updates**: always bump `updated` in YAML.
* **Migrations**: prefer adding aliases over renaming filenames; if rename is necessary, update incoming links.
* **Archive**: move outdated/duplicate notes to `99-Archive/` and mark `status: retired`.
* **Tag health**: periodically audit and merge near-duplicates (e.g., `hashmap` vs `hash-map`).

---

## Backup & Sync

* Use Git (commit early/often). The `.gitignore` file excludes AI model files, cache directories, and sensitive configuration
* Cross-device: Obsidian Sync or your preferred encrypted sync; keep IDs stable across devices
* AI tools: LM Studio configurations and validation artifacts are automatically ignored

---

## Quickstart

### Basic Setup
1. Clone the repository and open in Obsidian
2. Install plugins: Dataview, Templater (optional: MetaEdit, Tag Wrangler, Breadcrumbs)
3. Review `00-Administration/README.md` for documentation structure
4. Check `00-Administration/Index/DOCUMENTATION-INDEX.md` for quick start guides

### Content Creation
1. Review `AGENTS.md` for AI agent guidelines and rules
2. Use templates from `_templates/` for consistent note creation
3. Follow the file naming conventions from `00-Administration/Vault-Rules/FILE-NAMING-RULES.md`
4. Use taxonomy from `00-Administration/Vault-Rules/TAXONOMY.md` for topics and tags
5. Create concept notes in `10-Concepts/` and questions in appropriate topic folders
6. Fill EN/RU sections; add complete YAML frontmatter; link to concepts + MOCs

### AI-Assisted Workflows
1. Set up LM Studio following `00-Administration/AI-Integration/LM-STUDIO-QUICKSTART.md`
2. Use validation tools from `utils/` and `validators/`
3. Follow agent checklists from `00-Administration/AI-Agents/`
4. Monitor link health with `00-Administration/Linking-System/LINK-HEALTH-DASHBOARD.md`

### Exploration
1. Start with `00-Administration/Linking-System/00-MOC-Start-Here.md` for topic overview
2. Use MOCs in `90-MOCs/` and Dataview queries for content discovery
3. Check recent updates and link health regularly

---

## FAQ

* **Why English filenames and tags?** Predictable search, portability, and ecosystem conventions.
* **Where do Russian titles live?** In `aliases` and in the RU sections of the body.
* **Multiple topics?** Pick one `topic` (folder) and express extras via `subtopics`/`tags`/links.
