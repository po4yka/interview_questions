---
id: 20251012-122800
title: CI/CD Pipeline Setup for Android / Настройка CI/CD пайплайна для Android
aliases: ["CI/CD Pipeline Setup for Android", "Настройка CI/CD пайплайна для Android"]
topic: android
subtopics: [ci-cd, gradle, testing-unit]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-gradle-build-optimization--android--medium, q-testing-strategies--android--hard]
sources: []
created: 2025-10-11
updated: 2025-10-29
tags: [android/ci-cd, android/gradle, android/testing-unit, devops, automation, difficulty/medium]
date created: Thursday, October 30th 2025, 11:18:03 am
date modified: Thursday, October 30th 2025, 12:43:36 pm
---

# Вопрос (RU)
> Как настроить CI/CD пайплайн для Android-приложения?

# Question (EN)
> How do you set up a CI/CD pipeline for an Android application?

---

## Ответ (RU)

### Выбор платформы
GitHub Actions (облачные раннеры + бесплатный минуты), GitLab CI (встроенная интеграция), или Jenkins (self-hosted, максимальная гибкость). Для Android предпочтительны Linux-раннеры с Docker-образами, содержащими Android SDK.

### Базовая конфигурация окружения
- **JDK**: указать точную версию через `setup-java` (обычно LTS-релиз)
- **Android SDK**: использовать cmdline-tools или готовые Docker-образы типа `cimg/android`
- **Gradle**: полагаться на wrapper в репозитории, активировать build cache и configuration cache

### Секреты и подписывание
Хранить keystores, service account JSON, API-ключи в защищенных переменных CI. Никогда не коммитить credential файлы. По возможности использовать OIDC для доступа к облачным ресурсам.

### Стратегия кеширования
Кешировать `~/.gradle/caches`, `~/.gradle/wrapper`, зависимости и Build Cache. На self-hosted раннерах можно кешировать emulator system images для ускорения инструментальных тестов.

### Типичный пайплайн
```yaml
# ✅ Минимальная GitHub Actions конфигурация
name: Android CI
on: [pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: '17'
      - uses: gradle/gradle-build-action@v2
        with:
          gradle-home-cache-cleanup: true
      - name: Lint & Test
        run: |
          ./gradlew lintDebug testDebugUnitTest \
            --parallel --build-cache --configuration-cache
      - name: Build APK
        run: ./gradlew :app:assembleDebug
      - name: Upload artifacts
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: reports
          path: '**/build/reports/**'
```

### Инструментальное тестирование
Для UI-тестов использовать матрицу эмуляторов (разные API levels / ABI). Применять test sharding для параллелизации, настроить retry при flaky tests. Полный набор тестов запускать nightly, на PR — smoke subset.

### Артефакты и отчеты
Сохранять JUnit XML, lint results, code coverage (Jacoco/Kover). Аннотировать PR комментариями при падении тестов или lint warnings. Публиковать build scans для диагностики производительности сборки.

## Answer (EN)

### Platform Selection
GitHub Actions (cloud runners + free minutes), GitLab CI (built-in integration), or Jenkins (self-hosted, maximum flexibility). For Android, prefer Linux runners with Docker images containing Android SDK.

### Basic Environment Setup
- **JDK**: specify exact version via `setup-java` (usually LTS release)
- **Android SDK**: use cmdline-tools or prebuilt Docker images like `cimg/android`
- **Gradle**: rely on wrapper in repository, enable build cache and configuration cache

### Secrets and Signing
Store keystores, service account JSON, API keys in CI secret variables. Never commit credential files. Use OIDC for cloud resource access when possible.

### Caching Strategy
Cache `~/.gradle/caches`, `~/.gradle/wrapper`, dependencies and Build Cache. On self-hosted runners, cache emulator system images to accelerate instrumented tests.

### Typical Pipeline
```yaml
# ✅ Minimal GitHub Actions configuration
name: Android CI
on: [pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: '17'
      - uses: gradle/gradle-build-action@v2
        with:
          gradle-home-cache-cleanup: true
      - name: Lint & Test
        run: |
          ./gradlew lintDebug testDebugUnitTest \
            --parallel --build-cache --configuration-cache
      - name: Build APK
        run: ./gradlew :app:assembleDebug
      - name: Upload artifacts
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: reports
          path: '**/build/reports/**'
```

### Instrumented Testing
For UI tests use emulator matrix (different API levels / ABI). Apply test sharding for parallelization, configure retry for flaky tests. Run full test suite nightly, smoke subset on PRs.

### Artifacts and Reporting
Save JUnit XML, lint results, code coverage (Jacoco/Kover). Annotate PRs with comments on test failures or lint warnings. Publish build scans for build performance diagnostics.

## Follow-ups
- How do you optimize Gradle build performance in CI beyond basic caching?
- What strategies handle flaky instrumented tests in Android CI pipelines?
- How do you implement blue-green deployments for Android apps via CI/CD?
- What security best practices apply to storing signing keys in CI/CD?
- How do you set up incremental builds in monorepo CI configurations?

## References
- [[c-gradle-build-system]]
- [[c-android-testing-pyramid]]
- [[c-ci-cd-patterns]]
- https://developer.android.com/studio/build
- https://docs.gradle.org/current/userguide/build_cache.html
- https://docs.github.com/en/actions

## Related Questions

### Prerequisites
- [[q-gradle-basics--android--easy]]
- [[q-unit-testing-fundamentals--android--easy]]

### Related
- [[q-gradle-build-optimization--android--medium]]
- [[q-testing-strategies--android--hard]]
- [[q-docker-android-builds--tools--medium]]

### Advanced
- [[q-monorepo-ci-strategies--system-design--hard]]
- [[q-distributed-test-execution--system-design--hard]]
