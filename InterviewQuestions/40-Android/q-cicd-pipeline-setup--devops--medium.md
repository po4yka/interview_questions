---
id: 20251012-122800
title: CI/CD Pipeline Setup for Android / Настройка CI/CD пайплайна для Android
aliases: [CI/CD Pipeline Setup for Android, Настройка CI/CD пайплайна для Android]
topic: android
subtopics: [gradle, pipeline]
question_kind: android
difficulty: medium
status: reviewed
moc: moc-android
related: [q-cicd-pipeline-android--android--medium, q-cicd-automated-testing--devops--medium, q-cicd-deployment-automation--devops--medium]
created: 2025-10-11
updated: 2025-10-20
original_language: en
language_tags: [en, ru]
tags: [android/gradle, ci-cd, pipeline, setup, difficulty/medium]
---

# Question (EN)
> How do you set up an Android CI/CD pipeline from scratch (tools, runners, SDK, caches, secrets, and baseline stages)?

# Вопрос (RU)
> Как с нуля настроить CI/CD пайплайн для Android (инструменты, раннеры, SDK, кеши, секреты и базовые этапы)?

---

## Answer (EN)

### Baseline choices
- Platform: GitHub Actions / GitLab CI / Jenkins
- Runners: hosted Linux; self‑hosted for device labs/heavy caching
- JDK 17; Android SDK + cmdline‑tools; Gradle wrapper

### Secrets and security
- Store Play service account JSON, signing keys, API tokens in CI secret store (OIDC where possible)
- Principle of least privilege; rotate regularly; no secrets in repo

### Caches
- Gradle wrapper and dependencies; Gradle build cache; emulator system images (if self‑hosted)
- Enable configuration cache to speed configuration phase

### Baseline stages
- Setup → Static checks (lint/detekt) → Unit tests → Build (AAB/APK) → Instrumented tests (matrix/shards) → Artifacts/Reports → (optional) Deploy

### Minimal setup (GitHub Actions)
```yaml
name: Android CI
on: [pull_request]
jobs:
  setup-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: '17' }
      - uses: gradle/gradle-build-action@v2
      - name: Lint
        run: ./gradlew lintDebug --configuration-cache --build-cache
      - name: Unit tests
        run: ./gradlew testDebugUnitTest --configuration-cache --build-cache --parallel
      - name: Build
        run: ./gradlew :app:assembleDebug --configuration-cache --build-cache
      - name: Upload reports
        uses: actions/upload-artifact@v4
        with: { name: reports, path: '**/build/reports/**' }
```

### Devices/emulators
- For PRs: small emulator matrix (API/ABI); shard tests; retry failures
- For nightly: broader device farm; perf/jank checks

### Observability
- Keep junit/xml, lint, coverage, and build scans; annotate PRs on failure

## Ответ (RU)

### Базовые выборы
- Платформа: GitHub Actions / GitLab CI / Jenkins
- Раннеры: хостовые Linux; self‑hosted для девайсов/тяжёлых кешей
- JDK 17; Android SDK + cmdline‑tools; Gradle wrapper

### Секреты и безопасность
- Хранить JSON сервис‑аккаунта Play, ключи подписи, токены в хранилище секретов CI (по возможности OIDC)
- Принцип наименьших привилегий; регулярная ротация; никаких секретов в репозитории

### Кеши
- Gradle wrapper и зависимости; Gradle build cache; образы эмуляторов (для self‑hosted)
- Включить configuration cache для ускорения конфигурации

### Базовые этапы
- Setup → Статпроверки → Unit → Сборка (AAB/APK) → Инструментальные (матрица/шарды) → Артефакты/отчёты → (опц.) Деплой

### Минимальная настройка (GitHub Actions)
```yaml
name: Android CI
on: [pull_request]
jobs:
  setup-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: '17' }
      - uses: gradle/gradle-build-action@v2
      - name: Lint
        run: ./gradlew lintDebug --configuration-cache --build-cache
      - name: Unit tests
        run: ./gradlew testDebugUnitTest --configuration-cache --build-cache --parallel
      - name: Build
        run: ./gradlew :app:assembleDebug --configuration-cache --build-cache
      - name: Upload reports
        uses: actions/upload-artifact@v4
        with: { name: reports, path: '**/build/reports/**' }
```

### Девайсы/эмуляторы
- Для PR: небольшая матрица эмуляторов (API/ABI); шардинг; ретраи
- Для nightly: широкая ферма; перф/джанк проверки

### Наблюдаемость
- Хранить junit/xml, lint, coverage, build scans; аннотировать PR при сбоях

---

## Follow-ups
- How to provision self‑hosted runners with pre‑warmed SDKs/emulators?
- How to structure jobs/matrix to minimize total wall time?
- How to standardize reports across modules/apps?

## References
- https://docs.github.com/actions
- https://developer.android.com/studio
- https://docs.gradle.org/current/userguide/build_cache.html

## Related Questions

### Prerequisites (Easier)
- [[q-cicd-pipeline-android--android--medium]]

### Related (Same Level)
- [[q-cicd-automated-testing--devops--medium]]
- [[q-cicd-deployment-automation--devops--medium]]

### Advanced (Harder)
- [[q-android-modularization--android--medium]]
