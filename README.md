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
📁 InterviewQuestions/    # Main content directory (nesting level 0)
    ├─ Algorithms/     # coding interview problems, LeetCode-style (nesting level 1)
    ├─ Android/        # platform, APIs, patterns, pitfalls (nesting level 1)
    ├─ Behavioural/    # optional; non-technical (nesting level 1)
    ├─ CompSci/        # computer science concepts (nesting level 1)
    ├─ Data Structures/ # data structure implementations (nesting level 1)
    └─ System Design/  # scenarios, components, trade-offs (nesting level 1)
```

**Notes**

* Files **belong to exactly one topic folder**. Use tags/links for cross-cutting concerns (e.g., `hash-table`, `graphs`).
* Concept notes live in **Concepts** and are referenced by many questions.
* MOCs (hub notes) live in **MOCs** and index a topic via links and/or Dataview.

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
id: iv-2025-0001           # unique id (string)
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
moc: [[moc-algorithms]]    # link to Map of Content
related:                   # optional cross-links
  - [[c-hash-map]]
  - [[q-three-sum--algorithms--medium]]

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
id: <% tp.date.now("YYYY") %>-<% tp.user.uid() %>
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

## LLM Workflows (Optional, Reviewed)

* **Translate sections**: Select "Вопрос (RU)" -> generate "Question (EN)" -> human review.
* **Normalize YAML**: Ask model to validate/repair keys (`topic`, `difficulty`, `tags`).
* **Summarize**: Generate a 1–2 line TL;DR for the top of the answer sections.
* **Cross-linking suggestions**: Ask for 3–5 related concepts/questions to link.

**Rule**: All LLM changes remain **draft** until reviewed; update `status` to `reviewed/ready` after verification.

---

## Maintenance & Hygiene

* **Statuses**: `draft` -> `reviewed` -> `ready`.
* **Updates**: always bump `updated` in YAML.
* **Migrations**: prefer adding aliases over renaming filenames; if rename is necessary, update incoming links.
* **Archive**: move outdated/duplicate notes to `99-Archive/` and mark `status: retired`.
* **Tag health**: periodically audit and merge near-duplicates (e.g., `hashmap` vs `hash-map`).

---

## Backup & Sync

* Use Git (commit early/often). Consider excluding heavy caches; keep `.obsidian` to preserve plugin settings.
* Cross-device: Obsidian Sync or your preferred encrypted sync; keep IDs stable across devices.

---

## Quickstart

1. Create the folder layout.
2. Install plugins: Dataview, Templater (optional: MetaEdit, Tag Wrangler, Breadcrumbs).
3. Add `_tpl-qna.md` template and bind a hotkey.
4. Create a first concept note (e.g., `c-hash-map.md`).
5. Create a first question (e.g., `q-two-sum--algorithms--easy.md`) via the template.
6. Fill EN/RU sections; add YAML; link to concept + MOC; tag properly.
7. Use MOC + Dataview to surface and review.

---

## FAQ

* **Why English filenames and tags?** Predictable search, portability, and ecosystem conventions.
* **Where do Russian titles live?** In `aliases` and in the RU sections of the body.
* **Multiple topics?** Pick one `topic` (folder) and express extras via `subtopics`/`tags`/links.
