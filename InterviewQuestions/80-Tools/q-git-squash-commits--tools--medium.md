---
id: 20251003140701
title: Git squashing commits / Объединение коммитов в Git
aliases: []

# Classification
topic: tools
subtopics: [git, version-control]
question_kind: practical
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
source: https://t.me/easy_kotlin/283
source_note: easy_kotlin Telegram channel

# Workflow & relations
status: reviewed
moc: moc-tools
related:
  - c-git
  - c-version-control

# Timestamps
created: 2025-10-03
updated: 2025-10-03

# Tags
tags: [git, rebase, squash, version-control, difficulty/medium, easy_kotlin, lang/ru, tools]
---
## Question (EN)
> How to combine multiple commits into one in Git
## Вопрос (RU)
> Как объединить несколько коммитов в один в Git

---

## Answer (EN)

Combining multiple commits into one in Git is a process known as **squashing commits**. There are several ways to perform this operation, depending on your scenario.

### Method 1: Interactive Rebase (recommended)

1. Run interactive rebase:
```bash
git rebase -i HEAD~n
```
where `n` is the number of commits you want to combine

2. In the editor, change `pick` to `squash` (or `s`) for all commits except the first one:
```
pick abc1234 First commit
squash def5678 Second commit
squash ghi9012 Third commit
```

3. Save and close the editor

4. You'll see another editor to combine commit messages - edit as needed and save

### Method 2: Soft Reset and New Commit

1. Create a temporary branch (optional, for safety)
2. Do a soft reset to the desired point:
```bash
git reset --soft HEAD~n
```
3. Create a new commit with all changes:
```bash
git commit -m "Combined commit message"
```

**Note**: Be careful when rewriting history on shared branches!

## Ответ (RU)

Объединение нескольких коммитов в один в Git — это процесс, известный как squash коммитов. Существует несколько способов выполнения этой операции, в зависимости от вашего сценария. Наиболее распространенные способы включают использование интерактивного rebase или создание нового коммита, объединяющего изменения, а затем перезапись истории. Способ 1: Интерактивный rebase. Запустите git rebase -i HEAD~n где n — это количество коммитов, которые вы хотите объединить. Измените pick на squash для всех коммитов кроме самого первого и сохраните изменения. Вы увидите редактор для объединения сообщений коммитов и измените его на нужное. Способ 2: Объединение и создание нового коммита. Создайте временную ветку, сделайте soft reset до нужного момента и создайте новый коммит. Переключитесь обратно на основную ветку и перепишите историю.

---

## Follow-ups
- When should you squash commits vs keep them separate?
- How to handle conflicts during interactive rebase?
- What's the difference between squash and fixup?

## References
- [[c-git]]
- [[c-version-control]]
- [[moc-tools]]

## Related Questions
- [[q-git-merge-vs-rebase--tools--medium]]
