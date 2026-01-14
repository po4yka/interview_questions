---
id: android-046
title: CI/CD Pipeline Setup for Android / Настройка CI/CD пайплайна для Android
aliases:
- CI/CD Pipeline Setup for Android
- Настройка CI/CD пайплайна для Android
topic: android
subtopics:
- ci-cd
- testing-unit
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-ci-cd
- c-gradle
- q-android-build-optimization--android--medium
sources: []
created: 2025-10-11
updated: 2025-11-11
tags:
- android/ci-cd
- android/testing-unit
- automation
- devops-ci-cd
- difficulty/medium
anki_cards:
- slug: android-046-0-en
  language: en
  anki_id: 1768365308023
  synced_at: '2026-01-14T09:17:53.347149'
- slug: android-046-0-ru
  language: ru
  anki_id: 1768365308048
  synced_at: '2026-01-14T09:17:53.349739'
---
# Вопрос (RU)
> Как настроить CI/CD пайплайн для Android-приложения?

# Question (EN)
> How do you set up a CI/CD pipeline for an Android application?

---

## Ответ (RU)

### Выбор Платформы
GitHub Actions (облачные раннеры + бесплатный лимит минут в зависимости от тарифа), GitLab CI (встроенная интеграция), или Jenkins (self-hosted, максимальная гибкость). Для Android предпочтительны Linux-раннеры с Docker-образами, содержащими Android SDK.

### Базовая Конфигурация Окружения
- **JDK**: указать точную версию через `setup-java` (обычно LTS-релиз)
- **Android SDK**: использовать cmdline-tools или готовые Docker-образы типа `cimg/android`
- **Gradle**: полагаться на wrapper в репозитории, активировать build cache и (опционально, если сборка совместима) configuration cache

### Секреты И Подписывание
Хранить keystores, service account JSON, API-ключи в защищенных переменных CI. Никогда не коммитить credential файлы. По возможности использовать OIDC для доступа к облачным ресурсам. Использовать отдельные ключи и учетные данные для prod и non-prod окружений; подписывать релизные сборки только в защищенных job'ах с ограниченным доступом.

### Стратегия Кеширования
Кешировать `~/.gradle/caches`, `~/.gradle/wrapper`, зависимости и Build Cache. На self-hosted раннерах можно кешировать emulator system images для ускорения инструментальных тестов.

### Типичный Пайплайн
```yaml
# Minimal GitHub Actions configuration (CI for PR)
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
            --parallel --build-cache
      - name: Build APK
        run: ./gradlew :app:assembleDebug
      - name: Upload artifacts on failure
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: reports
          path: '**/build/reports/**'
```

### Инструментальное Тестирование
Для UI-тестов использовать матрицу эмуляторов (разные API levels / ABI). Применять test sharding для параллелизации, настроить retry при flaky tests. Полный набор тестов запускать nightly, на PR — smoke subset.

### CD (Сборка И Доставка)
Добавить отдельный workflow/job для релизных веток или тегов, который:
- собирает релизный билд (`assembleRelease` или bundle),
- подписывает его с использованием секретов CI,
- публикует в Google Play (internal/beta) или доставляет тестировщикам.

### Артефакты И Отчеты
Сохранять JUnit XML, lint results, code coverage (Jacoco/Kover). Аннотировать PR комментариями при падении тестов или lint warnings. Публиковать build scans для диагностики производительности сборки.

## Answer (EN)

### Platform Selection
GitHub Actions (cloud runners + free minutes quota depending on plan), GitLab CI (built-in integration), or Jenkins (self-hosted, maximum flexibility). For Android, prefer Linux runners with Docker images containing Android SDK.

### Basic Environment Setup
- **JDK**: specify exact version via `setup-java` (usually an LTS release)
- **Android SDK**: use cmdline-tools or prebuilt Docker images like `cimg/android`
- **Gradle**: rely on wrapper in repository, enable build cache and (optionally, when build is compatible) configuration cache

### Secrets and Signing
Store keystores, service account JSON, API keys in CI secret variables. Never commit credential files. Use OIDC for cloud resource access when possible. Use separate keys/credentials for prod vs non-prod; perform release signing only in protected jobs with restricted access.

### Caching Strategy
Cache `~/.gradle/caches`, `~/.gradle/wrapper`, dependencies and Build Cache. On self-hosted runners, cache emulator system images to accelerate instrumented tests.

### Typical Pipeline
```yaml
# Minimal GitHub Actions configuration (CI for PRs)
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
            --parallel --build-cache
      - name: Build APK
        run: ./gradlew :app:assembleDebug
      - name: Upload artifacts on failure
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: reports
          path: '**/build/reports/**'
```

### Instrumented Testing
For UI tests, use an emulator matrix (different API levels / ABIs). Apply test sharding for parallelization, configure retries for flaky tests. Run full test suite nightly, smoke subset on PRs.

### CD (Build and Delivery)
Add a separate workflow/job for release branches or tags that:
- builds the release artifact (`assembleRelease` or bundle),
- signs it using CI-managed secrets,
- publishes to Google Play (internal/beta) or distributes to testers.

### Artifacts and Reporting
Save JUnit XML, lint results, code coverage (Jacoco/Kover). Annotate PRs with comments on test failures or lint warnings. Publish build scans for build performance diagnostics.

## Follow-ups
- How do you optimize Gradle build performance in CI beyond basic caching?
- What strategies handle flaky instrumented tests in Android CI pipelines?
- How do you implement blue-green deployments for Android apps via CI/CD?
- What security best practices apply to storing signing keys in CI/CD?
- How do you set up incremental builds in monorepo CI configurations?

## References
- [[c-ci-cd]]
- https://developer.android.com/studio/build
- https://docs.gradle.org/current/userguide/build_cache.html
- https://docs.github.com/en/actions

## Related Questions

### Prerequisites
- [[q-gradle-basics--android--easy]]

### Related
- [[q-android-build-optimization--android--medium]]
