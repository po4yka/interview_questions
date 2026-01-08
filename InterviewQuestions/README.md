---\
---\

# Obsidian Interview Vault

A complete, **bilingual (EN/RU)**, personal Obsidian vault for technical interview preparation across **Android**, **Kotlin**, **CompSci**, **Algorithms**, **System Design**, **Backend**, and **Tools**.

---

## Quick Links

| Resource | Description |
|----------|-------------|
| [[Homepage]] | Vault entry point with statistics and navigation |
| [[00-Administration/Vault-Rules/TAXONOMY\|Taxonomy]] | All valid topics, subtopics, difficulty values |
| [[00-Administration/Vault-Rules/FILE-NAMING-RULES\|Naming Rules]] | File naming conventions |
| [[00-Administration/Link-Health-Report\|Link Health Report]] | Broken links and orphan detection |
| [[_templates/_tpl-qna\|Q&A Template]] | Template for new questions |

---

## For LLM Agents

| Agent | Configuration |
|-------|---------------|
| **Cursor AI** | Rules in `../.cursorrules` (auto-loaded) |
| **Claude Code** | Workflows in `.claude/` directory |
| **General Agents** | See [[AGENTS.md]] for task instructions |
| **Quick Validation** | [[00-Administration/AI-Agents/AGENT-CHECKLIST.md\|AGENT-CHECKLIST]] |
| **Gemini CLI** | See [[GEMINI.md]] for command-line workflows |

**Key Rule**: `Set` `status: draft` for all LLM-created/modified content until human review.

---

## Quick Start

### Creating a New Q&A Note

1. Use template: `_templates/_tpl-qna.md`
2. Name file: `q-<slug>--<topic>--<difficulty>.md`
3. Place in correct folder based on topic
4. Fill both EN and RU sections
5. `Set` `status: draft`

### File Naming Examples

| Type | Pattern | Example |
|------|---------|---------|
| Q&A | `q-<slug>--<topic>--<difficulty>.md` | `q-two-sum--algorithms--easy.md` |
| Concept | `c-<slug>.md` | `c-hash-map.md` |
| MOC | `moc-<topic>.md` | `moc-android.md` |

---

## Design Goals

**Goals:**
- Keep all information **in one place** per question: EN+RU in the same note
- Make notes **queryable** via YAML for Dataview dashboards
- Use **folders for coarse topics**; **tags + links** for facets and relationships
- Maintain a **controlled vocabulary** for topics, subtopics, difficulty, language
- Support **LLM-assisted** translation/normalization with **human review**

**Non-Goals:**
- Flashcard/Spaced repetition (Anki) is out of scope
- Team collaboration features are not primary (personal vault)

---

## Canonical Rules

| Level | Rule |
|-------|------|
| **MUST** | One note == one Q&A item; both languages (EN/RU) in same file |
| **MUST** | Every note starts with complete YAML frontmatter |
| **MUST** | English-only tags; Russian only in content and `aliases` |
| **MUST** | Exactly one `topic` per note (maps 1:1 to folder) |
| **SHOULD** | Add 1-3 `subtopics`; use namespaced tags for clarity |
| **SHOULD** | Link each Q&A to at least one Concept and one MOC |
| **MAY** | Use LLMs to translate/normalize; mark `status: draft` until reviewed |

---

## Folder Layout

```
Homepage.md                 # Vault entry point with stats
README.md                   # This file - vault documentation
_templates/                 # Note templates (Q&A, Concept, MOC)
00-Administration/          # Vault rules, taxonomy, agent docs
10-Concepts/                # Theory/glossary notes (~359 files)
20-Algorithms/              # Coding problems, LeetCode-style
30-System-Design/           # Large-scale design, trade-offs
40-Android/                 # Platform APIs, Compose, lifecycle (~528 files)
50-Backend/                 # Backend development, APIs, databases
60-CompSci/                 # CS fundamentals, design patterns
70-Kotlin/                  # Coroutines, Flow, syntax, idioms (~358 files)
80-Tools/                   # Git, build systems, CI/CD, IDEs
90-MOCs/                    # Maps of Content (hub pages)
```

**Rules:**
- A file belongs to **exactly one** top-level topic folder
- Use **10-Concepts** for reusable theory; **90-MOCs** for hub pages
- Numeric prefixes (00, 10, 20...) ensure consistent sorting

---

## Topic Taxonomy

Use **one** of these canonical values for `topic:` (lower kebab-case):

| Topic | Description | Folder |
|-------|-------------|--------|
| `algorithms` | Problem solving, techniques (DP, greedy, two-pointers) | 20-Algorithms |
| `data-structures` | Arrays, trees, heaps, graphs, hash maps | 20-Algorithms |
| `system-design` | Scalability, availability, consistency | 30-System-Design |
| `android` | Platform, lifecycle, Jetpack, Compose | 40-Android |
| `kotlin` | Coroutines, `Flow`, syntax, idioms | 70-Kotlin |
| `architecture-patterns` | MVVM/MVI/Clean, SOLID, modularization | 60-CompSci |
| `design-patterns` | Creational, structural, behavioral patterns | 60-CompSci |
| `concurrency` | Threads, synchronization, actors | 60-CompSci |
| `databases` | SQL/NoSQL, indexing, transactions | 50-Backend |
| `networking` | TCP/UDP/HTTP, REST, gRPC | 50-Backend |
| `operating-systems` | Processes, scheduling, memory | 60-CompSci |
| `security` | AuthN/AuthZ, crypto, OWASP | 60-CompSci |
| `performance` | Profiling, memory/CPU optimization | 40-Android or 60-CompSci |
| `testing` | Unit/integration/UI, TDD | 40-Android or 70-Kotlin |
| `devops-ci-cd` | Build systems, pipelines, release engineering | 80-Tools |
| `tools` | Git, IDEs, development tools | 80-Tools |
| `cs` | Catch-all CS fundamentals (use only if nothing else fits) | 60-CompSci |

> Prefer the **most specific** topic. Expand detail with `subtopics` and tags.

---

## Android Subtopics

When `topic: android`, pick **1-3** subtopics. Mirror each to a tag `android/<subtopic>`.

### Categories

| Category | Subtopics |
|----------|-----------|
| **UI & UX** | `ui-compose`, `ui-views`, `ui-navigation`, `ui-state`, `ui-animation`, `ui-theming`, `ui-accessibility` |
| **Architecture** | `architecture-mvvm`, `architecture-mvi`, `architecture-clean`, `architecture-modularization`, `di-hilt`, `di-koin` |
| **`Lifecycle`** | `lifecycle`, `activity`, `fragment`, `service`, `broadcast-receiver`, `content-provider` |
| **Concurrency** | `coroutines`, `flow`, `threads-sync`, `background-execution` |
| **Data** | `room`, `sqldelight`, `datastore`, `files-media`, `serialization`, `cache-offline` |
| **Networking** | `networking-http`, `websockets`, `grpc`, `graphql`, `connectivity-caching` |
| **Performance** | `performance-startup`, `performance-rendering`, `performance-memory`, `performance-battery`, `profiling` |
| **Testing** | `testing-unit`, `testing-instrumented`, `testing-ui`, `testing-screenshot`, `testing-benchmark` |
| **Build** | `gradle`, `build-variants`, `dependency-management`, `static-analysis`, `ci-cd` |
| **Security** | `permissions`, `keystore-crypto`, `obfuscation`, `network-security-config` |

Full list: [[00-Administration/Vault-Rules/ANDROID-SUBTOPICS.md]]

---

## YAML Schema

### Q&A Note (Required Fields)

```yaml
---
# Identity
id: iv-2025-0001
title: Two Sum / Dva slagayemykh
aliases: [Two Sum, Dva slagayemykh]

# Classification
topic: algorithms                  # one canonical topic
subtopics: [arrays, hash-map]      # 0-3 values
question_kind: coding              # coding | theory | system-design | android
difficulty: easy                   # easy | medium | hard

# Language
original_language: en              # en | ru
language_tags: [en, ru]            # which languages are present

# Workflow
status: draft                      # draft | reviewed | ready | retired
moc: moc-algorithms                # without brackets
related:                           # list without brackets
  - c-hash-map
  - c-array

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags (English only)
tags: [leetcode, arrays, hash-map, difficulty/easy]
---
```

### Concept Note

```yaml
---
id: ivc-2025-0001
title: Hash Map / Khesh-tablitsa
aliases: [Hash Map, Hash Table, Khesh-tablitsa]
kind: concept
summary: Constant-time average lookups via hashing.
tags: [concept, data-structures, hashing]
---
```

### MOC Note

```yaml
---
id: ivm-2025-0001
title: Algorithms - MOC
kind: moc
tags: [moc, topic/algorithms]
---
```

---

## Note Body Structure

### Q&A Template

```markdown
# Question (EN)
> Clear, concise English version of the prompt.

# Vopros (RU)
> Tochnaya russkaya formulirovka zadachi.

---

## Answer (EN)
Explain approach, complexity, trade-offs. Include code when relevant.

## Otvet (RU)
Podrobnoye ob"yasneniye na russkom. Kod pri neobkhodimosti.

---

## Follow-ups
- Variation A...
- Edge cases...

## References
- [[c-hash-map]]
- External links

## Related Questions
- [[q-three-sum--algorithms--medium]]
```

---

## Tagging Conventions

| Namespace | Examples | Use |
|-----------|----------|-----|
| `difficulty/` | `difficulty/easy`, `difficulty/hard` | Required for all Q&A |
| `android/` | `android/ui-compose`, `android/lifecycle` | Mirror from subtopics |
| `lang/` | `lang/kotlin`, `lang/java` | Programming language used |
| `topic/` | `topic/algorithms` | Only in MOC files |

**Rules:**
- English-only, short, reusable
- Do not duplicate folder name as tag unless helpful
- Use namespaces for controlled vocabularies

---

## Linking Strategy

| Link Type | Rule |
|-----------|------|
| **Concepts** | Every Q&A SHOULD link to at least one `[[c-...]]` |
| **MOCs** | Every Q&A SHOULD reference its topic MOC |
| **Related** | Use YAML `related:` field (without brackets) |
| **Backlinks** | Obsidian auto-generates; check in right panel |

---

## Dataview Examples

**All LeetCode by Difficulty**
```dataview
TABLE difficulty, subtopics, status
FROM "20-Algorithms"
WHERE contains(tags, "leetcode")
SORT difficulty ASC, file.name ASC
```

**Android Notes Using Compose**
```dataview
LIST file.link
FROM "40-Android"
WHERE contains(tags, "android/ui-compose")
```

**Recently Updated (30 days)**
```dataview
TABLE updated, topic, difficulty
FROM ""
WHERE updated >= date(today) - dur(30 days)
SORT updated DESC
```

---

## LLM-Assisted Workflows

| Task | Instruction |
|------|-------------|
| **Translate** | Generate RU from EN (or vice versa); keep both; review |
| **Normalize YAML** | Validate keys/values against taxonomy |
| **Suggest Links** | `Request` 3-5 related concepts/questions |
| **Summaries** | Produce 1-2 line TL;DR for answer sections |

**Key Rule**: Keep `status: draft` for LLM-modified notes until human review.

---

## Maintenance Checklist

### Per-Note Quality Check

- [ ] YAML complete and valid
- [ ] Topic matches folder location
- [ ] 1-3 subtopics defined
- [ ] Tags include `difficulty/*`
- [ ] Android notes have `android/*` tags mirrored from subtopics
- [ ] Linked to at least 1 Concept and 1 MOC
- [ ] `related` field populated
- [ ] EN/RU sections accurate and equivalent
- [ ] Code examples compile

### Vault-Wide Maintenance

- [ ] Check [[00-Administration/Link-Health-Report|Link Health Report]] for broken links
- [ ] Dedupe similar tags (`hashmap` vs `hash-map`)
- [ ] Update `updated` timestamp on meaningful edits
- [ ] Archive deprecated notes with `status: retired`

---

## Status Workflow

```
draft --> reviewed --> ready --> retired
  |                      |
  +--- (needs work) <----+
```

| Status | Meaning |
|--------|---------|
| `draft` | New or LLM-generated, needs human review |
| `reviewed` | Human-verified content and metadata |
| `ready` | Production quality, fully validated |
| `retired` | Deprecated, moved to archive |

---

## Controlled Vocabularies Summary

| Field | Valid Values |
|-------|--------------|
| `difficulty` | `easy`, `medium`, `hard` |
| `question_kind` | `coding`, `theory`, `system-design`, `android` |
| `status` | `draft`, `reviewed`, `ready`, `retired` |
| `original_language` | `en`, `ru` |
| `language_tags` | `[en]`, `[ru]`, `[en, ru]` |

Full taxonomy: [[00-Administration/Vault-Rules/TAXONOMY.md]]
