---
tags:
  - git
  - merge
  - rebase
  - version-control
  - workflow
difficulty: medium
---

# Разница между git merge и git rebase

**English**: Difference between git merge and git rebase

## Answer

`git merge` и `git rebase` — команды для объединения веток, но работают по-разному и дают разную историю коммитов.

### git merge — объединение с сохранением истории

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

### git rebase — переписывание истории

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
| **Для опубликованных веток** | ✅ Безопасно | ⚠️ Опасно (переписывает историю) |
| **Для локальных веток** | ✅ OK | ✅ OK |

### Когда использовать merge

**✅ Используйте merge когда:**

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

### Когда использовать rebase

**✅ Используйте rebase когда:**

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

### Интерактивный rebase

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

### Разрешение конфликтов

#### С merge

```bash
git merge feature

# CONFLICT (content): Merge conflict in file.txt

# Решить конфликт в file.txt
git add file.txt
git commit  # Завершить merge
```

#### С rebase

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

### Опасности rebase

**❌ НЕ делайте rebase для опубликованных веток!**

```bash

# ❌ ОПАСНО - другие уже скачали эту ветку
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

# ✅ OK - локальная ветка
git checkout my-feature
git rebase main

# ❌ НЕ OK - публичная ветка
git checkout main
git rebase feature  # НЕ ДЕЛАЙТЕ ТАК!
```

### Практические workflow

#### Workflow 1: Feature branch с merge

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

#### Workflow 2: Feature branch с rebase

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

#### Workflow 3: Интерактивный rebase + merge

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

### Команды для отмены

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

**English**: **git merge** creates merge commit, preserves both branch histories (non-linear). **git rebase** rewrites history, moves commits to tip of target branch (linear). Use merge for: published branches, team collaboration, preserving context. Use rebase for: local branches, clean linear history, before push. **Never rebase published history** - causes conflicts for others. Merge conflicts resolved once; rebase conflicts may occur per commit. Interactive rebase (`-i`) for cleanup before merge. Fast-forward merge possible after rebase.
