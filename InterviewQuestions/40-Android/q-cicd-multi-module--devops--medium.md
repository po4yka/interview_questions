---
id: 20251012-122798
title: CI/CD for Multi‑Module Android / CI/CD для мультимодульных Android‑проектов
aliases: [CI/CD for Multi-Module Android, CI/CD для мультимодульных Android‑проектов]
topic: android
subtopics: [gradle, modularization]
question_kind: android
difficulty: medium
status: reviewed
moc: moc-android
related: [q-android-modularization--android--medium, q-build-optimization-gradle--gradle--medium, q-cicd-automated-testing--devops--medium]
created: 2025-10-11
updated: 2025-10-20
original_language: en
language_tags: [en, ru]
tags: [android/gradle, modularization, ci-cd, affected-targets, difficulty/medium]
---
# Question (EN)
> How do you design CI/CD for multi‑module Android to build and test only affected modules fast and reliably?

# Вопрос (RU)
> Как спроектировать CI/CD для мультимодульного Android‑проекта, чтобы быстро и надёжно собирать и тестировать только затронутые модули?

---

## Answer (EN)

### Goals
- Sub‑10 minute PR checks; scale with modules
- Build/test only what changed; deterministic caching

### Key ideas
- Affected graph: map modules → dependencies; compute impacted set from changed files
- Task filtering: run Gradle tasks only for impacted modules (and dependents)
- Caching: configuration cache + build cache + dependency cache
- Parallelism: matrix by module group, `--parallel`, test sharding

### Minimal strategy (pseudo)
```bash
# 1) List changed files vs main
CHANGED=$(git diff --name-only origin/main...HEAD)
# 2) Map files → modules
AFFECTED=$(scripts/resolve-modules.sh "$CHANGED")
# 3) Expand dependents (reverse deps)
AFFECTED=$(scripts/expand-dependents.sh "$AFFECTED")
# 4) Run only needed tasks
./gradlew $(echo $AFFECTED | xargs -n1 -I{} echo {}:assemble {}:testDebugUnitTest) \
  --configuration-cache --build-cache --parallel
```

### Gradle assistance
- Use included builds/composite builds for isolated caching
- Convention plugins in `build-logic/` for unified tasks and reports
- Configure per‑module test/lint; aggregate reports at root

### Flaky/stability
- Quarantine flakies per module; rerun failed shards only
- Hermetic tests: no network, fixed toolchains/SDKs

## Ответ (RU)

### Цели
- Проверки PR < 10 минут; масштабирование по модулям
- Собирать/тестировать только затронутые; детерминированные кеши

### Ключевые идеи
- Граф влияния: модули → зависимости; вычислять затронутые по изменённым файлам
- Фильтрация задач: запускать Gradle‑таски лишь для затронутых модулей (и зависимых)
- Кеширование: configuration cache + build cache + кеш зависимостей
- Параллелизм: матрица по группам модулей, `--parallel`, шардинг тестов

### Минимальная стратегия (псевдо)
```bash
# 1) Изменённые файлы к main
CHANGED=$(git diff --name-only origin/main...HEAD)
# 2) Файлы → модули
AFFECTED=$(scripts/resolve-modules.sh "$CHANGED")
# 3) Добавить зависящие модули
AFFECTED=$(scripts/expand-dependents.sh "$AFFECTED")
# 4) Запускать только нужные таски
./gradlew $(echo $AFFECTED | xargs -n1 -I{} echo {}:assemble {}:testDebugUnitTest) \
  --configuration-cache --build-cache --parallel
```

### Помощь Gradle
- Included/composite builds для изолированных кешей
- Конвеншн‑плагины в `build-logic/` для единообразных задач/отчётов
- Настройка test/lint на модуль; агрегация отчётов на корне

### Флаки/стабильность
- Карантин флаков по модулям; перезапуск только упавших шардов
- Герметичные тесты: без сети, фиксированные toolchains/SDK

---

## Follow-ups
- How to maintain module dependency graph (Gradle tooling API vs static mapping)?
- How to group modules for matrix builds to balance load?
- How to aggregate coverage across modules reliably?

## References
- https://docs.gradle.org/current/userguide/performance.html
- https://developer.android.com/studio/projects#Modularize

## Related Questions

### Prerequisites (Easier)
- [[q-android-modularization--android--medium]]

### Related (Same Level)
- [[q-build-optimization-gradle--gradle--medium]]
- [[q-cicd-automated-testing--devops--medium]]

### Advanced (Harder)
- [[q-android-performance-measurement-tools--android--medium]]
