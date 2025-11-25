---
id: android-052
title: CI/CD for Multi‑Module Android / CI/CD для мультимодульных Android‑проектов
aliases: [CI/CD for Multi-Module Android, CI/CD для мультимодульных Android‑проектов]
topic: android
subtopics:
  - architecture-modularization
  - ci-cd
  - gradle
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: reviewed
moc: moc-android
related:
  - c-gradle
  - c-modularization
  - c-release-engineering
  - q-android-lint-tool--android--medium
  - q-android-modularization--android--medium
  - q-build-optimization-gradle--android--medium
  - q-cicd-automated-testing--android--medium
  - q-module-types-android--android--medium
  - q-multi-module-best-practices--android--hard
sources: []
created: 2025-10-11
updated: 2025-10-29
tags: [android/architecture-modularization, android/ci-cd, android/gradle, difficulty/medium]
date created: Saturday, November 1st 2025, 12:46:45 pm
date modified: Tuesday, November 25th 2025, 8:54:02 pm
---

# Вопрос (RU)
> Как организовать CI/CD для мультимодульного Android-проекта с учётом оптимизации времени сборки и детерминированности?

# Question (EN)
> How to organize CI/CD for a multi-module Android project with build time optimization and deterministic behavior?

---

## Ответ (RU)

### Цели CI/CD Для Мультимодульных Проектов
- **Скорость**: PR-проверки < 10 минут независимо от размера проекта (как ориентир, а не жёсткая гарантия)
- **Эффективность**: сборка и тестирование только изменённых модулей и их зависимостей
- **Детерминированность**: стабильные результаты, воспроизводимые сборки
- **Масштабируемость**: время сборки растёт примерно линейно (а не квадратично) с ростом числа модулей при правильной конфигурации

### Ключевые Стратегии

#### 1. Affected Module Detection (определение Затронутых модулей)
Вычисление минимального набора модулей для проверки на основе изменённых файлов:

```bash
# Граф зависимостей модулей
# :app -> :feature:home, :feature:profile
# :feature:home -> :core:ui, :core:network
# :feature:profile -> :core:ui, :core:database

# ✅ Если изменён :core:ui → собрать :core:ui, :feature:home, :feature:profile, :app
CHANGED=$(git diff --name-only origin/main...HEAD)
AFFECTED=$(scripts/affected-modules.sh "$CHANGED")
# Пример вывода: :core:ui :feature:home :feature:profile :app
```

**Алгоритм**:
1. Маппинг изменённых файлов → модули (файлы в `core/ui/` → модуль `:core:ui`)
2. Поиск обратных зависимостей (reverse dependencies) для каждого модуля
3. Дедупликация и расчёт минимального множества

#### 2. Gradle Task Filtering (фильтрация задач)
Запуск только необходимых Gradle-задач для затронутых модулей:

```bash
# ✅ Запуск только для затронутых модулей (пример с явным перечислением)
./gradlew \
  :core:ui:assemble :core:ui:testDebugUnitTest \
  :feature:home:assemble :feature:home:testDebugUnitTest \
  --configuration-cache \
  --build-cache \
  --parallel
```

```bash
# ❌ Избегать полной сборки без необходимости
./gradlew assembleDebug testDebugUnitTest  # медленно
```

#### 3. Кэширование (трёхуровневое)
- **Configuration Cache**: кэш графа задач Gradle (`.gradle/configuration-cache/`)
- **Build Cache**: локальный (по умолчанию) и/или удалённый кэш артефактов задач (`buildCache { local { ... } remote { ... } }`)
- **Dependency Cache**: кэш Maven/Gradle-репозиториев на уровне CI (например, `actions/cache` или аналог)

```kotlin
// build.gradle.kts (root)
buildCache {
    local {
        isEnabled = true
    }
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

#### 4. Параллелизм И Шардирование
- **Matrix builds**: группировка модулей в независимые задачи CI (`:feature:*` → один job, `:core:*` → другой)
- **Test sharding**: распределение тестов по нескольким runner'ам (например, Gradle Enterprise Test Distribution)
- **Parallel execution**: `org.gradle.parallel=true`, `--max-workers=<N>`

### Gradle-специфичные Техники

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
Изоляция `build-logic/` для быстрого кэширования и независимой сборки:

```kotlin
// settings.gradle.kts
includeBuild("build-logic")
```

### Стабильность И Борьба С Flaky-тестами
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

### Пример Минимального CI-скрипта (GitHub Actions)

```yaml
# ✅ Affected modules + caching
- name: Detect affected modules
  run: |
    CHANGED=$(git diff --name-only origin/main...HEAD)
    AFFECTED=$(./scripts/affected-modules.sh "$CHANGED")
    echo "AFFECTED=$AFFECTED" >> $GITHUB_ENV

- name: Build and test
  run: |
    TASKS=""
    for module in $AFFECTED; do
      TASKS+="$module:assemble $module:test "
    done
    ./gradlew $TASKS --configuration-cache --build-cache --parallel
```

## Answer (EN)

### CI/CD Goals for Multi-Module Projects
- **Speed**: PR checks < 10 minutes regardless of project size (as a target, not a strict guarantee)
- **Efficiency**: build and test only changed modules and their dependencies
- **Determinism**: stable results, reproducible builds
- **Scalability**: build time grows approximately linearly (not quadratically) with module count when configured properly

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
# Example output: :core:ui :feature:home :feature:profile :app
```

**Algorithm**:
1. Map changed files → modules (files in `core/ui/` → module `:core:ui`)
2. Find reverse dependencies for each module
3. Deduplicate and compute minimal set

#### 2. Gradle Task Filtering
Run only necessary Gradle tasks for affected modules:

```bash
# ✅ Run only for affected modules (explicit example)
./gradlew \
  :core:ui:assemble :core:ui:testDebugUnitTest \
  :feature:home:assemble :feature:home:testDebugUnitTest \
  --configuration-cache \
  --build-cache \
  --parallel
```

```bash
# ❌ Avoid full builds when not needed
./gradlew assembleDebug testDebugUnitTest  # slow
```

#### 3. Three-Level Caching
- **Configuration Cache**: Gradle configuration phase cache (`.gradle/configuration-cache/`)
- **Build Cache**: local (by default) and/or remote cache of task outputs (`buildCache { local { ... } remote { ... } }`)
- **Dependency Cache**: CI-level cache of Maven/Gradle dependencies (e.g. `actions/cache` or similar)

```kotlin
// build.gradle.kts (root)
buildCache {
    local {
        isEnabled = true
    }
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
- **Test sharding**: distribute tests across multiple runners (e.g. Gradle Enterprise Test Distribution)
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
Isolate `build-logic` as an included build for faster caching and independent compilation:

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
    AFFECTED=$(./scripts/affected-modules.sh "$CHANGED")
    echo "AFFECTED=$AFFECTED" >> $GITHUB_ENV

- name: Build and test
  run: |
    TASKS=""
    for module in $AFFECTED; do
      TASKS+="$module:assemble $module:test "
    done
    ./gradlew $TASKS --configuration-cache --build-cache --parallel
```

---

## Follow-ups

- How to maintain and update the module dependency graph — Gradle Tooling API vs static mapping?
- What's the optimal module grouping strategy for matrix builds to balance CI load?
- How to aggregate code coverage reports across modules reliably (Jacoco multi-module)?
- How to handle version catalog updates in multi-module projects without breaking affected module detection?
- What are the trade-offs between Gradle Enterprise Build Cache vs self-hosted solutions?

## References

- [Gradle Performance Guide](https://docs.gradle.org/current/userguide/performance.html)
- [Android Multi-Module Architecture](https://developer.android.com/topic/modularization)
- [Gradle Build Cache Documentation](https://docs.gradle.org/current/userguide/build_cache.html)
- [Gradle Configuration Cache](https://docs.gradle.org/current/userguide/configuration_cache.html)

## Related Questions

### Prerequisites / Concepts

- [[c-modularization]]
- [[c-gradle]]
- [[c-release-engineering]]


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
