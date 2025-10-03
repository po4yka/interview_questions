---
id: 20251003140702
title: Git merge vs rebase / Различия между merge и rebase в Git
aliases: []

# Classification
topic: tools
subtopics: [git, version-control]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/678
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
tags: [git, merge, rebase, version-control, workflow, difficulty/medium, easy_kotlin, lang/ru, tools]
---

# Question (EN)
> Difference between merge and rebase

# Вопрос (RU)
> Разница между merge и rebase

---

## Answer (EN)

Merge and Rebase are Git commands for combining branches, but they work differently:

### Git Merge
- **Creates a new merge commit** that combines the histories of both branches
- **Preserves the complete history** of both branches
- Results in a **branched/non-linear history**
- Safe for shared/public branches
- History shows exactly when branches were merged

**Example:**
```bash
git checkout main
git merge feature-branch
```

### Git Rebase
- **Rewrites history** by moving commits from the current branch on top of another
- Creates a **linear, cleaner history**
- Makes it appear as if changes were made sequentially
- **Potentially risky** for already published code
- Should not be used on public/shared branches

**Example:**
```bash
git checkout feature-branch
git rebase main
```

**When to use:**
- **Merge**: When working on shared branches, want to preserve full history
- **Rebase**: When cleaning up local feature branches before merging, want linear history

## Ответ (RU)

Merge и Rebase — это команды в Git для объединения веток, но работают они по-разному. Merge создает новый коммит слияния, сохраняя историю обеих веток, что может привести к разветвленной истории. Rebase переписывает историю, перенося коммиты текущей ветки на вершину другой, делая историю линейной и более чистой, но с потенциальными рисками для уже опубликованного кода.

---

## Follow-ups
- What is the "golden rule" of rebasing?
- How to resolve conflicts during rebase?
- What is interactive rebase used for?

## References
- [[c-git]]
- [[c-version-control]]
- [[moc-tools]]

## Related Questions
- [[q-git-squash-commits--tools--medium]]
- [[q-git-pull-vs-fetch--tools--easy]]
