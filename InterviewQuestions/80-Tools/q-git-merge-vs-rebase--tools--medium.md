---
id: tools-003
title: "Git Merge vs Rebase / Git Merge vs Rebase"
aliases: [Git Merge, Git Rebase, Merge vs Rebase, Version Control]
topic: tools
subtopics: [git, version-control]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-tools
related: [q-git-pull-vs-fetch--tools--easy, q-git-squash-commits--tools--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [difficulty/medium, git, merge, rebase, tools, version-control, workflow]
date created: Friday, October 31st 2025, 6:32:23 pm
date modified: Tuesday, November 25th 2025, 8:53:48 pm
---
# Question (EN)
> What is the difference between git merge and git rebase?
# Вопрос (RU)
> В чем разница между git merge и git rebase?

---

## Answer (EN)

`git merge` and `git rebase` are both commands for integrating changes from one branch into another, but they work differently and produce different commit histories.

### Git Merge — Merging with History Preservation

**Creates a merge commit**, preserving the complete history of both branches.

```bash
# Situation: feature branch is behind main
main:    A - B - C - D
               \
feature:        E - F

# git merge
git checkout main
git merge feature

# Result: merge commit M created
main:    A - B - C - D - M
               \       /
feature:        E - F
```

**Merge commit** has two parents: the last commit from `main` (D) and the last commit from `feature` (F).

#### Example

```bash
# On feature branch
git checkout feature
git add .
git commit -m "Feature work"

# Return to main and merge
git checkout main
git merge feature

# History will be branched
git log --graph --oneline

# * abc1234 (HEAD -> main) Merge branch 'feature'
# |\
# | * def5678 (feature) Feature work
# | * ghi9012 More feature work
# * | jkl3456 Main work
# * | mno7890 More main work
# |/
# * pqr1234 Common ancestor
```

### Git Rebase — Rewriting History

**Moves commits** from feature branch onto the tip of main, creating a linear history.

```bash
# Same situation
main:    A - B - C - D
               \
feature:        E - F

# git rebase
git checkout feature
git rebase main

# Result: E and F "replanted" on D
main:    A - B - C - D
                     \
feature:              E' - F'
```

**Important**: E' and F' are NEW commits (different hash), even if changes are the same.

#### Example

```bash
# On feature branch
git checkout feature
git rebase main

# Linear history
git log --oneline

# abc1234 (HEAD -> feature) Feature work (E')
# def5678 More feature work (F')
# jkl3456 Main work (D)
# mno7890 More main work (C)
# pqr1234 Common ancestor (A)

# Now can do fast-forward merge
git checkout main
git merge feature  # Just moves main pointer to F'
```

### Comparison

| Aspect | git merge | git rebase |
|--------|-----------|------------|
| **History** | Branched | Linear |
| **Merge commit** | Created | Not created |
| **Commit hashes** | Preserved | Changed (new) |
| **Conflicts** | Resolved once | May occur for each commit |
| **For published branches** |  Safe |  Dangerous (rewrites history) |
| **For local branches** |  OK |  OK |

### When to Use Merge

** Use merge when:**

1. **Working in a team** — don't rewrite published history
```bash
# feature already in remote
git checkout main
git merge origin/feature  # Safe
```

2. **Want to preserve context** — see when branch was created and merged
```bash
git merge --no-ff feature  # Always creates merge commit
```

3. **Public branch** — main, develop, release
```bash
git checkout main
git merge feature  # History preserved
```

### When to Use Rebase

** Use rebase when:**

1. **Local branch** — not yet published
```bash
# Update local feature branch
git checkout feature
git rebase main
```

2. **Clean history** — want linear history without merge commits
```bash
git checkout feature
git rebase main
git checkout main
git merge feature  # Fast-forward merge
```

3. **Interactive rebase** — clean up history before merge
```bash
git rebase -i main  # Edit/combine commits
```

### Interactive Rebase

Powerful tool for cleaning up history.

```bash
git rebase -i HEAD~3  # Last 3 commits

# Editor opens:
pick abc1234 Add feature X
pick def5678 Fix typo
pick ghi9012 Add tests

# Commands:
# pick (p) - use commit
# reword (r) - change message
# edit (e) - stop for changes
# squash (s) - combine with previous
# fixup (f) - combine, discard message
# drop (d) - delete commit

# Example: combine "Fix typo" with previous
pick abc1234 Add feature X
fixup def5678 Fix typo
pick ghi9012 Add tests
```

### Resolving Conflicts

#### With Merge

```bash
git merge feature

# CONFLICT (content): Merge conflict in file.txt

# Resolve conflict in file.txt
git add file.txt
git commit  # Complete merge
```

#### With Rebase

```bash
git rebase main

# CONFLICT (content): Merge conflict in file.txt

# Resolve conflict
git add file.txt
git rebase --continue  # Continue with next commit

# Or abort
git rebase --abort
```

**Important**: With rebase, conflicts can occur for EACH commit.

### Dangers of Rebase

** DO NOT rebase published branches!**

```bash
#  DANGEROUS - others already downloaded this branch
git checkout feature
git rebase main
git push --force  # Rewrites history!

# Colleagues will have problems:
git pull  # ERROR: diverged histories
```

**Rule**: Never rebase branches that someone else might be using.

### Golden Rule of Rebase

> **Never rebase public history**

```bash
#  OK - local branch
git checkout my-feature
git rebase main

#  NOT OK - public branch
git checkout main
git rebase feature  # DON'T DO THIS!
```

### Practical Workflows

#### Workflow 1: Feature Branch with Merge

```bash
# 1. Create feature branch
git checkout -b feature/new-ui
git commit -m "Add new UI"

# 2. Update main
git checkout main
git pull

# 3. Merge feature
git merge feature/new-ui
git push

# 4. Delete feature branch
git branch -d feature/new-ui
```

#### Workflow 2: Feature Branch with Rebase

```bash
# 1. Create feature branch
git checkout -b feature/new-ui
git commit -m "Add new UI"

# 2. Update and rebase
git checkout main
git pull
git checkout feature/new-ui
git rebase main  # Linear history

# 3. Fast-forward merge
git checkout main
git merge feature/new-ui
git push
```

#### Workflow 3: Interactive Rebase + Merge

```bash
# 1. Work on feature branch
git commit -m "WIP: part 1"
git commit -m "WIP: part 2"
git commit -m "Fix typo"
git commit -m "Add feature"

# 2. Clean up history
git rebase -i main

# Combine WIP commits

# 3. Merge
git checkout main
git merge feature/new-ui
```

### Commands to Undo

```bash
# Undo merge (if not yet pushed)
git merge --abort  # During conflict
git reset --hard HEAD~1  # After merge

# Undo rebase
git rebase --abort  # During rebase
git reflog  # Find previous state
git reset --hard HEAD@{2}  # Go back

# Undo published merge
git revert -m 1 <merge-commit-hash>
```

### Best Practices

1. **Feature branches**: rebase locally, merge into main
2. **Main branch**: only merge, never rebase
3. **Before push**: can rebase
4. **After push**: only merge
5. **Pull requests**: merge or squash
6. **Cleanup history**: interactive rebase before PR

---

## Ответ (RU)

`git merge` и `git rebase` — команды для объединения веток, но работают по-разному и дают разную историю коммитов.

### Git Merge — Объединение С Сохранением Истории

**Создает merge commit**, сохраняя всю историю обеих веток.

```bash
# Ситуация: feature ветка отстала от main
main:    A - B - C - D
               \
feature:        E - F

# git merge
git checkout main
git merge feature

# Результат: создан merge commit M
main:    A - B - C - D - M
               \       /
feature:        E - F
```

**Merge commit** имеет два родителя: последний коммит `main` (D) и последний коммит `feature` (F).

#### Пример

```bash
# На feature ветке
git checkout feature
git add .
git commit -m "Feature work"

# Вернуться на main и смержить
git checkout main
git merge feature

# История будет разветвленной
git log --graph --oneline

# * abc1234 (HEAD -> main) Merge branch 'feature'
# |\
# | * def5678 (feature) Feature work
# | * ghi9012 More feature work
# * | jkl3456 Main work
# * | mno7890 More main work
# |/
# * pqr1234 Common ancestor
```

### Git Rebase — Переписывание Истории

**Переносит коммиты** feature ветки на вершину main, создавая линейную историю.

```bash
# Ситуация: та же
main:    A - B - C - D
               \
feature:        E - F

# git rebase
git checkout feature
git rebase main

# Результат: E и F "пересажены" на D
main:    A - B - C - D
                     \
feature:              E' - F'
```

**Важно**: E' и F' — это НОВЫЕ коммиты (другой hash), даже если изменения те же.

#### Пример

```bash
# На feature ветке
git checkout feature
git rebase main

# История линейная
git log --oneline

# abc1234 (HEAD -> feature) Feature work (E')
# def5678 More feature work (F')
# jkl3456 Main work (D)
# mno7890 More main work (C)
# pqr1234 Common ancestor (A)

# Теперь можно сделать fast-forward merge
git checkout main
git merge feature  # Просто передвинет указатель main на F'
```

### Сравнение

| Аспект | git merge | git rebase |
|--------|-----------|------------|
| **История** | Разветвленная | Линейная |
| **Merge commit** | Создается | Не создается |
| **Хеши коммитов** | Сохраняются | Изменяются (новые) |
| **Конфликты** | Решаются один раз | Могут возникнуть для каждого коммита |
| **Для опубликованных веток** |  Безопасно |  Опасно (переписывает историю) |
| **Для локальных веток** |  OK |  OK |

### Когда Использовать Merge

** Используйте merge когда:**

1. **Работа в команде** — не переписывайте опубликованную историю
```bash
# feature уже в remote
git checkout main
git merge origin/feature  # Безопасно
```

2. **Хотите сохранить контекст** — видно когда ветка была создана и смержена
```bash
git merge --no-ff feature  # Всегда создает merge commit
```

3. **Публичная ветка** — main, develop, release
```bash
git checkout main
git merge feature  # История сохранена
```

### Когда Использовать Rebase

** Используйте rebase когда:**

1. **Локальная ветка** — еще не опубликована
```bash
# Обновить локальную feature ветку
git checkout feature
git rebase main
```

2. **Чистая история** — хотите линейную историю без merge commits
```bash
git checkout feature
git rebase main
git checkout main
git merge feature  # Fast-forward merge
```

3. **Интерактивный rebase** — очистка истории перед merge
```bash
git rebase -i main  # Редактировать/объединить коммиты
```

### Интерактивный Rebase

Мощный инструмент для очистки истории.

```bash
git rebase -i HEAD~3  # Последние 3 коммита

# Откроется редактор:
pick abc1234 Add feature X
pick def5678 Fix typo
pick ghi9012 Add tests

# Команды:
# pick (p) - использовать коммит
# reword (r) - изменить сообщение
# edit (e) - остановиться для изменений
# squash (s) - объединить с предыдущим
# fixup (f) - объединить, отбросив сообщение
# drop (d) - удалить коммит

# Пример: объединить "Fix typo" с предыдущим
pick abc1234 Add feature X
fixup def5678 Fix typo
pick ghi9012 Add tests
```

### Разрешение Конфликтов

#### С Merge

```bash
git merge feature

# CONFLICT (content): Merge conflict in file.txt

# Решить конфликт в file.txt
git add file.txt
git commit  # Завершить merge
```

#### С Rebase

```bash
git rebase main

# CONFLICT (content): Merge conflict in file.txt

# Решить конфликт
git add file.txt
git rebase --continue  # Продолжить с следующим коммитом

# Или отменить
git rebase --abort
```

**Важно**: При rebase конфликты могут возникнуть для КАЖДОГО коммита.

### Опасности Rebase

** НЕ делайте rebase для опубликованных веток!**

```bash
#  ОПАСНО - другие уже скачали эту ветку
git checkout feature
git rebase main
git push --force  # Переписывает историю!

# У коллег возникнут проблемы:
git pull  # ERROR: diverged histories
```

**Правило**: Никогда не делайте rebase для веток, которые кто-то еще может использовать.

### Golden Rule of Rebase

> **Не делайте rebase публичной истории**

```bash
#  OK - локальная ветка
git checkout my-feature
git rebase main

#  НЕ OK - публичная ветка
git checkout main
git rebase feature  # НЕ ДЕЛАЙТЕ ТАК!
```

### Практические Workflow

#### Workflow 1: Feature Branch С Merge

```bash
# 1. Создать feature ветку
git checkout -b feature/new-ui
git commit -m "Add new UI"

# 2. Обновить main
git checkout main
git pull

# 3. Смержить feature
git merge feature/new-ui
git push

# 4. Удалить feature ветку
git branch -d feature/new-ui
```

#### Workflow 2: Feature Branch С Rebase

```bash
# 1. Создать feature ветку
git checkout -b feature/new-ui
git commit -m "Add new UI"

# 2. Обновить и rebase
git checkout main
git pull
git checkout feature/new-ui
git rebase main  # Линейная история

# 3. Fast-forward merge
git checkout main
git merge feature/new-ui
git push
```

#### Workflow 3: Интерактивный Rebase + Merge

```bash
# 1. Работа на feature ветке
git commit -m "WIP: part 1"
git commit -m "WIP: part 2"
git commit -m "Fix typo"
git commit -m "Add feature"

# 2. Очистить историю
git rebase -i main

# Объединить WIP коммиты

# 3. Merge
git checkout main
git merge feature/new-ui
```

### Команды Для Отмены

```bash
# Отменить merge (если еще не push)
git merge --abort  # Во время конфликта
git reset --hard HEAD~1  # После merge

# Отменить rebase
git rebase --abort  # Во время rebase
git reflog  # Найти предыдущее состояние
git reset --hard HEAD@{2}  # Вернуться

# Отменить уже опубликованный merge
git revert -m 1 <merge-commit-hash>
```

### Best Practices

1. **Feature branches**: rebase локально, merge в main
2. **Main branch**: только merge, никогда rebase
3. **Before push**: можно rebase
4. **After push**: только merge
5. **Pull requests**: merge или squash
6. **Cleanup history**: interactive rebase перед PR

---

## References

- [Git Branching - Rebasing](https://git-scm.com/book/en/v2/Git-Branching-Rebasing)
- [Git Merge vs Rebase](https://www.atlassian.com/git/tutorials/merging-vs-rebasing)

---

**Source**: Original content

## Related Questions

- [[q-git-squash-commits--tools--medium]]
- [[q-git-pull-vs-fetch--tools--easy]]
