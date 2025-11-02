---
id: android-043
title: Gradle Build Optimization / Оптимизация сборки Gradle
aliases: ["Gradle Build Optimization", "Оптимизация сборки Gradle"]
topic: android
subtopics: [gradle, build-variants, dependency-management]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related:
  - q-android-build-optimization--android--medium
  - q-android-modularization--android--medium
  - q-baseline-profiles-optimization--android--medium
sources: []
created: 2025-10-11
updated: 2025-10-29
tags: [android/gradle, android/build-variants, android/dependency-management, gradle, build-performance, difficulty/medium]
date created: Thursday, October 30th 2025, 11:11:42 am
date modified: Thursday, October 30th 2025, 12:43:28 pm
---

# Вопрос (RU)
> Как оптимизировать сборку Gradle в Android?

# Question (EN)
> How to optimize Gradle build in Android?

---

## Ответ (RU)

### Ключевые стратегии

**1. Configuration Cache** — крупнейший выигрыш для чистых сборок
- Кэширует фазу конфигурации; последующие сборки пропускают переконфигурацию
- Требования: отсутствие побочных эффектов во время конфигурации, использование Provider API

```kotlin
// ❌ Чтение переменных окружения напрямую во время конфигурации
val apiKey = System.getenv("API_KEY")

// ✅ Отложенное чтение через Provider API
val apiKey = providers.environmentVariable("API_KEY")
android {
  defaultConfig {
    buildConfigField("String", "API_KEY", apiKey.map { "\"$it\"" })
  }
}
```

**2. Build Cache (локальный + удаленный)**
- Переиспользование выходов задач между сборками и машинами
- Критично для CI: задачи должны быть cacheable (объявленные входы/выходы, детерминированные результаты)

```kotlin
// settings.gradle.kts
buildCache {
  local { isEnabled = true }
  remote<HttpBuildCache> {
    url = uri("https://build-cache.company.com")
    isPush = System.getenv("CI") == "true"
  }
}
```

**3. KSP вместо KAPT**
- KSP избегает генерации Java-стабов; обычно в 2× быстрее
- Поддерживается: Room, Hilt, Moshi

```kotlin
// ❌ Медленный KAPT
plugins { kotlin("kapt") }
dependencies { kapt(libs.room.compiler) }

// ✅ Быстрый KSP
plugins { id("com.google.devtools.ksp") }
dependencies { ksp(libs.room.compiler) }
```

**4. Модуляризация**
- Разделение на модули уменьшает поверхность пересборки
- Используйте `api` vs `implementation` осознанно — `implementation` скрывает зависимости от downstream-модулей

**5. Version Catalogs**
- Централизация версий ускоряет sync
- Избегайте динамических версий (`+`) — они делают кэш бесполезным

```toml
# libs.versions.toml
[versions]
kotlin = "<version>"
compose = "<version>"

[libraries]
compose-ui = { module = "androidx.compose.ui:ui", version.ref = "compose" }
```

### Профилирование

Используйте build scans для измерения:
```bash
./gradlew assembleDebug --scan --configuration-cache --build-cache
```

Анализируйте: timeline задач, cache hit rates, время конфигурации, разрешение зависимостей.

## Answer (EN)

### Key Strategies

**1. Configuration Cache** — largest single win for clean builds
- Caches the configuration phase; subsequent builds skip reconfiguration
- Requirements: no side effects during configuration, use Provider API for lazy evaluation

```kotlin
// ❌ Reading env directly during configuration
val apiKey = System.getenv("API_KEY")

// ✅ Deferred reading via Provider API
val apiKey = providers.environmentVariable("API_KEY")
android {
  defaultConfig {
    buildConfigField("String", "API_KEY", apiKey.map { "\"$it\"" })
  }
}
```

**2. Build Cache (local + remote)**
- Reuses task outputs across builds and machines
- Critical for CI: tasks must be cacheable (declared inputs/outputs, deterministic results)

```kotlin
// settings.gradle.kts
buildCache {
  local { isEnabled = true }
  remote<HttpBuildCache> {
    url = uri("https://build-cache.company.com")
    isPush = System.getenv("CI") == "true"
  }
}
```

**3. KSP instead of KAPT**
- KSP avoids Java stub generation; typically 2× faster
- Supported by: Room, Hilt, Moshi

```kotlin
// ❌ Slow KAPT
plugins { kotlin("kapt") }
dependencies { kapt(libs.room.compiler) }

// ✅ Fast KSP
plugins { id("com.google.devtools.ksp") }
dependencies { ksp(libs.room.compiler) }
```

**4. Modularization**
- Breaking into modules reduces rebuild surface
- Use `api` vs `implementation` intentionally — `implementation` hides dependencies from downstream modules

```kotlin
// ❌ Exposes internal dependencies
dependencies { api(libs.retrofit) }

// ✅ Hides implementation details
dependencies { implementation(libs.retrofit) }
```

**5. Version Catalogs**
- Centralized version management speeds up sync
- Avoid dynamic versions (`+`) — they invalidate caches

```toml
# libs.versions.toml
[versions]
kotlin = "<version>"
compose = "<version>"

[libraries]
compose-ui = { module = "androidx.compose.ui:ui", version.ref = "compose" }
```

### Profiling & Measurement

Use build scans to identify bottlenecks:
```bash
./gradlew assembleDebug --scan --configuration-cache --build-cache
```

Analyze: task timeline, cache hit rates, configuration time, dependency resolution.

### CI/CD Optimization

```yaml
# GitHub Actions example
- uses: gradle/gradle-build-action@v2
  with:
    cache-read-only: false  # ✅ Enable cache writes

- run: |
    ./gradlew assembleRelease \
      --configuration-cache \
      --build-cache \
      --parallel \
      --no-daemon  # ✅ CI doesn't benefit from daemon
```

### Common Pitfalls

- Dynamic versions (`1.+`) invalidate caches
- Configuration-time I/O breaks configuration cache
- Too many small modules increase overhead
- Not declaring task inputs/outputs properly
- Absolute paths in task arguments

---

## Follow-ups

- How do you make a custom Gradle task cacheable with proper input/output declarations?
- What breaks configuration cache compatibility and how do you debug it?
- How do you migrate from KAPT to KSP for Room and Hilt processors?
- What's the difference between local and remote build cache, and when to use each?
- How do you measure the ROI of modularization on build performance?

## References

**Official Documentation**:
- [Gradle Configuration Cache](https://docs.gradle.org/current/userguide/configuration_cache.html)
- [Gradle Build Cache](https://docs.gradle.org/current/userguide/build_cache.html)
- [Gradle Performance Optimization](https://docs.gradle.org/current/userguide/performance.html)
- [Android Build Best Practices](https://developer.android.com/build/optimize-your-build)

**Related Concepts**:
- [[c-gradle-build-cache]]
- [[c-ksp-vs-kapt]]
- [[c-android-modularization]]

## Related Questions

### Prerequisites (Easier)
- [[q-android-build-optimization--android--medium]] — General Android build optimization strategies
- [[q-gradle-basics--tools--easy]] — Gradle fundamentals and build lifecycle

### Related (Same Level)
- [[q-android-modularization--android--medium]] — Module structure for better build performance
- [[q-baseline-profiles-optimization--android--medium]] — Runtime and build-time optimization
- [[q-dependency-management-gradle--android--medium]] — Managing dependencies efficiently

### Advanced (Harder)
- [[q-cicd-pipeline-android--android--medium]] — CI/CD setup with build caching
- [[q-custom-gradle-plugin--tools--hard]] — Creating cacheable custom Gradle tasks
- [[q-build-reproducibility--tools--hard]] — Ensuring deterministic builds

