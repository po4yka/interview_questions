---
id: android-048
title: CI/CD Pipeline for Android / CI/CD пайплайн для Android
aliases: [CI/CD Pipeline for Android, CI/CD пайплайн для Android]
topic: android
subtopics:
  - ci-cd
  - gradle
  - testing-instrumented
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - q-android-build-optimization--android--medium
  - q-android-release-pipeline-cicd--android--hard
  - q-build-optimization-gradle--android--medium
  - q-cicd-automated-testing--android--medium
  - q-cicd-deployment-automation--android--medium
  - q-cicd-pipeline-setup--android--medium
created: 2025-10-11
updated: 2025-11-10
sources: []
tags: [android/ci-cd, android/gradle, android/testing-instrumented, difficulty/medium]

date created: Saturday, November 1st 2025, 12:46:45 pm
date modified: Tuesday, November 25th 2025, 8:54:02 pm
---

# Вопрос (RU)
> Как построить эффективный CI/CD пайплайн для Android-приложения?

# Question (EN)
> How to build an effective CI/CD pipeline for Android applications?

---

## Ответ (RU)

### Цели Пайплайна

* **Скорость**: проверки PR ≤10 минут на средних проектах
* **Воспроизводимость**: Gradle wrapper, зафиксированные версии SDK/build-tools
* **Безопасность**: OIDC для Play Console (без долгоживущих ключей), secret scanning
* **Надёжность**: минимальная flakiness, детерминированные релизы

### Основные Этапы

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
* Dependency security scan (OWASP)

**3. Unit тесты**
```kotlin
tasks.withType<Test> {
    maxParallelForks = Runtime.getRuntime().availableProcessors()
    // ✅ Retry plugin для flaky тестов (макс 1 retry)
}
```
* Kover/Jacoco для покрытия (XML + HTML)
* Отслеживание и карантин новых flaky-тестов в изменённых модулях на основе истории запусков

**4. Build**
```bash
./gradlew bundleRelease \
  --build-cache \
  --configuration-cache
# ✅ Производит AAB, mapping.txt, splits
```
* R8 full mode, reproducible versioning

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

### Оптимизация

**Кэширование**
* Configuration cache + remote build cache
* Кэш образов AVD
* Gradle wrapper, зависимости, build outputs

**Параллелизм**
* `--parallel` + настройка `org.gradle.workers.max`
* Независимые jobs (checks/tests/build)
* Matrix-запуски по уровням API

### Quality Gates (RU)

| Gate | Threshold | Action |
|------|-----------|--------|
| Lint | Fatal + новые ошибки | Block merge |
| Coverage | ≥70% lines, ≥50% branch | Fail для изменённых модулей |
| Security | High/Critical CVE | Block merge |
| Tests | ≥99% pass rate | Quarantine flaky |

### Release Workflow (RU)

```yaml
# Staged rollout
1. Build signed AAB (release config)
2. Upload to Play internal track (OIDC)
3. Staged rollout: 5% → 20% → 50% → 100%
4. Upload ProGuard mapping + native symbols
5. Auto-promote при здоровых метриках
```

**Rollback strategy**:
* Остановить rollout при падении crash-free users
* Контроль бюджета размера (max delta MB)
* Мониторинг уровня ANR

## Answer (EN)

### Pipeline Goals

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
* Track and quarantine newly flaky tests in changed modules based on run history

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

### Optimization

**Caching**
* Configuration cache + remote build cache
* AVD images cache
* Gradle wrapper, dependencies, build outputs

**Parallelism**
* `--parallel` + tune `org.gradle.workers.max`
* Independent jobs (checks/tests/build)
* Matrix runs across API levels

### Quality Gates

| Gate | Threshold | Action |
|------|-----------|--------|
| Lint | Fatal + new errors | Block merge |
| Coverage | ≥70% lines, ≥50% branch | Fail for changed modules |
| Security | High/Critical CVE | Block merge |
| Tests | ≥99% pass rate | Quarantine flaky |

### Release Workflow

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

---

## Дополнительные Вопросы (RU)

- Как обрабатывать flaky-тесты в CI, не блокируя полностью PR?
- Каковы компромиссы между локальным и удалённым build cache?
- Как реализовать zero-downtime откаты релизов Android?
- По каким метрикам принимать решение о продвижении staged rollout (crash rate, ANR, install success)?
- Как безопасно хранить ключи подписи и API credentials в облачном CI?

## Follow-ups

- How do you handle flaky tests in CI without blocking PRs entirely?
- What are the trade-offs between local vs remote build cache configurations?
- How do you implement zero-downtime rollbacks for Android releases?
- What metrics determine staged rollout promotion decisions (crash rate, ANR, install success)?
- How do you secure signing keys and API credentials in cloud CI environments?

## Ссылки (RU)

- [[c-app-bundle]]
- [[c-encryption]]
- https://docs.github.com/actions/automating-builds-and-tests/building-and-testing-java-with-gradle
- https://developer.android.com/studio/test/gradle-managed-devices
- https://docs.gradle.org/current/userguide/configuration_cache.html
- https://github.com/Triple-T/gradle-play-publisher

## References

- [[c-app-bundle]]
- [[c-encryption]]
- https://docs.github.com/actions/automating-builds-and-tests/building-and-testing-java-with-gradle
- https://developer.android.com/studio/test/gradle-managed-devices
- https://docs.gradle.org/current/userguide/configuration_cache.html
- https://github.com/Triple-T/gradle-play-publisher

## Связанные Вопросы (RU)

### Базовые (проще)
- [[q-build-optimization-gradle--android--medium]] — основы оптимизации сборки Gradle
- [[q-cicd-automated-testing--android--medium]] — стратегии автоматизации тестирования
- Понимание жизненного цикла и задач Gradle

### На Том Же Уровне
- [[q-cicd-deployment-automation--android--medium]] — детали автоматизации деплоя
- Управление зависимостями Gradle и version catalogs
- Стратегии шардинга и параллелизации Android-тестов
- Конфигурация ProGuard/R8 для релизных сборок

### Продвинутые (сложнее)
- Продвинутая оптимизация build cache и интеграция Gradle Enterprise
- Кастомные Gradle-плагины для автоматизации CI/CD
- Мультимодульная архитектура Android для эффективности CI
- Dynamic Feature Modules и стратегии staged rollout

## Related Questions

### Prerequisites (Easier)
- [[q-build-optimization-gradle--android--medium]] - Gradle build optimization basics
- [[q-cicd-automated-testing--android--medium]] - Test automation strategies
- Understanding of Gradle build lifecycle and tasks

### Related (Same Level)
- [[q-cicd-deployment-automation--android--medium]] - Deployment automation details
- Gradle dependency management and version catalogs
- Android test sharding and parallelization strategies
- ProGuard/R8 configuration for release builds

### Advanced (Harder)
- Advanced build cache optimization and Gradle Enterprise integration
- Custom Gradle plugins for CI/CD workflow automation
- Multi-module Android architecture for CI efficiency
- Dynamic feature modules and staged rollout strategies
