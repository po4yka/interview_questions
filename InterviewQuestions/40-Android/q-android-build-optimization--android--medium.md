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
status: draft
moc: moc-android
related:
  - c-gradle
  - c-modularization
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

### 1. Критичные настройки gradle.properties

```properties
# ✅ Параллельная сборка (подбирайте значение под вашу машину)
org.gradle.parallel=true
org.gradle.workers.max=8

# ✅ Build cache (кеш артефактов) и configuration cache (если плагины совместимы)
org.gradle.caching=true
org.gradle.configuration-cache=true

# ✅ File system watching
org.gradle.vfs.watch=true

# ✅ JVM heap (значение подбирается под доступную память)
org.gradle.jvmargs=-Xmx4096m -XX:MaxMetaspaceSize=512m

# ✅ Не транзитивные R-классы (уменьшает пересборку)
android.nonTransitiveRClass=true

# ✅ Инкрементальная компиляция (в новых версиях включена по умолчанию)
kotlin.incremental=true
```

**Эффект**: Потенциально до +30-70% на инкрементальных сборках и +15-30% на clean-сборках, в зависимости от проекта и окружения.

### 2. Зависимости: implementation vs api

```kotlin
dependencies {
    // ✅ implementation скрывает транзитивные зависимости
    implementation(libs.androidx.core)
    implementation(libs.retrofit)

    // ❌ api выставляет зависимости наружу → изменения приводят к пересборке потребителей
    // api(libs.retrofit)

    // ✅ KSP вместо Kapt (часто до ~2x быстрее для аннотаций)
    ksp(libs.hilt.compiler)
}
```

**Правило**: `api` использовать только если зависимость является частью публичного API модуля.

### 3. Отключение неиспользуемых функций

```kotlin
android {
    buildFeatures {
        // Отключайте только если не используете соответствующие артефакты,
        // иначе сборка или код сломаются.
        buildConfig = false
        aidl = false
        renderScript = false  // RenderScript устарел; включайте только при наличии легаси-кода
    }

    lint {
        checkReleaseBuilds = false  // ✅ Запускаем полный Lint в CI, не на локальных release-сборках
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

**Бонус**: Gradle Remote Build Cache для команды (при корректной конфигурации инфраструктуры).

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

### 1. Critical gradle.properties settings

```properties
# ✅ Parallel build (tune for your machine)
org.gradle.parallel=true
org.gradle.workers.max=8

# ✅ Build cache and configuration cache (only if plugins/tasks are compatible)
org.gradle.caching=true
org.gradle.configuration-cache=true

# ✅ File system watching
org.gradle.vfs.watch=true

# ✅ JVM heap (adjust based on available memory)
org.gradle.jvmargs=-Xmx4096m -XX:MaxMetaspaceSize=512m

# ✅ Non-transitive R classes (reduces unnecessary recompilation)
android.nonTransitiveRClass=true

# ✅ Incremental compilation (enabled by default in modern Kotlin/AGP)
kotlin.incremental=true
```

**Impact**: Potentially up to +30-70% on incremental builds and +15-30% on clean builds, depending on project and environment.

### 2. Dependencies: implementation vs api

```kotlin
dependencies {
    // ✅ implementation hides transitive dependencies from consumers
    implementation(libs.androidx.core)
    implementation(libs.retrofit)

    // ❌ api exposes dependencies → changes trigger rebuilds of consumers
    // api(libs.retrofit)

    // ✅ KSP instead of Kapt (often up to ~2x faster for annotation processing)
    ksp(libs.hilt.compiler)
}
```

**Rule**: Use `api` only if the dependency is part of the module's public API.

### 3. Disable unused features

```kotlin
android {
    buildFeatures {
        // Disable only if you are not using the generated artifacts;
        // otherwise builds or references will break.
        buildConfig = false
        aidl = false
        renderScript = false  // RenderScript is deprecated; enable only for existing legacy usage
    }

    lint {
        checkReleaseBuilds = false  // ✅ Run full Lint in CI instead of local release builds
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

**Bonus**: Gradle Remote Build Cache for team collaboration (with proper infrastructure configuration).

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

## Дополнительные вопросы (RU)

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

## Связанные вопросы (RU)

### Предпосылки (проще)
- [[q-gradle-basics--android--easy]]

### Связанные (того же уровня)



### Продвинутые (сложнее)



## Related Questions (EN)

### Prerequisites (Easier)
- [[q-gradle-basics--android--easy]]

### Related (Same Level)



### Advanced (Harder)


