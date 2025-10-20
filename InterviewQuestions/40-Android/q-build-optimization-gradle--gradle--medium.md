---
id: 20251011-220005
title: Gradle Build Optimization / Оптимизация сборки Gradle
aliases: [Gradle Build Optimization, Оптимизация сборки Gradle]
# Classification
topic: android
subtopics: [gradle, dependency-management]
question_kind: android
difficulty: medium
# Language & provenance
original_language: en
language_tags: [en, ru]
source: Original
source_note: Gradle build performance best practices
# Workflow & relations
status: draft
moc: moc-android
related: [q-android-build-optimization--android--medium, q-baseline-profiles-optimization--performance--medium, q-android-modularization--android--medium]
# Timestamps
created: 2025-10-11
updated: 2025-10-20
# Tags (mirror android subtopics + difficulty)
tags: [android/gradle, android/dependency-management, build-performance, difficulty/medium]
---

# Question (EN)
> How do you optimize Gradle build performance on Android using configuration cache, build cache, parallelism, modularization, and KSP? What are common pitfalls?

# Вопрос (RU)
> Как оптимизировать производительность сборки Gradle в Android с помощью configuration cache, build cache, параллелизма, модуляризации и KSP? Какие типичные ошибки?

---

## Answer (EN)

### Principles
- **Profile first**: Use build scans to locate bottlenecks (configuration vs execution, cache misses).
- **Cache aggressively**: Configuration cache + build cache for reuse across builds/CI.
- **Reduce work**: Modularization, KSP instead of KAPT, avoid dynamic versions, avoid non-cacheable tasks.
- **Parallelize**: Enable parallel workers, keep modules independent.
- **Stabilize inputs**: Pin versions (no dynamic), provider APIs, deterministic paths.

### Configuration Cache (largest single win)
- Caches the configuration phase; subsequent builds skip re-config.
- Requirements: no side effects at configuration time; use Provider API instead of reading env/files directly.
```kotlin
// GOOD: defer reading env to execution via Provider API
val apiKey = providers.environmentVariable("API_KEY")
android { defaultConfig { buildConfigField("String", "API_KEY", apiKey.map { "\"$it\"" }) } }
```

### Build Cache (local + remote)
- Reuses task outputs between builds/machines; great for CI/teams.
- Ensure tasks are cacheable (declared inputs/outputs; no absolute paths; no time-dependent logic).
```kotlin
// settings.gradle.kts (conceptual)
buildCache {
  local { isEnabled = true }
  // remote<HttpBuildCache> { url = uri("<your-cache-url>"); isPush = (System.getenv("CI") == "true") }
}
```

### Parallelism and Workers
- Enable parallel task execution and adequate workers.
- Keep module graph shallow; reduce cross-module coupling to maximize concurrency.

### Modularization
- Split features and core layers into modules for smaller incremental rebuilds.
- Depend on API-only where possible to minimize recompilation surface.

### KSP over KAPT
- KSP avoids Java stub generation; typically ~2x faster annotation processing.
- Migrate processors when supported (Room, Hilt, Moshi, etc.).
```kotlin
plugins { id("com.google.devtools.ksp") }
dependencies { ksp(libs.room.compiler); ksp(libs.hilt.compiler) }
```

### Version Catalogs (no hardcoded versions in build files)
- Centralize versions; speed up sync; avoid dynamic `+`.
```toml
# libs.versions.toml (structure only, no specific numbers)
[versions]
kotlin = "<version>"
compose = "<version>"

[libraries]
kotlin-stdlib = { module = "org.jetbrains.kotlin:kotlin-stdlib", version.ref = "kotlin" }
compose-ui = { module = "androidx.compose.ui:ui", version.ref = "compose" }
```

### Build Scans (measurement)
- Run with `--scan`; analyze task timeline, cache hit rates, configuration time, dependency resolution.
- Fix hotspots iteratively; confirm wins by comparing scans before/after.

### CI/CD
- Reuse caches (Gradle action + caches for wrapper and `.gradle` dirs).
- Run with `--configuration-cache --build-cache --parallel`.
- Keep Java toolchain stable; enable remote cache write from CI only.

### Common Pitfalls
- Dynamic versions (`1.+`), absolute paths, configuration-time I/O, too many tiny modules, non-cacheable custom tasks, disabled daemon, not profiling.

## Ответ (RU)

### Принципы
- **Сначала профилируйте**: build scans для поиска узких мест (configuration vs execution, cache miss).
- **Максимум кеширования**: configuration cache + build cache для повторного использования в локале и CI.
- **Меньше работы**: модуляризация, KSP вместо KAPT, без динамических версий, избегать не-кэшируемых задач.
- **Параллелизм**: включить параллельное выполнение и достаточное число workers.
- **Стабильные входы**: фиксировать версии (без `+`), Provider API, детерминированные пути.

### Configuration Cache (наибольший выигрыш)
- Кеширует фазу конфигурации; последующие сборки пропускают re-config.
- Требования: без сайд-эффектов на configuration; использовать Provider API вместо прямого I/O.
```kotlin
// GOOD: отложенное чтение переменных окружения через Provider API
val apiKey = providers.environmentVariable("API_KEY")
android { defaultConfig { buildConfigField("String", "API_KEY", apiKey.map { "\"$it\"" }) } }
```

### Build Cache (локальный + удаленный)
- Переиспользует выходы задач между сборками/машинами; особенно полезно в CI/команде.
- Убедитесь, что задачи кэшируемы (inputs/outputs; без абсолютных путей; без зависимости от времени).
```kotlin
// settings.gradle.kts (структура)
buildCache {
  local { isEnabled = true }
  // remote<HttpBuildCache> { url = uri("<url>"); isPush = (System.getenv("CI") == "true") }
}
```

### Параллелизм и workers
- Включить параллельное выполнение и достаточное число workers.
- Держать граф модулей плоским; уменьшать межмодульные зависимости.

### Модуляризация
- Делите фичи и core на модули для меньших инкрементальных пересборок.
- Зависеть по API там, где возможно, чтобы уменьшить область перекомпиляции.

### KSP вместо KAPT
- KSP избегает Java stubs; обычно ~в 2 раза быстрее.
- Мигрируйте процессоры при наличии поддержки (Room, Hilt, Moshi и т.д.).
```kotlin
plugins { id("com.google.devtools.ksp") }
dependencies { ksp(libs.room.compiler); ksp(libs.hilt.compiler) }
```

### Version Catalogs (без жестких версий в build-файлах)
- Централизованные версии; быстрее sync; никаких `+`.
```toml
# libs.versions.toml (структура, без конкретных номеров)
[versions]
kotlin = "<version>"
compose = "<version>"

[libraries]
kotlin-stdlib = { module = "org.jetbrains.kotlin:kotlin-stdlib", version.ref = "kotlin" }
compose-ui = { module = "androidx.compose.ui:ui", version.ref = "compose" }
```

### Build Scans (измерения)
- Запускайте с `--scan`; анализируйте timeline задач, cache hit, время конфигурации, разрешение зависимостей.
- Исправляйте горячие точки итеративно; подтверждайте выигрыши сравнением сканов.

### CI/CD
- Переиспользуйте кэши (Gradle action + кэш wrapper и `.gradle`).
- Запускайте с `--configuration-cache --build-cache --parallel`.
- Фиксируйте toolchain; запись в remote cache только из CI.

### Типичные ошибки
- Динамические версии (`1.+`), абсолютные пути, I/O на configuration, слишком много мелких модулей, не-кэшируемые задачи, выключенный daemon, отсутствие профилирования.

---

## Follow-ups
- How to make a custom Gradle task cacheable (inputs/outputs)?
- When does configuration cache break, and how to detect it quickly?
- KSP migration steps and verification for each processor?

## References
- https://docs.gradle.org/current/userguide/configuration_cache.html
- https://docs.gradle.org/current/userguide/build_cache.html
- https://docs.gradle.org/current/userguide/performance.html

## Related Questions

### Prerequisites (Easier)
- [[q-android-build-optimization--android--medium]]

### Related (Same Level)
- [[q-android-modularization--android--medium]]
- [[q-baseline-profiles-optimization--performance--medium]]

### Advanced (Harder)
- [[q-cicd-pipeline-android--android--medium]]
- [[q-android-performance-measurement-tools--android--medium]]
