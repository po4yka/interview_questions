---
id: android-158
title: Android Build Optimization / Оптимизация сборки Android
aliases: [Android Build Optimization, Оптимизация сборки Android]
topic: android
subtopics:
  - build-variants
  - dependency-management
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
sources: []
created: 2025-10-15
updated: 2025-10-30
tags: [android/build-variants, android/dependency-management, android/gradle, difficulty/medium, gradle, performance]
date created: Thursday, October 30th 2025, 11:26:48 am
date modified: Sunday, November 2nd 2025, 12:45:30 pm
---

# Вопрос (RU)
> Как оптимизировать время сборки Android-приложения?

---

# Question (EN)
> How to optimize Android application build time?

---

## Ответ (RU)

**Стратегия**: Gradle-конфигурация + модуляризация + управление зависимостями + профилирование.

### 1. Критичные Настройки gradle.properties

```properties
# ✅ Параллельная сборка
org.gradle.parallel=true
org.gradle.workers.max=8

# ✅ Build cache (кеш артефактов)
org.gradle.caching=true
org.gradle.configuration-cache=true

# ✅ File system watching
org.gradle.vfs.watch=true

# ✅ JVM heap
org.gradle.jvmargs=-Xmx4096m -XX:MaxMetaspaceSize=512m

# ✅ Non-transitive R classes
android.nonTransitiveRClass=true

# ✅ Incremental compilation
kotlin.incremental=true
```

**Эффект**: +30-70% на инкрементальных сборках, +15-30% на clean builds.

### 2. Зависимости: Implementation Vs Api

```kotlin
dependencies {
    // ✅ implementation скрывает транзитивные зависимости
    implementation(libs.androidx.core)
    implementation(libs.retrofit)

    // ❌ api выставляет наружу → пересборка потребителей
    // api(libs.retrofit)

    // ✅ KSP вместо Kapt (2x быстрее)
    ksp(libs.hilt.compiler)
}
```

**Правило**: `api` только если зависимость в публичном API модуля.

### 3. Отключение Неиспользуемых Функций

```kotlin
android {
    buildFeatures {
        buildConfig = false  // ✅ Только при использовании
        aidl = false
        renderScript = false
    }

    lint {
        checkReleaseBuilds = false  // ✅ Lint в CI
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
// ✅ Изоляция изменений
```

**Бонус**: Gradle Remote Build Cache для команды.

### 5. Профилирование

```bash
# Build scan (облачный отчет)
./gradlew assembleDebug --scan

# Profile report (локальный HTML)
./gradlew assembleDebug --profile

# Ищем:
# - Slowest tasks (>5% build time)
# - Cache misses (низкий hit rate)
# - Sequential execution
```

---

## Answer (EN)

**Strategy**: Gradle configuration + modularization + dependency management + profiling.

### 1. Critical gradle.properties Settings

```properties
# ✅ Parallel build
org.gradle.parallel=true
org.gradle.workers.max=8

# ✅ Build cache
org.gradle.caching=true
org.gradle.configuration-cache=true

# ✅ File system watching
org.gradle.vfs.watch=true

# ✅ JVM heap
org.gradle.jvmargs=-Xmx4096m -XX:MaxMetaspaceSize=512m

# ✅ Non-transitive R classes
android.nonTransitiveRClass=true

# ✅ Incremental compilation
kotlin.incremental=true
```

**Impact**: +30-70% on incremental builds, +15-30% on clean builds.

### 2. Dependencies: Implementation Vs Api

```kotlin
dependencies {
    // ✅ implementation hides transitive dependencies
    implementation(libs.androidx.core)
    implementation(libs.retrofit)

    // ❌ api exposes dependencies → rebuilds consumers
    // api(libs.retrofit)

    // ✅ KSP instead of Kapt (2x faster)
    ksp(libs.hilt.compiler)
}
```

**Rule**: Use `api` only if dependency is in module's public API.

### 3. Disable Unused Features

```kotlin
android {
    buildFeatures {
        buildConfig = false  // ✅ Generate only if used
        aidl = false
        renderScript = false
    }

    lint {
        checkReleaseBuilds = false  // ✅ Lint in CI
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
// ✅ Change isolation
```

**Bonus**: Gradle Remote Build Cache for team collaboration.

### 5. Profiling

```bash
# Build scan (cloud report)
./gradlew assembleDebug --scan

# Profile report (local HTML)
./gradlew assembleDebug --profile

# Look for:
# - Slowest tasks (>5% build time)
# - Cache misses (low hit rate)
# - Sequential execution
```

---

## Follow-ups

- How does Configuration Cache differ from Build Cache?
- What are the trade-offs of using api vs implementation in multi-module projects?
- How to diagnose and improve cache hit rates in CI?
- When should you split a feature module vs keeping it monolithic?
- How to set up Gradle Remote Build Cache securely for team use?

## References

- [[c-gradle]]
- [[c-dependency-injection]]
- [[c-modularization]]
- https://docs.gradle.org/current/userguide/performance.html
- https://developer.android.com/studio/build/optimize-your-build

## Related Questions

### Prerequisites (Easier)
- [[q-gradle-basics--android--easy]]

### Related (Same Level)



### Advanced (Harder)


