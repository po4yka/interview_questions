---
id: android-052
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
updated: 2025-10-29
tags: [android/architecture-modularization, android/gradle, android/ci-cd, difficulty/medium]
date created: Thursday, October 30th 2025, 11:18:32 am
date modified: Thursday, October 30th 2025, 12:43:34 pm
---

# Вопрос (RU)
> Как организовать CI/CD для мультимодульного Android-проекта с учётом оптимизации времени сборки и детерминированности?

# Question (EN)
> How to organize CI/CD for a multi-module Android project with build time optimization and deterministic behavior?

---

## Ответ (RU)

### Цели CI/CD для мультимодульных проектов
- **Скорость**: PR-проверки < 10 минут независимо от размера проекта
- **Эффективность**: сборка и тестирование только изменённых модулей и их зависимостей
- **Детерминированность**: стабильные результаты, воспроизводимые сборки
- **Масштабируемость**: время сборки растёт линейно (не квадратично) с ростом числа модулей

### Ключевые стратегии

#### 1. Affected Module Detection (определение затронутых модулей)
Вычисление минимального набора модулей для проверки на основе изменённых файлов:

```bash
# Граф зависимостей модулей
# :app -> :feature:home, :feature:profile
# :feature:home -> :core:ui, :core:network
# :feature:profile -> :core:ui, :core:database

# ✅ Если изменён :core:ui → собрать :core:ui, :feature:home, :feature:profile, :app
CHANGED=$(git diff --name-only origin/main...HEAD)
AFFECTED=$(scripts/affected-modules.sh "$CHANGED")
# :core:ui :feature:home :feature:profile :app
```

**Алгоритм**:
1. Маппинг изменённых файлов → модули (файлы в `core/ui/` → модуль `:core:ui`)
2. Поиск обратных зависимостей (reverse dependencies) для каждого модуля
3. Дедупликация и расчёт минимального множества

#### 2. Gradle Task Filtering (фильтрация задач)
Запуск только необходимых Gradle-задач:

```bash
# ✅ Запуск только для затронутых модулей
./gradlew \
  :core:ui:assemble :core:ui:testDebugUnitTest \
  :feature:home:assemble :feature:home:testDebugUnitTest \
  --configuration-cache \
  --build-cache \
  --parallel
```

```bash
# ❌ Избегать полной сборки
./gradlew assembleDebug testDebugUnitTest  # медленно
```

#### 3. Кэширование (трёхуровневое)
- **Configuration Cache**: кэш графа задач Gradle (`.gradle/configuration-cache/`)
- **Build Cache**: remote/local кэш артефактов задач (`buildCache { remote { ... } }`)
- **Dependency Cache**: кэш зависимостей CI (Maven/Gradle, actions/cache)

```kotlin
// build.gradle.kts (root)
buildCache {
    remote<HttpBuildCache> {
        url = uri("https://cache.example.com")
        isPush = System.getenv("CI_BUILD_CACHE_PUSH") == "true"
        credentials {
            username = System.getenv("BUILD_CACHE_USER")
            password = System.getenv("BUILD_CACHE_PASS")
        }
    }
}
```

#### 4. Параллелизм и шардирование
- **Matrix builds**: группировка модулей в независимые задачи CI (`:feature:*` → один job, `:core:*` → другой)
- **Test sharding**: распределение тестов по нескольким runner'ам (Gradle Enterprise Test Distribution)
- **Parallel execution**: `org.gradle.parallel=true`, `--max-workers=<N>`

### Gradle-специфичные техники

#### Convention Plugins (плагины конвенций)
Унификация конфигурации модулей через `build-logic/`:

```kotlin
// build-logic/src/main/kotlin/android-feature-convention.gradle.kts
plugins {
    id("com.android.library")
    id("kotlin-android")
}

android {
    compileSdk = 34
    defaultConfig { minSdk = 24 }
    testOptions { unitTests.isReturnDefaultValues = true }
}

dependencies {
    implementation(project(":core:ui"))
    testImplementation(libs.junit)
}
```

**Преимущества**: изменение конвенции → автоматическое применение ко всем модулям

#### Composite/Included Builds
Изоляция `build-logic/` для быстрого кэширования:

```kotlin
// settings.gradle.kts
includeBuild("build-logic")
```

### Стабильность и борьба с flaky-тестами
- **Quarantine**: изоляция нестабильных тестов по модулям (аннотации `@Ignore`, отдельные test suites)
- **Retry mechanism**: повтор только упавших тестов (Gradle Test Retry Plugin)
- **Hermetic tests**: без сети, фиксированные Java toolchains, детерминированные seed'ы

```kotlin
// ✅ Эрметичные тесты
tasks.withType<Test> {
    jvmArgs("-Djava.net.preferIPv4Stack=true")
    systemProperty("robolectric.offline", "true")
    useJUnitPlatform()
}
```

### Пример минимального CI-скрипта (GitHub Actions)

```yaml
# ✅ Affected modules + caching
- name: Detect affected modules
  run: |
    CHANGED=$(git diff --name-only origin/main...HEAD)
    echo "AFFECTED=$(./scripts/affected-modules.sh "$CHANGED")" >> $GITHUB_ENV

- name: Build and test
  run: |
    ./gradlew ${{ env.AFFECTED }}:assemble ${{ env.AFFECTED }}:test \
      --configuration-cache --build-cache --parallel
```

## Answer (EN)

### CI/CD Goals for Multi-Module Projects
- **Speed**: PR checks < 10 minutes regardless of project size
- **Efficiency**: build and test only changed modules and their dependencies
- **Determinism**: stable results, reproducible builds
- **Scalability**: build time grows linearly (not quadratically) with module count

### Key Strategies

#### 1. Affected Module Detection
Computing minimal set of modules to verify based on changed files:

```bash
# Module dependency graph
# :app -> :feature:home, :feature:profile
# :feature:home -> :core:ui, :core:network
# :feature:profile -> :core:ui, :core:database

# ✅ If :core:ui changed → build :core:ui, :feature:home, :feature:profile, :app
CHANGED=$(git diff --name-only origin/main...HEAD)
AFFECTED=$(scripts/affected-modules.sh "$CHANGED")
# :core:ui :feature:home :feature:profile :app
```

**Algorithm**:
1. Map changed files → modules (files in `core/ui/` → module `:core:ui`)
2. Find reverse dependencies for each module
3. Deduplicate and compute minimal set

#### 2. Gradle Task Filtering
Run only necessary Gradle tasks:

```bash
# ✅ Run only for affected modules
./gradlew \
  :core:ui:assemble :core:ui:testDebugUnitTest \
  :feature:home:assemble :feature:home:testDebugUnitTest \
  --configuration-cache \
  --build-cache \
  --parallel
```

```bash
# ❌ Avoid full builds
./gradlew assembleDebug testDebugUnitTest  # slow
```

#### 3. Three-Level Caching
- **Configuration Cache**: Gradle task graph cache (`.gradle/configuration-cache/`)
- **Build Cache**: remote/local task artifact cache (`buildCache { remote { ... } }`)
- **Dependency Cache**: CI dependency cache (Maven/Gradle, actions/cache)

```kotlin
// build.gradle.kts (root)
buildCache {
    remote<HttpBuildCache> {
        url = uri("https://cache.example.com")
        isPush = System.getenv("CI_BUILD_CACHE_PUSH") == "true"
        credentials {
            username = System.getenv("BUILD_CACHE_USER")
            password = System.getenv("BUILD_CACHE_PASS")
        }
    }
}
```

#### 4. Parallelism and Sharding
- **Matrix builds**: group modules into independent CI jobs (`:feature:*` → one job, `:core:*` → another)
- **Test sharding**: distribute tests across multiple runners (Gradle Enterprise Test Distribution)
- **Parallel execution**: `org.gradle.parallel=true`, `--max-workers=<N>`

### Gradle-Specific Techniques

#### Convention Plugins
Unify module configuration via `build-logic/`:

```kotlin
// build-logic/src/main/kotlin/android-feature-convention.gradle.kts
plugins {
    id("com.android.library")
    id("kotlin-android")
}

android {
    compileSdk = 34
    defaultConfig { minSdk = 24 }
    testOptions { unitTests.isReturnDefaultValues = true }
}

dependencies {
    implementation(project(":core:ui"))
    testImplementation(libs.junit)
}
```

**Benefits**: change convention → automatically applies to all modules

#### Composite/Included Builds
Isolate `build-logic/` for fast caching:

```kotlin
// settings.gradle.kts
includeBuild("build-logic")
```

### Stability and Flaky Test Management
- **Quarantine**: isolate flaky tests per module (`@Ignore` annotations, separate test suites)
- **Retry mechanism**: retry only failed tests (Gradle Test Retry Plugin)
- **Hermetic tests**: no network, fixed Java toolchains, deterministic seeds

```kotlin
// ✅ Hermetic tests
tasks.withType<Test> {
    jvmArgs("-Djava.net.preferIPv4Stack=true")
    systemProperty("robolectric.offline", "true")
    useJUnitPlatform()
}
```

### Minimal CI Script Example (GitHub Actions)

```yaml
# ✅ Affected modules + caching
- name: Detect affected modules
  run: |
    CHANGED=$(git diff --name-only origin/main...HEAD)
    echo "AFFECTED=$(./scripts/affected-modules.sh "$CHANGED")" >> $GITHUB_ENV

- name: Build and test
  run: |
    ./gradlew ${{ env.AFFECTED }}:assemble ${{ env.AFFECTED }}:test \
      --configuration-cache --build-cache --parallel
```

---

## Follow-ups

- How to maintain and update the module dependency graph — Gradle Tooling API vs static mapping?
- What's the optimal module grouping strategy for matrix builds to balance CI load?
- How to aggregate code coverage reports across modules reliably (Jacoco multi-module)?
- How to handle version catalog updates in multi-module projects without breaking affected module detection?
- What are the trade-offs between Gradle Enterprise Build Cache vs self-hosted solutions?

## References

- [[c-gradle-build-cache]] — Gradle build cache fundamentals
- [[c-android-modularization]] — Module boundaries and dependencies
- [[c-ci-cd-best-practices]] — General CI/CD patterns
- [Gradle Performance Guide](https://docs.gradle.org/current/userguide/performance.html)
- [Android Multi-Module Architecture](https://developer.android.com/topic/modularization)
- [Gradle Build Cache Documentation](https://docs.gradle.org/current/userguide/build_cache.html)
- [Gradle Configuration Cache](https://docs.gradle.org/current/userguide/configuration_cache.html)

## Related Questions

### Prerequisites
- [[q-android-modularization--android--medium]] — Understanding module boundaries and dependency management
- [[q-build-optimization-gradle--android--medium]] — Basic Gradle optimization techniques

### Related
- [[q-cicd-automated-testing--android--medium]] — Test automation strategies in CI/CD
- Module dependency graph algorithms and visualization
- Gradle composite builds and included builds setup
- Remote build cache infrastructure setup

### Advanced
- Dynamic feature modules in CI/CD pipelines
- Gradle Enterprise integration and Test Distribution Platform
- CI pipeline optimization for teams with 100+ modules
- A/B testing build configurations in multi-module projects
