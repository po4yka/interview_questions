---
id: 20251012-122799
title: CI/CD Pipeline for Android / CI/CD пайплайн для Android
aliases: [CI/CD Pipeline for Android, CI/CD пайплайн для Android]
topic: android
subtopics:
  - ci-cd
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
  - q-build-optimization-gradle--android--medium
  - q-cicd-automated-testing--android--medium
  - q-cicd-deployment-automation--android--medium
created: 2025-10-11
updated: 2025-10-27
sources: []
tags: [android/ci-cd, android/gradle, difficulty/medium]
---
# Вопрос (RU)
> CI/CD пайплайн для Android?

# Question (EN)
> CI/CD Pipeline for Android?

---

## Ответ (RU)

### Цели CI/CD пайплайна

* **Скорость**: проверки PR ≤10 минут на средних проектах
* **Воспроизводимость**: Gradle wrapper, зафиксированные версии SDK/build-tools
* **Безопасность**: OIDC для Play Console (без долгоживущих ключей), secret scanning
* **Надёжность**: минимальная flakiness, детерминированные релизы

### Основные этапы

**1. Setup**
```yaml
# GitHub Actions пример
- uses: actions/setup-java@v4
  with:
    distribution: 'temurin'
    java-version: '17'
- uses: android-actions/setup-android@v3
```
* JDK 17/21, Android SDK cmdline-tools
* Gradle configuration cache включён
* Remote build cache (Develocity) read-only для PR

**2. Static checks**
```kotlin
// build.gradle.kts
tasks.register("staticAnalysis") {
    dependsOn("ktlintCheck", "detekt", "lint")
    // ✅ Fail fast на новых нарушениях
}
```
* ktlint, detekt, Android Lint (SARIF для аннотаций PR)
* Dependency security scan (OWASP) с [[c-encryption]]

**3. Unit тесты**
```kotlin
tasks.withType<Test> {
    maxParallelForks = Runtime.getRuntime().availableProcessors()
    // ✅ Retry plugin для flaky тестов (макс 1 retry)
}
```
* Kover/Jacoco для покрытия (XML + HTML), см. [[c-unit-testing]]
* Fail на новых flaky в изменённых модулях

**4. Build**
```bash
./gradlew bundleRelease \
  --build-cache \
  --configuration-cache
# ✅ Производит AAB, mapping.txt, splits
```
* R8 full mode, reproducible versioning, см. [[c-gradle]] и [[c-app-bundle]]

**5. Instrumented тесты**
```kotlin
// Gradle Managed Devices
testOptions {
    managedDevices {
        devices {
            create<ManagedVirtualDevice>("pixel6api33") {
                device = "Pixel 6"
                apiLevel = 33
                systemImageSource = "aosp"
            }
        }
    }
}
```
* Headless emulator (GPU swiftshader)
* Sharding через Marathon/Flank для параллелизма
* Capture logcat, screenshots, videos

### Оптимизация

**Кэширование**
```yaml
# GitHub Actions
- uses: actions/cache@v4
  with:
    key: gradle-${{ hashFiles('**/*.gradle*', 'gradle.properties') }}
    path: |
      ~/.gradle/caches
      ~/.gradle/wrapper
```
* Configuration cache + remote build cache
* AVD images cache (`~/.android/avd`)

**Параллелизм**
* `--parallel` + tune `org.gradle.workers.max`
* Независимые jobs (checks/tests/build)
* Matrix runs по API levels/ABIs

### Quality gates

| Gate | Threshold | Action |
|------|-----------|--------|
| Lint | Fatal + новые ошибки | Block merge |
| Coverage | ≥70% lines, ≥50% branch | Fail для изменённых модулей |
| Security | High/Critical CVE | Block merge |
| Tests | ≥99% pass rate | Quarantine flaky |

### Release workflow

```yaml
# Staged rollout
1. Build signed AAB (release config)
2. Upload to Play internal track (OIDC)
3. Staged rollout: 5% → 20% → 50% → 100%
4. Upload ProGuard mapping + native symbols
5. Auto-promote при здоровых метриках
```

**Rollback strategy**:
* Halt rollout при падении crash-free users
* Size budget enforcement (max delta MB)
* ANR rate monitoring

## Answer (EN)

### CI/CD Pipeline Goals

* **Speed**: PR checks ≤10 min on mid-size projects
* **Reproducibility**: Gradle wrapper, locked SDK/build-tools versions
* **Security**: OIDC for Play Console (no long-lived keys), secret scanning
* **Reliability**: minimal flakiness, deterministic releases

### Core Stages

**1. Setup**
```yaml
# GitHub Actions example
- uses: actions/setup-java@v4
  with:
    distribution: 'temurin'
    java-version: '17'
- uses: android-actions/setup-android@v3
```
* JDK 17/21, Android SDK cmdline-tools
* Gradle configuration cache enabled
* Remote build cache (Develocity) read-only for PRs

**2. Static checks**
```kotlin
// build.gradle.kts
tasks.register("staticAnalysis") {
    dependsOn("ktlintCheck", "detekt", "lint")
    // ✅ Fail fast on new violations
}
```
* ktlint, detekt, Android Lint (SARIF for PR annotations)
* Dependency security scan (OWASP)

**3. Unit tests**
```kotlin
tasks.withType<Test> {
    maxParallelForks = Runtime.getRuntime().availableProcessors()
    // ✅ Retry plugin for flaky tests (max 1 retry)
}
```
* Kover/Jacoco for coverage (XML + HTML)
* Fail on new flaky in changed modules

**4. Build**
```bash
./gradlew bundleRelease \
  --build-cache \
  --configuration-cache
# ✅ Produces AAB, mapping.txt, splits
```
* R8 full mode, reproducible versioning

**5. Instrumented tests**
```kotlin
// Gradle Managed Devices
testOptions {
    managedDevices {
        devices {
            create<ManagedVirtualDevice>("pixel6api33") {
                device = "Pixel 6"
                apiLevel = 33
                systemImageSource = "aosp"
            }
        }
    }
}
```
* Headless emulator (GPU swiftshader)
* Sharding via Marathon/Flank for parallelism
* Capture logcat, screenshots, videos

### Optimization

**Caching**
```yaml
# GitHub Actions
- uses: actions/cache@v4
  with:
    key: gradle-${{ hashFiles('**/*.gradle*', 'gradle.properties') }}
    path: |
      ~/.gradle/caches
      ~/.gradle/wrapper
```
* Configuration cache + remote build cache
* AVD images cache (`~/.android/avd`)

**Parallelism**
* `--parallel` + tune `org.gradle.workers.max`
* Independent jobs (checks/tests/build)
* Matrix runs across API levels/ABIs

### Quality gates

| Gate | Threshold | Action |
|------|-----------|--------|
| Lint | Fatal + new errors | Block merge |
| Coverage | ≥70% lines, ≥50% branch | Fail for changed modules |
| Security | High/Critical CVE | Block merge |
| Tests | ≥99% pass rate | Quarantine flaky |

### Release workflow

```yaml
# Staged rollout
1. Build signed AAB (release config)
2. Upload to Play internal track (OIDC)
3. Staged rollout: 5% → 20% → 50% → 100%
4. Upload ProGuard mapping + native symbols
5. Auto-promote on healthy metrics
```

**Rollback strategy**:
* Halt rollout on crash-free users drop
* Size budget enforcement (max delta MB)
* ANR rate monitoring

## Follow-ups
- How do you handle flaky tests in CI without blocking PRs?
- What's the trade-off between local vs remote build cache?
- How do you implement zero-downtime rollbacks for Android releases?
- What metrics determine staged rollout promotion decisions?
- How do you secure signing keys in cloud CI environments?

## References
- https://docs.github.com/actions/automating-builds-and-tests/building-and-testing-java-with-gradle
- https://developer.android.com/studio/test/gradle-managed-devices
- https://docs.gradle.org/current/userguide/configuration_cache.html
- https://github.com/Triple-T/gradle-play-publisher

## Related Questions

### Prerequisites (Easier)
- [[q-build-optimization-gradle--android--medium]] - Gradle build optimization basics
- [[q-cicd-automated-testing--android--medium]] - Test automation strategies

### Related (Same Level)
- [[q-cicd-deployment-automation--android--medium]] - Deployment automation details
- Gradle dependency management and version catalogs
- Android test sharding strategies

### Advanced (Harder)
- Advanced build cache optimization and configuration
- Custom Gradle plugins for CI/CD workflows
- Multi-module Android architecture for CI efficiency
