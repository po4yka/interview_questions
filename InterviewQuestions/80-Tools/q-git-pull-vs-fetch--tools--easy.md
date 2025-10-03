---
id: 20251003140703
title: Git pull vs fetch / Различия между git pull и git fetch
aliases: []

# Classification
topic: tools
subtopics: [git, version-control]
question_kind: theory
difficulty: easy

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/1399
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: draft
moc: moc-tools
related:
  - c-git
  - c-version-control

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [git, fetch, pull, version-control, remote, difficulty/easy, easy_kotlin, lang/ru, tools]
---

# Question (EN)
> Difference between git pull and git fetch

# Вопрос (RU)
> Разница между git pull и git fetch

---

## Answer (EN)

**git fetch** downloads changes from the remote repository but doesn't merge them. Used for preview and review before integrating changes.

```bash
git fetch origin
# Downloads changes but doesn't apply them
# You can review with: git log origin/main
```

**git pull** = fetch + merge - downloads and immediately applies changes to the current branch.

```bash
git pull origin main
# Equivalent to:
# git fetch origin
# git merge origin/main
```

**Key differences:**
- **fetch**: Safe, non-destructive, lets you review changes first
- **pull**: Convenient but immediately modifies your working branch
- **Best practice**: Use `fetch` to review, then merge/rebase manually when ready

## Ответ (RU)

git fetch — загружает изменения из удалённого репозитория, но не сливает их. Используется для предварительного обзора. git pull = fetch + merge — загружает и сразу применяет изменения к текущей ветке.

---

## Follow-ups
- When should you use fetch instead of pull?
- What is git pull --rebase?
- How to configure default pull behavior?

## References
- [[c-git]]
- [[c-version-control]]
- [[moc-tools]]

## Related Questions
- [[q-git-merge-vs-rebase--tools--medium]]
- [[q-git-squash-commits--tools--medium]]
