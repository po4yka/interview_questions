---
id: 20251012-122798
title: CI/CD for Multi‑Module Android / CI/CD для мультимодульных Android‑проектов
aliases: [CI/CD for Multi-Module Android, CI/CD для мультимодульных Android‑проектов]
topic: android
subtopics:
  - architecture-modularization
  - gradle
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - q-android-modularization--android--medium
  - q-build-optimization-gradle--android--medium
  - q-cicd-automated-testing--android--medium
created: 2025-10-11
updated: 2025-10-20
tags: [android/architecture-modularization, android/gradle, difficulty/medium]
date created: Saturday, October 25th 2025, 1:26:30 pm
date modified: Saturday, October 25th 2025, 4:52:48 pm
---

# Вопрос (RU)
> CI/CD для мультимодульных Android‑проектов?

# Question (EN)
> CI/CD for Multi‑Module Android?

---

## Ответ (RU)

(Требуется перевод из английской секции)

## Answer (EN)

### Goals
- Sub‑10 minute PR checks; scale with modules
- Build/test only what changed; deterministic caching

### Key Ideas
- Affected graph: map modules → dependencies; compute impacted set from changed files
- Task filtering: run Gradle tasks only for impacted modules (and dependents)
- Caching: configuration cache + build cache + dependency cache to optimize build performance
- Parallelism: matrix by module group, `--parallel`, test sharding using [[c-unit-testing]]

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

### Gradle Assistance
- Use included builds/composite builds for isolated caching
- Convention plugins in `build-logic/` for unified tasks and reports
- Configure per‑module test/lint; aggregate reports at root

### Flaky/stability
- Quarantine flakies per module; rerun failed shards only
- Hermetic tests: no network, fixed toolchains/SDKs

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
- [[q-build-optimization-gradle--android--medium]]
- [[q-cicd-automated-testing--android--medium]]

### Advanced (Harder)
- [[q-android-performance-measurement-tools--android--medium]]
