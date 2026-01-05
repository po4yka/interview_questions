---
id: android-158
title: Android Build Optimization / Оптимизация сборки Android
aliases: [Android Build Optimization, Оптимизация сборки Android]
topic: android
subtopics: [build-variants, dependency-management, gradle]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-gradle, c-modularization, q-annotation-processing-android--android--medium, q-dagger-build-time-optimization--android--medium, q-optimize-memory-usage-android--android--medium]
sources: []
created: 2025-10-15
updated: 2025-11-10
tags: [android/build-variants, android/dependency-management, android/gradle, difficulty/medium, gradle, performance]
---
# Вопрос (RU)
> Как оптимизировать время сборки Android-приложения?

---

# Question (EN)
> How to optimize Android application build time?

---

## Ответ (RU)

**Стратегия**: настройка Gradle + модуляризация + управление зависимостями + профилирование.

### 1. Критичные Настройки gradle.properties

```properties
# ✅ Параллельная сборка
# Обычно Gradle сам подбирает оптимальное число воркеров.
# Явно задавайте org.gradle.workers.max только при понимании нагрузки и профилировании.
org.gradle.parallel=true
# org.gradle.workers.max=8

# ✅ Build cache (кеш артефактов)
org.gradle.caching=true

# ✅ Configuration cache — ВКЛЮЧАТЬ ПОЭТАПНО, только если плагины/таски совместимы.
# При несовместимых задачах возможны загадочные падения или некорректное поведение.
org.gradle.configuration-cache=true

# ✅ File system watching
org.gradle.vfs.watch=true

# ✅ JVM heap (значение подбирается под доступную память и результаты профилирования)
org.gradle.jvmargs=-Xmx4096m -XX:MaxMetaspaceSize=512m

# ✅ Не транзитивные R-классы (уменьшает пересборку и размер графа зависимостей)
android.nonTransitiveRClass=true

# ✅ Инкрементальная компиляция (в новых версиях включена по умолчанию)
kotlin.incremental=true
```

**Эффект**: Эти настройки могут дать заметный выигрыш (например, десятки процентов на инкрементальных сборках),
но точные цифры сильно зависят от структуры проекта, плагинов, железа и CI-инфраструктуры.

### 2. Зависимости: Implementation Vs Api

```kotlin
dependencies {
    // ✅ implementation скрывает транзитивные зависимости
    implementation(libs.androidx.core)
    implementation(libs.retrofit)

    // ❌ api выставляет зависимости наружу → изменения приводят к пересборке потребителей
    // Использовать api только при реальной необходимости экспонировать типы наружу.
    // api(libs.retrofit)

    // ✅ KSP вместо Kapt (часто ощутимо быстрее для аннотаций)
    ksp(libs.hilt.compiler)
}
```

**Правило**: `api` использовать только если зависимость является частью публичного API модуля, иначе предпочитать `implementation`.

### 3. Отключение Неиспользуемых Функций

```kotlin
android {
    buildFeatures {
        // Отключайте только те фичи, которые гарантированно не используются в модуле.
        // Например, buildConfig = false сломает доступ к BuildConfig.* в этом модуле.
        buildConfig = false
        aidl = false
        renderScript = false  // RenderScript устарел; включайте только при наличии легаси-кода
    }

    lint {
        // ✅ Полный Lint имеет смысл запускать в CI.
        // Отключение checkReleaseBuilds для локальных сборок уменьшает время сборки,
        // но убедитесь, что релизные артефакты проверяются в pipeline.
        checkReleaseBuilds = false
    }
}
```

### 4. Модуляризация

```kotlin
// settings.gradle.kts
include(":app")
include(":feature:home", ":feature:profile")
include(":core:network", ":core:database")

// ✅ Параллельная компиляция независимых модулей
// ✅ Изоляция изменений → меньше затронутых модулей при правках
```

**Бонус**: Gradle Remote Build Cache для команды (при корректной и безопасной конфигурации инфраструктуры).

### 5. Профилирование

```bash
# Build scan (облачный отчет)
./gradlew assembleDebug --scan

# Profile report (локальный HTML)
./gradlew assembleDebug --profile

# Ищем:
# - самые медленные задачи (>5% времени сборки)
# - cache misses (низкий hit rate)
# - последовательное выполнение, которое можно распараллелить
```

---

## Answer (EN)

**Strategy**: Gradle configuration + modularization + dependency management + profiling.

### 1. Critical gradle.properties Settings

```properties
# ✅ Parallel build
# Gradle usually chooses a good default for workers based on CPU cores.
# Set org.gradle.workers.max explicitly only when you understand the trade-offs and after profiling.
org.gradle.parallel=true
# org.gradle.workers.max=8

# ✅ Build cache
org.gradle.caching=true

# ✅ Configuration cache — ENABLE GRADUALLY, only when plugins/tasks are compatible.
# Incompatible tasks may cause failures or incorrect behavior.
org.gradle.configuration-cache=true

# ✅ File system watching
org.gradle.vfs.watch=true

# ✅ JVM heap (tune based on available memory and profiling)
org.gradle.jvmargs=-Xmx4096m -XX:MaxMetaspaceSize=512m

# ✅ Non-transitive R classes (reduces unnecessary recompilation and dependency graph size)
android.nonTransitiveRClass=true

# ✅ Incremental compilation (enabled by default in modern Kotlin/AGP)
kotlin.incremental=true
```

**Impact**: These settings can bring significant improvements (e.g., noticeable gains on incremental builds),
but exact percentages vary greatly with project structure, plugins, hardware, and CI setup.

### 2. Dependencies: Implementation Vs Api

```kotlin
dependencies {
    // ✅ implementation hides transitive dependencies from consumers
    implementation(libs.androidx.core)
    implementation(libs.retrofit)

    // ❌ api exposes dependencies → changes trigger rebuilds of consumers.
    // Use api only when you really need to expose those types as part of the public API.
    // api(libs.retrofit)

    // ✅ KSP instead of Kapt (often noticeably faster for annotation processing)
    ksp(libs.hilt.compiler)
}
```

**Rule**: Use `api` only if the dependency is part of the module's public API; otherwise prefer `implementation`.

### 3. Disable Unused Features

```kotlin
android {
    buildFeatures {
        // Disable only the features that are definitely unused in this module.
        // For example, buildConfig = false will break any BuildConfig.* references here.
        buildConfig = false
        aidl = false
        renderScript = false  // RenderScript is deprecated; enable only for existing legacy usage
    }

    lint {
        // ✅ Running full Lint in CI makes sense.
        // Disabling checkReleaseBuilds for local builds can speed up development,
        // but ensure release artifacts are linted in your pipeline.
        checkReleaseBuilds = false
    }
}
```

### 4. Modularization

```kotlin
// settings.gradle.kts
include(":app")
include(":feature:home", ":feature:profile")
include(":core:network", ":core:database")

// ✅ Parallel compilation of independent modules
// ✅ Change isolation → fewer modules affected per change
```

**Bonus**: Gradle Remote Build Cache for team collaboration (with correct and secure infrastructure configuration).

### 5. Profiling

```bash
# Build scan (cloud report)
./gradlew assembleDebug --scan

# Profile report (local HTML)
./gradlew assembleDebug --profile

# Look for:
# - slowest tasks (>5% of total build time)
# - cache misses (low hit rate)
# - sequential execution that can be parallelized
```

---

## Дополнительные Вопросы (RU)

- Чем Configuration Cache отличается от Build Cache?
- Каковы компромиссы использования `api` vs `implementation` в многомодульных проектах?
- Как диагностировать и улучшать cache hit rate в CI?
- Когда стоит выделять функциональность в отдельный модуль, а когда оставлять монолит?
- Как безопасно и эффективно настроить Gradle Remote Build Cache для команды?

## Follow-ups (EN)

- How does Configuration Cache differ from Build Cache?
- What are the trade-offs of using `api` vs `implementation` in multi-module projects?
- How to diagnose and improve cache hit rates in CI?
- When should you split a feature module vs keeping it monolithic?
- How to set up Gradle Remote Build Cache securely for team use?

---

## Ссылки (RU)

- [[c-gradle]]
- [[c-dependency-injection]]
- [[c-modularization]]
- https://docs.gradle.org/current/userguide/performance.html
- https://developer.android.com/studio/build/optimize-your-build

## References (EN)

- [[c-gradle]]
- [[c-dependency-injection]]
- [[c-modularization]]
- https://docs.gradle.org/current/userguide/performance.html
- https://developer.android.com/studio/build/optimize-your-build

---

## Связанные Вопросы (RU)

### Предпосылки (проще)
- [[q-gradle-basics--android--easy]]

### Связанные (того Же уровня)

### Продвинутые (сложнее)

## Related Questions (EN)

### Prerequisites (Easier)
- [[q-gradle-basics--android--easy]]

### Related (Same Level)

### Advanced (Harder)

