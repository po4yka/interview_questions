---
id: 20251012-122800
title: CI/CD Pipeline Setup for Android / Настройка CI/CD пайплайна для Android
aliases: ["CI/CD Pipeline Setup for Android", "Настройка CI/CD пайплайна для Android"]
topic: android
subtopics: [ci-cd, gradle]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-cicd-automated-testing--android--medium, q-cicd-deployment-automation--android--medium, q-cicd-pipeline-android--android--medium]
sources: []
created: 2025-10-11
updated: 2025-10-27
tags: [android/ci-cd, android/gradle, difficulty/medium]
---

# Вопрос (RU)
> Как настроить CI/CD пайплайн для Android-приложения?

# Question (EN)
> How do you set up a CI/CD pipeline for an Android application?

---

## Ответ (RU)

### Базовые решения
- Платформа: GitHub Actions / GitLab CI / Jenkins
- Раннеры: облачные Linux; self-hosted для device farm/тяжелого кеширования
- JDK 17; Android SDK + cmdline-tools; Gradle wrapper

### Секреты и безопасность
- Хранить Play service account JSON, ключи подписи, API токены в CI secret store (OIDC где возможно)
- Принцип наименьших привилегий; регулярная ротация; никаких секретов в репозитории

### Кеширование
- Gradle wrapper и зависимости; Gradle build cache; образы эмуляторов (для self-hosted)
- Включить configuration cache для ускорения фазы конфигурации

### Основные стадии
- Setup → Статический анализ (lint/detekt) → Unit-тесты → Build (AAB/APK) → Инструментальные тесты (матрица/шардинг) → Артефакты/Отчеты → (опционально) Deploy

### Минимальная настройка (GitHub Actions)
```yaml
name: Android CI
on: [pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: '17' }
      - uses: gradle/gradle-build-action@v2
      - name: Lint
        run: ./gradlew lintDebug --configuration-cache --build-cache
      - name: Unit tests
        run: ./gradlew testDebugUnitTest --parallel
      - name: Build
        run: ./gradlew :app:assembleDebug
      - name: Upload reports
        uses: actions/upload-artifact@v4
        with: { name: reports, path: '**/build/reports/**' }
```

### Устройства/эмуляторы
- Для PR: небольшая матрица эмуляторов (API/ABI); шардинг тестов; retry при падениях
- Для nightly: расширенная device farm; проверки производительности/jank

### Мониторинг
- Сохранять junit/xml, lint, coverage, build scans; аннотировать PR при падениях

## Answer (EN)

### Baseline Choices
- Platform: GitHub Actions / GitLab CI / Jenkins
- Runners: cloud Linux; self-hosted for device farms/heavy caching
- JDK 17; Android SDK + cmdline-tools; Gradle wrapper

### Secrets and Security
- Store Play service account JSON, signing keys, API tokens in CI secret store (OIDC where possible)
- Principle of least privilege; rotate regularly; no secrets in repo

### Caching Strategy
- Gradle wrapper and dependencies; Gradle build cache; emulator system images (self-hosted)
- Enable configuration cache to speed configuration phase

### Pipeline Stages
- Setup → Static checks (lint/detekt) → Unit tests → Build (AAB/APK) → Instrumented tests (matrix/shards) → Artifacts/Reports → (optional) Deploy

### Minimal Setup (GitHub Actions)
```yaml
name: Android CI
on: [pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: '17' }
      - uses: gradle/gradle-build-action@v2
      - name: Lint
        run: ./gradlew lintDebug --configuration-cache --build-cache
      - name: Unit tests
        run: ./gradlew testDebugUnitTest --parallel
      - name: Build
        run: ./gradlew :app:assembleDebug
      - name: Upload reports
        uses: actions/upload-artifact@v4
        with: { name: reports, path: '**/build/reports/**' }
```

### Device Testing
- PRs: small emulator matrix (API/ABI); shard tests; retry failures
- Nightly: broader device farm; performance/jank checks

### Observability
- Keep junit/xml, lint, coverage, build scans; annotate PRs on failure

## Follow-ups
- How to provision self-hosted runners with pre-warmed SDKs and emulators?
- How to structure job matrices to minimize total pipeline wall time?
- How to integrate code coverage and static analysis reporting in PRs?
- What strategies exist for incremental builds in monorepo setups?
- How to handle flaky instrumented tests in CI?

## References
- https://docs.github.com/actions - GitHub Actions documentation
- https://developer.android.com/studio/build - Android build system
- https://docs.gradle.org/current/userguide/build_cache.html - Gradle build cache

## Related Questions

### Prerequisites
- Understanding of Gradle build system basics
- Familiarity with Android build variants and product flavors

### Related (Same Level)
- [[q-cicd-automated-testing--android--medium]]
- [[q-cicd-deployment-automation--android--medium]]
- [[q-cicd-pipeline-android--android--medium]]

### Advanced (Harder)
- Implementing modular CI pipelines for multi-module Android projects
- Setting up distributed test execution across device farms
- Optimizing build performance in large-scale Android codebases
