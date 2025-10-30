---
id: 20251012-122763
title: Android Build Optimization / Оптимизация сборки Android
aliases: ["Android Build Optimization", "Оптимизация сборки Android"]
topic: android
subtopics: [gradle, build-variants, dependency-management]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-gradle-basics--android--easy, c-gradle, q-android-modularization--android--hard]
sources: []
created: 2025-10-15
updated: 2025-10-29
tags: [android/gradle, android/build-variants, android/dependency-management, gradle, performance, difficulty/medium]
---
# Вопрос (RU)
> Как оптимизировать сборку Android-приложения?

---

# Question (EN)
> How to optimize Android application build?

---

## Ответ (RU)

**Стратегия оптимизации:**

1. **Gradle Configuration** — параллелизм, кеширование, Configuration Cache
2. **Модуляризация** — независимые модули компилируются параллельно
3. **Управление зависимостями** — `implementation` vs `api`, KSP вместо Kapt
4. **Профилирование** — выявление узких мест через `--scan`/`--profile`

### 1. Критичные настройки gradle.properties

```properties
# ✅ Параллельная сборка (все ядра CPU)
org.gradle.parallel=true
org.gradle.workers.max=8

# ✅ Build cache (избегаем перекомпиляции)
org.gradle.caching=true

# ✅ Configuration cache (кеш фазы конфигурации)
org.gradle.configuration-cache=true

# ✅ File system watching (native FS events)
org.gradle.vfs.watch=true

# ✅ JVM heap (профилактика OOM)
org.gradle.jvmargs=-Xmx4096m -XX:MaxMetaspaceSize=512m

# ✅ Non-transitive R classes (изолированные R.java)
android.nonTransitiveRClass=true

# ✅ Incremental Kotlin compilation
kotlin.incremental=true
kotlin.incremental.usePreciseJavaTracking=true
```

**Эффект:** +30-70% на incremental builds, +15-30% на clean builds.

### 2. Зависимости: implementation vs api

```kotlin
dependencies {
    // ✅ implementation скрывает транзитивные зависимости
    implementation(libs.androidx.core)
    implementation(libs.retrofit)

    // ❌ api выставляет зависимости наружу
    // Изменения в api-зависимости пересобирают всех потребителей
    // api(libs.retrofit)

    // ✅ KSP (2x быстрее Kapt)
    ksp(libs.hilt.compiler)
}
```

**Правило:** используйте `api` только если зависимость явно экспортируется в публичном API модуля.

### 3. Отключение неиспользуемых функций

```kotlin
android {
    buildFeatures {
        viewBinding = true
        buildConfig = false  // ✅ Генерируем только если используем
        aidl = false
        renderScript = false
    }

    lint {
        checkReleaseBuilds = false  // ✅ Lint в CI, не локально
    }
}
```

### 4. Модуляризация

```kotlin
// settings.gradle.kts
include(":app")
include(":feature:home", ":feature:profile")
include(":core:network", ":core:database")

// ✅ Независимые модули компилируются параллельно
// ✅ Изменения в :core:network не пересобирают :feature:home
```

**Бонус:** возможность использовать Gradle Remote Build Cache для команды.

### 5. Профилирование

```bash
# Build scan (облачный отчет с визуализацией)
./gradlew assembleDebug --scan

# Profile report (локальный HTML)
./gradlew assembleDebug --profile

# Ищем:
# - Slowest tasks (>5% build time)
# - Cache misses (низкий cache hit rate)
# - Sequential execution (возможность параллелизации)
```

---

## Answer (EN)

**Optimization strategy:**

1. **Gradle Configuration** — parallelism, caching, Configuration Cache
2. **Modularization** — independent modules compile in parallel
3. **Dependency management** — `implementation` vs `api`, KSP instead of Kapt
4. **Profiling** — identify bottlenecks via `--scan`/`--profile`

### 1. Critical gradle.properties settings

```properties
# ✅ Parallel build (all CPU cores)
org.gradle.parallel=true
org.gradle.workers.max=8

# ✅ Build cache (avoid recompilation)
org.gradle.caching=true

# ✅ Configuration cache (cache configuration phase)
org.gradle.configuration-cache=true

# ✅ File system watching (native FS events)
org.gradle.vfs.watch=true

# ✅ JVM heap (prevent OOM)
org.gradle.jvmargs=-Xmx4096m -XX:MaxMetaspaceSize=512m

# ✅ Non-transitive R classes (isolated R.java)
android.nonTransitiveRClass=true

# ✅ Incremental Kotlin compilation
kotlin.incremental=true
kotlin.incremental.usePreciseJavaTracking=true
```

**Impact:** +30-70% on incremental builds, +15-30% on clean builds.

### 2. Dependencies: implementation vs api

```kotlin
dependencies {
    // ✅ implementation hides transitive dependencies
    implementation(libs.androidx.core)
    implementation(libs.retrofit)

    // ❌ api exposes dependencies outward
    // Changes in api dependency rebuild all consumers
    // api(libs.retrofit)

    // ✅ KSP (2x faster than Kapt)
    ksp(libs.hilt.compiler)
}
```

**Rule:** use `api` only if dependency is explicitly exported in module's public API.

### 3. Disable unused features

```kotlin
android {
    buildFeatures {
        viewBinding = true
        buildConfig = false  // ✅ Generate only if used
        aidl = false
        renderScript = false
    }

    lint {
        checkReleaseBuilds = false  // ✅ Lint in CI, not locally
    }
}
```

### 4. Modularization

```kotlin
// settings.gradle.kts
include(":app")
include(":feature:home", ":feature:profile")
include(":core:network", ":core:database")

// ✅ Independent modules compile in parallel
// ✅ Changes in :core:network don't rebuild :feature:home
```

**Bonus:** enables Gradle Remote Build Cache for team collaboration.

### 5. Profiling

```bash
# Build scan (cloud report with visualization)
./gradlew assembleDebug --scan

# Profile report (local HTML)
./gradlew assembleDebug --profile

# Look for:
# - Slowest tasks (>5% build time)
# - Cache misses (low cache hit rate)
# - Sequential execution (parallelization opportunities)
```

---

## Follow-ups

- How does Configuration Cache differ from Build Cache and when to use each?
- What are trade-offs of using `api` vs `implementation` in multi-module projects?
- How to diagnose cache misses and improve cache hit rate in CI?
- When should you split a feature module vs keeping it monolithic?
- How to set up Remote Build Cache for team without security risks?

## References

- [[c-gradle]]
- [[c-build-configuration]]
- https://docs.gradle.org/current/userguide/performance.html
- https://developer.android.com/studio/build/optimize-your-build

## Related Questions

### Prerequisites (Easier)
- [[q-gradle-basics--android--easy]]

### Related (Same Level)
- [[q-android-modularization--android--hard]]
- [[q-gradle-version-catalogs--android--medium]]

### Advanced (Harder)
- [[q-custom-gradle-plugins--android--hard]]
- [[q-remote-build-cache-setup--android--hard]]