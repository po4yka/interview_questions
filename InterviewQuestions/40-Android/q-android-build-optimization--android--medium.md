---
id: 20251012-122763
title: Android Build Optimization / Оптимизация сборки Android
aliases: [Android Build Optimization, Оптимизация сборки Android]
topic: android
subtopics: [gradle]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-gradle-basics--android--easy, c-gradle]
sources: []
created: 2025-10-15
updated: 2025-01-27
tags: [android/gradle, difficulty/medium]
---
# Вопрос (RU)
> Как оптимизировать сборку Android-приложения?

---

# Question (EN)
> How to optimize Android application build?

---

## Ответ (RU)

**Основные направления:**

1. **Gradle-конфигурация** — параллельная сборка, кеширование, Configuration Cache
2. **Модуляризация** — параллельная компиляция независимых модулей
3. **Управление зависимостями** — version catalogs, `implementation` вместо `api`
4. **Kotlin-оптимизации** — инкрементальная компиляция, KSP вместо Kapt

**gradle.properties (критичные настройки):**

```properties
# ✅ Параллельная сборка (используем все ядра CPU)
org.gradle.parallel=true

# ✅ Build cache (избегаем перекомпиляции неизменного кода)
org.gradle.caching=true

# ✅ Configuration cache (кешируем фазу конфигурации, +10-30%)
org.gradle.configuration-cache=true

# ✅ File system watching (нативные события FS вместо polling)
org.gradle.vfs.watch=true

# ✅ JVM heap (предотвращаем OOM, улучшаем GC)
org.gradle.jvmargs=-Xmx4096m -XX:MaxMetaspaceSize=512m

# ✅ Non-transitive R classes (каждый модуль получает свой R class)
android.nonTransitiveRClass=true

# ✅ Incremental Kotlin compilation
kotlin.incremental=true
```

**Модульная структура:**

```kotlin
// settings.gradle.kts
include(":app")
include(":feature:home")
include(":core:network")

// ✅ Независимые модули компилируются параллельно
// ✅ Изменения в :core:network не пересобирают :feature:home
// ✅ Gradle кеширует отдельные модули
```

**Зависимости:**

```kotlin
dependencies {
    // ✅ implementation скрывает зависимости от потребителей
    implementation(libs.androidx.core)

    // ❌ api выставляет зависимости наружу (больше перекомпиляций)
    // api(libs.androidx.core)

    // ✅ KSP (в 2x быстрее Kapt)
    ksp(libs.hilt.compiler)

    // ❌ Kapt (legacy)
    // kapt(libs.hilt.compiler)
}
```

**Build-скрипт:**

```kotlin
android {
    buildFeatures {
        viewBinding = true
        buildConfig = false  // ✅ Отключаем неиспользуемые фичи
        aidl = false
        renderScript = false
    }

    lint {
        checkReleaseBuilds = false  // ✅ Lint только в CI, не локально
        abortOnError = false
    }

    testOptions {
        unitTests {
            isReturnDefaultValues = true  // ✅ Mock Android APIs
        }
    }
}
```

**Профилирование:**

```bash
# Build scan (детальный cloud-отчет)
./gradlew build --scan

# Profile report (локальный HTML)
./gradlew assembleDebug --profile

# Анализируем: slowest tasks, cache hit rate, parallelization
```

**Quick wins (эффект 20-80%):**

- `org.gradle.parallel=true` → +20-40%
- `org.gradle.caching=true` → +30-50% (incremental)
- `org.gradle.configuration-cache=true` → +10-30%
- Модуляризация → параллельная компиляция
- KSP вместо Kapt → в 2x быстрее
- Отключить Lint/Tests в debug → +15-25%

---

## Answer (EN)

**Key optimization areas:**

1. **Gradle configuration** — parallel builds, caching, Configuration Cache
2. **Modularization** — parallel compilation of independent modules
3. **Dependency management** — version catalogs, `implementation` over `api`
4. **Kotlin optimizations** — incremental compilation, KSP instead of Kapt

**gradle.properties (critical settings):**

```properties
# ✅ Parallel build (use all CPU cores)
org.gradle.parallel=true

# ✅ Build cache (avoid recompiling unchanged code)
org.gradle.caching=true

# ✅ Configuration cache (cache configuration phase, +10-30%)
org.gradle.configuration-cache=true

# ✅ File system watching (native FS events instead of polling)
org.gradle.vfs.watch=true

# ✅ JVM heap (prevent OOM, improve GC)
org.gradle.jvmargs=-Xmx4096m -XX:MaxMetaspaceSize=512m

# ✅ Non-transitive R classes (each module gets its own R class)
android.nonTransitiveRClass=true

# ✅ Incremental Kotlin compilation
kotlin.incremental=true
```

**Module structure:**

```kotlin
// settings.gradle.kts
include(":app")
include(":feature:home")
include(":core:network")

// ✅ Independent modules compile in parallel
// ✅ Changes in :core:network don't rebuild :feature:home
// ✅ Gradle caches individual modules
```

**Dependencies:**

```kotlin
dependencies {
    // ✅ implementation hides dependencies from consumers
    implementation(libs.androidx.core)

    // ❌ api exposes dependencies (more recompilations)
    // api(libs.androidx.core)

    // ✅ KSP (2x faster than Kapt)
    ksp(libs.hilt.compiler)

    // ❌ Kapt (legacy)
    // kapt(libs.hilt.compiler)
}
```

**Build script:**

```kotlin
android {
    buildFeatures {
        viewBinding = true
        buildConfig = false  // ✅ Disable unused features
        aidl = false
        renderScript = false
    }

    lint {
        checkReleaseBuilds = false  // ✅ Lint only in CI, not locally
        abortOnError = false
    }

    testOptions {
        unitTests {
            isReturnDefaultValues = true  // ✅ Mock Android APIs
        }
    }
}
```

**Profiling:**

```bash
# Build scan (detailed cloud report)
./gradlew build --scan

# Profile report (local HTML)
./gradlew assembleDebug --profile

# Analyze: slowest tasks, cache hit rate, parallelization
```

**Quick wins (20-80% improvement):**

- `org.gradle.parallel=true` → +20-40%
- `org.gradle.caching=true` → +30-50% (incremental)
- `org.gradle.configuration-cache=true` → +10-30%
- Modularization → parallel compilation
- KSP instead of Kapt → 2x faster
- Disable Lint/Tests in debug → +15-25%

---

## Follow-ups

- How to identify which Gradle tasks cause bottlenecks using `--profile` and `--scan`?
- What are trade-offs between Configuration Cache and Build Cache in CI environments?
- How does `implementation` vs `api` affect incremental compilation boundaries?
- When should you split a module further vs keep it monolithic?
- How to configure remote build cache for team collaboration without conflicts?

## References

- [[c-gradle]] - Build system fundamentals
- https://docs.gradle.org/current/userguide/performance.html
- https://developer.android.com/studio/build/optimize-your-build

## Related Questions

### Prerequisites (Easier)
- [[q-gradle-basics--android--easy]] - Gradle fundamentals

### Related (Same Level)
- Android modularization patterns
- Version catalog best practices
- Annotation processing alternatives (KSP vs Kapt)

### Advanced (Harder)
- Custom Gradle plugins for build optimization
- Advanced caching strategies for monorepos
- Bazel migration for large projects