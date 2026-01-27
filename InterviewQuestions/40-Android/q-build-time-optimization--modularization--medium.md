---
id: android-mod-005
title: Build Time Optimization with Modularization / Оптимизация времени сборки через
  модуляризацию
aliases:
- Build Time Optimization
- Modularization Build Performance
- Ускорение сборки модуляризацией
topic: android
subtopics:
- modularization
- gradle
- build-optimization
question_kind: android
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-android
- q-module-types--modularization--medium
- q-api-vs-implementation--modularization--medium
created: 2026-01-23
updated: 2026-01-23
sources: []
tags:
- android/modularization
- android/gradle
- android/build-optimization
- difficulty/medium
- incremental-build
anki_cards:
- slug: android-mod-005-0-en
  language: en
- slug: android-mod-005-0-ru
  language: ru
---
# Вопрос (RU)

> Как модуляризация улучшает время сборки? Какие механизмы Gradle это обеспечивают?

# Question (EN)

> How does modularization improve build time? What Gradle mechanisms enable this?

---

## Ответ (RU)

Модуляризация значительно ускоряет сборку через **параллелизацию**, **инкрементальную компиляцию** и **кэширование**. Правильно спроектированный граф модулей может сократить время сборки на 50-80%.

### Механизмы Ускорения

#### 1. Параллельная Компиляция

```bash
# gradle.properties
org.gradle.parallel=true
org.gradle.workers.max=8  # Количество воркеров
```

```
Монолит (последовательно):
[====== app ======] -> 60 сек

Модульный проект (параллельно):
[== core:common ==]                    \
[=== core:model ===]                    \
[==== core:ui ====]                      }-> 25 сек
[=== core:domain ===]                   /
[== feature:home ==][== feature:profile ==]
                    [=== app ===]
```

**Формула**: Время сборки = высота графа (самый длинный путь), не общее количество модулей.

#### 2. Инкрементальная Компиляция

```kotlin
// Изменили один файл в :feature:profile

// БЕЗ модуляризации:
// Перекомпилируется ВСЕ приложение -> 60 сек

// С модуляризацией:
// Перекомпилируется только :feature:profile -> 5 сек

// С implementation зависимостями:
// Изменения не "протекают" вверх по графу
```

```kotlin
// BAD: Все зависимости как api - каскадная перекомпиляция
dependencies {
    api(project(":core:network"))  // Изменение в network -> все пересобирается
}

// GOOD: implementation изолирует изменения
dependencies {
    implementation(project(":core:network"))  // Изменение локализовано
}
```

#### 3. Gradle Build Cache

```bash
# gradle.properties
org.gradle.caching=true

# Для CI/CD
# settings.gradle.kts
buildCache {
    local { directory = File(rootDir, "build-cache") }
    remote<HttpBuildCache> {
        url = uri("https://cache.example.com/")
        isPush = System.getenv("CI") != null
    }
}
```

**Как это работает**:
```
Developer A: изменил :feature:home, собрал проект
  -> :core:common, :core:domain кэшируются

Developer B: изменил :feature:profile
  -> :core:common, :core:domain берутся из кэша
  -> Только :feature:profile + :app пересобираются
```

#### 4. Configuration Cache (Gradle 8+)

```bash
# gradle.properties
org.gradle.configuration-cache=true
```

Кэширует результат configuration phase (parsing build scripts).

### Метрики и Измерения

```bash
# Профилирование сборки
./gradlew assembleDebug --profile

# Build Scan (детальный анализ)
./gradlew assembleDebug --scan

# Сравнение с/без кэша
./gradlew clean assembleDebug  # Холодная сборка
./gradlew assembleDebug        # Инкрементальная сборка
```

### Влияние Структуры Графа

```
ПЛОХОЙ ГРАФ (глубокий):
  app -> feature -> domain -> data -> network -> common
  Высота: 6 уровней
  Параллелизм: минимальный

ХОРОШИЙ ГРАФ (широкий):
       app
      / | \
  home profile settings
     \  |  /
     domain
     /    \
  data   network
      \ /
    common
  Высота: 4 уровня
  Параллелизм: максимальный
```

### Оптимизации Gradle

```kotlin
// build.gradle.kts (root)
tasks.withType<org.jetbrains.kotlin.gradle.tasks.KotlinCompile>().configureEach {
    compilerOptions {
        // Инкрементальная компиляция Kotlin
        freeCompilerArgs.addAll(
            "-Xjvm-default=all",
        )
    }
}

// Avoid configuration phase work
subprojects {
    // BAD - выполняется на configuration
    // println("Configuring ${project.name}")

    // GOOD - выполняется на execution
    tasks.register("info") {
        doLast { println("Building ${project.name}") }
    }
}
```

### Стратегии для Больших Проектов

| Стратегия | Эффект | Сложность |
|-----------|--------|-----------|
| Разбить монолит на модули | -40% build time | Высокая |
| `implementation` вместо `api` | -20% incremental | Низкая |
| Включить build cache | -30% CI builds | Низкая |
| Configuration cache | -10% config time | Средняя |
| Remote build cache | -50% CI cold builds | Средняя |
| Gradle Enterprise | Аналитика, кэш | Дорого |

### Практический Пример

```kotlin
// settings.gradle.kts
rootProject.name = "MyApp"

// Включаем все модули
include(
    ":app",
    ":feature:home",
    ":feature:profile",
    ":feature:settings",
    ":core:ui",
    ":core:domain",
    ":core:data",
    ":core:network",
    ":core:database",
    ":core:common",
    ":core:testing"
)

// gradle.properties - оптимизации
/*
org.gradle.parallel=true
org.gradle.caching=true
org.gradle.configuration-cache=true
org.gradle.jvmargs=-Xmx4g -XX:+UseParallelGC
kotlin.incremental=true
kotlin.caching.enabled=true
*/
```

### Результаты (Реальный Проект)

| Метрика | Монолит | Модульный |
|---------|---------|-----------|
| Холодная сборка | 180 сек | 120 сек |
| Инкрементальная (1 файл) | 45 сек | 8 сек |
| CI с кэшем | 180 сек | 60 сек |
| Количество модулей | 1 | 15 |

### Диагностика Проблем

```bash
# Найти медленные задачи
./gradlew assembleDebug --profile
# Открыть build/reports/profile/profile-*.html

# Проверить кэш
./gradlew assembleDebug --build-cache --info | grep -i cache

# Анализ зависимостей
./gradlew :app:dependencies --configuration runtimeClasspath
```

---

## Answer (EN)

Modularization significantly speeds up builds through **parallelization**, **incremental compilation**, and **caching**. A well-designed module graph can reduce build time by 50-80%.

### Acceleration Mechanisms

#### 1. Parallel Compilation

```bash
# gradle.properties
org.gradle.parallel=true
org.gradle.workers.max=8  # Number of workers
```

```
Monolith (sequential):
[====== app ======] -> 60 sec

Modular project (parallel):
[== core:common ==]                    \
[=== core:model ===]                    \
[==== core:ui ====]                      }-> 25 sec
[=== core:domain ===]                   /
[== feature:home ==][== feature:profile ==]
                    [=== app ===]
```

**Formula**: Build time = graph height (longest path), not total module count.

#### 2. Incremental Compilation

```kotlin
// Changed one file in :feature:profile

// WITHOUT modularization:
// Recompiles ENTIRE app -> 60 sec

// WITH modularization:
// Recompiles only :feature:profile -> 5 sec

// WITH implementation dependencies:
// Changes don't "leak" up the graph
```

```kotlin
// BAD: All dependencies as api - cascading recompilation
dependencies {
    api(project(":core:network"))  // Change in network -> everything rebuilds
}

// GOOD: implementation isolates changes
dependencies {
    implementation(project(":core:network"))  // Change is localized
}
```

#### 3. Gradle Build Cache

```bash
# gradle.properties
org.gradle.caching=true

# For CI/CD
# settings.gradle.kts
buildCache {
    local { directory = File(rootDir, "build-cache") }
    remote<HttpBuildCache> {
        url = uri("https://cache.example.com/")
        isPush = System.getenv("CI") != null
    }
}
```

**How it works**:
```
Developer A: changed :feature:home, built project
  -> :core:common, :core:domain are cached

Developer B: changed :feature:profile
  -> :core:common, :core:domain taken from cache
  -> Only :feature:profile + :app rebuild
```

#### 4. Configuration Cache (Gradle 8+)

```bash
# gradle.properties
org.gradle.configuration-cache=true
```

Caches configuration phase result (parsing build scripts).

### Metrics and Measurement

```bash
# Profile build
./gradlew assembleDebug --profile

# Build Scan (detailed analysis)
./gradlew assembleDebug --scan

# Compare with/without cache
./gradlew clean assembleDebug  # Cold build
./gradlew assembleDebug        # Incremental build
```

### Graph Structure Impact

```
BAD GRAPH (deep):
  app -> feature -> domain -> data -> network -> common
  Height: 6 levels
  Parallelism: minimal

GOOD GRAPH (wide):
       app
      / | \
  home profile settings
     \  |  /
     domain
     /    \
  data   network
      \ /
    common
  Height: 4 levels
  Parallelism: maximum
```

### Gradle Optimizations

```kotlin
// build.gradle.kts (root)
tasks.withType<org.jetbrains.kotlin.gradle.tasks.KotlinCompile>().configureEach {
    compilerOptions {
        // Kotlin incremental compilation
        freeCompilerArgs.addAll(
            "-Xjvm-default=all",
        )
    }
}

// Avoid configuration phase work
subprojects {
    // BAD - executed at configuration
    // println("Configuring ${project.name}")

    // GOOD - executed at execution
    tasks.register("info") {
        doLast { println("Building ${project.name}") }
    }
}
```

### Strategies for Large Projects

| Strategy | Effect | Complexity |
|----------|--------|------------|
| Split monolith into modules | -40% build time | High |
| `implementation` instead of `api` | -20% incremental | Low |
| Enable build cache | -30% CI builds | Low |
| Configuration cache | -10% config time | Medium |
| Remote build cache | -50% CI cold builds | Medium |
| Gradle Enterprise | Analytics, cache | Expensive |

### Practical Example

```kotlin
// settings.gradle.kts
rootProject.name = "MyApp"

// Include all modules
include(
    ":app",
    ":feature:home",
    ":feature:profile",
    ":feature:settings",
    ":core:ui",
    ":core:domain",
    ":core:data",
    ":core:network",
    ":core:database",
    ":core:common",
    ":core:testing"
)

// gradle.properties - optimizations
/*
org.gradle.parallel=true
org.gradle.caching=true
org.gradle.configuration-cache=true
org.gradle.jvmargs=-Xmx4g -XX:+UseParallelGC
kotlin.incremental=true
kotlin.caching.enabled=true
*/
```

### Results (Real Project)

| Metric | Monolith | Modular |
|--------|----------|---------|
| Cold build | 180 sec | 120 sec |
| Incremental (1 file) | 45 sec | 8 sec |
| CI with cache | 180 sec | 60 sec |
| Module count | 1 | 15 |

### Troubleshooting

```bash
# Find slow tasks
./gradlew assembleDebug --profile
# Open build/reports/profile/profile-*.html

# Check cache
./gradlew assembleDebug --build-cache --info | grep -i cache

# Dependency analysis
./gradlew :app:dependencies --configuration runtimeClasspath
```

---

## Follow-ups

- How do you set up remote build cache for a team?
- What causes cache misses and how do you debug them?
- How does Kotlin incremental compilation work with multi-module projects?

## References

- https://developer.android.com/build/optimize-your-build
- https://docs.gradle.org/current/userguide/build_cache.html
- https://docs.gradle.org/current/userguide/configuration_cache.html

## Related Questions

### Prerequisites

- [[q-module-types--modularization--medium]] - Module types overview
- [[q-api-vs-implementation--modularization--medium]] - API vs implementation impact

### Related

- [[q-module-dependency-graph--modularization--hard]] - Graph design for performance
- [[q-gradle-basics--android--easy]] - Gradle fundamentals

### Advanced

- [[q-convention-plugins--modularization--hard]] - Build logic optimization
- [[q-ci-cd-android--android--hard]] - CI/CD with modular projects
