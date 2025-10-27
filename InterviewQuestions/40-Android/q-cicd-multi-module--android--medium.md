---
id: 20251012-122798
title: CI/CD for Multi‑Module Android / CI/CD для мультимодульных Android‑проектов
aliases: ["CI/CD for Multi-Module Android", "CI/CD для мультимодульных Android‑проектов"]
topic: android
subtopics: [architecture-modularization, gradle, ci-cd]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-android-modularization--android--medium, q-build-optimization-gradle--android--medium, q-cicd-automated-testing--android--medium]
sources: []
created: 2025-10-11
updated: 2025-10-27
tags: [android/architecture-modularization, android/gradle, android/ci-cd, difficulty/medium]
---

# Вопрос (RU)
> Как организовать CI/CD для мультимодульного Android-проекта?

# Question (EN)
> How to organize CI/CD for a multi-module Android project?

---

## Ответ (RU)

### Цели
- Проверки PR < 10 минут; масштабирование с ростом модулей
- Сборка/тестирование только изменённых частей; детерминированное кэширование

### Ключевые идеи
- **Граф зависимостей**: маппинг модулей → зависимости; вычисление затронутого множества по изменённым файлам
- **Фильтрация задач**: запуск Gradle-задач только для затронутых модулей (и зависимых от них)
- **Кэширование**: configuration cache + build cache + dependency cache для оптимизации производительности сборки
- **Параллелизм**: матричные сборки по группам модулей, `--parallel`, шардирование тестов

### Минимальная стратегия (псевдокод)
```bash
# 1) Список изменённых файлов относительно main
CHANGED=$(git diff --name-only origin/main...HEAD)
# 2) Маппинг файлов → модули
AFFECTED=$(scripts/resolve-modules.sh "$CHANGED")
# 3) Расширение зависимых модулей (обратные зависимости)
AFFECTED=$(scripts/expand-dependents.sh "$AFFECTED")
# 4) Запуск только необходимых задач
./gradlew $(echo $AFFECTED | xargs -n1 -I{} echo {}:assemble {}:testDebugUnitTest) \
  --configuration-cache --build-cache --parallel
```

### Помощь от Gradle
- Included builds/composite builds для изолированного кэширования
- Convention plugins в `build-logic/` для унифицированных задач и отчётов
- Настройка тестов/lint per-модуль; агрегация отчётов на корневом уровне

### Стабильность и флаки
- Карантин flaky-тестов по модулям; повтор только упавших шардов
- Эрметичные тесты: без сети, фиксированные toolchains/SDK

## Answer (EN)

### Goals
- Sub‑10 minute PR checks; scale with modules
- Build/test only what changed; deterministic caching

### Key Ideas
- **Affected graph**: map modules → dependencies; compute impacted set from changed files
- **Task filtering**: run Gradle tasks only for impacted modules (and dependents)
- **Caching**: configuration cache + build cache + dependency cache to optimize build performance
- **Parallelism**: matrix by module group, `--parallel`, test sharding

### Minimal Strategy (pseudo)
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

### Gradle Support
- Use included builds/composite builds for isolated caching
- Convention plugins in `build-logic/` for unified tasks and reports
- Configure per-module test/lint; aggregate reports at root

### Stability & Flaky Tests
- Quarantine flakies per module; rerun failed shards only
- Hermetic tests: no network, fixed toolchains/SDKs

---

## Follow-ups
- How to maintain module dependency graph — Gradle tooling API vs static mapping?
- How to group modules for matrix builds to balance CI load?
- How to aggregate code coverage across modules reliably?
- What caching strategies work best for mono-repos with multiple feature modules?
- How to handle version catalog updates in multi-module projects?

## References
- [Gradle Performance Guide](https://docs.gradle.org/current/userguide/performance.html)
- [Android Multi-Module Architecture](https://developer.android.com/studio/projects#Modularize)
- [Gradle Build Cache](https://docs.gradle.org/current/userguide/build_cache.html)

## Related Questions

### Prerequisites
- [[q-android-modularization--android--medium]] — Understanding module boundaries
- [[q-build-optimization-gradle--android--medium]] — Basic Gradle optimization

### Related
- [[q-cicd-automated-testing--android--medium]] — Test automation strategies
- Affected module detection algorithms
- Gradle composite builds setup

### Advanced
- [[q-android-performance-measurement-tools--android--medium]] — Advanced profiling
- CI pipeline optimization for large teams
- Dynamic feature modules in CI/CD
