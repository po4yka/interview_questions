---
id: android-043
title: Gradle Build Optimization / Оптимизация сборки Gradle
aliases:
- Gradle Build Optimization
- Оптимизация сборки Gradle
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
- c-app-bundle
- q-android-build-optimization--android--medium
sources: []
created: 2025-10-11
updated: 2025-11-10
tags:
- android/build-variants
- android/dependency-management
- android/gradle
- android/ci-cd
- difficulty/medium
---

# Вопрос (RU)
> Как оптимизировать сборку Gradle в Android?

# Question (EN)
> How to optimize Gradle build in Android?

---

## Ответ (RU)

### Ключевые стратегии

**1. Configuration Cache** — один из крупнейших выигрышей для чистых сборок
- Кэширует фазу конфигурации; последующие сборки пропускают повторную конфигурацию
- Требования: отсутствие побочных эффектов во время конфигурации, использование Provider API для ленивой оценки

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

При включении configuration cache внимательно отслеживайте предупреждения о несовместимых задачах и плагинах в выводе Gradle и документации билда и устраняйте конкретные задачи/плагины, нарушающие требования (побочные эффекты, чтение/запись во время конфигурации, неиспользование Provider API).

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
- KSP избегает генерации Java-стабов; обычно заметно быстрее (часто до ~2×)
- Поддерживается: Room, Hilt, Moshi

```kotlin
// ❌ Медленный KAPT
plugins { kotlin("kapt") }
dependencies { kapt(libs.room.compiler) }

// ✅ Более быстрый KSP
plugins { id("com.google.devtools.ksp") }
dependencies { ksp(libs.room.compiler) }
```

**4. Модуляризация**
- Разделение на модули уменьшает поверхность пересборки
- Осознанно используйте `api` vs `implementation` — `implementation` скрывает зависимости от downstream-модулей и уменьшает количество модулей, которые нужно пересобирать

```kotlin
// ❌ Раскрывает внутренние зависимости
dependencies { api(libs.retrofit) }

// ✅ Скрывает детали реализации
dependencies { implementation(libs.retrofit) }
```

**5. Version Catalogs**
- Централизация версий упрощает управление зависимостями и помогает избежать дублирования и рассинхронизации
- Избегайте динамических версий (`+`) — они делают кэширование и воспроизводимые сборки менее эффективными

```toml
# libs.versions.toml
[versions]
kotlin = "<version>"
compose = "<version>"

[libraries]
compose-ui = { module = "androidx.compose.ui:ui", version.ref = "compose" }
```

### Профилирование и измерение

Используйте build scans для измерения и поиска узких мест:
```bash
./gradlew assembleDebug --scan --configuration-cache --build-cache
```

Анализируйте: timeline задач, cache hit rates, время конфигурации, разрешение зависимостей.
При включении configuration cache внимательно отслеживайте сообщения о несовместимости и корректируйте соответствующие задачи и плагины.

### Оптимизация CI/CD

```yaml
# Пример для GitHub Actions
- uses: gradle/gradle-build-action@v2
  with:
    cache-read-only: false  # ✅ Разрешить запись в кэш (настройте под вашу среду)

- run: |
    ./gradlew assembleRelease \
      --configuration-cache \
      --build-cache \
      --parallel \
      --no-daemon  # ✅ Типично для короткоживущих CI-агентов; адаптируйте, если ваш CI эффективно переиспользует daemon
```

### Частые ошибки

- Динамические версии (`1.+`) ухудшают эффективность кэшей
- I/O во время конфигурации и изменяемое глобальное состояние ломают configuration cache
- Слишком много очень мелких модулей повышает накладные расходы
- Неправильное или неполное объявление входов/выходов задач
- Использование абсолютных путей во входах/выходах задач или аргументах мешает повторному использованию кэша

## Answer (EN)

### Key Strategies

**1. Configuration Cache** — one of the largest wins for clean builds
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

When enabling configuration cache, carefully watch Gradle output for incompatibility warnings and docs, and fix specific tasks/plugins that violate requirements (side effects, config-time I/O, not using Provider API).

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
- KSP avoids Java stub generation; typically significantly faster (often up to around 2×)
- Supported by: Room, Hilt, Moshi

```kotlin
// ❌ Slow KAPT
plugins { kotlin("kapt") }
dependencies { kapt(libs.room.compiler) }

// ✅ Faster KSP
plugins { id("com.google.devtools.ksp") }
dependencies { ksp(libs.room.compiler) }
```

**4. Modularization**
- Breaking into modules reduces rebuild surface
- Use `api` vs `implementation` intentionally — `implementation` hides dependencies from downstream modules and reduces the number of modules that must be recompiled

```kotlin
// ❌ Exposes internal dependencies
dependencies { api(libs.retrofit) }

// ✅ Hides implementation details
dependencies { implementation(libs.retrofit) }
```

**5. Version Catalogs**
- Centralized version management simplifies dependency maintenance and avoids duplication/misalignment
- Avoid dynamic versions (`+`) — they hurt caching and reproducibility

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
When enabling configuration cache, watch for reported incompatibilities and fix offending tasks/plugins.

### CI/CD Optimization

```yaml
# GitHub Actions example
- uses: gradle/gradle-build-action@v2
  with:
    cache-read-only: false  # ✅ Allow cache writes (tune per environment)

- run: |
    ./gradlew assembleRelease \
      --configuration-cache \
      --build-cache \
      --parallel \
      --no-daemon  # ✅ Typical for short-lived CI agents; adjust if your CI reuses the daemon effectively
```

### Common Pitfalls

- Dynamic versions (`1.+`) invalidate or reduce effectiveness of caches
- Configuration-time I/O and mutable global state break configuration cache
- Too many very small modules can increase overhead
- Not declaring task inputs/outputs properly
- Using absolute paths in task inputs/outputs or arguments can break cache reuse

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

## Related Questions

### Prerequisites / Concepts

- [[c-app-bundle]]

### Prerequisites (Easier)
- [[q-android-build-optimization--android--medium]] — General Android build optimization strategies

### Related (Same Level)
- [[q-android-modularization--android--medium]] — Module structure for better build performance

### Advanced (Harder)
- [[q-cicd-pipeline-android--android--medium]] — CI/CD setup with build caching
