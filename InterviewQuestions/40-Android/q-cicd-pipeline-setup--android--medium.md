---
id: 20251012-122800
title: CI/CD Pipeline Setup for Android / Настройка CI/CD пайплайна для Android
aliases:
- CI/CD Pipeline Setup for Android
- Настройка CI/CD пайплайна для Android
topic: android
subtopics:
- gradle
- ci-cd
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: reviewed
moc: moc-android
related:
- q-cicd-pipeline-android--android--medium
- q-cicd-automated-testing--android--medium
- q-cicd-deployment-automation--android--medium
created: 2025-10-11
updated: 2025-10-20
tags:
- android/gradle
- android/ci-cd
- difficulty/medium
name: Android CI
true:
- pull_request
jobs: null
---

# Вопрос (RU)
> Настройка CI/CD пайплайна для Android?

# Question (EN)
> CI/CD Pipeline Setup for Android?

---

## Ответ (RU)

(Требуется перевод из английской секции)

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

## Follow-ups
- How to provision self‑hosted runners with pre‑warmed SDKs/emulators?
- How to structure jobs/matrix to minimize total wall time?
- How to standardize reports across modules/apps?

## References
- [[c-git]] - Version control fundamentals for CI/CD
- https://docs.github.com/actions
- https://developer.android.com/studio
- https://docs.gradle.org/current/userguide/build_cache.html

## Related Questions

### Prerequisites (Easier)
- [[q-cicd-pipeline-android--android--medium]]

### Related (Same Level)
- [[q-cicd-automated-testing--android--medium]]
- [[q-cicd-deployment-automation--android--medium]]

### Advanced (Harder)
- [[q-android-modularization--android--medium]]
