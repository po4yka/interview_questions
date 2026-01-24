---
id: android-cicd-002
title: "Gradle Build Cache and Configuration Cache / Gradle Build Cache и Configuration Cache"
aliases: ["Gradle Build Cache", "Gradle Build Cache и Configuration Cache"]
topic: android
subtopics: [cicd, build-optimization, gradle]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-github-actions-android--cicd--medium, q-build-variants-flavors--cicd--medium]
created: 2026-01-23
updated: 2026-01-23
sources: ["https://docs.gradle.org/current/userguide/build_cache.html", "https://docs.gradle.org/current/userguide/configuration_cache.html"]
tags: [android/cicd, android/build-optimization, difficulty/medium, gradle, build-cache]

---
# Вопрос (RU)

> Что такое Gradle Build Cache и Configuration Cache? Как они ускоряют сборку Android-проектов?

# Question (EN)

> What are Gradle Build Cache and Configuration Cache? How do they speed up Android project builds?

## Ответ (RU)

Gradle предлагает два механизма кеширования для значительного ускорения сборок: **Build Cache** (кеш результатов задач) и **Configuration Cache** (кеш фазы конфигурации). Оба механизма дополняют друг друга и могут сократить время сборки на 40-90%.

### Build Cache

Build Cache сохраняет выходные данные задач (task outputs) и повторно использует их, когда входные данные не изменились.

#### Включение Build Cache

```properties
# gradle.properties
org.gradle.caching=true
```

Или через командную строку:

```bash
./gradlew assembleDebug --build-cache
```

#### Как Работает

```
Task Inputs (исходники, зависимости, конфигурация)
           |
           v
    +------+------+
    | Build Cache |
    +------+------+
           |
    Cache Hit?
     /         \
   Да           Нет
    |             |
    v             v
Использовать  Выполнить
 кеш          задачу
                  |
                  v
            Сохранить
            в кеш
```

#### Типы Build Cache

**Локальный кеш** (по умолчанию):

```properties
# gradle.properties
org.gradle.caching=true
# Локальный кеш в ~/.gradle/caches/build-cache-1/
```

**Удалённый кеш** (для команды):

```kotlin
// settings.gradle.kts
buildCache {
    local {
        isEnabled = true
        directory = file("${rootDir}/.gradle/build-cache")
    }

    remote<HttpBuildCache> {
        url = uri("https://cache.example.com/cache/")
        isPush = System.getenv("CI") == "true"  // Только CI пишет в кеш
        credentials {
            username = System.getenv("CACHE_USER") ?: ""
            password = System.getenv("CACHE_PASSWORD") ?: ""
        }
    }
}
```

#### Gradle Enterprise / Develocity

```kotlin
// settings.gradle.kts
plugins {
    id("com.gradle.develocity") version "3.17"
}

develocity {
    buildCache {
        remote(develocity.buildCache) {
            isEnabled = true
            isPush = System.getenv("CI") == "true"
        }
    }
}
```

#### Кешируемые Задачи

Не все задачи кешируемы. Задача кешируема, если:
- Все входы определены и детерминированы
- Все выходы определены
- Задача помечена как `@CacheableTask`

```kotlin
// Пример custom cacheable task
@CacheableTask
abstract class GenerateResourcesTask : DefaultTask() {
    @get:InputFile
    @get:PathSensitive(PathSensitivity.RELATIVE)
    abstract val inputFile: RegularFileProperty

    @get:OutputDirectory
    abstract val outputDir: DirectoryProperty

    @TaskAction
    fun generate() {
        // ...
    }
}
```

### Configuration Cache

Configuration Cache сохраняет результат фазы конфигурации (parsing build scripts, создание task graph) и пропускает её при повторных сборках.

#### Включение Configuration Cache

```properties
# gradle.properties
org.gradle.configuration-cache=true
org.gradle.configuration-cache.max-problems=5
```

#### Преимущества

| Без Configuration Cache | С Configuration Cache |
|------------------------|----------------------|
| Parsing build.gradle.kts при каждой сборке | Parsing только при изменении |
| Создание task graph каждый раз | Task graph из кеша |
| 5-15 секунд на конфигурацию | < 1 секунды |

#### Ограничения

Не все плагины совместимы. Проверяй логи:

```bash
./gradlew assembleDebug --configuration-cache
```

Несовместимые паттерны:

```kotlin
// НЕПРАВИЛЬНО: чтение файлов во время конфигурации
val version = file("version.txt").readText()

// ПРАВИЛЬНО: использовать providers
val version = providers.fileContents(
    layout.projectDirectory.file("version.txt")
).asText

// НЕПРАВИЛЬНО: доступ к Task во время конфигурации
tasks.named("assemble").get().doLast { }

// ПРАВИЛЬНО: lazy конфигурация
tasks.named("assemble") {
    doLast { }
}
```

### Параллельное Выполнение

```properties
# gradle.properties
org.gradle.parallel=true
org.gradle.workers.max=4
```

### Полная Конфигурация для Оптимизации

```properties
# gradle.properties

# Build Cache
org.gradle.caching=true

# Configuration Cache
org.gradle.configuration-cache=true
org.gradle.configuration-cache.max-problems=5

# Параллельность
org.gradle.parallel=true
org.gradle.workers.max=4

# Память
org.gradle.jvmargs=-Xmx4g -XX:+HeapDumpOnOutOfMemoryError

# Kotlin
kotlin.incremental=true
kotlin.incremental.useClasspathSnapshot=true

# Android
android.enableBuildCache=true
android.useAndroidX=true
android.enableR8.fullMode=true
```

### Отладка Build Cache

```bash
# Проверить причины cache miss
./gradlew assembleDebug --build-cache -Dorg.gradle.caching.debug=true

# Сканирование сборки
./gradlew assembleDebug --scan
```

### Сохранение Кеша в CI

#### GitHub Actions

```yaml
- name: Setup Gradle
  uses: gradle/actions/setup-gradle@v4
  with:
    cache-read-only: ${{ github.ref != 'refs/heads/main' }}
```

#### Ручное Кеширование

```yaml
- name: Cache Gradle
  uses: actions/cache@v4
  with:
    path: |
      ~/.gradle/caches
      ~/.gradle/wrapper
      .gradle/configuration-cache
    key: gradle-${{ runner.os }}-${{ hashFiles('**/*.gradle*', '**/gradle-wrapper.properties') }}
    restore-keys: |
      gradle-${{ runner.os }}-
```

### Сравнение Механизмов

| Аспект | Build Cache | Configuration Cache |
|--------|-------------|---------------------|
| Что кеширует | Выходы задач | Фазу конфигурации |
| Когда помогает | Инкрементальные сборки | Любая сборка |
| Удалённый кеш | Да | Нет (локальный) |
| Совместимость | Высокая | Требует адаптации |
| Выигрыш | 20-60% | 5-15 секунд |

### Резюме

- **Build Cache** кеширует результаты задач, ускорение до 60%
- **Configuration Cache** кеширует parsing скриптов, экономит 5-15s
- **Удалённый кеш** делит результаты между разработчиками и CI
- **Комбинирование** обоих даст максимальное ускорение
- **Отладка** через `--scan` и `-Dorg.gradle.caching.debug=true`

## Answer (EN)

Gradle offers two caching mechanisms for significantly faster builds: **Build Cache** (task output caching) and **Configuration Cache** (configuration phase caching). Both complement each other and can reduce build times by 40-90%.

### Build Cache

Build Cache stores task outputs and reuses them when inputs haven't changed.

#### Enabling Build Cache

```properties
# gradle.properties
org.gradle.caching=true
```

Or via command line:

```bash
./gradlew assembleDebug --build-cache
```

#### How It Works

```
Task Inputs (sources, dependencies, configuration)
           |
           v
    +------+------+
    | Build Cache |
    +------+------+
           |
    Cache Hit?
     /         \
   Yes          No
    |             |
    v             v
  Use          Execute
  cache         task
                  |
                  v
              Store in
               cache
```

#### Build Cache Types

**Local cache** (default):

```properties
# gradle.properties
org.gradle.caching=true
# Local cache in ~/.gradle/caches/build-cache-1/
```

**Remote cache** (for teams):

```kotlin
// settings.gradle.kts
buildCache {
    local {
        isEnabled = true
        directory = file("${rootDir}/.gradle/build-cache")
    }

    remote<HttpBuildCache> {
        url = uri("https://cache.example.com/cache/")
        isPush = System.getenv("CI") == "true"  // Only CI writes to cache
        credentials {
            username = System.getenv("CACHE_USER") ?: ""
            password = System.getenv("CACHE_PASSWORD") ?: ""
        }
    }
}
```

#### Gradle Enterprise / Develocity

```kotlin
// settings.gradle.kts
plugins {
    id("com.gradle.develocity") version "3.17"
}

develocity {
    buildCache {
        remote(develocity.buildCache) {
            isEnabled = true
            isPush = System.getenv("CI") == "true"
        }
    }
}
```

#### Cacheable Tasks

Not all tasks are cacheable. A task is cacheable when:
- All inputs are defined and deterministic
- All outputs are defined
- Task is annotated with `@CacheableTask`

```kotlin
// Custom cacheable task example
@CacheableTask
abstract class GenerateResourcesTask : DefaultTask() {
    @get:InputFile
    @get:PathSensitive(PathSensitivity.RELATIVE)
    abstract val inputFile: RegularFileProperty

    @get:OutputDirectory
    abstract val outputDir: DirectoryProperty

    @TaskAction
    fun generate() {
        // ...
    }
}
```

### Configuration Cache

Configuration Cache stores the result of the configuration phase (parsing build scripts, creating task graph) and skips it on subsequent builds.

#### Enabling Configuration Cache

```properties
# gradle.properties
org.gradle.configuration-cache=true
org.gradle.configuration-cache.max-problems=5
```

#### Benefits

| Without Configuration Cache | With Configuration Cache |
|----------------------------|-------------------------|
| Parse build.gradle.kts every build | Parse only on changes |
| Create task graph every time | Task graph from cache |
| 5-15 seconds for configuration | < 1 second |

#### Limitations

Not all plugins are compatible. Check logs:

```bash
./gradlew assembleDebug --configuration-cache
```

Incompatible patterns:

```kotlin
// WRONG: reading files during configuration
val version = file("version.txt").readText()

// CORRECT: use providers
val version = providers.fileContents(
    layout.projectDirectory.file("version.txt")
).asText

// WRONG: accessing Task during configuration
tasks.named("assemble").get().doLast { }

// CORRECT: lazy configuration
tasks.named("assemble") {
    doLast { }
}
```

### Parallel Execution

```properties
# gradle.properties
org.gradle.parallel=true
org.gradle.workers.max=4
```

### Full Optimization Configuration

```properties
# gradle.properties

# Build Cache
org.gradle.caching=true

# Configuration Cache
org.gradle.configuration-cache=true
org.gradle.configuration-cache.max-problems=5

# Parallelism
org.gradle.parallel=true
org.gradle.workers.max=4

# Memory
org.gradle.jvmargs=-Xmx4g -XX:+HeapDumpOnOutOfMemoryError

# Kotlin
kotlin.incremental=true
kotlin.incremental.useClasspathSnapshot=true

# Android
android.enableBuildCache=true
android.useAndroidX=true
android.enableR8.fullMode=true
```

### Debugging Build Cache

```bash
# Check cache miss reasons
./gradlew assembleDebug --build-cache -Dorg.gradle.caching.debug=true

# Build scan
./gradlew assembleDebug --scan
```

### Preserving Cache in CI

#### GitHub Actions

```yaml
- name: Setup Gradle
  uses: gradle/actions/setup-gradle@v4
  with:
    cache-read-only: ${{ github.ref != 'refs/heads/main' }}
```

#### Manual Caching

```yaml
- name: Cache Gradle
  uses: actions/cache@v4
  with:
    path: |
      ~/.gradle/caches
      ~/.gradle/wrapper
      .gradle/configuration-cache
    key: gradle-${{ runner.os }}-${{ hashFiles('**/*.gradle*', '**/gradle-wrapper.properties') }}
    restore-keys: |
      gradle-${{ runner.os }}-
```

### Comparison

| Aspect | Build Cache | Configuration Cache |
|--------|-------------|---------------------|
| What it caches | Task outputs | Configuration phase |
| When it helps | Incremental builds | Any build |
| Remote cache | Yes | No (local only) |
| Compatibility | High | Requires adaptation |
| Speedup | 20-60% | 5-15 seconds |

### Summary

- **Build Cache** caches task outputs, up to 60% speedup
- **Configuration Cache** caches script parsing, saves 5-15s
- **Remote cache** shares results between developers and CI
- **Combining** both gives maximum speedup
- **Debug** via `--scan` and `-Dorg.gradle.caching.debug=true`

## Дополнительные Вопросы (RU)

1. Как устранять неполадки cache miss в многомодульном проекте?
2. Какие соображения безопасности для удалённых build cache?
3. Как мигрировать существующие плагины для поддержки Configuration Cache?
4. В чём разница между Gradle Build Cache и Android Build Cache?

## Follow-ups

1. How do you troubleshoot cache misses in a multi-module project?
2. What are the security considerations for remote build caches?
3. How do you migrate existing plugins to support Configuration Cache?
4. What's the difference between Gradle Build Cache and Android Build Cache?

## Ссылки (RU)

- [Gradle Build Cache](https://docs.gradle.org/current/userguide/build_cache.html)
- [Gradle Configuration Cache](https://docs.gradle.org/current/userguide/configuration_cache.html)
- [Оптимизация сборки Android](https://developer.android.com/build/optimize-your-build)

## References

- [Gradle Build Cache](https://docs.gradle.org/current/userguide/build_cache.html)
- [Gradle Configuration Cache](https://docs.gradle.org/current/userguide/configuration_cache.html)
- [Android Build Performance](https://developer.android.com/build/optimize-your-build)
- [Develocity Build Cache](https://docs.gradle.com/enterprise/build-cache/)

## Связанные Вопросы (RU)

### Предпосылки
- [[q-build-variants-flavors--cicd--medium]] — Понимание вариантов сборки

### Похожие
- [[q-github-actions-android--cicd--medium]] — Настройка GitHub Actions
- [[q-signing-in-ci--cicd--hard]] — Безопасное подписание

### Продвинутое
- [[q-play-store-deployment--cicd--medium]] — Публикация в Play Store

## Related Questions

### Prerequisites
- [[q-build-variants-flavors--cicd--medium]] - Understanding build variants

### Related
- [[q-github-actions-android--cicd--medium]] - GitHub Actions setup
- [[q-signing-in-ci--cicd--hard]] - Secure signing

### Advanced
- [[q-play-store-deployment--cicd--medium]] - Play Store deployment
